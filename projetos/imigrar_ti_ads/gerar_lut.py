"""Gera o LUT 'cinema pastel' (.cube 33³): contraste suave em S, pretos levantados, realces rolando suave,
sombras azul-petróleo, realces e pele quentes, verdes contidos. Usado no anúncio horizontal IMG_4811."""
import numpy as np, sys

N = 33
saida = sys.argv[1] if len(sys.argv) > 1 else "cinema_pastel.cube"
g = np.linspace(0, 1, N)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")          # .cube: R varia mais rápido
x = np.stack([r, gg, b], -1).reshape(-1, 3)
PESOS = np.array([0.2126, 0.7152, 0.0722])


def curva_s(v, forca=0.12):
    # S suave e monotônica: 0→0, 0.5→0.5, 1→1
    return v - forca * np.sin(2 * np.pi * v) / (2 * np.pi)


x = np.clip(curva_s(x), 0, 1)
x = 0.04 + x * 0.91                                      # pretos levantados, branco a 95%
lum = x @ PESOS
sombra = np.clip(1 - lum / 0.45, 0, 1)[:, None]
luz = np.clip((lum - 0.55) / 0.45, 0, 1)[:, None]
x = x + sombra * np.array([-0.018, 0.006, 0.026]) + luz * np.array([0.022, 0.010, -0.020])
l2 = (x @ PESOS)[:, None]
quente = np.clip((x[:, 0] - x[:, 2]) * 3, 0, 1)[:, None]  # pele / madeira: perde menos saturação
x = l2 + (x - l2) * (0.82 + 0.12 * quente)
x = np.clip(x, 0, 1)

with open(saida, "w") as f:
    f.write('TITLE "cinema pastel"\nLUT_3D_SIZE 33\n')
    for c in x:
        f.write(f"{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}\n")
print("ok", saida)
