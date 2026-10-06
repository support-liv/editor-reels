#!/usr/bin/env python3
"""Gera a skill `editor-de-videos` do plugin a partir do CLAUDE.md (fonte única das regras).
Rode depois de mudar o CLAUDE.md:  python3 servidor_mcp/gerar_skill.py"""
import os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
regras = open(os.path.join(RAIZ, "CLAUDE.md"), encoding="utf-8").read()
cabecalho = '''---
name: editor-de-videos
description: Editar vídeos da LIV e da Imigrar (shorts, cortes longos de live, anúncios dinâmicos, trilha, B-roll, legendas, motion) e publicar no YouTube. Use sempre que a pessoa mandar um vídeo, pedir edição, cortes, shorts, reels, anúncio, trilha, legenda, ou agendar/publicar no YouTube.
---

# Editor de vídeos LIV / Imigrar

Você tem as ferramentas do servidor **editor-reels** (MCP): `situacao`, `instalar`, `teste_piloto`, `analisar_video`,
`transcrever`, `criar_video`, `criar_anuncio`, `buscar_imagens_externas`, `buscar_no_estoque_liv`, `sugerir_trilha`,
`colocar_trilha`, `youtube_publicar`, `ver_tarefa` e outras. **Prefira essas ferramentas aos comandos de terminal.**
Os comandos citados nas regras abaixo são o que cada ferramenta roda por dentro; use o terminal só para o que não tem
ferramenta. Comece sempre por `situacao`: se não estiver pronto, rode `instalar` e depois `teste_piloto` (sem narrar
detalhes técnicos). Tarefas demoradas devolvem um número: acompanhe com `ver_tarefa`.

Os arquivos do editor (roteiros de exemplo, estoque, trilhas) ficam na pasta do plugin; os vídeos prontos, na Mesa,
pasta "Editor Reels".

---

'''
corpo = re.sub(r"^# .*\n", "", regras, count=1)
destino = os.path.join(RAIZ, "skills", "editor-de-videos", "SKILL.md")
os.makedirs(os.path.dirname(destino), exist_ok=True)
open(destino, "w", encoding="utf-8").write(cabecalho + corpo)
print("skill gerada:", destino)
