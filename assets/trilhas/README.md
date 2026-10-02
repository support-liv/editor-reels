# Banco de trilhas

143 trilhas (MP3 128 kbps, Git LFS) analisadas por `editor/trilhas.py`: BPM, tom (maior/menor), energia,
brilho, loudness, clima e **licença**. Os originais ficam com o time (pacote "PACK BG MUSIC").

- Nome: `clima__titulo__BPMbpm__tom.mp3` (ex.: `corporativo__skylines-anno-domini-beats__99bpm__A-maior.mp3`).
- `catalogo.json`: por faixa, `climas`, `marcas` (liv/imigrar), `licenca` (`status`: liberada | credito | conferir;
  `anuncio_pago`: sim | conferir | nao), medidas. Também lista as **19 bloqueadas** que ficaram fora do repositório
  (temas de franquias/jogos/filmes/youtubers, samples, Epidemic Sound) e 3 efeitos sonoros.
- Sugerir: `python3 editor/trilhas.py sugerir --clima corporativo --marca liv --anuncio --dur 30`.
- Pôr no vídeo: `python3 editor/trilhas.py mixar VIDEO.mp4 TRILHA.mp3 --ss 18` (trilha ~16 LU abaixo da fala
  e ducking: abaixa mais quando a pessoa fala).
- Antes de usar, o agente **auditor-de-trilha** (`.claude/agents/`) confere licença, clima, marca, ritmo e volume.
- **Licença em anúncio pago:** nenhuma faixa da LIV está confirmada para anúncio (são "conferir"). Confirmar nos
  termos da fonte (ex.: YouTube Audio Library fora do YouTube) antes de subir anúncio com trilha.
- Adicionar músicas: ponha numa pasta e rode `trilhas.py analisar PASTA` e `trilhas.py catalogar PASTA`.
