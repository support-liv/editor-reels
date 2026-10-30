# Changelog

Cada mudança com o motivo, para o time entender por que o editor faz o que faz.

## 0.37 (30/10/2026) - Lições da aprovação (Video Machine)
- **`editor/licoes_da_aprovacao.py`** lê no liv.ai as reprovações da Video Machine (rota `GET /api/aprovacao/ingest/reprovacoes`, mesma chave da ingestão, `APROVACAO_INGEST_TOKEN`) e acrescenta cada uma em **`docs/REPROVACOES.md`**, na seção do motivo que a revisora marcou, com o texto dela e a lição para o editor. Pedido do Lucas: o que a Dra. Lívia e a Marinna escrevem ao reprovar ficava só no liv.ai e o mesmo erro podia voltar.
- **O guia só cresce.** Cada reprovação entra uma vez (o id da decisão vai anotado na linha), e a lição escrita à mão não é mexida. Reprovação desfeita ou trocada por aprovação não entra. Se a revisora reescreveu o motivo, vale só o mais novo. O placar no topo conta as vezes de cada motivo.
- **Dado de cliente:** quando o motivo é "Aparece dado de cliente", o texto da revisora não vem para o guia (pode conter o próprio dado) e fica só no liv.ai.
- **Chave no Chaveiro** (`editor-reels-aprovacao-ingest`), nunca em arquivo nem no chat. `--criar-chave` gera, guarda e copia a chave para colar no Easypanel; `--guardar-chave` abre uma janela do Mac para colar uma chave que já existe.
- Teste com um liv.ai de mentira: `python3 editor/teste_licoes_da_aprovacao.py`.

## 0.36 (30/10/2026) - Entrevista andando: recorte que acompanha e prévia do recorte em pé (Imigrar, Ronei)
- **`--crop-fixo` com zona morta:** o recorte segue parado enquanto o rosto fica no miolo (até 20% da largura do recorte para cada lado do centro) e só anda, devagar (média de ~2 s), quando o rosto vai para a borda. Na entrevista do Ronei, gravada andando, o recorte parado pela mediana do bloco deixava ele sair da cena ("em alguns momentos o Ronei some"); no R1, de 9% para 0% do tempo com o rosto fora do recorte. Rosto parado = mesmo resultado de antes.
- **`--previa-enquadramento` também no vídeo em pé** (antes, só na tela dividida): folha com quadros do vídeo pronto (gancho, legenda, CTA e a interface do Instagram por cima), o tamanho do recorte aberto e fechado, quanto tempo o rosto fica fora do recorte e quanto o recorte anda (px/s). Usa o mesmo cálculo do render e sai sem renderizar. Serve para validar o recorte antes do render.

## 0.35 (24/10/2026) - Recomeço colado e cortes da LIV (Mari e Dra. Lívia)
- **`--tirar-hesitacoes` tira recomeço colado:** a mesma sequência de 1 a 6 palavras dita duas vezes seguidas, com no máximo duas hesitações no meio ("é que, é que mais pega", "tem, tem uma instrução", "processo administrativo, processo administrativo", "quando, é, quando você", "mesmo ramo, é, é, mesmo ramo"). Sai a primeira ocorrência e a hesitação. Frase terminada seguida da mesma palavra é estilo e fica ("dual intent. Dual intent é duas intenções"). A fala rápida da Dra. Lívia tinha dezenas desses recomeços; cortar um a um à mão não escalava.
- **`--planos`** (corte longo `--layout youtube`): a cada corte o plano muda (aberto, fechado, médio, fechado...), recortado em 16:9 em volta do rosto, sem distorcer; corte curto (<1,2s) mantém o plano anterior. O corte longo da Dra. Lívia saiu com a cena inteira parada (o modo foi feito para live com tela) e o time pediu o enquadramento dinâmico. Use em gravação de uma pessoa (consulta, entrevista); live com tela compartilhada continua sem.
- `projetos/mari_reuniao/lote_mari.py` (6 Reels da Mari) e `projetos/livia_consultoria/lote_livia.py` (Reels verticais + cortes longos 16:9 da Dra. Lívia, intermediário 4K para o vertical recortar sem perder nitidez). Reunião/consulta com cliente: nenhum corte leva nome, voz ou detalhe do caso do cliente, nem preço ou prazo.

## 0.34 (24/10/2026) - Narrados: corte na batida, punch-in e versão B
- `lote_narrados.py` com `ritmo=True`: o plano de cortes do editor sai primeiro (narração sobre fundo preto); cada troca de cena vai para a batida da trilha mais próxima da palavra-âncora (até 0,30s antes / 0,15s depois; batidas pelo librosa a partir do `trilha_ss`); cena com mais de 2,4s ganha punch-in (recorte central 1,12x, mesma proporção) na batida do meio. O time achou os narrados parados: agora são 13-21 trocas por vídeo.
- Versão B: `gancho_b` + `abertura_b` (outra cena no gancho); o resto do vídeo é igual ao A (teste A/B só do gancho).
- Trilha por vídeo com `trilha_abaixo`/`trilha_ducking` (repassados ao `trilhas.mixar`). Narração não tem pausa: com ducking forte (ratio 6) a trilha ficava ~30 dB sob a voz, inaudível. Narrado: base 12 LU abaixo e ducking 1.3 (~16 LU sob a fala), faixas de batida estável (auditor-de-trilha).
- Cena por frase revisada (n1, n5, n6, n8): nada de cena "bonita" fora do assunto (Disney em "sair do Brasil", painel em "qual visto", camisa da seleção em "reclamando da política", mural relaxado em "tensão constante").

