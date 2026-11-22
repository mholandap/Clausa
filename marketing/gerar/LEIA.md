# Como regerar o anúncio

1. Edite textos/tempos em `../anuncio.html` (abra no navegador para ver a prévia em loop).
2. `node render.js full frames 60` — gera 1020 quadros (17 s a 60 fps). Requer Playwright.
3. `python3 audio.py trilha.wav` — sintetiza a trilha (requer numpy).
4. `ffmpeg -framerate 60 -i frames/f%04d.jpg -i trilha.wav -c:v libx264 -crf 21 -pix_fmt yuv420p -c:a aac -shortest -movflags +faststart ../clausa-anuncio.mp4`
