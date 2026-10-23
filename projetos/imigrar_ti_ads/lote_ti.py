"""Anúncios Imigrar · TI (Lucas, Orlando). Cada anúncio junta os melhores takes (gancho de um, corpo e CTA de outro)
num intermediário SDR 1440x2560 e passa pelo editor (cortes pelo áudio, hesitações, legenda, gancho, B-roll).

Uso: python3 projetos/imigrar_ti_ads/lote_ti.py [id ...]     (sem id: todos)
"""
import json, os, re, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "editor"))
import plataforma as PLAT

BRUTOS = "/Users/lucastoledo/Downloads/imigrar/ads/TI"
SAIDA = os.path.join(BRUTOS, "_em_revisao")      # só vai pra prontos/ depois de aprovado na auditoria
TRANSC = os.path.join(RAIZ, "editor", "transcricoes")
INTER = PLAT.pasta_cache("ti_intermediarios")
BROLL = PLAT.pasta_cache("broll_ti")
LONGO = "5CDB86EB-3C17-47DA-8429-0A9A3CB2C56D.mp4"
W, H, FPS = 1440, 2560, 30

# correções de legenda (o Whisper erra Green Card e "visto")
TROCAS = {"Gwincard": "Green Card", "wincard": "Green Card", "Gwin": "Green", "Pego": "Green", "vista.": "visto.",
          "vista?": "visto?", "baixarelado": "bacharelado", "toquem": "toque", "façam": "faça",
          "Canalis": "que analisa", "developments": "o", "patrocinante.": "patrocinando.", "trajetório": "trajetória",
          "Sao": "nos", "Vinhese": "EUA", "empresa?": "empresa", "Maria": "maioria"}