## 0.33 (23/10/2026) - Vídeos narrados (Imigrar)
- **`projetos/imigrar_narrados/lote_narrados.py`**: vídeo narrado = narração gravada (melhor take de cada frase, pela transcrição literal alinhada) + cenas de bastidores ancoradas nas palavras da narração + legenda, gancho e CTA da Imigrar + trilha. Sem motion. A cena começa na palavra-âncora; cena curta vira câmera lenta (gravação em 60 fps); cena horizontal é recortada na vertical sem distorcer; HDR do iPhone vai para SDR com leve realce (`eq` contraste 1,05 / saturação 1,10). O editor roda com `--aperto 1.0 --punch 1.0` (a cena já é vertical: sem zoom nem recorte por rosto).
- Trava de repetição (`auditar_fala.repeticoes`) agora pega recomeço de até 10 palavras (era 5): "Comprar passagem pro Terminal 3 no impulso, | comprar passagem pro Terminal 3 no impulso da eleição" passava.
- Cache da transcrição por janela leva a data do arquivo: vídeo renderizado de novo com o mesmo nome reaproveitava a leitura antiga na auditoria.
- Correção: cena do iPhone saía deitada no intermediário (matriz de rotação herdada do `-noautorotate`); o lote zera a rotação de cada trecho (`zerar_rotacao`). `--reusar-montagem` renderiza de novo sem remontar a narração.
- Narração gravada em sequência (vários vídeos num áudio só, com recomeços): o Whisper normal esconde 5-6 tentativas da mesma frase dentro do tempo de uma palavra (em "está trocando a ansiedade do noticiário" havia 6). Sempre escolher o take pela leitura **literal** da janela e conferir o volume no ponto do corte.

## 0.32 (23/10/2026) - Emendas entre takes e palavras com número
- **Alinhamento por pedaço (take):** o `lote_ti.py` grava na transcrição de onde veio cada palavra (`pedaco`) e os limites de cada take (`pedacos`). O `alinhar.py` alinha take por take e nunca joga uma palavra para o take vizinho (o "Unidos." do 06 terminava dentro do take seguinte; o "não é?" do R9 caía no take de depois e sumia da legenda).
- **O corte nunca passa da emenda** (`respeitar_pedacos` no editor): a sobra do take vizinho tocava um pedacinho de sílaba antes da fala (R6, "que é o visto").
- **Palavra com número:** o número da legenda ("2025,", "100", "1,8") vai para o alinhador como foi falado (campo `falado`, gravado pelo `lote_ti.py` ao trocar "dois mil e vinte e cinco" por "2025"); em dígito o alinhador não lê, inventava o tempo pelos vizinhos e o R3 perdia "mil e vinte e cinco". Sigla com número sem forma falada ("E-2", "O-1", "PERFIL27") fica com o tempo do Whisper.
- Trava do alinhador: perto de palavra esticada do Whisper (>0,9s) ele pode corrigir até 2s (era 0,7s). O "fortes," do R3 marcado com 1,8s empurrava o "onde" seguinte, que saía como hesitação sem palavra.
- **Pausa no meio da palavra não é pausa:** volume baixo dentro de uma palavra alinhada com o Silero ouvindo voz (o "f" de "perfil", o "ss" de "assim") não vira corte. Buraco de até 0,12s entre pedaços vira fala contínua (era 0,06s).
- **`--tirar-hesitacoes`:** "há" com acento é o verbo ("há dez anos"), nunca hesitação. O "e" esticado é medido pela voz real (Silero), não pelo tempo do Whisper (um "E" de 0,1s marcado com 0,94s saía e levava o começo de "descubra"). A hesitação tirada nunca invade a palavra vizinha.
- Borda fraca da palavra pelo Silero E pelo volume: o fim avança até 0,55s (era 0,35s) enquanto os dois ouvirem voz (o "s" de "Unidos" no 01) e o começo recua até 0,35s até o começo alinhado da 1ª palavra (o "e" baixinho de "coisas, e outros" no R10 ficava pela metade).
- Auditoria: "corte na palavra" só acusa quando a voz continua do lado de fora do corte (depois do fim / antes do começo). O fim alinhado que engole silêncio ("pra" do R5 com 0,8s) gerava alerta falso.
- `lote_ti.py`: trava de **repetição na emenda** (o fim de um take e o começo do seguinte dizendo a mesma palavra: "acha que precisa | precisa de uma empresa" no 04; frase terminada seguida de frase nova não conta: "O seu visto. | O visto de turista") e pedaço `"exato"` (4º item da tupla: sem extensão, para tirar gaguejada colada à palavra, "maior que o da, do Brasil" no R3).

