#!/usr/bin/env python3
"""Formato "ads dinâmico" (vertical 1080x1920): texto ATRÁS da pessoa, B-roll por API, film burns nas emendas,
punch-ins de enquadramento, legenda de 1-3 palavras com destaque e CTA no fim. Versão opcional com a tela
dividida no gancho (B-roll em cima, pessoa embaixo, pergunta na divisória).

    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py [--versao A|B] [--quadros 1.5,12.8,...]

O roteiro (um .py com ROTEIRO = {...}) descreve tempos e textos; a fala vem do Whisper (palavras com tempo).
Roda no computador (Mac ou Windows): recorte da pessoa pelo Vision no Mac / MediaPipe no Windows, B-roll baixado pelo
servidor do time (editor/broll_api.py). Marca LIV: sem sombra/contorno, cores e fonte do manual.
"""
import argparse, hashlib, importlib.util, json, os, re, subprocess, sys, tempfile
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plataforma as PLAT

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
W, H, FPS = 1080, 1920, 30
CACHE = PLAT.pasta_cache("ads")
COR = {"azul": (44, 54, 66), "laranja": (255, 110, 31), "bege": (255, 240, 230), "branco": (255, 255, 255),
       "marrom": (148, 89, 67)}
FONTE = os.path.join(RAIZ, "assets", "fontes", "DarkerGrotesque[wght].ttf")
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
    with tempfile.TemporaryDirectory() as tmp:
        ent, sai = os.path.join(tmp, "q"), os.path.join(tmp, "m")
        os.makedirs(ent)
        fl = Fluxo(video, lado=(W // 2, H // 2))          # meia resolução basta pra máscara (e é 4x mais rápido)
        for i in range(n):
            Image.fromarray(fl.quadro(i)).save(os.path.join(ent, f"{i:05d}.png"), compress_level=1)
        PLAT.mascaras_pessoa(ent, sai)                  # Mac: Vision; Windows: MediaPipe
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
def render_span(texto, tam, cor, peso=800, track=-0.02, protecao=0.0):
    """texto de display: tracking apertado (em fração do corpo), sem contorno.
    protecao > 0: esfumaçado escuro bem suave atrás das letras (só para dar contraste sobre imagem clara)."""
    f = fonte(tam, peso)
    tr = tam * track
    xs = [f.getlength(texto[:i]) + tr * i for i in range(len(texto))]
    larg = int((f.getlength(texto) + tr * (len(texto) - 1)) if texto else 1)
    asc, desc = f.getmetrics()
    pad = _pad(tam, protecao)
    im = Image.new("RGBA", (larg + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for ch, x in zip(texto, xs):
        d.text((pad + x, pad), ch, font=f, fill=COR.get(cor, cor) + (255,))
    if protecao > 0:
        a_ = np.array(im)[..., 3].astype(np.float32)
        r = max(1, int(tam * 0.05))
        halo = cv2.dilate(a_, np.ones((2 * r + 1, 2 * r + 1), np.uint8))
        halo = cv2.GaussianBlur(halo, (0, 0), tam * 0.16)
        sombra = np.zeros((im.height, im.width, 4), np.uint8)
        sombra[..., 3] = np.clip(halo * protecao, 0, 255).astype(np.uint8)
        im = Image.alpha_composite(Image.fromarray(sombra), im)
    bb = im.getbbox() or (0, 0, im.width, im.height)
    out = im.crop((bb[0], 0, bb[2], im.height))
    out.info["tinta"] = (max(0, int(pad - bb[0])), int(pad - bb[0] + larg))
    return out


def _pad(tam, protecao=0.0):
    return int(tam * (0.45 if protecao > 0 else 0.12))


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


def altura_optica(linha):
    """2x a distância da linha de base ao centro de massa (peso visual) das letras, sem acentos.
    Centralizar por aí deixa a linha visualmente no meio, mesmo com acento ou maiúscula alta."""
    import unicodedata
    soma = peso_tot = 0.0
    for sp in linha["spans"]:
        tam, peso = sp.get("tam", linha.get("tam", 100)), sp.get("peso", linha.get("peso", 800))
        sem = "".join(c for c in unicodedata.normalize("NFD", sp["texto"]) if unicodedata.category(c) != "Mn")
        im = render_span(sem, tam, "branco", peso, sp.get("track", linha.get("track", -0.02)))
        al = np.array(im)[..., 3].astype(np.float64)
        base = _pad(tam) + fonte(tam, peso).getmetrics()[0]          # linha de base dentro da imagem
        ys = np.arange(al.shape[0])[:, None]
        soma += float(((base - ys) * al).sum()); peso_tot += float(al.sum())
    return 2 * soma / peso_tot if peso_tot else 0.0


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
                        self.cache[k] = render_span(sp["texto"], sp.get("tam", linha.get("tam", 100)), sp.get("cor", linha.get("cor", "branco")),
                                                    sp.get("peso", linha.get("peso", 800)), sp.get("track", linha.get("track", -0.02)),
                                                    linha.get("protecao", 0.0))
                imgs.append((self.cache[k], sp["t"]))
            # espaço entre palavras = o espaço natural da fonte (como texto digitado), medido entre as LETRAS,
            # nunca pela imagem (que pode ter halo/margem); "espaco" no roteiro só ajusta esse espaço natural
            tam_e = max(sp.get("tam", linha.get("tam", 100)) for sp in linha["spans"])
            esp = int(fonte(tam_e, linha.get("peso", 800)).getlength(" ") * linha.get("espaco_fator", 1.0))
            tintas = [im.info.get("tinta", (0, im.size[0])) for im, _ in imgs]
            larg = sum(t1 - t0 for t0, t1 in tintas) + esp * (len(imgs) - 1)
            x = W / 2 - larg / 2 if linha.get("alinha", "centro") == "centro" else linha.get("x", 80)
            # y da linha = centro óptico: do topo das letras (sem contar acento) até a linha de base comum
            base_y = linha["y"] + altura_optica(linha) / 2
            for (im, t_), sp in zip(imgs, linha["spans"]):
                p = (t - t_) / 0.32
                if p > 0:
                    v = entra(im, p)
                    if saida > 0:
                        v = entra(v, 1 - saida, desfoque=10, escala=-0.08)
                    if linha.get("caixa"):
                        cy = linha["y"]
                    else:
                        tam_s, peso_s = sp.get("tam", linha.get("tam", 100)), sp.get("peso", linha.get("peso", 800))
                        topo = base_y - (_pad(tam_s, linha.get("protecao", 0)) + fonte(tam_s, peso_s).getmetrics()[0])
                        cy = topo + im.size[1] / 2
                    t0_, t1_ = im.info.get("tinta", (0, im.size[0]))
                    colar(base, v, x - t0_ + im.size[0] / 2, cy)          # a letra começa exatamente em x
                t0_, t1_ = im.info.get("tinta", (0, im.size[0]))
                x += (t1_ - t0_) + esp


class Lettering:
    """lettering grande alinhado à esquerda (nos inserts de imagem): cada linha sobe de dentro de uma máscara.
    Ênfase pelo peso (Black x Light da mesma família), entrelinha justa, uma barra laranja curta como único acento."""

    def __init__(self, bloco):
        self.b, self.cache = bloco, {}

    def ativo(self, t):
        return self.b["t0"] <= t < self.b["t1"]

    def desenhar(self, base, t):
        b = self.b
        if not self.ativo(t):
            return
        for li, ln in enumerate(b["linhas"]):
            if li not in self.cache:
                self.cache[li] = render_span(ln["texto"], ln["tam"], ln.get("cor", "bege"), ln.get("peso", 900), ln.get("track", -0.03))
        x = b.get("x", SEGURA["x0"])
        if "y" in b:
            y = b["y"]
        else:                                               # pé do bloco na base comum (área segura, acima da legenda do app)
            total = sum(int(ln["tam"] * b.get("entrelinha", 0.98)) for ln in b["linhas"][:-1]) + self.cache[len(b["linhas"]) - 1].height
            y = b.get("pe", SEGURA["y1"] - 60) - total
        if b.get("barra", True):
            p = max(0.0, min(1.0, (t - b["linhas"][0]["t"] + 0.1) / 0.35))
            e = 1 - (1 - p) ** 4
            if e > 0:
                base[int(y - 34):int(y - 24), int(x):int(x + 96 * e)] = np.array(COR["laranja"], np.float32)
        for li, ln in enumerate(b["linhas"]):
            if li not in self.cache:
                self.cache[li] = render_span(ln["texto"], ln["tam"], ln.get("cor", "bege"), ln.get("peso", 900), ln.get("track", -0.03))
            im = self.cache[li]
            h_linha = int(ln["tam"] * b.get("entrelinha", 0.98))
            p = (t - ln["t"]) / 0.42
            if p > 0:
                e = 1 - (1 - min(1.0, p)) ** 4                         # sai rápido e assenta devagar
                dy = int((1 - e) * im.height * 0.9)
                a = np.asarray(im).astype(np.float32) / 255.0
                hh = min(im.height - dy, H - int(y))
                if hh > 0:
                    sub = a[:hh]
                    y0 = int(y) + dy
                    y1 = min(y0 + sub.shape[0], int(y) + im.height, H)  # recorte da máscara: a linha "nasce" da base
                    sub = sub[:max(0, y1 - y0)]
                    w_ = min(sub.shape[1], W - int(x))
                    if sub.shape[0] > 0 and w_ > 0:
                        al = sub[:, :w_, 3:4]
                        reg = base[y0:y0 + sub.shape[0], int(x):int(x) + w_]
                        base[y0:y0 + sub.shape[0], int(x):int(x) + w_] = reg * (1 - al) + sub[:, :w_, :3] * 255.0 * al
            y += h_linha


def escurecer_base(q, forca=0.55):
    """véu suave na metade de baixo da imagem (não é sombra no texto): dá contraste ao lettering claro."""
    g = np.clip((np.arange(H, dtype=np.float32) - H * 0.40) / (H * 0.45), 0, 1)
    g = g * g * (3 - 2 * g)
    return q * (1 - forca * g)[:, None, None]


def oculto(bloco, ms, n):
    """fração do texto (já todo na tela) que a pessoa cobre, no pior trecho do bloco (média por quadro, pega o p90)."""
    camada = np.zeros((H, W, 3), np.float32)
    Linhas(dict(bloco, linhas=[dict(l, spans=[dict(s_, t=-10) for s_ in l["spans"]]) for l in bloco["linhas"]])).desenhar(camada, bloco["t0"])
    alfa = (camada.max(axis=2) > 8).astype(np.float32)
    tot = alfa.sum()
    if tot == 0:
        return 0.0
    fr = []
    for i in range(int(bloco["t0"] * FPS), min(n, int(bloco["t1"] * FPS)), 3):
        m = cv2.resize(ms[i], (W, H)).astype(np.float32) / 255.0
        fr.append(float((alfa * m).sum() / tot))
    return float(np.percentile(fr, 90)) if fr else 0.0


def ajustar_legibilidade(rot, atras, frente, ms, n, limite=0.18):
    """texto atrás que não dá pra ler: (1) se tem mais de uma palavra numa linha, quebra em linhas;
    (2) se ainda não dá, vai pra FRENTE, acima da legenda (mesmo tamanho de leitura). Mostra a medição."""
    novos_atras = []
    for b in atras:
        oc = oculto(b.b, ms, n)
        print(f"  texto atrás ({b.b['t0']:.1f}s): {oc:.0%} coberto pela pessoa", flush=True)
        if oc <= limite or b.b.get("forcar_atras"):
            novos_atras.append(b); continue
        modo = b.b.get("se_ilegivel", "auto")
        linhas = b.b["linhas"]
        if modo in ("auto", "quebrar") and any(len(l["spans"]) > 1 for l in linhas):
            quebradas, y = [], linhas[0]["y"]
            for l in linhas:
                for s_ in l["spans"]:
                    quebradas.append(dict(l, y=y, spans=[s_])); y += int(l.get("tam", 100) * 0.82)
            nb = dict(b.b, linhas=quebradas)
            oc2 = oculto(nb, ms, n)
            print(f"    quebrando em linhas: {oc2:.0%} coberto", flush=True)
            if oc2 <= limite:
                novos_atras.append(Linhas(nb)); continue
        # na frente, acima da legenda: uma linha, tamanho que caiba na área segura
        tam = min(max(l.get("tam", 100) for l in linhas), rot.get("tam_frente", 190))
        y_leg = rot.get("y_legenda", int(H * 0.62))
        # pé da palavra ~40 px acima da caixa da legenda (respiro), nunca encostado
        nb = dict(b.b, linhas=[dict(linhas[0], protecao=rot.get("protecao_frente", 0.55), y=y_leg - 88 - int(tam * 0.42),
                                    spans=[s_ for l in linhas for s_ in l["spans"]], tam=tam)])
        print(f"    → na frente, acima da legenda", flush=True)
        frente.append(Linhas(nb))
    return novos_atras


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
def carregar_burns(arquivos, vel=1.0):
    """film burns acelerados (vel > 1 = flash mais curto); o pico de luz continua caindo no corte."""
    out = []
    for arq in arquivos:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", f"setpts=PTS/{vel},fps={FPS},scale={W // 2}:{H // 2}:force_original_aspect_ratio=increase,crop={W // 2}:{H // 2}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        q = np.frombuffer(raw, np.uint8).reshape(-1, H // 2, W // 2, 3)   # luz desfocada: meia resolução não perde nada
        out.append({"q": q, "pico": int(q.reshape(len(q), -1).mean(1).argmax()), "dur": len(q) / FPS})
    return out


def max_volume(arq):
    """pico do áudio do arquivo em dB (None se não tem áudio)."""
    r = subprocess.run(["ffmpeg", "-i", arq, "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"max_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else None


def tela(a, b, k=1.0):
    """mistura 'tela' (screen): a luz clareia, o preto não muda nada."""
    return 255.0 - (255.0 - a) * (255.0 - b * k) / 255.0


# ------------------------------------------------------------------ CTA
# área segura do anúncio: sobrevive ao corte 4:5 (y 285-1635) e 3:4 do feed e fica acima da interface do Reels
SEGURA = {"x0": 72, "x1": W - 72, "y0": 300, "y1": 1400}


def _tinta(im):
    """caixa da tinta (pixels visíveis) de uma imagem RGBA: o espaçamento é medido pelo desenho, não pela caixa."""
    return im.getbbox() or (0, 0, im.width, im.height)


def render_cta(c, p_seta):
    """card da marca: respiro igual em cima, embaixo e dos lados; ritmo vertical pelo desenho das letras;
    Light + Black da mesma família; seta laranja centrada na linha principal."""
    P = c.get("respiro", 64)                                 # respiro interno (igual nos 4 lados)
    l1 = render_span(c["linha1"], c.get("tam1", 64), "bege", 400, -0.005)
    larg = SEGURA["x1"] - SEGURA["x0"]
    tam2 = c.get("tam2", 124)
    while True:                                              # linha principal + vão (= respiro) + seta cabem no card
        l2 = render_span(c["linha2"], tam2, "bege", 900, -0.03)
        if P + (_tinta(l2)[2] - _tinta(l2)[0]) + P + 80 + P <= larg or tam2 <= 80:
            break
        tam2 -= 4
    l3 = render_span(c["linha3"], c.get("tam3", 50), "laranja", 600, 0.005)
    linhas = [(l1, _tinta(l1)), (l2, _tinta(l2)), (l3, _tinta(l3))]
    gaps = [int(tam2 * 0.22), int(tam2 * 0.26)]               # entre as linhas, proporcional à principal
    altura = 2 * P + sum(t[3] - t[1] for _, t in linhas) + sum(gaps)
    im = Image.new("RGBA", (larg, altura), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, larg - 1, altura - 1), radius=40, fill=COR["azul"] + (255,))
    y = P
    pos = []
    for k, (l, t) in enumerate(linhas):
        im.alpha_composite(l.crop(t), (P, y))
        pos.append((y, y + t[3] - t[1]))
        y += t[3] - t[1] + (gaps[k] if k < 2 else 0)
    if p_seta > 0:                                           # seta: centro óptico da linha principal, margem = respiro
        d = ImageDraw.Draw(im)
        a = int(255 * min(1, p_seta * 3))
        dy = int(8 * np.sin(p_seta * 8))
        cy = (pos[1][0] + pos[1][1]) // 2 + dy
        cx = larg - P - 40
        d.line([(cx - 38, cy - 19), (cx, cy + 19), (cx + 38, cy - 19)], fill=COR["laranja"] + (a,), width=13, joint="curve")
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
    vel = rot.get("burn_velocidade", 1.6)                  # ~38% mais curto: um flash rápido, som junto
    burns = carregar_burns(rot["burns_arquivos"], vel)
    cortes = rot["burns"] if versao == "A" else rot.get("burns_B", rot["burns"])
    atras = [Linhas(b) for b in rot["atras"] if versao == "A" or not b.get("so_A")]
    frente = [Linhas(b) for b in rot.get("frente", []) if versao == "A" or not b.get("so_A")]
    atras = ajustar_legibilidade(rot, atras, frente, ms, n, rot.get("limite_oculto", 0.18))
    faixa = Linhas(dividido["faixa"]) if dividido else None
    # legenda: o padrão minimalista da LIV do editor (palavra falada em laranja), sem mexer no editor
    sys.path.insert(0, AQUI)
    import editor_reels as er
    ws = []
    for p in palavras:
        w = p["w"]
        for a_, b_ in rot.get("trocas", {}).items():
            w = w.replace(a_, b_)
        ws.append(dict(p, w=w))
    grupos = er.grupos_legenda(ws)
    leg = er.Legenda("liv")
    letterings = [Lettering(b) for b in rot.get("lettering", [])]
    sem_leg = [(b.b.get("legenda_desde", b.b["t0"]) if b.b.get("legenda_desde") else b.b["t0"],
                b.b["t1"]) for b in atras + frente if not b.b.get("legenda") and not b.b.get("legenda_desde")]
    sem_leg += [(b.b["t0"], b.b.get("legenda_desde")) for b in atras + frente if b.b.get("legenda_desde")]
    sem_leg += [(b.b["t0"], b.b["t1"]) for b in letterings] + [(rot["cta"]["t0"], dur + 1)]
    if dividido:
        sem_leg.append((dividido["t0"], dividido["t1"]))
    cache_leg = {}
    cta = rot["cta"]

    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", *PLAT.h264("16M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", tmp_v],
                           stdin=subprocess.PIPE)
    alvo_png = sorted(quadros_png or [])
    previas = os.path.join(CACHE, "previas", os.path.splitext(os.path.basename(saida))[0])   # temporário, fora da pasta do vídeo
    if alvo_png:
        os.makedirs(previas, exist_ok=True)
    m_ant = None
    ate = rot.get("_ate")
    if alvo_png:
        print(f"  quadros de conferência em: {previas}", flush=True)
    for i in range(n):
        t = i / FPS
        if ate and t > ate:
            break
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
            if any(l.ativo(t) for l in letterings):
                q = escurecer_base(q, br.get("veu", 0.62))
        for l in letterings:
            l.desenhar(q, t)
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
            gi = next((k for k, g in enumerate(grupos) if g[0]["s"] <= t < (grupos[k + 1][0]["s"] if k + 1 < len(grupos) else g[-1]["e"] + 0.6)
                       and t < g[-1]["e"] + 0.6), None)
            if gi is not None:
                g = grupos[gi]
                ativo = max(k for k, p in enumerate(g) if p["s"] <= t + 0.02)
                colar(q, leg.render(gi, g, ativo), W / 2, rot.get("y_legenda", int(H * 0.62)))
        # CTA: card sobe para o lugar (pé do card no limite da área segura)
        if t >= cta["t0"]:
            p = min(1.0, (t - cta["t0"]) / 0.45)
            e = 1 - (1 - p) ** 4
            im = render_cta(cta, max(0.0, t - cta["t_seta"]) if t >= cta["t_seta"] else 0)
            if im.height + 0 > SEGURA["y1"] - SEGURA["y0"]:
                print("  ⚠️  CTA maior que a área segura")
            pe = cta.get("pe", SEGURA["y1"])
            topo = pe - im.height + int((1 - e) * 90)
            a = np.array(im); a[..., 3] = (a[..., 3] * e).astype(np.uint8)
            colar(q, Image.fromarray(a), SEGURA["x0"] + im.width / 2, topo + im.height / 2)
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
                Image.fromarray(out).save(os.path.join(previas, f"{tp:05.2f}s.png"))
        if i % 150 == 0:
            print(f"  {t:5.1f}s / {dur:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    if ate:
        os.remove(tmp_v); return None
    # áudio: a fala + o som do próprio film burn (alinhado com a imagem dele), equalizado por baixo da voz
    ent = ["-i", tmp_v, "-i", base_v]
    filt, rot_alvo = ["[1:a]volume=1.0[voz]"], rot.get("burn_som_db", -10.0)   # pico do som da transição
    usados = 0
    for k, c in enumerate(cortes):
        arq = rot["burns_arquivos"][k % len(burns)]
        pico = max_volume(arq)
        if pico is None:
            continue
        ent += ["-i", arq]
        bn = burns[k % len(burns)]
        ini = max(0.0, c - bn["pico"] / FPS)
        fim = max(0.2, bn["dur"] - 0.22)                     # o som acaba junto com a luz (nada tocando na cena seguinte)
        filt.append(f"[{usados + 2}:a]atempo={vel},volume={rot_alvo - pico:.1f}dB,atrim=0:{bn['dur']:.2f},"
                    f"afade=t=out:st={fim:.2f}:d=0.22,adelay={int(ini * 1000)}:all=1[w{usados}]")
        usados += 1
    rotulos = "[voz]" + "".join(f"[w{k}]" for k in range(usados))
    fc = ";".join(filt + [f"{rotulos}amix=inputs={usados + 1}:normalize=0:duration=first[a]"])
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
    ap.add_argument("--ate", type=float, help="prévia: renderiza só até esse segundo (sem áudio), pra conferir quadros")
    ap.add_argument("--se-ilegivel", choices=["auto", "quebrar", "frente", "atras"], help="força o tratamento do texto atrás")
    a = ap.parse_args()
    PLAT.limpar_temporarios()
    rot = carregar_roteiro(a.roteiro)
    rot["_ate"] = a.ate
    if a.se_ilegivel:
        for b in rot.get("atras", []):
            if a.se_ilegivel == "atras":
                b["forcar_atras"] = True
            else:
                b["se_ilegivel"] = a.se_ilegivel
    rot["saida"] = PLAT.caminho(rot.get("saida", "~/Desktop/Editor Reels/anuncios"))
    os.makedirs(rot["saida"], exist_ok=True)
    nome = rot["nome"] + ("_A_texto_atras" if a.versao == "A" else "_B_tela_dividida") + (f"_teste_{a.se_ilegivel}" if a.se_ilegivel else "") + ".mp4"
    saida = os.path.join(rot["saida"], nome)
    qs = [float(x) for x in a.quadros.split(",") if x.strip()]
    print("pronto:", montar(rot, a.versao, saida, qs))
