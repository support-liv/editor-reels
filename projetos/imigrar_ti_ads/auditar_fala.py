"""Auditoria de fala: transcreve cada pedaço escolhido SOZINHO (o Whisper "engole" repetições curtas quando
transcreve o take inteiro) e aponta repetições ("sabia que, sabia que", "mais de... mais de") e palavras cortadas.

Uso:
  python3 projetos/imigrar_ti_ads/auditar_fala.py pedacos [id ...]   # pedaços dos anúncios (antes de renderizar)
  python3 projetos/imigrar_ti_ads/auditar_fala.py prontos ARQ.mp4 ...  # vídeo pronto inteiro, em janelas de ~6s
As palavras de cada pedaço ficam em cache e o lote_ti.py usa elas no lugar da transcrição do take inteiro.
"""
import json, os, re, subprocess, sys, tempfile, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
sys.path.insert(0, os.path.join(AQUI, "..", "..", "editor"))
import plataforma as PLAT

CACHE = PLAT.pasta_cache("ti_pedacos_literal")
_modelo = None


def modelo():
    global _modelo
    if _modelo is None:
        import whisper
        _modelo = whisper.load_model("medium")
    return _modelo


def max_iguais(ws):
    m = n = 0
    for a, b in zip(ws, ws[1:]):
        n = n + 1 if norm(a["w"]) == norm(b["w"]) else 0
        m = max(m, n)
    return m + 1 if ws else 0


def transcrever_janela(src, ini, fim, literal=True):
    """palavras (tempo absoluto no arquivo) da janela ini-fim, transcrita sozinha. Cache por janela."""
    chave = f"{os.path.basename(src)}_{ini:.3f}_{fim:.3f}{'' if literal else '_limpo'}.json"
    cache = os.path.join(CACHE, chave)
    if os.path.exists(cache):
        return json.load(open(cache))
    wav = os.path.join(tempfile.mkdtemp(), "p.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", src,
                    "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    from transcrever_literal import PROMPT                  # modo literal: mostra as repetições
    r = modelo().transcribe(wav, language="pt", word_timestamps=True, fp16=False, condition_on_previous_text=False,
                            temperature=0.0, initial_prompt=PROMPT if literal else None)
    ws = [{"w": x["word"].strip(), "s": round(ini + x["start"], 3), "e": round(ini + x["end"], 3)}
          for sg in r["segments"] for x in sg.get("words", [])]
    json.dump(ws, open(cache, "w"), ensure_ascii=False)
    return ws


def norm(w):
    w = unicodedata.normalize("NFKD", w.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in w if not unicodedata.combining(c)))


def repeticoes(ws):
    """[(i, n)] onde as n palavras a partir de i se repetem logo em seguida (n=1..5), ou com 1 palavra no meio."""
    t = [norm(w["w"]) for w in ws]
    achou = []
    for n in range(5, 0, -1):
        for i in range(len(t) - 2 * n + 1):
            a = t[i:i + n]
            if not all(a) or (n == 1 and len(a[0]) <= 2):
                continue
            if a == t[i + n:i + 2 * n] or (n >= 2 and a == t[i + n + 1:i + 2 * n + 1]):
                if not any(i < j + m and j < i + n for j, m in achou):
                    achou.append((i, n))
    return achou


def mostrar(ws, rotulo):
    reps = repeticoes(ws)
    marcas = {}
    for i, n in reps:
        for k in range(i, i + n):
            marcas[k] = True
    texto = " ".join(("⟦" + w["w"] + "⟧") if k in marcas else w["w"] for k, w in enumerate(ws))
    print(f"{'⚠ ' if reps else '  '}{rotulo}: {texto}")
    for i, n in reps:
        print(f"      repetição: '{' '.join(w['w'] for w in ws[i:i + n])}' em {ws[i]['s']:.2f}s e {ws[i + n]['s']:.2f}s")
    return reps


def main():
    modo = sys.argv[1]
    if modo == "pedacos":
        import lote_ti as LT
        ids = sys.argv[2:] or list(LT.ANUNCIOS)
        for id_ in ids:
            print(f"\n=== {id_}")
            for arq, a, b in LT.ANUNCIOS[id_][1]:
                ini, fim, _ = LT.faixa(arq, a, b)
                ws = transcrever_janela(os.path.join(LT.BRUTOS, arq), ini, fim)
                mostrar(ws, f"{arq} {ini:.2f}-{fim:.2f}")
    else:
        for arq in sys.argv[2:]:
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                       capture_output=True, text=True).stdout)
            ws, t = [], 0.0
            while t < dur - 0.3:
                # janelas de 6,5s que se sobrepõem 0,5s: cada palavra fica só na janela onde ela COMEÇA depois da
                # metade da sobreposição (antes, a mesma palavra entrava duas vezes e parecia repetição)
                jan = transcrever_janela(arq, t, min(dur, t + 6.5))
                if max_iguais(jan) >= 5:                # alucinação do prompt literal ("e, e, e, ..."): sem prompt
                    jan = transcrever_janela(arq, t, min(dur, t + 6.5), literal=False)
                ws += [w for w in jan if (t == 0 or w["s"] >= t + 0.25) and w["s"] < t + 6.25]
                t += 6.0
            print(f"\n=== {os.path.basename(arq)}")
            mostrar(ws, "texto")


if __name__ == "__main__":
    main()