## 0.31 (23/10/2026) - Corte preciso: WhisperX + Silero VAD
- **`--alinhar`** (editor/alinhar.py): alinhamento forçado (WhisperX + wav2vec2 em português) refaz o tempo de cada palavra com precisão de 20-50 ms. Era a causa principal das palavras comidas: o Whisper marcava o "ou" do Ednaldo em 14,55s e ele estava em 14,29s.
- **`--vad`** (editor/vad.py): detector de voz neural Silero nas bordas das palavras. A pausa continua pelo volume (o Silero ouve a conversa do fundo do shopping como fala e o ritmo morria).
- Pedaços encostados (buraco <= 0,06s) viram um só: acabou o micro-corte de 20 ms no meio da palavra com troca de zoom.
- Extensão das bordas limitada (começo 0,15s, fim 0,12s): o fim alinhado às vezes engole o silêncio e as pausas sumiam.
- Correção: o `--vad` era ligado depois do refinamento dos cortes (não tinha efeito).
- Correção: queda de volume no meio da palavra ("propicia") deixava o 1º pedaço sem palavra "dona" e ele saía como hesitação, comendo o começo da palavra. Bloco que sobrepõe palavra alinhada nunca é hesitação.
- Ambiente separado `.venv-whisperx` (o WhisperX traz versões próprias de torch/torchaudio); o `setup.sh` instala. Transcrições literais dos brutos alinhadas (`<base>.literal.json`; a original fica em `.literal.whisper.json`).
- Alinhador com trava: tempo fora de ordem ou >0,7s longe do Whisper fica com o do Whisper (no R1 ele jogou a frase final 4s pra trás).
- Fim da palavra pelo detector de voz: o corte avança enquanto o Silero ouvir voz, até o fim alinhado (máx. 0,35s) — o "o" fraco de "visto" era cortado.
- Pedaço de take: palavra entra se começa até 0,03s antes do fim marcado; o fim estica até o fim do Whisper + 0,15s (+0,20 de folga) e nunca encosta na palavra seguinte. Palavra de ligação solta no fim do vídeo ("Então", "e", "mas"...) depois de pausa sai: era começo da frase seguinte ou palavra que o Whisper inventou numa respiração.
- Auditoria (`projetos/imigrar_ti_ads/auditoria.py`) ganhou checagens exatas: corte caindo dentro de palavra (com voz pelo Silero E pelo volume), palavra do trecho que sumiu do pronto e FALA FORA DO CORTE (voz do intermediário que não entrou no vídeo).

## 0.30 (22-23/10/2026) - Imigrar · TI (correções) e Ednaldo
- **Correção: final da fala cortado.** Dois motivos: pedaços de take fechados no INÍCIO da última palavra (escolhidos pelo tempo de início do Whisper) e o último corte com só 0,08s depois da voz. Agora o `lote_ti.py` estende o pedaço até o fim da palavra (+0,30s, sem encostar na vizinha) e o editor leva o último corte até o fim da última palavra + 0,35s, com fade de 0,12s. Regra no CLAUDE.md.
- Crop fixo agora é por bloco de fala (grupo), não por pedaço: a imagem pulava a cada micro-corte do mesmo bloco.
- Nomes de vistos e em inglês na legenda (E-2, O-1, L-1, EB-2 NIW, B1/B2, DS-160, Lake Nona...): regra no CLAUDE.md, correção no `CORRECOES` do editor e no `lote_ti.py`.
- Reels do Ednaldo com B-roll de contexto (banco de cenas da pasta Downloads: escritório, documentos, Flórida, Orlando, Lake Nona, vacas) e CTA PERFIL27.
- **Correção: palavra curta sumindo ("ou", "mas", "é", "então").** O Whisper erra o tempo de palavra curta (o "ou" do Ednaldo estava de 14,00 a 14,34s; o Whisper marcou 14,55s). Três efeitos somavam: (1) o plano inicial cortava toda pausa >0,35s pelos tempos do Whisper, e a voz da palavra ficava no "buraco"; agora, com `--proteger-palavra`, o plano não corta pausa (quem corta é o áudio); (2) o bloco de voz da palavra ficava sem palavra e saía como hesitação; agora bloco curto sem palavra colado a vizinho que começa/termina com palavra curta fica com ela; (3) começo/fim suave abaixo do limiar: o corte recua/avança enquanto houver voz fraca (-5 dB) colada.
- **Correção: palavra curta comida no corte.** O corte pelo áudio descartava todo trecho de voz com menos de 0,25s entre pausas; palavra curta isolada ("ou", "mas", "é", "então") sumia. Agora o trecho curto só sai se não tiver palavra.
- **Correção: imagem tremendo em selfie na mão.** O recorte seguia o rosto amostra a amostra e somava ao balanço da câmera. `--crop-fixo` deixa o recorte parado em cada corte (posição mediana do rosto). `--punch` controla o zoom do plano fechado (0,82 quase não aparecia em selfie aberta; anúncios de TI usam 0,72).
- Legenda dos anúncios de TI desceu de 55% para 62% (estava na boca do Lucas). Grafia de "Green Card": regra única que pega todas as variações do Whisper (wincard, win card, going card, Green Car...).
- `--seg-gancho`: duração do balão do gancho (padrão 3,2s). Nos anúncios de TI e do Ednaldo o time pediu 1s a mais: 4,2s.
- **Correção: `--tirar-hesitacoes` cortava o verbo "é".** O `norm()` tira o acento, e "é" esticado (≥0,45s) virava hesitação ("a única forma de morar aqui é depender" saía "aqui depender"). Agora "é" acentuado só sai com reticências ou isolado entre pausas.
- `--proteger-palavra SEG`: em ambiente barulhento, o corte pelo áudio não come o fim/começo fraco da palavra ("profissionai-s"); estende o pedaço até onde o Whisper diz que a palavra vai (no máximo SEG).
- **Repetições escondidas:** o Whisper limpa a fala e esconde "sabia que, sabia que" dentro do tempo de uma palavra. `projetos/imigrar_ti_ads/transcrever_literal.py` (initial_prompt cheio de hesitações) transcreve literal; `auditar_fala.py` transcreve cada pedaço sozinho em modo literal e acha repetições; o `lote_ti.py` não renderiza com repetição. Anúncios com versões A/B (só o gancho muda).
- Anúncio horizontal 4811 refeito na identidade da Imigrar (Inter Tight, tarjas rosa/azul), câmera endireitada 1,4° (só giro, recorte da área útil sem canto preto) e zooms presos no topo (a bandeira fica na cena).