# id: ((gancho A, gancho B), [(arquivo, início, fim) em segundos do bruto], [(b-roll, arquivo, tempo no bruto)])
# Tempos escolhidos na transcrição LITERAL de cada janela (auditar_fala.py): cada pedaço pula a tentativa errada
# ("sabia que o salário, sabia que o salário" → fica só a 2ª). Os ganchos A/B mudam só o balão.
ANUNCIOS = {
    "01_dev_salario": (("Quanto ganha um dev nos EUA 🇺🇸?", "Desenvolvedor: qual o salário nos EUA 🇺🇸?"), [
        ("IMG_4790.MOV", 5.15, 6.95), ("IMG_4790.MOV", 8.85, 13.80), ("IMG_4790.MOV", 22.95, 26.85),
        ("IMG_4790.MOV", 33.70, 39.15), ("IMG_4790.MOV", 39.95, 45.60), ("IMG_4789.MOV", 82.25, 86.90)],
        [("lucas_digitando", "IMG_4790.MOV", 23.5), ("banco_bandeira", "IMG_4790.MOV", 42.4)]),
    "02_dev_brasil": (("Dev no Brasil 🇧🇷, já pensou em trabalhar nos EUA 🇺🇸?", "Desenvolvedor: Green Card nos EUA 🇺🇸 sem sponsor?"), [
        ("IMG_4789.MOV", 7.40, 14.10), ("IMG_4789.MOV", 23.95, 27.60), ("IMG_4789.MOV", 52.15, 57.20),
        ("IMG_4789.MOV", 64.70, 67.15), ("IMG_4797.MOV", 79.90, 84.95),   # "...existe uma modalidade" + "do Green Card
        ("IMG_4789.MOV", 82.25, 83.85), ("IMG_4789.MOV", 92.30, 95.60)],      # baseada na sua trajetória profissional..."
        [("fonte_notebook", "IMG_4789.MOV", 24.4), ("codigo", "IMG_4789.MOV", 65.9),
         ("bandeira_notebook", "IMG_4797.MOV", 80.0)]),       # cobre a troca de cenário (4789 -> 4797) no meio da frase
    "03_dev_residencia": (("Você sabe quanto um dev ganha nos EUA 🇺🇸?", "Dev: residência permanente nos EUA 🇺🇸 sem empresa?"), [
        ("IMG_4795.MOV", 25.35, 32.60), ("IMG_4795.MOV", 46.60, 56.40), ("IMG_4795.MOV", 113.45, 116.30),
        ("IMG_4795.MOV", 123.75, 127.70), ("IMG_4795.MOV", 129.85, 134.60), ("IMG_4795.MOV", 136.35, 142.60),
        ("IMG_4795.MOV", 151.05, 155.60)],
        [("maos_teclado", "IMG_4795.MOV", 47.4), ("bandeira_notebook", "IMG_4795.MOV", 124.5)]),
    "04_dev_vagas": (("Quantas vagas de TI os EUA 🇺🇸 vão abrir até 2035?", "Desenvolvedor: os EUA 🇺🇸 precisam de você?"), [
        ("IMG_4796.MOV", 44.20, 48.20), ("IMG_4796.MOV", 49.78, 53.60), ("IMG_4796.MOV", 60.05, 64.50),
        ("IMG_4796.MOV", 64.60, 66.97), ("IMG_4796.MOV", 69.20, 73.55), ("IMG_4796.MOV", 90.15, 93.20),
        ("IMG_4796.MOV", 98.25, 103.20), ("IMG_4796.MOV", 110.15, 115.60)],
        [("notebook_colo", "IMG_4796.MOV", 61.0), ("digitando_close", "IMG_4796.MOV", 98.8)]),
    "05_dev_5anos": (("Dev com mais de 5 anos de experiência?", "Dev sênior: Green Card nos EUA 🇺🇸 sem sponsor?"), [
        ("IMG_4797.MOV", 20.40, 24.70), ("IMG_4797.MOV", 27.10, 36.85), ("IMG_4797.MOV", 52.00, 59.30),
        ("IMG_4797.MOV", 89.15, 95.00)],
        [("lucas_digitando2", "IMG_4797.MOV", 31.0), ("banco_bandeira", "IMG_4797.MOV", 54.8)]),
    "06_ti_5anos": (("Profissional de TI com +5 anos de experiência?", "TI: morar e trabalhar nos EUA 🇺🇸 sem sponsor?"), [
        ("IMG_4800.MOV", 4.05, 7.30), ("IMG_4800.MOV", 13.25, 20.95), ("IMG_4800.MOV", 21.70, 28.00)],
        [("bandeira_notebook", "IMG_4800.MOV", 17.1)]),
    "07_eng_software": (("Engenheiro de software: visto americano 🇺🇸 sem empresa?", "Engenheiro de software: precisa de sponsor nos EUA 🇺🇸?"), [
        (LONGO, 28.10, 34.95), (LONGO, 69.45, 77.40), (LONGO, 145.55, 153.20), (LONGO, 161.25, 162.85),
        (LONGO, 164.30, 168.40)],
        [("lucas_digitando", LONGO, 72.0), ("banco_bandeira", LONGO, 147.5)]),
    "08_dev_objecao": (("Desenvolvedor: sua área é comum demais pro Green Card?", "Dev: dá pra ter Green Card nos EUA 🇺🇸 sendo de TI?"), [
        (LONGO, 181.60, 189.30), (LONGO, 194.95, 200.90), (LONGO, 200.95, 204.70), (LONGO, 210.95, 215.70),
        (LONGO, 218.20, 229.90)],
        [("fonte_notebook", LONGO, 201.3), ("codigo", LONGO, 211.2)]),
    "09_cientista_salario": (("Quanto ganha um cientista de dados nos EUA 🇺🇸?", "Cientista de dados: qual o salário nos EUA 🇺🇸?"), [
        (LONGO, 234.40, 239.42), (LONGO, 241.08, 243.90), (LONGO, 244.60, 247.80), (LONGO, 250.30, 256.20),
        (LONGO, 278.55, 284.40), (LONGO, 286.90, 289.95), (LONGO, 290.25, 296.65), (LONGO, 299.65, 303.30)],
        [("fonte_notebook", LONGO, 245.0), ("banco_bandeira", LONGO, 279.4)]),
    "10_cientista_crescimento": (("Cientista de dados: quanto sua área vai crescer nos EUA 🇺🇸?", "Cientista de dados: sua área está em alta nos EUA 🇺🇸?"), [
        (LONGO, 311.70, 322.00), (LONGO, 244.60, 247.80), (LONGO, 250.30, 256.20), (LONGO, 278.55, 284.40),
        (LONGO, 286.90, 289.95), (LONGO, 290.25, 296.65), (LONGO, 299.65, 303.30)],
        [("notebook_colo", LONGO, 245.0), ("lucas_digitando2", LONGO, 279.4)]),
    "11_cientista_objecao": (("Cientista de dados: só a área em alta basta pro Green Card?", "Cientista de dados: o que pesa no Green Card dos EUA 🇺🇸?"), [
        (LONGO, 328.70, 334.55), (LONGO, 339.95, 342.40), (LONGO, 343.95, 347.40), (LONGO, 351.55, 359.58),
        (LONGO, 387.75, 391.95), (LONGO, 391.95, 400.75)],
        [("codigo", LONGO, 354.9), ("digitando_close", LONGO, 388.2)]),
}


