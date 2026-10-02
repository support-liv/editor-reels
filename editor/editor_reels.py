#!/usr/bin/env python3
"""
Editor automático de Reels (IN26).

Etapas:
  1. transcreve com Whisper (timestamps por palavra, cache em JSON)
  2. corta as perguntas do entrevistador e os silêncios
  3. enquadra 9:16 seguindo o rosto (detector Vision do macOS), direto do 4K,
     com punch-in alternado a cada corte
  4. queima legenda palavra a palavra, gancho no topo e CTA no final
  5. exporta 1080x1920, 30fps, áudio normalizado, pronto pra postar

Uso rápido:
  python3 editor_reels.py VIDEO.MOV --marca imigrar --gancho "Texto do gancho"
Veja COMO_USAR.md pra todas as opções.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
import numpy as np
import cv2
import plataforma as PLAT
from PIL import Image, ImageDraw, ImageFont

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT_W, OUT_H, FPS = 1080, 1920, 30
RESPIRO = {}                          # --respiro: pausas mais naturais pra quem fala mais devagar
TAM_LEGENDA = 38                      # fonte da legenda (era 58; 35% menor)
Y_CAIXA = 290                         # abaixo da barra do Instagram (topo ~250px)
LIMITE_SOBREPOSICAO = 0.70            # tela dividida: abaixo disso a live mostra chat/banners (medido: até 73%)
LIMIAR_VOZ = 200                      # Hz: acima disso considera voz aguda
AMOSTRAS_POR_SEG = 5                  # frequência da detecção de rosto

FONTES = os.path.join(os.path.dirname(AQUI), "assets", "fontes")
# fonte e cores de cada marca, sempre (legenda, gancho, CTA). escala: a fonte da marca desenha menor que a
# Arial Black em que os tamanhos foram aprovados; a escala mantém a mesma altura visual.
MARCAS = {
    "imigrar": {"destaque": (249, 13, 91), "caixa": (255, 255, 255), "texto_caixa": (20, 20, 20),
                "fonte": os.path.join(FONTES, "InterTight[wght].ttf"), "peso": "Black", "escala": 1.10},
    "liv":     {"destaque": (255, 110, 31), "caixa": (44, 54, 66), "texto_caixa": (255, 255, 255),
                "fonte": os.path.join(FONTES, "DarkerGrotesque[wght].ttf"), "peso": "Black", "escala": 1.35,
                # LIV é clean: sem contorno nem sombra no texto. A legenda vai num bloco sólido azul (como as etiquetas do manual)
                "legenda": "bloco", "bloco": (44, 54, 66), "texto_legenda": (255, 240, 230)},
}
# estilos da tarja (gancho/CTA): cor de fundo, cor do texto, só com cores da paleta de cada marca
ESTILOS_CAIXA = {
    "imigrar": {"branco": ((255, 255, 255), (20, 20, 20)),       # Imigrar: rosa #F90D5B, azul royal #0E59C5
                "azul": ((14, 89, 197), (255, 255, 255)),
                "rosa": ((249, 13, 91), (255, 255, 255))},
    "liv":     {"azul": ((44, 54, 66), (255, 255, 255)),          # LIV: manual de identidade visual
                "laranja": ((255, 110, 31), (255, 255, 255)),
                "bege": ((255, 240, 230), (44, 54, 66)),
                "marrom": ((148, 89, 67), (255, 255, 255))},
}

VINHETA = {"liv": os.path.join(os.path.dirname(AQUI), "assets", "vinheta_cortes_liv.mp4")}   # só corte longo do YouTube


def fonte_marca(marca, tam):
    """fonte oficial da marca no peso das legendas/caixas, no tamanho equivalente ao aprovado."""
    m = MARCAS[marca]
    f = ImageFont.truetype(m["fonte"], int(round(tam * m["escala"])))
    f.set_variation_by_name(m["peso"])
    return f


# ---------------------------------------------------------------- utilidades
def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", "", s)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Erro rodando {' '.join(cmd[:3])}...\n{r.stderr[-2000:]}")
    return r.stdout


def duracao(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", path]).strip())


def tamanho_real(path):
    """largura x altura já com a rotação do iPhone aplicada."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height:stream_side_data=rotation", "-of", "json", path])
    st = json.loads(out)["streams"][0]
    w, h = st["width"], st["height"]
    rot = next((abs(int(sd.get("rotation", 0))) for sd in st.get("side_data_list", []) if "rotation" in sd), 0)
    return (h, w) if rot in (90, 270) else (w, h)


def entrada_video(path):
    """argumentos de entrada + filtro inicial pra decodificar em SDR BT.709 com a orientação certa.
    iPhone grava em HDR (HLG/Dolby Vision, BT.2020): sem converter, a imagem fica lavada.
    A conversão (com tone mapping) é feita pelo VideoToolbox do macOS."""
    out = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
               "stream=width,height,color_transfer:stream_side_data=rotation", "-of", "json", path])
    st = json.loads(out)["streams"][0]
    hdr = st.get("color_transfer") in ("arib-std-b67", "smpte2084")
    if not hdr:
        return [], ""
    return PLAT.entrada_hdr(st)                        # Mac: VideoToolbox; Windows: zscale + tonemap


