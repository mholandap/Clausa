# Reel "Bom dia, Jarvis": roteiro

Formato da referência (vídeo de 74 s no Drive, `0 - Referências`): quarto escuro, a pessoa de lado ou de costas, monitor com uma tela "futurista", "BOM DIA / J.A.R.V.I.S" fixo no topo e legenda de uma palavra por vez. O assistente lê o resumo do dia e no fim a pessoa sai e deixa ele falando sozinho.

**Nossa virada:** tudo o que o Jarvis fala é **real**, tirado do Instagram, do LinkedIn e do repositório do Clausa. No lugar das notícias entra **uma dica de contrato com o artigo de lei**.

- Duração: ~55 s
- Vozes: Pedro, com a própria voz, gravada no celular. Jarvis com voz do ElevenLabs, **diferente da do Matheus** (sugestão: uma voz calma e grave, tipo "mordomo").
- No Instagram: marcar **conteúdo gerado por IA** (`isAiGenerated`).

---

## Roteiro (dados de quarta, 25/11/2026)

| # | Quem | Fala | Na tela (monitor / legenda) |
|---|---|---|---|
| 1 | **Pedro** | Bom dia, Jarvis. | Pedro entra no quadro, de lado, e liga o monitor. A tela acende. |
| 2 | **Jarvis** | Bom dia, Pedro. O mundo não parou enquanto você dormia. Vamos lá. | Círculo central pulsando (a balança do Clausa no meio). |
| 2b | **Jarvis** | Lá fora, em Brasília, faz vinte e três graus. Hoje vai de vinte e três a trinta e um. A chance de chuva é de quarenta e três por cento. | Cartão "BRASÍLIA": 23°, 23–31°, 43%. |
| 3 | **Jarvis** | No Instagram, o Reel de ontem teve quarenta e uma curtidas e vinte e um comentários. | Cartão "INSTAGRAM": 41 curtidas, 21 comentários. |
| 4 | **Jarvis** | Quatro em cada dez pessoas que assistiram ainda não te seguem. | Barra 59% seguidores / 41% não seguidores. |
| 5 | **Jarvis** | No LinkedIn, duas advogadas responderam. Uma vai testar o Clausa esta semana. A outra pediu o link. | Cartão "LINKEDIN": 2 respostas. **Sem nomes.** |
| 6 | **Jarvis** | Ontem foram quinze melhorias publicadas no Clausa. Agora ele instala no celular, como um aplicativo. | Contador subindo até 15; ícone do app. |
| 7 | **Jarvis** | Hoje, às dez e cinco, sai o Reel dos cinco avisos que não valem nada. | Cartão "AGENDA": 10:05, 5 avisos. |
| 8 | **Jarvis** | Agora, a dica do dia. Multa de contrato exagerada pode ser reduzida pelo juiz. Está no artigo quatrocentos e treze do Código Civil. | Cartão "DICA": art. 413 do Código Civil. |
| 9 | **Jarvis** | Quer que eu prepare a mensagem para a advogada que vai testar? | Cursor piscando num rascunho. |
| 10 | **Pedro** | Prepara. E me lembra às seis de responder os comentários. Valeu. | Pedro pega o café e se levanta. |
| 11 | **Jarvis** | Pronto, Pedro. A mensagem está esperando a sua revisão. | Rascunho "PRONTO PARA REVISAR". |
| 12 | **Jarvis** | Pedro? | Cadeira vazia. |
| 13 | **Jarvis** | Me deixou falando sozinho. De novo. | A tela escurece devagar. Logo do Clausa e @pedrom.holanda. |

