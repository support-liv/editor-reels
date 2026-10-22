"""Corta e converte os B-rolls do iPhone (HDR HLG, 4K vertical) para SDR 1080x1920, sem áudio, prontos pro --broll."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "editor"))
import plataforma as PLAT

BRUTOS = "/Users/lucastoledo/Downloads/imigrar/ads/TI"
SAIDA = PLAT.pasta_cache("broll_ti")
CLIPES = {  # nome: (arquivo, início, duração)
    "bandeira_notebook": ("IMG_4779.MOV", 0.2, 2.4),
    "codigo": ("IMG_4788.MOV", 0.0, 1.6),
    "digitando_close": ("IMG_4802.MOV", 4.0, 2.4),
    "banco_bandeira": ("IMG_4804.MOV", 3.0, 2.6),
    "lucas_digitando": ("IMG_4807.MOV", 5.0, 2.4),
    "lucas_digitando2": ("IMG_4809.MOV", 6.0, 2.4),
    "fonte_notebook": ("IMG_4777.MOV", 1.5, 2.4),
    "maos_teclado": ("IMG_4801.MOV", 5.0, 2.4),
    "notebook_colo": ("IMG_4803.MOV", 8.0, 2.4),
}

os.makedirs(SAIDA, exist_ok=True)
for nome, (arq, ini, dur) in CLIPES.items():
    src = os.path.join(BRUTOS, arq)
    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", src],
                                   capture_output=True, text=True).stdout)["streams"][0]
    args, filtro = PLAT.entrada_hdr(st)
    out = os.path.join(SAIDA, nome + ".mp4")
    rot = next((int(sd.get("rotation", 0)) for sd in st.get("side_data_list", []) if "rotation" in sd), 0) % 360
    w, h = (1080, 1920) if rot in (90, 270) or st["height"] > st["width"] else (1920, 1080)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-ss", str(ini), "-t", str(dur), "-i", src,
                    "-vf", filtro + f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                    "-an", *PLAT.h264("16M"), out + ".tmp.mp4"], check=True)
    # o -noautorotate leva a matriz de rotação do iPhone pro arquivo novo: zera (a imagem já saiu de pé)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation:v", "0", "-i", out + ".tmp.mp4", "-c", "copy", out], check=True)
    os.remove(out + ".tmp.mp4")
    print("ok", nome, out)
