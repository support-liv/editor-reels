# Enquadramento da tela dividida (shorts de live): auditoria e guardrails

Auditoria feita na LIVE 81 (out/2026), depois de o time apontar nos shorts: **muito espaço acima da cabeça da
Dra. Lívia** e, em alguns momentos, **a cabeça cortada no topo**.

## O que estava errado

Na tela dividida (`--layout dividido`), cada pessoa vira um painel de 1080x960. O editor recortava da live um
retângulo de **88% da metade da largura** (845x750 px numa live 1920x1080) e o limitava a terminar em **70% da
altura** (756 px), para não pegar o chat e os banners que o StreamYard põe embaixo.

Com 750 px de altura e fim máximo em 756 px, o recorte só podia começar entre **0 e 6 px**: ficava **preso no topo
da imagem**. A regra "rosto a 42% do painel" nunca era aplicada. O espaço acima da cabeça dependia só de onde a
pessoa estava na webcam, e era um recorte só para o vídeo inteiro.

Quem fala numa webcam se mexe muito. Na LIVE 81, o topo da cabeça da Dra. Lívia variou de **8% a 29% da altura da
imagem** (inclinada para a câmera x encostada na cadeira). Um recorte fixo preso no topo dava:

| Short | Teto antes (mediana) | Teto depois (mediana) |
|---|---|---|
| S1 inglês na entrevista | 34% | 8% |
| S2 documentos da nova entrevista | 19% | 8% |
| S3 dois pedidos | 17% | 10% |
| S4 IA no processo | 32% | 8% |
| S5 área no EB-2 NIW | 28% | 11% |
| S6 estudante e green card | 14% | 10% |

"Teto" = espaço entre o topo do painel e o topo da cabeça, em fração da altura do painel. Medido com o detector de
rosto, 2 quadros/s, em todos os cortes de cada short.

Nos momentos em que ela se inclinava (entre uma amostra e outra), o cabelo encostava ou saía pelo topo. Em outros
momentos, com ela muito perto da câmera, o queixo descia para a faixa da legenda.

## Como ficou (editor 0.28)

1. **Zoom e posição lateral fixos por pessoa, altura decidida corte a corte.** Em cada corte o recorte se posiciona
   pelo topo da cabeça (o mais alto do corte, percentil 10), com a margem do painel. A mudança só acontece na
   emenda entre cortes, que já é um salto. Diferenças menores que 4% do painel são ignoradas (sem "pulinho").
2. **Margem por painel** (`MARGEM_TOPO`): em cima 8%, embaixo 16%. Embaixo é maior porque a legenda e a tarja ficam
   na divisa e não podem cobrir a cabeça de quem está no painel de baixo.
3. **Topo da cabeça = caixa do rosto + cabelo** (`FOLGA_CABELO` = 12% da altura do rosto). O detector marca da
   testa ao queixo; o cabelo sobe ~9-10% acima disso (medido) e o resto é folga para a inclinação que a amostragem
   perde.
4. **Zoom que cabe** (`zoom_que_cabe`): se a cabeça inteira (cabelo ao queixo, p90) não cabe entre a margem do
   topo e 10% de reserva embaixo, o recorte abre de 88% até 100% da metade da live (fixo no short). Na LIVE 81:
   S2 93%, S3 89%, S6 96%.
5. **`--sem-sobreposicao`**: para live **sem chat/banner na tela**, o recorte pode descer além dos 70%. Sem ele,
   quando o limite impede descer e o teto passa do máximo, o aviso sugere a opção. Confira no mosaico da live
   antes de usar (`ffmpeg -i LIVE.mp4 -vf "fps=1/240,scale=480:-1,tile=4x4" -frames:v 1 mosaico.jpg`).

## Guardrails (o editor confere sozinho)

Em todo render de tela dividida, o editor imprime o teto de cada painel e avisa:

| Aviso | Regra | O que fazer |
|---|---|---|
| cabeça cortada | mais de 10% das amostras de um corte com o topo da cabeça fora do painel | prévia; se a pessoa se mexe muito, dividir o corte ou trocar o trecho |
| queixo fora do painel | mais de 25% das amostras com o queixo abaixo do painel | o zoom já abre até 100%; se ainda assim, trocar o trecho |
| teto demais | teto mediano acima de margem + 13% (cima 21%, embaixo 29%) | `--sem-sobreposicao` se a live não tem chat; senão, prévia |
| limite da câmera (info) | a cabeça sai da própria webcam | nenhum recorte resolve; só informa |
| nenhum rosto detectado | painel sem detecção | conferir a prévia |

- **`--exigir-enquadramento`**: não renderiza se houver aviso. Os lotes de live usam essa opção nos renders.
- **`--previa-enquadramento ARQ.jpg`**: antes de renderizar, salva a folha de conferência (1 quadro do meio de
  cada corte, já montado na tela dividida) com as guias: **verde** = margem do topo de cada painel, **laranja** =
  início da faixa da legenda, **branco** = divisa. Sai sem renderizar.

## Fluxo para shorts de live (tela dividida)

1. Plano dos cortes (`--so-cortes --checar-olhar`).
2. **Prévia do enquadramento** (`lote ... previa`) e validação com o time: cabeça inteira abaixo do verde, queixo
   acima do laranja, nada de teto sobrando.
3. Render com `--exigir-enquadramento`.
4. Conferência dos quadros do vídeo pronto.

## Limites conhecidos

- A posição muda só na emenda entre cortes. Se a pessoa se inclina muito **dentro** de um corte longo, o corte
  continua com uma altura só (a mais alta do corte, para não cortar a cabeça).
- O modo `--colunas N --pessoas` (live com 3+ pessoas) ainda usa o recorte da coluna inteira, sem esse ajuste.
- Detector no Windows: OpenCV YuNet (o `auditar_pronto.py` ainda chama o detector do Mac e não roda no Windows).
