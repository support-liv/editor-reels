# Montar um projeto novo

Cada evento ou campanha tem uma pasta em `projetos/` com um ou mais **lotes**: arquivos Python que listam os vídeos finais. Assim dá para refazer tudo com um comando quando um padrão muda.

## 1. Copie o modelo
```bash
cp -R projetos/_modelo projetos/nome_do_projeto
```

## 2. Aponte a pasta dos brutos
No `lote_modelo.py`, ajuste `PASTA_PROJETO` (ou use a variável de ambiente, como no IN26: `export IN26_DIR=...`).

## 3. Transcreva e audite
Ver [FLUXO.md](FLUXO.md), passos 2 e 3.

## 4. Preencha a lista `VIDEOS`
Cada linha é um vídeo final:
```python
("V01", "nome_curto", PASTA + "IMG_1234.MOV", "2.1-8.1,8.5-16.3,45.6-48.0",
 "Gancho em caixa alta com bandeira 🇺🇸", {"pessoa": None, "y_legenda": 0.62}),
```
- **trechos:** faixas do bruto em segundos, na ordem final. `?` marca pergunta; `@1`/`@2` força quem aparece.
- **gancho:** frase curta. Bandeira sempre depois da palavra.
- **extras:** `pessoa` (`None`, `"direita"`, `"esquerda"`, `"voz"`), `aperto`, `y_legenda`.

Dica: comece os trechos um pouco antes e termine um pouco depois da fala. O ajuste pelo áudio aperta sozinho.

## 5. Confira e renderize
```bash
python3 projetos/nome_do_projeto/lote_modelo.py --so-cortes
python3 projetos/nome_do_projeto/lote_modelo.py
```

## Exemplos reais
`projetos/in26/` tem três lotes completos:
- `lote_ricardo.py`: entrevista com o entrevistado à direita. Séries R (resposta), P (pergunta + resposta) e B (topo de funil).
- `lote_andre_julia.py`: solos (pergunta fora do quadro) e conversa com três pessoas (`--pessoa voz`).
- `lote_ads.py`: anúncios (sem caixa de CTA, legenda a 55%, selfie a 64%).
