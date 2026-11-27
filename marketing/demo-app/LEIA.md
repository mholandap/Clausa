# Vídeo de demonstração do Clausa (vertical, 41 s, sem música)

- `demo.html`: a "cena" (textos grandes, celular flutuando) com o **app de verdade** num iframe; `window.render(t)` controla o app quadro a quadro.
- `render-demo.js`: gera os quadros (precisa do site em `http://localhost:8766`, com `python3 -m http.server 8766` na raiz). Usa um login de mentira num "Escritório Modelo" fictício.
- `contrato-demo.txt`: o contrato fictício usado.
- `demo-clausa.mp4`: o vídeo pronto (1080×1920, 60 fps, sem áudio, a pedido do Pedro).

Montagem: `ffmpeg -framerate 60 -i quadros/f%05d.jpg -c:v libx264 -crf 17 -pix_fmt yuv420p -an -movflags +faststart demo-clausa.mp4`
