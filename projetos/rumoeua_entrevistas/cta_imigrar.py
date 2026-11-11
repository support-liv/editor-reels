#!/usr/bin/env python3
"""CTA animado da Imigrar no fim do vídeo, no modelo dos shorts da LIV: o último quadro fica parado e o painel do CTA
(motion HyperFrames, com whoosh grave na entrada e sino) entra por cima, logo depois da última palavra.

    python3 cta_imigrar.py VIDEO.mp4 youtube|instagram DESTINO.mp4 [--previa SEG]
"""
import os, subprocess, sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# rosa (padrão) e azul: os vídeos alternam a cor do CTA pra não ficar tudo rosa (Lucas, 09/11)
CTA = {(r, c): os.path.join(RAIZ, "motion", "renders", f"imigrar_cta_{r}{'' if c == 'rosa' else '_' + c}.mov")
       for r in ("youtube", "instagram") for c in ("rosa", "azul", "preto")}
CAUDA = 3.8


def dur(v):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v],
                                capture_output=True, text=True).stdout)


def fim_da_fala(video, d, janela=4.0):
    """onde a última fala termina: RMS em janelas de 50 ms nos últimos segundos; a fala é o que passa de 20% do pico."""
    import numpy as np
    ini = max(0.0, d - janela)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ini:.3f}", "-i", video, "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    n = 800                                                # 50 ms
    if len(x) < n * 4:
        return d
    rms = np.sqrt((x[: len(x) // n * n].reshape(-1, n) ** 2).mean(1))
    alto = np.where(rms > 0.2 * np.percentile(rms, 95))[0]
    return ini + (alto[-1] + 1) * n / 16000 if len(alto) else d


# o painel começa a entrar 0,35 s depois do início do .mov (t0 do roteiro). Lucas (10/11): o CTA demorava e sobrava uma
# cena parada estranha no fim. Agora o painel entra 0,1 s depois da última palavra, cortando o silêncio que sobrava.
T0_PAINEL = 0.35


def aplicar(video, rede, destino, previa=None, cor="preto"):   # preto limpo é o padrão (Lucas, 09/11)
    d = dur(video)
    ini = max(0.0, d - previa) if previa else 0.0          # prévia: só os últimos segundos do vídeo + o CTA
    fala = min(d, fim_da_fala(video, d))
    s = min(d, max(d - 1.2, fala + 0.10) - T0_PAINEL) - ini   # início do .mov do CTA na linha do tempo da saída
    total = s + CAUDA
    filtro = (
        f"[0:v]trim=start={ini:.3f},setpts=PTS-STARTPTS,fps=30,scale=1080:1920,setsar=1,format=yuv420p,"
        f"tpad=stop_mode=clone:stop_duration={CAUDA},trim=duration={total:.3f}[base];"
        f"[1:v]setpts=PTS+{s:.3f}/TB,format=yuva420p[cta];"
        f"[base][cta]overlay=0:0:eof_action=pass:format=auto,format=yuv420p[v];"
        f"[0:a]atrim=start={ini:.3f},asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={total:.3f},"
        f"atrim=duration={total:.3f}[a0];"
        f"[1:a]aresample=48000,adelay={int(s * 1000)}:all=1[a1];"
        f"[a0][a1]amix=inputs=2:normalize=0:duration=first[a]"
    )
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", CTA[(rede, cor)], "-filter_complex", filtro,
                    "-map", "[v]", "-map", "[a]", "-c:v", "h264_videotoolbox", "-b:v", "14M", "-profile:v", "high",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", destino + ".tmp.mp4"], check=True)
    os.replace(destino + ".tmp.mp4", destino)
    print(f"cta imigrar: {destino} (fala acaba {fala:.2f}/{d:.2f}s, painel em {s + ini + T0_PAINEL:.2f}s)")


if __name__ == "__main__":
    prev = float(sys.argv[sys.argv.index("--previa") + 1]) if "--previa" in sys.argv else None
    cor = sys.argv[sys.argv.index("--cor") + 1] if "--cor" in sys.argv else "preto"
    aplicar(sys.argv[1], sys.argv[2], sys.argv[3], prev, cor)
