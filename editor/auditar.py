#!/usr/bin/env python3
"""Auditoria de um vídeo bruto: cada frase do Whisper com a % do tempo olhando pra baixo/lado.
Uso: python3 auditar.py VIDEO [VIDEO ...]
Frases marcadas com ▼ provavelmente são leitura do celular: prefira o take seguinte, falado pra câmera."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from editor_reels import transcrever, olhando_pra_baixo, AQUI

for v in sys.argv[1:]:
    base = os.path.splitext(os.path.basename(v))[0]
    dados = transcrever(v, os.path.join(AQUI, "transcricoes", base + ".json"))
    print(f"\n===== {base}")
    for sg in dados["segmentos"]:
        fr = olhando_pra_baixo(v, sg["s"], sg["e"])
        marca = "▼" if fr > 0.4 else " "
        print(f"{marca} {sg['s']:6.1f}-{sg['e']:6.1f} [{fr:4.0%}] {sg['t'][:95]}")
