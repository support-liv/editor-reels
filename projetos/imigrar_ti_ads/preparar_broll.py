"""Corta e converte os B-rolls do iPhone (HDR HLG, 4K vertical) para SDR 1080x1920, sem áudio, prontos pro --broll."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "editor"))
import plataforma as PLAT

BRUTOS = "/Users/lucastoledo/Downloads/imigrar/ads/TI"
SAIDA = PLAT.pasta_cache("broll_ti")
DOWN = "/Users/lucastoledo/Downloads"
CLIPES = {  # nome: (arquivo, início, duração[, recorte (largura, centro x, centro y) em fração do quadro em pé])
    "bandeira_notebook": ("IMG_4779.MOV", 0.2, 2.4),
    "codigo": ("IMG_4788.MOV", 0.0, 1.6),
    "digitando_close": ("IMG_4802.MOV", 4.0, 2.4),
    "banco_bandeira": ("IMG_4804.MOV", 3.0, 2.6),
    "lucas_digitando": ("IMG_4807.MOV", 5.0, 2.4),
    "lucas_digitando2": ("IMG_4809.MOV", 6.0, 2.4),
    "fonte_notebook": ("IMG_4777.MOV", 1.5, 2.4),
    "maos_teclado": ("IMG_4801.MOV", 5.0, 2.4),
    "notebook_colo": ("IMG_4803.MOV", 8.0, 2.4),
    # Reels do Ednaldo (contexto pedido): vacas longhorn no pasto (bem no fundo: recorte ~2x) e casas/bairro planejado
    "vacas_1": (f"{DOWN}/IMG_9451 2.MOV", 18.3, 2.6, (0.50, 0.30, 0.60)),
    "vacas_2": (f"{DOWN}/IMG_9451 2.MOV", 20.6, 2.4, (0.50, 0.40, 0.60)),
    "pasto": (f"{DOWN}/IMG_9451 2.MOV", 11.0, 2.4),
    "casas_1": (f"{DOWN}/IMG_9408.MOV", 0.5, 3.0),
    "casas_2": (f"{DOWN}/IMG_9408.MOV", 14.5, 2.8),
    "rua_planejada": (f"{DOWN}/IMG_9409.MOV", 13.1, 2.8),
    "fachada": (f"{DOWN}/IMG_9409.MOV", 20.2, 2.6),
    "casa_moderna": (f"{DOWN}/IMG_9435.MOV", 0.0, 2.4),
    # banco de cenas da pasta Downloads (catalogado em 23/10): escritório, documentos, Flórida, Orlando, Lake Nona
    "escritorio_equipe": (f"{DOWN}/IMG_8534 2.mov", 3.0, 2.6),
    "escritorio_conversa": (f"{DOWN}/IMG_8522.mov", 2.0, 2.6),
    "escritorio_duas": (f"{DOWN}/IMG_8543.mov", 2.0, 2.6),
    "escritorio_computador": (f"{DOWN}/IMG_8545 2.mov", 2.0, 2.6),
    "escritorio_mesa": (f"{DOWN}/IMG_8539.mov" if os.path.exists(f"{DOWN}/IMG_8539.mov") else f"{DOWN}/IMG_8539.MOV", 4.0, 2.6),
    "escritorio_analista": (f"{DOWN}/IMG_8542.mov", 4.0, 2.6),
    "documento_vistos": (f"{DOWN}/ScreenRecording_10-22-2026 21-04-03_1.mov", 10.0, 2.8),
    "documento_vistos_2": (f"{DOWN}/ScreenRecording_10-22-2026 21-04-03_1.mov", 30.0, 2.8),
    "rua_bandeiras": (f"{DOWN}/IMG_9447.MOV", 0.8, 2.6),
    "rodovia_placas": (f"{DOWN}/IMG_9440.MOV", 2.4, 2.6),
    "rodovia_transito": (f"{DOWN}/IMG_9448.MOV", 3.0, 2.6),
    "comercio_estacionamento": (f"{DOWN}/IMG_9442.MOV", 1.5, 2.6),
    "pessoas_calcada": (f"{DOWN}/IMG_9446.MOV", 4.0, 2.6),
    "predio_moderno": (f"{DOWN}/IMG_9449.MOV", 8.0, 2.6),
    "predio_hospital": (f"{DOWN}/IMG_9450.MOV", 2.0, 2.6),
    "predio_bandeira": (f"{DOWN}/IMG_9431.MOV", 8.5, 2.6),
    "placa_lake_nona": (f"{DOWN}/IMG_9439.MOV", 15.0, 2.6),
    "condominio_lago": (f"{DOWN}/IMG_9432.MOV", 1.5, 2.6),
    "casas_lago": (f"{DOWN}/IMG_9430.MOV", 3.5, 2.6),
    "casas_rua": (f"{DOWN}/IMG_9407.MOV", 1.0, 2.6),
    "homem_mochila": (f"{DOWN}/IMG_9398.MOV", 7.0, 2.6),
    "estacionamento_carros": (f"{DOWN}/IMG_9390.MOV", 21.0, 2.6),
    "dirigindo": (f"{DOWN}/IMG_9395.MOV", 4.0, 2.6),
    "semaforo": (f"{DOWN}/IMG_9437.MOV", 3.5, 2.6),
    "pasto_2": (f"{DOWN}/IMG_9438.MOV", 3.0, 2.6),
}

os.makedirs(SAIDA, exist_ok=True)
so = sys.argv[1:]                                        # nomes (sem nada: todos)
for nome, (arq, ini, dur, *rec) in CLIPES.items():
    if so and nome not in so:
        continue
    src = os.path.join(BRUTOS, arq)
    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_streams", "-of", "json", src],
                                   capture_output=True, text=True).stdout)["streams"][0]
    hdr = st.get("color_transfer") in ("arib-std-b67", "smpte2084")          # gravação de tela é SDR
    args, filtro = PLAT.entrada_hdr(st) if hdr else ([], "")
    out = os.path.join(SAIDA, nome + ".mp4")
    rot = next((int(sd.get("rotation", 0)) for sd in st.get("side_data_list", []) if "rotation" in sd), 0) % 360
    w, h = (1080, 1920) if rot in (90, 270) or st["height"] > st["width"] else (1920, 1080)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-ss", str(ini), "-t", str(dur), "-i", src,
                    "-vf", filtro + (f"crop=iw*{rec[0][0]}:iw*{rec[0][0]}*16/9:iw*({rec[0][1]}-{rec[0][0]}/2):ih*{rec[0][2]}-iw*{rec[0][0]}*8/9,"
                                     if rec else "") +
                    f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,format=yuv420p",
                    "-an", *PLAT.h264("16M"), out + ".tmp.mp4"], check=True)
    # o -noautorotate leva a matriz de rotação do iPhone pro arquivo novo: zera (a imagem já saiu de pé)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation:v", "0", "-i", out + ".tmp.mp4", "-c", "copy", out], check=True)
    os.remove(out + ".tmp.mp4")
    print("ok", nome, out)