# ---------------------------------------------------------------- 1. transcrição
def transcrever(video, cache):
    if os.path.exists(cache):
        return json.load(open(cache))
    import whisper
    wav = cache.replace(".json", ".wav")
    run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-ac", "1", "-ar", "16000", wav])
    print("Transcrevendo (pode levar uns minutos)...")
    model = whisper.load_model("medium")
    res = model.transcribe(wav, language="pt", word_timestamps=True, fp16=False,
                           condition_on_previous_text=False)
    palavras = []
    for seg in res["segments"]:
        for w in seg.get("words", []):
            palavras.append({"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)})
    # o Whisper às vezes "pula" frases e estica uma palavra por vários segundos: transcreve de novo só essa janela
    for w in [p for p in palavras if p["e"] - p["s"] > 2.0]:
        ini, fim = max(0.0, w["s"] - 1.0), w["e"] + 0.5
        jan = cache.replace(".json", ".janela.wav")
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", wav, jan])
        r2 = model.transcribe(jan, language="pt", word_timestamps=True, fp16=False, condition_on_previous_text=False)
        novas = [{"w": x["word"].strip(), "s": round(ini + x["start"], 3), "e": round(ini + x["end"], 3)}
                 for sg in r2["segments"] for x in sg.get("words", [])]
        os.remove(jan)
        if novas and max(x["e"] - x["s"] for x in novas) < 2.0:
            palavras = [p for p in palavras if p["e"] <= ini + 0.05] + novas + [p for p in palavras if p["s"] >= fim - 0.05]
            print(f"  Whisper pulou fala em {ini:.1f}-{fim:.1f}s: transcrito de novo ({len(novas)} palavras)")
    dados = {"texto": res["text"].strip(), "palavras": palavras,
             "segmentos": [{"s": s["start"], "e": s["end"], "t": s["text"].strip()} for s in res["segments"]]}
    json.dump(dados, open(cache, "w"), ensure_ascii=False, indent=1)
    os.remove(wav)
    return dados


def achar_frase(palavras, frase, depois=0):
    alvo = norm(frase).split()
    toks = [norm(p["w"]) for p in palavras]
    for i in range(depois, len(toks) - len(alvo) + 1):
        if toks[i:i + len(alvo)] == alvo:
            return i
    return None


# ---------------------------------------------------------------- 2. cortes
def plano_de_cortes(dados, comecar=None, terminar=None, remover=(), trechos=None,
                    tirar_perguntas=True, max_pausa=0.35, folga=0.10, perguntas=()):
    P = dados["palavras"]
    ini, fim = 0, len(P) - 1
    if comecar:
        i = achar_frase(P, comecar)
        if i is None:
            sys.exit(f'Não achei "{comecar}" na fala. Veja o .json da transcrição.')
        ini = i
    if terminar:
        i = achar_frase(P, terminar, ini)
        if i is None:
            sys.exit(f'Não achei "{terminar}" na fala.')
        fim = i + len(norm(terminar).split()) - 1

    manter = [ini <= k <= fim for k in range(len(P))]
    if trechos:
        for k, p in enumerate(P):
            if not any(a - 0.05 <= p["s"] and p["e"] <= b + 0.05 for a, b in trechos):
                manter[k] = False
    if tirar_perguntas:
        # pergunta do entrevistador: segmento que termina em "?" (e o recomeço "..." logo antes)
        segs = dados["segmentos"]
        for j, sg in enumerate(segs):
            t = sg["t"].strip()
            eh_pergunta = t.endswith("?") and len(t.split()) >= 4
            recomeco = t.endswith("...") and j + 1 < len(segs) and segs[j + 1]["t"].strip().endswith("?")
            if eh_pergunta or recomeco:
                for k, p in enumerate(P):
                    if p["s"] >= sg["s"] - 0.05 and p["e"] <= sg["e"] + 0.05:
                        manter[k] = False
    for trecho in remover:
        i = achar_frase(P, trecho, ini)
        if i is None:
            print(f'  aviso: não achei "{trecho}" pra remover')
            continue
        for k in range(i, i + len(norm(trecho).split())):
            manter[k] = False

    eh_perg = lambda p: any(a - 0.05 <= p["s"] and p["e"] <= b + 0.05 for a, b in perguntas)
    blocos, atual = [], None
    for k, p in enumerate(P):
        if not manter[k]:
            atual = None
            continue
        if atual and p["s"] - atual["e_word"] <= max_pausa and eh_perg(p) == atual["perg"]:
            atual["e_word"] = p["e"]
            atual["idx"].append(k)
        else:
            atual = {"s_word": p["s"], "e_word": p["e"], "idx": [k], "perg": eh_perg(p)}
            blocos.append(atual)
    cortes = []
    for b in blocos:
        s = max(0.0, b["s_word"] - folga)
        e = b["e_word"] + folga + 0.05
        if cortes and cortes[-1].get("perg") != b["perg"]:
            s = max(s, cortes[-1]["e"])                  # pergunta e resposta nunca se misturam
            cortes.append({"s": round(s, 3), "e": round(e, 3), "idx": b["idx"], "perg": b["perg"]})
        elif cortes and s <= cortes[-1]["e"]:
            cortes[-1]["e"] = e
            cortes[-1]["idx"] += b["idx"]
        else:
            cortes.append({"s": round(s, 3), "e": round(e, 3), "idx": b["idx"], "perg": b["perg"]})
    for c in cortes:
        c["texto"] = " ".join(P[k]["w"] for k in c["idx"])
    return cortes


# ---------------------------------------------------------------- 2b. ajuste fino pelo áudio e pelo olhar
_cache_energia = {}


def energia_db(video):
    """energia da fala em dB a cada 20 ms (cache por vídeo)."""
    if video not in _cache_energia:
        sr = 16000
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", str(sr),
                              "-f", "s16le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        hop = int(0.02 * sr)
        n = len(x) // hop - 1
        e = np.sqrt(np.array([np.mean(x[i * hop:(i + 2) * hop] ** 2) for i in range(n)]) + 1e-10)
        db = 20 * np.log10(e)
        lim = np.percentile(db, 10) + 0.45 * (np.percentile(db, 95) - np.percentile(db, 10))
        _cache_energia[video] = (db, lim)
    return _cache_energia[video]


def refinar_cortes(video, cortes, P, pausa_max=0.25, antes=0.05, depois=0.10):
    """corta onde a voz começa/termina de verdade e tira pausas internas (respiro, olhada pro lado).
    O Whisper costuma esticar o fim da última palavra pro silêncio: é isso que denuncia o corte."""
    pausa_max, depois = RESPIRO.get("pausa_max", pausa_max), RESPIRO.get("depois", depois)
    db, lim = energia_db(video)
    suave = lambda m: np.convolve(m.astype(int), np.ones(3, int), "same") >= 2   # ignora estalos < 60 ms
    fala_normal = suave(db > lim)
    fala_baixa = suave(db > lim - 8)          # pergunta do entrevistador costuma sair mais baixa no microfone
    novos = []
    for gi_orig, c in enumerate(cortes):
        fala = fala_baixa if c.get("perg") else fala_normal
        i0, i1 = int(c["s"] / 0.02), min(len(fala), int(c["e"] / 0.02) + 1)
        idx = np.where(fala[i0:i1])[0]
        if len(idx) == 0:
            continue
        # blocos de fala separados por silêncios maiores que pausa_max
        blocos, ini, ant = [], idx[0], idx[0]
        for j in idx[1:]:
            if (j - ant) * 0.02 > pausa_max:
                blocos.append((ini, ant)); ini = j
            ant = j
        blocos.append((ini, ant))
        faixas = []
        for a, b in blocos:
            s = max(c["s"], (i0 + a) * 0.02 - antes)
            e = min(c["e"] + 0.05, (i0 + b + 1) * 0.02 + depois)
            if e - s >= 0.25:
                faixas.append((s, e))
        if not faixas:
            continue
        # cada palavra vai pro pedaço mais próximo (o tempo do Whisper às vezes cai no silêncio: nenhuma se perde)
        dist = lambda m, f: 0 if f[0] <= m <= f[1] else min(abs(m - f[0]), abs(m - f[1]))
        donos = {k: [] for k in range(len(faixas))}
        for q in c["idx"]:
            m = (P[q]["s"] + P[q]["e"]) / 2
            donos[min(range(len(faixas)), key=lambda k: dist(m, faixas[k]))].append(q)
        for k, (s, e) in enumerate(faixas):
            if HESITACOES and not donos[k] and e - s < 1.2:   # voz sem palavra nenhuma: "éé", "hmm", respiração
                print(f"  hesitação sem palavra tirada: {s:.2f}-{e:.2f}")
                continue
            n = dict(c); n.update({"s": round(s, 3), "e": round(e, 3), "idx": donos[k]})
            n.setdefault("grupo", gi_orig)                 # zoom alterna por bloco original, não por pedaço
            n["texto"] = " ".join(P[q]["w"] for q in donos[k])
            novos.append(n)
    # pedaço seguinte começando antes do fim do anterior repetia o começo da palavra ("LIV vi vi")
    for a, b in zip(novos, novos[1:]):
        if a["s"] < b["s"] < a["e"]:
            a["e"] = b["s"]
    # palavra que ficou em dois pedaços vai só pro primeiro
    vistos = set()
    for n in novos:
        n["idx"] = [q for q in n["idx"] if q not in vistos]
        vistos.update(n["idx"])
    return novos


HESITACOES = False                                # --tirar-hesitacoes
COLUNAS = (2, None)                               # --colunas N --pessoas cima,baixo (live com N pessoas lado a lado)
SONS_HESITACAO = {"ah", "eh", "ha", "hum", "hm", "hmm", "ahn", "uhm", "uh", "ehh", "ee", "eee", "aa"}


def tirar_hesitacoes(cortes, P):
    """tira muletas e hesitações faladas: "é..."/"e..." esticado (>= 0,45s), "ah/eh/hã/hum", e "então, assim" seguido
    de pausa. A legenda perde a palavra junto."""
    alvo = []
    for c in cortes:
        idx = c["idx"]
        for j, q in enumerate(idx):
            w, d = norm(P[q]["w"]), P[q]["e"] - P[q]["s"]
            prox = P[idx[j + 1]] if j + 1 < len(idx) else None
            if w in SONS_HESITACAO or (w == "e" and d >= 0.45):
                alvo.append(([q], P[q]["s"], P[q]["e"]))
            elif w == "entao" and prox and norm(prox["w"]) == "assim":
                depois = P[idx[j + 2]]["s"] - prox["e"] if j + 2 < len(idx) else 1.0
                if depois >= 0.12 or prox["e"] - prox["s"] >= 0.4:
                    alvo.append(([q, idx[j + 1]], P[q]["s"], prox["e"]))
    for qs, a, b in alvo:
        print(f"  hesitação tirada: {' '.join(P[q]['w'] for q in qs)} ({a:.2f}-{b:.2f})")
        cortes = tirar_trecho(cortes, P, a - 0.02, b + 0.02)
        for c in cortes:
            c["idx"] = [q for q in c["idx"] if q not in qs]
            c["texto"] = " ".join(P[q]["w"] for q in c["idx"])
    return cortes


def tirar_trecho(cortes, P, a, b):
    """tira [a, b] do bruto (gagueira, palavra repetida): o pedaço vira dois, com troca de zoom na emenda."""
    novos = []
    for c in cortes:
        if b <= c["s"] or a >= c["e"]:
            novos.append(c); continue
        partes = [(s, e) for s, e in ((c["s"], a), (b, c["e"])) if e - s >= 0.15]
        dist = lambda m, f: 0 if f[0] <= m <= f[1] else min(abs(m - f[0]), abs(m - f[1]))
        for k, (s, e) in enumerate(partes):
            n = dict(c); n.update({"s": s, "e": e})
            n["idx"] = [q for q in c["idx"]                  # cada palavra no pedaço mais próximo: nenhuma some
                        if min(range(len(partes)), key=lambda j: dist((P[q]["s"] + P[q]["e"]) / 2, partes[j])) == k]
            n["texto"] = " ".join(P[q]["w"] for q in n["idx"])
            n.pop("continua", None)
            if s == b:
                n["salto"] = True                       # zoom muda na emenda: o corte não aparece como pulo
            novos.append(n)
    return novos


def dividir_pra_zoom(cortes, P, alvo=2.6, minimo=1.5):
    """--dinamico: quebra pedaços longos entre palavras (de preferência na vírgula/ponto) pra trocar o zoom
    sem cortar a fala. Os pedaços novos são contínuos (sem fade no áudio)."""
    novos, grupo, ult = [], -1, None
    for c in cortes:
        if c.get("grupo") != ult or c.get("salto") or not novos:
            grupo += 1; ult = c.get("grupo")
        partes, ini, idx = [], c["s"], list(c["idx"])
        atual = []
        for j, q in enumerate(idx):
            atual.append(q)
            if j + 1 >= len(idx):
                break
            fim = P[q]["e"]
            corrido = fim - ini
            pontuado = P[q]["w"].rstrip()[-1:] in ",.;:!?"
            if corrido >= alvo * (1 if pontuado else 1.35) and c["e"] - fim >= minimo:
                t = round(min(max((fim + P[idx[j + 1]]["s"]) / 2, ini + 0.5), c["e"] - 0.5), 3)
                partes.append((ini, t, atual)); ini, atual = t, []
        partes.append((ini, c["e"], atual))
        for k, (a, b, ws) in enumerate(partes):
            n = dict(c); n.update({"s": a, "e": b, "idx": ws, "grupo": grupo + k})
            n["texto"] = " ".join(P[q]["w"] for q in ws)
            if k:
                n["continua"] = True
            novos.append(n)
        grupo += len(partes) - 1
    return novos


_cache_olhar = {}


def olhar(video, fps=4):
    """inclinação da cabeça ao longo do vídeo: [(t, pitch, yaw)] do rosto principal."""
    if video in _cache_olhar:
        return _cache_olhar[video]
    garantir_detector()
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale=360:-2", "-q:v", "5",
         os.path.join(tmp, "%05d.jpg")])
    imgs = sorted(os.listdir(tmp))
    pontos = []
    for i in range(0, len(imgs), 400):
        lote = imgs[i:i + 400]
        for j, ln in enumerate(_detectar([os.path.join(tmp, f) for f in lote])):
            faces = [f for f in json.loads(ln) if len(f) >= 6]
            if faces:
                f = max(faces, key=lambda f: f[2])
                pontos.append(((i + j + 0.5) / fps, f[4], f[5]))
    shutil.rmtree(tmp)
    _cache_olhar[video] = pontos
    return pontos


def olhando_pra_baixo(video, s, e):
    """fração do trecho com a cabeça baixa (lendo o celular) ou virada pro lado."""
    pts = olhar(video)
    if not pts:
        return 0.0
    base_p = np.percentile([p for _, p, _ in pts], 25)
    base_y = np.median([y for _, _, y in pts])
    trecho = [(p, y) for t, p, y in pts if s <= t <= e]
    if not trecho:
        return 0.0
    return float(np.mean([(p > base_p + 0.16) or (abs(y - base_y) > 0.28) for p, y in trecho]))


# ---------------------------------------------------------------- 3. enquadramento
DETECTOR = os.path.join(AQUI, "rostos")


def garantir_detector():
    """o detector é escolhido pela plataforma (Mac: Vision; Windows: OpenCV YuNet)."""


def _detectar(imgs):
    """uma linha JSON por imagem: [[cx, cy, w, h, pitch, yaw], ...] (mesmo formato nos dois sistemas)."""
    return [json.dumps(r) for r in PLAT.rostos(imgs)] if imgs else []


