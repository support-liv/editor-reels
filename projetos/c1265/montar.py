#!/usr/bin/env python3
"""Entrevista Dra. Lívia (C1265, 4K): ajuste de status x processo consular. Vídeo longo produzido para o YouTube.

    python3 projetos/c1265/montar.py            # monta o corte (sem títulos) e grava capitulos.json
    python3 projetos/c1265/montar.py --previas  # + prévias dos títulos de capítulo
    python3 projetos/c1265/montar.py --final    # + títulos de capítulo -> Mesa/Editor Reels/C1265

Decisões (06/10/2026):
- cada pergunta ganha uma cartela própria de 4s: degradê sólido da LIV (sem vídeo atrás), a pergunta como foi feita,
  som de entrada suave e a trilha mais presente; passa para a resposta com um light leak (som dele bem baixo);
- fala limpa: sem muletas, recomeços e restos de frase; cada corte cai no ponto mais silencioso entre as palavras;
- três enquadramentos (aberto, médio, close) trocando a cada corte, para o corte não parecer pulo;
- câmera ~2,5° torta corrigida só girando; o plano aberto fecha um pouco para tirar o softbox do canto.
"""
import json, os, subprocess, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, os.path.join(RAIZ, "editor"))
import plataforma as PLAT

BRUTO = os.path.expanduser("~/Downloads/C1265.MP4")
TRANSCRICAO = os.path.join(RAIZ, "editor", "transcricoes", "C1265.json")
NOME = "dra_livia_ajuste_ou_consular"
TRAB = PLAT.pasta_cache("c1265")
FPS_Q = 1001 / 30000

# (nome curto para a descrição, destaque, faixas do bruto: só a resposta, sem a pergunta nem os bastidores)
CAPITULOS = [
    # a 1ª tomada (103-113s) foi interrompida (mão na frente da câmera): começa na resposta refeita
    ("Entrar como turista", "e ajustar?", [(119.18, 234.60)]),
    ("A regra", "dos 90 dias", [(311.80, 382.00)]),
    ("Entrou pensando", "em ficar?", [(404.20, 438.95)]),
    ("A pausa", "dos vistos consulares", [(454.06, 523.70)]),
    ("Vale a pena", "o ajuste?", [(547.32, 603.40)]),
    ("Ajuste", "ou consulado?", [(614.18, 615.80), (622.64, 664.80)]),
    ("EB-2 NIW aprovado:", "e agora?", [(706.68, 766.26)]),
    ("O governo está", "mais rigoroso?", [(815.80, 865.12), (876.68, 923.96)]),
    ("O cenário", "mudou?", [(994.04, 1051.10)]),
    ("Se fosse", "imigrar hoje", [(1064.02, 1108.16)]),
]
# na tela: a pergunta como foi feita no vídeo (sem o "Doutora Lívia"), em até 2 linhas, final em laranja
PERGUNTAS = [
    ("Vir para os EUA como turista e, após 90 dias, fazer ajuste de status com o EB-2 NIW", "é muito arriscado?"),
    ("A regra dos 90 dias realmente protege quem entra como turista", "e decide ficar nos EUA?"),
    ("Quem entrou nos EUA como turista já pensando em ficar", "deve se preocupar?"),
    ("A pausa nos vistos consulares", "está perto do fim?"),
    ("Vale a pena", "fazer o ajuste de status?"),
    ("O que está mais seguro hoje:", "ajuste de status ou processo consular?"),
    ("Quem tem um EB-2 NIW aprovado deve priorizar", "o consulado ou o ajuste de status?"),
    ("O governo americano está mais rigoroso com ajustes de status", "de quem entrou como turista?"),
    ("O ajuste de status continua sendo", "uma boa estratégia ou o cenário mudou?"),
    ("Se você fosse imigrar hoje, escolheria", "o processo consular ou o ajuste de status?"),
]
# recomeços, repetições e muletas que saem (tempo das palavras no bruto)
TIRAR = [
    (180.08, 180.20),    # "E..." esticado antes de "além disso"
    (591.84, 594.90),    # "que valem a pena sim fazer um ajuda-estada. O" (recomeçou a frase)
    (647.64, 647.96),    # "existem." repetido antes de "Existem pontos..."
    (721.36, 725.27),    # "Caso essa mesma pessoa esteja nos EUA post" (recomeçou a frase)
    (818.22, 818.40),    # "né,"
    (1064.98, 1065.50),  # "Depende." repetido
]
MULETAS = {"ah", "eh", "ha", "hum", "hm", "hmm", "ahn", "uhm", "uh", "ehh", "ee", "eee", "aa", "né"}

