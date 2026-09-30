#!/usr/bin/env python3
"""Folha de conferência de um vídeo 9:16 (pronto ou cena de motion), com a zona segura desenhada por cima.

    python3 motion/conferir.py VIDEO [--tempos 1,4.5,8] [--saida folha.png]

Zona segura (padrão do time, Reels/Stories/Shorts 1080x1920):
  verde    = zona segura: x 60-1020, y 153-1510
  vermelho = botões de interação (x > 835, y > 1205): nada importante ali
  amarelo  = faixa da legenda do editor (y 1190-1390, com 62% de altura): o motion não põe texto ali
Sem --tempos, pega 12 quadros espalhados."""
import argparse, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
SEGURA = (60, 153, 1020, 1510)
BOTOES = (835, 1205, 1020, 1510)
LEGENDA = (60, 1190, 1020, 1390)


def duracao(v):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v],
                                capture_output=True, text=True).stdout)


def quadro(v, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", v, "-frames:v", "1",
                          "-vf", f"scale={W}:{H},format=rgba", "-f", "rawvideo", "-pix_fmt", "rgba", "-"],
                         capture_output=True).stdout
    im = Image.frombytes("RGBA", (W, H), raw)
    fundo = Image.new("RGBA", (W, H), (120, 120, 120, 255))       # transparência aparece cinza
    fundo.alpha_composite(im)
    return fundo


def marcar(im, t):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle(LEGENDA, outline=(255, 220, 0, 255), width=4)
    d.rectangle(BOTOES, outline=(255, 0, 0, 255), width=4)
    d.rectangle(SEGURA, outline=(0, 255, 90, 255), width=6)
    d.rectangle((0, 0, 260, 70), fill=(0, 0, 0, 200))
    d.text((16, 14), f"{t:.2f}s", fill=(255, 255, 255, 255), font_size=44)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--tempos")
    ap.add_argument("--saida", default="conferencia.png")
    a = ap.parse_args()
    tempos = [float(x) for x in a.tempos.split(",")] if a.tempos else list(np.linspace(0.3, duracao(a.video) - 0.2, 12))
    miniaturas = [marcar(quadro(a.video, t), t).resize((270, 480)) for t in tempos]
    col = 6
    lin = (len(miniaturas) + col - 1) // col
    folha = Image.new("RGBA", (270 * col, 480 * lin), (30, 30, 30, 255))
    for i, m in enumerate(miniaturas):
        folha.alpha_composite(m, ((i % col) * 270, (i // col) * 480))
    folha.convert("RGB").save(a.saida)
    print(a.saida)


if __name__ == "__main__":
    sys.exit(main())