def palavras(arq):
    """transcrição literal (com as repetições: ver transcrever_literal.py); sem ela, a normal."""
    base = os.path.splitext(arq)[0]
    lit = os.path.join(TRANSC, base + ".literal.json")
    return json.load(open(lit if os.path.exists(lit) else os.path.join(TRANSC, base + ".json")))["palavras"]


# números falados por extenso na transcrição literal -> dígitos na legenda
NUMEROS = [("dois mil e trinta e cinco", "2035"), ("cento e trinta e seis", "136"), ("cento e vinte", "120"),
           ("trinta e cinco por cento", "35%"), ("trinta e cinco", "35"), ("cem", "100"), ("cinco anos", "5 anos")]


# grafia da legenda: frases que o Whisper literal escreve errado (comparadas sem caixa) -> texto certo
FRASES = [("Seu desenvolvedor no Brasil sabia", "Você é desenvolvedor no Brasil? Sabia"),
          ("O personal de TI com o Bacharelado", "Profissional de TI com bacharelado"),
          ("O sinal de TI com o Bacharelado", "Profissional de TI com bacharelado"),
          ("brincardio,", "Green Card,"), ("firmamentemente", "permanentemente"), ("win hard...", "Green Card."),
          ("qual vista", "qual visto"), ("sorteios e vistos.", "sorteios de vistos."), ("sorteiros", "sorteios"),
          ("Colume", "Volume"), ("valia", "avalia"), ("Toquem,", "toque em"), ("façam", "faça"),
          ("recebem em em", "receba em"), ("recebem em", "receba em"), ("em em", "em"), ("Analise o seu", "que analisa o seu"),
          ("patrocida.", "patrocine."), ("vista.", "visto."), ("vista?", "visto?"), ("vistas.", "vistos."),
          ("de vista", "de visto"), ("transferência de executivo,", "transferência executiva,"), ("acho E os", "acho que os"), ("que Se precisa", "que precisa"), ("sorteiros", "sorteios"), ("perfil gratuitas.", "perfil gratuita."), ("wincard", "Green Card"), ("GwinCard", "Green Card"), ("Gwyncard", "Green Card")]


def corrigir_frases(pal):
    # reticências do Whisper saem antes de comparar ("o... No Brasil" não casava com "o No Brasil")
    pal = [dict(p, w=p["w"].replace("...", "")) for p in pal]
    pal = [p for p in pal if p["w"]]
    out, i = [], 0
    while i < len(pal):
        for errado, certo in FRASES:
            e = errado.lower().split()
            if [p["w"].lower() for p in pal[i:i + len(e)]] == e:
                novas, s0, s1 = certo.split(), pal[i]["s"], pal[i + len(e) - 1]["e"]
                passo = (s1 - s0) / len(novas)
                out += [{"w": w, "s": round(s0 + k * passo, 3), "e": round(s0 + (k + 1) * passo, 3)} for k, w in enumerate(novas)]
                if len(novas) == 1 and any(ch.isdigit() for ch in certo):     # número: o alinhador lê o falado
                    out[-1]["falado"] = " ".join(p["w"] for p in pal[i:i + len(e)])
                i += len(e)
                break
        else:
            w = dict(pal[i]); w["w"] = w["w"].replace("...", "")      # reticências do Whisper não vão pra legenda
            if w["w"]:
                out.append(w)
            i += 1
    return out


