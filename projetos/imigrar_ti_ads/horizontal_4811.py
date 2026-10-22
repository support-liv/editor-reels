"""Anúncio horizontal de teste (IMG_4811, Lucas no banco): 16:9 1920x1080, punch-in alternando por corte,
LUT 'cinema pastel', grão leve, letterings editoriais em serifa (New York) com tons pastel do lado do banco.
Fora da identidade da Imigrar de propósito (teste de anúncio).

Uso: python3 projetos/imigrar_ti_ads/horizontal_4811.py cortes.json [--quadros 3,12,25]
     cortes.json = plano do editor (editor_reels.py ... --json-cortes), com os ajustes de CORRIGIR abaixo.
"""
import json, os, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "editor"))
sys.path.insert(0, AQUI)
import plataforma as PLAT
import lettering as L

SRC = "/Users/lucastoledo/Downloads/imigrar/ads/TI/IMG_4811.mov"
SAIDA = "/Users/lucastoledo/Downloads/imigrar/ads/TI/prontos/imigrar_ti_horizontal_4811.mp4"
TMP = PLAT.pasta_cache("horizontal_4811")
LUT = os.path.join(AQUI, "cinema_pastel.cube")
FPS = 30000 / 1001
SW, SH = 3840, 2160
# fim dos cortes que pegavam o começo da palavra seguinte ("existe u-", "modalidade no", "perfil 27")
CORRIGIR = {20.84: 20.66, 26.64: 26.46, 63.40: 63.24}
# enquadramentos (zoom, centro x, centro y em fração do quadro original), alternando por corte
PLANOS = [(1.00, 0.50, 0.50), (1.22, 0.40, 0.58), (1.10, 0.46, 0.55)]

# letterings: (palavra-gatilho no bruto, segundos na tela, linhas)
CARDS = [
    (4.56, 3.4, [[("dev no Brasil", "rot", "creme")], [("Sonha em viver", "rom", "creme")],
                 [("nos ", "rom", "creme"), ("Estados Unidos?", "ita", "rosa")]]),
    (12.86, 3.1, [[("os dois caminhos de sempre", "rot", "creme")], [("Sponsor", "rom", "creme")],
                  [("ou ", "ita", "rosa"), ("sorteio.", "rom", "creme")]]),
    (19.80, 4.6, [[("a realidade", "rot", "creme")], [("Green Card", "rom", "creme")],
                  [("por ", "ita", "rosa"), ("mérito", "ita", "rosa")], [("e trajetória.", "rom", "creme")]]),
    (52.64, 4.0, [[("sem precisar de", "rot", "creme")], [("sponsor", "rom", "creme"), (",", "rom", "creme")],
                  [("nem de ", "ita", "rosa"), ("sorteio.", "rom", "creme")]]),
    (62.50, 4.2, [[("análise de perfil gratuita", "rot", "creme")], [("Comente", "rom", "creme")],
                  [("“perfil”", "ita", "rosa")]]),
]


def cortes(arq):
    cs = json.load(open(arq))
    for c in cs:
        c["e"] = CORRIGIR.get(round(c["e"], 2), c["e"])
        # quadros inteiros, iguais no vídeo e no áudio
        n = round((c["e"] - c["s"]) * FPS)
        c["e"] = c["s"] + n / FPS
        c["n"] = n
    return cs


def tempo_saida(cs, t):
    acc = 0.0
    for c in cs:
        if c["s"] <= t < c["e"]:
            return acc + t - c["s"]
        if t < c["s"]:
            return acc
        acc += c["n"] / FPS
    return acc


def crop(z, cx, cy):
    w, h = round(SW / z / 2) * 2, round(SH / z / 2) * 2
    x = min(max(0, round(cx * SW - w / 2)), SW - w)
    y = min(max(0, round(cy * SH - h / 2)), SH - h)
    return f"crop={w}:{h}:{x}:{y}"


