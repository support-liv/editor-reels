# Changelog

Cada mudança com o motivo, para o time entender por que o editor faz o que faz.

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
