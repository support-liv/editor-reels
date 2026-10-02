#!/usr/bin/env python3
"""Estoque interno de vídeos da LIV (assets/estoque_liv/, Git LFS): importar e buscar.

    python3 editor/estoque.py importar "~/Downloads/LIV/Stock de Videos"   # converte p/ 1080p e cataloga
    python3 editor/estoque.py buscar processo vertical                      # acha por palavras do nome

Os nomes seguem orientação__quem__o-que-faz__onde__look__detalhe__duração (ex.:
vertical__dra-livia__assinando-processo__mesa-dela__terno-risca-de-giz__19s.mov). Na importação o vídeo vira
1080p H.264 SDR BT.709 (HDR do iPhone com tone mapping, P3 e faixa cheia convertidos), pra ficar leve no Git
e com a mesma cor em todos. Os originais 4K ficam no Drive.
"""
import json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import plataforma as P
PASTA = os.path.join(os.path.dirname(AQUI), "assets", "estoque_liv")
CATALOGO = os.path.join(PASTA, "catalogo.json")


def _info(arq):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height,pix_fmt,color_primaries,color_transfer:stream_side_data=rotation:format=duration",
                                   "-of", "json", arq], capture_output=True, text=True).stdout)
    return d["streams"][0], float(d["format"]["duration"])


def converter(origem, destino, orientacao):
    import editor_reels as er
    st, _ = _info(origem)
    args, filtro = er.entrada_video(origem)                 # HDR: tone mapping pelo VideoToolbox (como no editor)
    lado = "1080:1920" if orientacao == "vertical" else "1920:1080"
    cor = ""
    if not args:                                             # SDR: P3 → BT.709, faixa cheia (yuvj) → TV
        prim = st.get("color_primaries") or "bt709"
        if prim not in ("bt709", "unknown"):
            cor = f"colorspace=all=bt709:iprimaries={prim}:itrc=bt709:ispace=bt709:range=tv,"
    vf = f"{filtro}{cor}scale={lado}:force_original_aspect_ratio=decrease:flags=lanczos:out_range=tv,format=yuv420p"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + args + ["-i", origem, "-vf", vf,
                    *P.h264("7M"), "-maxrate", "9M", "-bufsize", "14M",
                    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
                    "-c:a", "aac", "-b:a", "96k", "-ac", "2", "-movflags", "+faststart", destino], check=True)


def campos(nome):
    base = os.path.splitext(os.path.basename(nome))[0]
    p = base.split("__")
    dur = re.match(r"(\d+)s$", p[-1])
    return {"arquivo": os.path.splitext(os.path.basename(nome))[0] + ".mp4", "orientacao": p[0], "quem": p[1].replace("-", " "),
            "acao": p[2].replace("-", " "), "local": p[3].replace("-", " ") if len(p) > 4 else "",
            "detalhes": [x.replace("-", " ") for x in p[4:-1]], "duracao_s": int(dur.group(1)) if dur else None,
            "uso_especial": "uso-especial" in base, "outra_marca": "imigrar" in base}


def importar(origem_pasta):
    origem_pasta = os.path.expanduser(origem_pasta)
    os.makedirs(PASTA, exist_ok=True)
    cat = json.load(open(CATALOGO)) if os.path.exists(CATALOGO) else {"videos": []}
    existentes = {v["arquivo"] for v in cat["videos"]}
    nomes = sorted(f for f in os.listdir(origem_pasta) if f.lower().endswith((".mp4", ".mov")) and "__" in f)
    for i, f in enumerate(nomes, 1):
        c = campos(f)
        destino = os.path.join(PASTA, c["arquivo"])
        if not os.path.exists(destino):
            converter(os.path.join(origem_pasta, f), destino, c["orientacao"])
        tam = os.path.getsize(destino) / 1e6
        print(f"  {i:2d}/{len(nomes)} {tam:5.1f} MB  {c['arquivo']}", flush=True)
        if c["arquivo"] not in existentes:
            cat["videos"].append(c)
    cat["videos"].sort(key=lambda v: v["arquivo"])
    json.dump(cat, open(CATALOGO, "w"), ensure_ascii=False, indent=1)
    print(f"catálogo: {len(cat['videos'])} vídeos")


def buscar(termos):
    cat = json.load(open(CATALOGO))
    t = [x.lower() for x in termos]
    for v in cat["videos"]:
        if all(x in v["arquivo"].lower().replace("-", " ") for x in t):
            print(v["arquivo"])


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    {"importar": lambda: importar(sys.argv[2]), "buscar": lambda: buscar(sys.argv[2:])}[sys.argv[1]]()
