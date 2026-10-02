#!/usr/bin/env python3
"""Teste piloto: confere, peça por peça, se o editor funciona neste computador (Mac ou Windows).

    Mac:      python3 editor/teste_piloto.py
    Windows:  py -3.12 -X utf8 editor\\teste_piloto.py

Usa só arquivos do repositório (estoque da LIV, trilhas, transições). Grava um relatório em
piloto/relatorio_<sistema>_<computador>_<data>.md e os arquivos de teste na pasta temporária do editor.
Depois: commit do relatório numa branch `piloto-<nome>` e push, para quem mantém o editor ler e corrigir.
"""
import datetime as dt, json, os, platform, shutil, subprocess, sys, tempfile, time, traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import plataforma as PLAT

SAIDA = PLAT.pasta_cache("piloto")
CLIP = os.path.join(RAIZ, "assets", "estoque_liv",
                    "vertical__dra-livia__sorrindo-e-conversando__sala-de-reuniao__blazer-xadrez__10s.mp4")
FALA = os.path.join(RAIZ, "assets", "teste", "fala_dra_livia_10s.mp4")     # amostra com fala (anúncio da LIV)
TRILHA = os.path.join(RAIZ, "assets", "trilhas", "corporativo__skylines-anno-domini-beats__99bpm__A-maior.mp3")
PY = sys.executable
resultados = []


def run(cmd, timeout=900, **k):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace", **k)


def teste(nome):
    def deco(f):
        def w():
            t0 = time.time()
            try:
                det = f() or ""
                resultados.append((nome, True, det, time.time() - t0))
                print(f"  OK    {nome}  {det}", flush=True)
            except Exception as e:
                det = f"{type(e).__name__}: {str(e)[:400]}"
                resultados.append((nome, False, det + "\n" + traceback.format_exc()[-1500:], time.time() - t0))
                print(f"  FALHOU {nome}  {det}", flush=True)
        w.nome = nome
        return w
    return deco


@teste("ambiente")
def t_ambiente():
    v = run(["ffmpeg", "-version"]).stdout.splitlines()[0]
    filtros = run(["ffmpeg", "-hide_banner", "-filters"]).stdout
    node = run([PLAT.cmd("node") if PLAT.WIN else "node", "--version"]).stdout.strip() if shutil.which("node") else "sem node"
    utf8 = sys.flags.utf8_mode or os.environ.get("PYTHONUTF8") == "1"
    falta = [x for x in ("zscale", "tonemap") if f" {x} " not in filtros]
    det = f"Python {platform.python_version()} | {v[:40]} | node {node} | UTF-8 {'sim' if utf8 else 'NÃO'}"
    if falta:
        det += f" | ffmpeg SEM {', '.join(falta)} (HDR sem tone mapping)"
    if PLAT.WIN and not utf8:
        raise RuntimeError(det + " — rode com py -3.12 -X utf8")
    return det


@teste("arquivos grandes (Git LFS)")
def t_lfs():
    for arq in (CLIP, FALA, TRILHA, os.path.join(RAIZ, "assets", "transicoes", "FILM BURNS 19.mp4")):
        with open(arq, "rb") as f:
            if f.read(40).startswith(b"version https://git-lfs"):
                raise RuntimeError(f"{os.path.basename(arq)} é só o ponteiro do LFS: rode git lfs pull")
    return "estoque, trilhas e transições baixados"


@teste("codificador de vídeo")
def t_codificador():
    enc = PLAT.codificador()
    out = os.path.join(SAIDA, "codificador.mp4")
    r = run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:d=2:r=30"] + PLAT.h264("8M") + [out])
    if r.returncode or not os.path.getsize(out):
        raise RuntimeError(r.stderr[-400:])
    return f"{enc}"


