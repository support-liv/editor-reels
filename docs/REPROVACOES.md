# Reprovações: o que a revisão devolveu e a lição de cada motivo

Todo vídeo reprovado na **Video Machine** (liv.ai) volta para cá: a Dra. Lívia revisa a LIV e a Marinna revisa a
Imigrar. Cada reprovação entra na seção do motivo que a revisora marcou, com o texto que ela escreveu. Antes de
editar, leia a seção de cada motivo que tem a ver com o vídeo. O que já foi reprovado não pode voltar.

**Atualizar:** antes de um lote novo, rode `python3 editor/licoes_da_aprovacao.py`. Ele acrescenta só as reprovações
novas. Nada daqui é apagado, e a lição escrita à mão não é mexida. A chave do liv.ai fica no Chaveiro (ver o começo do
script).

**Erro que aparece duas vezes vira regra.** Corrija a **causa** no editor ou no lote (não só o vídeo) e registre a
regra no `CLAUDE.md` ou no doc do assunto (`docs/CORTE_DE_FALA.md`, `docs/ENQUADRAMENTO.md`, `docs/PADROES.md`) e no
`CHANGELOG.md`. Depois acrescente na **Lição** da seção o que mudou.

Cada linha traz: data · marca · lote · `arquivo` (título) · quem revisou: o texto dela. Reprovação desfeita ou trocada
por aprovação não entra. Quando o motivo é **dado de cliente**, o texto dela fica só no liv.ai.

**Aprovados com ajustes** (desde 30/10/2026): quando a revisora aprova a ideia mas pede para refinar ("faltou
contexto"), o pedido entra nas seções **Ajuste · <motivo>**. O vídeo volta ao time e, com a versão nova (`_v2`), para
ela validar; o ajuste fica no guia mesmo depois de aprovado, porque o erro aconteceu.

<!-- placar -->
| Motivo | Vezes | Última |
|---|---|---|
| Não vale publicar | 1 | 29/10/2026 |
| Sem atalho (só o texto) | 1 | 29/10/2026 |
<!-- /placar -->

## Legenda errada

**Lição:** Confira a legenda **inteira** antes de entregar: vistos no formato oficial (E-2, O-1, EB-2 NIW, H-1B, Green
Card), nomes em inglês (Lake Nona, Tavistock) e concordância. O Whisper escreve "wincard", "Lequinona", "QMK". A palavra
que a revisora apontou vira correção fixa do lote e entra em `docs/CORTE_DE_FALA.md` → Legenda.

## Corte no meio da fala

**Lição:** Nunca corte palavra, nem no fim: use `--proteger-palavra --alinhar --vad`. Pedaço escolhido à mão termina no
FIM da última palavra (na transcrição literal). Rode a auditoria (`auditoria.py` + `conferir_alertas.py` +
`filtrar_confirmados.py`) antes de passar para `prontos/`. As causas conhecidas estão em `docs/CORTE_DE_FALA.md`.

## Fala repetida

**Lição:** O Whisper normal esconde repetição. Escolha os takes pela transcrição **literal**, use `--tirar-hesitacoes`
e confira as emendas (o fim de um take e o começo do seguinte). Ver `docs/CORTE_DE_FALA.md`.

## Aparece dado de cliente

**Lição:** Nada de cliente no vídeo: nome, rosto, voz, caso, documento, preço ou prazo, nem na fala nem na tela (tela
compartilhada, chat da live, documento na mesa). Leia a transcrição inteira atrás de nomes e olhe os quadros antes de
escolher os trechos. O texto da revisora **não** é copiado aqui, porque pode conter o próprio dado (ele fica no liv.ai).

## Enquadramento

**Lição:** Rosto enquadrado, legenda e caixas sem tapar rosto, verticais retas, nada distorcido. Live em tela dividida:
prévia com `--previa-enquadramento` validada e render com `--exigir-enquadramento`. Selfie na mão: `--crop-fixo` e
legenda abaixo do queixo. Ver `docs/ENQUADRAMENTO.md` e `docs/PADROES.md`, e confira quadros do vídeo pronto.

## Áudio

**Lição:** Voz clara e no mesmo volume do começo ao fim, com a trilha bem abaixo da fala (auditor-de-trilha). Áudio e
vídeo com a mesma duração (`ffprobe`; diferença acima de 0,05s é bug). Rode `editor/auditar_pronto.py` para achar
buracos e respiros, e ouça pelo menos um vídeo inteiro de cada tipo antes de mandar.

## Gancho

**Lição:** Gancho só pergunta, nunca responde, e a resposta tem de estar no vídeo. Sem promessa de aprovação ou de
prazo. Ver `docs/FORMATOS.md` e `docs/PADROES.md`, e mostre os ganchos no plano antes de renderizar.

## Não vale publicar

**Lição:** O trecho não se sustenta sozinho (assunto fraco, sem conclusão, repetido de outro corte, informação
sensível). Cada corte precisa de uma ideia que vale por si, com começo, meio e fim. Na dúvida, ofereça menos cortes e
mostre o texto de cada um no plano antes de renderizar.
- 29/10/2026 · LIV · Cartas com Aline Monteiro · `R7B_carta_fraca.mp4` (R7B carta fraca) · Livia: “fala que passou.. como se deixasse que tivesse feito algo nao bom” <!-- r:7 v:17 em:2026-10-29T19:23:12.669Z -->

## Sem atalho (só o texto)

**Lição:** A revisora escreveu sem escolher um atalho. Leia o texto: pedido que aparecer duas vezes vira regra no
`CLAUDE.md` ou no doc do assunto, e a seção ganha a lição.
- 29/10/2026 · LIV · Cartas com Aline Monteiro · `R8B_peso_do_especialista.mp4` (R8B peso do especialista) · Livia: “ficou confuso.” <!-- r:8 v:18 em:2026-10-29T19:24:20.285Z -->