PAUSA_MAX = 0.40     # pausa maior que isso vira corte
PECA_MIN = 1.5       # não corta uma pausa se um dos lados ficar menor que isso
TROCA = 8.0          # pedaço longo troca de plano no fim de uma frase a cada ~8s (sem cortar)
L, A = 3840, 2160
GIRAR = -2.5         # câmera torta: só GIRA, nunca distorce (negativo = anti-horário no ffmpeg)
GIRO = f"rotate={GIRAR}*PI/180:fillcolor=black,"
ABERTO = (3200, 1800, 400, 140)   # fecha 1,2x e desce para a direita: tira o softbox e os cantos pretos do giro
MEDIO, FECHADO = 0.76, 0.56       # largura do plano médio e do close (fração do quadro)
MARGEM = 160
CICLO = ["aberto", "fechado", "medio", "fechado"]

CARTELA = 4.0
LUZES = [os.path.join(RAIZ, "assets", "transicoes", f"FILM BURNS {n}.mp4") for n in (19, 44, 24, 41)]
LUZ_VEL = 1.35       # light leak um pouco acelerado (flash, não arrasta)
LUZ_PICO_DB = -27    # som do light leak: sutil, bem abaixo da fala (-14 LUFS)
SOM_PICO_DB = -25    # som de entrada da cartela
TRILHA = os.path.join(RAIZ, "assets", "trilhas", "corporativo__skylines-anno-domini-beats__99bpm__A-maior.mp3")


def quadro(t):
    """encaixa no quadro exato (29,97 fps): som e imagem não escorregam ao juntar muitos pedaços."""
    return round(round(t / FPS_Q) * FPS_Q, 5)


# ------------------------------------------------------------------ fala limpa
def energia():
    """energia da voz a cada 10 ms (dB) e o limiar de fala."""
    cache = os.path.join(TRAB, "energia.npy")
    if not os.path.exists(cache):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", BRUTO, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                             capture_output=True, check=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        n = len(x) // 160
        e = np.sqrt((x[:n * 160].reshape(n, 160) ** 2).mean(1) + 1e-10)
        np.save(cache, 20 * np.log10(e))
    db = np.load(cache)
    return db, np.percentile(db, 10) + 0.45 * (np.percentile(db, 95) - np.percentile(db, 10))


def silencio_ate(db, lim, t, para, limite):
    """anda de t na direção 'para' (+1/-1) até a voz cair (fim real da palavra), no máximo 'limite' segundos."""
    i, fim = int(t * 100), int((t + para * limite) * 100)
    while i != fim and db[i] > lim - 6:
        i += para
    return i / 100


def voz_isolada(db, lim, e, s):
    """voz sem palavra entre duas palavras, separada delas por silêncio dos dois lados ("é...", "hmm").
    Rabo de palavra e respiração curta não contam (ficam grudados na palavra ou duram menos de 0,2s)."""
    seg = db[int(e * 100):int(s * 100)]
    voz, quieto = seg > lim, seg < lim - 6
    k = 0
    while k < len(seg):
        if voz[k]:
            j = k
            while j < len(seg) and voz[j]:
                j += 1
            if j - k >= 20 and quieto[:k].sum() >= 5 and quieto[j:].sum() >= 5:
                return True
            k = j
        k += 1
    return False


