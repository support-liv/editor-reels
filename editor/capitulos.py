#!/usr/bin/env python3
"""Cartela de título de capítulo da LIV para VÍDEOS LONGOS PRODUZIDOS (16:9, YouTube). Não é para corte de live
nem para shorts.

    python3 editor/capitulos.py VIDEO --capitulo "12.5|A vida|no Brasil" --capitulo "95|Os vistos|que funcionam"
    python3 editor/capitulos.py VIDEO --capitulo ... --quadros      # só as prévias (PNG) para validar antes

Cada capítulo: "segundo|parte branca|parte em destaque (laranja)". Uma das partes pode ficar vazia.
Visual (definido a partir da referência do time, out/2026): a cena continua rodando por trás, escurecida em azul LIV,
com um degradê marrom/laranja puxando do canto superior direito; o monograma da LIV em linha fina no canto superior
direito; o título centralizado em caixa alta, branco + destaque laranja. Entra e sai suave (~3s no total).
"""
import argparse, json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plataforma as PLAT

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTE = os.path.join(RAIZ, "assets", "fontes", "InterTight[wght].ttf")
AZUL, MARROM, LARANJA, LINHA = (44, 54, 66), (148, 89, 67), (255, 110, 31), (232, 220, 210)
DUR, ENTRA, SAI = 3.2, 0.45, 0.5       # tempo na tela, fade de entrada e de saída (s)
SEM_FUNDO = False                      # --sem-fundo: a cartela já é o degradê sólido (sem vídeo atrás)


def fundo_solido(L, A):
    """o degradê da cartela sem vídeo atrás: azul LIV com o calor do canto superior direito."""
    im = Image.new("RGBA", (L, A), AZUL + (255,))
    im.alpha_composite(camada_fundo(L, A))
    return im.convert("RGB")


def fonte(tam, peso):
    f = ImageFont.truetype(FONTE, tam)
    f.set_variation_by_axes([peso])
    return f