def render_cards(cs):
    """PNG de cada linha de cada card (mesmo layout do card inteiro) e quando entra/sai no vídeo pronto."""
    os.makedirs(TMP, exist_ok=True)
    capas = []
    for k, (gatilho, dur, linhas) in enumerate(CARDS):
        t0 = tempo_saida(cs, gatilho)
        for i in range(len(linhas)):
            png = os.path.join(TMP, f"card{k}_l{i}.png")
            L.desenhar(linhas, x0=1150, y_centro=720, tam=100, so_linha=i).save(png)
            capas.append((png, t0 + 0.22 * i, t0 + dur))
    veu = os.path.join(TMP, "veu.png")
    L.veu(forca=0.44).save(veu)
    return capas, veu


def main():
    cs = cortes(sys.argv[1])
    quadros = None
    if "--quadros" in sys.argv:
        quadros = [float(x) for x in sys.argv[sys.argv.index("--quadros") + 1].split(",")]
    total = sum(c["n"] for c in cs) / FPS
    capas, veu = render_cards(cs)
    lut = os.path.join(TMP, "cinema_pastel.cube")          # sem espaço no caminho (o filtro do ffmpeg quebra no espaço)
    shutil.copy(LUT, lut)

    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", SRC],
                                   capture_output=True, text=True).stdout)["streams"][0]
    args, filtro = PLAT.entrada_hdr(st)
    entradas, fc = [], []
    for k, c in enumerate(cs):
        z, cx, cy = PLANOS[k % len(PLANOS)]
        dur = c["n"] / FPS
        entradas += [*args, "-ss", f"{c['s']:.3f}", "-t", f"{dur:.4f}", "-i", SRC]
        fc.append(f"[{k}:v]{filtro}{crop(z, cx, cy)},scale=1920:1080:flags=lanczos,fps=30000/1001,format=yuv420p,setsar=1,"
                  f"trim=end_frame={c['n']},setpts=PTS-STARTPTS[v{k}];"
                  f"[{k}:a]aresample=48000,atrim=duration={dur:.4f},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.012,afade=t=out:st={max(0, dur - 0.012):.4f}:d=0.012[a{k}]")
    n = len(cs)
    fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[base][acat]")
    # grade + véu + grão
    i_veu = n
    entradas += ["-loop", "1", "-framerate", "30000/1001", "-t", f"{total:.3f}", "-i", veu]
    fc.append(f"[base]format=gbrp,lut3d={lut}:interp=tetrahedral,format=yuv420p,vignette=angle=PI/5[g]")
    fc.append(f"[{i_veu}:v]format=rgba[veu];[g][veu]overlay=0:0:format=auto,noise=c0s=5:c0f=t+u[cam0]")
    atual = "cam0"
    for j, (png, t0, t1) in enumerate(capas):
        idx = n + 1 + j
        d = t1 - t0
        entradas += ["-loop", "1", "-framerate", "30000/1001", "-t", f"{d:.3f}", "-i", png]
        fc.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d=0.55:alpha=1,fade=t=out:st={d - 0.45:.3f}:d=0.45:alpha=1,"
                  f"setpts=PTS+{t0:.3f}/TB[c{j}];"
                  f"[{atual}][c{j}]overlay=x=0:y='16*max(0,1-(t-{t0:.3f})/0.7)':eof_action=pass:format=auto[cam{j + 1}]")
        atual = f"cam{j + 1}"
    fc.append(f"[{atual}]format=yuv420p[vout]")
    fc.append("[acat]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[aout]")

    if quadros:
        fc = fc[:-1] + ["[acat]anullsink"]                  # prévia: só imagem
        for q in quadros:
            out = os.path.join(TMP, f"previa_{q:.1f}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(fc), "-map", "[vout]",
                            "-ss", str(q), "-frames:v", "1", out], check=True)
            print("prévia", out)
        return
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
                    *PLAT.h264("16M"), "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", SAIDA], check=True)
    print("Pronto:", SAIDA, f"{total:.1f}s")


if __name__ == "__main__":
    main()