## 0.29 (22/10/2026) - Imigrar · anúncios de TI
- `--broll-com-legenda`: B-roll de imagem real (anúncio) mantém a legenda por cima. Sem a opção, B-roll de tela cheia tira a legenda (regra do motion). Em anúncio a fala continua durante o B-roll e a legenda não pode sumir.
- `projetos/imigrar_ti_ads/`: 11 anúncios verticais montados de vários takes (`lote_ti.py` junta gancho de um, corpo e CTA de outro num intermediário SDR, com a transcrição deslocada, sem rodar o Whisper de novo), B-rolls do iPhone (`preparar_broll.py`) e o anúncio horizontal de teste `horizontal_4811.py` (16:9, LUT `cinema_pastel.cube`, letterings em serifa New York com tons pastel, fora da identidade da Imigrar).
- Aviso: arquivo gerado com `-noautorotate` (HDR do iPhone) herda a matriz de rotação; zere com `-display_rotation:v 0` ao remuxar, senão a imagem sai deitada.

## 0.28 (07/10/2026) - LIVE 81: enquadramento da tela dividida e sublinhado do motion
- **Correção: enquadramento da tela dividida.** O recorte (88% da metade, ~750 px de altura) com o limite de 70% da altura (chat/banner) só podia começar entre 0 e 6 px: ficava preso no topo da imagem, e a regra "rosto a 42%" nunca valia. Resultado na LIVE 81: até 34% do painel de teto acima da Dra. Lívia e, quando ela se inclinava, cabelo cortado. Agora o zoom e o x são fixos por pessoa, e a altura é decidida corte a corte pelo topo da cabeça (margem 8% em cima, 16% embaixo por causa da legenda na divisa); o zoom abre até 100% quando a cabeça não cabe. Auditoria completa e números em `docs/ENQUADRAMENTO.md`.
- Guardrails de enquadramento em todo render de tela dividida: avisa cabeça cortada, queixo fora do painel, teto demais e cabeça fora da própria webcam (só informa). `--exigir-enquadramento` não renderiza com aviso; `--previa-enquadramento ARQ.jpg` gera a folha de conferência (1 quadro por corte, com as guias) antes do render.
- `--sem-sobreposicao`: live sem chat/banner na tela libera o recorte para descer além dos 70%.
- **Correção: sublinhado e risco do motion desalinhados.** `sub` e `risco` usavam `x`/`largura` fixos do roteiro (e o "no canal" do CTA, 300 px fixos), então ficavam longe da palavra ou maiores que ela. Agora são presos à linha de texto e medidos no navegador (`sob`, `sobre`, `apaga`, `palavra`); o gerador avisa traço solto.
- Correção: `tempo_na_saida` com trechos fora de ordem (`--trechos "3870-3885,360-395"`) punha todo o 2º trecho em 0s (afetava `--json-palavras`, `--tempos-palavras` e `--broll @fonte:`).
- `projetos/live81/`: 2 cortes longos e 6 shorts (3 com motion), trilha Skylines, `publicacao.json`; lote com modos `previa` e `final`.

## 0.27 (30/09/2026) - Plano EUA 2027: todos os shorts com motion
- Layout `quadro` (live solo 720p) aceita `--broll` (motion em tela cheia, sem legenda nem gancho por cima) e `--cauda` (CTA animado no fim).
- Batidas da Imigrar: o item da fala pode acender de novo e o respiro da cena pode se repetir (1,4s de intervalo), pra fala pausada não deixar a cena parada. A LIV segue igual.
- `projetos/plano_eua_2027/lote_motion.py` cobre os 31 cortes (L01-L17 tela dividida, M01-M14 quadro); roteiros em `projetos/plano_eua_2027/motion/roteiros.py`.