def pedacos():
    w = json.load(open(TRANSCRICAO))["palavras"]
    db, lim = energia()
    norm = lambda s: "".join(ch for ch in s.lower() if ch.isalnum())
    todos = []
    for ci, (_, _, faixas) in enumerate(CAPITULOS):
        primeiro = True
        for a, b in faixas:
            idx = [i for i, x in enumerate(w) if a - 0.05 <= x["s"] <= b + 0.05]
            fora = {i for i in idx if norm(w[i]["w"]) in MULETAS
                    or any(r0 - 0.02 <= (w[i]["s"] + w[i]["e"]) / 2 <= r1 + 0.02 for r0, r1 in TIRAR)}
            # voz sem palavra entre duas palavras ("é...", "hmm" que a transcrição não escreve) também sai
            for i, j in zip(idx, idx[1:]):
                if voz_isolada(db, lim, w[i]["e"], w[j]["s"]):
                    fora.add(("voz", i))
            # blocos de palavras: corta nas palavras tiradas, na voz sem palavra e nas pausas longas
            blocos, atual = [], []
            for k, i in enumerate(idx):
                if i in fora:
                    if atual:
                        blocos.append(atual); atual = []
                    continue
                if atual and (("voz", atual[-1]) in fora or w[i]["s"] - w[atual[-1]]["e"] > PAUSA_MAX):
                    blocos.append(atual); atual = []
                atual.append(i)
            if atual:
                blocos.append(atual)
            # pausa longa com um lado curto: junta (fica a pausa) — corte forçado (palavra tirada) não junta
            forcado = lambda x, y: any(k in fora for k in range(x[-1] + 1, y[0])) or ("voz", x[-1]) in fora
            unidos = []
            for bl in blocos:
                dur = lambda g: w[g[-1]]["e"] - w[g[0]]["s"]
                if unidos and not forcado(unidos[-1], bl) and (dur(bl) < PECA_MIN or dur(unidos[-1]) < PECA_MIN):
                    unidos[-1] += bl
                else:
                    unidos.append(bl)
            for bl in unidos:
                i0, i1 = bl[0], bl[-1]
                ant = w[i0 - 1]["e"] if i0 > 0 else 0
                prox = w[i1 + 1]["s"] if i1 + 1 < len(w) else w[i1]["e"] + 1
                # começo e fim no silêncio de verdade (nunca no meio da palavra), com respiro curto
                ini = max(ant + 0.03, silencio_ate(db, lim, w[i0]["s"], -1, 0.25) - 0.04)
                fim = min(prox - 0.03, silencio_ate(db, lim, w[i1]["e"], +1, 0.30) + 0.06)
                if primeiro:
                    ini = max(ant + 0.03, ini - 0.15)
                    primeiro = False
                ini = max(ant + 0.01, np.floor(ini / FPS_Q) * FPS_Q)
                fim = min(prox - 0.01, np.ceil(fim / FPS_Q) * FPS_Q)
                ini, fim = quadro(ini), quadro(fim)
                if todos and todos[-1]["cap"] == ci and ini < todos[-1]["fim"] < fim:
                    ini = todos[-1]["fim"]          # nunca repete o fim do pedaço anterior
                # troca de plano no fim de uma frase em pedaço longo (sem cortar a fala)
                marcas, ult = [], ini
                for i in bl[:-1]:
                    fecha = w[i]["w"].strip()[-1:] in ".?!," and w[i + 1]["s"] - w[i]["e"] > 0.15
                    if fecha and w[i]["e"] - ult >= TROCA and fim - w[i]["e"] >= TROCA * 0.6:
                        meio = quadro((w[i]["e"] + w[i + 1]["s"]) / 2)
                        marcas.append(meio); ult = meio
                bordas = [ini] + marcas + [fim]
                for j in range(len(bordas) - 1):
                    todos.append({"cap": ci, "ini": bordas[j], "fim": bordas[j + 1],
                                  "corte_ini": j == 0, "corte_fim": j == len(bordas) - 2,
                                  "texto": " ".join(w[i]["w"].strip() for i in bl) if j == 0 else ""})
    return todos


def com_cartelas(ps):
    saida = []
    n = round(CARTELA / FPS_Q)
    for ci in range(len(CAPITULOS)):
        saida.append({"cap": ci, "cartela": True, "ini": 0.0, "fim": round(n * FPS_Q, 5),
                      "corte_ini": True, "corte_fim": True})
        saida += [p for p in ps if p["cap"] == ci]
    return saida