@teste("HDR do iPhone → cor padrão")
def t_hdr():
    hlg = os.path.join(SAIDA, "hlg.mp4")                      # vídeo sintético marcado como HLG/BT.2020
    r = run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:d=1:r=30", "-pix_fmt", "yuv420p10le",
             "-c:v", "libx265" if "libx265" in run(["ffmpeg", "-hide_banner", "-encoders"]).stdout else "libx264",
             "-color_primaries", "bt2020", "-color_trc", "arib-std-b67", "-colorspace", "bt2020nc", hlg])
    if r.returncode:
        raise RuntimeError("não gerou o vídeo HLG de teste: " + r.stderr[-300:])
    st = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                         "stream=width,height,color_transfer:stream_side_data=rotation", "-of", "json", hlg]).stdout)["streams"][0]
    args, filtro = PLAT.entrada_hdr(st)
    out = os.path.join(SAIDA, "hdr_sdr.mp4")
    r = run(["ffmpeg", "-v", "error", "-y"] + args + ["-i", hlg, "-vf", filtro + "scale=540:960"] + PLAT.h264("4M") + [out])
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])
    return "tone mapping ok" if "zscale" in filtro or PLAT.MAC else "convertido SEM tone mapping (ffmpeg sem zscale)"


def _quadros(n=3):
    pasta = tempfile.mkdtemp()
    run(["ffmpeg", "-v", "error", "-i", CLIP, "-vf", "fps=1,scale=540:960", "-frames:v", str(n), os.path.join(pasta, "%03d.png")])
    return pasta, sorted(os.path.join(pasta, f) for f in os.listdir(pasta))


@teste("detector de rostos")
def t_rostos():
    pasta, imgs = _quadros()
    res = PLAT.rostos(imgs)
    shutil.rmtree(pasta)
    achou = sum(1 for r in res if r)
    if not achou:
        raise RuntimeError(f"nenhum rosto em {len(imgs)} quadros com a Dra. Lívia")
    return f"rosto em {achou}/{len(imgs)} quadros, centro {[round(v, 2) for v in res[0][0][:2]] if res[0] else '-'}"


@teste("recorte da pessoa (texto atrás)")
def t_recorte():
    import numpy as np
    from PIL import Image
    pasta, imgs = _quadros()
    sai = os.path.join(pasta, "m")
    PLAT.mascaras_pessoa(pasta, sai)
    cob = [float((np.array(Image.open(os.path.join(sai, os.path.basename(i))).convert("L")) > 128).mean()) for i in imgs]
    shutil.rmtree(pasta)
    if not all(0.03 < c < 0.9 for c in cob):
        raise RuntimeError(f"máscara estranha: pessoa cobre {[round(c, 2) for c in cob]} do quadro")
    return f"pessoa ocupa {[f'{c:.0%}' for c in cob]} do quadro"


@teste("emoji e bandeiras")
def t_emoji():
    from PIL import Image
    out = os.path.join(SAIDA, "emoji.png")
    PLAT.emoji_png("🙂", out)
    if not Image.open(out).getbbox():
        raise RuntimeError("emoji saiu vazio")
    for b in ("eua", "brasil"):
        if not os.path.exists(os.path.join(AQUI, f"bandeira_{b}.png")):
            raise RuntimeError(f"falta editor/bandeira_{b}.png")
    return "emoji e bandeiras ok"


@teste("login guardado (Chaveiro / Gerenciador de Credenciais)")
def t_segredo():
    PLAT.guardar_segredo("editor-reels-teste", "ok-çã🇺🇸")
    v = PLAT.ler_segredo("editor-reels-teste")
    PLAT.apagar_segredo("editor-reels-teste")
    if v != "ok-çã🇺🇸":
        raise RuntimeError(f"leu {v!r}")
    return "guardou, leu e apagou"


@teste("short completo (Whisper + enquadramento + legenda + gancho + CTA animado)")
def t_short():
    r = run([PY, os.path.join(AQUI, "editor_reels.py"), FALA, "--marca", "liv", "--gancho", "Teste piloto 🇺🇸 ação",
             "--cta-animado", "TESTE", "--nome", "piloto_short", "--saida", SAIDA], timeout=1800)
    out = os.path.join(SAIDA, "piloto_short.mp4")
    if r.returncode or not os.path.exists(out):
        raise RuntimeError((r.stderr or r.stdout)[-800:])
    return f"{os.path.getsize(out) / 1e6:.1f} MB (motion/HyperFrames incluído no CTA)"