## 0.26 (30/09/2026) - live com 3 pessoas (Jornada do dentista)
- `--colunas N --pessoas cima,baixo`: tela dividida a partir de live com N pessoas lado a lado (as 2 que conversam; coluna inteira, rosto um pouco acima do meio).
- `editor/vtt_para_json.py`: usa a legenda .vtt do YouTube como transcrição (corte longo de live comprida sem rodar o Whisper em 1h+). Atenção: a legenda vem ~0,8s adiantada; nos shorts, recorte o trecho e deixe o Whisper transcrever.
- `editor/retranscrever.py`: transcreve de novo uma janela quando o Whisper "pula" frases (palavra esticada por vários segundos).
- Motion: fundo animado recortado pela forma do painel (os círculos vazavam na tela depois que a cena saía); destaque de item em cartão de interface acende em rosa (branco sumia no cartão branco) e balão de chat pulsa; `sync_t`/`tempos` por item.
- **Correção grave:** o layout vertical supunha vídeo em pé e, com fonte 16:9 (live), recortava um retângulo deitado e esticava para 9:16 (Marinna espremida). `caixa()` agora recorta sempre 9:16 (pela altura quando o vídeo é deitado) e tem trava contra distorção.
- Transcrição: palavra esticada por mais de 2s (o Whisper pulou fala) é transcrita de novo automaticamente naquela janela.
- `projetos/jornada_dentista/lote.py`: corte longo (cold open + 15 trechos, 13:40, 16:9, sem vinheta) e os 15 shorts da lista (um por trecho), com início e fim pelas frases do documento da equipe (`rel_por_frases`) e motion da Imigrar (`motion/roteiros.py`). No S07 o motion cobre o slide que a live mostra no fim do trecho.

## 0.25 (30/09/2026) - motion na identidade da Imigrar
- `gerar_liv.py` com tema por marca (`"marca": "imigrar"` no roteiro): paleta rosa #F90D5B, azul royal #0E59C5, branco e preto; Inter Tight Black; painel em diagonal com faixa dupla; palavras entrando com impacto; marca-texto chapado atrás das palavras de destaque; faixas sutis correndo no fundo; sons mais fortes. A LIV continua clean e igual.
- Contraste na Imigrar: nunca rosa sobre azul nem azul sobre rosa (no azul, destaque e marca-texto em branco).
- Fundo animado diferente a cada cena (faixas, pontos, grade, círculos) e conteúdo mais no meio da tela (zona 330-1420, metade das cenas centralizada).
- Interfaces novas (Imigrar): `chat` (balões com "digitando..."), `status` (tela do processo com selos aprovado/negado/em análise), `notificacao` (desce com mola) e `busca` (digita letra a letra).
- CTA dos testes: "Veja a live completa no canal" (YouTube).
- Sincronia: palavras curtas ("e", "o", "de") não servem mais de âncora (casavam com o "é" errado da fala).
- `projetos/plano_eua_2027/lote_motion.py`: shorts de teste da live Plano EUA 2027 com motion (L05, L10, L12), fala enxuta e CTA animado "Existe um caminho pro seu perfil? Link na bio".

## 0.24 (30/09/2026) - motion sem tempo parado, variado e CTA por canal
- Texto do motion entra palavra por palavra no tempo da fala (`--json-palavras` exporta as palavras do corte; `gerar_liv.py` casa cada palavra da linha e dos itens dos componentes com o Whisper).
- Batidas automáticas: onde a fala segue sem texto novo, o gerador acentua no tempo de uma palavra dita (as linhas anteriores recuam, um fio fino se desenha sob a última, o item da fala acende na cor de destaque, ou um respiro leve da cena). Tudo dentro do manual da LIV.
- Respiro de câmera sutil em toda cena (1,5%): nada fica congelado.
- Componentes novos: `degraus`, `barra` (progresso segmentado), `colunas` (lado a lado com fio) e `numero` (numeral grande). A rota BR → EUA e os cards deixam de ser padrão; a checagem avisa quando um recurso se repete no vídeo.
- Checagem de ritmo mais rígida: 1º elemento em até 0,6s, no máximo 1,3s parado entre revelações e 1,2s no fim.
- Títulos de uma mesma comparação (colunas, cartões) no mesmo tamanho: se um encolhe pra caber, o grupo todo encolhe junto. O fio entre colunas fica no meio do vão real entre os textos (mesma margem dos dois lados), medido, não fixo no meio da tela.
- CTA por canal: YouTube Shorts "Veja a live completa no canal"; Instagram, palavra-chave nos comentários. O briefing pergunta o canal.

## 0.23 (30/09/2026) - sem filete e fala mais enxuta
- Transição do motion sem filete: as curvas do painel ficam 30px fora da tela quando a cena está parada (sobrava um fio laranja no canto).
- `--tirar-hesitacoes`: tira "éé", "hmm", "ah", "e..." esticado, "então, assim" com pausa e voz sem palavra.
- `--respiro` menor que 0,25 aperta também a folga depois da fala (0,08s); shorts da LIVE 80 em `--respiro 0.18`.
- `--json-cortes` + `motion/remapear.py`: o motion acompanha quando o corte muda.

