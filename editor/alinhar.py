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
    audio = whisperx.load_audio(video)
    dur = len(audio) / 16000
    # vídeo montado de vários takes (lote): cada palavra sabe de que pedaço veio e o alinhamento nunca passa da emenda.
    # Alinhando por cima da emenda, o WhisperX jogava a palavra pro take vizinho ("Unidos." terminando 0,3s dentro do
    # pedaço seguinte, "não é?" do R9 caindo no pedaço de depois) e o corte comia ou sobrava sílaba.
    pecas = dados.get("pedacos")
    peca = lambda i: pal[i].get("pedaco", 0) if pecas else 0
    limites = lambda i: tuple(pecas[peca(i)]) if pecas else (0.0, dur)
    # trechos para o alinhador: grupos de palavras separados por pausa > 0,8s (ou pela emenda)
    grupos, g = [], [0]
    for i in range(1, len(pal)):
        if pal[i]["s"] - pal[i - 1]["e"] > 0.8 or len(g) >= 40 or peca(i) != peca(i - 1):
            grupos.append(g); g = []
        g.append(i)
    grupos.append(g)
    # número na legenda ("2025,") vai pro alinhador como foi FALADO ("dois mil e vinte e cinco,", campo "falado" que o
    # lote grava): em dígito o alinhador não lê e empurrava as palavras seguintes pra dentro do número
    falado = lambda i: pal[i].get("falado") or pal[i]["w"]
    segs = []
    for g in grupos:
        lo, hi = limites(g[0])
        s = max(lo, pal[g[0]]["s"] - 0.4)
        e = min(hi, dur, max(pal[g[-1]]["e"] + 0.4, s + 0.2))
        segs.append({"start": s, "end": e, "text": " ".join(falado(i) for i in g)})
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
        partes = falado(i).split()
        for k in range(j, min(j + 3, len(ws))):
            bloco = ws[k:k + len(partes)]
            if len(bloco) == len(partes) and all(norm(a["word"]) == norm(b) for a, b in zip(bloco, partes)):
                if len(partes) == 1:
                    pares.append((i, ws[k]))
                elif all("start" in a and "end" in a for a in bloco):
                    pares.append((i, {"word": pal[i]["w"], "start": bloco[0]["start"], "end": bloco[-1]["end"]}))
                j = k + len(partes); break
    # trava: alinhamento que sai fora de ordem ou se afasta muito do Whisper é erro do alinhador (no R1 ele jogou a frase
    # final 4s pra trás e o corte acabou antes dela). Nesses casos fica o tempo do Whisper.
    # Palavra com número ("2025,", "E-2", "O-1", "PERFIL27") o alinhador não sabe ler: ele inventa o tempo pelos vizinhos
    # e o "2025," do R3 acabou 1s antes da hora (o corte comeu "mil e vinte e cinco"). Fica o tempo do Whisper.
    # Perto de palavra esticada do Whisper (>0,9s: "fortes," do R3 marcado com 1,8s) o tempo do Whisper das seguintes é
    # que está errado: ali o alinhador pode corrigir até 2s ("onde" estava 1,3s antes e saía como hesitação sem palavra).
    esticada = lambda k: 0 <= k < len(pal) and pal[k]["e"] - pal[k]["s"] > 0.9
    ult_s = -1.0
    validos = []
    for i, w in pares:
        lo, hi = limites(i)
        tolera = 2.0 if esticada(i - 1) or esticada(i) or esticada(i - 2) else 0.7
        if "start" in w and "end" in w and w["start"] >= ult_s - 0.02 and abs(w["start"] - pal[i]["s"]) <= tolera \
                and w["end"] > w["start"] and not any(ch.isdigit() for ch in falado(i)) \
                and lo - 0.01 <= w["start"] and w["end"] <= hi + 0.01:
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
