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
- **Ads dinâmico (vertical):** `editor/ads_dinamico.py projetos/<p>/<ad>.py --versao A|B`. Texto ATRÁS da pessoa no gancho (recorte da pessoa pelo Vision, `editor/recorte_pessoa.swift`, no Mac; o motor mede quanto fica coberto e, acima de 18%, quebra em linhas ou põe na frente, acima da legenda; teste com `--ate 2 --quadros 1.1 --se-ilegivel atras|quebrar|frente`), B-roll por API (`broll_api.py`), film burns nas emendas (`assets/transicoes/`, fora do Git: copie o pacote no Mac), punch-ins por frase, legenda minimalista da LIV (a mesma dos shorts) nas cenas da pessoa e **lettering grande** nos inserts de imagem (Black × Light da mesma fonte, tracking apertado, véu suave na imagem), CTA em faixa azul no fim. **Imagens externas sempre aspiracionais.** LIV é escritório de advocacia licenciado nos EUA: imagem **formal, profissional, empoderada** (postura de autoridade, roupa e ambiente profissionais; nada de sorriso forçado de banco de imagem, objeto na cara da câmera ou fundo de estúdio vazio). LIV: falou em sonho, morar ou viver, é **sonho americano**: cenário claramente dos EUA (Santa Monica, Miami, NY…) e pessoas que representem o nosso público; nada que remeta a outro país, a não ser que a fala cite o país. Confira os quadros: o título do banco de imagens erra (um "Golden Gate" era uma ponte da Coreia). Descarte o banal ou errado (passaporte de outro país, bandeira a meio-mastro). Imigrar pode ser mais provocativa (topo de funil). Transição = flash rápido (film burn acelerado ~1,6x, `burn_velocidade`) com o som do próprio arquivo, que acaba junto com a luz. Card do CTA: respiro igual nos 4 lados, vãos proporcionais medidos pelo desenho das letras, nada encostado. Texto em faixa/bloco centralizado pelo peso visual das letras (sem acento), todas na mesma linha de base. Texto na frente sobre imagem clara: proteção sutil (esfumaçado escuro desfocado, sem contorno). Mande quadros para validar antes do render final (`--ate`/`--quadros`, que vão para `~/Library/Caches/editor-reels/ads/previas/`; na pasta do vídeo, só o vídeo). **Tudo dentro da área segura** (`SEGURA`: x 72-1008, y 300-1400), que sobrevive ao corte 4:5/3:4 do feed; o lettering fica numa base comum. Design: skills `frontend-design` e `design-taste-frontend` (princípios de tipografia). Versão B: tela dividida no gancho (B-roll em cima, pessoa embaixo, pergunta na faixa). Na LIV: sem sombra/contorno. Exemplo: `projetos/ads_liv/ad2.py`.
- **Estoque interno da LIV** (`assets/estoque_liv/`, Git LFS, 1080p; originais 4K no Drive): B-roll próprio (Dra. Lívia, equipe, escritório, processo). Só para a LIV; quando a fala é processo/equipe/atendimento, use antes do Pexels. Buscar/importar: `editor/estoque.py`. Ver o README da pasta.
- **Balão "Inscreva-se" (só corte longo da live da LIV; nunca em shorts nem na Imigrar):** entra sozinho no `--layout youtube` da LIV (`editor/inscricao.py`, asset `assets/inscreva_liv.mov`): ~1 por minuto com variação de alguns segundos, centralizado embaixo (40% da largura). **Nunca junto com o banner da live** (card do QR Code, embaixo no centro): o banner é detectado no vídeo e o balão espera ele sair ou pula aquela vez. Validar com `inscricao.py VIDEO --quadro 75` (PNG). Desligar: `--sem-inscreva`.
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
- **Imigrar explora mais** (`"marca": "imigrar"` no roteiro): interfaces (`chat`, `status`, `notificacao`, `busca`), contadores, marca-texto, painel diagonal. Nunca rosa sobre azul nem azul sobre rosa; fundo animado muda a cada cena; conteúdo no meio da tela, não no canto de cima.
- **Design:** itens equivalentes (títulos de colunas e cartões) sempre no mesmo tamanho de fonte; o fio entre colunas com a mesma margem dos dois lados (medido pelo texto, nunca posição fixa).
- **Quantidade de motion varia no lote (shorts com motion):** nunca todos com a mesma cobertura. Antes dos roteiros, `python3 motion/cobertura.py plano --marca <liv|imigrar> --fala ID=seg ...` sorteia uma meta por short (uns com pouco, outros com muito; Imigrar mais alto, LIV mais contido); o motion entra onde o assunto pede ilustração (lista, número, etapa, comparação, processo, prazo) e o resto fica com a pessoa. Depois, `motion/cobertura.py conferir projetos/<p>/motion/*.json` tem que passar sem o aviso de lote padronizado.
- **Tela dividida:** motion sempre em tela cheia (nunca cobrir o rosto de um e deixar o outro).
- **Motion na tela = sem legenda.** O editor tira a legenda sozinho enquanto o motion cobre a tela; o conteúdo da cena fica centralizado na vertical na zona segura (200-1300 px). Maioria alinhada à esquerda, ~1 em 4 cenas centralizada.
- **CTA nos shorts:** depois da fala final, numa cauda de 3-4s (`--cauda 3.8`) com o CTA animado em tela cheia; vale para a versão A e a B.
- A pessoa fica na tela no gancho, nos momentos de confiança e no CTA; o B-roll entra nos conceitos, listas, números e comparações.
- Ao criar um modelo novo, confira quadros do resultado e registre em `motion/README.md`.

