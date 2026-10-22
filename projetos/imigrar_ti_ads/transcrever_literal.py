"""Transcrição LITERAL (com repetições e hesitações) para escolher takes sem fala errada.

O Whisper limpa a fala por padrão: "sabia que o salário, sabia que o salário" vira um só, e a repetição fica
escondida dentro do tempo de uma palavra (ex.: "que" de 7,70 a 9,38s). Um initial_prompt cheio de hesitações faz
ele transcrever o que foi dito de verdade. Salva <base>.literal.json em editor/transcricoes/ (mesmo formato).

Uso: python3 projetos/imigrar_ti_ads/transcrever_literal.py VIDEO [VIDEO ...] [--como-principal]
     --como-principal: grava também como <base>.json (o cache que o editor usa).
"""
import json, os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
TRANSC = os.path.join(AQUI, "..", "..", "editor", "transcricoes")
PROMPT = ("Então, é... sabia que, sabia que o, o salário... mais de, mais de cem mil, tipo, é, é, "
          "quer saber, quer saber se você, toque, toque no botão.")


def main():
    principal = "--como-principal" in sys.argv
    videos = [v for v in sys.argv[1:] if not v.startswith("--")]
    import whisper
    m = whisper.load_model("medium")
    for v in videos:
        base = os.path.splitext(os.path.basename(v))[0]
        out = os.path.join(TRANSC, base + ".literal.json")
        if os.path.exists(out):
            print("já tem", base, flush=True)
            continue
        wav = os.path.join(tempfile.mkdtemp(), "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
        r = m.transcribe(wav, language="pt", word_timestamps=True, fp16=False, condition_on_previous_text=False,
                         initial_prompt=PROMPT, temperature=0.0)
        ws = [{"w": w["word"].strip(), "s": round(w["start"], 3), "e": round(w["end"], 3)}
              for s in r["segments"] for w in s.get("words", [])]
        dados = {"texto": r["text"].strip(), "palavras": ws,
                 "segmentos": [{"s": s["start"], "e": s["end"], "t": s["text"].strip()} for s in r["segments"]]}
        json.dump(dados, open(out, "w"), ensure_ascii=False, indent=1)
        if principal:
            shutil.copy(out, os.path.join(TRANSC, base + ".json"))
        print("ok", base, len(ws), "palavras", flush=True)


if __name__ == "__main__":
    main()
