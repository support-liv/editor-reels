#!/usr/bin/env python3
"""Formato "ads dinâmico" (vertical 1080x1920): texto ATRÁS da pessoa, B-roll por API, film burns nas emendas,
punch-ins de enquadramento, legenda de 1-3 palavras com destaque e CTA no fim. Versão opcional com a tela
dividida no gancho (B-roll em cima, pessoa embaixo, pergunta na divisória).

    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py [--versao A|B] [--quadros 1.5,12.8,...]

O roteiro (um .py com ROTEIRO = {...}) descreve tempos e textos; a fala vem do Whisper (palavras com tempo).
Tudo roda no Mac: recorte da pessoa pelo Vision (editor/recorte_pessoa.swift), B-roll baixado pelo
servidor do time (editor/broll_api.py). Marca LIV: sem sombra/contorno, cores e fonte do manual.
"""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
W, H, FPS = 1080, 1920, 30
CACHE = os.path.expanduser("~/Library/Caches/editor-reels/ads")
COR = {"azul": (44, 54, 66), "laranja": (255, 110, 31), "bege": (255, 240, 230), "branco": (255, 255, 255),
       "marrom": (148, 89, 67)}
FONTE = os.path.join(RAIZ, "assets", "fontes", "DarkerGrotesque[wght].ttf")
SFX = os.path.join(RAIZ, "motion", "sfx", "whoosh.wav")
_fontes = {}


def fonte(tam, peso=800):
    k = (tam, peso)
    if k not in _fontes:
        f = ImageFont.truetype(FONTE, tam)
        try:
            f.set_variation_by_axes([peso])
        except Exception:
            pass
        _fontes[k] = f
    return _fontes[k]


def run(cmd, **k):
    return subprocess.run(cmd, check=True, capture_output=True, **k)