## Git
Commits locais à vontade; `git push` só quando a pessoa pedir. Mudança no editor: registrar no `CHANGELOG.md` e nos docs.

## Quem roda os comandos
- **O Claude roda todos os comandos** (login, conectar canal, buscar B-roll, enviar vídeo, editar). Nunca peça para o usuário abrir o terminal ou rodar comando.
- O usuário só faz o que exige a identidade dele: clicar no link de login que chega no e-mail e clicar em "Permitir" na tela do Google ao conectar um canal. Códigos, senhas e chaves não passam pelo chat: se precisar de um segredo, ele mesmo cadastra no painel (Supabase → Secrets).
- Login no servidor do time: `python3 editor/conta.py entrar --email <email>` (rodar em segundo plano; a pessoa clica no link do e-mail e a sessão fica no Chaveiro do Mac).

## Publicação (YouTube)
- **Canais não se misturam:** vídeo da LIV só vai pro canal da LIV, e da Imigrar só pro da Imigrar (nem para procurar). O canal sai da marca do projeto.
- Caminho principal: `editor/studio.py`, que envia pelo YouTube Studio com o login da própria pessoa (editor ou administrador do canal; não precisa ser dono nem de credencial do Google). Roda num Chrome **invisível** (`--headless=new`) com o perfil do editor: rode com Bash `run_in_background` e a pessoa segue usando o Mac. Se a janela do login estiver aberta, o script fecha e usa o invisível; no fim do lote fecha tudo.
- Primeiro uso no Mac: `python3 editor/studio.py abrir` abre o "Chrome do editor" (perfil próprio, com janela); a pessoa faz login com a conta dela (a senha nunca passa pelo Claude). Depois `studio.py fechar`. `studio.py status` lista os canais que a conta enxerga; IDs em `editor/canais_youtube.json` (liv, imigrar).
- `projetos/<projeto>/publicacao.json`: por vídeo `titulo` (até 100 caracteres, no estilo do canal: pergunta sem resposta, 1 palavra em MAIÚSCULAS, emoji, 2 hashtags no fim), `resumo` (2 parágrafos fiéis ao que é falado; transcreva com Whisper local), `hashtags` (do vídeo) e `tags`. Longo: `resumo` (abertura) + `topicos` [[título, explicação], ...].
- A descrição sai do modelo do canal em `editor/descricoes.py` (LIV short: resumo → "👉 Quer compreender a situação específica do seu processo?" → link to.liv.law/gc-yt → hashtags → DISCLAIMER; longo: abertura → "Você vai conferir:" com 🔸 → links de avaliação de perfil e especialistas → hashtags → DISCLAIMER). **Hashtags numa linha só, logo antes do disclaimer; nada de hashtag no meio do texto nem depois do disclaimer — o disclaimer fecha a descrição.** Imigrar: modelo ainda a definir.
- Toda subida marca: não é para crianças, **sem promoção paga**, **conteúdo alterado/sintético: Não**.
- Agendamento de shorts (`lote ... --agendar`): lê no Studio a data do último short do canal (programado ou publicado) e programa 1 por dia, às 12h, a partir do dia seguinte. Confira antes com `--plano` (não envia).
- **Imigrar:** shorts e longos são agendados, mas ainda sem regra fixa: **sempre pergunte a data e a hora** antes de subir.
- Vídeos longos da LIV: sobem **privados**, sem agendar e sem estreia (`lote ... --tipo longo`, sem `--agendar`); o time programa depois. Antes, verifique se o vídeo já não foi publicado no canal.
- O envio só conta como feito depois que o script confere no Studio (título + "Programado"/"Privado"). Ele espera o upload **e as verificações de direitos autorais** terminarem antes de clicar em "Programar" (antes disso o Studio trava e o vídeo vira rascunho). Se sobrar rascunho com o arquivo completo, `concluir_rascunho()` termina sem subir de novo. Para corrigir vídeo já enviado (descrição, deixar privado) use `atualizar(youtube_id, ...)`; os ids ficam em `youtube_id` no publicacao.json. Datas já agendadas ficam em `~/Library/Application Support/editor-reels/agenda_youtube.json` (a lista do Studio demora a mostrar o recém-enviado). Rode um lote por vez: não rode outro comando do studio.py que feche o Chrome enquanto um lote está subindo.
- Publicar é ação externa: mostre a lista (títulos e datas) e espere o OK antes de cada lote; num canal ou fluxo novo, comece com 1 vídeo. Sem `--agendar` o vídeo fica privado.
- `editor/youtube.py` (API pelo Supabase) fica como alternativa, mas só funciona com a conta dona do canal e sobe só privado. Ver `docs/SUPABASE.md`.
