# motion

Animações feitas em HTML e renderizadas pelo [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache 2.0), com fundo transparente, para o editor colar nos vídeos.

- `modelos/`: um arquivo por modelo. Cada um declara variáveis (marca, textos) e usa só a fonte e as cores da marca.
- `fontes` aponta para `../assets/fontes`; `vendor/gsap.min.js` é a biblioteca de animação, local (o render não depende de internet).
- Render **sempre local**. Telemetria desligada e comandos de nuvem bloqueados em `.claude/settings.json`: vídeo de cliente nunca sai da máquina.

## O que é motion aqui: B-roll de cena
O motion é uma **cena extra de B-roll** que entra por cima da pessoa e **explica a narrativa** enquanto ela fala: tela cheia na identidade da marca, texto cinético sincronizado com as palavras, efeitos sonoros no quadro exato, e entrada e saída com transição (a faixa diagonal do "V" da LIV). A voz continua; a legenda do editor continua por cima.

Não é enfeite em cima do gancho nem da legenda.

Como fazer uma cena:
1. Leia a fala com os tempos (`--so-cortes` e a transcrição) e escolha o trecho que ganha com explicação visual (conceito, lista, número, comparação). Deixe a pessoa na tela no gancho e nos momentos de confiança.
2. Cada animação e cada efeito sonoro vão no tempo da palavra dita (tempos relativos ao começo da cena).
3. Texto só entre 330 e 1090 px de altura: a faixa da legenda (~1150-1330) e a parte de baixo (interface do Reels) ficam livres.
4. Fundo com entrada e saída transparentes (a pessoa aparece antes e depois da transição).
5. Passe o checklist `motion-design/reference/quality-checklist.md` (camadas primária/secundária/ambiente, follow-through 50-150 ms, nada linear em movimento, stagger < 500 ms).
6. Texto com classe `fit` / `fit-grupo` e `data-max`: ajusta à largura e nunca corta na lateral.
7. Renderize em `--format mov`, confira quadros (contact sheet) e só então use: `--broll arquivo.mov@fonte:SEGUNDOS` (tempo da fala no bruto; o editor converte).

## Efeitos sonoros
`sfx/` (gerados por `gerar_sfx.py`, sem licença de terceiros): `whoosh`, `whoosh_grave` (entrada/virada), `pop` (elemento aparece), `tick` (contador, lista), `impacto` (texto batendo), `riscar` (negação), `subida` (tensão), `sino` (resolução/CTA). No HTML: `<audio id="..." src="sfx/pop.wav" data-start="0.41" data-duration="0.09" data-volume="0.7">`. O editor mixa os efeitos por baixo da voz.

## Modelos

| Modelo | O que é | Variáveis |
|---|---|---|
| `broll_perfil_liv` | **Referência principal.** B-roll da narrativa inteira (19s, 5 cenas): cards 3D "Formação acadêmica / Experiência sólida" com barras, rota BR→EUA com "CAMINHO LEGÍTIMO" em tipografia com volume e partículas, prédio carimbado + contador US$ 1.000.000 riscado, painel "Análise" com anel 0→100% e checklist, CTA "ANÁLISE DO SEU PERFIL" com selo SEM CUSTO. Fundo com 3 camadas de profundidade, grão, brilho; texto ajustado à largura; 32 efeitos sonoros no tempo das palavras. Posicionado inteiro com `--broll arquivo.mov@0` | — |
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