# "Green Card" sai de mil jeitos no Whisper (wincard, WinCard, Gwyncard, win card, going card, Green Car, brincardio...)
_GC1 = re.compile(r"^(g?w[iy]n|green|brin|going|pego|wing|grin)(card|cards|car|hard|kard|cardio|tard)$", re.I)
_GC_A = {"win", "gwin", "gwyn", "going", "green", "brin", "pego", "wing", "grin", "wyn"}
_GC_B = {"card", "cards", "car", "hard", "kard", "cardio", "tard"}


def green_card(pal):
    out, i = [], 0
    limpo = lambda w: re.sub(r"[^\wáéíóúãõç]", "", w.lower())
    pont = lambda w: w[len(w.rstrip(".,?!;:")):]
    while i < len(pal):
        a = limpo(pal[i]["w"])
        b = limpo(pal[i + 1]["w"]) if i + 1 < len(pal) else ""
        if _GC1.match(a):
            out += [dict(pal[i], w="Green"), dict(pal[i], w="Card" + pont(pal[i]["w"]))]; i += 1
        elif a in _GC_A and b in _GC_B:
            out += [dict(pal[i], w="Green"), dict(pal[i + 1], w="Card" + pont(pal[i + 1]["w"]))]; i += 2
        else:
            out.append(pal[i]); i += 1
    return out


# REGRA: nomes de vistos no formato oficial (E-2, O-1, O-3, L-1, H-1B, EB-1, EB-2, EB-2 NIW, B1/B2, DS-160) e nomes em
# inglês grafados certo (Lake Nona, Tavistock, USTA...). Vale para todo vídeo.
VISTOS = {"e2": "E-2", "i2": "E-2", "o1": "O-1", "o3": "O-3", "l1": "L-1", "h1b": "H-1B", "eb1": "EB-1", "eb2": "EB-2",
          "niw": "NIW", "b1b2": "B1/B2", "ds160": "DS-160"}
NOMES_EN = [(re.compile(r"^l[aeéê](k|qu|c|q)u?[ie]?n[oô]na$", re.I), "Lake Nona"), (re.compile(r"^tav[ia]?st(op|ock)$", re.I), "Tavistock"),
            (re.compile(r"^usta$", re.I), "USTA")]


def nomes(pal):
    out, i = [], 0
    chave = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
    pont = lambda w: w[len(w.rstrip(".,?!;:")):]
    while i < len(pal):
        w = pal[i]["w"]; c = chave(w)
        c2 = chave(w + (pal[i + 1]["w"] if i + 1 < len(pal) else ""))
        if c2 in ("ds160", "b1b2", "eb2niw", "lakenona") and i + 1 < len(pal):    # "DS -160", "B1 B2", "Lake Nona"
            novo = {"ds160": "DS-160", "b1b2": "B1/B2", "eb2niw": "EB-2 NIW", "lakenona": "Lake Nona"}[c2]
            out.append(dict(pal[i], w=novo + pont(pal[i + 1]["w"]), e=pal[i + 1]["e"])); i += 2; continue
        if c in VISTOS:
            out.append(dict(pal[i], w=VISTOS[c] + pont(w)))
        else:
            for rx, certo in NOMES_EN:
                if rx.match(re.sub(r"[.,?!;:]", "", w)):
                    out.append(dict(pal[i], w=certo + pont(w))); break
            else:
                out.append(pal[i])
        i += 1
    return out


