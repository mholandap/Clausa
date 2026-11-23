#!/bin/bash
# Instala as ferramentas de vídeo do Clausa (rodar uma vez por sessão nova: bash marketing/ferramentas/instalar.sh)
set -e
cd "$(dirname "$0")"
command -v ffmpeg >/dev/null || { apt-get update -q && apt-get install -y -q ffmpeg; }
PUPPETEER_SKIP_DOWNLOAD=1 npm ci --no-fund --no-audit           # Remotion, Hyperframes, GSAP (versões travadas no package-lock)
pip install -q yt-dlp==2026.10.26 faster-whisper==1.2.1          # yt-dlp e Whisper
echo "ok: ffmpeg $(ffmpeg -version | head -1 | cut -d' ' -f3) · remotion $(node -p "require('remotion/package.json').version") · hyperframes $(node -p "require('hyperframes/package.json').version") · yt-dlp $(yt-dlp --version)"