def trajetoria(video, c, pessoa, alvo_x=None):
    """posição (cx, cy normalizados) do rosto escolhido ao longo do corte, já suavizada."""
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s']:.3f}", "-i", video,
         "-vf", f"fps={AMOSTRAS_POR_SEG},scale=540:-2", "-q:v", "4", os.path.join(tmp, "%04d.jpg")])
    imgs = sorted(os.listdir(tmp))
    linhas = _detectar([os.path.join(tmp, f) for f in imgs]) if imgs else []
    shutil.rmtree(tmp)
    if isinstance(alvo_x, int):
        return _trajetoria_por_ordem([json.loads(ln) for ln in linhas], alvo_x)
    pontos = []
    for ln in linhas:
        faces = [f for f in json.loads(ln) if f[2] > 0.03]       # ignora rosto minúsculo no fundo
        if alvo_x is not None:                                 # fecha em quem está nessa posição
            faces = [f for f in faces if abs(f[0] - alvo_x) < 0.13]
        if pessoa == "direita":                                # nunca pega quem está do outro lado
            faces = [f for f in faces if f[0] > 0.45]
        elif pessoa == "esquerda":
            faces = [f for f in faces if f[0] < 0.55]
        if faces:                                              # só os rostos principais (gente do fundo sai)
            maior = max(f[2] for f in faces)
            faces = [f for f in faces if f[2] >= maior * 0.6]
        if not faces:
            pontos.append(None)
        elif pessoa == "direita":
            pontos.append(max(faces, key=lambda f: f[0]))
        elif pessoa == "esquerda":
            pontos.append(min(faces, key=lambda f: f[0]))
        else:
            pontos.append(max(faces, key=lambda f: f[2]))      # o maior = mais perto da câmera
    # ignora saltos bruscos (detector trocou de pessoa); só aceita se o salto durar mais de 2s
    ref, fila = None, []
    for i, p in enumerate(pontos):
        if not p:
            continue
        if ref is None or abs(p[0] - ref[0]) < 0.18:
            ref, fila = p, []
            continue
        fila.append(i)
        if len(fila) > 2 * AMOSTRAS_POR_SEG:
            ref, fila = p, []
        else:
            pontos[i] = None
    validos = [p for p in pontos if p]
    if not validos:
        return np.array([0.0]), np.array([[0.5, 0.35]])
    ultimo = validos[0]
    for i, p in enumerate(pontos):                             # preenche buracos
        pontos[i] = ultimo = p or ultimo
    xy = np.array([[p[0], p[1]] for p in pontos])
    k = min(len(xy), 7)                                        # média móvel ~1,4s
    if k > 1:
        pad = np.pad(xy, ((k // 2, k // 2), (0, 0)), mode="edge")
        xy = np.stack([np.convolve(pad[:, d], np.ones(k) / k, mode="valid") for d in (0, 1)], axis=1)[:len(pontos)]
    ts = (np.arange(len(xy)) + 0.5) / AMOSTRAS_POR_SEG
    return ts, xy


def _suavizar(pontos):
    validos = [p for p in pontos if p]
    if not validos:
        return np.array([0.0]), np.array([[0.5, 0.35]])
    ultimo = validos[0]
    for i, p in enumerate(pontos):
        pontos[i] = ultimo = p or ultimo
    xy = np.array([[p[0], p[1]] for p in pontos])
    k = min(len(xy), 7)
    if k > 1:
        pad = np.pad(xy, ((k // 2, k // 2), (0, 0)), mode="edge")
        xy = np.stack([np.convolve(pad[:, d], np.ones(k) / k, mode="valid") for d in (0, 1)], axis=1)[:len(pontos)]
    return (np.arange(len(xy)) + 0.5) / AMOSTRAS_POR_SEG, xy


def _trajetoria_por_ordem(amostras, ordem):
    """identifica as pessoas pela ordem da esquerda pra direita no frame com mais rostos
    e segue cada uma pelo vizinho mais próximo (pra frente e pra trás)."""
    amostras = [[f for f in fs if f[2] > 0.03] for fs in amostras]
    amostras = [[f for f in fs if f[2] >= max(g[2] for g in fs) * 0.6] if fs else [] for fs in amostras]
    if not any(amostras):
        return _suavizar([None])
    ref = max(range(len(amostras)), key=lambda i: len(amostras[i]))
    pessoas = sorted(amostras[ref], key=lambda f: f[0])
    if len(pessoas) < ordem:
        return _suavizar([None] * len(amostras))
    pontos = [None] * len(amostras)
    for sentido in (range(ref, len(amostras)), range(ref, -1, -1)):
        pos = [p[:] for p in pessoas]
        for i in sentido:
            usados = set()
            for j, p in enumerate(pos):
                cands = [(abs(f[0] - p[0]) + abs(f[1] - p[1]), k) for k, f in enumerate(amostras[i]) if k not in usados]
                if cands:
                    d, k = min(cands)
                    if d < 0.10:
                        usados.add(k)
                        pos[j] = amostras[i][k]
                        if j == ordem - 1:
                            pontos[i] = amostras[i][k]
    return _suavizar(pontos)


def posicoes_pessoas(video, n_amostras=16):
    """x (0-1) de cada pessoa em cena, da esquerda pra direita."""
    dur = duracao(video)
    tmp = tempfile.mkdtemp()
    for i, t in enumerate(np.linspace(dur * 0.05, dur * 0.95, n_amostras)):
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                        "-vf", "scale=540:-2", os.path.join(tmp, f"{i:03d}.jpg")])
    imgs = sorted(os.listdir(tmp))
    xs = []
    for ln in _detectar([os.path.join(tmp, f) for f in imgs]):
        faces = [f for f in json.loads(ln) if f[2] > 0.03]
        if faces:
            maior = max(f[2] for f in faces)
            xs += [f[0] for f in faces if f[2] >= maior * 0.6]
    shutil.rmtree(tmp)
    xs = sorted(xs)
    grupos, g = [], [xs[0]] if xs else []
    for x in xs[1:]:
        if x - g[-1] > 0.08:
            grupos.append(g); g = [x]
        else:
            g.append(x)
    if g:
        grupos.append(g)
    grupos = [g for g in grupos if len(g) >= n_amostras * 0.3]      # só quem aparece bastante
    return [float(np.median(g)) for g in grupos]


def tom_de_voz(video, c):
    """frequência fundamental mediana (Hz) da fala no corte: ~100-150 grave, ~180-250 aguda."""
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s']:.3f}",
                          "-i", video, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    if len(x) < sr // 4:
        return 0.0
    win, hop = int(0.05 * sr), int(0.02 * sr)
    quadros = [x[i:i + win] for i in range(0, len(x) - win, hop)]
    energia = np.array([np.sqrt(np.mean(q ** 2)) for q in quadros])
    lim = np.percentile(energia, 60)
    f0s = []
    lo, hi = sr // 400, sr // 70
    for q, e in zip(quadros, energia):
        if e < lim:
            continue
        q = q - q.mean()
        ac = np.correlate(q, q, "full")[win - 1:]
        if ac[0] <= 0:
            continue
        lag = lo + int(np.argmax(ac[lo:hi]))
        if 2 * lag < hi and ac[2 * lag] > 0.9 * ac[lag]:
            lag *= 2                                   # o pico real era o dobro do período
        if ac[lag] / ac[0] > 0.35:
            f0s.append(sr / lag)
    return float(np.median(f0s)) if f0s else 0.0


def caixa(cx, cy, frac, W, H):
    """crop 9:16 com 'frac' da largura (vídeo em pé) ou da altura (vídeo deitado, ex.: live 16:9), rosto a ~38% do topo.
    O recorte é SEMPRE 9:16: nunca estica nem espreme a imagem."""
    if W * frac * 16 / 9 <= H:                           # vídeo em pé: a largura manda
        cw = int(W * frac) // 2 * 2
        ch = int(cw * 16 / 9) // 2 * 2
    else:                                                # vídeo deitado: a altura manda (frac 0,93 = altura toda)
        ch = int(H * min(1.0, frac / 0.93)) // 2 * 2
        cw = int(ch * 9 / 16) // 2 * 2
    assert abs(cw / ch - 9 / 16) < 0.01, f"recorte fora de 9:16 ({cw}x{ch}): distorceria o vídeo"
    x0 = int(np.clip(cx * W - cw / 2, 0, W - cw))
    y0 = int(np.clip(cy * H - ch * 0.38, 0, H - ch))
    return x0, y0, cw, ch


# ---------------------------------------------------------------- 4. legenda e caixas
CORRECOES = {  # erros comuns do Whisper nesses vídeos
    "ENBDE": "INBDE", "ENBD": "INBDE", "INBD": "INBDE", "NBD": "INBDE", "INBDI": "INBDE",
    "TOFEL": "TOEFL", "BORG": "BOARD", "BORDER": "BOARD", "BORDE": "BOARD", "BORNEI": "BOARD", "BORDEN": "BOARD",
    "GREENCARD": "GREEN CARD", "EMIGRAR": "IMIGRAR", "IMIGRARIUA": "IMIGRAR EUA", "EMIGRARIUA": "IMIGRAR EUA",
    "ALIVE": "LIV", "EB2": "EB-2", "O1": "O-1", "VCB1": "EB-1", "VISTUA": "VISTO",
    "ODOTOLOGIA": "ODONTOLOGIA", "ONONTOLOGIA": "ODONTOLOGIA", "ESPATRIAR": "EXPATRIAR", "BORDS": "BOARD", "HIDROGENISTAS": "HIGIENISTAS",
    "DOUTOLOGIA": "ODONTOLOGIA", "DENTOLOGIA": "ODONTOLOGIA", "PRESADORA": "FRESADORA", "APROPILAXIA": "PROFILAXIA",
    "RB2": "EB-2", "EB2NW": "EB-2 NIW", "INBZ": "INBDE", "ANVD": "INBDE", "NBDI": "INBDE", "UNBD": "INBDE", "JULIE": "JÚLIA", "MERITOGRAFIA": "MERITOCRACIA",
}


def limpar(w):
    w = re.sub(r"[.,!:;?]+$", "", w).upper()
    return CORRECOES.get(w, w)


def aplicar_trocas(pal, trocas):
    for troca in trocas:
        de, para = troca.split("=", 1)
        alvo, novas = norm(de).split(), para.split()
        i = 0
        while i <= len(pal) - len(alvo):
            if [norm(p["w"]) for p in pal[i:i + len(alvo)]] == alvo:
                s0, e0 = pal[i]["s"], pal[i + len(alvo) - 1]["e"]
                passo = (e0 - s0) / len(novas)
                pal[i:i + len(alvo)] = [{"w": w, "s": s0 + k * passo, "e": s0 + (k + 1) * passo}
                                        for k, w in enumerate(novas)]
                i += len(novas)
            else:
                i += 1
    return pal


def grupos_legenda(palavras_saida, max_palavras=3, max_chars=18):
    grupos, g = [], []
    for p in palavras_saida:
        texto = " ".join(x["w"] for x in g + [p])
        pontua = g and re.search(r"[.,?!:]$", g[-1]["w"])
        if g and (len(g) >= max_palavras or len(texto) > max_chars or pontua):
            grupos.append(g)
            g = []
        g.append(p)
    if g:
        grupos.append(g)
    return grupos


class Legenda:
    def __init__(self, marca, tam=TAM_LEGENDA):
        self.cor = MARCAS[marca]["destaque"]
        self.m = MARCAS[marca]
        self.tam = int(round(tam * MARCAS[marca]["escala"]))
        self.f = fonte_marca(marca, tam)
        self.cache = {}

    def render(self, gi, grupo, ativo):
        if (gi, ativo) in self.cache:
            return self.cache[(gi, ativo)]
        img = Image.new("RGBA", (OUT_W, 200), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        palavras = [limpar(p["w"]) for p in grupo]
        esp = int(self.tam * 0.28)
        larg = [d.textlength(w, font=self.f) for w in palavras]
        linhas, linha, lw = [], [], 0
        for i in range(len(palavras)):
            if linha and lw + larg[i] > OUT_W - 140:
                linhas.append(linha); linha, lw = [], 0
            linha.append(i); lw += larg[i] + esp
        linhas.append(linha)
        passo = int(self.tam * 1.24)
        y = 100 - len(linhas) * passo // 2
        bloco = self.m.get("legenda") == "bloco"
        for ln in linhas:
            total = sum(larg[i] for i in ln) + esp * (len(ln) - 1)
            x = (OUT_W - total) / 2
            if bloco:                                   # etiqueta sólida atrás da linha, sem contorno no texto
                topo, base = d.textbbox((x, y), "ÁgÇ", font=self.f)[1], d.textbbox((x, y), "ÁgÇ", font=self.f)[3]
                pad = int(self.tam * 0.34)
                d.rounded_rectangle([x - pad, topo - pad * 0.6, x + total + pad, base + pad * 0.5],
                                    radius=int(self.tam * 0.3), fill=self.m["bloco"] + (240,))
            for i in ln:
                if bloco:
                    d.text((x, y), palavras[i], font=self.f, fill=self.cor if i == ativo else self.m["texto_legenda"])
                else:
                    d.text((x, y), palavras[i], font=self.f, fill=self.cor if i == ativo else (255, 255, 255),
                           stroke_width=max(4, round(self.tam * 0.12)), stroke_fill=(0, 0, 0))
                x += larg[i] + esp
            y += passo
        self.cache[(gi, ativo)] = img
        return img


EMOJIS = {"🇺🇸": os.path.join(AQUI, "bandeira_eua.png"), "🇧🇷": os.path.join(AQUI, "bandeira_brasil.png"),
          "🇪🇺": os.path.join(AQUI, "bandeira_ue.png"), "🇵🇹": os.path.join(AQUI, "bandeira_portugal.png"),
          "🇮🇹": os.path.join(AQUI, "bandeira_italia.png")}


def _emoji(tok, altura):
    if not os.path.exists(EMOJIS[tok]):
        PLAT.emoji_png(tok, EMOJIS[tok])               # bandeiras já vêm no repo (o Windows não desenha bandeira)
    im = Image.open(EMOJIS[tok]).convert("RGBA")
    im = im.crop(im.getbbox())
    return im.resize((int(im.width * altura / im.height), altura), Image.LANCZOS)


def caixa_texto(texto, marca, tam=52, estilo=None):
    """caixa com texto em CAIXA ALTA; aceita 🇺🇸 e 🇧🇷 no meio do texto. estilo: branco/azul/rosa."""
    m = dict(MARCAS[marca])
    if estilo:
        if estilo not in ESTILOS_CAIXA[marca]:
            sys.exit(f'--cor-caixa {estilo} não é da {marca}: use {", ".join(ESTILOS_CAIXA[marca])}')
        m["caixa"], m["texto_caixa"] = ESTILOS_CAIXA[marca][estilo]
    f = fonte_marca(marca, tam)
    tam = f.size
    d0 = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    texto = texto.upper()
    for bandeira in EMOJIS:
        texto = texto.replace(bandeira, f" {bandeira} ")
    toks = texto.split()
    esp = d0.textlength(" ", font=f)
    alt_emoji = int(tam * 1.05)
    larg = lambda t: _emoji(t, alt_emoji).width if t in EMOJIS else d0.textlength(t, font=f)
    # pontuação que sobrou sozinha depois da bandeira ("EUA 🇺🇸?") cola sem espaço
    cola = lambda t: bool(re.fullmatch(r"[?!.,:;]+", t))
    linhas, l, lw = [], [], 0
    for t in toks:
        w = larg(t)
        if l and not cola(t) and lw + esp + w > OUT_W - 200:
            linhas.append(l); l, lw = [], 0
        lw += (esp if l and not cola(t) else 0) + w
        l.append(t)
    linhas.append(l)
    lh = int(tam * 1.3)
    h = lh * len(linhas) + 50
    wl = [sum(larg(t) for t in ln) + esp * sum(1 for k, t in enumerate(ln) if k and not cola(t)) for ln in linhas]
    img = Image.new("RGBA", (OUT_W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0 = (OUT_W - max(wl)) / 2 - 36
    d.rounded_rectangle([x0, 0, OUT_W - x0, h], radius=26, fill=m["caixa"] + (245,))
    for i, ln in enumerate(linhas):
        x, y = (OUT_W - wl[i]) / 2, 25 + i * lh
        for k, t in enumerate(ln):
            if k and cola(t):
                x -= esp
            if t in EMOJIS:
                e = _emoji(t, alt_emoji)
                img.alpha_composite(e, (int(x), int(y + (tam - alt_emoji) / 2 + tam * 0.12)))
            else:
                d.text((x, y), t, font=f, fill=m["texto_caixa"])
            x += larg(t) + esp
    return img


CAUDA = 0.0                                       # --cauda: segundos extras no fim (último quadro parado, silêncio) pro CTA
SEM_LEGENDA = False                               # --sem-legenda: o vídeo de origem já tem legenda gravada
BROLLS = []                                       # [(arquivo, "12.5" ou "fonte:8.4")] vindos do --broll


class Broll:
    """cena de motion (MOV/WebM com transparência) que entra por cima da imagem, embaixo da legenda."""
    def __init__(self, arq, t0, w, h):
        self.arq, self.t0 = arq, t0
        self.dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq]).strip())
        self.w, self.h, self.dec, self.ultimo = w, h, None, None
        self.lidos = 0

    def quadro(self, t):
        """quadro BGRA da cena no tempo t do vídeo final (None fora dela). Leitura sequencial."""
        if not (self.t0 <= t < self.t0 + self.dur):
            return None
        if self.dec is None:
            self.dec = subprocess.Popen(["ffmpeg", "-v", "fatal", "-i", self.arq, "-vf",
                                         f"fps={FPS},scale={self.w}:{self.h}:flags=lanczos,format=bgra",
                                         "-f", "rawvideo", "-pix_fmt", "bgra", "-"], stdout=subprocess.PIPE)
        alvo = int(round((t - self.t0) * FPS))
        while self.lidos <= alvo:
            buf = self.dec.stdout.read(self.w * self.h * 4)
            if len(buf) < self.w * self.h * 4:
                break
            self.ultimo = np.frombuffer(buf, np.uint8).reshape(self.h, self.w, 4)
            self.lidos += 1
        return self.ultimo


def tempo_na_saida(cortes, t_fonte):
    """tempo do bruto -> tempo no vídeo pronto (soma dos cortes antes dele)."""
    acc = 0.0
    for c in cortes:
        if c["s"] <= t_fonte < c["e"]:
            return acc + t_fonte - c["s"]
        if t_fonte < c["s"]:
            return acc
        acc += c["e"] - c["s"]
    return acc


def preparar_brolls(cortes, w, h):
    camadas = []
    for arq, quando in BROLLS:
        t0 = tempo_na_saida(cortes, float(quando[6:])) if quando.startswith("fonte:") else float(quando)
        camadas.append(Broll(arq, t0, w, h))
        print(f"  b-roll {os.path.basename(arq)} em {t0:.2f}s")
    return camadas


def escrever_cauda(enc, base, camadas, n_out):
    """--cauda: último quadro parado (sem legenda) por CAUDA segundos, com os b-rolls por cima (o CTA entra aqui)."""
    for k in range(int(round(CAUDA * FPS))):
        out = base.copy()
        aplicar_brolls(out, camadas, (n_out + k) / FPS)
        enc.stdin.write(out.tobytes())


def aplicar_brolls(out, camadas, t):
    """cola os b-rolls no quadro e devolve quanto da tela eles cobrem (0-1): com o motion na tela, a legenda sai."""
    cobre = 0.0
    for b in camadas:
        q = b.quadro(t)
        if q is not None:
            a = q[:, :, 3:4].astype(np.float32) / 255
            out[:] = (q[:, :, :3] * a + out * (1 - a)).astype(np.uint8)
            cobre = max(cobre, float(a[::16, ::16].mean()))
    return cobre


def colar(frame_bgr, rgba, y):
    arr = np.asarray(rgba)
    h, w = arr.shape[:2]
    alpha = arr[:, :, 3:4].astype(np.float32) / 255
    rgb = arr[:, :, 2::-1].astype(np.float32)
    reg = frame_bgr[y:y + h, 0:w].astype(np.float32)
    frame_bgr[y:y + h, 0:w] = (rgb * alpha + reg * (1 - alpha)).astype(np.uint8)


def n_quadros(c):
    """quadros exatos do corte na saída (o áudio usa a mesma duração: sem isso a boca dessincroniza aos poucos)."""
    return max(1, int(round((c["e"] - c["s"]) * FPS)))


def quadros(dec, fsize, n):
    """lê exatamente n quadros do decodificador: repete o último se faltar, descarta o que sobrar."""
    ultimo = None
    for _ in range(n):
        buf = dec.stdout.read(fsize)
        if len(buf) < fsize:
            if ultimo is None:
                return
            buf = ultimo
        ultimo = buf
        yield buf
    dec.stdout.close()
    dec.kill()


# ---------------------------------------------------------------- 5. render
def renderizar(video, cortes, dados, saida, marca, gancho="", cta="", pessoa=None,
               frac_base=None, frac_punch=None, seg_gancho=3.2, seg_cta=3.5, trocas=(), so_checar=False, y_legenda=0.62, estilo_caixa=None, layout=None, cima="esquerda", girar=0.0, dinamico=False, endireitar=False, vinheta=True, inscreva=True):
    garantir_detector()
    W, H = tamanho_real(video)
    ent_args, ent_filtro = entrada_video(video)
    if ent_filtro:
        print("  vídeo HDR: convertendo pra SDR (BT.709)")
    if frac_base is None:
        frac_base = 0.34 if pessoa == "voz" else 0.55 if pessoa else 0.93
    if frac_punch is None:
        frac_punch = frac_base * (0.85 if pessoa else 0.82)
    mapa_voz = None
    if pessoa == "voz":
        # conversa: pessoa 1 (esquerda) voz grave, pessoa 2 voz aguda (ex.: André e Julia)
        mapa_voz = {"grave": 1, "aguda": 2}
        pessoa = None

    for i, c in enumerate(cortes):                     # duração em quadros inteiros: vídeo e áudio iguais
        if c.get("continua"):
            c["s"] = cortes[i - 1]["e"]
        c["e"] = round(c["s"] + n_quadros(c) / FPS, 4)
    P = dados["palavras"]
    pal_saida, offset = [], 0.0
    for c in cortes:
        for k in c["idx"]:
            p = P[k]
            d = c["e"] - c["s"]
            ini = min(max(0.0, p["s"] - c["s"]), d - 0.12)            # palavra com tempo fora do pedaço fica dentro dele
            fim = max(ini + 0.12, min(d, p["e"] - c["s"]))
            pal_saida.append({"w": p["w"], "s": offset + ini, "e": offset + fim})
        offset += c["e"] - c["s"]
    total = offset
    grupos = [] if SEM_LEGENDA else grupos_legenda(aplicar_trocas(pal_saida, trocas))
    leg = Legenda(marca)
    img_gancho = caixa_texto(gancho, marca, estilo=estilo_caixa) if gancho else None
    img_cta = caixa_texto(cta, marca, estilo=estilo_caixa) if cta else None
    if layout == "youtube":
        return renderizar_youtube(video, cortes, saida, marca, vinheta=vinheta, so_checar=so_checar, inscreva=inscreva)
    if layout == "quadrado":
        return renderizar_quadrado(video, cortes, saida, grupos, marca, img_gancho, img_cta, total,
                                   seg_gancho, seg_cta, so_checar, girar=girar, dinamico=dinamico, endireitar=endireitar)
    if layout == "quadro":
        return renderizar_quadro(video, cortes, saida, grupos, leg, img_gancho, img_cta, total,
                                 seg_gancho, seg_cta, so_checar)
    if layout == "dividido":
        return renderizar_dividido(video, cortes, saida, grupos, leg, img_gancho, img_cta, total,
                                   seg_gancho, seg_cta, so_checar, cima=cima)

    # 1) planeja o enquadramento de todos os cortes
    planos, voz_grupo = [], {}
    for ci, c in enumerate(cortes):
        frac = frac_punch if c.get("grupo", ci) % 2 == 1 else frac_base
        alvo_x = None
        if c.get("quem") and not c.get("perg"):
            alvo_x = c["quem"]
            if pessoa in ("esquerda", "direita"):
                pessoa = None
        elif mapa_voz and not c.get("perg"):
            g = c.get("grupo", ci)
            if g not in voz_grupo:                       # mede no bloco original inteiro (pedaço curto engana)
                irmaos = [x for x in cortes if x.get("grupo", -1) == g] or [c]
                f0 = tom_de_voz(video, {"s": min(x["s"] for x in irmaos), "e": max(x["e"] for x in irmaos)})
                voz_grupo[g] = "aguda" if f0 > LIMIAR_VOZ else "grave"
                print(f"    bloco {g + 1}: voz {f0:.0f} Hz -> {voz_grupo[g]}")
            alvo_x = mapa_voz[voz_grupo[g]]
        if c.get("perg") and (pessoa or mapa_voz):
            frac, ts, xy = 1.0, np.array([0.0]), np.array([[0.5, 0.5]])   # quadro aberto com todos
        else:
            ts, xy = trajetoria(video, c, pessoa, alvo_x)
        planos.append((frac, ts, xy))

    def quadro_saida(t_out):
        """o frame final (sem textos) num instante do vídeo de saída."""
        acc = 0.0
        for c, (frac, ts, xy) in zip(cortes, planos):
            d = c["e"] - c["s"]
            if t_out < acc + d or c is cortes[-1]:
                tl = min(max(0.0, t_out - acc), d - 0.05)
                break
            acc += d
        cx, cy = np.interp(tl, ts, xy[:, 0]), np.interp(tl, ts, xy[:, 1])
        x0, y0, cw, ch = caixa(cx, cy, frac, W, H)
        raw = subprocess.run(["ffmpeg", "-v", "error"] + ent_args + ["-ss", f"{c['s'] + tl:.3f}", "-i", video,
                              "-frames:v", "1", "-vf", f"{ent_filtro}crop={cw}:{ch}:{x0}:{y0},scale=540:960",
                              "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
        return np.frombuffer(raw, np.uint8).reshape(960, 540, 3) if len(raw) == 540 * 960 * 3 else None

    def rostos_em(tempos):
        tmp = tempfile.mkdtemp()
        arqs = []
        for i, t in enumerate(tempos):
            fr = quadro_saida(t)
            if fr is not None:
                arqs.append(os.path.join(tmp, f"{i}.jpg")); cv2.imwrite(arqs[-1], fr)
        linhas = _detectar(arqs) if arqs else []
        shutil.rmtree(tmp)
        return [f for ln in linhas for f in json.loads(ln) if f[2] >= 0.04]

    def sobrepoe(y0, y1, faces, parte):
        """quanto (px) a faixa [y0, y1] cobre dos rostos. parte: 'cabeca' (testa ao queixo) ou 'miolo' (olhos à boca)."""
        tot = 0.0
        for f in faces:
            fy, fh = f[1] * OUT_H, f[3] * OUT_H
            a, b = (fy - fh * 0.75, fy + fh * 0.5) if parte == "cabeca" else (fy - fh * 0.3, fy + fh * 0.35)
            tot += max(0.0, min(y1, b) - max(y0, a))
        return tot

    def escolher_posicao(img, tempos):
        """em cima se não encostar na cabeça; senão no lugar da legenda; senão onde cobrir menos olhos e boca."""
        if img is None:
            return Y_CAIXA, False
        faces = rostos_em(tempos)
        h = img.height
        cand = [(Y_CAIXA, False), (y_leg + 100 - h // 2, True)]
        for y, meio in cand:
            if sobrepoe(y - 20, y + h + 20, faces, "cabeca") == 0:
                return y, meio
        return min(cand, key=lambda c: (sobrepoe(c[0], c[0] + h, faces, "miolo"), c[1]))

    # 2) gancho e CTA: em cima, ou no lugar da legenda se forem tapar um rosto
    y_leg = int(OUT_H * y_legenda)
    y_g, baixo_g = escolher_posicao(img_gancho, [t for t in (0.3, 1.6, 2.9) if t < total])
    y_c, baixo_c = escolher_posicao(img_cta, [max(0, total - x) for x in (3.2, 1.8, 0.4)])
    desc = lambda y, meio: "embaixo (tapava rosto)" if meio else "em cima"
    print(f"  gancho: {desc(y_g, baixo_g)} | cta: {desc(y_c, baixo_c)}")
    if so_checar:
        return {"gancho_baixo": baixo_g, "cta_baixo": baixo_c}

    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
                            *PLAT.h264("14M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", tmp_v],
                           stdin=subprocess.PIPE)
    # 3) renderiza
    camadas = preparar_brolls(cortes, OUT_W, OUT_H)
    n_out, gi = 0, 0
    for ci, c in enumerate(cortes):
        frac, ts, xy = planos[ci]
        # região que cobre todos os crops desse corte: o ffmpeg já entrega só ela (menos dados no pipe)
        caixas = [caixa(x, y, frac, W, H) for x, y in xy]
        bx0 = min(b[0] for b in caixas) // 2 * 2
        by0 = min(b[1] for b in caixas) // 2 * 2
        bx1 = min(W, max(b[0] + b[2] for b in caixas) + 2) // 2 * 2
        by1 = min(H, max(b[1] + b[3] for b in caixas) + 2) // 2 * 2
        bw, bh = bx1 - bx0, by1 - by0
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal"] + ent_args + ["-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s'] + 0.2:.3f}",
                                "-i", video, "-vf", f"{ent_filtro}crop={bw}:{bh}:{bx0}:{by0},fps={FPS}",
                                "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
        fsize, fi = bw * bh * 3, 0
        for buf in quadros(dec, fsize, n_quadros(c)):
            fr = np.frombuffer(buf, np.uint8).reshape(bh, bw, 3)
            tl = fi / FPS
            cx, cy = np.interp(tl, ts, xy[:, 0]), np.interp(tl, ts, xy[:, 1])
            x0, y0, cw, ch = caixa(cx, cy, frac, W, H)
            x0 = int(np.clip(x0 - bx0, 0, bw - cw)); y0 = int(np.clip(y0 - by0, 0, bh - ch))
            out = cv2.resize(fr[y0:y0 + ch, x0:x0 + cw], (OUT_W, OUT_H), interpolation=cv2.INTER_AREA)
            base_ult = out.copy()
            t = n_out / FPS
            com_motion = aplicar_brolls(out, camadas, t) > 0.5      # motion na tela: sem legenda competindo
            while gi < len(grupos) - 1 and t >= grupos[gi][-1]["e"] + 0.25 and t >= grupos[gi + 1][0]["s"]:
                gi += 1
            g = grupos[gi] if grupos and grupos[gi][0]["s"] <= t < grupos[gi][-1]["e"] + 0.25 else None
            mostra_g = img_gancho is not None and t < seg_gancho
            mostra_c = img_cta is not None and t > total - seg_cta
            ocupa_leg = (mostra_g and baixo_g) or (mostra_c and baixo_c)
            if g and not ocupa_leg and not com_motion:
                ativo = max((i for i, p in enumerate(g) if p["s"] <= t), default=0)
                colar(out, leg.render(gi, g, ativo), y_leg)
            if mostra_g:
                colar(out, img_gancho, y_g)
            if mostra_c:
                colar(out, img_cta, y_c)
            enc.stdin.write(out.tobytes())
            fi, n_out = fi + 1, n_out + 1
        dec.wait()
        print(f"  corte {ci + 1}/{len(cortes)} ok")
    escrever_cauda(enc, base_ult, camadas, n_out)
    enc.stdin.close(); enc.wait()

    montar_audio(video, cortes, tmp_v, saida, sfx=[(b.arq, b.t0) for b in camadas])
    return total


def loudness(path):
    """volume integrado (LUFS) do áudio do arquivo."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(m[-1]) if m else -14.0


def montar_audio(video, cortes, tmp_v, saida, vinheta=None, seg_vinheta=0.0, sfx=()):
    """junta o áudio dos mesmos cortes (fade curtinho), equaliza vozes, -14 LUFS, e muxa com o vídeo."""
    partes, filtros = [], []
    for i, c in enumerate(cortes):
        d = c["e"] - c["s"]
        fade = ("" if c.get("continua") else ",afade=t=in:d=0.02") + \
               ("" if i + 1 < len(cortes) and cortes[i + 1].get("continua") else f",afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03")
        filtros.append(f"[0:a]atrim={c['s']:.4f}:{c['e']:.4f},asetpts=PTS-STARTPTS{fade}[a{i}]")
        partes.append(f"[a{i}]")
    fc = ";".join(filtros) + f";{''.join(partes)}concat=n={len(cortes)}:v=0:a=1,dynaudnorm=f=250:g=15:p=0.9,loudnorm=I=-14:TP=-1.5:LRA=11"
    if CAUDA:
        fc += f",aresample=48000,apad=pad_dur={CAUDA:.3f}"
    entradas = ["-i", video, "-i", tmp_v]
    if vinheta:                                  # som da vinheta no mesmo volume, e o fim dele por cima do começo da live
        ganho = -14 - loudness(vinheta)
        ms = int(round(seg_vinheta * 1000))
        fc += (f",aresample=48000,adelay={ms}:all=1[live];[2:a]aresample=48000,volume={ganho:.1f}dB[vin];"
               f"[vin][live]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89[aout]")
        entradas += ["-i", vinheta]
    else:
        fc += "[aout]"
    sfx = [(a, t) for a, t in sfx if "audio" in run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
                                                    "-of", "csv=p=0", a])]
    if sfx:                                      # efeitos sonoros das cenas de motion, por baixo da voz
        fc = fc.replace("[aout]", "[voz]")
        base = len(entradas) // 2
        mix = ["[voz]"]
        for k, (arq, t0) in enumerate(sfx):
            entradas += ["-i", arq]
            fc += f";[{base + k}:a]aresample=48000,volume=0.55,adelay={int(round(t0 * 1000))}:all=1[fx{k}]"
            mix.append(f"[fx{k}]")
        fc += f";{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0,alimiter=limit=0.89[aout]"
    run(["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex", fc,
         "-map", "1:v", "-map", "[aout]", "-c:v", "copy",
         "-bsf:v", "h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0",
         "-c:a", "aac", "-b:a", "192k",
         "-ar", "48000", "-shortest", "-movflags", "+faststart", saida])
    os.remove(tmp_v)

# ---------------------------------------------------------------- 5a. corte longo do YouTube
def renderizar_youtube(video, cortes, saida, marca, vinheta=True, so_checar=False, lado=(1920, 1080), inscreva=True):
    """corte longo 16:9: a cena da live inteira (sem recorte, sem legenda, sem gancho), com a vinheta
    da marca na abertura. Grava ao lado um .tempos.txt com o tempo de cada trecho no vídeo final (capítulos)."""
    W, H = lado
    arq_vin = VINHETA.get(marca) if vinheta else None
    seg_vin = 0.0
    if arq_vin:
        seg_vin = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                           "stream=nb_read_frames", "-of", "csv=p=0", arq_vin]).strip()) / FPS
    total = seg_vin + sum(c["e"] - c["s"] for c in cortes)
    print(f"  youtube: {W}x{H} | {len(cortes)} trechos | {total / 60:.1f} min" + (f" | vinheta {seg_vin:.2f}s" if arq_vin else ""))
    with open(os.path.splitext(saida)[0] + ".tempos.txt", "w") as f:
        f.write("# tempo no vídeo final -> tempo na live (use pra montar os capítulos)\n")
        t = seg_vin
        for c in cortes:
            if not c.get("continua"):
                f.write(f"{int(t // 60):02d}:{int(t % 60):02d} -> {int(c['s'] // 60):02d}:{c['s'] % 60:05.2f}  {c['texto'][:70]}\n")
            t += c["e"] - c["s"]
    if so_checar:
        return total
    ent_args, ent_filtro = entrada_video(video)
    escala = f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS},format=bgr24"
    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            *PLAT.h264("12M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", tmp_v], stdin=subprocess.PIPE)
    fsize = W * H * 3
    if arq_vin:
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal", "-i", arq_vin, "-an", "-vf", escala, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for buf in quadros(dec, fsize, int(round(seg_vin * FPS))):
            enc.stdin.write(buf)
        dec.wait()
    for ci, c in enumerate(cortes):
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal"] + ent_args + ["-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s'] + 0.2:.3f}",
                                "-i", video, "-an", "-vf", ent_filtro + escala, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for buf in quadros(dec, fsize, n_quadros(c)):
            enc.stdin.write(buf)
        dec.wait()
        print(f"  trecho {ci + 1}/{len(cortes)} ok")
    enc.stdin.close(); enc.wait()
    montar_audio(video, cortes, tmp_v, saida, vinheta=arq_vin, seg_vinheta=seg_vin)
    if marca == "liv" and inscreva:                # balão "Inscreva-se" ~1/min, nunca em cima do banner da live
        import inscricao
        tmp_i = saida + ".inscreva.mp4"
        inscricao.aplicar(saida, tmp_i)
        os.replace(tmp_i, saida)
    return total


# ---------------------------------------------------------------- 5b. tela dividida (live com duas pessoas lado a lado)
def rostos_por_lado(video, c, fps=2):
    """posição mediana do rosto da esquerda e da direita no corte (webcam: quase parado)."""
    garantir_detector()
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-ss", f"{c['s']:.3f}", "-t", f"{max(0.5, c['e'] - c['s']):.3f}", "-i", video,
         "-vf", f"fps={fps},scale=640:-2", os.path.join(tmp, "%04d.jpg")])
    imgs = sorted(os.listdir(tmp))
    esq, dir_ = [], []
    if imgs:
        for ln in _detectar([os.path.join(tmp, f) for f in imgs]):
            for f in json.loads(ln):
                if f[2] < 0.06:
                    continue
                (esq if f[0] < 0.5 else dir_).append(f[:2])
    shutil.rmtree(tmp)
    med = lambda l, padrao: tuple(np.median(np.array(l), axis=0)) if l else padrao
    return med(esq, (0.25, 0.38)), med(dir_, (0.75, 0.40))


def rostos_por_coluna(video, c, n, fps=2):
    """posição mediana do rosto em cada coluna da live (n pessoas lado a lado, cada uma numa faixa de 1/n)."""
    garantir_detector()
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-ss", f"{c['s']:.3f}", "-t", f"{max(0.5, c['e'] - c['s']):.3f}", "-i", video,
         "-vf", f"fps={fps},scale=960:-2", os.path.join(tmp, "%04d.jpg")])
    imgs = sorted(os.listdir(tmp))
    cols = [[] for _ in range(n)]
    if imgs:
        for ln in _detectar([os.path.join(tmp, f) for f in imgs]):
            for f in json.loads(ln):
                if f[2] < 0.04:
                    continue
                cols[min(n - 1, int(f[0] * n))].append(f[:2])
    shutil.rmtree(tmp)
    return [tuple(np.median(np.array(l), axis=0)) if l else ((k + 0.5) / n, 0.38) for k, l in enumerate(cols)]


def renderizar_dividido(video, cortes, saida, grupos, leg, img_gancho, img_cta, total, seg_gancho, seg_cta,
                        so_checar=False, frac=0.88, cima="esquerda"):
    """uma pessoa em cima, a outra embaixo; legenda e tarja na divisa, sem tapar rosto.
    Enquadramento FIXO no vídeo inteiro (live é câmera parada: zoom ou recorte mexendo fica estranho)."""
    W, H = tamanho_real(video)
    PW, PH = OUT_W, OUT_H // 2
    y_meio = OUT_H // 2
    y_leg = y_meio - 100
    pos_caixa = lambda img: y_meio - img.height // 2

    n_col, pessoas = COLUNAS

    def recorte(face, lado, pos_rosto, frac):
        if isinstance(lado, int):                       # coluna k (1 = esquerda) de uma live com n_col pessoas
            x_min, larg = (lado - 1) * W // n_col, W // n_col
        else:
            x_min, larg = (0 if lado == "esq" else W // 2), W // 2
        cw = int(larg * frac) // 2 * 2
        ch = int(cw * PH / PW) // 2 * 2
        x0 = int(np.clip(face[0] * W - cw / 2, x_min, x_min + larg - cw))
        # a faixa de baixo da live tem comentários do chat e banners: o recorte fica acima dela
        y_max = max(0, int(H * LIMITE_SOBREPOSICAO) - ch)
        y0 = int(np.clip(face[1] * H - pos_rosto * ch, 0, y_max))
        return x0, y0, cw, ch

    if pessoas:                                         # live com n_col pessoas: escolhe as duas da conversa
        amostras = [rostos_por_coluna(video, c, n_col) for c in cortes[::max(1, len(cortes) // 8)]]
        rosto = lambda k: tuple(np.median([a[k - 1] for a in amostras], axis=0))
        # webcam em coluna estreita já é bem fechada: usa a largura toda da coluna e o rosto um pouco acima do meio
        caixas = (recorte(rosto(pessoas[0]), pessoas[0], 0.46, 1.0), recorte(rosto(pessoas[1]), pessoas[1], 0.50, 1.0))
        planos = [caixas] * len(cortes)
        print(f"  tela dividida: {len(cortes)} cortes | live com {n_col} pessoas: coluna {pessoas[0]} em cima, {pessoas[1]} embaixo")
        return _dividido_render(video, cortes, saida, grupos, leg, img_gancho, img_cta, total, seg_gancho, seg_cta,
                                so_checar, planos, W, H, PW, PH, y_leg, pos_caixa)
    # posição média de cada pessoa no vídeo inteiro -> um recorte só por pessoa
    esqs, dirs = [], []
    for c in cortes[::max(1, len(cortes) // 8)]:
        fe, fd = rostos_por_lado(video, c)
        esqs.append(fe); dirs.append(fd)
    fe, fd = tuple(np.median(esqs, axis=0)), tuple(np.median(dirs, axis=0))
    if cima == "esquerda":
        caixa_cima, caixa_baixo = recorte(fe, "esq", 0.42, frac), recorte(fd, "dir", 0.56, frac)
    else:
        caixa_cima, caixa_baixo = recorte(fd, "dir", 0.42, frac), recorte(fe, "esq", 0.56, frac)
    planos = [(caixa_cima, caixa_baixo)] * len(cortes)
    print(f"  tela dividida: {len(cortes)} cortes | pessoa da {cima} em cima | enquadramento fixo")
    return _dividido_render(video, cortes, saida, grupos, leg, img_gancho, img_cta, total, seg_gancho, seg_cta,
                            so_checar, planos, W, H, PW, PH, y_leg, pos_caixa)


def _dividido_render(video, cortes, saida, grupos, leg, img_gancho, img_cta, total, seg_gancho, seg_cta,
                     so_checar, planos, W, H, PW, PH, y_leg, pos_caixa):
    if so_checar:
        return {}

    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
                            *PLAT.h264("14M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", tmp_v], stdin=subprocess.PIPE)
    camadas = preparar_brolls(cortes, OUT_W, OUT_H)
    n_out, gi = 0, 0
    for ci, c in enumerate(cortes):
        (ax, ay, aw, ah), (bx, by, bw, bh) = planos[ci]
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal", "-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s'] + 0.2:.3f}",
                                "-i", video, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE)
        fsize = W * H * 3
        for buf in quadros(dec, fsize, n_quadros(c)):
            fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            cima = cv2.resize(fr[ay:ay + ah, ax:ax + aw], (PW, PH), interpolation=cv2.INTER_CUBIC)
            baixo = cv2.resize(fr[by:by + bh, bx:bx + bw], (PW, PH), interpolation=cv2.INTER_CUBIC)
            out = np.vstack([cima, baixo])
            base_ult = out.copy()
            t = n_out / FPS
            com_motion = aplicar_brolls(out, camadas, t) > 0.5      # motion na tela: sem legenda competindo
            while gi < len(grupos) - 1 and t >= grupos[gi][-1]["e"] + 0.25 and t >= grupos[gi + 1][0]["s"]:
                gi += 1
            g = grupos[gi] if grupos and grupos[gi][0]["s"] <= t < grupos[gi][-1]["e"] + 0.25 else None
            mostra_g = img_gancho is not None and t < seg_gancho
            mostra_c = img_cta is not None and t > total - seg_cta
            if g and not (mostra_g or mostra_c) and not com_motion:
                ativo = max((i for i, p in enumerate(g) if p["s"] <= t), default=0)
                colar(out, leg.render(gi, g, ativo), y_leg)
            if mostra_g:
                colar(out, img_gancho, pos_caixa(img_gancho))
            if mostra_c:
                colar(out, img_cta, pos_caixa(img_cta))
            enc.stdin.write(out.tobytes())
            n_out += 1
        dec.wait()
        print(f"  corte {ci + 1}/{len(cortes)} ok")
    escrever_cauda(enc, base_ult, camadas, n_out)
    enc.stdin.close(); enc.wait()
    montar_audio(video, cortes, tmp_v, saida, sfx=[(b.arq, b.t0) for b in camadas])
    return total


# ---------------------------------------------------------------- 5c. quadro inteiro (live com uma pessoa, câmera parada)
def renderizar_quadro(video, cortes, saida, grupos, leg, img_gancho, img_cta, total, seg_gancho, seg_cta,
                      so_checar=False, altura=0.66, largura=0.58):
    """imagem da live nítida no meio, fundo desfocado da própria cena; gancho acima e legenda abaixo.
    Enquadramento fixo. Mostra só até 'altura' da imagem (abaixo disso a live exibe chat e banners)."""
    W, H = tamanho_real(video)
    xs = []
    for c in cortes[::max(1, len(cortes) // 8)]:
        fe, fd = rostos_por_lado(video, c)
        xs += [fe[0], fd[0]]
    cx = float(np.median(xs)) * W if xs else W / 2
    cw = int(W * largura) // 2 * 2
    ch = int(H * altura) // 2 * 2
    x0 = int(np.clip(cx - cw / 2, 0, W - cw))
    mh = int(OUT_W * ch / cw) // 2 * 2                    # altura do quadro nítido na tela
    y_q = (OUT_H - mh) // 2 - 60                          # um pouco acima do centro
    y_leg = y_q + mh + 30
    pos_g = lambda img: max(260, y_q - img.height - 40)
    # fundo: recorte vertical da própria cena, desfocado e escurecido
    fw = int(H * 9 / 16) // 2 * 2
    fx0 = int(np.clip(cx - fw / 2, 0, W - fw))
    print(f"  quadro inteiro: {len(cortes)} cortes | recorte {cw}x{ch} | enquadramento fixo")
    if so_checar:
        return {}
    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
                            *PLAT.h264("14M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", tmp_v], stdin=subprocess.PIPE)
    camadas = preparar_brolls(cortes, OUT_W, OUT_H)
    n_out, gi = 0, 0
    for ci, c in enumerate(cortes):
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal", "-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s'] + 0.2:.3f}",
                                "-i", video, "-vf", f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE)
        fsize = W * H * 3
        for buf in quadros(dec, fsize, n_quadros(c)):
            fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            fundo = cv2.resize(fr[:, fx0:fx0 + fw], (135, 240), interpolation=cv2.INTER_AREA)
            fundo = cv2.GaussianBlur(fundo, (0, 0), 6)
            out = (cv2.resize(fundo, (OUT_W, OUT_H), interpolation=cv2.INTER_LINEAR) * 0.5).astype(np.uint8)
            out[y_q:y_q + mh] = cv2.resize(fr[:ch, x0:x0 + cw], (OUT_W, mh), interpolation=cv2.INTER_CUBIC)
            base_ult = out.copy()
            t = n_out / FPS
            com_motion = aplicar_brolls(out, camadas, t) > 0.5      # motion na tela: sem legenda nem gancho por cima
            while gi < len(grupos) - 1 and t >= grupos[gi][-1]["e"] + 0.25 and t >= grupos[gi + 1][0]["s"]:
                gi += 1
            g = grupos[gi] if grupos and grupos[gi][0]["s"] <= t < grupos[gi][-1]["e"] + 0.25 else None
            if g and not com_motion:
                ativo = max((i for i, p in enumerate(g) if p["s"] <= t), default=0)
                colar(out, leg.render(gi, g, ativo), y_leg)
            if img_gancho is not None and t < seg_gancho and not com_motion:
                colar(out, img_gancho, pos_g(img_gancho))
            if img_cta is not None and t > total - seg_cta and not com_motion:
                colar(out, img_cta, pos_g(img_cta))
            enc.stdin.write(out.tobytes())
            n_out += 1
        dec.wait()
        print(f"  corte {ci + 1}/{len(cortes)} ok")
    escrever_cauda(enc, base_ult, camadas, n_out)
    enc.stdin.close(); enc.wait()
    montar_audio(video, cortes, tmp_v, saida, sfx=[(b.arq, b.t0) for b in camadas])
    return total


# ---------------------------------------------------------------- 5d. quadrado (WhatsApp), câmera em tripé
def rosto_principal(video, cortes, por_corte=3):
    """posição mediana (x, y normalizados) do maior rosto ao longo dos cortes."""
    garantir_detector()
    tmp = tempfile.mkdtemp()
    for i, c in enumerate(cortes[::max(1, len(cortes) // 10)]):
        for k, t in enumerate(np.linspace(c["s"], c["e"], por_corte + 2)[1:-1]):
            subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                            "-vf", "scale=640:-2", os.path.join(tmp, f"{i:03d}_{k}.jpg")])
    imgs = sorted(os.listdir(tmp))
    pts = []
    for ln in (_detectar([os.path.join(tmp, f) for f in imgs]) if imgs else []):
        faces = json.loads(ln)
        if faces:
            f = max(faces, key=lambda f: f[2]); pts.append(f[:2])
    shutil.rmtree(tmp)
    return tuple(np.median(np.array(pts), axis=0)) if pts else (0.5, 0.35)


def ponto_de_fuga(video, cortes):
    """ponto onde as verticais da cena (portas, paredes, prateleiras) se encontram, em frações da largura.
    Com câmera inclinada as verticais abrem em leque; o editor gira pelo ângulo da vertical na posição do rosto."""
    import math
    tmp = tempfile.mkdtemp()
    for i, c in enumerate(cortes[::max(1, len(cortes) // 5)]):
        subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{(c['s'] + c['e']) / 2:.2f}", "-i", video,
                        "-frames:v", "1", "-vf", "scale=1920:-2", os.path.join(tmp, f"{i}.png")])
    L = []
    for f in sorted(os.listdir(tmp)):
        g = cv2.cvtColor(cv2.imread(os.path.join(tmp, f)), cv2.COLOR_BGR2GRAY)
        h, w = g.shape
        achadas = cv2.HoughLinesP(cv2.Canny(g, 50, 150), 1, np.pi / 1440, 80, minLineLength=h * 0.14, maxLineGap=5)
        for x1, y1, x2, y2 in (achadas[:, 0] if achadas is not None else []):
            if abs(y2 - y1) > abs(x2 - x1) * 4:                     # quase vertical
                L.append((x1 / w, y1 / w, x2 / w, y2 / w))
    shutil.rmtree(tmp)
    if len(L) < 6:
        return None
    L = np.array(L)
    usar = np.ones(len(L), bool)
    for _ in range(5):                                             # mínimos quadrados, descartando as linhas que não batem
        d = L[:, 2:] - L[:, :2]
        comp = np.linalg.norm(d, axis=1)
        n = np.stack([-d[:, 1], d[:, 0]], 1) / comp[:, None]
        pw = np.sqrt(comp[usar])
        v = np.linalg.lstsq(n[usar] * pw[:, None], (n * L[:, :2]).sum(1)[usar] * pw, rcond=None)[0]
        t = v - (L[:, :2] + L[:, 2:]) / 2
        erro = np.degrees(np.abs(np.arctan2(d[:, 0] * t[:, 1] - d[:, 1] * t[:, 0], (d * t).sum(1))))
        erro = np.minimum(erro, 180 - erro)
        usar = erro < max(1.0, np.percentile(erro[usar], 70))
    print(f"  endireitar: fuga das verticais em ({v[0]:.2f}, {v[1]:.2f}) larguras, {usar.sum()}/{len(L)} linhas")
    return v


def renderizar_quadrado(video, cortes, saida, grupos, marca, img_gancho, img_cta, total, seg_gancho, seg_cta,
                        so_checar=False, girar=0.0, lado_px=1080, frac=0.85, dinamico=False, endireitar=False):
    """vídeo quadrado 1080x1080, enquadramento dinâmico (punch-in por bloco), com correção de câmera torta (girar em graus).
    Legenda na cor da marca, perto da base, sem cobrir o rosto."""
    W, H = tamanho_real(video)
    import math
    margem = 8
    ent_args, ent_filtro = entrada_video(video)     # iPhone em HDR: converte pra SDR como nos outros layouts
    if endireitar:                                  # só GIRA: nunca distorcer a imagem (perspectiva deformava o rosto)
        v = ponto_de_fuga(video, cortes)
        if v is not None:
            fx, fy = rosto_principal(video, cortes)
            girar = round(math.degrees(math.atan((fx - v[0]) / (v[1] - fy * H / W))), 2)   # vertical reta na altura do rosto
            print(f"  endireitar: girando {girar:+.2f}°")
    a_rad = math.radians(girar)
    # não é live: punch-in alternando por bloco de fala e enquadramento refeito em cada bloco
    planos, ult_g = [], None
    for ci, c in enumerate(cortes):
        g = c.get("grupo", ci)
        if g != ult_g:
            irmaos = [x for x in cortes if x.get("grupo", -1) == g] or [c]
            fx, fy = rosto_principal(video, irmaos, por_corte=2)
            dx, dy = fx * W - W / 2, fy * H - H / 2           # posição do rosto depois de girar (anti-horário)
            cx = W / 2 + dx * math.cos(a_rad) + dy * math.sin(a_rad)
            cy = H / 2 - dx * math.sin(a_rad) + dy * math.cos(a_rad)
            ult_g = g
        niveis = (1.0, 0.70, 0.84) if dinamico else (1.0, 0.80)     # aberto, fechado, médio
        f = frac * niveis[g % len(niveis)]
        lado = int(H * f) // 2 * 2                                    # lado do recorte na imagem original
        folga = int(lado * math.sin(abs(a_rad))) + margem              # rotação: não deixa canto preto
        x0 = int(np.clip(cx - lado / 2, folga, W - lado - folga)) // 2 * 2
        y0 = int(np.clip(cy - lado * (0.34 if f < frac else 0.30), folga, H - lado - folga)) // 2 * 2
        planos.append((lado, x0, y0))
    print(f"  quadrado: {len(cortes)} cortes | girar {girar:+.1f}° | zoom alternando por bloco")
    if so_checar:
        return {}
    leg = Legenda(marca, tam=30)
    y_leg = int(lado_px * 0.84) - 100
    # o rotate do ffmpeg gira no sentido horário: sinal invertido pra "positivo = anti-horário"
    gira = f"rotate={-a_rad:.5f}:fillcolor=black," if girar else ""
    tmp_v = saida + ".video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                            "-s", f"{lado_px}x{lado_px}", "-r", str(FPS), "-i", "-",
                            *PLAT.h264("6M"), "-pix_fmt", "yuv420p",
                            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                            "-color_range", "tv", tmp_v], stdin=subprocess.PIPE)
    n_out, gi = 0, 0
    fsize = lado_px * lado_px * 3
    for ci, c in enumerate(cortes):
        lado, x0, y0 = planos[ci]
        filtro = ent_filtro + gira + f"crop={lado}:{lado}:{x0}:{y0},scale={lado_px}:{lado_px}:flags=lanczos,fps={FPS}"
        dec = subprocess.Popen(["ffmpeg", "-v", "fatal"] + ent_args + ["-ss", f"{c['s']:.3f}", "-t", f"{c['e'] - c['s'] + 0.2:.3f}",
                                "-i", video, "-vf", filtro, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                               stdout=subprocess.PIPE)
        for buf in quadros(dec, fsize, n_quadros(c)):
            out = np.frombuffer(buf, np.uint8).reshape(lado_px, lado_px, 3).copy()
            t = n_out / FPS
            while gi < len(grupos) - 1 and t >= grupos[gi][-1]["e"] + 0.25 and t >= grupos[gi + 1][0]["s"]:
                gi += 1
            g = grupos[gi] if grupos and grupos[gi][0]["s"] <= t < grupos[gi][-1]["e"] + 0.25 else None
            if g:
                ativo = max((i for i, p in enumerate(g) if p["s"] <= t), default=0)
                colar(out, leg.render(gi, g, ativo), y_leg)
            if img_gancho is not None and t < seg_gancho:
                colar(out, img_gancho, 40)
            if img_cta is not None and t > total - seg_cta:
                colar(out, img_cta, 40)
            enc.stdin.write(out.tobytes())
            n_out += 1
        dec.wait()
        print(f"  corte {ci + 1}/{len(cortes)} ok")
    enc.stdin.close(); enc.wait()
    montar_audio(video, cortes, tmp_v, saida)
    return total


# ---------------------------------------------------------------- 6. animações (HyperFrames, render sempre local)
MOTION = os.path.join(os.path.dirname(AQUI), "motion")


def renderizar_modelo(modelo, variaveis, saida):
    """renderiza um modelo de motion/modelos/ em MOV com transparência (ProRes 4444)."""
    env = dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", HYPERFRAMES_SKIP_SKILLS="1")
    if not os.path.exists(os.path.join(MOTION, "node_modules")):
        subprocess.run([PLAT.cmd("npm"), "install", "--no-fund", "--no-audit"], cwd=MOTION, env=env, check=True)
    r = subprocess.run([PLAT.cmd("npx"), "hyperframes", "render", ".", "-c", f"modelos/{modelo}.html", "--format", "mov",
                        "--variables", json.dumps(variaveis, ensure_ascii=False), "-o", saida, "--quiet"],
                       cwd=MOTION, env=env, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(saida):
        sys.exit(f"Erro no render da animação {modelo}:\n{(r.stderr or r.stdout)[-1500:]}")
    return saida


def aplicar_animacoes(saida, animacoes):
    """cola as animações transparentes (arquivo, segundo) no vídeo pronto; o áudio não é tocado."""
    W, H = tamanho_real(saida)
    entradas, cadeia, ult = ["-i", saida], [], "0:v"
    for k, (arq, t) in enumerate(animacoes, 1):
        aw, ah = tamanho_real(arq)
        if abs(aw / ah - W / H) > 0.01:
            sys.exit(f"A animação {arq} é {aw}x{ah} e o vídeo {W}x{H}: proporções diferentes (nunca distorcer).")
        entradas += ["-i", arq]
        cadeia.append(f"[{k}:v]scale={W}:{H}:flags=lanczos,format=yuva444p,setpts=PTS+{t:.3f}/TB[m{k}];"
                      f"[{ult}][m{k}]overlay=0:0:eof_action=pass:format=auto[v{k}]")
        ult = f"v{k}"
    tmp = saida + ".motion.mp4"
    run(["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex", ";".join(cadeia), "-map", f"[{ult}]", "-map", "0:a",
         *PLAT.h264("14M"), "-pix_fmt", "yuv420p",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
         "-c:a", "copy", "-movflags", "+faststart", tmp])
    os.replace(tmp, saida)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Editor automático de Reels")
    ap.add_argument("video")
    ap.add_argument("--marca", choices=MARCAS, default="imigrar")
    ap.add_argument("--gancho", default="", help="texto no topo nos primeiros 3s")
    ap.add_argument("--cta", default="", help="texto no topo nos últimos 3,5s")
    ap.add_argument("--trechos", help='faixas do original em segundos, ex: "124-166.6,1048-1053"')
    ap.add_argument("--comecar")
    ap.add_argument("--terminar")
    ap.add_argument("--remover", action="append", default=[])
    ap.add_argument("--pessoa", choices=["esquerda", "direita", "voz"],
                    help="cena com duas pessoas: fecha nessa. 'voz': conversa, fecha em quem fala (esquerda=grave, 2a=aguda)")
    ap.add_argument("--aperto", type=float, help="fração da largura original mantida (menor = mais fechado)")
    ap.add_argument("--manter-perguntas", action="store_true", help="não tira as falas que terminam em ?")
    ap.add_argument("--pergunta", help='faixas que são a pergunta do entrevistador (ficam em quadro aberto), ex: "169.8-173.5"')
    ap.add_argument("--trocar", action="append", default=[], help='corrige a legenda: "um gente sério=com gente séria"')
    ap.add_argument("--nome", help="nome do arquivo final (sem extensão)")
    ap.add_argument("--saida", default=PLAT.pasta_renders("prontos"), help="pasta do arquivo final (padrão: Mesa/Editor Reels/prontos)")
    ap.add_argument("--so-cortes", action="store_true", help="só mostra o plano de cortes")
    ap.add_argument("--sem-ajuste-audio", action="store_true", help="não corta pelo áudio (usa só o tempo do Whisper)")
    ap.add_argument("--checar-olhar", action="store_true", help="avisa trechos em que a pessoa olha pra baixo (lendo) ou pro lado")
    ap.add_argument("--cor-caixa", choices=sorted({e for m in ESTILOS_CAIXA.values() for e in m}),
                    help="estilo da tarja do gancho/CTA. Imigrar: branco, azul, rosa. LIV: azul, laranja, bege, marrom")
    ap.add_argument("--colunas", type=int, default=2, help="tela dividida: quantas pessoas lado a lado na live (ex.: 3)")
    ap.add_argument("--pessoas", help='tela dividida com --colunas: quem vai em cima e embaixo, pela coluna da live (1 = esquerda), ex: "3,1"')
    ap.add_argument("--cima", choices=["esquerda", "direita"], default="esquerda",
                    help="tela dividida: quem da live vai em cima (a pessoa da esquerda ou da direita)")
    ap.add_argument("--endireitar", action="store_true", help="quadrado: mede as verticais da cena e escolhe o ângulo de --girar sozinho (só gira, não distorce)")
    ap.add_argument("--tirar", action="append", default=[], help='tira um trecho exato do bruto, ex: "96.52-97.07" (gagueira, travada). Pode repetir')
    ap.add_argument("--dinamico", action="store_true", help="troca o zoom a cada ~2,5s (entre palavras), com 3 níveis")
    ap.add_argument("--respiro", type=float, help="mantém pausas internas até esse tamanho (s). Padrão 0.25; fala mais natural: 0.5")
    ap.add_argument("--girar", type=float, default=0.0, help="corrige câmera torta: graus (positivo = anti-horário)")
    ap.add_argument("--layout", choices=["dividido", "quadro", "quadrado", "youtube"],
                    help="dividido: live com duas pessoas; quadro: live solo 720p; quadrado: WhatsApp; youtube: corte longo 16:9")
    ap.add_argument("--json-palavras", metavar="ARQ", help="salva cada palavra com o tempo no vídeo pronto (JSON) e sai")
    ap.add_argument("--json-cortes", metavar="ARQ", help="salva o plano de cortes (início/fim no bruto) e sai")
    ap.add_argument("--tempos-palavras", action="store_true",
                    help="só mostra cada palavra com o tempo no vídeo pronto (pra sincronizar o motion) e sai")
    ap.add_argument("--tirar-hesitacoes", action="store_true",
                    help='tira "éé", "hmm", "e..." esticado, "então, assim" com pausa e voz sem palavra (mostra o que tirou)')
    ap.add_argument("--cauda", type=float, default=0.0,
                    help="segundos extras no fim, depois da última fala (último quadro parado): espaço do CTA animado")
    ap.add_argument("--sem-legenda", action="store_true",
                    help="não queima legenda (use só quando o vídeo de origem JÁ tem legenda gravada: senão duplica)")
    ap.add_argument("--broll", action="append", default=[],
                    help='cena de motion por cima da imagem (embaixo da legenda), com os efeitos sonoros dela: '
                         '"arquivo.mov@12.5" (tempo do vídeo pronto) ou "arquivo.mov@fonte:8.4" (tempo da fala no bruto)')
    ap.add_argument("--animacao", action="append", default=[],
                    help='animação transparente (.mov/.webm) colada no vídeo: "arquivo.mov@12.5". Pode repetir')
    ap.add_argument("--cta-animado", metavar="PALAVRA",
                    help='CTA animado da marca no fim ("Comente PALAVRA"). Substitui a caixa --cta')
    ap.add_argument("--cta-rotulo", default="Comente", help="texto antes da palavra no --cta-animado")
    ap.add_argument("--sem-vinheta", action="store_true", help="youtube: não põe a vinheta da marca na abertura")
    ap.add_argument("--sem-inscreva", action="store_true", help="youtube (LIV): não põe o balão Inscreva-se")
    ap.add_argument("--y-legenda", type=float, default=0.62, help="altura da legenda (fração da tela). Anúncio: 0.55")
    ap.add_argument("--so-checar-caixas", action="store_true", help="só diz se o gancho/CTA taparia um rosto")
    a = ap.parse_args()
    global HESITACOES, COLUNAS
    HESITACOES = a.tirar_hesitacoes
    if a.pessoas:
        COLUNAS = (a.colunas, tuple(int(x) for x in a.pessoas.split(",")))

    base = os.path.splitext(os.path.basename(a.video))[0]
    cache_dir = os.path.join(AQUI, "transcricoes")
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(a.saida, exist_ok=True)
    if not os.path.exists(a.video):
        sys.exit(f"Não achei o vídeo: {a.video}")
    if "audio" not in run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type", "-of", "csv=p=0", a.video]):
        sys.exit(f"O vídeo não tem áudio: {a.video}")
    dados = transcrever(a.video, os.path.join(cache_dir, base + ".json"))
    forcar = {}
    trechos = None
    perguntas_inline = []
    if a.trechos:
        trechos = []
        for x in a.trechos.split(","):
            faixa, _, quem = x.partition("@")
            if faixa.endswith("?"):                      # "a-b?" = pergunta do entrevistador nessa posição
                faixa = faixa[:-1]
                perguntas_inline.append(tuple(map(float, faixa.split("-"))))
            t = tuple(map(float, faixa.split("-")))
            trechos.append(t)
            if quem:
                forcar[t] = int(quem)
    if not trechos and not a.comecar and dados["segmentos"] and dados["segmentos"][0]["t"].endswith("?"):
        pass  # a primeira pergunta já sai pelo filtro de perguntas
    perguntas = [tuple(map(float, x.split("-"))) for x in a.pergunta.split(",")] if a.pergunta else []
    ordem = perguntas + (trechos or [])
    perguntas = perguntas + perguntas_inline
    if trechos or perguntas:
        # respeita a ordem escrita (pergunta, resposta, outra pergunta... podem estar fora de ordem)
        cortes = []
        for t in ordem:
            novos = plano_de_cortes(dados, a.comecar, a.terminar, a.remover, [t], perguntas=perguntas,
                                    tirar_perguntas=False)
            for c in novos:
                if t in forcar:
                    c["quem"] = forcar[t]
            cortes += novos
    else:
        cortes = plano_de_cortes(dados, a.comecar, a.terminar, a.remover,
                                 tirar_perguntas=not a.manter_perguntas)
    if a.layout == "youtube" and not a.respiro:
        a.respiro = 0.8                           # corte longo: só tira silêncio de verdade, a conversa fica natural
    if a.respiro:
        # respiro maior (fala mais pausada) solta a folga; menor que o padrão (shorts) aperta
        RESPIRO.update({"pausa_max": a.respiro,
                        "depois": 0.08 if a.respiro < 0.25 else min(0.25, 0.10 + (a.respiro - 0.25) / 2)})
    if not a.sem_ajuste_audio:
        cortes = refinar_cortes(a.video, cortes, dados["palavras"])
    if not cortes:
        sys.exit("Nenhum trecho sobrou depois dos cortes.")
    for x in a.tirar:
        cortes = tirar_trecho(cortes, dados["palavras"], *map(float, x.split("-")))
    if a.tirar_hesitacoes:
        cortes = tirar_hesitacoes(cortes, dados["palavras"])
    fim_video = duracao(a.video)                  # a folga do corte pelo áudio não passa do fim do arquivo
    for c in cortes:
        c["e"] = min(c["e"], fim_video)
    if a.dinamico:
        cortes = dividir_pra_zoom(cortes, dados["palavras"])

    dur = sum(c["e"] - c["s"] for c in cortes)
    print(f"\nPlano: {len(cortes)} cortes, {dur:.1f}s (original {duracao(a.video):.1f}s)")
    for c in cortes:
        aviso = ""
        if a.checar_olhar:
            fr = olhando_pra_baixo(a.video, c["s"], c["e"])
            aviso = f"  [olhando pra baixo/lado {fr:.0%}]" if fr > 0.4 else ""
        print(f"  {c['s']:7.2f}-{c['e']:7.2f}  {c['texto'][:80]}{aviso}")
    if a.json_palavras:                           # pro motion sincronizar o texto palavra por palavra com a fala
        P = dados["palavras"]
        lista = [{"w": P[q]["w"], "t": round(tempo_na_saida(cortes, max(P[q]["s"], c["s"])), 3)} for c in cortes for q in c["idx"]]
        json.dump(lista, open(a.json_palavras, "w"), ensure_ascii=False)
        print(f"{len(lista)} palavras salvas em {a.json_palavras}")
        return
    if a.json_cortes:                             # plano final (pra remapear roteiros de motion quando o corte muda)
        json.dump([{"s": c["s"], "e": c["e"]} for c in cortes], open(a.json_cortes, "w"))
        print(f"plano salvo em {a.json_cortes}")
        return
    if a.tempos_palavras:                         # pro motion: cada palavra no tempo do vídeo pronto
        P = dados["palavras"]
        total = sum(c["e"] - c["s"] for c in cortes)
        print(f"\nDURACAO {total:.2f}")
        for c in cortes:
            for q in c["idx"]:
                print(f"{tempo_na_saida(cortes, max(P[q]['s'], c['s'])):7.2f} {P[q]['w']}")
        return
    if a.so_cortes:
        return
    nome = a.nome or f"{base}_{a.marca}"
    saida = os.path.abspath(os.path.join(a.saida, nome + ".mp4"))
    print("\nRenderizando...")
    global SEM_LEGENDA, CAUDA
    SEM_LEGENDA = a.sem_legenda
    CAUDA = a.cauda
    for x in a.broll:
        arq, _, quando = x.rpartition("@")
        BROLLS.append((os.path.abspath(arq), quando))
    renderizar(a.video, cortes, dados, saida, a.marca, a.gancho, "" if a.cta_animado else a.cta, a.pessoa, frac_base=a.aperto, trocas=a.trocar,
               so_checar=a.so_checar_caixas, y_legenda=a.y_legenda, estilo_caixa=a.cor_caixa, layout=a.layout, cima=a.cima, girar=a.girar,
               dinamico=a.dinamico, endireitar=a.endireitar, vinheta=not a.sem_vinheta, inscreva=not a.sem_inscreva)
    animacoes = []
    for x in a.animacao:
        arq, _, t = x.rpartition("@")
        animacoes.append((arq, float(t)))
    if a.cta_animado and not a.so_checar_caixas:
        print("Renderizando o CTA animado...")
        arq = renderizar_modelo("cta_palavra_chave", {"marca": a.marca, "rotulo": a.cta_rotulo,
                                                      "palavra": a.cta_animado.upper()}, saida + ".cta.mov")
        animacoes.append((arq, max(0.0, duracao(saida) - 4.2)))
    if animacoes and not a.so_checar_caixas:
        aplicar_animacoes(saida, animacoes)
        if a.cta_animado:
            os.remove(saida + ".cta.mov")
    if not a.so_checar_caixas:
        print(f"\nPronto: {saida}")


if __name__ == "__main__":
    main()
