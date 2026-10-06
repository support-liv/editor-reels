"""Tudo que muda entre macOS e Windows fica aqui: pastas, codificador de vídeo, HDR, Chrome, rostos, recorte da
pessoa, emoji e onde guardar o login. O resto do editor só chama estas funções.

Mac: VideoToolbox + Vision (Swift) + Chaveiro. Windows: NVENC/QuickSync/AMF (ou libx264) + OpenCV YuNet +
MediaPipe + Gerenciador de Credenciais (keyring).
"""
import json, os, shutil, subprocess, sys, tempfile, urllib.request

MAC = sys.platform == "darwin"
WIN = os.name == "nt"
if WIN:                                   # texto sempre em UTF-8 (no Windows o padrão é cp1252: quebra acento e emoji)
    os.environ.setdefault("PYTHONUTF8", "1")


def cmd(nome):
    """npx/npm no Windows são .cmd (o subprocess não acha sem a extensão)."""
    return nome + ".cmd" if WIN and nome in ("npx", "npm", "node-gyp") else nome
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)


# ------------------------------------------------------------------ pastas
def pasta_cache(*partes):
    if MAC:
        base = os.path.expanduser("~/Library/Caches/editor-reels")
    elif WIN:
        base = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "editor-reels", "Cache")
    else:
        base = os.path.expanduser("~/.cache/editor-reels")
    p = os.path.join(base, *partes)
    os.makedirs(p if not os.path.splitext(p)[1] else os.path.dirname(p), exist_ok=True)
    return p


def pasta_dados(*partes):
    if MAC:
        base = os.path.expanduser("~/Library/Application Support/editor-reels")
    elif WIN:
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "editor-reels")
    else:
        base = os.path.expanduser("~/.local/share/editor-reels")
    p = os.path.join(base, *partes)
    os.makedirs(p if not os.path.splitext(p)[1] else os.path.dirname(p), exist_ok=True)
    return p


def pasta_desktop():
    """a Mesa (Desktop) de verdade. No Windows com OneDrive ela fica em ...\\OneDrive\\Desktop: lê do registro."""
    if WIN:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
                p = os.path.expandvars(winreg.QueryValueEx(k, "Desktop")[0])
                if os.path.isdir(p):
                    return p
        except OSError:
            pass
        for p in (os.path.join(os.environ.get("OneDrive", ""), "Desktop"), os.path.expanduser("~/Desktop")):
            if p and os.path.isdir(p):
                return p
    return os.path.expanduser("~/Desktop")


def pasta_renders(*partes):
    """onde os vídeos prontos vão: Mesa/Editor Reels/<projeto> (Mac e Windows). Cria a pasta."""
    p = os.path.join(pasta_desktop(), "Editor Reels", *partes)
    os.makedirs(p, exist_ok=True)
    return p


def caminho(p):
    """expande ~ e troca "~/Desktop" pela Mesa real (no Windows pode estar no OneDrive)."""
    p = os.path.expanduser(p) if not p.startswith("~/Desktop") else os.path.join(pasta_desktop(), p[len("~/Desktop/"):])
    return os.path.normpath(p)


# ------------------------------------------------------------------ limpeza automática (disco não enche)
LIMPEZA = [   # (pasta, extensões, dias sem uso até apagar) — nunca o perfil do Chrome (login do Studio)
    (os.path.join(RAIZ, "motion", "renders"), (".mov", ".mp4", ".webm", ".png"), 2),
    ("ads/previas", None, 7), ("trilhas_previas", None, 7), ("analise", None, 7), ("piloto", None, 7),
    ("tarefas", None, 7), ("ads", (".npy",), 14), ("broll", (".mp4", ".json"), 60),
]


def espaco_livre_gb(pasta=None):
    return shutil.disk_usage(pasta or os.path.expanduser("~")).free / 1e9


