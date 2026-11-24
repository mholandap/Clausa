"""Máquina de vídeos do Clausa: roteiro + narração -> Reel pronto + relatório de conferência.

Uso:
  python3 maquina.py roteiro.json pasta_de_trabalho            # vídeo completo
  python3 maquina.py roteiro.json pasta_de_trabalho --previa   # só algumas imagens de prévia

Etapas: transcreve a narração (Whisper large-v3, tempo por palavra) -> alinha cada cena do roteiro à fala ->
monta a linha do tempo -> renderiza o estúdio (render.js + estudio.html) -> trilha (música com ducking + efeitos)
-> codifica (1080x1920, 30 fps, -14 LUFS) -> conferência automática (qc.json).

Roteiro (JSON):
  {"titulo": "...", "audio": "narracao.mp3", "saida": "video.mp4", "palavras_chave": ["contrato", ...],
   "cenas": [ {"tipo": "telefone", "fala": "primeiras palavras da fala desta cena...", "hora": "7:00", "data": "terça, 24 de novembro",
               "notificacoes": [{"titulo": "Clausa", "texto": "...", "palavra": "palavra que dispara"}]},
              {"tipo": "monitor", "n": "01", "titulo": "IRREVOGÁVEL", "fala": "...",
               "tela": {"cabecalho": "CLÁUSULA 3ª", "texto": "...", "destaque": "trecho do texto", "nota": "..."}} ]}
"""
import json, os, re, subprocess, sys, unicodedata, difflib, wave
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..', 'ferramentas'))
from transcrever import transcrever  # noqa: E402

