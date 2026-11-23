# "Uma tarde construindo o Clausa" — como regerar

Brutos (não ficam no repositório): 5 clipes do celular, na ordem do roteiro, em `brutos/c1.mp4` … `c5.mp4`.

1. `bash base.sh teste` — antes/depois do tratamento de cor (opcional).
2. `bash base.sh` — corta, acelera, preenche os planos 3:4 com fundo desfocado, trata a cor e junta em `base.mp4`.
3. `python3 lofi.py 31.13 "[7.033,11.6,19.233,23.333]" 26.75 musica.wav` — trilha lo-fi + whoosh nos cortes.
4. Som ambiente dos clipes 1 e 5 + mixagem: ver o comando `ambiente.wav`/`trilha.wav` no histórico do commit.
5. `node overlay.js full ov` — textos animados (`../../tarde-founder.html`) como PNG transparentes.
6. `ffmpeg -i base.mp4 -framerate 30 -i ov/o%04d.png -i trilha.wav -filter_complex "[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 19 -c:a aac -shortest -movflags +faststart ../../tarde-founder-dia1.mp4`

Textos e horários das cenas ficam no array `S` de `tarde-founder.html`.

## Versão 2 (ritmo de "day in the life")
`base2.sh` monta 11 cortes de 2–4 batidas da trilha (88 BPM), cortando no gesto; `overlay2.js` renderiza `../../tarde-founder-v2.html`.
Trilha: `python3 lofi.py 25.133 "[1.367,3.4,4.767,7.5,9.533,11.567,14.3,16.333,18.367,20.4]" 22.3 musica2.wav` + som ambiente dos cortes abertos.
Saída: `../../tarde-founder-dia1-v2.mp4` (25 s).

## Versão 3 (texto atrás da pessoa)
1. Máscara da pessoa: `python3 ../../ferramentas/recortar_pessoa.py base2.mp4 mascara.mkv rvm_mobilenetv3_fp32.onnx 0.25`
   (modelo RVM: github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx — GPL-3.0, não versionado).
2. Textos em duas camadas: `node overlay3.js behind full ovB` e `node overlay3.js front full ovF` (`../../tarde-founder-v3.html`).
3. Montagem: base + camada de trás + (base recortada pela máscara) + camada da frente:
   `-filter_complex "[1:v]format=gray[m];[0:v]split[b0][b1];[b0][2:v]overlay[bt];[b1][m]alphamerge[pe];[bt][pe]overlay[c];[c][3:v]overlay"`
Palavras de trás: posicionadas pela altura da cabeça medida na máscara (closes: no alto, a cabeça cobre a base das letras; planos abertos: no meio da sala).

## Versão 4 (fontes art déco + pessoa nítida)
- Fontes: palavras de trás em **Limelight** (impacto: TRAVOU, PACIÊNCIA, 17, AMANHÃ 8H) e **Federo** (QUARTA, COMPUTADOR, FIM DE TARDE); legendas simples em **Poiret One** com contorno escuro (sombras). Arquivo: `../../tarde-founder-v4.html`, camadas com `overlay4.js`.
- Máscara em alta: `recortar_pessoa.py base2.mp4 mascara_hd.mkv rvm.onnx 0.6` (~5 min).
- Pessoa nítida e sem texto vazando no cabelo: borda firme na máscara e nitidez só na pessoa:
  `[1:v]format=gray,lutyuv=y='clip((val-90)*255/(200-90),0,255)',gblur=sigma=0.6[m]` e `[pessoa]unsharp=7:7:0.9:5:5:0`.
- Sem zoom nos cortes (ampliar amoleceria a imagem).