## 0.22 (30/09/2026) - motion com jornada
- `gerar_liv.py`: componentes `rota`, `etapas`, `checklist`, `anel`, `contador`, `cartoes` (clean, na identidade da LIV), pra contar a história além de texto e ícones.
- Shorts B da LIVE 80 com jornada: rota BR → EUA, linha do tempo "USCIS → NVC → entrevista", cards comparando (consular × ajuste, business × professional plan, plano A × plano B), checklist da proposta, contador "18 anos".

## 0.21 (30/09/2026) - motion sem legenda por cima
- Com o motion cobrindo a tela, o editor não desenha a legenda (medido pela transparência do b-roll a cada quadro).
- `gerar_liv.py`: bloco da cena centralizado na vertical na zona segura (200-1300 px), ícones puxados pra perto do texto, alinhamento variado (esquerda na maioria, ~1 em 4 centralizada), risco medido pelo texto que risca, checagem da zona segura.

## 0.20 (30/09/2026) - motion no ritmo da fala e CTA no fim
- `--cauda SEG`: segundos extras depois da última fala (último quadro parado, silêncio); o CTA animado entra ali.
- Shorts da LIVE 80 refeitos: motion sempre em tela cheia na tela dividida, cenas curtas no ritmo da fala (sem tempo parado), CTA "Comente PERFIL27" depois da fala nas versões A e B.
- `gerar_liv.py` confere o ritmo e avisa (e, na tela dividida, texto invadindo a faixa da legenda 860-1060): demora até o 1º elemento (> 0,8s), tempo parado entre elementos (> 2s) ou no fim (> 1,6s), e meia cena em tela dividida.

## 0.19 (30/09/2026) - LIVE 80: cortes longos e shorts A/B
- `motion/gerar_liv.py`: gera o B-roll da LIV a partir de um roteiro JSON (painéis com a curva da marca, cheios ou cobrindo uma metade da tela dividida, linhas reveladas, riscos, sublinhados, ícones oficiais, CTA animado, sons discretos). Mantém os 6 shorts consistentes.
- `--broll` também na tela dividida; o motion cobre a metade de quem está ouvindo e a legenda continua na divisa.
- `--tempos-palavras`: lista cada palavra com o tempo no vídeo pronto (pra sincronizar o motion).
- `motion/conferir.py --dividido`: marca a faixa da legenda da tela dividida.
- Tom de voz: nesta live a Dra. Lívia fica em ~190-205 Hz e o Breno em ~115-150 Hz (limite 170, não 200).
- Decodificadores em `-v fatal`: some a enxurrada de "Broken pipe" (inofensiva) do terminal.
- Projeto `projetos/live80`: 2 cortes longos (9:10 e 8:14) e 6 shorts em versão A (gancho + legenda + CTA) e B (com motion + CTA animado "Comente PERFIL27").

## 0.18 (29/09/2026) - LIV clean e zona segura
- **LIV clean:** B-roll refeito só com elementos do manual (curva da marca, fio com arco, seta dupla, arco duplo, estrela no círculo, losangos), movimento calmo e som discreto. A versão cheia de efeitos virou base para a Imigrar (`broll_perfil_explorado`).
- **Legenda da LIV sem contorno:** texto bege em bloco sólido azul, palavra em laranja. Imigrar mantém o contorno.
- **Zona segura** padrão (x 60-1020, y 153-1510, sem o canto dos botões): motion redistribuído (bloco 250-950, apoio 980-1170, legenda 1190-1390 livre). CTA animado à esquerda e a 1400 px.
- `motion/conferir.py`: folha de quadros com a zona segura, a legenda e os botões desenhados por cima.

## 0.17 (29/09/2026) - motion mais trabalhado
- Modelo `broll_perfil_liv`: B-roll da narrativa inteira (5 cenas), com profundidade (3 camadas em paralaxe, grão, brilho), cards 3D, tipografia com extrusão, partículas, rastro de velocidade, contador, anel de progresso, follow-through e 32 efeitos sonoros sincronizados.
- Texto ajustado à largura na montagem (o "EXPERIÊNCIA" quase cortava na lateral).
- Skills novas no projeto: LottieFiles `motion-design`, ecc `motion-foundations`, `motion-patterns`, `motion-advanced`. (`motion-ui` não existe no repositório da ecc, não instalou.)

## 0.16 (29/09/2026) - B-roll de motion com efeitos sonoros
- **Motion passou a ser B-roll de cena extra** explicando a narrativa (o teste anterior pôs o CTA por cima de um vídeo já legendado e duplicou legenda e gancho).
- `--broll arquivo.mov@fonte:SEG`: a cena entra por cima da imagem e embaixo da legenda; os efeitos sonoros dela entram mixados por baixo da voz. O tempo pode ser o da fala no bruto.
- `motion/sfx/` + `gerar_sfx.py`: 8 efeitos sonoros sintetizados (sem licença de terceiros).
- Modelo `broll_caminho_liv` (7s, 2 atos, sincronizado com a fala), exemplo de referência.
- `--sem-legenda`, para quando a origem já vem com legenda gravada.
- CLAUDE.md: conferir se o material é bruto antes de editar.

