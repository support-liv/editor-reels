# motion

Animações feitas em HTML e renderizadas pelo [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache 2.0), com fundo transparente, para o editor colar nos vídeos.

- `modelos/`: um arquivo por modelo. Cada um declara variáveis (marca, textos) e usa só a fonte e as cores da marca.
- `fontes` aponta para `../assets/fontes`; `vendor/gsap.min.js` é a biblioteca de animação, local (o render não depende de internet).
- Render **sempre local**. Telemetria desligada e comandos de nuvem bloqueados em `.claude/settings.json`: vídeo de cliente nunca sai da máquina.

## Nível de motion por marca
- **LIV: clean, só elementos do manual de identidade.** Fundos lisos (bege, azul, laranja), Darker Grotesque, fio fino com arcos, seta dupla, arco duplo, estrela no círculo, losangos ♦♦, a curva bege/azul com fio laranja do outdoor/posts como transição, sublinhado laranja fino. Movimento calmo (revelação por máscara, traços se desenhando, deslizes). **Sem sombra, contorno, extrusão, brilho, grão, partícula, tremida ou carimbo.** Som discreto. Referência: `broll_perfil_liv`.
- **Imigrar: pode explorar** (3D, partículas, impacto, contador, extrusão), sempre na paleta e na fonte dela. Base: `broll_perfil_explorado`.

## Zona segura
Texto e elementos importantes em x 60-1020, y 153-1510, fora do canto dos botões (x > 835, y > 1205) e da faixa da legenda (1190-1390). Bloco principal 250-950, apoio 980-1170. Conferir sempre com `python3 motion/conferir.py VIDEO --tempos ...` antes de entregar.

## O que é motion aqui: B-roll de cena
O motion é uma **cena extra de B-roll** que entra por cima da pessoa e **explica a narrativa** enquanto ela fala: tela cheia na identidade da marca, texto cinético sincronizado com as palavras, efeitos sonoros no quadro exato, e entrada e saída com transição (a faixa diagonal do "V" da LIV). A voz continua; a legenda do editor continua por cima.

Não é enfeite em cima do gancho nem da legenda.

Como fazer uma cena:
0. **Legenda e posição:** com o motion na tela o editor tira a legenda (os textos não competem); o gerador centraliza o bloco da cena na vertical (200-1300 px) e varia o alinhamento (esquerda na maioria, ~1 em 4 centralizada; `"alinhar"` força).
   **Regras de ritmo (aprendidas na LIVE 80):** o texto entra palavra por palavra no tempo da fala (roteiro com `"palavras": "palavras/S1.json"`, exportado com `editor_reels.py ... --json-palavras`); 1º elemento em até 0,6s, no máximo 1,3s parado, sai até 1,2s depois do último. Onde a fala segue sem texto novo, o gerador põe batidas sozinho (foco, fio, item aceso, respiro); `"batidas": false` na cena desliga. Varie os componentes a cada vídeo (etapas, checklist, cartoes, degraus, barra, colunas, numero, anel, contador; rota só quando a fala é sobre ir de um lugar a outro). Se a fala pausa, a cena sai. **Design:** itens equivalentes (títulos de colunas e cartões) sempre no mesmo tamanho, e o fio entre colunas com a mesma margem dos dois lados (o gerador mede o texto; nunca posição fixa). Tela dividida: sempre tela cheia. CTA dos shorts depois da fala, na cauda (`--cauda 3.8`).
1. Leia a fala com os tempos (`--so-cortes` e a transcrição) e escolha o trecho que ganha com explicação visual (conceito, lista, número, comparação). Deixe a pessoa na tela no gancho e nos momentos de confiança.
2. Cada animação e cada efeito sonoro vão no tempo da palavra dita (tempos relativos ao começo da cena).
3. Texto só entre 330 e 1090 px de altura: a faixa da legenda (~1150-1330) e a parte de baixo (interface do Reels) ficam livres.
4. Fundo com entrada e saída transparentes (a pessoa aparece antes e depois da transição).
5. Passe o checklist `motion-design/reference/quality-checklist.md` (camadas primária/secundária/ambiente, follow-through 50-150 ms, nada linear em movimento, stagger < 500 ms).
6. Texto com classe `fit` / `fit-grupo` e `data-max`: ajusta à largura e nunca corta na lateral.
7. Renderize em `--format mov`, confira quadros (contact sheet) e só então use: `--broll arquivo.mov@fonte:SEGUNDOS` (tempo da fala no bruto; o editor converte).

## Gerador de B-roll da LIV
`python3 motion/gerar_liv.py roteiro.json` monta o HTML a partir de um roteiro (cenas com tempo, painel `cheio`/`baixo`/`cima`, cor e elementos: `rotulo`, `linha`, `sub`, `risco`, `icone`, e `cta`). Exemplos em `projetos/live80/motion/`. Tempos das palavras: `editor_reels.py VIDEO --trechos ... --tempos-palavras`.

