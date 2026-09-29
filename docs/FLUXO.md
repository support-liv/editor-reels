# Fluxo de trabalho

Do vídeo bruto ao vídeo aprovado. Os exemplos usam o projeto `projetos/in26`.

## 1. Organizar os brutos
Coloque os vídeos numa pasta do projeto (ex.: `~/Desktop/IN26/ADS/`). Não renomeie os arquivos do iPhone: os lotes apontam pelo nome original.

## 2. Transcrever
```bash
cd ~/Desktop/IN26/ADS
python3 ~/editor-reels/editor/transcrever_lote.py *.MOV
```
Leva cerca de 1 min por minuto de vídeo. A transcrição fica salva em `editor/transcricoes/` e não é refeita.

## 3. Auditar os brutos (escolher os takes)
```bash
python3 ~/editor-reels/editor/auditar.py IMG_3442.MOV IMG_3443.MOV
```
Sai cada frase com o tempo e a % do tempo olhando pra baixo ou pro lado:
```
    22.9-  26.8 [  0%] Começar a se informar não significa que você vai se mudar amanhã.
▼   64.6-  68.4 [ 80%] Quer saber mais? Participe do nosso evento...   <- lendo o celular
    70.0-  75.2 [ 14%] Quer saber mais? Participe do nosso evento...   <- take bom
```
**Regra:** quando a mesma frase aparece duas vezes, a marcada com ▼ é leitura do roteiro. Use o take falado pra câmera (em geral, o seguinte).

Em selfie a % oscila porque o celular se mexe na mão. Nesses casos, confie no áudio e no seu olho.

## 4. Montar o lote
Cada vídeo final é uma linha no lote do projeto (ver [NOVO_PROJETO.md](NOVO_PROJETO.md)):
```python
("AD1b", "sonho_adiado_andando", D + "IMG_3442.MOV", "1.2-9.9,22.9-26.8,50.9-60.2,70.0-75.2",
 "Dentista, já pensou em morar nos EUA 🇺🇸?", 0.6),
```
Os trechos são faixas do bruto em segundos, na ordem em que devem aparecer. Marque `?` na pergunta do entrevistador (`22.4-24.7?`) e `@1`/`@2` para forçar quem aparece.

## 5. Conferir os cortes (rápido, sem renderizar)
```bash
python3 projetos/in26/lote_ads.py --so-cortes AD1b
```
Mostra o texto de cada pedaço. Veja se nenhuma frase ficou cortada no meio e se não sobrou "falo tudo de novo?".

## 6. Renderizar
```bash
python3 projetos/in26/lote_ads.py AD1b      # um
python3 projetos/in26/lote_ads.py           # todos
```
Cerca de 1 min por vídeo de 40s.

## 7. Auditar os prontos
```bash
python3 editor/auditar_pronto.py ~/Desktop/IN26/ADS/prontos/teste_A/*.mp4
```
Aponta silêncios maiores que 0,35s e momentos olhando pra baixo. Pausas de até ~0,45s são o respiro normal entre frases. Se aparecer algo acima de 0,6s, confira: pode ser só fala baixa (o relatório de energia ajuda a separar).

## 8. Revisão humana (obrigatória)
Assistir cada vídeo inteiro antes de postar:
- **Legenda:** o Whisper erra palavras. Corrija com `--trocar "errado=certo"` no lote (entra na lista `TROCAS`).
- **Números e afirmações:** confira os dados citados pelo entrevistado antes de publicar.
- **Contexto de data:** "é hoje", "é amanhã" só servem no dia certo.

Anote os ajustes na lista de publicação do projeto (`prontos/LISTA_*.md`).
