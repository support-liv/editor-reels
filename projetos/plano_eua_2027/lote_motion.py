#!/usr/bin/env python3
"""Live "Plano EUA 2027" (Imigrar): shorts com motion na identidade da Imigrar (teste).

Os mesmos cortes do lote_live.py, com fala enxuta, motion em tela cheia no ritmo da fala e CTA animado
depois da fala final (cauda de 3,8s).

    python3 projetos/plano_eua_2027/lote_motion.py palavras [L05 L10 ...]   # exporta as palavras (pro roteiro)
    python3 projetos/plano_eua_2027/lote_motion.py duracao [L05 ...]    # duração da fala (roteiro = fala + 3,8)
    python3 projetos/plano_eua_2027/lote_motion.py B [L05 L10 ...]          # monta com motion/renders/plano27_<id>.mov
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from lote_live import CORTES, TROCAS, VIDEO, CORES   # mesmos trechos, ganchos e correções da legenda

EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
MOTION = os.path.join(AQUI, "..", "..", "motion", "renders")
PALAVRAS = os.path.join(AQUI, "motion", "palavras")
SAIDA = os.path.expanduser(os.environ.get("LIVE_SAIDA_MOTION", "~/Desktop/PLANO_EUA_2027/motion"))
CAUDA = 3.8


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "B"
    filtro = sys.argv[2:]
    os.makedirs(PALAVRAS, exist_ok=True)
    for i, (cid, nome, trechos, gancho) in enumerate(CORTES):
        if filtro and cid not in filtro:
            continue
        cmd = ["python3", EDITOR, VIDEO, "--layout", "dividido", "--cima", "direita", "--marca", "imigrar",
               "--cor-caixa", CORES[i % 3], "--trechos", trechos, "--gancho", gancho,
               "--tirar-hesitacoes", "--respiro", "0.18", "--cauda", str(CAUDA)]   # fala enxuta + cauda pro CTA
        for t in TROCAS:
            cmd += ["--trocar", t]
        if modo == "palavras":
            cmd += ["--json-palavras", os.path.join(PALAVRAS, f"{cid}.json")]
        elif modo == "duracao":                       # duração da fala (o roteiro usa fala + cauda)
            cmd += ["--tempos-palavras"]
        else:
            cmd += ["--broll", os.path.join(MOTION, f"plano27_{cid}.mov") + "@0",
                    "--nome", f"{cid}B_{nome}", "--saida", SAIDA]
        print(f"######## {cid} {nome}", flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
