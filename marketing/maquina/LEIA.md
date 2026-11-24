# Máquina de vídeo do Clausa

Linha de montagem: **roteiro → narração → cenas → legendas → som → conferência**.
Você só aprova.

## Como usar

```bash
cd marketing/maquina
python3 maquina.py roteiros/teste-3palavras.json /caminho/de/trabalho          # vídeo completo
python3 maquina.py roteiros/teste-3palavras.json /caminho/de/trabalho --previa # só 6 quadros de prévia
```

O vídeo sai em `saidas/` (definido em `"saida"` no roteiro) e o relatório de conferência em `qc.json` na pasta de trabalho.

## O que cada peça faz

| Arquivo | Função |
|---|---|
| `roteiros/*.json` | O roteiro: áudio da narração e a lista de cenas (telefone ou monitor), com as falas de cada uma |
| `maquina.py` | Transcreve a narração (Whisper large-v3), acha onde cada cena começa, monta a linha do tempo, gera a trilha (música própria, sem direitos de terceiros), mixa, codifica e confere |
| `estudio.html` | O estúdio: bancada, celular com notificações, monitores retrô com cláusula grifada, câmera que desliza, legendas com palavra-chave em laranja |
| `render.js` | Fotografa o estúdio quadro a quadro (30 fps) |

## Conferência automática (QC)

- 1080×1920, 30 fps, entre 10 e 90 s
- Sem tela preta nem quadro congelado
- Volume −14 LUFS (padrão Instagram), pico ≤ −1 dB
- Re-transcreve o vídeo final e compara com o roteiro (≥ 85% igual)

Se algo falhar, o `qc.json` diz o quê, e o vídeo não deve ir para aprovação.

## Formato de cena

```json
{"tipo": "monitor", "numero": "01", "titulo": "Irrevogável",
 "fala": "Irrevogável e irretratável.",
 "clausula": "CLÁUSULA 3ª", "texto": "...", "destaque": "irrevogável e irretratável",
 "nota": "não pode voltar atrás"}
```

```json
{"tipo": "telefone", "hora": "9:41", "fala": "...",
 "notificacoes": [{"texto": "3 pontos de atenção neste contrato", "em": "três palavras"}]}
```

## Falta (depende de decisão)

- Voz clonada (ElevenLabs pago) → narração automática a partir do texto do roteiro
- Concorrentes no Metricool → busca automática de referências virais do nicho
- Agendamento → a máquina roda sozinha e manda para aprovação no app do Metricool
