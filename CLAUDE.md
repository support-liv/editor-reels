# editor-reels — instruções para o Claude

Você edita vídeos da **LIV** (escritório de imigração, meio de funil) e da **Imigrar** (topo de funil) com as ferramentas deste repositório. Quem pede é do time de marketing: fale português, sem jargão técnico, e entregue o vídeo pronto.

Leia antes de editar: `docs/FORMATOS.md` (o que cada formato leva), `docs/PADROES.md` (padrões visuais aprovados) e `docs/OPCOES.md` (todas as opções do editor).

## Como trabalhar: rápido, certeiro, com poucas perguntas

1. **Confira se o material é bruto.** Olhe quadros: se já tem legenda, gancho ou grafismo gravado, **não queime outra legenda por cima** (duplica). Peça o bruto; se não houver, use `--sem-legenda` e avise.
2. **Assista.** Transcreva (`python3 editor/transcrever_lote.py VIDEO`), veja alguns quadros e a resolução (`ffprobe`). Deduza sozinho: marca, tipo de cena, assunto, público, objetivo, pautas e ganchos.
3. **Pergunte uma vez só, e só o que não dá para deduzir.** Uma rodada curta, já com a sua sugestão preenchida. Normalmente:
   - quais formatos saem desse material (corte longo, Reels/Shorts, stories, carrossel, WhatsApp, anúncio);
   - **canal de destino** (YouTube, Instagram…): o **CTA muda por canal**. YouTube (Shorts de live): "Veja a live completa no canal". Instagram: link na bio ou **palavra-chave** (muda por campanha e por vídeo, sempre confirmar);
   - **live solo em 720p**: quadro com fundo desfocado ou tela cheia perdendo qualidade;
   - nomes com grafia duvidosa (o Whisper erra: "Livre" = LIV, "Marina Damás" = Marinna Damásio).
   Não pergunte o que o vídeo já responde nem o que já tem padrão.
   Se a origem vier com legenda gravada e não houver bruto: enquadre acima dela (`--aperto`, só zoom uniforme) e use a legenda padrão; avise que o bruto dá mais qualidade.
4. **Mostre o plano antes de renderizar**: lista de cortes com o texto de cada um, ganchos e CTAs. Renderize só depois do ok.
5. **Renderize, confira e entregue** (ver "Conferência" abaixo).

## Regras que nunca mudam
- **Gancho só pergunta, nunca responde.** A resposta está no vídeo.
- **Bandeira depois da palavra** ("americano 🇺🇸"), nunca no lugar dela.
- **Nunca distorcer a imagem** (perspectiva, esticar, mudar proporção). Câmera torta: só girar (`--endireitar` ou `--girar`).
- **Live com 2 pessoas não tem crop** (tela dividida fixa). Fala pra câmera e entrevista são dinâmicas.
- **Nunca usar take em que a pessoa lê o celular** (`editor/auditar.py`).
- **Vinheta só no corte longo do YouTube.**
- Sem promessa de aprovação ou prazo. Números sem fonte ficam de fora ou vão para conferência.

## Corrigir um ponto que a pessoa apontou ("em 0:26 ele trava")
O tempo que a pessoa fala é do vídeo **pronto**. Converta para o bruto somando a duração dos cortes (`--so-cortes` mostra o plano). No bruto, olhe a energia do áudio e as palavras do Whisper em volta; se precisar, retranscreva só aquele trecho. Tire o trecho exato com `--tirar "a-b"`. Mudou o respiro de alguém? `--respiro`.

## Conferência antes de entregar
- **Sincronia:** duração do vídeo e do áudio do arquivo final iguais (`ffprobe`); diferença acima de 0,05s é bug.
- `python3 editor/auditar_pronto.py ARQUIVO.mp4`: buracos, respiros, olhar pra baixo.
- Olhe quadros do resultado: rosto enquadrado, legenda e caixas sem tapar rosto, verticais retas.