@teste("anúncio dinâmico (texto atrás, film burn, legenda LIV)")
def t_ads():
    rot = os.path.join(SAIDA, "rot_piloto.py")
    pal = os.path.join(SAIDA, "pal_piloto.json")
    json.dump([{"w": "Teste", "s": 0.2, "e": 0.6}, {"w": "piloto", "s": 0.6, "e": 1.1}], open(pal, "w", encoding="utf-8"))
    tr = os.path.join(RAIZ, "assets", "transicoes", "FILM BURNS 19.mp4").replace("\\", "/")
    open(rot, "w", encoding="utf-8").write(f'''ROTEIRO = {{"nome": "piloto_ads", "saida": r"{SAIDA}", "video": r"{CLIP}", "palavras": r"{pal}",
 "zoom": [], "broll": [], "burns_arquivos": [r"{tr}"], "burns": [1.0],
 "atras": [{{"t0": 0.0, "t1": 1.4, "legenda": True, "linhas": [{{"y": 600, "tam": 220, "peso": 900, "cor": "laranja", "spans": [{{"texto": "Ação", "t": 0.1}}]}}]}}],
 "cta": {{"t0": 99, "t_seta": 99, "linha1": "a", "linha2": "b", "linha3": "c"}}}}''')
    r = run([PY, os.path.join(AQUI, "ads_dinamico.py"), rot, "--versao", "A", "--ate", "1.5", "--quadros", "0.8"], timeout=1800)
    png = os.path.join(PLAT.pasta_cache("ads", "previas", "piloto_ads_A_texto_atras"), "00.80s.png")
    if r.returncode or not os.path.exists(png):
        raise RuntimeError((r.stderr or r.stdout)[-800:])
    return "quadro de prévia gerado (veja " + png + ")"


@teste("trilha por baixo da fala")
def t_trilha():
    import trilhas
    out = os.path.join(SAIDA, "piloto_trilha.mp4")
    s, voz, mus, g = trilhas.mixar(FALA, TRILHA, out, ss=18)
    return f"fala {voz} LUFS, ganho da trilha {g:+.1f} dB"


@teste("Chrome + Playwright (base do envio pelo YouTube Studio)")
def t_chrome():
    from playwright.sync_api import sync_playwright
    perfil = tempfile.mkdtemp()
    porta = 9444
    p = subprocess.Popen([PLAT.chrome(), "--headless=new", f"--user-data-dir={perfil}", f"--remote-debugging-port={porta}",
                          "--no-first-run", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        time.sleep(4)
        with sync_playwright() as pw:
            nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{porta}")
            pg = nav.contexts[0].new_page()
            pg.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=60000)
            url = pg.url
            nav.new_browser_cdp_session().send("Browser.close")
        return "abriu o Studio (pede login: normal) — " + url[:60]
    finally:
        p.kill(); shutil.rmtree(perfil, ignore_errors=True)


def main():
    print(f"Teste piloto — {platform.system()} {platform.release()} — {platform.node()}\n", flush=True)
    for t in (t_ambiente, t_lfs, t_codificador, t_hdr, t_rostos, t_recorte, t_emoji, t_segredo,
              t_short, t_ads, t_trilha, t_chrome):
        t()
    ok = sum(1 for r in resultados if r[1])
    os.makedirs(os.path.join(RAIZ, "piloto"), exist_ok=True)
    nome = f"relatorio_{platform.system().lower()}_{platform.node().split('.')[0]}_{dt.datetime.now():%Y%m%d-%H%M}.md"
    rel = os.path.join(RAIZ, "piloto", nome)
    with open(rel, "w", encoding="utf-8") as f:
        f.write(f"# Teste piloto — {platform.system()} {platform.release()} ({platform.machine()})\n\n")
        f.write(f"{dt.datetime.now():%d/%m/%Y %H:%M} · Python {platform.python_version()} · {ok}/{len(resultados)} ok\n\n")
        f.write("| Teste | Resultado | Tempo | Detalhe |\n|---|---|---|---|\n")
        for n, o, d, s in resultados:
            f.write(f"| {n} | {'✅' if o else '❌'} | {s:.0f}s | {d.splitlines()[0][:160].replace('|', '/')} |\n")
        falhas = [r for r in resultados if not r[1]]
        if falhas:
            f.write("\n## Detalhes das falhas\n\n")
            for n, o, d, s in falhas:
                f.write(f"### {n}\n```\n{d}\n```\n")
        f.write(f"\nArquivos de teste: `{SAIDA}`\n")
    print(f"\n{ok}/{len(resultados)} ok — relatório: {rel}")


if __name__ == "__main__":
    main()
