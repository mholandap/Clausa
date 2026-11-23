#!/bin/bash
# Monta a base do vídeo: corte, velocidade, enquadramento 9:16 e tratamento de cor
set -e
cd "$(dirname "$0")"
mkdir -p seg
# tratamento: tira ruído, contraste e cor um pouco mais vivos, leve calor nos tons claros, nitidez e vinheta suaves
GRADE="hqdn3d=1.5:1.5:6:6,eq=contrast=1.08:saturation=1.10:gamma=1.06,colorbalance=rs=-0.02:bs=0.02:rh=0.035:bh=-0.03,unsharp=5:5:0.55:5:5:0,vignette=angle=PI/5"
SCALE="scale=1080:1920:flags=lanczos"

# plano aberto (3:4 com faixas pretas): imagem inteira no centro + fundo desfocado
wide () { # $1=entrada $2=inicio $3=fim $4=velocidade $5=saida
  ffmpeg -loglevel error -y -ss $2 -to $3 -i "$1" -filter_complex \
  "[0:v]crop=576:770:0:130,setpts=(PTS-STARTPTS)/$4,fps=30,split[a][b];\
   [a]scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.10:saturation=0.8[bg];\
   [b]scale=1080:-2:flags=lanczos,$GRADE[fg];[bg][fg]overlay=0:(H-h)/2,format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -crf 14 -preset fast "$5"
}
# close (já em 9:16)
close () { # $1=entrada $2=inicio $3=fim $4=velocidade $5=saida
  ffmpeg -loglevel error -y -ss $2 -to $3 -i "$1" -vf \
  "setpts=(PTS-STARTPTS)/$4,fps=30,$SCALE,$GRADE,format=yuv420p" -an -c:v libx264 -crf 14 -preset fast "$5"
}

if [ "$1" = "teste" ]; then
  # antes e depois do tratamento, num quadro de cada tipo de plano
  ffmpeg -loglevel error -y -ss 15 -i brutos/c1.mp4 -frames:v 1 -vf "crop=576:770:0:130,scale=540:-2" t_antes_wide.png
  ffmpeg -loglevel error -y -ss 15 -i brutos/c1.mp4 -frames:v 1 -vf "crop=576:770:0:130,scale=540:-2:flags=lanczos,$GRADE" t_depois_wide.png
  ffmpeg -loglevel error -y -ss 3 -i brutos/c2.mp4 -frames:v 1 -vf "scale=405:720" t_antes_close.png
  ffmpeg -loglevel error -y -ss 3 -i brutos/c2.mp4 -frames:v 1 -vf "scale=405:720:flags=lanczos,$GRADE" t_depois_close.png
  exit 0
fi

wide  brutos/c1.mp4 9.0 21.67 1.8  seg/s1.mp4
close brutos/c2.mp4 1.0 6.7   1.25 seg/s2.mp4
close brutos/c3.mp4 0   45.87 6    seg/s3.mp4
close brutos/c4.mp4 0   20.5  5    seg/s4.mp4
wide  brutos/c5.mp4 0   8.62  1.1  seg/s5.mp4
printf "file 'seg/s1.mp4'\nfile 'seg/s2.mp4'\nfile 'seg/s3.mp4'\nfile 'seg/s4.mp4'\nfile 'seg/s5.mp4'\n" > lista.txt
ffmpeg -loglevel error -y -f concat -safe 0 -i lista.txt -c copy base.mp4
for f in seg/s*.mp4 base.mp4; do echo "$f $(ffprobe -v error -show_entries format=duration -of csv=p=0 $f)"; done
