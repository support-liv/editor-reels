#!/usr/bin/env python3
"""Tira o ronco de vento da fala gravada na rua (Ronney, aprovado pelo Lucas em 10/11/2026).

Corta o grave abaixo de 120 Hz (onde fica quase todo o vento), abaixa um pouco a faixa do "bum" (250 Hz), reduz o chiado
de fundo, dá um leve brilho na voz (3 kHz) e devolve o volume para -16 LUFS. O vídeo é copiado sem recompressão.
Só mexe no corte que tem vento de fato (pico de grave alto) e marca o arquivo para não filtrar duas vezes.

    python3 vento.py BASE.mp4 [...]
"""
import os, subprocess, sys

import numpy as np

FILTRO = ("highpass=f=120:poles=2,highpass=f=120:poles=2,lowshelf=f=250:g=-3,afftdn=nr=16:nf=-30:tn=1,"
          "equalizer=f=3000:t=q:w=1.2:g=2,loudnorm=I=-16:TP=-1.5:LRA=11")
MARCA = "vento-filtrado"
LIMIAR_DB = -8.0     # p90 da energia abaixo de 120 Hz em relação à voz; gravação de interior fica em torno de -11 a -13


def ja_filtrado(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags=comment", "-of", "csv=p=0", video],
                         capture_output=True, text=True).stdout
    return MARCA in out


def vento_db(video):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32)
    n = 4096
    fr = x[: len(x) // n * n].reshape(-1, n) * np.hanning(n)
    s = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    fq = np.fft.rfftfreq(n, 1 / 16000)
    r = 10 * np.log10(s[:, fq < 120].sum(1) / (s[:, (fq >= 120) & (fq < 4000)].sum(1) + 1e-9) + 1e-9)
    return float(np.percentile(r, 90))


def limpar(video):
    if ja_filtrado(video):
        print(f"  vento: {os.path.basename(video)} já filtrado")
        return False
    db = vento_db(video)
    if db < LIMIAR_DB:
        print(f"  vento: {os.path.basename(video)} sem vento ({db:.1f} dB), mantido")
        return False
    tmp = video + ".vento.tmp.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-map", "0:v", "-map", "0:a", "-c:v", "copy",
                    "-af", FILTRO, "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-metadata", f"comment={MARCA}",
                    "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, video)
    print(f"  vento: {os.path.basename(video)} filtrado ({db:.1f} dB de grave)")
    return True


if __name__ == "__main__":
    for v in sys.argv[1:]:
        limpar(v)