# ------------------------------------------------------------------ enquadramento
def enquadrar(ps):
    """depois da cartela, a resposta começa aberta; a cada corte o plano muda (aberto, close, médio, close...)."""
    quadros = []
    for p in ps:
        if p.get("cartela"):
            quadros.append(None); continue
        q = os.path.join(TRAB, f"rosto_{p['ini']:.2f}.jpg")
        if not os.path.exists(q):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(p['ini'] + p['fim']) / 2:.2f}", "-i", BRUTO,
                            "-frames:v", "1", "-vf", "scale=1280:-2", q], check=True)
        quadros.append(q)
    achados = iter(PLAT.rostos([q for q in quadros if q]))
    rostos = [next(achados) if q else None for q in quadros]
    k_ciclo = 0
    for k, p in enumerate(ps):
        if p.get("cartela"):
            p["plano"], p["crop"] = "cartela", ""
            k_ciclo = 0
            continue
        plano = CICLO[k_ciclo % len(CICLO)]
        k_ciclo += 1
        r = max(rostos[k], key=lambda c: c[2] * c[3]) if rostos[k] else None
        if not r or plano == "aberto":
            p["plano"], p["crop"] = "aberto", f"{GIRO}crop={ABERTO[0]}:{ABERTO[1]}:{ABERTO[2]}:{ABERTO[3]},"
            continue
        frac = FECHADO if plano == "fechado" else MEDIO
        cw = round(L * frac / 2) * 2
        ch = round(cw * 9 / 16 / 2) * 2
        x = min(max(r[0] * L - cw / 2, MARGEM), L - cw - MARGEM)
        y = min(max(r[1] * A - ch * (0.38 if plano == "fechado" else 0.34), MARGEM), A - ch - MARGEM)
        p["plano"], p["crop"] = plano, f"{GIRO}crop={cw}:{ch}:{round(x)}:{round(y)},"
    return ps


# ------------------------------------------------------------------ render
def fundo_cartela():
    import capitulos
    p = os.path.join(TRAB, "cartela_fundo.png")
    capitulos.fundo_solido(1920, 1080).save(p)
    return p


def nome_pedaco(p):
    if p.get("cartela"):
        return f"cartela_{CARTELA:.1f}.mov"
    return f"p_{p['ini']:.3f}_{p['fim']:.3f}_{p['plano']}_{len(p['crop'])}_{p['crop'][-12:].replace(':', '-').rstrip(',')}.mov"


def renderizar_pedacos(ps):
    lista = os.path.join(TRAB, "lista.txt")
    bg = fundo_cartela()
    with open(lista, "w") as f:
        for k, p in enumerate(ps):
            out = os.path.join(TRAB, nome_pedaco(p))
            d = p["fim"] - p["ini"]
            if p.get("cartela"):
                if not os.path.exists(out):     # degradê sólido e silêncio (o som entra depois, com nível fixo)
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30000/1001", "-t", f"{d:.5f}",
                                    "-i", bg, "-f", "lavfi", "-t", f"{d:.5f}", "-i", "anullsrc=r=48000:cl=stereo",
                                    "-vf", "format=yuv420p", *PLAT.h264("24M"), "-c:a", "pcm_s16le", out], check=True)
            elif not os.path.exists(out):
                af = ",".join(["anull"] + (["afade=t=in:d=0.015"] if p["corte_ini"] else [])
                              + ([f"afade=t=out:st={d - 0.025:.3f}:d=0.025"] if p["corte_fim"] else []))
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{p['ini']:.5f}", "-t", f"{d:.5f}", "-i", BRUTO,
                                "-vf", f"{p['crop']}scale=1920:1080:flags=lanczos,format=yuv420p", "-af", af,
                                *PLAT.h264("24M"), "-r", "30000/1001", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
                                out], check=True)
            f.write(f"file '{out}'\n")
            print(f"  pedaço {k + 1}/{len(ps)} ({p['plano']})", flush=True)
    corte = os.path.join(TRAB, "corte.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c:v", "copy",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                    "-movflags", "+faststart", corte], check=True)
    return corte


