# Ferramentas de vídeo do Clausa

Instalar (sessão nova): `bash marketing/ferramentas/instalar.sh`

| Ferramenta | Para quê | Como usar aqui |
|---|---|---|
| **FFmpeg** | cortar, acelerar, tratar cor, juntar, áudio | já vem no sistema; receitas no `GUIA-DA-MARCA.md` e em `gerar/` |
| **Remotion** | vídeo feito em React (animações, templates reutilizáveis) | `npx remotion render remotion/src/index.jsx Teste out/x.mp4 --browser-executable=$CHROME` |
| **Hyperframes** | vídeo feito em HTML + GSAP; mede referências (`measure`), batidas (`beats`), compara cores (`grade-compare`) | ver variáveis abaixo; exemplo em `teste-hf/` |
| **Whisper** (faster-whisper) | transcrever fala com tempo de cada palavra (legendas, conferir locução) | `python3 transcrever.py arquivo.mp3 large-v3 pt` → `arquivo.mp3.palavras.json` |
| **yt-dlp** | baixar vídeo de sites | YouTube/Instagram pedem login vindo de servidor; **não** usar cookies da conta do Pedro. Só para referência, nunca para republicar |

Navegador para Remotion/Hyperframes (já instalado no ambiente):
```
export CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
export PUPPETEER_EXECUTABLE_PATH=$CHROME DO_NOT_TRACK=1 HYPERFRAMES_NO_TELEMETRY=1 HYPERFRAMES_SKIP_SKILLS=1
```
- Hyperframes: telemetria desligada pelas variáveis acima; `init` com `--skip-skills` (não instalar "skills" no ambiente). Funções de conta HeyGen (publish, share, templates Pro, reverse, billing) não são usadas.
- GSAP: os modelos do Hyperframes buscam a GSAP num CDN; usar a cópia local (`node_modules/gsap/dist/gsap.min.js`).
- Whisper: `small` é rápido (~8 s) mas erra palavras ("fora" no lugar de "foro"); para legendas e conferência use `large-v3` (~1–2 min na primeira vez, baixa o modelo).

Licenças: Remotion é gratuito para pessoa física e empresas de até 3 pessoas (acima disso exige licença paga); Hyperframes Apache-2.0; GSAP gratuita; faster-whisper MIT; yt-dlp Unlicense.
