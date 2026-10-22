"""Anúncios Imigrar · TI (Lucas, Orlando). Cada anúncio junta os melhores takes (gancho de um, corpo e CTA de outro)
num intermediário SDR 1440x2560 e passa pelo editor (cortes pelo áudio, hesitações, legenda, gancho, B-roll).

Uso: python3 projetos/imigrar_ti_ads/lote_ti.py [id ...]     (sem id: todos)
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "editor"))
import plataforma as PLAT

BRUTOS = "/Users/lucastoledo/Downloads/imigrar/ads/TI"
SAIDA = os.path.join(BRUTOS, "prontos")
TRANSC = os.path.join(RAIZ, "editor", "transcricoes")
INTER = PLAT.pasta_cache("ti_intermediarios")
BROLL = PLAT.pasta_cache("broll_ti")
LONGO = "5CDB86EB-3C17-47DA-8429-0A9A3CB2C56D.mp4"
W, H, FPS = 1440, 2560, 30

# correções de legenda (o Whisper erra Green Card e "visto")
TROCAS = {"Gwincard": "Green Card", "wincard": "Green Card", "Gwin": "Green", "Pego": "Green", "vista.": "visto.",
          "vista?": "visto?", "baixarelado": "bacharelado", "toquem": "toque", "façam": "faça", "recebem": "receba em",
          "Canalis": "que analisa", "developments": "o", "patrocinante.": "patrocinando.", "trajetório": "trajetória",
          "Sao": "nos", "Vinhese": "EUA", "empresa?": "empresa", "Maria": "maioria"}

# id: (gancho, [(arquivo, 1ª palavra, última palavra)], [(b-roll, arquivo, tempo no bruto)])
ANUNCIOS = {
    "01_dev_salario_a": ("Quanto ganha um dev nos EUA 🇺🇸?", [
        ("IMG_4790.MOV", 5.26, 13.36), ("IMG_4790.MOV", 22.78, 26.46), ("IMG_4790.MOV", 33.86, 38.78),
        ("IMG_4790.MOV", 40.10, 45.14), ("IMG_4789.MOV", 82.38, 86.42)],
        [("lucas_digitando", "IMG_4790.MOV", 23.3), ("banco_bandeira", "IMG_4790.MOV", 42.4)]),
    "02_dev_salario_b": ("Dev no Brasil 🇧🇷, já pensou em trabalhar nos EUA 🇺🇸?", [
        ("IMG_4789.MOV", 7.52, 13.82), ("IMG_4789.MOV", 23.74, 27.14), ("IMG_4789.MOV", 52.30, 56.80),
        ("IMG_4789.MOV", 64.82, 77.36), ("IMG_4789.MOV", 82.38, 83.28), ("IMG_4789.MOV", 92.40, 95.14)],
        [("fonte_notebook", "IMG_4789.MOV", 24.3), ("codigo", "IMG_4789.MOV", 67.4)]),
    "03_dev_salario_c": ("Você sabe quanto um dev ganha nos EUA 🇺🇸?", [
        ("IMG_4795.MOV", 25.70, 32.12), ("IMG_4795.MOV", 46.76, 55.98), ("IMG_4795.MOV", 113.44, 115.84),
        ("IMG_4795.MOV", 124.12, 127.46), ("IMG_4795.MOV", 129.90, 134.18), ("IMG_4795.MOV", 135.30, 142.26),
        ("IMG_4795.MOV", 151.18, 155.14)],
        [("maos_teclado", "IMG_4795.MOV", 47.4), ("bandeira_notebook", "IMG_4795.MOV", 125.8)]),
    "04_dev_vagas": ("Quantas vagas de TI os EUA 🇺🇸 vão abrir?", [
        ("IMG_4796.MOV", 44.24, 52.70), ("IMG_4796.MOV", 60.20, 64.08), ("IMG_4796.MOV", 64.64, 66.64),
        ("IMG_4796.MOV", 69.28, 73.18), ("IMG_4796.MOV", 90.18, 92.88), ("IMG_4796.MOV", 98.92, 102.84),
        ("IMG_4796.MOV", 110.20, 115.18)],
        [("notebook_colo", "IMG_4796.MOV", 60.8), ("digitando_close", "IMG_4796.MOV", 99.4)]),
    "05_dev_5anos": ("Dev com mais de 5 anos de experiência?", [
        ("IMG_4797.MOV", 20.50, 24.16), ("IMG_4797.MOV", 27.24, 36.44), ("IMG_4797.MOV", 52.12, 58.92),
        ("IMG_4797.MOV", 89.28, 94.66)],
        [("lucas_digitando2", "IMG_4797.MOV", 31.0), ("banco_bandeira", "IMG_4797.MOV", 54.8)]),
    "06_ti_5anos": ("Profissional de TI com mais de 5 anos de experiência?", [
        ("IMG_4800.MOV", 2.72, 6.66), ("IMG_4800.MOV", 11.74, 20.58), ("IMG_4797.MOV", 89.28, 94.66)],
        [("bandeira_notebook", "IMG_4800.MOV", 17.08)]),
    "07_eng_software": ("Precisa de empresa pra ter visto americano 🇺🇸?", [
        (LONGO, 28.26, 34.40), (LONGO, 69.58, 76.90), (LONGO, 145.06, 152.54), (LONGO, 161.38, 167.98)],
        [("lucas_digitando", LONGO, 73.46), ("banco_bandeira", LONGO, 147.54)]),
    "08_dev_objecao": ("TI é comum demais pro Green Card?", [
        (LONGO, 181.72, 188.78), (LONGO, 194.86, 200.30), (LONGO, 201.08, 203.90), (LONGO, 211.04, 215.04),
        (LONGO, 218.32, 228.20)],
        [("fonte_notebook", LONGO, 201.3), ("codigo", LONGO, 211.2)]),
    "09_cientista_salario": ("Quanto ganha um cientista de dados nos EUA 🇺🇸?", [
        (LONGO, 234.56, 243.38), (LONGO, 244.74, 247.34), (LONGO, 250.42, 255.26), (LONGO, 278.60, 283.48),
        (LONGO, 286.14, 289.52), (LONGO, 290.38, 296.18), (LONGO, 299.76, 302.54)],
        [("fonte_notebook", LONGO, 245.0), ("banco_bandeira", LONGO, 279.4)]),
    "10_cientista_crescimento": ("Cientista de dados: quanto sua área vai crescer nos EUA 🇺🇸?", [
        (LONGO, 311.84, 321.32), (LONGO, 244.74, 247.34), (LONGO, 250.42, 255.26), (LONGO, 278.60, 283.48),
        (LONGO, 286.14, 289.52), (LONGO, 290.38, 296.18), (LONGO, 299.76, 302.54)],
        [("notebook_colo", LONGO, 245.0), ("lucas_digitando2", LONGO, 279.4)]),
    "11_cientista_objecao": ("Sua área em alta basta pro Green Card?", [
        (LONGO, 328.84, 334.00), (LONGO, 340.06, 341.96), (LONGO, 344.10, 346.56), (LONGO, 351.70, 359.18),
        (LONGO, 387.88, 391.02), (LONGO, 392.04, 400.32)],
        [("codigo", LONGO, 354.92), ("digitando_close", LONGO, 388.2)]),
}


def palavras(arq):
    base = os.path.splitext(arq)[0]
    return json.load(open(os.path.join(TRANSC, base + ".json")))["palavras"]


def faixa(arq, a, b):
    """(início, fim) do pedaço no bruto: das palavras que começam entre a e b, com folga sem invadir as vizinhas."""
    ps = palavras(arq)
    idx = [i for i, w in enumerate(ps) if a - 0.02 <= w["s"] <= b + 0.02]
    i0, i1 = idx[0], idx[-1]
    ini = ps[i0]["s"] - 0.18
    if i0 > 0:
        ini = max(ini, ps[i0 - 1]["e"] + 0.02)
    fim = ps[i1]["e"] + 0.22
    if i1 + 1 < len(ps):
        fim = min(fim, ps[i1 + 1]["s"] - 0.02)
    ini = round(max(0.0, ini) * FPS) / FPS
    fim = round(fim * FPS) / FPS
    return ini, fim, ps[i0:i1 + 1]


def montar(id_, pedacos):
    """intermediário (vídeo SDR + áudio) e a transcrição dele, deslocando as palavras dos brutos."""
    out = os.path.join(INTER, id_ + ".mov")
    entradas, filtros, pal, mapa, segs, t = [], [], [], [], [], 0.0
    for k, (arq, a, b) in enumerate(pedacos):
        src = os.path.join(BRUTOS, arq)
        ini, fim, ws = faixa(arq, a, b)
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
    texto = " ".join(p["w"] for p in pal)
    json.dump({"texto": texto, "palavras": pal, "segmentos": segs},
              open(os.path.join(TRANSC, id_ + ".json"), "w"), ensure_ascii=False, indent=1)
    return out, mapa


def no_intermediario(mapa, arq, t_bruto):
    for a, ini, fim, t0 in mapa:
        if a == arq and ini <= t_bruto < fim:
            return t0 + t_bruto - ini
    raise SystemExit(f"b-roll fora dos pedaços: {arq} {t_bruto}")


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = sys.argv[1:] or list(ANUNCIOS)
    for id_ in ids:
        gancho, pedacos, brolls = ANUNCIOS[id_]
        print(f"\n=== {id_}")
        video, mapa = montar(id_, pedacos)
        cmd = [sys.executable, os.path.join(RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
               "--gancho", gancho, "--y-legenda", "0.55", "--tirar-hesitacoes", "--respiro", "0.18",
               "--manter-perguntas", "--broll-com-legenda", "--nome", f"imigrar_ti_{id_}", "--saida", SAIDA]
        for nome, arq, tb in brolls:
            cmd += ["--broll", f"{os.path.join(BROLL, nome + '.mp4')}@fonte:{no_intermediario(mapa, arq, tb):.2f}"]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
