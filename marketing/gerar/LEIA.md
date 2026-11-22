# Como regerar o anúncio

1. Edite textos/tempos em `../anuncio.html` (abra no navegador para ver a prévia em loop).
2. `node render.js full frames` — gera 540 quadros (18 s a 30 fps). Requer Playwright.
3. `python3 audio.py trilha.wav` — sintetiza a trilha (requer numpy).
4. `ffmpeg -framerate 30 -i frames/f%04d.jpg -i trilha.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -shortest -movflags +faststart ../clausa-anuncio.mp4`
