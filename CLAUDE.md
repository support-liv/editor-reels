# editor-reels — instruções para o Claude

Você edita vídeos da **LIV** (escritório de imigração, meio de funil) e da **Imigrar** (topo de funil) com as ferramentas deste repositório. Quem pede é do time de marketing: fale português, sem jargão técnico, e entregue o vídeo pronto.

Leia antes de editar: `docs/FORMATOS.md` (o que cada formato leva), `docs/PADROES.md` (padrões visuais aprovados) e `docs/OPCOES.md` (todas as opções do editor).

## Primeira vez neste computador (faça sozinho, sem detalhes técnicos)
Se ainda não existe o marcador `instalado.txt` em `plataforma.pasta_dados()`:
1. Confira se o setup já rodou (Mac `./setup.sh`; Windows `setup.ps1`); se não, rode. Só fale com a pessoa se o
   sistema pedir permissão ("Clique em Sim na janela que abriu") ou login.
2. Rode o teste piloto (`editor/teste_piloto.py`; Windows `py -3.12 -X utf8 editor\teste_piloto.py`) **sem narrar**.
3. Tudo ok: grave o marcador e diga só **"Pronto! Pode me mandar o vídeo que quiser editar."**
   Se algo falhou: diga em uma frase simples o que não vai funcionar ainda (ex.: "as animações ainda não funcionam
   neste computador") e peça para enviar ao suporte o arquivo do relatório (mostre o caminho de `piloto/`). Não
   suba nada para o GitHub (o acesso pode ser só de leitura).
Fale sempre em linguagem simples com a pessoa: ela não precisa saber de comandos, pastas técnicas ou ferramentas.

## Como trabalhar: guiado, ativo, sempre oferecendo o próximo passo

Quem usa a ferramenta **não sabe tudo o que ela faz** nem sempre sabe o que quer. O Claude conduz: analisa sozinho,
segue quando entende, **pergunta quando tem dúvida** e, **ao fim de cada etapa, oferece o próximo passo**.
Use a ferramenta de perguntas com opções (botões), sempre com a sua recomendação marcada e uma frase do que cada
opção faz. Nada de jargão técnico na pergunta.

1. **Receber o vídeo e assistir.** Confira se é bruto (se já tem legenda/grafismo gravado, **não queime outra legenda
   por cima**: peça o bruto ou use `--sem-legenda` e avise). Transcreva (`editor/transcrever_lote.py`), veja quadros e
   resolução. Deduza: marca, tipo (live, anúncio, depoimento…), assunto, público, objetivo, ganchos.
2. **Contar o que dá para fazer e perguntar o que a pessoa quer**, com a sugestão já marcada. Ex.: "Esse material
   rende 1 corte longo + 6 shorts. Quer: (a) corte longo e shorts [recomendado], (b) só shorts, (c) anúncio dinâmico…".
   Na mesma rodada, o que não dá para deduzir: **canal de destino** (o CTA muda: YouTube "Veja a live completa no
   canal"; Instagram palavra-chave, sempre confirmar), **quer trilha sonora?**, **quer motion/animações?**, live solo em
   720p (fundo desfocado x tela cheia), nomes com grafia duvidosa ("Livre" = LIV, "Marina Damás" = Marinna Damásio).
   Não pergunte o que o vídeo já responde nem o que tem padrão.
3. **Mostrar o plano e validar antes de renderizar:** cortes com o texto de cada um, ganchos, CTAs; quadros de
   conferência quando houver design (texto, motion, card). Renderize só depois do ok.
4. **Renderizar, conferir e entregar** (ver "Conferência"). Diga onde estão os arquivos.
5. **Oferecer o próximo passo — sempre.** Depois da entrega, pergunte com opções o que faz sentido, por exemplo:
   - "Quer agendar no YouTube?" → se sim: gera título, descrição no padrão, tags e hashtags, mostra a lista com as
     datas (LIV: shorts no dia seguinte ao último agendado, 12h; longos privados. Imigrar: perguntar a data), espera o
     ok e sobe pelo Studio em segundo plano;
   - "Quer trilha sonora?" (se ainda não tem) → auditor-de-trilha + prévias;
   - "Quer versão para outro formato?" (stories, carrossel, anúncio dinâmico, tela dividida no gancho…);
   - "Quer ajustar algo?" (gancho, corte, legenda).
   Uma pergunta por vez quando a resposta muda o caminho; agrupe as que são independentes.

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
- **Ads dinâmico (vertical):** `editor/ads_dinamico.py projetos/<p>/<ad>.py --versao A|B`. Texto ATRÁS da pessoa no gancho (recorte da pessoa pelo Vision, `editor/recorte_pessoa.swift`, no Mac; o motor mede quanto fica coberto e, acima de 18%, quebra em linhas ou põe na frente, acima da legenda; teste com `--ate 2 --quadros 1.1 --se-ilegivel atras|quebrar|frente`), B-roll por API (`broll_api.py`), film burns nas emendas (`assets/transicoes/`, fora do Git: copie o pacote no Mac), punch-ins por frase, legenda minimalista da LIV (a mesma dos shorts) nas cenas da pessoa e **lettering grande** nos inserts de imagem (Black × Light da mesma fonte, tracking apertado, véu suave na imagem), CTA em faixa azul no fim. **Imagens externas sempre aspiracionais.** LIV é escritório de advocacia licenciado nos EUA: imagem **formal, profissional, empoderada** (postura de autoridade, roupa e ambiente profissionais; nada de sorriso forçado de banco de imagem, objeto na cara da câmera ou fundo de estúdio vazio). LIV: falou em sonho, morar ou viver, é **sonho americano**: cenário claramente dos EUA (Santa Monica, Miami, NY…) e pessoas que representem o nosso público; nada que remeta a outro país, a não ser que a fala cite o país. Confira os quadros: o título do banco de imagens erra (um "Golden Gate" era uma ponte da Coreia). Descarte o banal ou errado (passaporte de outro país, bandeira a meio-mastro). Imigrar pode ser mais provocativa (topo de funil). Transição = flash rápido (film burn acelerado ~1,6x, `burn_velocidade`) com o som do próprio arquivo, que acaba junto com a luz. Card do CTA: respiro igual nos 4 lados, vãos proporcionais medidos pelo desenho das letras, nada encostado. Espaço entre palavras é o natural da fonte, medido entre as letras (nunca pelo halo/margem da imagem). Texto em faixa/bloco centralizado pelo peso visual das letras (sem acento), todas na mesma linha de base. Texto na frente sobre imagem clara: proteção sutil (esfumaçado escuro desfocado, sem contorno). Mande quadros para validar antes do render final (`--ate`/`--quadros`, que vão para `~/Library/Caches/editor-reels/ads/previas/`; na pasta do vídeo, só o vídeo). **Tudo dentro da área segura** (`SEGURA`: x 72-1008, y 300-1400), que sobrevive ao corte 4:5/3:4 do feed; o lettering fica numa base comum. Design: skills `frontend-design` e `design-taste-frontend` (princípios de tipografia). Versão B: tela dividida no gancho (B-roll em cima, pessoa embaixo, pergunta na faixa). Na LIV: sem sombra/contorno. Exemplo: `projetos/ads_liv/ad2.py`.
- **Trilha sonora** (`assets/trilhas/`, Git LFS; `editor/trilhas.py`): **sempre pergunte ao usuário se quer trilha** no vídeo. A trilha combina com o clima da narrativa (corporativo, inspirador, emocional, tenso/polêmico…) e com a marca (LIV formal, sem humor/polêmica/estilo de outro país; Imigrar pode provocar). **A trilha fica sempre bem abaixo da fala** (o `mixar` põe ~16 LU abaixo + ducking). Antes de usar, rode o agente **auditor-de-trilha** (licença, clima, marca, ritmo, volume) e mande as prévias. Licença: `bloqueada` nunca; em anúncio pago, `nao` nunca e `conferir` só com o aviso de confirmar a licença.
- **Estoque interno da LIV** (`assets/estoque_liv/`, Git LFS, 1080p; originais 4K no Drive): B-roll próprio (Dra. Lívia, equipe, escritório, processo). Só para a LIV; quando a fala é processo/equipe/atendimento, use antes do Pexels. Buscar/importar: `editor/estoque.py`. Ver o README da pasta.
- **Balão "Inscreva-se" (só corte longo da live da LIV; nunca em shorts nem na Imigrar):** entra sozinho no `--layout youtube` da LIV (`editor/inscricao.py`, asset `assets/inscreva_liv.mov`): ~1 por minuto com variação de alguns segundos, centralizado embaixo (40% da largura). **Nunca junto com o banner da live** (card do QR Code, embaixo no centro): o banner é detectado no vídeo e o balão espera ele sair ou pula aquela vez. Validar com `inscricao.py VIDEO --quadro 75` (PNG). Desligar: `--sem-inscreva`.
- **Títulos de capítulo (só vídeo longo PRODUZIDO da LIV, 16:9 para YouTube; nunca em corte de live nem em shorts):** `editor/capitulos.py` (ferramenta `titulos_de_capitulo`). Entrevista com perguntas: o título é a **pergunta como foi feita** (sem "Doutora Lívia"), em até 2 linhas (branco em cima, final em laranja inteiro embaixo, mesmo tamanho em todas), numa **cartela própria de 4s** com o degradê sólido da LIV (azul + calor laranja no canto, monograma), **sem vídeo atrás** (`--sem-fundo` sobre a cartela); som de entrada suave (ar + acorde no tom da trilha, pico ~-25 dB); a trilha toca **o vídeo inteiro**, baixinha e contínua sob a fala (~20 dB abaixo da voz, ducking leve `mixar(..., ducking=1.6)`, nunca sumindo depois da pergunta) e sobe ~9 dB na cartela; passa para a resposta com **light leak** (pico de luz no corte, som dele ~-27 dB, nunca estourado). Na descrição do YouTube os capítulos usam nomes curtos (`"capitulos"` no publicacao.json). Mostrar a prévia antes de renderizar. Look de cor: oferecer prévia de 3 looks lado a lado com o original (céu de janela estourado: joelho suave nos realces sem escurecer o rosto); o aprovado da LIV é o "cinema natural" (`LOOK` em `projetos/c1265/montar.py`), só nos trechos da pessoa, nunca nas cartelas. Saída em 4K quando o bruto é 4K (`--4k`: o YouTube comprime melhor; precisa de ~10 GB livres). Exemplo completo: `projetos/c1265/montar.py`.
- **Fala de entrevista:** tirar recomeços, repetições e muletas ("né", "é..." isolado, "E..." esticado); pausa > 0,4s vira corte; cada corte no silêncio real entre palavras (nunca no meio); tomada interrompida (mão na câmera, correção de fundo) sai inteira; plano aberto/médio/close trocando a cada corte. Conferir câmera torta e equipamento no quadro já na análise.
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

## Plugin do Claude (como a equipe instala)
- O repositório é também um **plugin do Claude Code** (`.claude-plugin/plugin.json` + marketplace `liv-imigrar` em `.claude-plugin/marketplace.json`). Ele traz o servidor MCP `editor-reels` (19 ferramentas: `situacao`, `instalar`, `teste_piloto`, `analisar_video`, `transcrever`, `criar_video`, `criar_anuncio`, `buscar_imagens_externas`, `buscar_no_estoque_liv`, `sugerir_trilha`, `colocar_trilha`, `youtube_publicar`, `ver_tarefa`…), a skill `editor-de-videos` e o agente `auditor-de-trilha`. Funciona na aba **Code** do app (não na aba Chat).
- O plugin instalado não traz os arquivos grandes (LFS): o servidor roda a partir da **pasta de trabalho** (clone completo na Mesa ou na pasta do usuário, ou `EDITOR_REELS_DIR`), que o `servidor_mcp/iniciar.mjs` atualiza sozinho (git pull + lfs pull) a cada início.
- **Acesso ao GitHub da equipe:** um token compartilhado, **só leitura e só deste repositório**, colado uma vez na instalação e guardado no gerenciador de senhas do Git (nunca no endereço do repositório nem em arquivo). Se `situacao` disser que "as atualizações pararam" (token vencido), explique em uma frase e peça o acesso novo ao administrador; o editor segue funcionando na versão atual. Troca de token: o administrador cria um novo (só leitura, este repositório, validade 6-12 meses) e cada pessoa cola uma vez.
- Mudou este CLAUDE.md? Rode `python3 servidor_mcp/gerar_skill.py` para atualizar a skill do plugin, e suba a versão em `plugin.json`. Valide com `claude plugin validate .`.

## Mac e Windows
- O repositório roda nos dois. Tudo que muda entre sistemas está em `editor/plataforma.py` (pastas de cache, codificador H.264 — VideoToolbox no Mac, NVENC/QuickSync/AMF ou libx264 no Windows —, HDR do iPhone, Chrome, detector de rostos — Vision no Mac, OpenCV YuNet no Windows —, recorte da pessoa — Vision / MediaPipe —, emoji e login guardado — Chaveiro / Gerenciador de Credenciais). **Nunca escreva caminho de Mac (`~/Library/...`, `/Applications/...`) nem `h264_videotoolbox` direto no código: use `plataforma`.**
- Instalação: Mac `./setup.sh`; Windows `powershell -ExecutionPolicy Bypass -File .\setup.ps1` (instala via winget; Python 3.12 por causa do MediaPipe).
- **Limpeza automática:** `plataforma.limpar_temporarios()` roda 1x por dia (editor, anúncio e servidor MCP): apaga animações intermediárias de `motion/renders` (2 dias), prévias/testes/análises (7), máscaras (14) e B-roll sem uso (60). Nunca toca nos vídeos prontos nem no login do Studio. Avisa quando o disco tem menos de 10 GB.
- **Onde ficam os vídeos prontos:** sempre em **Mesa → `Editor Reels` → `<PROJETO>`** (`plataforma.pasta_renders()`; no Windows a Mesa real é achada mesmo no OneDrive). Projeto novo usa `~/Desktop/Editor Reels/<PROJETO>` passando por `plataforma.caminho()`. Na pasta de saída, só os vídeos finais (prévias vão para a pasta temporária).
- **Teste piloto** (computador novo ou depois de mudar algo de plataforma): quando a pessoa pedir "roda o teste piloto", rode `editor/teste_piloto.py` (Windows: `py -3.12 -X utf8 editor\teste_piloto.py`). Ele testa 12 peças (ambiente, LFS, codificador, HDR, rostos, recorte, emoji, login guardado, short completo, anúncio dinâmico, trilha, Chrome/Studio) e grava `piloto/relatorio_*.md`. Depois faça commit **só do relatório** numa branch `piloto-<nome-do-computador>` e push, e conte o resultado à pessoa em linguagem simples.
- No Windows os comandos são no PowerShell e o Python é `py -3.12 -X utf8` (no lugar de `python3`; o `-X utf8` garante acento e emoji); scripts que chamam outros scripts usam `sys.executable`; `npx`/`npm` via `plataforma.cmd()`; atalho de teclado no Playwright é `ControlOrMeta`. Abra e grave arquivos de texto sempre em UTF-8.

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
