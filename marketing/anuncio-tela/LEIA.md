# Anúncio de tela ("Pedi para o Claude criar um anúncio")

Anúncio 16:9 para passar em tela cheia no notebook e filmar com o celular (formato de Reel de referência).

- `anuncio-tela.html`: o anúncio (tipografia em movimento, documento grifado, celular com o app, final com logo). `window.render(t)` desenha o instante `t`.
- `render.js`: `node render.js anuncio-tela.html pasta 60` gera os quadros (ou `preview 1.5 3.2 ...` para prévias).
- `musica.py`: trilha própria a 120 BPM, com impacto em cada corte (múltiplos de 0,5 s). Sem amostras de terceiros.
- `celular.jpg`: captura real do app.

Montagem:
```bash
ffmpeg -framerate 60 -i quadros/f%05d.jpg -i trilha.wav -af loudnorm=I=-14:TP=-1.5 -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest anuncio-tela.mp4
```

Como filmar: notebook em tela cheia, brilho no máximo, luz do quarto apagada, celular na vertical a ~50 cm, um pouco acima do teclado, sem tremer. Grave uns 3 s antes de dar play e 2 s depois do fim.
