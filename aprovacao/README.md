# Aprovação de cortes (link no celular)

Página publicada como artefato do Claude: **https://claude.ai/artifact/RfUp2o5YzHF9xLVc9pDucu**
("Aprovação de Cortes LIV"). Abre numa tela de início ("Você tem X vídeos para aprovar" + "Começar agora"), com placar
discreto de aprovados/reprovados no topo durante a avaliação. Visual de app de swipe (cartão em tela cheia, botões redondos sobre o vídeo, abas Avaliar · Lotes · Resumo). Um vídeo por vez; enquanto o vídeo roda, a faixa de baixo
(título, arquivo, botões) some para não parecer parte do vídeo, e volta quando a pessoa toca na tela (pausa).
**Aprovar** (ou arrastar para a direita) pede confirmação num balão e passa para o próximo; **Reprovar** (ou arrastar para a esquerda) pede o motivo (atalhos + texto) e segue; trocar de vídeo é como nos Stories e num slider: tocar na lateral esquerda volta, na direita avança (mesmo
sem decidir), e as setas laterais aparecem com o vídeo pausado; ao chegar no fim, se algum vídeo ficou sem decisão, um
aviso lista os pendentes e leva até eles; no fim aparece "Tudo certo!" dizendo quantos foram aprovados e reprovados, com o placar e a lista dos reprovados. Uma pessoa avalia
cada lote.

Fonte da página: `aprovacao-cortes-liv.html` (republicar com o Artifact tool passando o `url` acima; de outra conversa,
leia o artefato antes). Capacidades: `db` (regra: `lotes` só editores escrevem), `user` (nome de quem avalia), `assets`
(vídeos e capas).

### Sem login (link aberto)

Quem abre o link sem estar logado no Claude não lê o banco do artefato. Por isso os lotes também ficam **embutidos na
página** (`<script type="application/json" id="dados-embutidos">`, uma lista com os docs de `lotes` + `id`): os vídeos
e capas (`/_blob/...`) tocam para qualquer pessoa com o link. Dois modos:

- **link** (logado e com permissão de gravar): lotes e decisões vêm do banco, como antes.
- **local** (sem login, ou conta só de leitura, ou gravação recusada): as decisões ficam no aparelho (`localStorage`,
  chave `aprovacao:lote:<id>`; o nome em `aprovacao:nome`) e sobrevivem a fechar e abrir o link. A tela de início avisa,
  e o Resumo mostra "Seu nome" + **Copiar resumo**: um texto com o lote, quem avaliou, data, aprovados, reprovados com o
  motivo e os sem decisão (com o nome do arquivo). Se o quadro bloquear a área de transferência, o texto aparece numa
  caixa selecionada para copiar. A pessoa cola no WhatsApp/e-mail e manda.

Sem login, o claude.ai mostra um aviso fixo embaixo ("Sign in to see this artifact's data"); a página sobe a barra de
abas e a folha de motivo (`--folga`) para nada ficar por baixo dele.

## Dados (banco do artefato)

- `lotes/<id>`: o lote. `titulo`, `descricao`, `marca`, `criadoEm`, `ordem` (maior aparece primeiro), `pasta` (onde
  estão os originais) e `videos`: lista de `{id, titulo, gancho, formato, orientacao, duracao, src, capa, arquivo}`.
  `src`/`capa` são `/_blob/<id>` dos assets enviados ao artefato.
- `decisoes/<id do lote>`: `{itens: {<id do vídeo>: {status: "aprovado"|"reprovado", motivos, detalhe, motivo, em,
  por}}, por, atualizadoEm, total, concluidoEm}`. `por` é o id opaco da pessoa (resolver o nome com a ação `profiles`).

## Lote novo

1. Versões leves dos vídeos (limite de 15 MB por arquivo): Reels 720x1280, libx264 ~1,4 Mbps + AAC 96k,
   `-movflags +faststart`; longos 854x480 em 2 passadas com a taxa calculada para ~14 MB. Capa: um JPG por vídeo.
2. Enviar como assets do artefato (`Artifact` publish com `url`, `asset: true`, `file_paths`; até ~40 MB por chamada).
3. Gravar `lotes/<id>` com o `ArtifactData` (`set`), `ordem` maior que a dos anteriores.
4. **Embutir o lote na página** (lista em `dados-embutidos`, com o `id`) e republicar: sem isso, quem abre sem login
   não vê o lote novo. Para tirar um lote antigo, tire das duas partes.
5. Depois da avaliação, ler `decisoes/<id>` e refazer só os reprovados, pelo motivo. Quem avaliou sem login manda o
   resumo copiado (não vai para o banco).

Para gravar direto no link, quem avalia precisa estar logado e ter acesso de **Colaborador** no menu Compartilhar do
artefato. Sem isso, avalia no modo local e manda o resumo.

## Link da Imigrar (Marinna aprova)

Artefato separado, na identidade da Imigrar (Inter Tight, rosa #F90D5B; fundo escuro neutro, nunca rosa sobre azul):
**https://claude.ai/artifact/QUb2X8DWDM7EbLTXyqKbCk** ("Aprovação Imigrar"). Mesma tela, mesmo formato de dados e mesmo
passo a passo do link da LIV, com banco e vídeos próprios. Fonte: `aprovacao-imigrar.html` (gerada a partir da página da
LIV trocando marca, fonte e cores; a tela de início cumprimenta quem avalia pelo nome). Primeiro lote:
`marinna-reuniao-estrategica` (os 6 Reels da Mari, de `Downloads/Mari IMG_5069/prontos`).
