#!/usr/bin/env python3
"""Auditoria de um vídeo PRONTO: silêncios longos (denunciam corte) e trechos com a pessoa olhando pra baixo.
Uso: python3 auditar_pronto.py arquivo.mp4 [...]"""
import sys, os, subprocess, json, tempfile, shutil
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from editor_reels import energia_db, DETECTOR, run, garantir_detector

garantir_detector()
for v in sys.argv[1:]:
    db, lim = energia_db(v)
    fala = db > lim
    fala = np.convolve(fala.astype(int), np.ones(3, int), "same") >= 2
    idx = np.where(fala)[0]
    pausas = []
    for a, b in zip(idx[:-1], idx[1:]):
        if (b - a) * 0.02 > 0.35:
            pausas.append((a * 0.02, (b - a) * 0.02))
    ini = idx[0] * 0.02 if len(idx) else 0
    fim = (len(fala) - idx[-1]) * 0.02 if len(idx) else 0
    # olhar
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-i", v, "-vf", "fps=4,scale=360:-2", os.path.join(tmp, "%04d.jpg")])
    imgs = sorted(os.listdir(tmp))
    pts = []
    for i, ln in enumerate(run([DETECTOR] + [os.path.join(tmp, f) for f in imgs]).strip().splitlines()):
        fs = [f for f in json.loads(ln) if len(f) >= 6]
        if fs:
            f = max(fs, key=lambda f: f[2]); pts.append(((i + 0.5) / 4, f[4]))
    shutil.rmtree(tmp)
    base = np.percentile([p for _, p in pts], 25) if pts else 0
    baixo = [t for t, p in pts if p > base + 0.16]
    # agrupa momentos seguidos olhando pra baixo (>= 1 s)
    grupos, g = [], []
    for t in baixo:
        if g and t - g[-1] > 0.3:
            grupos.append(g); g = []
        g.append(t)
    if g: grupos.append(g)
    grupos = [(x[0], x[-1]) for x in grupos if x[-1] - x[0] >= 0.75]
    nome = os.path.basename(v)
    print(f"\n{nome}: início {ini:.2f}s de silêncio, fim {fim:.2f}s")
    print("  pausas > 0,35s:", ", ".join(f"{t:.1f}s ({d:.2f}s)" for t, d in pausas) or "nenhuma")
    print("  olhando pra baixo >= 0,75s:", ", ".join(f"{a:.1f}-{b:.1f}s" for a, b in grupos) or "nenhum")