## Projetos
Cada projeto tem um lote em `projetos/<nome>/lote_*.py` com os trechos, ganchos e opções de cada vídeo (modelo: `projetos/_modelo/lote_modelo.py`, guia: `docs/NOVO_PROJETO.md`). Vídeos brutos e prontos ficam **fora** do repositório.

## Ferramentas por formato
- Reels/Shorts, anúncio, stories: `editor/editor_reels.py` (vertical).
- Corte longo YouTube: `editor/editor_reels.py --layout youtube` (vinheta da LIV entra sozinha; Imigrar: `--sem-vinheta`).
- WhatsApp: `--layout quadrado`. Live: `--layout dividido` / `quadro`.
- Carrossel: `editor/carrossel.py roteiro.json`.
- Fonte e cores são sempre as da marca (`--marca`); `--cor-caixa` só aceita cores da paleta.

## Motion design (animações)
- Animações ficam em `motion/` (HyperFrames: HTML + GSAP, render local, fundo transparente) e o editor cola no vídeo (`--cta-animado`, `--animacao`). Ver `motion/README.md`.
- Técnica: skills do projeto em `.claude/skills/` (HyperFrames + iart-ai/motion-skills). As do motion-skills falam de Remotion: use só a técnica e **renderize pelo HyperFrames** (Remotion exige licença paga).
- **Nunca** use render na nuvem (`hyperframes cloud`, `lambda`, `cloudrun`) nem login/telemetria: vídeo de cliente não sai da máquina. Já está bloqueado em `.claude/settings.json`.
- **Motion = B-roll de cena extra que explica a narrativa** (`--broll`): tela cheia na identidade da marca, texto cinético no tempo das palavras, efeitos sonoros (`motion/sfx/`), transição de entrada e saída. Nunca é enfeite em cima do gancho ou da legenda. Como montar: `motion/README.md`.
- **Nível por marca:** LIV clean, só elementos do manual, sem sombra/contorno no texto; Imigrar pode explorar. **Zona segura:** x 60-1020, y 153-1510, fora do canto dos botões e da faixa da legenda; conferir com `motion/conferir.py`.
- **Ritmo:** o texto entra palavra por palavra no tempo da fala (exporte as palavras com `editor_reels.py ... --json-palavras` e aponte `"palavras"` no roteiro). 1º elemento em até 0,6s, no máximo 1,3s sem nada novo, sai até 1,2s depois do último; na pausa da fala, volta a pessoa. Onde a fala segue sem texto novo, o `gerar_liv.py` põe batidas sozinho (linhas anteriores recuam, fio sob a última, item aceso). Nunca "uma palavra entra e o motion fica parado": o gerador avisa.
- **Variar a cada vídeo:** a rota BR → EUA e os cards não são padrão. Use etapas, checklist, cartoes, degraus, barra, colunas, numero, anel, contador conforme a fala; rota só quando a fala é sobre ir de um lugar a outro. O gerador avisa repetição.
- **Design:** itens equivalentes (títulos de colunas e cartões) sempre no mesmo tamanho de fonte; o fio entre colunas com a mesma margem dos dois lados (medido pelo texto, nunca posição fixa).
- **Tela dividida:** motion sempre em tela cheia (nunca cobrir o rosto de um e deixar o outro).
- **Motion na tela = sem legenda.** O editor tira a legenda sozinho enquanto o motion cobre a tela; o conteúdo da cena fica centralizado na vertical na zona segura (200-1300 px). Maioria alinhada à esquerda, ~1 em 4 cenas centralizada.
- **CTA nos shorts:** depois da fala final, numa cauda de 3-4s (`--cauda 3.8`) com o CTA animado em tela cheia; vale para a versão A e a B.
- A pessoa fica na tela no gancho, nos momentos de confiança e no CTA; o B-roll entra nos conceitos, listas, números e comparações.
- Ao criar um modelo novo, confira quadros do resultado e registre em `motion/README.md`.

## Git
Commits locais à vontade; `git push` só quando a pessoa pedir. Mudança no editor: registrar no `CHANGELOG.md` e nos docs.
