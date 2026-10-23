# Corte de fala: erros que já aconteceram e como não repetir

Lições dos lotes **Imigrar · TI** (11 anúncios A/B + horizontal 4811) e **Imigrar · Ednaldo** (3 anúncios A/B + 15
Reels da conversa no carro), out/2026. Cada rodada voltou com erro que o time achou **ouvindo**: palavra comida,
final cortado, repetição, legenda errada. Leia antes de editar qualquer vídeo de fala.

## Por que o erro acontece

O Whisper é ótimo para saber **o que** foi dito, ruim para saber **quando** e ruim para ouvir **tudo**:

- **Tempo errado:** marca o tempo da palavra "no olho" (erra 0,1-0,5s; pior em palavra curta como "ou", "é", "mas")
  e **estica** o fim da palavra pelo silêncio seguinte (às vezes 1-2s). Cortar pelo tempo do Whisper come palavra.
- **Fala limpa demais:** o modo normal **apaga** repetição, gaguejada e recomeço ("sabia que, sabia que" vira um só).
  O que ele não escreve, o editor não vê e não tira.
- **Inventa:** numa respiração no fim do trecho ele escreve um "Então" que ninguém falou; com o prompt literal às vezes
  repete "e, e, e, e..." (alucinação).

Por isso o editor corta pelo **áudio** (volume + detector de voz Silero), com o tempo das palavras refeito pelo
**alinhamento forçado** (WhisperX), e o lote escolhe takes pela transcrição **literal**.

## Erros, causa e regra

| O que o time ouviu | Causa | Regra / correção (versão) |
|---|---|---|
| Final da fala cortado ("ele é", "favorável", "cortou o final porra") | Pedaço de take fechado no **início** da última palavra; último corte só 0,08s depois da voz | Pedaço termina no **fim** da última palavra (o lote estende); último corte = fim da palavra + 0,35s com fade de 0,12s (0.30) |
| Palavra curta sumindo ("ou", "mas", "é") | Tempo do Whisper errado; o plano cortava pausa pelo Whisper; bloco de voz sem palavra saía como hesitação | `--alinhar --vad --proteger-palavra`; o plano não corta pausa pelo Whisper; bloco curto fica com a palavra curta vizinha (0.30-0.31) |
| "a única forma de morar aqui depender" (sumiu o "é"); "do que dez anos" (sumiu o "há") | `norm()` tira o acento: "é" virou "e" esticado e "há" virou "hã" | Verbo "é" e "há" nunca são hesitação (0.30, 0.32) |
| Repetição: "sabia que, sabia que", "gira em torno" 2x, "mais de… mais de 100 mil" | O Whisper normal esconde a repetição dentro do tempo de uma palavra | Escolher takes pela transcrição **literal**; o lote transcreve cada pedaço e **não renderiza** com repetição (0.30) |
| "acha que precisa… precisa de uma empresa" (04) | O fim de um take e o começo do seguinte dizem a mesma palavra; o alinhamento puxou "precisa" para dentro do take | Trava de **repetição na emenda** no lote; tempos do pedaço medidos pelo tempo **alinhado** da palavra (0.32) |
| Gaguejada curta: "o, o itinerário", "um, um stamp", "uma, um desenvolvimento", "É, é muito" | A trava de repetição ignorava palavra de 1-2 letras | `--tirar-hesitacoes` tira a 1ª da dupla (com a pausa). "o O" e "no O," (o visto) não contam (0.32) |
| "per\|fil", "a\|ssim": pedaço da palavra sumindo | "f" e "ss" têm volume baixo: o editor via pausa no meio da palavra | Volume baixo dentro de palavra alinhada com o Silero ouvindo voz não é pausa; buraco ≤ 0,12s vira fala contínua (0.32) |
| "descubra" sem o começo (e3) | Um "E" de 0,1s com tempo do Whisper de 0,94s saiu como "e..." esticado e levou o começo da palavra seguinte | Duração do "e" medida pela voz real (Silero); hesitação tirada nunca invade a palavra vizinha (0.32) |
| Sílaba solta antes da fala (r6); "Unidos." e "não é?" no take errado | O alinhador atravessava a emenda entre takes | Alinhamento **take a take** (`pedacos`/`pedaco` na transcrição); o corte nunca passa da emenda (0.32) |
| r3 perdeu "mil e vinte e cinco" | Palavra com número ("2025,") o alinhador não lê: inventou o tempo e jogou as palavras seguintes para dentro do número | O número vai para o alinhador como foi **falado** (campo `falado`); sigla com número sem forma falada (E-2, O-1) fica com o tempo do Whisper (0.32) |
| r3 perdeu "onde" depois de "fortes," | "fortes," esticado em 1,8s no Whisper; a trava do alinhador (máx. 0,7s de diferença) recusou a correção | Perto de palavra esticada (>0,9s) o alinhador corrige até 2s (0.32) |
| "Então" fantasma no fim (r1) | O Whisper inventou a palavra numa respiração; o fim alinhado engolia o silêncio | Extensão do fim limitada; palavra de ligação solta no fim do vídeo sai (0.31) |
| "maior que o da, do Brasil" | A extensão automática do pedaço pegava de volta a gaguejada colada | Pedaço `"exato"` (4º item da tupla): tempos medidos à mão, sem extensão (0.32) |
| Fim fraco cortado ("Unidos" no 01, "vist-o"), começo baixinho pela metade ("e outros" no r10) | Borda da palavra abaixo do limiar de volume | Fim avança até 0,55s e começo recua até 0,35s enquanto Silero **e** volume ouvem voz (0.32) |
| Micro-corte de 20 ms com troca de zoom ("seu \| histórico") | Pedaços encostados depois de estender as bordas | Pedaços encostados viram um só (0.31-0.32) |

