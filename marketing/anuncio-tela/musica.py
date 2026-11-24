"""Trilha própria do anúncio de tela: leve e contínua, sem impactos nos cortes.
Dó maior, 120 BPM, progressão C–G–Am–F, marimba com um refrão curto que gruda, piano elétrico,
baixo redondo, batida suave e chocalho. Sem amostras de terceiros.
Uso: python3 musica.py saida.wav [duração]"""
import sys, wave
import numpy as np

SR = 48000
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 17.5
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(3)
B = 0.5            # um tempo a 120 BPM
BAR = 4 * B
START = 1.0        # a batida entra quando a tela fica laranja


def put(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N or at < 0: return
    s = sig[:N - i] * gain
    L[i:i + len(s)] += s * (1 - max(0, pan)); R[i:i + len(s)] += s * (1 + min(0, pan))


def hz(n): return 440 * 2 ** ((n - 69) / 12)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def marimba(note, d=.7, g=.2):
    n = int(d * SR); t = np.arange(n) / SR; f = hz(note)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / .35) + .35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / .05) + .1 * np.sin(2 * np.pi * f * 9.9 * t) * np.exp(-t / .015)
    return s * np.minimum(1, t / .002) * g


def epiano(notes, d, g=.05):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * hz(x) * t + .6 * np.sin(2 * np.pi * hz(x) * 2 * t) * np.exp(-t / .3)) for x in notes)
    e = np.minimum(1, t / .01) * np.exp(-t / 1.6) * np.minimum(1, (d - t) / .08)
    return s * e * g


def bass(note, d=.45, g=.28):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * hz(note) * t) + .15 * np.sin(2 * np.pi * hz(note) * 2 * t)
    return s * env(n, .008, .3) * np.minimum(1, (d - t) / .03) * g


def kick(g=.5):
    n = int(.3 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-t / .03)) / SR) * env(n, .002, .09) * g


def snap(g=.16):
    n = int(.18 * SR); x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    return x * env(n, .001, .03) * g


def shaker(g=.05):
    n = int(.08 * SR); x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    t = np.arange(n) / SR
    return x * np.sin(np.pi * np.minimum(1, t / .06)) * g


# acordes: C, G, Am, F  (raiz para o baixo, tríade para o piano)
PROG = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [60, 64, 69]), (41, [60, 65, 69])]
# refrão da marimba (colcheias, None = pausa), 2 compassos que se repetem
HOOK = [76, None, 79, 76, 74, None, 72, 74, 76, None, 79, 81, 79, None, 76, None,
        72, None, 74, 76, 74, None, 72, 69, 71, None, 72, 74, 72, None, None, None]

nbars = int(np.ceil((DUR - START) / BAR)) + 1
# introdução: só piano e a marimba suave antes da batida
put(epiano([60, 64, 67, 72], 1.0, .045), 0.0)
for i, nt in enumerate([72, 76, 79, 84]):
    put(marimba(nt, .6, .12), .1 + i * .2)

for b in range(nbars):
    t0 = START + b * BAR
    root, chord = PROG[b % 4]
    put(epiano(chord, BAR, .05), t0)
    for k in range(4):
        tb = t0 + k * B
        put(kick(), tb)
        if k in (1, 3): put(snap(), tb, pan=.1)
        put(bass(root if k % 2 == 0 else root + 12, .42), tb + (0 if k % 2 == 0 else .25))
        for s in range(4):
            put(shaker(.035 if s % 2 else .055), tb + s * B / 4, pan=.35)
    # refrão a partir do 2º compasso
    if b >= 1:
        for i in range(16):
            nt = HOOK[((b - 1) % 2) * 16 + i]
            if nt: put(marimba(nt), t0 + i * B / 2, pan=-.2 if i % 2 else .15)

mix = np.stack([L, R], 1)
t = np.arange(N) / SR
mix *= np.minimum(1, (DUR - t) / 2.0)[:, None]          # some devagar no final
mix = np.tanh(mix * 1.05) / np.tanh(1.05)
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('trilha pronta', sys.argv[1], f'{DUR}s')