def cartelas(ps):
    t, faixas = 0.0, []
    for p in ps:
        if p.get("cartela"):
            faixas.append((t, t + p["fim"] - p["ini"]))
        t += p["fim"] - p["ini"]
    return faixas


def com_trilha(corte, faixas):
    """trilha contínua e baixinha por baixo de toda a fala (colchão, ducking leve); nas cartelas sobe ~9 dB, rampas de 0,6s."""
    import trilhas
    colchao = os.path.join(TRAB, "trilha_loop.mp3")
    if not os.path.exists(colchao):      # loop de 56 compassos (6,4s-142,2s) com emendas de 2s (auditor de trilha)
        f, ant = "[0:a]atrim=6.4:142.2,asetpts=PTS-STARTPTS,asplit=5[a][b][c][d][e]", "a"
        for x in "bcde":
            f += f";[{ant}][{x}]acrossfade=d=2:c1=tri:c2=tri[{ant}{x}]"
            ant += x
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", TRILHA, "-filter_complex", f, "-map", "[abcde]",
                        "-c:a", "libmp3lame", "-b:a", "192k", colchao], check=True)
    sobe = "+".join(f"clip(min((t-{a:.2f})/0.6,({b:.2f}-t)/0.6),0,1)" for a, b in faixas)
    moldado = os.path.join(TRAB, "trilha_moldada.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", colchao, "-af", f"volume='1+1.8*({sobe})':eval=frame",
                    moldado], check=True)
    # mixa num vídeo-sombra minúsculo (só a fala): não cria outra cópia de 2 GB do vídeo; devolve o áudio mixado
    sombra = os.path.join(TRAB, "sombra.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", corte, "-f", "lavfi", "-i", "color=black:s=64x36:r=30000/1001",
                    "-map", "1:v", "-map", "0:a", "-shortest", "-c:v", "libx264", "-c:a", "copy", sombra], check=True)
    mixado = os.path.join(TRAB, "sombra_trilha.mp4")
    trilhas.mixar(sombra, moldado, mixado, 0, 21, ducking=1.6)
    return mixado


def pico_db(arq):
    import re
    r = subprocess.run(["ffmpeg", "-i", arq, "-vn", "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    return float(re.search(r"max_volume: (-?[\d.]+) dB", r.stderr).group(1))


def som_de_entrada():
    """som suave da cartela: ar filtrado subindo devagar + um acorde de lá maior (o tom da trilha), com cauda."""
    p = os.path.join(TRAB, "som_cartela.wav")
    if not os.path.exists(p):
        g = ("anoisesrc=color=pink:duration=2.2:amplitude=0.6,highpass=f=350,lowpass=f=2600,"
             "afade=t=in:d=0.9:curve=qsin,afade=t=out:st=0.9:d=1.3:curve=qsin,volume=0.5[ar];"
             "sine=f=220:d=2.2,volume=0.5[s1];sine=f=277.18:d=2.2,volume=0.35[s2];sine=f=329.63:d=2.2,volume=0.3[s3];"
             "sine=f=440:d=2.2,volume=0.12[s4];"
             "[s1][s2][s3][s4]amix=inputs=4:normalize=0,afade=t=in:d=0.7:curve=qsin,afade=t=out:st=0.8:d=1.4:curve=qsin,"
             "volume=0.35[pad];[ar][pad]amix=inputs=2:normalize=0,aecho=0.8:0.6:70|140:0.25|0.15,"
             "aformat=sample_rates=48000:channel_layouts=stereo")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-filter_complex", g, p], check=True)
    return p


def com_luz_e_sons(base, faixas, audio):
    """light leak na passagem cartela -> resposta (pico de luz no corte, mistura 'tela') e os sons em nível fixo."""
    saida = os.path.join(TRAB, "corte_luz.mp4")
    som = som_de_entrada()
    g_som = SOM_PICO_DB - pico_db(som)
    ent = ["-i", base, "-i", som, "-i", audio]
    partes, ev_audio, t_cursor, n = [], [], 0.0, 3
    for k, (a, b) in enumerate(faixas):
        luz = LUZES[k % len(LUZES)]
        ent += ["-i", luz]
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", luz],
                                   capture_output=True, text=True).stdout) / LUZ_VEL
        pico = brilho_pico(luz) / LUZ_VEL
        ini = max(t_cursor, b - pico)
        if ini > t_cursor:
            partes.append(f"color=c=black:s=1920x1080:r=30000/1001:d={ini - t_cursor:.4f}[g{k}]")
        partes.append(f"[{n}:v]setpts=PTS/{LUZ_VEL},fps=30000/1001,scale=1920:1080,format=yuv420p,trim=duration={dur:.4f}[l{k}]")
        g_luz = LUZ_PICO_DB - pico_db(luz)
        partes.append(f"[{n}:a]atempo={LUZ_VEL},volume={g_luz:.1f}dB,adelay={int(ini * 1000)}:all=1[la{k}]")
        partes.append(f"[1:a]volume={g_som:.1f}dB,adelay={int(a * 1000)}:all=1[sa{k}]")
        ev_audio += [f"[la{k}]", f"[sa{k}]"]
        t_cursor = ini + dur
        n += 1
    seq = "".join((f"[g{k}]" if f"[g{k}]" in "".join(partes) else "") + f"[l{k}]" for k in range(len(faixas)))
    nseq = seq.count("[")
    partes.append(f"{seq}concat=n={nseq}:v=1:a=0,tpad=stop_mode=add:stop_duration=3600[luz]")
    partes.append("[0:v]format=gbrp[bv];[luz]format=gbrp[lv];[bv][lv]blend=all_mode=screen:shortest=1,format=yuv420p[v]")
    partes.append(f"[2:a]{''.join(ev_audio)}amix=inputs={1 + len(ev_audio)}:duration=first:normalize=0[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-stats", "-y", *ent, "-filter_complex", ";".join(partes),
                    "-map", "[v]", "-map", "[a]", *PLAT.h264("12M"), "-c:a", "aac", "-b:a", "256k",
                    "-movflags", "+faststart", saida], check=True)
    return saida


