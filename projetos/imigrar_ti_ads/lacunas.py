"""Acha fala que o Whisper não transcreveu (repetições "engolidas": "sabia que, sabia que", "mais de... mais de")
e transcreve de novo só essas janelas, trocando as palavras na transcrição do editor.

O Whisper costuma esticar uma palavra por cima da repetição (ex.: "de" de 240,0 a 241,9s) ou deixar um buraco entre
duas palavras com voz no meio. Aqui medimos a voz (energia) e comparamos com o tempo coberto pelas palavras.

Uso: python3 projetos/imigrar_ti_ads/lacunas.py ARQUIVO [ARQUIVO ...]     (só relata: --aplicar para trocar)
"""
import json, os, shutil, subprocess, sys, tempfile
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
TRANSC = os.path.join(AQUI, "..", "..", "editor", "transcricoes")
BRUTOS = "/Users/lucastoledo/Downloads/imigrar/ads/TI"
SR = 16000
HOP = 160                                                  # 10 ms


def voz(arq):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    n = len(x) // HOP
    rms = np.sqrt((x[:n * HOP].reshape(n, HOP) ** 2).mean(1) + 1e-12)
    db = 20 * np.log10(rms)
    limiar = max(np.percentile(db, 30) + 12, np.percentile(db, 95) - 28)
    return db > limiar


def suspeitas(ws, v):
    """janelas (ini, fim) com voz sem palavra: buraco entre palavras ou palavra esticada."""
    out = []
    def voz_em(a, b):
        return v[int(a * 100):int(b * 100)].sum() / 100.0
    for i in range(len(ws) - 1):
        a, b = ws[i]["e"], ws[i + 1]["s"]
        if b - a > 0.45 and voz_em(a + 0.08, b - 0.08) > 0.30:
            out.append((ws[i]["s"], ws[i + 1]["e"], "buraco"))
    for w in ws:
        d = w["e"] - w["s"]
        if d > 0.85 and voz_em(w["s"] + 0.45, w["e"]) > 0.35:
            out.append((w["s"], w["e"], "esticada"))
    out.sort()
    juntas = []
    for a, b, t in out:                                   # junta janelas encostadas
        if juntas and a <= juntas[-1][1] + 0.3:
            juntas[-1] = (juntas[-1][0], max(b, juntas[-1][1]), juntas[-1][2] + "+" + t)
        else:
            juntas.append((a, b, t))
    return juntas


def main():
    aplicar = "--aplicar" in sys.argv
    arqs = [a for a in sys.argv[1:] if not a.startswith("--")]
    modelo = None
    for arq in arqs:
        src = os.path.join(BRUTOS, arq)
        base = os.path.splitext(arq)[0]
        cache = os.path.join(TRANSC, base + ".json")
        dados = json.load(open(cache))
        ws = dados["palavras"]
        js = suspeitas(ws, voz(src))
        print(f"\n== {arq}: {len(js)} janela(s)")
        if not js:
            continue
        if aplicar and not os.path.exists(cache + ".orig"):
            shutil.copy(cache, cache + ".orig")
        for a, b, tipo in js:
            antes = " ".join(w["w"] for w in ws if a - 0.01 <= w["s"] <= b)
            if not aplicar:
                print(f"  {a:7.2f}-{b:7.2f} [{tipo}] {antes}")
                continue
            if modelo is None:
                import whisper
                modelo = whisper.load_model("medium")
            ini, fim = max(0.0, a - 0.25), b + 0.25
            wav = os.path.join(tempfile.mkdtemp(), "j.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", src,
                            "-vn", "-ac", "1", "-ar", str(SR), wav], check=True)
            r = modelo.transcribe(wav, language="pt", word_timestamps=True, fp16=False, condition_on_previous_text=False)
            novas = [{"w": x["word"].strip(), "s": round(ini + x["start"], 3), "e": round(ini + x["end"], 3)}
                     for sg in r["segments"] for x in sg.get("words", [])]
            novas = [p for p in novas if a - 0.05 <= p["s"] <= b + 0.05]
            if not novas:
                print(f"  {a:7.2f}-{b:7.2f} [{tipo}] {antes}  →  (nada)")
                continue
            ws = [p for p in ws if not (a - 0.05 <= p["s"] <= b + 0.05)] + novas
            ws.sort(key=lambda p: p["s"])
            print(f"  {a:7.2f}-{b:7.2f} [{tipo}] {antes}  →  {' '.join(p['w'] for p in novas)}")
        if aplicar:
            dados["palavras"] = ws
            json.dump(dados, open(cache, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
