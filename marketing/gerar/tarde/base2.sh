#!/bin/bash
# Versão 2: 11 cortes curtos, cada um com duração em batidas da música (88 BPM => 1 batida = 0,6818 s)
set -e
cd "$(dirname "$0")"
mkdir -p seg2
GRADE="hqdn3d=1.5:1.5:6:6,eq=contrast=1.08:saturation=1.10:gamma=1.06,colorbalance=rs=-0.02:bs=0.02:rh=0.035:bh=-0.03,unsharp=5:5:0.55:5:5:0,vignette=angle=PI/5"
B=0.681818
# clipe  início  fim   batidas  tipo   (tipo: w = plano aberto 3:4, c = close 9:16)
SEGS="c1 10.0 12.2 2 w
c1 14.0 16.0 3 w
c1 18.0 20.2 2 w
c2 0.5 3.0 4 c
c2 4.6 6.6 3 c
c3 21.5 24.5 3 c
c3 0 15 4 c
c3 34 44 3 c
c4 4 12 3 c
c4 12 14.5 3 c
c5 4.0 8.6 7 w"
: > lista2.txt; : > tempos2.txt; i=0; t=0
while read clip a b beats tipo; do
  i=$((i+1)); dur=$(python3 -c "print(round($beats*$B,4))"); spd=$(python3 -c "print(($b-$a)/($beats*$B))")
  out=seg2/s$(printf %02d $i).mp4
  if [ "$tipo" = w ]; then
    ffmpeg -nostdin -loglevel error -y -ss $a -to $b -i brutos/$clip.mp4 -filter_complex \
    "[0:v]crop=576:770:0:130,setpts=(PTS-STARTPTS)/$spd,fps=30,split[x][y];\
     [x]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,eq=brightness=-0.10:saturation=0.8[bg];\
     [y]scale=1080:-2:flags=lanczos,$GRADE[fg];[bg][fg]overlay=0:(H-h)/2,trim=duration=$dur,format=yuv420p[v]" \
    -map "[v]" -an -c:v libx264 -crf 14 -preset fast $out
  else
    ffmpeg -nostdin -loglevel error -y -ss $a -to $b -i brutos/$clip.mp4 -vf \
    "setpts=(PTS-STARTPTS)/$spd,fps=30,scale=1080:1920:flags=lanczos,$GRADE,trim=duration=$dur,format=yuv420p" -an -c:v libx264 -crf 14 -preset fast $out
  fi
  echo "file '$out'" >> lista2.txt
  echo "$i $clip $a $b $spd $t $dur $tipo" >> tempos2.txt
  t=$(python3 -c "print(round($t+$dur,4))")
done <<< "$SEGS"
ffmpeg -loglevel error -y -f concat -safe 0 -i lista2.txt -c copy base2.mp4
echo "duração total: $(ffprobe -v error -show_entries format=duration -of csv=p=0 base2.mp4)"
cat tempos2.txt
