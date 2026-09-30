# motion

Animações feitas em HTML e renderizadas pelo [HyperFrames](https://github.com/heygen-com/hyperframes) (Apache 2.0), com fundo transparente, para o editor colar nos vídeos.

- `modelos/`: um arquivo por modelo. Cada um declara variáveis (marca, textos) e usa só a fonte e as cores da marca.
- `fontes` aponta para `../assets/fontes`; `vendor/gsap.min.js` é a biblioteca de animação, local (o render não depende de internet).
- Render **sempre local**. Telemetria desligada e comandos de nuvem bloqueados em `.claude/settings.json`: vídeo de cliente nunca sai da máquina.

## Modelos

| Modelo | O que é | Variáveis |
|---|---|---|
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

As skills de motion instaladas no projeto (`.claude/skills/`) ensinam a técnica: HyperFrames (render) e iart-ai/motion-skills (tempo, easing, tipografia cinética, gráficos). As do motion-skills citam Remotion: aqui usamos só a técnica delas e renderizamos pelo HyperFrames, porque o Remotion exige licença paga para empresa com mais de 3 pessoas.
