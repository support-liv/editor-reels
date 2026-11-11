#!/usr/bin/env python3
"""Pega cada base pronta (Imigrar_cortes/_base/*.mp4, sem CTA) e gera as 2 versões finais com o CTA preto animado:
Imigrar_cortes/YouTube/<nome>.mp4 (Inscreva-se no canal) e Imigrar_cortes/Instagram/<nome>.mp4 (Siga @imigrar.eua).
Pula o que já está em dia (final mais novo que a base e que o cta_imigrar.py). Uso: python3 finalizar_imigrar.py"""
import glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cta_imigrar as C

RAIZ = "/Volumes/Untitled/Imigrar_cortes"
PASTAS = {"youtube": "YouTube", "instagram": "Instagram"}

PADRAO = sys.argv[1] if len(sys.argv) > 1 else "imigrar_*.mp4"
for base in sorted(glob.glob(os.path.join(RAIZ, "_base", PADRAO))):
    if base.endswith(".video.mp4") or ".tmp" in base:
        continue
    nome = os.path.basename(base)
    for rede, pasta in PASTAS.items():
        os.makedirs(os.path.join(RAIZ, pasta), exist_ok=True)
        dest = os.path.join(RAIZ, pasta, nome.replace(".mp4", f"_{rede}.mp4"))
        ref = max(os.path.getmtime(base), os.path.getmtime(C.__file__))
        if not os.path.exists(dest) or os.path.getmtime(dest) < ref:
            C.aplicar(base, rede, dest)
