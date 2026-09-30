#!/usr/bin/env python3
"""Carrossel do Instagram (1080x1350) na fonte e nas cores da marca.

    python3 editor/carrossel.py roteiro.json --saida PASTA

roteiro.json:
{
  "marca": "liv",                       # liv | imigrar
  "nome": "c01_board",                  # prefixo dos arquivos
  "cards": [
    {"tipo": "capa",  "titulo": "O que é o board?", "subtitulo": "e por que ele decide tudo",
     "imagem": "/caminho/video.mp4@12.5"},          # opcional: foto (arquivo) ou quadro de vídeo (arquivo@segundos)
    {"tipo": "texto", "titulo": "1. É a prova", "texto": "Explicação curta, uma ideia por card."},
    {"tipo": "cta",   "titulo": "Quer saber o seu caminho?", "texto": "Comente PERFIL"}
  ]
}
A imagem nunca é distorcida: é ampliada por igual e recortada (cover).
"""
import argparse, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from editor_reels import MARCAS, entrada_video   # noqa: E402

W, H, MARGEM = 1080, 1350, 96

# paleta de cada card, só com cores da marca: (fundo, título, texto, destaque)
TEMAS = {
    "liv": {
        "capa": ((44, 54, 66), (255, 240, 230), (255, 240, 230), (255, 110, 31)),     # azul trust
        "texto": ((255, 240, 230), (44, 54, 66), (44, 54, 66), (255, 110, 31)),     # bege elegance
        "cta": ((255, 110, 31), (255, 255, 255), (255, 255, 255), (44, 54, 66)),    # laranja
    },
    "imigrar": {
        "capa": ((14, 89, 197), (255, 255, 255), (255, 255, 255), (249, 13, 91)),   # azul royal
        "texto": ((255, 255, 255), (20, 20, 20), (40, 40, 40), (249, 13, 91)),      # branco
        "cta": ((249, 13, 91), (255, 255, 255), (255, 255, 255), (255, 255, 255)),  # rosa
    },
}


def fonte(marca, peso, tam):
    f = ImageFont.truetype(MARCAS[marca]["fonte"], int(tam * MARCAS[marca]["escala"]))
    f.set_variation_by_name(peso)
    return f


def quebrar(d, texto, f, largura):
    linhas = []
    for par in texto.split("\n"):
        linha = ""
        for p in par.split():
            teste = (linha + " " + p).strip()
            if linha and d.textlength(teste, font=f) > largura:
                linhas.append(linha); linha = p
            else:
                linha = teste
        linhas.append(linha)
    return linhas


def escrever(d, xy, texto, f, cor, largura, entrelinha=1.15):
    x, y = xy
    for ln in quebrar(d, texto, f, largura):
        d.text((x, y), ln, font=f, fill=cor)
        y += int(f.size * entrelinha)
    return y


def carregar_imagem(ref):
    """arquivo de imagem, ou quadro de vídeo em 'arquivo@segundos' (convertido pra SDR se for HDR)."""
    if "@" in ref and not os.path.exists(ref):
        video, t = ref.rsplit("@", 1)
        ent_args, ent_filtro = entrada_video(video)
        out = subprocess.run(["ffmpeg", "-v", "error"] + ent_args + ["-ss", t, "-i", video, "-frames:v", "1",
                              "-vf", ent_filtro + "format=rgb24", "-f", "image2pipe", "-vcodec", "png", "-"],
                             capture_output=True).stdout
        from io import BytesIO
        return Image.open(BytesIO(out)).convert("RGB")
    return Image.open(ref).convert("RGB")


def cobrir(img, w, h, foco_y=0.35):
    """escala por igual até cobrir w x h e recorta o excesso (nunca estica)."""
    k = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * k), round(img.height * k)), Image.LANCZOS)
    x0 = (img.width - w) // 2
    y0 = int(min(max(0, img.height * foco_y - h / 2), img.height - h))
    return img.crop((x0, y0, x0 + w, y0 + h))


def card(marca, c, i, n):
    fundo, cor_tit, cor_txt, dest = TEMAS[marca][c.get("tipo", "texto")]
    im = Image.new("RGB", (W, H), fundo)
    d = ImageDraw.Draw(im)
    larg = W - 2 * MARGEM
    y = MARGEM
    if c.get("imagem"):
        alt = int(H * 0.52)
        im.paste(cobrir(carregar_imagem(c["imagem"]), W, alt), (0, 0))
        d.rectangle((0, alt, W, alt + 10), fill=dest)
        y = alt + 70
    else:                                        # sem foto: bloco de texto centralizado na altura
        blocos = [(c.get("titulo", ""), fonte(marca, "Black", 92 if c.get("tipo") == "capa" else 74), 1.05, 0),
                  (c.get("subtitulo", ""), fonte(marca, "Medium", 44), 1.15, 24),
                  (c.get("texto", ""), fonte(marca, "Medium", 46), 1.3, 36)]
        alt = sum(len(quebrar(d, t, f, larg)) * int(f.size * e) + esp for t, f, e, esp in blocos if t)
        y = max(MARGEM + 40, (H - alt) // 2 - 20)
    if c.get("tipo") != "capa" or not c.get("imagem"):
        d.rectangle((MARGEM, y - 36, MARGEM + 120, y - 26), fill=dest)          # traço de destaque
    tam_tit = 92 if c.get("tipo") == "capa" else 74
    y = escrever(d, (MARGEM, y), c.get("titulo", ""), fonte(marca, "Black", tam_tit), cor_tit, larg, 1.05)
    if c.get("subtitulo"):
        y = escrever(d, (MARGEM, y + 24), c["subtitulo"], fonte(marca, "Medium", 44), cor_txt, larg)
    if c.get("texto"):
        peso = "Black" if c.get("tipo") == "cta" else "Medium"
        y = escrever(d, (MARGEM, y + 36), c["texto"], fonte(marca, peso, 46), cor_txt, larg, 1.3)
    rodape = fonte(marca, "SemiBold", 30)
    d.text((W - MARGEM, H - 70), f"{i}/{n}", font=rodape, fill=cor_txt, anchor="rs")
    if i < n:
        d.text((MARGEM, H - 70), "arraste →", font=rodape, fill=dest, anchor="ls")
    return im


def main():
    ap = argparse.ArgumentParser(description="Gera o carrossel (1080x1350) na identidade da marca")
    ap.add_argument("roteiro")
    ap.add_argument("--saida", default="prontos")
    a = ap.parse_args()
    r = json.load(open(a.roteiro))
    marca, nome = r["marca"], r.get("nome", "carrossel")
    os.makedirs(a.saida, exist_ok=True)
    for i, c in enumerate(r["cards"], 1):
        arq = os.path.join(a.saida, f"{nome}_{i:02d}.png")
        card(marca, c, i, len(r["cards"])).save(arq)
        print(arq)


if __name__ == "__main__":
    main()
