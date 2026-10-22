"""Letterings editoriais (serifa New York, romano x itálico, tons pastel) em PNG transparente 1920x1080.

Cada card é uma lista de linhas; cada linha é uma lista de pedaços (texto, estilo, cor).
Estilos: "rom" (New York regular), "ita" (itálico), "rot" (rótulo pequeno em caixa alta espaçada).
O bloco fica alinhado à esquerda numa coluna à direita do quadro (sobre o banco), com uma sombra
difusa bem suave para ler sobre fundo claro, sem contorno.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
ROM = "/System/Library/Fonts/NewYork.ttf"
ITA = "/System/Library/Fonts/NewYorkItalic.ttf"
PASTEL = {
    "creme": (246, 236, 220),
    "rosa": (236, 196, 190),
    "salvia": (200, 216, 196),
    "ceu": (196, 212, 232),
    "areia": (230, 208, 176),
}


ROT = 0.36                                               # rótulo pequeno: fração do tamanho do texto


def largura(d, ln, tam):
    x = 0
    for txt, est, cor in ln:
        if est == "rot":
            f = fonte("rot", int(tam * ROT))
            x += sum(d.textlength(ch, font=f) + int(tam * ROT * 0.26) for ch in txt.upper())
        else:
            x += d.textlength(txt, font=fonte(est, tam))
    return x


def fonte(estilo, tam):
    f = ImageFont.truetype(ITA if estilo == "ita" else ROM, tam)
    nome = {"rom": b"Regular", "ita": b"Regular Italic", "rot": b"Semibold"}[estilo]
    f.set_variation_by_name(nome)
    return f


def desenhar(linhas, x0=1080, y_centro=560, tam=92, entrelinha=1.08, so_ate=None, so_linha=None, margem=110):
    """so_ate: quantas linhas desenhar; so_linha: só essa linha, no lugar dela (entrada linha a linha)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    medidas = []
    for ln in linhas:
        alt = 0
        for txt, est, cor in ln:
            t = int(tam * ROT) if est == "rot" else tam
            alt = max(alt, t)
        medidas.append(alt)
    total = sum(m * entrelinha for m in medidas)
    y = y_centro - total / 2
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    larg = max(largura(d, ln, tam) for ln in linhas)
    x0 = min(x0, W - margem - larg)                       # o bloco nunca encosta na borda direita
    for i, ln in enumerate(linhas):
        if so_ate is not None and i >= so_ate:
            break
        if so_linha is not None and i != so_linha:
            y += medidas[i] * entrelinha
            continue
        x = x0
        alt = medidas[i]
        for txt, est, cor in ln:
            if est == "rot":
                f = fonte("rot", int(tam * ROT))
                espaco = int(tam * ROT * 0.26)
                for ch in txt.upper():
                    d.text((x, y + alt * 0.72), ch, font=f, fill=PASTEL[cor] + (255,), anchor="ls")
                    x += d.textlength(ch, font=f) + espaco
                x += espaco
            else:
                f = fonte(est, tam)
                d.text((x, y + alt * 0.80), txt, font=f, fill=PASTEL[cor] + (255,), anchor="ls")
                x += d.textlength(txt, font=f)
        y += alt * entrelinha
    # sombra difusa (sem contorno): só para descolar do fundo claro
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    alfa = camada.split()[3].filter(ImageFilter.GaussianBlur(18))
    sombra.putalpha(alfa.point(lambda v: int(v * 0.55)))
    img = Image.alpha_composite(img, sombra)
    return Image.alpha_composite(img, camada)


def veu(lado="direita", forca=0.42):
    """degradê escuro suave no lado do texto (cinematográfico), 1920x1080."""
    import numpy as np
    x = np.arange(W, dtype=np.float32)
    t = (x - W * 0.45) / (W * 0.55) if lado == "direita" else (W * 0.55 - x) / (W * 0.55)
    a = (255 * forca * np.clip(t, 0, 1) ** 1.4).astype(np.uint8)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[:, :, :3] = (12, 16, 22)
    arr[:, :, 3] = a[None, :]
    return Image.fromarray(arr, "RGBA")


# ------------------------------------------------------------------ identidade Imigrar (Inter Tight, rosa e azul)
INTER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "fontes", "InterTight[wght].ttf")
ROSA, AZUL, BRANCO = (249, 13, 91), (14, 89, 197), (255, 255, 255)


def inter(peso, tam):
    f = ImageFont.truetype(INTER, tam)
    f.set_variation_by_name(peso)
    return f


def desenhar_imigrar(linhas, x0=1100, y_centro=700, tam=92, so_linha=None, margem=110):
    """bloco de lettering na identidade da Imigrar: caixa alta Inter Tight Black, branco, destaque em tarja rosa
    (ou azul), rótulo pequeno espaçado. Estilos: "rot", "txt", "rosa" (tarja), "azul" (tarja).
    Alinhado à esquerda, sombra difusa leve para ler sobre o fundo."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    camada = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    f_txt, f_rot = inter(b"Black", tam), inter(b"SemiBold", int(tam * 0.30))
    pad_x, pad_y = int(tam * 0.16), int(tam * 0.10)
    alt_txt, alt_rot = int(tam * 1.06), int(tam * 0.46)

    def larg(ln):
        x = 0
        for txt, est in ln:
            if est == "rot":
                x += sum(d.textlength(c, font=f_rot) + tam * 0.06 for c in txt.upper())
            else:
                x += d.textlength(txt.upper(), font=f_txt) + (2 * pad_x if est in ("rosa", "azul") else 0)
        return x

    altura = [alt_rot if all(e == "rot" for _, e in ln) else alt_txt for ln in linhas]
    x0 = min(x0, W - margem - max(larg(ln) for ln in linhas))
    y = y_centro - sum(altura) / 2
    for i, ln in enumerate(linhas):
        if so_linha is not None and i != so_linha:
            y += altura[i]
            continue
        x = x0
        base = y + altura[i] * 0.80
        for txt, est in ln:
            if est == "rot":
                for c in txt.upper():
                    d.text((x, base), c, font=f_rot, fill=BRANCO + (235,), anchor="ls")
                    x += d.textlength(c, font=f_rot) + tam * 0.06
                continue
            t = txt.upper()
            w = d.textlength(t, font=f_txt)
            if est in ("rosa", "azul"):
                topo = base - tam * 0.74 - pad_y
                d.rounded_rectangle([x, topo, x + w + 2 * pad_x, base + pad_y + tam * 0.04], radius=int(tam * 0.14),
                                    fill=(ROSA if est == "rosa" else AZUL) + (255,))
                d.text((x + pad_x, base), t, font=f_txt, fill=BRANCO + (255,), anchor="ls")
                x += w + 2 * pad_x
            else:
                d.text((x, base), t, font=f_txt, fill=BRANCO + (255,), anchor="ls")
                x += w
        y += altura[i]
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    alfa = camada.split()[3].filter(ImageFilter.GaussianBlur(16))
    sombra.putalpha(alfa.point(lambda v: int(v * 0.50)))
    img = Image.alpha_composite(img, sombra)
    return Image.alpha_composite(img, camada)
