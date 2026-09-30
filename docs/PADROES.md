# Padrões validados

Decisões tomadas e aprovadas na edição dos vídeos do IN26 (set/2026). Mude só com motivo, e registre no CHANGELOG.

## Formato
- 1080x1920, 30 fps, H.264 14 Mbps, AAC 192 kbps, -14 LUFS.
- **Cor:** o iPhone grava em HDR (HLG/Dolby Vision, BT.2020). Sem conversão, a imagem fica lavada. O editor converte para SDR BT.709 com tone mapping (VideoToolbox) e marca o arquivo como BT.709.

## Zona segura (9:16: Reels, Stories, Shorts)
- **Tudo que precisa ser visto fica em x 60-1020, y 153-1510.** O canto de baixo à direita (x > 835, y > 1205) é dos botões de interação: nada importante ali.
- Legenda do editor: faixa 1190-1390 (62% da altura).
- Motion: bloco principal 250-950, apoio 980-1170, nada na faixa da legenda. Conferir com `python3 motion/conferir.py VIDEO` (desenha a zona segura, a legenda e os botões por cima dos quadros).

## Legenda
- **LIV: sem contorno e sem sombra no texto** (é clean). Texto bege num bloco sólido azul #2C3642 arredondado, palavra falada em laranja.
- **Imigrar:** texto branco com contorno preto, palavra falada em rosa.
- **Fonte e cores da marca, sempre** (legenda, gancho e CTA): LIV em Darker Grotesque Black, Imigrar em Inter Tight Black (`assets/fontes/`). O tamanho equivale aos 38 px aprovados em Arial Black (a primeira versão era 58; foi reduzida 35% a pedido do time).
- Caixa alta, até 3 palavras ou 18 caracteres por vez, palavra falada na cor de destaque da marca, contorno preto.
- Altura: **62%** da tela nos Reels orgânicos. **55%** em anúncio (o Meta cobre mais a parte de baixo com botão e texto). **64%** em selfie (o rosto ocupa o meio da tela; a legenda fica abaixo do queixo).

## Gancho (caixa de texto no começo)
- 3,2 segundos, CAIXA ALTA, na fonte da marca. Fundo só com cores da paleta (ver `--cor-caixa`).
- Posição: **290 px do topo**, abaixo da barra do Instagram (~250 px).
- **Nunca tapa rosto.** O editor gera o quadro final, procura os rostos e escolhe:
  1. em cima, se não encostar na cabeça;
  2. senão, no lugar da legenda (a legenda some enquanto a caixa aparece);
  3. se as duas encostarem (selfie), onde cobrir menos olhos e boca.
- **O gancho nunca entrega a resposta.** Ele é a pergunta ou a curiosidade; a resposta está no vídeo e a pessoa precisa assistir pra saber. Nada de "Mito.", "não define você", "é porque precisam" no gancho.
- **Bandeira:** 🇺🇸 e 🇧🇷 sempre **depois** da palavra que complementam ("americano 🇺🇸", "nos EUA 🇺🇸?", "no Brasil 🇧🇷"). Nunca substituem a palavra: sozinha, a bandeira não é entendida de primeira.

## CTA
- Reels orgânico: caixa "Quer saber se existe um caminho pro seu perfil? Link na bio" nos últimos 3,5s.
- Anúncio: **sem caixa**. A pessoa fala o CTA e o Meta coloca o botão.
- Não usar o CTA falado "segue o perfil da X" (pedido do time).

## Cortes
- Pelo **áudio**, não só pelo tempo do Whisper (ele estica o fim da palavra para o silêncio, e isso aparece como respiro/olhada pro lado no fim da frase).
- Folga de 0,05s antes da voz e 0,10s depois. Pausas internas acima de 0,25s saem.
- **Sincronia:** cada corte tem duração em quadros inteiros, igual no vídeo e no áudio. Conferir com `ffprobe`: a duração do vídeo e a do áudio do arquivo final devem bater.
- Nunca usar take em que a pessoa está lendo o celular (auditoria de olhar).
- **Shorts: fala enxuta.** `--tirar-hesitacoes --respiro 0.18`: sem "éé"/"então, assim" e com pausas de no máximo 0,18s.
- Pergunta do entrevistador: fica no vídeo quando vira gancho ("pergunta + resposta"). Em cena com várias pessoas, aparece em quadro aberto.

## Tela dividida (live com duas pessoas)
- Quem vai em cima é escolhido com `--cima` (na Plano EUA 2027: a Dra. Lívia). Cada metade é 1080x960.
- **Enquadramento fixo** no vídeo inteiro, sem zoom alternado: live é câmera parada, o recorte mexendo fica estranho.
- Rosto de cima a ~42% do quadro dela e o de baixo a ~56%, pra sobrar fundo na divisa.
- **Legenda e tarja ficam na divisa** (y = 960). A legenda some enquanto a tarja aparece.
- **Tarja alternando branco, azul e rosa** entre os cortes. A legenda corrida continua rosa.
- O recorte fica nos **70% de cima** da imagem da live: abaixo disso o StreamYard mostra comentários e banners (medido: até 73% da altura).

## Live com uma pessoa (layout "quadro")
- A imagem da live aparece **nítida no meio**, sem ampliar demais (live é 720p): recorte de 58% da largura x 66% da altura, centrado na pessoa.
- Os 34% de baixo da live ficam de fora: é onde aparecem os comentários do chat (medido: até 68% da altura no trecho solo).
- Fundo: a própria cena desfocada e escurecida. Gancho acima do quadro, legenda abaixo, nunca sobre o rosto.
- Enquadramento fixo, como na tela dividida.

## WhatsApp (layout "quadrado")
- 1080x1080, 6 Mbps (arquivo leve pra mandar no WhatsApp). Enquadramento dinâmico, com punch-in de 80% alternando por bloco de fala: não é live, e o corte parado ficava monótono.
- Sem gancho e sem CTA: é mensagem direta pra quem agendou.
- Legenda na cor da marca, 30 px, a 84% da altura.
- Quem fala mais travado: `--dinamico` (zoom a cada ~2,5s) e `--respiro 0.35`, como no Thiago (cortar toda pausa acima de 0,25s deixava a fala robótica). Gagueira e travada que sobrarem: achar no bruto (energia/Whisper) e tirar com `--tirar`.
- **Nunca distorcer a imagem** (perspectiva, esticar, mudar proporção): deforma o rosto. Câmera torta se corrige só girando.
- Câmera torta: `--endireitar` (mede as verticais e escolhe o ângulo) ou `--girar` com o ângulo medido nas verticais da cena (portas, janelas, prateleiras). O recorte deixa folga pra não aparecer canto preto.

## Enquadramento
- Solo: 93% da largura, com punch-in de 82% alternando **por bloco de fala** (não por pedaço, senão o zoom pisca).
- Entrevistado de um lado (`--pessoa direita`): 55% da largura, centrado no rosto dele.
- Conversa (`--pessoa voz`): 34% da largura, fecha em quem fala pelo tom de voz (medido no bloco inteiro). Voz aguda acima de 200 Hz = 2ª pessoa da esquerda.
- Rosto a ~38% do topo do quadro.

## Conteúdo (Imigrar / LIV)
- Imigrar é topo de funil; LIV é meio. Entrevistados que não são da LIV não dão orientação jurídica: nos vídeos da LIV, a informação técnica entra como "o que a LIV explicou pra gente".
- Sem promessa de aprovação ou prazo. Números citados pelo entrevistado sem fonte ficam de fora ou vão para a lista de conferência.