def juntar_numeros(pal):
    from auditar_fala import norm
    out, i = [], 0
    while i < len(pal):
        for frase, dig in NUMEROS:
            fs = frase.split()
            if [norm(p["w"]) for p in pal[i:i + len(fs)]] == fs:
                ult = pal[i + len(fs) - 1]
                pont = ult["w"][len(ult["w"].rstrip(".,?!;:")):]
                if dig.endswith(" anos"):
                    out += [{"w": "5", "s": pal[i]["s"], "e": pal[i]["e"], "falado": pal[i]["w"]}, dict(ult, w="anos" + pont)]
                else:          # "falado": o alinhador (editor/alinhar.py) não lê dígito, lê "dois mil e trinta e cinco"
                    out.append({"w": dig + pont, "s": pal[i]["s"], "e": ult["e"],
                                "falado": " ".join(p["w"] for p in pal[i:i + len(fs)])})
                i += len(fs)
                break
        else:
            out.append(pal[i]); i += 1
    return out


def faixa(arq, a, b, exato=False):
    """(início, fim, palavras) do pedaço: tempos explícitos em quadros inteiros e as palavras da transcrição
    literal da própria janela (o Whisper no take inteiro esconde repetições)."""
    from auditar_fala import transcrever_janela
    # REGRA: o pedaço nunca corta palavra. Estende o fim até o fim da última palavra + 0,30s e o começo até 0,12s antes
    # da primeira (pela transcrição literal do take), sem encostar na palavra vizinha. Fechar o pedaço no INÍCIO da
    # última palavra cortava o final dos vídeos ("ele é", "favorável", "acontecer").
    ps = palavras(arq)
    # palavra pertence ao pedaço se COMEÇA antes do fim marcado (0,03s de margem). Margem maior excluía palavra que era
    # pra entrar ("novamente" no fim do R13). Fim marcado tem que ficar ANTES da palavra seguinte (ver 07: 162,85).
    dentro = [i for i, w in enumerate(ps) if a - 0.05 <= w["s"] < b - 0.03]
    # pedaço "exato" (4º item da tupla): tempos medidos à mão entre duas palavras coladas, sem extensão (a extensão
    # pegava de volta a gaguejada que o corte tirou: "maior que o da, do Brasil" no R3)
    if dentro and not exato:
        i0, i1 = dentro[0], dentro[-1]
        # fim da palavra: o alinhado às vezes engole o silêncio seguinte (e a extensão pegava respiração, onde o Whisper
        # ainda "ouvia" um "Então" fantasma); limita pelo fim do Whisper + 0,15s
        fim_pal = min(ps[i1]["e"], ps[i1].get("e_whisper", 1e9) + 0.15)
        prox = ps[i1 + 1]["s"] if i1 + 1 < len(ps) else 1e9
        if fim_pal - b < 0.6:                            # palavra esticada demais = tempo errado: não confia
            b = max(b, min(fim_pal + 0.20, prox - 0.08))
        b = min(b, prox - 0.06)                          # nunca encosta na palavra seguinte
        ant = ps[i0 - 1]["e"] if i0 > 0 else 0.0
        a = min(a, max(ps[i0]["s"] - 0.12, ant + 0.03))  # o começo só recua (nunca anda pra depois do marcado)
    ini, fim = round(a * FPS) / FPS, round(b * FPS) / FPS
    ws = transcrever_janela(os.path.join(BRUTOS, arq), ini, fim)
    from auditar_fala import max_iguais
    if max_iguais(ws) >= 5:                              # alucinação do prompt literal ("E, e, e, e..."): leitura normal
        ws = transcrever_janela(os.path.join(BRUTOS, arq), ini, fim, literal=False)
    longas = [w for w in ws[:-1] if w["e"] - w["s"] > 0.9]
    for w in longas:                                     # palavra esticada = pode ter fala escondida embaixo
        print(f"  ⚠ palavra esticada em {arq} {w['s']:.2f}-{w['e']:.2f}: '{w['w']}'")
    return ini, fim, ws