def camada_fundo(L, A):
    """azul LIV por cima de tudo + degradê marrom/laranja vindo do canto superior direito."""
    x = np.linspace(0, 1, L)[None, :]
    y = np.linspace(0, 1, A)[:, None]
    g = np.clip((x - 0.42) / 0.58, 0, 1) ** 1.4 * (1 - 0.55 * y)
    quente = np.array(MARROM) * 0.7 + np.array(LARANJA) * 0.3
    cor = np.array(AZUL)[None, None, :] * (1 - g[..., None]) + quente[None, None, :] * g[..., None]
    alfa = 0.74 + 0.04 * g
    rgba = np.dstack([cor, alfa[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def camada_monograma(L, A):
    """monograma da LIV em linha: grade 2x2 com quartos de círculo (redesenhado a partir da referência)."""
    k = 4                                    # desenha 4x maior e reduz: linha fina e lisa
    s = round(A * 0.146) * k                 # lado de cada quadrado da grade
    x0, y0, w = round(L * 0.752) * k, round(A * 0.018) * k, max(2, round(A / 400)) * k
    im = Image.new("RGBA", (L * k, A * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = LINHA + (235,)
    P = lambda u, v: (x0 + u * s, y0 + v * s)
    for a, b in [((0, 0), (0, 2)), ((1, 0), (1, 2)), ((1, 0), (2, 0)), ((0, 1), (2, 1))]:
        d.line([P(*a), P(*b)], fill=c, width=w)
    def arco(cu, cv, ini, fim):              # arco de raio 1 célula com centro em (cu, cv)
        cx, cy = P(cu, cv)
        d.arc([cx - s, cy - s, cx + s, cy + s], ini, fim, fill=c, width=w)
    arco(0, 1, 270, 360)                     # alto à esquerda: de (0,0) até (1,1)
    arco(1, 0, 0, 90)                        # alto à direita: de (2,0) até (1,1)
    arco(0, 2, 270, 360)                     # baixo à esquerda: de (0,1) até (1,2)
    arco(1, 1, 0, 62)                        # baixo à direita: sai de (2,1) e termina antes da base
    return im.resize((L, A), Image.LANCZOS)


LARG_MAX, LINHAS_MAX = 0.86, 2                # o título ocupa até 86% da largura, em até 2 linhas


def _medidas(tam):
    fb, fd = fonte(tam, 500), fonte(tam, 620)
    track = tam * 0.035                       # a referência é mais aberta que a Inter Tight pura
    larg = lambda txt, f: sum(f.getlength(ch) for ch in txt) + track * max(0, len(txt) - 1)
    return fb, fd, track, larg


def _linhas(branco, destaque, tam, L):
    """palavras (com a cor de cada uma) quebradas em 1 ou 2 linhas equilibradas. None se não couber."""
    fb, fd, track, larg = _medidas(tam)
    pal = [(p, fb, (255, 255, 255, 255)) for p in branco.upper().split()] + \
          [(p, fd, LARANJA + (255,)) for p in destaque.upper().split()]
    esp = fb.getlength(" ") + track
    w = lambda ps: sum(larg(p, f) for p, f, _ in ps) + esp * max(0, len(ps) - 1)
    lim, nb = L * LARG_MAX, len(branco.split())
    if w(pal) <= lim:                                       # cabe numa linha
        return [pal], w, esp
    # 2 linhas: de preferência branco em cima e laranja embaixo; se não couber, só o branco se divide
    # (o destaque laranja fica sempre inteiro na 2ª linha, nunca começa no fim da 1ª)
    for i in [nb] + sorted(range(1, nb), key=lambda i: abs(w(pal[:i]) - w(pal[i:]))):
        if 0 < i < len(pal) and w(pal[:i]) <= lim and w(pal[i:]) <= lim:
            return [pal[:i], pal[i:]], w, esp
    return None


def tamanho_comum(L, A, titulos):
    """um tamanho só para todos os títulos do vídeo (itens equivalentes no mesmo tamanho)."""
    tam = round(A * 0.075)
    while tam > A * 0.045 and any(_linhas(b, d, tam, L) is None for b, d in titulos):
        tam -= 2
    return tam


def camada_titulo(L, A, branco, destaque, tam=None):
    """pergunta do capítulo centralizada em até 2 linhas: parte branca + final em laranja. Centro óptico pelas
    maiúsculas; espaço natural da fonte entre as palavras."""
    tam = tam or tamanho_comum(L, A, [(branco, destaque)])
    linhas, w, esp = _linhas(branco, destaque, tam, L) or _linhas(branco, destaque, round(A * 0.045), L)
    fb, fd, track, larg = _medidas(tam)
    _, topo, _, base = fb.getbbox("H", anchor="ls")
    cap = base - topo
    entre = tam * 1.22
    y = A * 0.515 - (cap + entre * (len(linhas) - 1)) / 2 + cap
    im = Image.new("RGBA", (L, A), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ls in linhas:
        x = (L - w(ls)) / 2
        for p, f, cor in ls:
            for ch in p:
                d.text((x, y), ch, font=f, fill=cor, anchor="ls")
                x += f.getlength(ch) + track
            x += esp - track
        y += entre
    return im


def info(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,color_transfer:format=duration", "-of", "json", video],
                         capture_output=True, text=True).stdout
    j = json.loads(out)
    st = j["streams"][0]
    n, dd = st["r_frame_rate"].split("/")
    return st, float(n) / float(dd), float(j["format"]["duration"])


def ler_capitulos(lista):
    caps = []
    for c in lista:
        partes = (c.split("|") + ["", ""])[:3]
        caps.append((float(partes[0]), partes[1], partes[2]))
    return sorted(caps)


def camadas(L, A, caps, pasta):
    fundo = os.path.join(pasta, "fundo.png"); camada_fundo(L, A).save(fundo)
    mono = os.path.join(pasta, "monograma.png"); camada_monograma(L, A).save(mono)
    titulos = []
    tam = tamanho_comum(L, A, [(b, d) for _, b, d in caps])
    for i, (_, b, d) in enumerate(caps):
        p = os.path.join(pasta, f"titulo_{i + 1:02d}.png")
        camada_titulo(L, A, b, d, tam).save(p)
        titulos.append(p)
    return fundo, mono, titulos


def quadros(video, caps, nome):
    """prévia de cada cartela sobre o quadro real do vídeo (no meio da cartela)."""
    st, _, _ = info(video)
    L, A = st["width"], st["height"]
    pasta = PLAT.pasta_cache("capitulos", nome)
    fundo, mono, titulos = camadas(L, A, caps, pasta)
    saidas = []
    for i, (t, _, _) in enumerate(caps):
        q = os.path.join(pasta, f"_quadro_{i + 1:02d}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t + DUR / 2:.2f}", "-i", video, "-frames:v", "1", q],
                       check=True)
        im = Image.open(q).convert("RGBA").resize((L, A))
        for c in ((fundo,) if not SEM_FUNDO else ()) + (mono, titulos[i]):
            im.alpha_composite(Image.open(c))
        p = os.path.join(pasta, f"previa_capitulo_{i + 1:02d}.png")
        im.convert("RGB").save(p)
        os.remove(q)
        saidas.append(p)
    return saidas


def renderizar(video, caps, saida, so_ate=None):
    st, fps, dur = info(video)
    L, A = st["width"], st["height"]
    nome = os.path.splitext(os.path.basename(saida))[0]
    fundo, mono, titulos = camadas(L, A, caps, PLAT.pasta_cache("capitulos", nome))
    ent = ["-i", video]
    filtro, ult = [], "0:v"
    hdr = st.get("color_transfer") in ("arib-std-b67", "smpte2084")
    if hdr:
        args, f = PLAT.entrada_hdr(st)
        ent = args + ent
        filtro.append(f"[0:v]{f.rstrip(',')}[base]")
        ult = "base"
    n = 1
    for i, (t, _, _) in enumerate(caps):
        for papel, png in ((("f", fundo),) if not SEM_FUNDO else ()) + (("m", mono), ("t", titulos[i])):
            ent += ["-loop", "1", "-framerate", f"{fps:.3f}", "-t", f"{DUR:.2f}", "-i", png]
            atraso = {"f": 0.0, "m": 0.15, "t": 0.25}[papel]
            filtro.append(f"[{n}:v]format=rgba,fade=t=in:st={atraso}:d={ENTRA}:alpha=1,"
                          f"fade=t=out:st={DUR - SAI:.2f}:d={SAI}:alpha=1,setpts=PTS-STARTPTS+{t:.3f}/TB[{papel}{i}]")
            # o título sobe de leve ao entrar
            y = (f"'{round(A * 0.025)}*pow(max(0,1-(t-{t + atraso:.3f})/0.7),3)'" if papel == "t" else "0")
            filtro.append(f"[{ult}][{papel}{i}]overlay=0:{y}:eof_action=pass:eval=frame[v{n}]")
            ult = f"v{n}"
            n += 1
    filtro.append(f"[{ult}]format=yuv420p[vout]")
    cmd = ["ffmpeg", "-v", "error", "-stats", "-y", *ent, "-filter_complex", ";".join(filtro),
           "-map", "[vout]", "-map", "0:a?", "-c:a", "copy", *PLAT.h264("16M"), "-movflags", "+faststart"]
    if so_ate:
        cmd += ["-t", str(so_ate)]
    subprocess.run(cmd + [saida], check=True)
    return saida


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--capitulo", action="append", required=True, help='"segundo|parte branca|destaque"')
    ap.add_argument("--nome", help="nome do arquivo final (sem extensão)")
    ap.add_argument("--saida", help="pasta (padrão: Mesa/Editor Reels)")
    ap.add_argument("--quadros", action="store_true", help="só gera as prévias para validar")
    ap.add_argument("--ate", type=float, help="renderiza só até esse segundo (teste)")
    ap.add_argument("--duracao", type=float, default=DUR, help="tempo da cartela na tela (s)")
    ap.add_argument("--sem-fundo", action="store_true", help="não escurece: o vídeo já tem a cartela de fundo sólido")
    a = ap.parse_args()
    globals()["DUR"] = a.duracao
    globals()["SEM_FUNDO"] = a.sem_fundo
    caps = ler_capitulos(a.capitulo)
    nome = a.nome or os.path.splitext(os.path.basename(a.video))[0] + "_capitulos"
    if a.quadros:
        for p in quadros(a.video, caps, nome):
            print(p)
        return
    pasta = PLAT.caminho(a.saida) if a.saida else PLAT.pasta_renders()
    os.makedirs(pasta, exist_ok=True)
    print(renderizar(a.video, caps, os.path.join(pasta, nome + ".mp4"), a.ate))


if __name__ == "__main__":
    main()