# ------------------------------------------------------------------ vídeo de entrada
def ler_quadros(video, ss=0.0, dur=None, fps=FPS, cobrir=True):
    """quadros RGB 1080x1920 (cobrindo a tela, sem distorcer: escala pelo lado que falta e corta o excesso)."""
    vf = f"fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}" if cobrir else f"fps={fps}"
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{ss:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) + \
          ["-i", video, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


class Fluxo:
    """lê quadros um a um (cobrindo 1080x1920); abre o ffmpeg só quando precisa."""

    def __init__(self, video, ss=0.0, dur=None, lado=(W, H)):
        self.args, self.lado, self.p, self.ult, self.k = (video, ss, dur), lado, None, None, -1

    def quadro(self, k):
        if self.p is None:
            video, ss, dur = self.args
            w, h = self.lado
            vf = f"fps={FPS},scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,crop={w}:{h}"
            self.p = subprocess.Popen(["ffmpeg", "-v", "fatal", "-ss", f"{ss:.3f}"] + (["-t", f"{dur:.3f}"] if dur else []) +
                                      ["-i", video, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        w, h = self.lado
        while self.k < k:
            b = self.p.stdout.read(w * h * 3)
            if len(b) < w * h * 3:
                break
            self.ult = np.frombuffer(b, np.uint8).reshape(h, w, 3); self.k += 1
        return self.ult


def contar_quadros(video):
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                             capture_output=True, text=True).stdout)
    return int(d * FPS)


def mascaras(video, n):
    """máscara da pessoa (0-1) em cada quadro, pelo Vision; cache por vídeo."""
    chave = hashlib.md5(f"{os.path.abspath(video)}{os.path.getsize(video)}{n}".encode()).hexdigest()[:12]
    npz = os.path.join(CACHE, f"mask_{chave}.npy")
    if os.path.exists(npz):
        return np.load(npz, mmap_mode="r")
    os.makedirs(CACHE, exist_ok=True)
    binario = os.path.join(CACHE, "recorte_pessoa")
    if not os.path.exists(binario):
        run(["swiftc", "-O", "-o", binario, os.path.join(AQUI, "recorte_pessoa.swift")])
    with tempfile.TemporaryDirectory() as tmp:
        ent, sai = os.path.join(tmp, "q"), os.path.join(tmp, "m")
        os.makedirs(ent)
        fl = Fluxo(video, lado=(W // 2, H // 2))          # meia resolução basta pra máscara (e é 4x mais rápido)
        for i in range(n):
            Image.fromarray(fl.quadro(i)).save(os.path.join(ent, f"{i:05d}.png"), compress_level=1)
        run([binario, ent, sai])
        ms = np.zeros((n, H // 2, W // 2), np.uint8)
        for i in range(n):
            ms[i] = np.array(Image.open(os.path.join(sai, f"{i:05d}.png")).convert("L"))
    np.save(npz, ms)
    return ms


def mascara_cheia(ms, i, ant=None):
    m = cv2.resize(ms[i], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    m = cv2.GaussianBlur(m, (0, 0), 1.2)
    return m if ant is None else 0.65 * m + 0.35 * ant      # suaviza no tempo (sem "tremer" a borda)


# ------------------------------------------------------------------ enquadramento (punch-in)
def ancora(ms, i):
    """centro do rosto aproximado: meio da pessoa na horizontal, um pouco abaixo do topo da cabeça."""
    m = ms[i] > 128
    ys, xs = np.where(m)
    if not len(xs):
        return W / 2, H * 0.3
    top = ys.min() * 2
    return float(np.median(xs) * 2), float(top + 0.11 * H)


def aplicar_zoom(img, s, ax, ay):
    if s <= 1.001:
        return img
    cw, ch = W / s, H / s
    x0 = min(max(ax - cw / 2, 0), W - cw)
    y0 = min(max(ay - ch * 0.32, 0), H - ch)                 # rosto no terço de cima
    M = np.float32([[s, 0, -x0 * s], [0, s, -y0 * s]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


# ------------------------------------------------------------------ texto
def render_span(texto, tam, cor, peso=800):
    f = fonte(tam, peso)
    x0, y0, x1, y1 = f.getbbox(texto)
    pad = int(tam * 0.25)
    im = Image.new("RGBA", (x1 - x0 + 2 * pad, int(tam * 1.25) + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad), texto, font=f, fill=COR.get(cor, cor) + (255,))
    return im


def entra(im, p, desfoque=16, escala=0.14):
    """entrada com desfoque + escala (p de 0 a 1)."""
    p = max(0.0, min(1.0, p))
    e = 1 - (1 - p) ** 3
    if e >= 0.999:
        return im
    s = 1 + escala * (1 - e)
    w, h = im.size
    im2 = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR)
    if desfoque * (1 - e) > 0.5:
        im2 = im2.filter(ImageFilter.GaussianBlur(desfoque * (1 - e)))
    a = np.array(im2)
    a[..., 3] = (a[..., 3] * e).astype(np.uint8)
    return Image.fromarray(a)


def colar(base, im, cx, cy):
    """cola RGBA centrado em (cx, cy) num array RGB float."""
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    sub = a[ya - y0:yb - y0, xa - x0:xb - x0]
    al = sub[..., 3:4]
    base[ya:yb, xa:xb] = base[ya:yb, xa:xb] * (1 - al) + sub[..., :3] * 255.0 * al


class Linhas:
    """bloco de linhas; cada linha é uma lista de spans (texto, tam, cor, t) que entram no tempo da fala."""

    def __init__(self, bloco):
        self.b = bloco
        self.cache = {}

    def desenhar(self, base, t):
        b = self.b
        if not (b["t0"] <= t < b["t1"]):
            return
        saida = max(0.0, min(1.0, (t - (b["t1"] - 0.22)) / 0.22))     # sai junto do corte (o film burn cobre)
        for li, linha in enumerate(b["linhas"]):
            imgs = []
            for si, sp in enumerate(linha["spans"]):
                k = (li, si)
                if k not in self.cache:
                    if linha.get("caixa"):              # texto em pílula (como a legenda): legível em qualquer fundo
                        self.cache[k] = render_legenda(sp["texto"], linha["caixa"] == "laranja", tam=sp.get("tam", linha.get("tam", 100)))
                    else:
                        self.cache[k] = render_span(sp["texto"], sp.get("tam", linha.get("tam", 100)), sp.get("cor", linha.get("cor", "branco")))
                imgs.append((self.cache[k], sp["t"]))
            esp = int(linha.get("tam", 100) * 0.12)
            larg = sum(im.size[0] for im, _ in imgs) - esp * (len(imgs) - 1)
            x = W / 2 - larg / 2 if linha.get("alinha", "centro") == "centro" else linha.get("x", 80)
            for im, t_ in imgs:
                p = (t - t_) / 0.32
                if p > 0:
                    v = entra(im, p)
                    if saida > 0:
                        v = entra(v, 1 - saida, desfoque=10, escala=-0.08)
                    colar(base, v, x + im.size[0] / 2, linha["y"])
                x += im.size[0] - esp


# ------------------------------------------------------------------ legenda 1-3 palavras
def blocos_legenda(palavras, trocas, destaques):
    ws = []
    for p in palavras:
        w = p["w"]
        for a, b in trocas.items():
            w = w.replace(a, b)
        ws.append(dict(p, w=w))
    out, cur = [], []
    for i, p in enumerate(ws):
        cur.append(p)
        fim = (i == len(ws) - 1 or re.search(r"[.,?!]$", p["w"]) or len(cur) >= 3 or
               ws[i + 1]["s"] - p["e"] > 0.25 or p["e"] - cur[0]["s"] > 0.95)
        if fim:
            out.append(cur); cur = []
    blocos = []
    for i, c in enumerate(out):
        t1 = out[i + 1][0]["s"] if i + 1 < len(out) else c[-1]["e"] + 0.6
        texto = " ".join(re.sub(r"[.,!]$", "", p["w"]) for p in c)
        dest = any(re.sub(r"\W", "", p["w"]).lower() in destaques for p in c)
        blocos.append({"t0": c[0]["s"], "t1": min(t1, c[-1]["e"] + 0.6), "texto": texto, "dest": dest})
    return blocos


def render_legenda(texto, dest, tam=88):
    f = fonte(tam, 800)
    x0, y0, x1, y1 = f.getbbox(texto)
    px, py = int(tam * 0.38), int(tam * 0.16)
    w, h = x1 - x0 + 2 * px, int(tam * 1.02) + 2 * py
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(h * 0.28), fill=COR["laranja" if dest else "azul"] + (255,))
    d.text((px - x0, py - int(tam * 0.06)), texto, font=f, fill=COR["branco"] + (255,))
    return im


# ------------------------------------------------------------------ film burn
def carregar_burns(arquivos):
    out = []
    for arq in arquivos:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", f"fps={FPS},scale={W // 2}:{H // 2}:force_original_aspect_ratio=increase,crop={W // 2}:{H // 2}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        q = np.frombuffer(raw, np.uint8).reshape(-1, H // 2, W // 2, 3)   # luz desfocada: meia resolução não perde nada
        out.append({"q": q, "pico": int(q.reshape(len(q), -1).mean(1).argmax())})
    return out


def tela(a, b, k=1.0):
    """mistura 'tela' (screen): a luz clareia, o preto não muda nada."""
    return 255.0 - (255.0 - a) * (255.0 - b * k) / 255.0


# ------------------------------------------------------------------ CTA
def render_cta(c, p_seta):
    w, h = 940, 330
    im = Image.new("RGBA", (w, h + 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=46, fill=COR["bege"] + (255,))
    f1, f2 = fonte(c.get("tam1", 112), 800), fonte(c.get("tam2", 70), 700)
    for txt, f, y, cor in ((c["linha1"], f1, 62, "laranja"), (c["linha2"], f2, 196, "azul")):
        x0, _, x1, _ = f.getbbox(txt)
        d.text(((w - (x1 - x0)) / 2 - x0, y), txt, font=f, fill=COR[cor] + (255,))
    if p_seta > 0:                                         # seta pro botão do anúncio, pulsando
        a = int(255 * min(1, p_seta * 3))
        dy = int(10 * np.sin(p_seta * 9))
        cx, cy = w / 2, h + 70 + dy
        d.polygon([(cx - 46, cy - 26), (cx + 46, cy - 26), (cx, cy + 30)], fill=COR["laranja"] + (a,))
    return im


# ------------------------------------------------------------------ montagem
def montar(rot, versao, saida, quadros_png=None):
    base_v = os.path.expanduser(rot["video"])
    palavras = json.load(open(os.path.expanduser(rot["palavras"])))
    n = contar_quadros(base_v)
    dur = n / FPS
    print(f"  {n} quadros ({dur:.1f}s) | recorte da pessoa (Vision)…", flush=True)
    ms = mascaras(base_v, n)
    base = Fluxo(base_v)
    # enquadramento por trecho (com um leve avanço de câmera dentro de cada trecho)
    zooms = []
    for z in rot["zoom"]:
        i0 = min(int(z["t0"] * FPS), n - 1)
        zooms.append(dict(z, anc=ancora(ms, i0)))
    brolls = []
    for b in rot["broll"]:
        brolls.append(dict(b, f=Fluxo(os.path.expanduser(b["arq"]), ss=b.get("ss", 0), dur=b["t1"] - b["t0"] + 0.3)))
    dividido = None
    if versao == "B" and rot.get("dividido"):
        dv = rot["dividido"]
        dividido = dict(dv, f=Fluxo(os.path.expanduser(dv["arq"]), ss=dv.get("ss", 0), dur=dv["t1"] - dv["t0"] + 0.3))
    burns = carregar_burns(rot["burns_arquivos"])
    cortes = rot["burns"] if versao == "A" else rot.get("burns_B", rot["burns"])
    atras = [Linhas(b) for b in rot["atras"] if versao == "A" or not b.get("so_A")]
    frente = [Linhas(b) for b in rot.get("frente", []) if versao == "A" or not b.get("so_A")]
    faixa = Linhas(dividido["faixa"]) if dividido else None
    legs = blocos_legenda(palavras, rot.get("trocas", {}), set(rot.get("destaques", [])))
    sem_leg = [(b.b["t0"], b.b["t1"]) for b in atras + frente if not b.b.get("legenda")] + [(rot["cta"]["t0"], dur + 1)]
    if dividido:
        sem_leg.append((dividido["t0"], dividido["t1"]))
    cache_leg = {}
    cta = rot["cta"]

    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "h264_videotoolbox", "-b:v", "16M", "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", tmp_v],
                           stdin=subprocess.PIPE)
    alvo_png = sorted(quadros_png or [])
    m_ant = None
    for i in range(n):
        t = i / FPS
        z = next((z for z in zooms if z["t0"] <= t < z["t1"]), None)
        s = 1.0
        if z:
            s = z["s"] * (1 + z.get("avanco", 0.025) * (t - z["t0"]) / max(0.1, z["t1"] - z["t0"]))
        ax, ay = z["anc"] if z else (W / 2, H * 0.3)
        bruto = base.quadro(i)
        q = aplicar_zoom(bruto, s, ax, ay).astype(np.float32)
        precisa_m = any(b.b["t0"] <= t < b.b["t1"] for b in atras)
        if precisa_m:
            m = mascara_cheia(ms, i, m_ant)
            m = aplicar_zoom((m * 255).astype(np.uint8)[..., None].repeat(3, 2), s, ax, ay)[..., 0].astype(np.float32) / 255.0 \
                if s > 1.001 else m
            m_ant = m
            camada = q.copy()
            for b in atras:
                b.desenhar(camada, t)
            q = camada * (1 - m[..., None]) + q * m[..., None]     # texto entre o fundo e a pessoa
        else:
            m_ant = None
        for b in frente:
            b.desenhar(q, t)
        br = next((b for b in brolls if b["t0"] <= t < b["t1"]), None)
        if br:
            q = br["f"].quadro(int((t - br["t0"]) * FPS)).astype(np.float32)
        if dividido and dividido["t0"] <= t < dividido["t1"]:
            topo = dividido["f"].quadro(int((t - dividido["t0"]) * FPS))[dividido["y_topo"]:dividido["y_topo"] + H // 2]
            pessoa = bruto[dividido["y_pessoa"]:dividido["y_pessoa"] + H // 2]
            q = np.vstack([topo, pessoa]).astype(np.float32)
            d = dividido["faixa"]
            if t >= d["t0"]:
                p = min(1.0, (t - d["t0"]) / 0.3)
                hh = int(d["altura"] * (1 - (1 - p) ** 3))
                if hh > 0:
                    q[H // 2 - hh // 2:H // 2 + hh // 2] = np.array(COR[d.get("cor", "bege")], np.float32)
            faixa.desenhar(q, t)
        # legenda
        if not any(a <= t < b for a, b in sem_leg):
            lg = next((l for l in legs if l["t0"] <= t < l["t1"]), None)
            if lg:
                k = lg["texto"]
                if k not in cache_leg:
                    cache_leg[k] = render_legenda(lg["texto"], lg["dest"])
                colar(q, entra(cache_leg[k], (t - lg["t0"]) / 0.12, desfoque=0, escala=0.10), W / 2, rot.get("y_legenda", 1330))
        # CTA
        if t >= cta["t0"]:
            p = (t - cta["t0"]) / 0.35
            im = render_cta(cta, max(0.0, t - cta["t_seta"]) if t >= cta["t_seta"] else 0)
            e = 1 - (1 - min(1, p)) ** 3
            colar(q, entra(im, p, desfoque=0, escala=0.06), W / 2, cta["y"] + (1 - e) * 80)
        # film burn: o pico de luz cai exatamente no corte
        for ci, c in enumerate(cortes):
            bn = burns[ci % len(burns)]
            k = i - (int(round(c * FPS)) - bn["pico"])
            if 0 <= k < len(bn["q"]):
                luz = cv2.resize(bn["q"][k], (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
                q = tela(q, luz, rot.get("burn_forca", 0.92))
        out = np.clip(q, 0, 255).astype(np.uint8)
        enc.stdin.write(out.tobytes())
        for tp in alvo_png:
            if abs(t - tp) < 0.5 / FPS:
                Image.fromarray(out).save(os.path.splitext(saida)[0] + f"_{tp:05.2f}s.png")
        if i % 150 == 0:
            print(f"  {t:5.1f}s / {dur:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    # áudio: a fala + whoosh baixinho em cada film burn
    ent = ["-i", tmp_v, "-i", base_v]
    filt, mix = [], ["[1:a]volume=1.0[voz]"]
    for k, c in enumerate(cortes):
        ent += ["-i", SFX]
        filt.append(f"[{k + 2}:a]volume=0.22,adelay={int(max(0, c - 0.35) * 1000)}:all=1[w{k}]")
    rotulos = "[voz]" + "".join(f"[w{k}]" for k in range(len(cortes)))
    fc = ";".join(mix + filt + [f"{rotulos}amix=inputs={len(cortes) + 1}:normalize=0:duration=first[a]"])
    run(["ffmpeg", "-v", "error", "-y"] + ent + ["-filter_complex", fc, "-map", "0:v", "-map", "[a]",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida])
    os.remove(tmp_v)
    return saida


def carregar_roteiro(caminho):
    spec = importlib.util.spec_from_file_location("roteiro", caminho)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.ROTEIRO


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro"); ap.add_argument("--versao", default="A", choices=["A", "B"])
    ap.add_argument("--quadros", default="", help="segundos pra salvar PNG de conferência (ex.: 1.5,12.8)")
    a = ap.parse_args()
    rot = carregar_roteiro(a.roteiro)
    os.makedirs(os.path.expanduser(rot["saida"]), exist_ok=True)
    nome = rot["nome"] + ("_A_texto_atras" if a.versao == "A" else "_B_tela_dividida") + ".mp4"
    saida = os.path.join(os.path.expanduser(rot["saida"]), nome)
    qs = [float(x) for x in a.quadros.split(",") if x.strip()]
    print("pronto:", montar(rot, a.versao, saida, qs))