SR = 44100


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    return re.sub(r'[^a-z0-9%]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


def sh(*cmd):
    subprocess.run(cmd, check=True)


# ---------------------------------------------------------------- alinhamento
def achar(palavras, alvo, desde=0, ate=None):
    """Índice da primeira palavra onde a sequência `alvo` (tokens normalizados) começa; tolera erros do Whisper."""
    ate = len(palavras) if ate is None else ate
    toks = [norm(x) for x in alvo.split() if norm(x)][:4]
    if not toks:
        return None
    melhor, idx = 0.0, None
    for i in range(desde, ate):
        janela = [norm(palavras[j]['w']) for j in range(i, min(ate, i + len(toks)))]
        r = difflib.SequenceMatcher(None, ' '.join(toks), ' '.join(janela)).ratio()
        if r > melhor:
            melhor, idx = r, i
        if r > .92:
            break
    return idx if melhor >= .6 else None


def frases_de(palavras, max_pal=5, pausa=.35):
    fr, cur = [], []
    for k, w in enumerate(palavras):
        cur.append(w)
        prox = palavras[k + 1] if k + 1 < len(palavras) else None
        fim = re.search(r'[.,!?;:]$', w['w']) or len(cur) >= max_pal or prox is None or prox['t0'] - w['t1'] > pausa
        if fim:
            fr.append({'ini': cur[0]['t0'], 'fim': cur[-1]['t1'], 'palavras': cur})
            cur = []
    return fr


def linha_do_tempo(rot, palavras, cauda=1.3):
    cenas = rot['cenas']; ptr = 0
    for c in cenas:
        i = achar(palavras, c['fala'], ptr)
        if i is None:
            raise SystemExit(f'Não achei na narração a fala da cena: "{c["fala"][:50]}..."')
        c['_i'] = i; ptr = i + 1
    for k, c in enumerate(cenas):
        c['ini'] = 0.0 if k == 0 else max(0.0, palavras[c['_i']]['t0'] - .2)
        prox = cenas[k + 1]['_i'] if k + 1 < len(cenas) else len(palavras)
        lim = (c['_i'], prox)
        if c['tipo'] == 'monitor':
            t = c.get('tela', {})
            for campo, chave in (('destaque', 'destaque_em'), ('nota', 'nota_em')):
                if t.get(campo):
                    j = achar(palavras, t[campo], *lim)
                    c[chave] = palavras[j]['t0'] if j is not None else c['ini'] + (.5 if campo == 'destaque' else 1.2)
        for n in c.get('notificacoes', []):
            j = achar(palavras, n['palavra'], *lim) if n.get('palavra') else None
            n['em'] = palavras[j]['t0'] if j is not None else c['ini'] + .5
    dur = round(palavras[-1]['t1'] + cauda, 3)
    for k, c in enumerate(cenas):
        c['fim'] = cenas[k + 1]['ini'] if k + 1 < len(cenas) else dur
        c.pop('_i', None)
    return {'titulo': rot.get('titulo', ''), 'dur': dur, 'cenas': cenas, 'frases': frases_de(palavras),
            'palavras_chave': rot.get('palavras_chave', []), 'logo': 'file://' + os.path.abspath(os.path.join(AQUI, '..', '..', 'favicon.png'))}


# ---------------------------------------------------------------- trilha
def tt(d): return np.arange(int(d * SR)) / SR


def banda(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def trilha(voz_wav, tl, saida, seed=7):
    rng = np.random.default_rng(seed)
    w = wave.open(voz_wav); v = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(float) / 32767
    N = int(tl['dur'] * SR); voz = np.zeros(N); voz[:min(N, len(v))] = v[:N]
    mus = np.zeros((N, 2)); fx = np.zeros((N, 2))

    def put(buf, s, t, g=1., pan=0.):
        i = int(t * SR)
        if 0 <= i < N:
            j = min(N, i + len(s)); s = s[:j - i] * g; buf[i:j, 0] += s * (1 - max(0, pan)); buf[i:j, 1] += s * (1 + min(0, pan))
    # música: pulso suave em Lá menor (sintetizada, sem direitos de terceiros)
    B = 60 / 96
    acordes = [[220, 261.63, 329.63], [174.61, 220, 261.63], [261.63, 329.63, 392], [196, 246.94, 293.66]]
    t0, k = 0., 0
    while t0 < tl['dur']:
        for q in range(8):
            f = acordes[k % 4][q % 3] * (2 if q in (3, 6) else 1); d = tt(.5)
            put(mus, (np.sin(2 * np.pi * f * d) + .4 * np.sin(4 * np.pi * f * d) * np.exp(-d * 9)) * np.exp(-d * 6) * np.minimum(1, d / .004), t0 + q * B / 2, .09, (-.3, .3)[q % 2])
        d = tt(4 * B); put(mus, np.sin(2 * np.pi * acordes[k % 4][0] / 2 * d) * np.minimum(1, d / .05) * np.exp(-d * .5), t0, .16)
        for q in range(4):
            d = tt(.28); put(mus, np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-d * 32)) / SR) * np.exp(-d * 10), t0 + q * B, .30 if q % 2 == 0 else .0)
            d = tt(.05); put(mus, banda(rng.standard_normal(len(d)), 7000, 14000) * np.exp(-d * 80), t0 + q * B + B / 2, .03, .3)
        t0 += 4 * B; k += 1
    # efeitos: deslize da câmera em cada troca de cena, "pop" nas notificações, "tique" nos destaques
    for c in tl['cenas'][1:]:
        d = tt(.55); put(fx, banda(rng.standard_normal(len(d)), 400, 5000) * np.sin(np.pi * d / .55) ** 2.2, c['ini'] - .1, .10)
    for c in tl['cenas']:
        for n in c.get('notificacoes', []):
            d = tt(.4); put(fx, (np.sin(2 * np.pi * 1180 * d) + .5 * np.sin(2 * np.pi * 1770 * d)) * np.exp(-d * 12), n['em'], .10)
        if c.get('destaque_em'):
            d = tt(.08); put(fx, banda(rng.standard_normal(len(d)), 2500, 9000) * np.exp(-d * 60), c['destaque_em'], .12)
    # ducking: música ~15 dB abaixo quando a voz fala
    hop = 441; env = np.array([np.sqrt(np.mean(voz[i:i + hop] ** 2)) for i in range(0, N, hop)])
    env = np.convolve(env, np.ones(20) / 20, 'same'); env = np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    mus *= np.repeat(1 - .78 * env, hop)[:N, None]
    mix = mus + fx + np.stack([voz, voz], 1)
    fo = int(.8 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
    mix /= np.abs(mix).max() / .85
    o = wave.open(saida, 'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR)
    o.writeframes((mix * 32767).astype('<i2').tobytes()); o.close()


# ---------------------------------------------------------------- conferência
def conferir(video, rot, tl):
    r = {}
    p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=width,height,r_frame_rate,codec_type',
                                   '-of', 'json', video], capture_output=True, text=True).stdout)
    v = [s for s in p['streams'] if s['codec_type'] == 'video'][0]
    r['formato'] = {'ok': (v['width'], v['height'], v['r_frame_rate']) == (1080, 1920, '30/1'), 'valor': f"{v['width']}x{v['height']} @ {v['r_frame_rate']}"}
    dur = float(p['format']['duration']); r['duracao'] = {'ok': 10 <= dur <= 90, 'valor': round(dur, 2)}
    log = subprocess.run(['ffmpeg', '-nostdin', '-i', video, '-vf', 'blackdetect=d=0.3:pix_th=0.06,freezedetect=n=0.002:d=1.5',
                          '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    r['quadros_pretos'] = {'ok': 'black_start' not in log, 'valor': log.count('black_start')}
    r['quadros_congelados'] = {'ok': 'freeze_start' not in log, 'valor': log.count('freeze_start')}
    i = re.findall(r'I:\s+(-?[\d.]+) LUFS', log); pk = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', log)
    lufs = float(i[-1]) if i else None; peak = float(pk[-1]) if pk else None
    r['volume'] = {'ok': lufs is not None and abs(lufs + 14) <= 1 and (peak is None or peak <= -1), 'valor': f'{lufs} LUFS, pico {peak} dBFS'}
    # o Whisper reouve o vídeo final e compara com o roteiro
    _, pal = transcrever(video, 'large-v3', 'pt')
    ouvido = ' '.join(norm(w['w']) for w in pal); esperado = ' '.join(norm(x) for c in rot['cenas'] for x in c.get('fala_completa', c['fala']).split())
    sim = difflib.SequenceMatcher(None, ouvido, esperado).ratio()
    r['fala_bate_com_roteiro'] = {'ok': sim >= .85, 'valor': round(sim, 3)}
    r['tudo_ok'] = all(x['ok'] for x in r.values() if isinstance(x, dict))
    return r


# ---------------------------------------------------------------- principal
def main():
    rot_path, trab = sys.argv[1], sys.argv[2]; previa = '--previa' in sys.argv
    rot = json.load(open(rot_path)); base = os.path.dirname(os.path.abspath(rot_path)); os.makedirs(trab, exist_ok=True)
    audio = os.path.join(base, rot['audio'])
    cache = os.path.join(trab, 'palavras.json')
    if os.path.exists(cache):
        palavras = json.load(open(cache))
    else:
        _, palavras = transcrever(audio, 'large-v3', 'pt'); json.dump(palavras, open(cache, 'w'), ensure_ascii=False)
    tl = linha_do_tempo(rot, palavras)
    tlp = os.path.join(trab, 'timeline.json'); json.dump(tl, open(tlp, 'w'), ensure_ascii=False, indent=1)
    for c in tl['cenas']:
        print(f"cena {c.get('n', c['tipo']):>9}: {c['ini']:6.2f} -> {c['fim']:6.2f}  {c['fala'][:45]}")
    if previa:
        ts = [round((c['ini'] + c['fim']) / 2, 2) for c in tl['cenas']] + [round(tl['cenas'][1]['ini'] + .2, 2)]
        sh('node', os.path.join(AQUI, 'render.js'), tlp, os.path.join(trab, 'previa'), 'preview', *map(str, ts)); return
    q = os.path.join(trab, 'quadros'); sh('node', os.path.join(AQUI, 'render.js'), tlp, q)
    voz = os.path.join(trab, 'voz.wav')
    sh('ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', audio, '-ar', str(SR), '-ac', '1', '-af',
       'highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=8:release=120:makeup=2,alimiter=limit=0.89', voz)
    tri = os.path.join(trab, 'trilha.wav'); trilha(voz, tl, tri)
    saida = os.path.join(base, rot.get('saida', 'video.mp4'))
    sh('ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-framerate', '30', '-i', os.path.join(q, 'f%05d.jpg'), '-i', tri,
       '-filter_complex', '[0:v]format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100[a]', '-map', '[v]', '-map', '[a]',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-profile:v', 'high', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', saida)
    r = conferir(saida, rot, tl); json.dump(r, open(os.path.join(trab, 'qc.json'), 'w'), ensure_ascii=False, indent=1)
    print('\nCONFERÊNCIA:'); [print(f"  {'OK ' if v['ok'] else 'FALHOU'}  {k}: {v['valor']}") for k, v in r.items() if isinstance(v, dict)]
    print('  =>', 'APROVADO' if r['tudo_ok'] else 'REVISAR', '|', saida)


if __name__ == '__main__':
    main()
