# Clausa — guia da marca e de edição

Referência para qualquer pessoa (ou sessão do Claude) que for criar conteúdo, vídeo ou tela do Clausa.

## 1. Quem fala
- **Perfil @pedrom.holanda (Instagram) e LinkedIn do Pedro:** perfil de **fundador**. Quem fala é o Pedro, em primeira pessoa, construindo o Clausa em público. O Clausa aparece como "o que eu estou construindo", não como autor.
- **Perfil @clausa (futuro):** voz da marca: produto, novidades, dicas em tom institucional, anúncios pagos.
- **Mistura de conteúdo no perfil do fundador:** ~metade dicas de contrato, ~um terço bastidores, o resto produto.

## 2. Regras que nunca mudam
1. **Só o que é verdade.** Hoje o teste grátis funciona por **regras**, não por IA. Não escrever "com IA" até a IA estar no ar. Sem números, clientes ou depoimentos inventados.
2. **A decisão é sempre do advogado/da pessoa.** O Clausa aponta, não substitui.
3. **Conteúdo jurídico correto.** Se citar lei, citar o artigo (ex.: art. 413 do Código Civil para redução de multa).
4. **Privacidade:** nunca mostrar nome, rosto ou voz de terceiros (ex.: advogado numa chamada) sem autorização.
5. **Música e imagens só com licença para uso comercial.** As trilhas atuais são sintetizadas do zero.
6. **Voz sintética (ElevenLabs etc.):** marcar "conteúdo gerado por IA" no Instagram. Plano grátis do ElevenLabs não permite uso comercial.
7. **Publicação:** posts novos só saem com o **aval do Pedro**. Mudanças no site/app podem ser publicadas direto (e depois relatadas).

## 3. Cores

| Uso | Nome | Hex |
|---|---|---|
| Fundo principal (escuro) | Grafite | `#0B0B0C` |
| Cartões / painéis | Grafite claro | `#161617` |
| Bordas | Linha | `#2A2A2D` |
| Texto principal | Branco | `#FAFAFA` |
| Texto secundário | Cinza | `#9B9B9E` |
| **Destaque / marca** | **Laranja Clausa** | **`#FF8A33`** |
| Botões / laranja profundo | Selo | `#E2590B` |
| Risco alto | Vermelho | `#F0625A` |
| Atenção | Amarelo | `#E0B65C` |
| Sem alerta | Verde | `#5FB58C` |

Tema claro do site: fundo `#EAEAEE`, texto `#1A1A1A`, laranja `#C2560A`.

**Texto sobre laranja:** usar quase-preto `#140A05`, nunca branco.

## 4. Tipografia (todas gratuitas, Google Fonts, licença OFL)
- **Site e app:** títulos em **Inter Tight** (700/800, espaçamento −0,03em), texto em **Inter** (400–600). Sem serifa: a mesma família dos vídeos.
- **Imagens do site:** capturas reais do app (`img/`), em moldura de navegador e celular. Nada de banco de imagens genérico.
- **Vídeos, carrosséis e Stories:** títulos em **Inter Tight Black (900)**, espaçamento apertado (−0,045em); texto em **Inter**.
  Motivo: título em serifa + laranja + fundo escuro lembrava a identidade do Claude; o sans pesado dá cara própria e de rede social.
- Links: https://fonts.google.com/specimen/Inter · https://fonts.google.com/specimen/Inter+Tight

## 5. Logo
- Símbolo: **balança** com haste fina, bolinha no topo, travessão reto com as pontas descendo, pratos em arco raso e base curta. Traço laranja `#FF8A33`, pontas arredondadas.
- Ícone de app: o símbolo sobre um quadrado grafite de cantos arredondados, com um brilho alaranjado suave no centro (é o favicon do site).
- Arquivos (vetor, servem em qualquer tamanho): `clausa-logo-app.svg` (ícone completo) e `clausa-simbolo-laranja.svg` (só o símbolo, fundo transparente). Original em PNG: `favicon.png` na raiz do repositório.
- Nome escrito: **Clausa** (C maiúsculo, resto minúsculo).
- Não esticar, não trocar a cor do símbolo, não pôr sombra.

## 6. Estilo dos vídeos
- **Formato:** 1080×1920, 9:16. Reels de 15–35 s. Volume em −14 LUFS.
- **Gancho nos primeiros 2 s:** um problema real em uma frase.
- **Legendas:** caixa grafite translúcida (`rgba(11,11,12,.72)`, cantos 22px), Inter Tight 900, palavra-chave em bloco laranja; palavras entram uma a uma. Ficam na **parte de baixo** (não cobrir rosto), respeitando ~340px livres no rodapé (interface do Instagram) e ~250px no topo.
- **Hora na tela (série de bastidores):** pílula grafite com ponto laranja + `17:20`.
- **Barra de progresso** laranja fina no topo.
- **Tratamento de cor (ffmpeg):**
  `hqdn3d=1.5:1.5:6:6, eq=contrast=1.08:saturation=1.10:gamma=1.06, colorbalance=rs=-0.02:bs=0.02:rh=0.035:bh=-0.03, unsharp=5:5:0.55, vignette=PI/5`
  → menos ruído, contraste e cor um pouco mais vivos, calor leve na pele, nitidez e vinheta suaves.
- **Planos 3:4:** imagem inteira centralizada + fundo desfocado (não esticar).
- **Trilha:** lo-fi suave (~88 BPM), whoosh leve nos cortes, som ambiente real quando houver.
- **Final:** chamada clara ("Segue pra acompanhar", "Teste grátis", endereço do site).

## 7. Séries
- **"Uma tarde/Um dia construindo o Clausa":** clipes reais do dia (café, trabalho, testes), hora na tela, tudo verdadeiro. Rosto opcional; ângulos de lado/por trás.
- **Dicas de contrato** (ex.: "3 palavras perigosas", carrossel "Renovação automática"): animação no visual da marca + locução.
- **Produto:** o app funcionando.

## 8. Como gravar (para o Pedro)
- Celular apoiado, **na vertical**, lente limpa, luz de frente ou de lado.
- Clipes de 10–15 s (eu corto); blocos longos em time-lapse.
- No WhatsApp, enviar **como documento** (sem compressão) — ou subir no Drive em `1 - Brutos/AAAA-MM-DD`.

## 9. Endereços
- Site: https://mholandap.github.io/Clausa/ (C maiúsculo)
- App: https://mholandap.github.io/Clausa/app.html
- Instagram: @pedrom.holanda · Metricool: marca 8184609 (fuso America/Sao_Paulo)
- Arquivos de vídeo e fontes de edição: `marketing/` neste repositório