def limpar_temporarios(forcar=False, avisar=True):
    """apaga arquivos intermediários antigos (animações, prévias, máscaras, testes) — no máximo 1x por dia.
    Os vídeos prontos (Mesa/Editor Reels) e o login do YouTube Studio nunca são tocados."""
    import time
    marca = os.path.join(pasta_cache(), ".ultima_limpeza")
    if not forcar and os.path.exists(marca) and time.time() - os.path.getmtime(marca) < 86400:
        return 0
    agora, liberado = time.time(), 0
    for pasta, exts, dias in LIMPEZA:
        base = pasta if os.path.isabs(pasta) else os.path.join(pasta_cache(), pasta)
        if not os.path.isdir(base) or "chrome-studio" in base:
            continue
        for raiz, _, arqs in os.walk(base):
            if "chrome-studio" in raiz:
                continue
            for a in arqs:
                p = os.path.join(raiz, a)
                if exts and not a.lower().endswith(exts):
                    continue
                try:
                    if agora - max(os.path.getmtime(p), os.path.getatime(p)) > dias * 86400:
                        liberado += os.path.getsize(p); os.remove(p)
                except OSError:
                    pass
    open(marca, "w").write(str(agora))
    if avisar and espaco_livre_gb() < 10:
        print(f"  ! pouco espaço no disco ({espaco_livre_gb():.1f} GB livres): renders grandes podem falhar.", file=sys.stderr)
    return liberado


# ------------------------------------------------------------------ codificação de vídeo
_ENC = None


