"""Transcreve áudio/vídeo com Whisper (faster-whisper), com o tempo de cada palavra.

Uso:  python3 transcrever.py ARQUIVO [modelo] [idioma]
      modelo: tiny, base, small (padrão), medium, large-v3
Saída: imprime as frases com tempo e grava ARQUIVO.palavras.json (palavra, início, fim).

O áudio é decodificado pelo ffmpeg (a versão instalada do PyAV não é compatível
com o leitor de áudio embutido do faster-whisper).
"""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel


def carregar_audio(caminho, sr=16000):
    pcm = subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-i', caminho, '-f', 's16le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def transcrever(caminho, modelo='small', idioma='pt'):
    m = WhisperModel(modelo, device='cpu', compute_type='int8')
    segs, _ = m.transcribe(carregar_audio(caminho), language=idioma, word_timestamps=True, vad_filter=True)
    frases, palavras = [], []
    for s in segs:
        frases.append((s.start, s.end, s.text.strip()))
        palavras += [{'w': w.word.strip(), 't0': round(w.start, 3), 't1': round(w.end, 3)} for w in (s.words or [])]
    return frases, palavras


if __name__ == '__main__':
    arq = sys.argv[1]
    frases, palavras = transcrever(arq, *(sys.argv[2:4]))
    for a, b, t in frases:
        print(f'{a:6.2f}-{b:6.2f}  {t}')
    with open(arq + '.palavras.json', 'w') as f:
        json.dump(palavras, f, ensure_ascii=False, indent=1)
