# Opções

## editor/editor_reels.py

```bash
python3 editor/editor_reels.py VIDEO [opções]
```

### Conteúdo
| Opção | O que faz |
|---|---|
| `--trechos "a-b,c-d"` | Usa só essas faixas do bruto (segundos), **na ordem escrita** (podem estar fora de ordem). Sem `--trechos`, usa o vídeo todo |
| `a-b?` (dentro de `--trechos`) | Essa faixa é a pergunta do entrevistador. Em cena com várias pessoas, sai em quadro aberto |
| `a-b@1` / `a-b@2` | Força quem aparece nessa faixa (1 = pessoa mais à esquerda). Use quando o tom de voz errar |
| `--pergunta "a-b"` | Pergunta que abre o vídeo (equivale a `a-b?` no começo) |
| `--comecar "palavras"` / `--terminar "palavras"` | Começa ou termina nessas palavras |
| `--tirar "96.52-97.07"` | Tira um trecho exato do bruto, em segundos (gagueira, palavra repetida, travada). Pode repetir |
| `--remover "trecho"` | Tira uma frase específica (pode repetir) |
| `--manter-perguntas` | Sem `--trechos`, o editor tira sozinho as falas que terminam em "?". Isso desliga esse filtro |
| `--trocar "errado=certo"` | Corrige a legenda (pode repetir). Ex.: `--trocar "um gente sério=com gente séria"` |