### Componentes de jornada (LIV, clean)
Além de texto e ícones, o roteiro pode contar a história com componentes chapados, de traço fino e movimento leve:
- `rota`: dois pontos (ex.: BR → EUA) ligados por um caminho que se desenha, com um ponto viajando (`de`, `para`, `t`, `dur`).
- `etapas`: linha do tempo vertical; a jornada aparece apagada e cada etapa acende no tempo da fala (`itens: [{texto, t}]`).
- `checklist`: itens recebendo ✓ ou × (`itens: [{texto, t, ok}]`).
- `anel`: progresso 0 → 100% com número contando (`t`, `dur`, `legenda`).
- `contador`: número subindo (`de`, `ate`, `prefixo`, `sufixo`).
- `cartoes`: dois cards pra comparar (`itens: [{titulo, texto, t, risco_t, destaque_t}]`); o card destacado acende e o outro volta ao normal.
Use quando a fala tem jornada, etapas, comparação ou número; texto puro só quando a frase é o que importa.

## Quando o corte muda depois do motion pronto
`motion/remapear.py roteiro.json antes.json depois.json --cauda 3.8` ajusta todos os tempos do roteiro pelo plano novo (salve os planos com `editor_reels.py ... --json-cortes`). Depois é só gerar e renderizar de novo.

## Efeitos sonoros
`sfx/` (gerados por `gerar_sfx.py`, sem licença de terceiros): `whoosh`, `whoosh_grave` (entrada/virada), `pop` (elemento aparece), `tick` (contador, lista), `impacto` (texto batendo), `riscar` (negação), `subida` (tensão), `sino` (resolução/CTA). No HTML: `<audio id="..." src="sfx/pop.wav" data-start="0.41" data-duration="0.09" data-volume="0.7">`. O editor mixa os efeitos por baixo da voz.

## Modelos

| Modelo | O que é | Variáveis |
|---|---|---|
| `broll_perfil_liv` | **Referência LIV (clean).** 19s, 5 cenas em painéis que entram com a curva da marca: "Formação acadêmica e experiência sólida" (fio com arco, seta dupla), "um caminho legítimo" (seta dupla sólida), "sem empresa / sem investir milhões" riscados (estrela no círculo), "se existe esse caminho para você" (arco duplo), CTA laranja "Análise do seu perfil, sem custo". 13 sons discretos. `--broll arquivo.mov@0` | — |
| `broll_perfil_explorado` | **Base para a Imigrar.** Mesma narrativa com 3D, extrusão, partículas, contador, impactos e 32 sons (trocar paleta/fonte para a Imigrar) | — |
| `broll_caminho_liv` | B-roll de 7s, 2 atos: "FORMAÇÃO + EXPERIÊNCIA" e "UM CAMINHO LEGÍTIMO / sem empresa / sem US$ 1.000.000" riscados, com whoosh, pops, ticks do contador, riscos e impacto | — (exemplo de referência) |
| `cta_palavra_chave` | "Comente PALAVRA" entrando, pulsando e saindo (4s), abaixo da faixa da legenda | `marca`, `rotulo`, `palavra`, `topo` |

## Usar
Pelo editor (renderiza e cola sozinho):
```bash
python3 editor/editor_reels.py VIDEO --marca liv --cta-animado PERFIL
```
Render avulso de um modelo:
```bash
cd motion
npx hyperframes render . -c modelos/cta_palavra_chave.html --format mov --variables '{"marca":"liv","palavra":"PERFIL"}' -o renders/cta.mov
```
Depois: `python3 editor/editor_reels.py VIDEO --animacao motion/renders/cta.mov@12.5`.

## Novo modelo
1. Copie um modelo existente; mantenha `data-width/height` do formato (1080x1920 Reels, 1080x1080 WhatsApp, 1920x1080 YouTube).
2. Fonte e cores só da marca (classes `.liv` / `.imigrar`). Nada sobre o rosto nem na faixa da legenda.
3. Renderize em `--format mov` (transparente) e confira quadros antes de usar.
4. Documente na tabela acima e no CHANGELOG.

As skills de motion instaladas no projeto (`.claude/skills/`) ensinam a técnica: HyperFrames (render e regras de animação: `hyperframes-animation/rules`), iart-ai/motion-skills (tempo, easing, tipografia cinética, gráficos), LottieFiles `motion-design` (checklist de qualidade e `reference/troubleshooting.md`: "parece robótico/barato/lento") e ecc `motion-foundations/patterns/advanced` (princípios de UI motion; o código delas é React, aqui só os princípios). As do motion-skills citam Remotion: aqui usamos só a técnica delas e renderizamos pelo HyperFrames, porque o Remotion exige licença paga para empresa com mais de 3 pessoas.