### Por que cada fala é verdade
- 41 curtidas, 21 comentários e 59/41%: print dos Insights que o Pedro mandou em 24/11, às 19h.
- Duas advogadas: retornos que o Pedro contou em 24/11 (uma vai testar na semana, uma advogada solo pediu o link).
- 15 melhorias: 15 mudanças (pull requests #11 a #25) publicadas no `main` em 24/11, incluindo o app instalável (#22 e #23).
- Clima: previsão de Brasília (wttr.in) às 8h de 25/11: 23 °C agora, mínima 23, máxima 31, até 43% de chance de chuva. **Muda todo dia: conferir na hora de gravar.**
- Agenda: Metricool, "5 avisos" agendado para 25/11, às 10h05.
- Dica: Código Civil, art. 413: "A penalidade deve ser reduzida equitativamente pelo juiz se a obrigação principal tiver sido cumprida em parte, ou se o montante da penalidade for manifestamente excessivo". https://www.planalto.gov.br/ccivil_03/leis/2002/l10406compilada.htm
- Mensagem para a advogada: está pronta em `mensagem-acompanhamento.md`, ou seja, a fala 11 também é verdade.

**Se gravar em outro dia:** atualizar as falas 2b a 7 com os números do dia (eu refaço em 5 minutos). A fala 8 pode trocar por outra dica com artigo (sugestões abaixo).

### Dicas reserva (todas com fonte)
- "Comprou pela internet? Você tem sete dias para desistir. Artigo quarenta e nove do Código de Defesa do Consumidor."
- "Cláusula que te faz abrir mão de um direito num contrato de adesão é nula. Artigo quatrocentos e vinte e quatro do Código Civil."
- "Na dúvida, cláusula de contrato de adesão se interpreta a favor de quem aderiu. Artigo quatrocentos e vinte e três do Código Civil."

---

## Texto só do Jarvis (para colar no ElevenLabs)

Gerar cada bloco separado e salvar como `01.mp3`, `02.mp3`… na ordem abaixo.

```
Bom dia, Pedro. O mundo não parou enquanto você dormia. Vamos lá.
```
```
Lá fora, em Brasília, faz vinte e três graus. Hoje vai de vinte e três a trinta e um. A chance de chuva é de quarenta e três por cento.
```
```
No Instagram, o Reel de ontem teve quarenta e uma curtidas e vinte e um comentários. Quatro em cada dez pessoas que assistiram ainda não te seguem.
```
```
No LinkedIn, duas advogadas responderam. Uma vai testar o Clausa esta semana. A outra pediu o link.
```
```
Ontem foram quinze melhorias publicadas no Clausa. Agora ele instala no celular, como um aplicativo.
```
```
Hoje, às dez e cinco, sai o Reel dos cinco avisos que não valem nada.
```
```
Agora, a dica do dia. Multa de contrato exagerada pode ser reduzida pelo juiz. Está no artigo quatrocentos e treze do Código Civil.
```
```
Quer que eu prepare a mensagem para a advogada que vai testar?
```
```
Pronto, Pedro. A mensagem está esperando a sua revisão.
```
```
Pedro?
```
```
Me deixou falando sozinho. De novo.
```

Números por extenso de propósito: a voz lê melhor.

---

## Tela do monitor
Link: https://mholandap.github.io/Clausa/marketing/jarvis/tela.html (usar o **Chrome**).

1. Abra o link e **clique uma vez** na tela. O Chrome pede o microfone: permita. No topo aparece "● OUVINDO".
2. Aperte **F11** (tela cheia).
3. Comece a gravar no celular e diga **"Bom dia, Jarvis"**: a tela acende sozinha.
4. Ela anda no ritmo do roteiro e **para na pergunta** ("Quer que eu prepare a mensagem…?"), mostrando "OUVINDO…".
5. Diga **"Prepara…"**: ela continua, digita a mensagem, mostra "PRONTO PARA REVISAR", chama "Pedro?" e fecha com o logo.

Sem microfone, o **espaço** faz as duas coisas (começar e continuar). **R** reinicia.

**Voz ao vivo:** gere as 11 falas no ElevenLabs e salve em `marketing/jarvis/audio/` como `01.mp3` a `11.mp3`, na ordem dos blocos abaixo (ou me mande e eu coloco). Aí o Jarvis fala pelo alto-falante na hora certa. Na edição eu troco pelo áudio limpo, sem eco do quarto.

Limites: ele só reconhece essas duas frases. As respostas são gravadas, não é conversa livre.

## Como gravar (Pedro)
1. Quarto escuro, só o monitor e uma luz quente pequena de lado (abajur ou luminária). A referência funciona porque o rosto quase não aparece.
2. Celular **na vertical**, apoiado, atrás e um pouco acima do ombro, pegando você de lado e o monitor inteiro.
3. Grave **um take só, contínuo**, de ~60 s: entra, fala "Bom dia, Jarvis", fica ouvindo (a voz eu coloco depois), mexe no mouse ou toma café e, na fala 10, levanta e sai do quadro. Deixe gravando mais 8 s com a cadeira vazia.
4. Mande o vídeo **como documento** no WhatsApp ou suba no Drive em `1 - Brutos/2026-11-25`.

Na edição eu ponho: a voz do Jarvis, "BOM DIA / J.A.R.V.I.S" fixo no topo (Inter Tight 900, branco, com "BOM DIA" pequeno em laranja), a legenda palavra por palavra e a música própria bem baixa.

---

## Legenda do post

```
Pedi pro Claude virar o meu Jarvis. 🤖

Tudo o que ele fala no vídeo é real: os números do meu Instagram, as respostas no LinkedIn e o que mudou no Clausa ontem.

E a dica vale pra qualquer contrato: multa exagerada pode ser reduzida pelo juiz (art. 413 do Código Civil).

O Clausa aponta as cláusulas que merecem atenção antes de você assinar. Teste grátis: mholandap.github.io/Clausa

Qual pergunta você faria pro seu Jarvis de manhã? 👇

#buildinpublic #startup #empreendedorismo #inteligenciaartificial #claude #contratos #direito #legaltech
```