def _ffmpeg_tem(enc):
    """o codificador existe E funciona nesta máquina (NVENC sem placa NVIDIA aparece na lista mas falha)."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=s=256x256:d=0.2", "-c:v", enc, "-f", "null", "-"],
                       capture_output=True)
    return r.returncode == 0


def codificador():
    global _ENC
    if _ENC is None:
        if MAC:
            _ENC = "h264_videotoolbox"
        else:
            _ENC = next((e for e in ("h264_nvenc", "h264_qsv", "h264_amf") if _ffmpeg_tem(e)), "libx264")
    return _ENC


def h264(bitrate="14M", extra=None):
    """argumentos de codificação H.264 para este computador (acelerado por hardware quando dá)."""
    enc = codificador()
    args = ["-c:v", enc, "-b:v", bitrate]
    if enc == "libx264":
        args += ["-preset", "medium", "-maxrate", bitrate, "-bufsize", str(int(bitrate.rstrip("M")) * 2) + "M"]
    elif enc == "h264_nvenc":
        args += ["-preset", "p5"]
    return args + (extra or [])


# ------------------------------------------------------------------ HDR do iPhone → SDR BT.709
def entrada_hdr(st):
    """(args de entrada, filtro inicial) para decodificar HDR (HLG/PQ) em SDR com tone mapping."""
    if MAC:
        rot = next((int(sd.get("rotation", 0)) for sd in st.get("side_data_list", []) if "rotation" in sd), 0) % 360
        gira = {90: "transpose=2,", 270: "transpose=1,", 180: "hflip,vflip,"}.get(rot, "")
        args = ["-hwaccel", "videotoolbox", "-hwaccel_output_format", "videotoolbox_vld", "-noautorotate"]
        filtro = (f"scale_vt=w={st['width']}:h={st['height']}:color_matrix=bt709:color_primaries=bt709:"
                  f"color_transfer=bt709,hwdownload,format=p010le,{gira}")
        return args, filtro
    # Windows/Linux: zscale + tonemap do ffmpeg (o ffmpeg "full" do gyan.dev já vem com zimg); a rotação é automática
    if _tem_filtro("zscale") and _tem_filtro("tonemap"):
        return [], ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,"
                    "zscale=t=bt709:m=bt709:r=tv,format=yuv420p,")
    print("  ! ffmpeg sem zscale: vídeo HDR vai sem tone mapping (cor pode ficar lavada). Instale o ffmpeg 'full'.")
    return [], "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p,"


def _tem_filtro(nome):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return any(ln.split()[1:2] == [nome] for ln in r.splitlines() if len(ln.split()) > 1)


# ------------------------------------------------------------------ Chrome (Studio do YouTube, render do motion)
def chrome():
    if MAC:
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if WIN:
        for base in (os.environ.get("PROGRAMFILES", r"C:\Program Files"), os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
                     os.path.join(os.environ.get("LOCALAPPDATA", ""), "")):
            p = os.path.join(base, "Google", "Chrome", "Application", "chrome.exe")
            if os.path.exists(p):
                return p
        return "chrome.exe"
    return shutil.which("google-chrome") or "google-chrome"


# ------------------------------------------------------------------ rostos
YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"


def _swift(nome, fonte):
    """compila um utilitário Swift do macOS (uma vez) e devolve o caminho do binário."""
    binario = os.path.join(pasta_cache("bin"), nome)
    if not os.path.exists(binario) or os.path.getmtime(binario) < os.path.getmtime(fonte):
        subprocess.run(["swiftc", "-O", fonte, "-o", binario], check=True, capture_output=True)
    return binario


def rostos(imagens):
    """uma lista por imagem: [[cx, cy, w, h, pitch, yaw], ...] normalizado (0-1, origem no topo)."""
    if MAC:
        b = _swift("rostos", os.path.join(AQUI, "rostos.swift"))
        out = subprocess.run([b] + list(imagens), capture_output=True, text=True, check=True).stdout
        return [json.loads(ln) for ln in out.strip().splitlines()]
    import cv2, numpy as np
    modelo = os.path.join(RAIZ, "assets", "modelos", "face_detection_yunet_2023mar.onnx")   # vem no repositório (OpenCV Zoo, MIT)
    res = []
    det = None
    for p in imagens:
        img = cv2.imread(p)
        if img is None:
            res.append([]); continue
        h, w = img.shape[:2]
        if det is None or det.getInputSize() != (w, h):
            det = cv2.FaceDetectorYN.create(modelo, "", (w, h), 0.7, 0.3, 5000)
        _, faces = det.detect(img)
        caixas = []
        for f in (faces if faces is not None else []):
            x, y, fw, fh = f[:4]
            ol, od, na = f[4:6], f[6:8], f[8:10]                      # olhos e nariz: estima o giro da cabeça
            meio = (ol + od) / 2
            dist = max(1.0, float(np.linalg.norm(od - ol)))
            yaw = float((na[0] - meio[0]) / dist) * 1.2
            pitch = float(((na[1] - meio[1]) / dist) - 0.55)
            caixas.append([float(v) for v in ((x + fw / 2) / w, (y + fh / 2) / h, fw / w, fh / h, pitch, yaw)])
        res.append(caixas)
    return res


# ------------------------------------------------------------------ recorte da pessoa (texto atrás)
def mascaras_pessoa(pasta_in, pasta_out):
    """grava em pasta_out uma máscara PNG (pessoa branca) para cada PNG de pasta_in."""
    os.makedirs(pasta_out, exist_ok=True)
    if MAC:
        b = _swift("recorte_pessoa", os.path.join(AQUI, "recorte_pessoa.swift"))
        subprocess.run([b, pasta_in, pasta_out], check=True, capture_output=True)
        return
    import cv2, numpy as np, mediapipe as mp
    seg = mp.solutions.selfie_segmentation.SelfieSegmentation(model_selection=0)
    for nome in sorted(f for f in os.listdir(pasta_in) if f.endswith(".png")):
        img = cv2.imread(os.path.join(pasta_in, nome))
        r = seg.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        m = (np.clip(r.segmentation_mask, 0, 1) * 255).astype(np.uint8)
        cv2.imwrite(os.path.join(pasta_out, nome), m)


# ------------------------------------------------------------------ emoji
def emoji_png(texto, saida):
    if MAC:
        b = _swift("emoji", os.path.join(AQUI, "emoji.swift"))
        subprocess.run([b, texto, saida], check=True, capture_output=True)
        return
    from PIL import Image, ImageDraw, ImageFont
    fonte = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "seguiemj.ttf")
    f = ImageFont.truetype(fonte, 109)
    im = Image.new("RGBA", (220, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), texto, font=f, embedded_color=True)
    im.crop(im.getbbox() or (0, 0, 220, 160)).save(saida)


# ------------------------------------------------------------------ login guardado (Chaveiro / Gerenciador de Credenciais)
def guardar_segredo(servico, valor):
    if MAC:
        import getpass
        subprocess.run(["security", "add-generic-password", "-U", "-a", getpass.getuser(), "-s", servico, "-w", valor],
                       check=True, capture_output=True)
    else:
        import keyring
        keyring.set_password(servico, "editor-reels", valor)


def ler_segredo(servico):
    if MAC:
        import getpass
        r = subprocess.run(["security", "find-generic-password", "-a", getpass.getuser(), "-s", servico, "-w"],
                           capture_output=True, text=True)
        v = r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
        if v and len(v) % 2 == 0 and all(c in "0123456789abcdef" for c in v):   # com acento o Chaveiro devolve em hex
            try:
                v = bytes.fromhex(v).decode("utf-8")
            except ValueError:
                pass
        return v
    import keyring
    return keyring.get_password(servico, "editor-reels")


def apagar_segredo(servico):
    if MAC:
        import getpass
        subprocess.run(["security", "delete-generic-password", "-a", getpass.getuser(), "-s", servico], capture_output=True)
    else:
        import keyring
        try:
            keyring.delete_password(servico, "editor-reels")
        except Exception:
            pass
