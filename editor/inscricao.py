#!/usr/bin/env python3
"""Balão "Inscreva-se" da LIV no corte longo da live (só corte longo da LIV: nunca em shorts nem na Imigrar).

    python3 editor/inscricao.py CORTE_LONGO.mp4 [-o saida.mp4] [--intervalo 60] [--quadro 75]

Aparece a cada ~1 minuto (com uma variação de alguns segundos pra não ficar mecânico), centralizado na parte
de baixo, e NUNCA junto com o banner da live (o card "Faça uma análise de perfil… QR Code", que fica no mesmo
lugar): o banner é detectado no próprio vídeo e o balão espera ele sair (ou pula aquela vez).
O balão é assets/inscreva_liv.mov (PNG sem perda com transparência; fundo verde tirado pela "verdice" do pixel, então
cinza/preto/branco/laranja ficam opacos; entra subindo e sai com a entrada invertida, 5,5 s).
--quadro T só gera um PNG do vídeo no segundo T com o balão (pra validar posição e tamanho).
"""
import argparse, os, random, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plataforma as PLAT

AQUI = os.path.dirname(os.path.abspath(__file__))
BALAO = os.path.join(os.path.dirname(AQUI), "assets", "inscreva_liv.mov")
DUR = 5.466                  # duração do balão
LARGURA = 0.40               # fração da largura do vídeo
MARGEM_BAIXO = 0.045         # distância da borda de baixo (fração da altura)
FOLGA = 1.5                  # segundos livres de banner antes e depois do balão
INICIO = 45.0                # primeiro balão não antes disso (depois da vinheta e da abertura)
FIM = 12.0                   # nem nos últimos segundos


def duracao(video):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                                capture_output=True, text=True).stdout.strip())


def tempos_banner(video, fps=2):
    """segundos (na timeline do vídeo) em que o banner da live está na faixa de baixo, no centro.
    O banner é um card claro com bordas retas: procura uma borda horizontal forte cruzando a região central."""
    W, H = 320, 180
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps={fps},scale={W}:{H}:flags=area,format=gray",
                          "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
    x0, x1, y0 = int(W * 0.24), int(W * 0.79), int(H * 0.70)
    ocupado, i = [], 0
    while True:
        b = p.stdout.read(W * H)
        if len(b) < W * H:
            break
        q = np.frombuffer(b, np.uint8).reshape(H, W).astype(np.int16)[y0:, x0:x1]
        bordas = (np.abs(np.diff(q, axis=0)) > 25).mean(axis=1)        # por linha: fração com borda horizontal
        if bordas.max() > 0.55:
            ocupado.append(i / fps)
        i += 1
    p.wait()
    return ocupado


def agenda(total, ocupado, intervalo=60.0, variacao=6.0, semente=None):
    """momentos de entrada do balão: ~1 por minuto, fora do banner (com folga)."""
    rnd = random.Random(semente)
    livres = lambda t: not any(t - FOLGA <= o <= t + DUR + FOLGA for o in ocupado)
    ts, alvo = [], INICIO + rnd.uniform(0, variacao)
    while alvo + DUR < total - FIM:
        t = next((alvo + d for d in np.arange(0, 25, 0.5) if alvo + d + DUR < total - FIM and livres(alvo + d)), None)
        if t is not None:
            ts.append(round(float(t), 2))
            alvo = t + intervalo + rnd.uniform(-variacao, variacao)
        else:
            alvo += intervalo                                           # banner o tempo todo: pula essa vez
    return ts


def _filtro(ts, W, H):
    w = int(round(W * LARGURA / 2)) * 2
    h = int(round(w * 268 / 1526 / 2)) * 2
    x, y = (W - w) // 2, H - h - int(H * MARGEM_BAIXO)
    partes, ant = [], "0:v"
    for k, t in enumerate(ts):
        partes.append(f"[{k + 1}:v]scale={w}:{h}:flags=lanczos,format=rgba,setpts=PTS-STARTPTS+{t}/TB[b{k}]")
        partes.append(f"[{ant}][b{k}]overlay={x}:{y}:eof_action=pass:enable='between(t,{t},{t + DUR})'[v{k}]")
        ant = f"v{k}"
    return ";".join(partes), f"[{ant}]"


def aplicar(video, saida=None, intervalo=60.0, log=print):
    saida = saida or os.path.splitext(video)[0] + "_inscreva.mp4"
    W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip().split(","))
    total = duracao(video)
    ocupado = tempos_banner(video)
    ts = agenda(total, ocupado, intervalo, semente=os.path.basename(video))
    blocos = _faixas(ocupado)
    log(f"  inscreva-se: {len(ts)} vezes em {total / 60:.1f} min | banner da live: "
        + (", ".join(f"{a // 60:.0f}:{a % 60:04.1f}–{b // 60:.0f}:{b % 60:04.1f}" for a, b in blocos) or "nenhum"))
    log("  entradas: " + ", ".join(f"{t // 60:.0f}:{t % 60:04.1f}" for t in ts))
    filtro, saida_v = _filtro(ts, W, H)
    entradas = ["-i", video]
    for _ in ts:
        entradas += ["-i", BALAO]
    cmd = ["ffmpeg", "-v", "error", "-y"] + entradas + ["-filter_complex", filtro, "-map", saida_v, "-map", "0:a?",
           *PLAT.h264("12M"), "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", saida]
    subprocess.run(cmd, check=True)
    return saida, ts, blocos


def _faixas(ocupado, junta=2.0):
    blocos = []
    for o in ocupado:
        if blocos and o - blocos[-1][1] <= junta:
            blocos[-1][1] = o
        else:
            blocos.append([o, o])
    return blocos


def quadro(video, t, png):
    """PNG do vídeo no segundo t com o balão já parado (2 s depois da entrada), pra validar."""
    W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                                    "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip().split(","))
    filtro, saida_v = _filtro([0.0], W, H)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-ss", "2", "-i", BALAO,
                    "-filter_complex", filtro.replace("setpts=PTS-STARTPTS+0.0/TB", "setpts=PTS-STARTPTS"),
                    "-map", saida_v, "-frames:v", "1", png], check=True)
    return png


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("-o", "--saida"); ap.add_argument("--intervalo", type=float, default=60.0)
    ap.add_argument("--quadro", type=float, help="só gera um PNG com o balão no segundo indicado")
    a = ap.parse_args()
    if a.quadro is not None:
        print(quadro(a.video, a.quadro, os.path.splitext(a.saida or a.video)[0] + f"_inscreva_{int(a.quadro)}s.png"))
    else:
        print("pronto:", aplicar(a.video, a.saida, a.intervalo)[0])
