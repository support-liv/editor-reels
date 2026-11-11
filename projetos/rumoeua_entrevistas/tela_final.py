#!/usr/bin/env python3
"""Tela final do rumo.eua: depois que o vídeo acaba, entra uma tela preta com "Siga @rumo.eua" e o som do CTA
dos shorts da LIV (whoosh na entrada + sino), igual ao CTA "no canal" da cauda. Nunca durante a fala.

    python3 tela_final.py VIDEO.mp4 [VIDEO2.mp4 ...]      (substitui o arquivo; --quadro gera só o PNG do cartão)
"""
import os, subprocess, sys, tempfile
from PIL import Image

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "editor"))
import editor_reels as ER  # noqa: E402

TEXTO = "Siga *@rumo.eua*"
DUR = 2.6            # duração da tela preta
ENTRA = 0.12         # o cartão entra (e o whoosh toca) logo no início
SFX = os.path.join(RAIZ, "motion", "sfx")


def cartao(png, escala=1.0, texto=None, marca="rumoeua"):
    # Imigrar: caixa branca em caixa alta, do padrão da marca (sem a escala menor do rumo.eua)
    tam = round(84 * 0.85 * escala) if marca == "rumoeua" else round(70 * escala)
    caixa = ER.caixa_texto(texto or TEXTO, marca, tam=tam)
    img = Image.new("RGB", (ER.OUT_W, ER.OUT_H), "black")
    img.paste(caixa, ((ER.OUT_W - caixa.width) // 2, (ER.OUT_H - caixa.height) // 2), caixa)
    img.save(png)


def aplicar(video, escala=1.0, texto=None, marca="rumoeua", destino=None):
    """destino: grava a versão com a tela final nesse arquivo e mantém o original (Imigrar: uma por CTA)."""
    tmp = tempfile.mkdtemp()
    png = os.path.join(tmp, "cartao.png")
    cartao(png, escala, texto, marca)
    saida = (destino or video) + ".final.mp4"
    # cartão: preto puro até ENTRA, depois o cartão sobe 40px com fade (0,25 s); som: whoosh + sino, sem voz
    filtro = (
        f"color=black:s={ER.OUT_W}x{ER.OUT_H}:r=30:d={DUR}[preto];"
        f"[1:v]format=rgba,fade=in:st={ENTRA}:d=0.25:alpha=1,setpts=PTS-STARTPTS[c];"
        f"[preto][c]overlay=x=0:y='if(lt(t,{ENTRA}),40,max(0,40-(t-{ENTRA})*160))':shortest=1,format=yuv420p,setsar=1[vfim];"
        f"[2:a]adelay={int(ENTRA * 1000)}:all=1,volume=0.35[w];"
        f"[3:a]adelay={int((ENTRA + 0.35) * 1000)}:all=1,volume=0.30[s];"
        f"anullsrc=r=48000:cl=mono:d={DUR}[sil];"
        f"[sil][w][s]amix=inputs=3:normalize=0:duration=first,aformat=sample_rates=48000:channel_layouts=mono[afim];"
        f"[0:v]setsar=1[v0];[0:a]aformat=sample_rates=48000:channel_layouts=mono[a0];"
        f"[v0][a0][vfim][afim]concat=n=2:v=1:a=1[v][a]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-loop", "1", "-t", str(DUR), "-i", png,
                    "-i", os.path.join(SFX, "whoosh.wav"), "-i", os.path.join(SFX, "sino.wav"),
                    "-filter_complex", filtro, "-map", "[v]", "-map", "[a]",
                    "-c:v", "h264_videotoolbox", "-b:v", "14M", "-profile:v", "high", "-pix_fmt", "yuv420p",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida], check=True)
    os.replace(saida, destino or video)
    print("tela final:", destino or video)


if __name__ == "__main__":
    opc = lambda k: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else None
    if "--quadro" in sys.argv:
        cartao(opc("--quadro"), texto=opc("--texto"), marca=opc("--marca") or "rumoeua"); sys.exit()
    esc = float(sys.argv[sys.argv.index("--escala") + 1]) if "--escala" in sys.argv else 1.0
    for v in [x for i, x in enumerate(sys.argv[1:], 1) if not x.startswith("--") and sys.argv[i - 1] != "--escala"]:
        aplicar(v, esc)