def montar(id_, pedacos):
    """intermediário (vídeo SDR + áudio) e a transcrição dele, deslocando as palavras dos brutos."""
    out = os.path.join(INTER, id_ + ".mov")
    entradas, filtros, pal, mapa, segs, t = [], [], [], [], [], 0.0
    for k, (arq, a, b, *modo) in enumerate(pedacos):
        src = os.path.join(BRUTOS, arq)
        ini, fim, ws = faixa(arq, a, b, exato="exato" in modo)
        dur = fim - ini
        st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", src],
                                       capture_output=True, text=True).stdout)["streams"][0]
        hdr = st.get("color_transfer") in ("arib-std-b67", "smpte2084")
        args, filtro = PLAT.entrada_hdr(st) if hdr else ([], "")
        entradas += [*args, "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", src]
        filtros.append(f"[{k}:v]{filtro}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
                       f"format=yuv420p,setsar=1,trim=duration={dur:.3f},setpts=PTS-STARTPTS[v{k}];"
                       f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.012,afade=t=out:st={max(0, dur - 0.012):.3f}:d=0.012[a{k}]")
        seg0 = len(pal)
        for w in ws:
            if w["w"] == "em" and pal and pal[-1]["w"] == "Green":      # "Pego em card" = Green Card
                continue
            pal.append({"w": TROCAS.get(w["w"], w["w"]), "s": round(w["s"] - ini + t, 3), "e": round(min(w["e"], fim) - ini + t, 3)})
        segs.append({"s": round(t, 3), "e": round(t + dur, 3), "t": " ".join(p["w"] for p in pal[seg0:])})
        mapa.append((arq, ini, fim, t))
        t += dur
    n = len(pedacos)
    fc = ";".join(filtros) + ";" + "".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "hevc_videotoolbox", "-b:v", "40M", "-tag:v", "hvc1", "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "pcm_s16le", out + ".tmp.mov"], check=True)
    # o -noautorotate leva a matriz de rotação do iPhone pro intermediário: zera (a imagem já saiu de pé)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation:v", "0", "-i", out + ".tmp.mov", "-c", "copy", out], check=True)
    os.remove(out + ".tmp.mov")
    pal = juntar_numeros(nomes(green_card(corrigir_frases(pal))))
    # cada palavra sabe de que pedaço (take) veio: o alinhador e o editor não passam da emenda (ver editor/alinhar.py)
    for w in pal:
        w["pedaco"] = max([k for k, sg in enumerate(segs) if sg["s"] <= max(w["s"], 0.0) + 0.001] or [0])
    # palavra de ligação solta no FIM do vídeo, depois de pausa ("...acabar o Brasil. Então"): começo da frase seguinte
    # ou palavra que o Whisper inventou numa respiração. Sai (o editor não guarda o áudio dela).
    soltas = {"entao", "e", "mas", "ai", "ne", "tipo", "bom", "o", "a", "que"}
    from auditar_fala import norm
    while len(pal) > 2 and norm(pal[-1]["w"]) in soltas and pal[-1]["s"] - pal[-2]["e"] > 0.2:
        print(f"  palavra solta no fim tirada: «{pal[-1]['w']}»")
        pal.pop()
    from auditar_fala import repeticoes
    reps = repeticoes(pal)
    # repetição NA EMENDA: o fim de um take e o começo do seguinte dizem a mesma palavra ("acha que precisa | Se precisa
    # de uma empresa" no 04: o take 1 terminava em "precisa" e o take 2 recomeçava nela)
    for k in range(1, len(segs)):
        # só a ÚLTIMA palavra do take: "pro futuro dela. | O futuro da família" (R1) é estilo, não recomeço
        fim_k = [norm(w["w"]) for w in pal if w["pedaco"] == k - 1][-1:]
        ini_k = [norm(w["w"]) for w in pal if w["pedaco"] == k][:3]
        ult_w = [w["w"] for w in pal if w["pedaco"] == k - 1][-1:]
        if ult_w and ult_w[0].rstrip().endswith((".", "?", "!")):
            continue                                     # frase terminada + frase nova ("O seu visto. | O visto de turista")
        comum = [x for x in fim_k if len(x) >= 4 and x in ini_k]
        if comum:
            i = max(j for j, w in enumerate(pal) if w["pedaco"] == k - 1)
            print(f"  ⚠ REPETIÇÃO NA EMENDA {k - 1}|{k} em {id_}: '{comum[0]}' ({segs[k - 1]['t'][-40:]} | {segs[k]['t'][:40]})")
            reps.append((i, 1))
    if reps:
        for i, n in reps:
            print(f"  ⚠ REPETIÇÃO em {id_}: '{' '.join(p['w'] for p in pal[i:i + n])}' em {pal[i]['s']:.2f}s e {pal[i + n]['s']:.2f}s")
        if "--forcar" not in sys.argv:
            raise SystemExit(f"{id_}: fala repetida nos pedaços, corrija antes de renderizar")
    texto = " ".join(p["w"] for p in pal)
    json.dump({"texto": texto, "palavras": pal, "segmentos": segs, "pedacos": [[sg["s"], sg["e"]] for sg in segs]},
              open(os.path.join(TRANSC, id_ + ".json"), "w"), ensure_ascii=False, indent=1)
    return out, mapa


ESPERADO = PLAT.pasta_cache("auditoria_esperado")


def rodar_editor(cmd, nome):
    """roda o editor; com --esperado só salva o que o vídeo pronto deve dizer (palavras no tempo do pronto e cortes)
    para o auditar_pronto.py comparar com o que o Whisper ouve."""
    if "--esperado" not in sys.argv:
        subprocess.run(cmd, check=True)
    os.makedirs(ESPERADO, exist_ok=True)                 # o esperado sai sempre junto do render (para a auditoria)
    for opc, suf in (("--json-palavras", ".palavras.json"), ("--json-cortes", ".cortes.json")):
        subprocess.run(cmd + [opc, os.path.join(ESPERADO, nome + suf)], check=True, capture_output=True)
    print("  esperado salvo:", nome)


def no_intermediario(mapa, arq, t_bruto):
    for a, ini, fim, t0 in mapa:
        if a == arq and ini <= t_bruto < fim:
            return t0 + t_bruto - ini
    raise SystemExit(f"b-roll fora dos pedaços: {arq} {t_bruto}")


def main():
    os.makedirs(SAIDA, exist_ok=True)
    so_montar = "--so-montar" in sys.argv                 # só junta os pedaços e confere repetição (sem renderizar)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ANUNCIOS)
    for id_ in ids:
        ganchos, pedacos, brolls = ANUNCIOS[id_]
        print(f"\n=== {id_}")
        try:
            video, mapa = montar(id_, pedacos)
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e); continue
        if so_montar:
            print("  ", json.load(open(os.path.join(TRANSC, id_ + ".json")))["texto"])
            continue
        for versao, gancho in zip("AB", ganchos):        # A/B: muda só o gancho do balão
            cmd = [sys.executable, os.path.join(RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
                   "--gancho", gancho, "--seg-gancho", "4.2", "--y-legenda", "0.62", "--crop-fixo", "--aperto", "0.80", "--punch", "0.72", "--alinhar", "--vad", "--tirar-hesitacoes", "--respiro", "0.22",
                   "--proteger-palavra", "0.40", "--manter-perguntas", "--broll-com-legenda",
                   "--nome", f"imigrar_ti_{id_}_{versao}", "--saida", SAIDA]
            for nome, arq, tb in brolls:
                cmd += ["--broll", f"{os.path.join(BROLL, nome + '.mp4')}@fonte:{no_intermediario(mapa, arq, tb):.2f}"]
            rodar_editor(cmd, f"imigrar_ti_{id_}_{versao}")
            if "--esperado" in sys.argv:
                break


if __name__ == "__main__":
    main()
