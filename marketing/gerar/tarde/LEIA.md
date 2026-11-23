# "Uma tarde construindo o Clausa" — como regerar

Brutos (não ficam no repositório): 5 clipes do celular, na ordem do roteiro, em `brutos/c1.mp4` … `c5.mp4`.

1. `bash base.sh teste` — antes/depois do tratamento de cor (opcional).
2. `bash base.sh` — corta, acelera, preenche os planos 3:4 com fundo desfocado, trata a cor e junta em `base.mp4`.
3. `python3 lofi.py 31.13 "[7.033,11.6,19.233,23.333]" 26.75 musica.wav` — trilha lo-fi + whoosh nos cortes.
4. Som ambiente dos clipes 1 e 5 + mixagem: ver o comando `ambiente.wav`/`trilha.wav` no histórico do commit.
5. `node overlay.js full ov` — textos animados (`../../tarde-founder.html`) como PNG transparentes.
6. `ffmpeg -i base.mp4 -framerate 30 -i ov/o%04d.png -i trilha.wav -filter_complex "[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 19 -c:a aac -shortest -movflags +faststart ../../tarde-founder-dia1.mp4`

Textos e horários das cenas ficam no array `S` de `tarde-founder.html`.