## 0.15 (29/09/2026) - motion design (piloto)
- `motion/`: animações em HTML renderizadas pelo HyperFrames 0.8.94 (Apache 2.0), fundo transparente (ProRes 4444), render local.
- Primeiro modelo: `cta_palavra_chave` ("Comente PALAVRA" animado), nas duas marcas.
- Editor: `--cta-animado PALAVRA` (renderiza o modelo e cola no fim) e `--animacao arquivo@segundos` (qualquer animação). Proporção diferente do vídeo é recusada (nunca distorcer).
- Skills do projeto em `.claude/skills/`: 9 do HyperFrames e 15 do iart-ai/motion-skills (técnica de motion; render pelo HyperFrames, não Remotion). Versões travadas em `skills-lock.json`.
- `.claude/settings.json`: telemetria do HyperFrames desligada e comandos de nuvem/login bloqueados.
- `setup.sh` instala o motion quando há Node 22+.

## 0.14 (29/09/2026) - identidade das marcas, corte longo e carrossel
- **Fonte e cores da marca, sempre**, na legenda e nas caixas: LIV em Darker Grotesque, Imigrar em Inter Tight. Tamanho ajustado para a mesma altura visual aprovada em Arial Black.
- `--cor-caixa` por marca, só com cores da paleta: LIV azul/laranja/bege/marrom (manual de identidade), Imigrar branco/azul/rosa.
- `--layout youtube`: corte longo 16:9 1080p com a vinheta da LIV (o som da transição entra por cima do começo da live, no mesmo volume, -14 LUFS). Gera o `.tempos.txt` para os capítulos.
- `editor/carrossel.py`: carrossel 1080x1350 na identidade da marca. Carrossel é narrativa (7 a 10 cards: capa, contexto, desenvolvimento, virada, resumo, CTA); o gerador avisa quando tem menos de 6.
- Layout quadrado converte HDR do iPhone (antes saía lavado).
- Avisos claros quando o vídeo não existe ou não tem áudio; o corte não passa do fim do arquivo.

## 0.13 (29/09/2026) - formatos, marcas e guia do Claude
- `CLAUDE.md`: como o Claude do time trabalha no repositório. Assiste o material e deduz a estratégia; pergunta uma vez só o que não dá para deduzir (formatos, palavra-chave do CTA, live em 720p, nomes); mostra o plano antes de renderizar.
- `docs/FORMATOS.md`: corte longo YouTube, Reels/Shorts, stories, WhatsApp, anúncio e carrossel; estilo por tipo de cena; paletas e fontes das marcas.
- `assets/vinheta_cortes_liv.mp4`: vinheta do corte longo. Imagem até 3,80s (sem o flash branco da trilha) e som da transição até 4,7s, pra tocar por cima do começo da live.
- `assets/fontes/`: Darker Grotesque (LIV) e Inter Tight (Imigrar), licença OFL.

## 0.12 (29/09/2026) - perspectiva e ajustes finos
- `--endireitar`: mede as verticais da cena e escolhe sozinho o ângulo de `--girar` (a vertical fica reta na altura do rosto; no Thiago, +3,4° em vez dos 5° no olho).
- **Regra: nunca distorcer a imagem.** A primeira versão do `--endireitar` corrigia perspectiva e deformou o rosto do Thiago. Foi removida: câmera torta se corrige só girando.
- `--tirar "a-b"`: tira um trecho exato do bruto (palavra repetida, travada). O pedaço vira dois e o zoom muda na emenda.

## 0.11 (29/09/2026) - emendas e zoom dinâmico
- **Pedaços sem sobreposição:** quando o fim de um pedaço passava do começo do seguinte, o começo da palavra tocava duas vezes (no Thiago: "LIV vi vi"). Agora o pedaço anterior termina onde o próximo começa.
- `--dinamico`: quebra pedaços longos entre palavras (de preferência na vírgula ou no ponto) a cada ~2,5s e alterna 3 níveis de zoom (aberto, fechado, médio). A fala continua sem corte e o áudio emenda sem fade. Bom pra quem fala mais travado.

## 0.10 (29/09/2026) - sincronia de áudio e WhatsApp dinâmico
- **Correção de lip sync (todos os layouts):** cada corte gerava alguns quadros a mais ou a menos que o áudio (arredondamento de 29,97 → 30 fps e o fim do corte fora da grade de quadros). O erro somava de corte em corte: num vídeo de 17 cortes o vídeo ficava 0,49s mais longo que o áudio, e a boca descolava da fala do meio pro fim. Agora o fim de cada corte cai num quadro exato e o vídeo lê exatamente esse número de quadros. **Tudo renderizado antes da 0.10 tem esse desvio.**
- `--layout quadrado` deixou de ser fixo: punch-in alternando por bloco de fala e rosto reenquadrado a cada bloco (não é live).
- Legenda do quadrado menor (40 → 30 px), a 84% da altura.
- `--respiro 0.5`: mantém pausas internas até esse tamanho, pra quem fala mais pausado (o corte seco deixava a fala robótica).

## 0.9 (29/09/2026) - WhatsApp
- `--layout quadrado` (1080x1080) e `--girar` pra corrigir câmera torta. O `rotate` do ffmpeg gira no sentido horário: o sinal é invertido pra "positivo = anti-horário", e a posição do rosto é recalculada depois de girar.
- Projeto `whatsapp_liv`: boas-vindas do Thiago (câmera corrigida em 5°) e da Marinna, na cor da LIV.

