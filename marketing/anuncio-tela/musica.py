"""Trilha própria do anúncio de tela (120 BPM, 18,5 s). Sem amostras de terceiros.
Uso: python3 musica.py saida.wav
Os cortes do vídeo caem em múltiplos de 0,5 s (um tempo), então cada corte ganha um impacto."""
import sys, wave
import numpy as np

SR = 48000
DUR = 18.5
N = int(SR * DUR)
t_all = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)
BEAT = 0.5


def put(sig, at, pan=0.0, gain=1.0):
    i = int(at * SR)
    if i >= N: return
    s = sig[:N - i] * gain
    L[i:i + len(s)] += s * (1 - max(0, pan))
    R[i:i + len(s)] += s * (1 + min(0, pan))


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def kick(d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    f = 48 + 120 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .16) * 1.1


def hat(d=0.06, g=0.25):
    n = int(d * SR); x = rng.standard_normal(n)
    x = np.diff(np.concatenate([[0], x]))  # agudo
    return x * env(n, .0005, .018) * g


def clap():
    n = int(0.25 * SR); x = rng.standard_normal(n)
    e = sum(np.exp(-np.maximum(0, np.arange(n) / SR - k * .011) / .012) * (np.arange(n) / SR >= k * .011) for k in range(3))
    return x * (e + .5 * np.exp(-np.arange(n) / SR / .09)) * .35


def bass(freq, d=0.45):
    n = int(d * SR); t = np.arange(n) / SR
    s = np.tanh(2.2 * np.sin(2 * np.pi * freq * t)) + .3 * np.sin(2 * np.pi * freq / 2 * t)
    return s * env(n, .004, .22) * .42


def pluck(freq, d=0.6, g=.16):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * freq * k * t) / k ** 1.4 for k in range(1, 6))
    return s * env(n, .002, .14) * g


def impact():
    n = int(1.6 * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-t / .06)) / SR) * np.exp(-t / .5)
    noise = rng.standard_normal(n) * np.exp(-t / .12) * .35
    return (boom + noise) * .9


def riser(d):
    n = int(d * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # passa-baixa que abre aos poucos
    a = 0.02 + 0.5 * (t / d) ** 2; y = np.zeros(n); acc = 0.0
    for i in range(n):
        acc += a[i] * (x[i] - acc); y[i] = acc
    return y * (t / d) ** 2 * .5


def whoosh(d=0.7):
    r = riser(d)
    return np.concatenate([r, r[::-1][: int(.2 * SR)]])


def pad(chord, d, g=.06):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * .3 * t)) for f in chord)
    e = np.minimum(1, t / .4) * np.minimum(1, (d - t) / .6)
    return s * e * g


A, F, C, G = 55.0, 43.65, 65.41, 49.0  # lá menor - fá - dó - sol (graves)
PROG = [A, A, F, F, C, C, G, G]

# 0–1 s: abertura com pad e subida até o primeiro corte
put(pad([220, 261.6, 329.6], 1.2, .05), 0)
put(riser(1.0), 0.0, gain=.9)
put(pluck(880, .4, .1), 0.05)

# 1–10 s: batida principal
for k in range(int((10 - 1) / BEAT)):
    tb = 1 + k * BEAT
    put(kick(), tb)
    put(hat(), tb + BEAT / 2, pan=.3)
    put(hat(.04, .14), tb + BEAT * .75, pan=-.3)
    if k % 2 == 1: put(clap(), tb, gain=.9)
    root = PROG[(k // 2) % len(PROG)]
    put(bass(root * 2), tb + BEAT / 2)
    put(pluck(root * 8 * (1.5 if k % 4 == 2 else 1), .5), tb, pan=-.2 if k % 2 else .2)
put(pad([220, 261.6, 329.6, 392], 9.2, .035), 1)

# cortes rápidos 5,5–7: acentos extras
for tb in (5.5, 6.0, 6.5):
    put(pluck(1318.5, .3, .12), tb); put(clap(), tb, gain=.6)

# 10–11: respiro + whoosh para a cortina
put(whoosh(.8), 10.1, gain=1.0)
put(pad([174.6, 220, 261.6], 1.1, .05), 10)

# 11–14,5: volta mais forte
for k in range(int((14.5 - 11) / BEAT)):
    tb = 11 + k * BEAT
    put(kick(), tb); put(hat(), tb + .25, pan=.3); put(hat(.04, .14), tb + .375, pan=-.3)
    if k % 2 == 1: put(clap(), tb)
    root = [F, F, C, C, G, G, A][k % 7]
    put(bass(root * 2), tb + .25)
    put(pluck(root * 8, .45, .14), tb)
put(riser(.9), 13.6, gain=.8)

# 14,5–18,5: final com acorde aberto
put(pad([220, 329.6, 440, 523.3, 659.3], 4.0, .045), 14.5)
put(pluck(440, 1.5, .18), 14.5); put(pluck(659.3, 1.5, .12), 14.5, pan=.3)

# impactos em cada corte de cena
for tc in (1.0, 2.5, 4.0, 7.0, 11.0, 12.5, 13.5, 14.5):
    put(impact(), tc, gain=.55 if tc not in (1.0, 14.5) else .8)

mix = np.stack([L, R], 1)
fade = np.minimum(1, (DUR - t_all) / 1.5)[:, None]
mix *= fade
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('trilha pronta', sys.argv[1])
