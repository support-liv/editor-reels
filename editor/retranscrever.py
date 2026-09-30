#!/usr/bin/env python3
"""Transcreve de novo só uma janela do vídeo e troca as palavras dela na transcrição do editor.

    python3 editor/retranscrever.py VIDEO INICIO FIM       # segundos do vídeo

Quando usar: o Whisper às vezes "pula" um pedaço (uma palavra esticada por vários segundos, ex. "estudar" de 23 a 30s,
e as frases do meio somem da legenda e do corte). O editor avisa essas palavras esticadas; rode isto na janela delas.
"""
import json, os, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def main():
    video, ini, fim = os.path.expanduser(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    cache = os.path.join(AQUI, "transcricoes", os.path.splitext(os.path.basename(video))[0] + ".json")
    dados = json.load(open(cache))
    wav = os.path.join(tempfile.mkdtemp(), "janela.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", video,
                    "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    import whisper
    res = whisper.load_model("medium").transcribe(wav, language="pt", word_timestamps=True, fp16=False,
                                                  condition_on_previous_text=False)
    novas = [{"w": w["word"].strip(), "s": round(ini + w["start"], 3), "e": round(ini + w["end"], 3)}
             for seg in res["segments"] for w in seg.get("words", [])]
    velhas = dados["palavras"]
    antes = [p for p in velhas if p["e"] <= ini + 0.05]
    depois = [p for p in velhas if p["s"] >= fim - 0.05]
    dados["palavras"] = antes + novas + depois
    json.dump(dados, open(cache, "w"), ensure_ascii=False, indent=1)
    print(f"{len(novas)} palavras em {ini:.1f}-{fim:.1f}s:", " ".join(p["w"] for p in novas))


if __name__ == "__main__":
    main()
