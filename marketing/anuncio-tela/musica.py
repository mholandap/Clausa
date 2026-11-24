"""Trilha própria do anúncio de tela: pop eletrônico leve e animado, contínua, sem impactos nos cortes.
122 BPM, lá menor (Am–F–C–G), bumbo reto, chimbal no contratempo, palmas no 2 e 4, baixo sincopado,
acordes curtos de sintetizador e um refrão brilhante. Sem amostras de terceiros.
Uso: python3 musica.py saida.wav [duração]"""
import sys, wave
import numpy as np

SR = 48000
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 17.5
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
BPM = 122
B = 60 / BPM
BAR = 4 * B
START = 1.0  # a batida entra quando a tela fica laranja


def put(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N or at < 0: return
    s = sig[:N - i] * gain
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))


def hz(n): return 440 * 2 ** ((n - 69) / 12)


def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y


def saw(f, t, harm=14, det=0.0):
    s = np.zeros_like(t)
    for k in range(1, harm + 1):
        if f * k > SR / 2.2: break
        s += np.sin(2 * np.pi * f * (1 + det) * k * t) / k
    return s


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def kick(g=.85):
    n = int(.35 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t / .028)) / SR) * env(n, .001, .13)
    click = rng.standard_normal(n) * np.exp(-t / .002) * .15
    return (body + click) * g


def clap(g=.3):
    n = int(.22 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    e = sum((t >= k * .01) * np.exp(-np.maximum(0, t - k * .01) / .01) for k in range(3)) + .6 * np.exp(-t / .07)
    return lowpass(np.diff(np.concatenate([[0], x])), .6) * e * g


def hat(op=False, g=.12):
    n = int((.16 if op else .05) * SR); x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], np.diff(np.concatenate([[0], x]))]))
    return x * env(n, .0005, .05 if op else .012) * g


def bass(note, d, g=.34):
    n = int(d * SR); t = np.arange(n) / SR
    s = lowpass(saw(hz(note), t, 10), .08) * 2.2 + .5 * np.sin(2 * np.pi * hz(note) * t)
    return s * env(n, .004, .18) * np.minimum(1, (d - t) / .02) * g


def stab(notes, d=.18, g=.07):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(saw(hz(x), t, 12, .004) + saw(hz(x), t, 12, -.004) for x in notes)
    return lowpass(s, .22) * env(n, .002, .07) * g


def lead(note, d=.22, g=.11):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(note)
    s = saw(f, t, 16, .003) + saw(f, t, 16, -.003) + .6 * np.sin(2 * np.pi * f * 2 * t)
    cut = .12 + .35 * np.exp(-t / .05)            # abre e fecha rápido: som de "pluck" brilhante
    y = np.empty_like(s); acc = 0.0
    for i in range(n):
        acc += cut[i] * (s[i] - acc); y[i] = acc
    return y * env(n, .003, .16) * g


def pad(notes, d, g=.025):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(saw(hz(x), t, 8, .006) + saw(hz(x), t, 8, -.006) for x in notes)
    return lowpass(s, .05) * np.minimum(1, t / .3) * np.minimum(1, (d - t) / .3) * g


# Am – F – C – G
PROG = [(45, [57, 60, 64]), (41, [57, 60, 65]), (48, [55, 60, 64]), (43, [55, 59, 62])]
# refrão em semicolcheias (None = pausa), 2 compassos
HOOK = [76, None, 76, 79, None, 81, None, 79, 76, None, 74, None, 76, None, None, None,
        72, None, 72, 74, None, 76, None, 74, 72, None, 71, None, 67, None, 69, None]
BASSPAT = [0, None, 0, 12, None, 0, 12, None]  # colcheias, sincopado

# introdução: pad abrindo + refrão filtrado antes da batida
put(pad([57, 60, 64, 69], 1.2, .03), 0)
for i, nt in enumerate([76, 79, 81, 84]):
    put(lead(nt, .2, .06), .15 + i * B / 2)

nbars = int(np.ceil((DUR - START) / BAR)) + 1
for b in range(nbars):
    t0 = START + b * BAR
    root, chord = PROG[b % 4]
    put(pad(chord + [chord[0] + 12], BAR, .02), t0)
    for k in range(4):
        tb = t0 + k * B
        put(kick(), tb)
        if k in (1, 3): put(clap(), tb, pan=.05)
        put(hat(True), tb + B / 2, pan=.3)
        put(hat(), tb + B / 4, pan=-.25); put(hat(g=.07), tb + 3 * B / 4, pan=-.25)
        put(stab(chord), tb + B / 2, pan=-.15)          # acorde no contratempo
    for i, off in enumerate(BASSPAT):
        if off is not None: put(bass(root + off, B / 2 * .9), t0 + i * B / 2)
    hk = HOOK[(b % 2) * 16:(b % 2) * 16 + 16]
    for i, nt in enumerate(hk):
        if nt: put(lead(nt), t0 + i * B / 4, pan=.15 if i % 2 else -.1)

mix = np.stack([L, R], 1)
t = np.arange(N) / SR
# "sidechain" leve: o resto abaixa um pouco a cada bumbo, dá o balanço do pop eletrônico
ph = ((t - START) % B) / B
duck = np.where(t >= START, .78 + .22 * np.minimum(1, ph / .35), 1.0)
mix *= duck[:, None]
mix *= np.minimum(1, (DUR - t) / 1.8)[:, None]
mix = np.tanh(mix * 1.2) / np.tanh(1.2)
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('trilha pronta', sys.argv[1], f'{DUR}s')