### Visual
| Opção | O que faz |
|---|---|
| `--marca imigrar` / `liv` | Cores: rosa Imigrar / laranja e azul LIV |
| `--gancho "texto"` | Caixa nos primeiros 3,2s, em caixa alta. Aceita 🇺🇸 e 🇧🇷 |
| `--cta "texto"` | Caixa nos últimos 3,5s |
| `--cta-animado PERFIL` | CTA animado da marca ("Comente PERFIL") nos últimos 4s, no lugar da caixa. `--cta-rotulo` muda o "Comente" |
| `--broll arq.mov@fonte:8.4` | **B-roll de motion**: cena por cima da imagem, embaixo da legenda, com os efeitos sonoros dela mixados por baixo da voz. `@fonte:` = tempo da fala no bruto (o editor converte); `@12.5` = tempo do vídeo pronto. Pode repetir |
| `--sem-legenda` | Não queima legenda. Só quando o vídeo de origem **já tem legenda gravada** (senão duplica) |
| `--animacao arq.mov@12.5` | Cola uma animação transparente (feita em `motion/`) nesse segundo do vídeo pronto. Pode repetir. Proporção tem que ser a mesma do vídeo |
| `--y-legenda 0.62` | Altura da legenda (fração da tela). Orgânico 0.62, anúncio 0.55, selfie 0.64 |
| `--cor-caixa` | Estilo da tarja do gancho/CTA, só com cores da marca. **Imigrar:** `branco`, `azul` (#0E59C5), `rosa` (#F90D5B). **LIV:** `azul` (#2C3642), `laranja` (#FF6E1F), `bege` (#FFF0E6), `marrom` (#945943) |
| `--layout dividido` | Live com duas pessoas lado a lado: uma em cima, outra embaixo, enquadramento fixo, legenda e tarja na divisa |
| `--cima esquerda` / `direita` | Na tela dividida, quem da live vai em cima |
| `--layout youtube` | Corte longo 16:9 1080p: a cena inteira da live, sem legenda e sem gancho, com a vinheta da marca na abertura (LIV). Tira só silêncios longos (respiro 0,8s). Gera junto um `.tempos.txt` com a minutagem de cada trecho, para os capítulos |
| `--sem-vinheta` | No `youtube`, não põe a vinheta |
| `--layout quadrado` | WhatsApp: 1080x1080, punch-in alternando por bloco de fala, legenda perto da base |
| `--dinamico` | Troca o zoom a cada ~2,5s entre palavras, em 3 níveis, sem cortar a fala. Pra quem fala mais travado |
| `--endireitar` | Quadrado: mede as verticais da cena e escolhe o ângulo de `--girar` sozinho. Só gira, nunca distorce |
| `--girar 5` | Corrige câmera torta, em graus (positivo = anti-horário). Use as linhas verticais da cena como referência |
| `--layout quadro` | Live com uma pessoa: imagem nítida no meio (sem a faixa do chat), fundo desfocado, gancho acima e legenda abaixo, enquadramento fixo |

### Enquadramento
| Opção | O que faz |
|---|---|
| (nenhuma) | Uma pessoa: segue o rosto maior |
| `--pessoa direita` / `esquerda` | Duas pessoas: fecha em quem está desse lado |
| `--pessoa voz` | Conversa: fecha em quem fala, pelo tom de voz (grave = 1ª da esquerda, aguda = 2ª) |
| `--aperto 0.5` | Fração da largura original mantida (menor = mais fechado). Padrões: 0.93 solo, 0.55 com `--pessoa`, 0.34 com `voz` |

### Cortes pelo áudio
| Opção | O que faz |
|---|---|
| (padrão) | Corta onde a voz começa e termina de verdade e tira pausas internas acima de 0,25s |
| `--respiro 0.5` | Mantém pausas internas até esse tamanho (s). Maior que 0,25 = fala mais natural (quem fala pausado); menor = mais enxuto. **Shorts: 0.18** |
| `--tirar-hesitacoes` | Tira "éé", "hmm", "ah", "e..." esticado, "então, assim" seguido de pausa e voz sem palavra. Mostra no terminal o que tirou. Padrão nos shorts |
| `--json-cortes ARQ` | Salva o plano de cortes e sai (usado pelo `motion/remapear.py` quando o corte muda depois do motion pronto) |
| `--sem-ajuste-audio` | Usa só o tempo do Whisper (mais folgado) |

### Conferência sem renderizar
| Opção | O que faz |
|---|---|
| `--so-cortes` | Mostra os pedaços e o texto de cada um |
| `--checar-olhar` | Junto com o plano, avisa pedaços com a pessoa olhando pra baixo/lado |
| `--so-checar-caixas` | Diz onde o gancho e o CTA vão ficar |

### Saída
| Opção | O que faz |
|---|---|
| `--nome NOME` | Nome do arquivo (sem extensão) |
| `--saida PASTA` | Pasta do arquivo (padrão: `./prontos`) |

## editor/carrossel.py
```bash
python3 editor/carrossel.py roteiro.json --saida PASTA
```
Carrossel 1080x1350 na fonte e nas cores da marca: capa (com foto ou quadro de vídeo `arquivo.mp4@12.5`), cards de texto e card de CTA. O formato do `roteiro.json` está no começo do arquivo. A foto nunca é distorcida (amplia por igual e recorta).

## editor/auditar.py
```bash
python3 editor/auditar.py VIDEO [VIDEO ...]
```
Cada frase do bruto com a % do tempo olhando pra baixo ou pro lado. ▼ = provável leitura do celular.

## editor/auditar_pronto.py
```bash
python3 editor/auditar_pronto.py ARQUIVO.mp4 [...]
```
Silêncio no início e no fim, pausas maiores que 0,35s e trechos de 0,75s ou mais olhando pra baixo.

## editor/transcrever_lote.py
```bash
python3 editor/transcrever_lote.py VIDEO [VIDEO ...]
```
Transcreve vários de uma vez (fica salvo em `editor/transcricoes/`).

## Correções automáticas de legenda
O editor já corrige erros comuns do Whisper em termos de imigração e odonto (INBDE, board, TOEFL, EB-1, EB-2 NIW, Imigrar EUA, LIV, higienista…). A lista fica em `CORRECOES`, dentro de `editor_reels.py`. Acrescente termos novos lá.
