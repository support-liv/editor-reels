#!/usr/bin/env python3
"""Lote modelo: copie esta pasta para projetos/<seu_projeto> e preencha VIDEOS.
Rodar tudo:            python3 lote_modelo.py
Só conferir os cortes: python3 lote_modelo.py --so-cortes
Só alguns:             python3 lote_modelo.py V01 V03
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")

# pasta com os vídeos brutos (ou: export PASTA_PROJETO=/caminho)
PASTA_PROJETO = os.path.expanduser(os.environ.get("PASTA_PROJETO", "~/Desktop/MEU_PROJETO"))
PASTA = PASTA_PROJETO + "/"
SAIDA = os.path.join(PASTA_PROJETO, "prontos")

MARCA = "imigrar"                                   # ou "liv"
CTA = "Quer saber se existe um caminho pro seu perfil? Link na bio"   # "" para anúncio
TROCAS = []                                         # correções de legenda: "errado=certo"

VIDEOS = [
    # id, nome, vídeo, trechos, gancho, extras
    ("V01", "exemplo", PASTA + "IMG_0000.MOV", "0.0-30.0",
     "Gancho em caixa alta com bandeira 🇺🇸", {}),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    for vid, nome, video, trechos, gancho, extras in VIDEOS:
        if filtro and vid not in filtro:
            continue
        print(f"\n######## {vid} {nome}", flush=True)
        cmd = [sys.executable, EDITOR, video, "--marca", MARCA, "--trechos", trechos, "--gancho", gancho,
               "--nome", f"{vid}_{nome}", "--saida", SAIDA]
        if CTA:
            cmd += ["--cta", CTA]
        if extras.get("pessoa"):
            cmd += ["--pessoa", extras["pessoa"]]
        if extras.get("aperto"):
            cmd += ["--aperto", str(extras["aperto"])]
        if extras.get("y_legenda"):
            cmd += ["--y-legenda", str(extras["y_legenda"])]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd += ["--so-cortes", "--checar-olhar"]
        subprocess.run(cmd, cwd=PASTA_PROJETO)
