"""Alinhamento forçado das palavras (WhisperX + wav2vec2 em português): refaz o tempo de cada palavra da transcrição
com precisão de ~20-50 ms. O Whisper marca o tempo das palavras "no olho" (erra 0,1-0,5s, pior em palavra curta como
"ou", "é", "mas"), e o corte comia palavra. Roda no ambiente separado .venv-whisperx (o editor chama sozinho).

Uso: .venv-whisperx/bin/python editor/alinhar.py VIDEO TRANSCRICAO.json
     Reescreve a transcrição (guarda a original em .whisper.json). Palavra que o alinhador não acha (número escrito
     em dígito, sigla) fica com o tempo do Whisper.
"""
import json, os, shutil, sys

import whisperx


def main():
    video, arq = sys.argv[1], sys.argv[2]
    dados = json.load(open(arq))
    pal = dados["palavras"]
    if not pal:
        return
    # trechos para o alinhador: grupos de palavras separados por pausa > 0,8s
    grupos, g = [], [0]
    for i in range(1, len(pal)):
        if pal[i]["s"] - pal[i - 1]["e"] > 0.8 or len(g) >= 40:
            grupos.append(g); g = []
        g.append(i)
    grupos.append(g)
    audio = whisperx.load_audio(video)
    dur = len(audio) / 16000
    segs = []
    for g in grupos:
        s = max(0.0, pal[g[0]]["s"] - 0.4)
        e = min(dur, pal[g[-1]]["e"] + 0.4)
        segs.append({"start": s, "end": e, "text": " ".join(pal[i]["w"] for i in g)})
    modelo, meta = whisperx.load_align_model(language_code="pt", device="cpu")
    res = whisperx.align(segs, modelo, meta, audio, "cpu", return_char_alignments=False)
    mudou = 0
    # o WhisperX quebra cada trecho em frases: junta tudo na ordem e casa palavra a palavra com a transcrição
    ws = [w for sg in res["segments"] for w in sg.get("words", [])]
    if len(ws) != len(pal):
        print(f"  aviso: alinhador devolveu {len(ws)} palavras para {len(pal)}; casando pelo texto")
    j = 0
    pares = []
    norm = lambda t: "".join(ch for ch in t.lower() if ch.isalnum())
    for i in range(len(pal)):                         # casa pelo texto, tolerando palavra que sobra/falta
        for k in range(j, min(j + 3, len(ws))):
            if norm(ws[k]["word"]) == norm(pal[i]["w"]):
                pares.append((i, ws[k])); j = k + 1; break
    # trava: alinhamento que sai fora de ordem ou se afasta muito do Whisper é erro do alinhador (no R1 ele jogou a frase
    # final 4s pra trás e o corte acabou antes dela). Nesses casos fica o tempo do Whisper.
    ult_s = -1.0
    validos = []
    for i, w in pares:
        if "start" in w and "end" in w and w["start"] >= ult_s - 0.02 and abs(w["start"] - pal[i]["s"]) <= 0.7 \
                and w["end"] > w["start"]:
            validos.append((i, w)); ult_s = w["start"]
    pares = validos
    for i, w in pares:
        if "start" in w and "end" in w:
            if abs(pal[i]["s"] - w["start"]) > 0.03 or abs(pal[i]["e"] - w["end"]) > 0.03:
                mudou += 1
            pal[i]["s_whisper"], pal[i]["e_whisper"] = pal[i]["s"], pal[i]["e"]
            pal[i]["s"], pal[i]["e"] = round(w["start"], 3), round(w["end"], 3)
            pal[i]["alinhada"] = True
    if not os.path.exists(arq.replace(".json", ".whisper.json")):
        shutil.copy(arq, arq.replace(".json", ".whisper.json"))
    json.dump(dados, open(arq, "w"), ensure_ascii=False, indent=1)
    n = sum(1 for p in pal if p.get("alinhada"))
    print(f"alinhado: {n}/{len(pal)} palavras ({mudou} com tempo corrigido) em {os.path.basename(arq)}")


if __name__ == "__main__":
    main()
