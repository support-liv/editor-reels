"""Detector de voz neural (Silero VAD): onde há fala de verdade, em quadros de 20 ms. Separa voz de ruído de shopping,
carro e vento muito melhor que o volume do som. O editor usa com --vad (no lugar do limiar de energia).

Uso: .venv-whisperx/bin/python editor/vad.py VIDEO SAIDA.npz
     SAIDA.npz: "normal" (limiar 0,5) e "suave" (limiar 0,25: começo/fim fraco da palavra), um valor por 20 ms.
"""
import sys

import numpy as np
import torch
import whisperx
from silero_vad import get_speech_timestamps, load_silero_vad

PASSO = 0.02


def mascara(ts, n):
    m = np.zeros(n, bool)
    for t in ts:
        m[int(t["start"] / PASSO):int(np.ceil(t["end"] / PASSO))] = True
    return m


def main():
    video, saida = sys.argv[1], sys.argv[2]
    modelo = load_silero_vad()
    wav = torch.from_numpy(whisperx.load_audio(video))       # ffmpeg (lê .mov/.mp4 do iPhone), 16 kHz mono
    n = int(len(wav) / 16000 / PASSO) + 1
    comum = dict(sampling_rate=16000, return_seconds=True, min_silence_duration_ms=60, min_speech_duration_ms=60)
    normal = get_speech_timestamps(wav, modelo, threshold=0.5, speech_pad_ms=20, **comum)
    suave = get_speech_timestamps(wav, modelo, threshold=0.25, speech_pad_ms=40, **comum)
    np.savez_compressed(saida, normal=mascara(normal, n), suave=mascara(suave, n))
    print(f"vad: {len(normal)} trechos de fala em {len(wav) / 16000:.1f}s")


if __name__ == "__main__":
    main()