def brilho_pico(arq):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", "scale=64:36", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         capture_output=True, check=True).stdout
    q = np.frombuffer(raw, np.uint8).reshape(-1, 36 * 64).mean(1)
    fps = 25.0
    return int(q.argmax()) / fps


def tempos_capitulos(ps):
    t, inicio = 0.0, {}
    for p in ps:
        inicio.setdefault(p["cap"], t)
        t += p["fim"] - p["ini"]
    caps = [{"t": round(inicio[i], 2), "branco": b, "destaque": d, "pergunta": PERGUNTAS[i]}
            for i, (b, d, _) in enumerate(CAPITULOS)]
    json.dump({"duracao": round(t, 2), "capitulos": caps}, open(os.path.join(AQUI, "capitulos.json"), "w"),
              ensure_ascii=False, indent=2)
    return caps, t


def main():
    ps = enquadrar(com_cartelas(pedacos()))
    print(f"{len(ps)} pedaços")
    corte = renderizar_pedacos(ps)
    faixas = cartelas(ps)
    montado = corte
    corte = com_luz_e_sons(montado, faixas, com_trilha(montado, faixas))
    os.remove(montado)                  # intermediário de 2 GB: o disco é curto (refaz em segundos pelos pedaços)
    caps, total = tempos_capitulos(ps)
    print(f"corte: {corte} ({int(total // 60)}:{int(total % 60):02d})")
    for c in caps:
        print(f"  {int(c['t'] // 60)}:{int(c['t'] % 60):02d}  {c['branco']} {c['destaque']}")
    args = [sys.executable, os.path.join(RAIZ, "editor", "capitulos.py"), corte, "--nome", NOME,
            "--duracao", str(CARTELA), "--sem-fundo"]
    for c in caps:
        args += ["--capitulo", f"{c['t']}|{c['pergunta'][0]}|{c['pergunta'][1]}"]
    if "--previas" in sys.argv:
        subprocess.run(args + ["--quadros"], check=True)
    if "--final" in sys.argv:
        subprocess.run(args + ["--saida", PLAT.pasta_renders("C1265")], check=True)


if __name__ == "__main__":
    main()