## 0.8 (29/09/2026) - live com uma pessoa
- `--layout quadro`: imagem da live nítida no meio, fundo desfocado da própria cena, gancho acima e legenda abaixo, enquadramento fixo. Escolhido no lugar do recorte vertical, que ampliava 2,7x a imagem 720p e ficava borrado.
- Recorte do quadro sem a faixa de baixo da live (chat).
- Projeto `plano_eua_2027`: 14 cortes solo da Marinna (`lote_mari_solo.py`).

## 0.7.1 (28/09/2026) - tela dividida fixa
- Tela dividida com **enquadramento fixo** no vídeo inteiro e sem zoom alternado: live é câmera parada e o recorte mexendo ficava estranho. Entrevistas e demais cortes continuam com o enquadramento dinâmico.
- `--cima direita|esquerda`: escolhe quem da live vai em cima (na Plano EUA 2027, a Dra. Lívia).
- Regra do gancho: só a pergunta, nunca a resposta (ver PADROES.md).

## 0.7 (28/09/2026) - tela dividida para lives
- `--layout dividido`: live com duas pessoas lado a lado vira uma em cima e outra embaixo, com legenda e tarja na divisa, sem tapar rosto.
- Recorte limitado aos 70% de cima da live: os balões de comentário do chat sobem até 73% da altura quando entram vários.
- `--cor-caixa branco|azul|rosa`: variação da tarja na identidade Imigrar.
- Bandeiras novas no gancho: 🇪🇺, 🇵🇹, 🇮🇹.
- **Nenhuma palavra se perde no corte pelo áudio:** o Whisper às vezes marca a palavra no silêncio entre dois pedaços (um "não" sumiu da legenda e invertia o sentido da frase). Agora cada palavra vai pro pedaço mais próximo.
- Projeto `projetos/plano_eua_2027`: 17 cortes da live.

## 0.6 (28/09/2026) - cortes pelo áudio e auditorias
- **Cortes pelo áudio:** o Whisper estica o fim da última palavra para o silêncio, e isso aparecia como respiro ou olhada pro lado no fim da frase. Agora o editor mede a voz (energia em dB a cada 20 ms) e corta onde a fala começa e termina, com folga de 0,05s antes e 0,10s depois. Pausas internas acima de 0,25s saem.
- **Pergunta do entrevistador:** limite de voz 8 dB mais sensível, porque sai mais baixa no microfone.
- **Zoom por bloco:** com o corte pelo áudio surgem muitos pedaços curtos. O punch-in passou a alternar por bloco original, senão o zoom pisca.
- **Tom de voz por bloco:** na conversa, medir em pedaços curtos errava quem falava.
- **Detecção de leitura do celular:** o detector de rostos agora devolve a inclinação da cabeça (pitch/yaw). `auditar.py` mostra, por frase do bruto, a % do tempo olhando pra baixo. Takes lidos não entram.
- **`auditar_pronto.py`:** confere pausas e olhar no vídeo final.
- **Legenda 35% menor** (58 → 38 px), aprovada pelo time.
- **Caixa do gancho em selfie:** escolhe a posição que menos cobre olhos e boca.

## 0.5 (28/09/2026) - anúncios
- Modo anúncio: sem caixa de CTA (o Meta põe o botão), legenda a 55% (selfie a 64%).

## 0.4 (28/09/2026) - cor e posição da caixa
- **HDR → SDR:** o iPhone grava em HDR (HLG/Dolby Vision). Sem conversão, a imagem ficava lavada. Conversão com tone mapping pelo VideoToolbox e arquivo marcado como BT.709.
- **Caixa não tapa rosto:** o editor gera o quadro final, procura os rostos e desce a caixa para o lugar da legenda quando precisa (a legenda some enquanto a caixa aparece).
- **Bandeira depois da palavra:** a bandeira sozinha não era entendida de primeira.

## 0.3 (27/09/2026) - conversa e ordem livre
- `--pessoa voz`: fecha em quem fala pelo tom de voz (Julia ~235 Hz, André ~160 Hz; limite 200 Hz) e segue cada pessoa por identidade, frame a frame.
- Trechos em qualquer ordem, `a-b?` para pergunta e `@N` para forçar quem aparece.
- Série "pergunta + resposta": a pergunta abre em quadro aberto.
- Equalização de voz (dynaudnorm) antes do loudnorm.

## 0.2 (27/09/2026) - visual e cortes
- Detector de rostos trocado de OpenCV (Haar) para o Vision do macOS: o Haar falhava com perfil e óculos.
- Gancho em caixa alta e bandeiras (renderizadas pelo macOS, porque o Pillow sem libraqm não junta as letras da bandeira).
- Legenda 25% menor (78 → 58 px). Caixas a 290 px do topo, abaixo da barra do Instagram.
- Removido o CTA falado "segue o perfil".

## 0.1 (27/09/2026) - primeira versão
- Transcrição com Whisper (timestamps por palavra), corte de perguntas e pausas, enquadramento 9:16 seguindo o rosto, legenda palavra a palavra, gancho e CTA, áudio a -14 LUFS.
- Legenda desenhada em Python porque o ffmpeg do Homebrew vem sem libass/drawtext.
