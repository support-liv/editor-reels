# Aprovação de cortes (link no celular)

Página publicada como artefato do Claude: **https://claude.ai/artifact/RfUp2o5YzHF9xLVc9pDucu**
("Aprovação de Cortes LIV"). Um vídeo por vez, no estilo do Tinder: **Aprovar** (ou arrastar para a direita) passa
para o próximo; **Reprovar** (ou arrastar para a esquerda) pede o motivo (atalhos + texto) e segue; **Voltar** reabre
o anterior para trocar a decisão; no fim aparece "Tudo certo!" com o placar e a lista dos reprovados. Uma pessoa avalia
cada lote.

Fonte da página: `aprovacao-cortes-liv.html` (republicar com o Artifact tool passando o `url` acima; de outra conversa,
leia o artefato antes). Capacidades: `db` (regra: `lotes` só editores escrevem), `user` (nome de quem avalia), `assets`
(vídeos e capas).

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
3. Gravar `lotes/<id>` com o `ArtifactData` (`set`), `ordem` maior que a dos anteriores. A página mostra sozinha.
4. Depois da avaliação, ler `decisoes/<id>` e refazer só os reprovados, pelo motivo.

Quem avalia precisa de acesso de **Colaborador** no menu Compartilhar do artefato (Leitor só assiste).