## Legenda (o Whisper escreve errado)

- **Green Card**: "wincard", "win card", "going card", "Green Car", "brincardio", "QMK" → regra única no `lote_ti.py`.
- **Vistos no formato oficial**: E-2, O-1, O-3, L-1, H-1B, EB-1, EB-2, EB-2 NIW, B1/B2, DS-160. "o O" falado é o O-1
  ("Moto 3" = O-3, "A1" = O-1).
- **Nomes em inglês**: Lake Nona ("lequinona"), Tavistock ("Tavstop"), USTA. Siglas do Brasil: ITR ("ICR"), IPTU ("PTU").
- **Concordância**: "perfil gratuitas" → "gratuita"; "estimativo" → "estimativa"; "turistar" ("tudo estar").
- Conferir a legenda **inteira** de todo vídeo antes de entregar (lista de palavras esperadas no
  `~/Library/Caches/editor-reels/auditoria_esperado/`).

## Imagem

- **Selfie na mão tremendo / zoom que não aparece:** `--crop-fixo` (recorte parado por bloco de fala) e `--punch`
  forte (0,72 TI; 0,80 Ednaldo). Seguir o rosto quadro a quadro soma ao balanço da câmera.
- **Legenda na boca:** abaixo do queixo (`--y-legenda 0.62` TI; 0.66 selfie fechada). Conferir em quadros.
- **Câmera torta (4811):** só girar e recortar a área útil (sem canto preto); zoom preso no topo para não perder a
  bandeira. Nunca distorcer.
- **Marca:** anúncio da Imigrar fica na identidade da Imigrar (Inter Tight, rosa/azul). A versão em serifa com tom
  pastel foi recusada.
- **B-roll de contexto** quando a fala cita lugar/objeto (vacas, casas, Lake Nona): conferir o quadro (crop das vacas).

## Processo que funcionou

1. Escolher os takes pela transcrição **literal** (`transcrever_literal.py`); conferir as emendas (fim de um take x
   começo do outro).
2. Renderizar em `_em_revisao/`, nunca direto em `prontos/`.
3. Auditar **todos** os vídeos:
   - checagem exata (sem ouvir, pelo tempo alinhado): corte dentro de palavra, palavra tirada, fala fora do corte;
   - fala ouvida x esperada (`auditoria.py`, leitura literal + normal), micro-conferência (`conferir_alertas.py`) e
     filtro do que as duas leituras confirmam (`filtrar_confirmados.py`);
   - sincronia áudio x vídeo (diferença ≤ 0,05s) e quadros (legenda, recorte, CTA).
4. Corrigir a **causa** no editor/lote (não só o vídeo), registrar aqui e no `CHANGELOG.md`, renderizar de novo só os
   afetados e auditar de novo.
5. Só então mover para `prontos/`.

O que a máquina **não** garante: entonação, ritmo e se a frase faz sentido depois do corte. Num lote novo, ouça pelo
menos um vídeo inteiro de cada tipo antes de mandar.

## Cuidados de operação (Mac de 8 GB)

- Não rode duas coisas pesadas juntas (Whisper da auditoria + render/alinhamento): a auditoria passou de ~2 para ~20
  minutos por vídeo.
- Rode a auditoria com `python3 -u` e grave o relatório por vídeo: com saída em buffer, interromper no meio perde tudo.
- Não regrave um vídeo que a auditoria ainda vai ler (o resultado dela fica misturado).
