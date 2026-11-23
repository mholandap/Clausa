# Como regerar o anúncio

Tudo roda offline. Requisitos: Node + Playwright, Python 3 com `numpy` e `onnxruntime`, `espeak-ng` e `ffmpeg`.

## 1. Narração

### Opção A (atual): locução gravada (ElevenLabs, voz Matheus)
A locução está em `locucao-matheus.mp3`. O `align.py` encontra as pausas entre as frases,
confere que há uma fala para cada frase do roteiro e gera `voz.wav` + `../timing.js`:
```
ffmpeg -i locucao-matheus.mp3 -ar 44100 -ac 1 loc44.wav
python3 align.py loc44.wav voz.wav ../timing.js alinhamento.json
ffmpeg -i voz.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=2:attack=8:release=120:makeup=2,alimiter=limit=0.89" voz44.wav
```
Para trocar de locução (outra voz ou a sua própria gravação), basta gravar o mesmo roteiro
com uma pausa curta entre as frases. `insert_after` em `alinhamento.json` abre respiros extras.
Depois siga para o passo 2.

### Opção B: voz neural offline (Kokoro-82M, pt-BR)
Os modelos não ficam no repositório (são grandes). Baixe-os do npm:
```
mkdir -p modelos && cd modelos
npm pack kokoro-q8-shards kokoro-js
tar xzf kokoro-q8-shards-*.tgz && cat package/kokoro-q8.part*.bin > model_q8.onnx && rm -rf package
tar xzf kokoro-js-*.tgz && cp package/voices/pf_dora.bin package/voices/pm_alex.bin . && rm -rf package
# sha256 de model_q8.onnx: fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478
cd ..
```
Edite as falas em `narracao.json` (`lines`) e rode `python3 narrate.py narracao.json`.
Isso gera `voz.wav` e atualiza `../timing.js` (a animação segue esse arquivo sozinha).
Para voz masculina, troque `voice` por `modelos/pm_alex.bin`.

## 2. Trilha (música + efeitos + ducking)
```
ffmpeg -i voz.wav -af "aresample=44100,highpass=f=90,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,alimiter=limit=0.89" voz44.wav
python3 mix.py voz44.wav ../timing.js trilha.wav
```

## 3. Vídeo (120 fps fundidos em 60 fps = desfoque de movimento)
```
node render.js full frames 120
ffmpeg -framerate 120 -i frames/f%04d.jpg -i trilha.wav -filter_complex "[0:v]tmix=frames=2:weights='1 1',fps=60,format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 20 -c:a aac -b:a 192k -shortest -movflags +faststart ../clausa-anuncio.mp4
```
Para prévia rápida, abra `../anuncio.html` no navegador (toca em loop, sem som).
