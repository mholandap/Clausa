# Reel "5 avisos que não valem nada"

Vertical 1080×1920, 27 s, 60 fps, trilha própria (`../anuncio-tela/musica.py`). Placas genéricas, sem marca real.

Gerar:
```bash
LARG=1080 ALT=1920 node ../anuncio-tela/render.js avisos.html quadros 60
python3 ../anuncio-tela/musica.py trilha.wav 27.0
ffmpeg -framerate 60 -i quadros/f%05d.jpg -i trilha.wav -af "loudnorm=I=-14.5:TP=-2,alimiter=limit=0.79:level=false" -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -shortest avisos.mp4
```

## Base legal de cada aviso (conferida em 24/11/2026)
1. **Estacionamento, "não nos responsabilizamos por danos ou furtos ao veículo"**: Súmula 130 do STJ (a empresa responde por dano ou furto de veículo em seu estacionamento). https://scon.stj.jus.br/SCON/sumstj/toc.jsp?sumula=130
2. **Cinema, "proibida a entrada com alimentos comprados fora"**: STJ, REsp 744.602/RJ (2007) e decisão de 2016; venda casada, CDC art. 39, I. Vale quando o próprio cinema vende alimentos. https://www.migalhas.com.br/quentes/240907/proibir-entrada-no-cinema-com-alimentos-e-abusivo
3. **Bar, "multa por perda da comanda"**: prática abusiva, CDC art. 39, V; o controle do consumo é do estabelecimento. https://blogs.correiobraziliense.com.br/consumidor/perdeu-a-comanda-nao-se-preocupe-a-responsabilidade-e-da-empresa/
4. **Restaurante, "taxa de serviço obrigatória"**: a taxa é gorjeta e é opcional (Procon-SP, Idec). https://idec.org.br/node/27588
5. **Loja online, "não aceitamos devolução"**: direito de arrependimento em 7 dias para compras fora do estabelecimento, CDC art. 49. https://idec.org.br/dicas-e-direitos/direito-do-consumidor-devolucao

Cortados por base fraca ou discutível: consumação mínima, valor mínimo no cartão (Lei 13.455/2017 permite preço diferenciado).

Sugestão: pedir revisão do estudante de Direito antes de publicar e convidá-lo como colaborador.
