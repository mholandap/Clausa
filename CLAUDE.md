# Clausa: onde paramos (leia antes de começar)

Projeto do Pedro (GitHub `mholandap`, Instagram `@pedrom.holanda`). Clausa = app que aponta cláusulas de atenção em contratos. Hoje funciona **por regras, sem IA**.
- Site: https://mholandap.github.io/Clausa/ · App: `app.html` · Login: Supabase (`js/clausa-config.js`).
- Responder sempre em português do Brasil, linguagem simples.

## Regras combinadas com o Pedro
- **Site/app/repositório:** pode alterar sem perguntar. Fluxo: branch de trabalho → PR → merge em `main` (GitHub Pages publica) → contar o que mudou.
- **Posts novos em rede social:** só com o "pode publicar" dele, com horário. Agendados já aprovados saem sozinhos.
- **Só verdade nos posts:** nada de "com IA" até a IA existir; nada de números, clientes ou depoimentos inventados. Conteúdo jurídico com fonte (ver `marketing/avisos/LEIA.md`).
- **Nunca** pedir/aceitar senha ou cookie de Instagram/LinkedIn. LinkedIn só com o Claude in Chrome na máquina dele, com ele revisando e enviando (roteiro em `marketing/linkedin/abordagem.md`). Nada de envio em massa.
- Não mudar compartilhamento de arquivos no Drive: ele mesmo coloca "Qualquer pessoa com o link".
- Voz sintética (ElevenLabs/Matheus) → marcar `isAiGenerated` no Instagram. Música só própria (`marketing/anuncio-tela/musica.py`).
- Não mostrar dados de terceiros (nomes, perfis, mensagens) sem desfocar.
- **Gosto do Pedro:** ler a seção 10 de `marketing/GUIA-DA-MARCA.md` antes de criar qualquer peça (vertical 1080×1920 para Reels, sem vazio, nada desfocado/opaco, sem "cara de Claude", música leve e contínua).

## Ferramentas
- Metricool: marca `8184609`, fuso `America/Sao_Paulo`. Mídia via URL pública `raw.githubusercontent.com/mholandap/Clausa/main/...`.
- Drive: pastas "Clausa — Vídeos" → `0 - Referências`, `1 - Brutos`, `Marca`. Baixar com `drive.usercontent.google.com/download?id=...&export=download&confirm=t` depois que ele compartilhar.
- Vídeo: `marketing/anuncio-tela/render.js` (quadro a quadro, `LARG=1080 ALT=1920` para vertical), ffmpeg, Whisper (`marketing/ferramentas/transcrever.py`), máquina de vídeo em `marketing/maquina/`.
- Banco: tarefa `.github/workflows/manter-banco-ativo.yml` evita a pausa do Supabase grátis.
- App instalável (PWA): `manifest.webmanifest`, `sw.js`, `js/instalar.js`. **Ao mudar `app.html`, atualize `<meta name="clausa-versao">` (AAAAMMDDhhmm):** é ela que faz o app avisar "Tem uma versão nova" no celular.

## Agenda do Instagram (atualizado em 26/11/2026)
- Ter 24/11 18h: anúncio vertical "Dia 2 construindo o Clausa" (`marketing/anuncio-tela/anuncio-vertical.mp4`).
- Qua 25/11 10h05: Reel "5 avisos que não valem nada", narrado (`marketing/avisos/avisos-narrado.mp4`). Publicado.
- Qui 26/11 ~10h30: Reel "Bom dia, Jarvis" (`marketing/jarvis/reel/bom-dia-jarvis.mp4`), postado pelo Pedro no celular com música da biblioteca do Instagram (Sweet Child O' Mine) e rótulo de IA. Música de terceiros só pela biblioteca do app, nunca embutida no arquivo; Metricool não consegue pôr música (conta sem Página do Facebook).
- Sex 27/11 10h: Reel "3 palavras".
- Qua 02/12 10h: carrossel "Renovação automática".
- Rascunho (não sai): anúncio com voz do Matheus "Comecei a construir uma coisa".

## Pendente
- **Jarvis (resumo diário automático):** tarefa agendada que lê o Gmail conectado (cadastros do site, alertas do Supabase, avisos de conta, respostas do LinkedIn), o Metricool (posts de ontem, agenda de hoje) e o status do banco, e manda notificação no celular. Nunca envia e-mail (só rascunho), nunca publica, nunca apaga. Pendente do Pedro: horário (sugestão 8h) e apontar o Formspree para o mesmo e-mail que está conectado.
- **Jarvis automático:** fica só "Jarvis: resumo diário do Clausa" (7h50); o das 7h37 foi desativado em 26/11. Pendente: Pedro adicionar os conectores Gmail e Metricool nele pelo claude.ai.
- **Jarvis ao vivo (R$ 0, ligado em 26/11):** `marketing/jarvis/ao-vivo.html` lê o último resumo da tabela `jarvis_resumos` (só o dono logado), fala com a voz do Edge (Antônio) e conversa via função do Supabase `jarvis-conversa` (Gemini grátis, segredo `GEMINI_API_KEY` no Supabase; projeto Google "Clausa IA"). O das 7h50 salva via `rpc/jarvis_salvar`; o token `x-jarvis-token` está guardado no ambiente Default (nunca no chat). SQL em `supabase/jarvis.sql`, função em `supabase/functions/jarvis-conversa/`. Gemini grátis: não mandar contrato de cliente. Pesquisa (v7): Gemini 2.5 deu 404 (aposentado); quem responde é `gemini-flash-lite-latest` com ferramentas próprias (Google Notícias RSS e cotação open.er-api.com). v8: 2.5 removidos, função "aquecida" ao abrir a tela, fala "Um instante, senhor" se demorar. Pedro cola o código pelo painel (Edge Functions → Code → Deploy).
- Tela do Jarvis: `marketing/jarvis/tela.html` (teclas: espaço começa, C continua, F tela cheia, H esconde relógio, D mostra o que o microfone ouviu). Lição: não processar demais a voz do Pedro; gravar no próprio ambiente.
- Reel com foto/print do Claude trabalhando no LinkedIn: legenda sóbria nas cores do Clausa; Pedro vai mandar inspiração e a foto no Drive. Desfocar dados de terceiros.
- Stories da semana (ideias: chamada para o post das 18h; enquete dos 5 avisos; "instale o app"; time-lapse). Figurinhas de link/enquete o Pedro adiciona à mão.
- Time-lapse da gravação que o Pedro fez de si mesmo em 24/11 (ele vai mandar).
- Play Store (≈ R$ 180) e versão com IA (≈ R$ 240–620/mês) ficam para quando houver dinheiro; custos em detalhe na conversa de 24/11.
- Decisões em aberto: voz clonada no ElevenLabs (plano pago), concorrentes no Metricool (exige Facebook ligado), frequência de posts (sugestão: 3 por semana).
