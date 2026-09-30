# Changelog

Cada mudança com o motivo, para o time entender por que o editor faz o que faz.

## 0.25 (30/09/2026) - motion na identidade da Imigrar
- `gerar_liv.py` com tema por marca (`"marca": "imigrar"` no roteiro): paleta rosa #F90D5B, azul royal #0E59C5, branco e preto; Inter Tight Black; painel em diagonal com faixa dupla; palavras entrando com impacto; marca-texto chapado atrás das palavras de destaque; faixas sutis correndo no fundo; sons mais fortes. A LIV continua clean e igual.
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
