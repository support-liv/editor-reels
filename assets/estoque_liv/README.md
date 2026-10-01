# Estoque interno de vídeos da LIV

Material próprio da LIV (Dra. Lívia, equipe, escritório, atendimento, processo) para usar como B-roll **só nos
vídeos da LIV**. Quando a fala é sobre **processo, petição, equipe, atendimento, análise de caso, advogados
licenciados**, use este estoque antes de qualquer banco de imagens externo.

- Versões 1080p (H.264, SDR BT.709) no Git LFS. Os originais 4K ficam no Google Drive da LIV.
- Nome = `orientação__quem__o-que-faz__onde__look__detalhe__duração`. O look (terno verde, risca de giz,
  blazer azul/xadrez/bege) ajuda a combinar cenas da mesma gravação.
- `catalogo.json` tem os mesmos campos separados. Buscar: `python3 editor/estoque.py buscar processo vertical`.
- Adicionar vídeos novos: renomeie no padrão e rode `python3 editor/estoque.py importar PASTA`.
- `uso_especial` (ex.: a filha da Dra. Lívia): só com pedido explícito. `outra_marca` (Marinna Damasio, da
  Imigrar): confirmar antes de usar num vídeo da LIV.
- Primeira vez no Mac: `git lfs install` (o `git pull` baixa os vídeos).
