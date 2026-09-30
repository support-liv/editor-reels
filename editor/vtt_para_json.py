#!/usr/bin/env python3
"""Converte a legenda .vtt do YouTube na transcrição que o editor usa (editor/transcricoes/<nome do vídeo>.json).

    python3 editor/vtt_para_json.py "~/Downloads/LIVE.vtt" "~/Downloads/LIVE.mp4"

Serve para os cortes longos de lives compridas (evita rodar o Whisper em 1h+ de vídeo). O tempo de cada palavra é
distribuído dentro da frase da legenda, proporcional ao tamanho da palavra; o editor ainda ajusta os cortes pelo
áudio. Para shorts (sincronia fina do motion, tirar hesitações), recorte o trecho e deixe o Whisper transcrever.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))


def seg(ts):
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def converter(vtt):
    palavras, segmentos = [], []
    blocos = re.findall(r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)[^\n]*\n(.+?)(?:\n\n|\Z)", open(vtt, encoding="utf-8").read(), re.S)
    for a, b, texto in blocos:
        s, e = seg(a), seg(b)
        texto = re.sub(r"<[^>]+>", "", texto).replace("\n", " ").strip()
        ws = texto.split()
        if not ws:
            continue
        segmentos.append({"s": s, "e": e, "t": texto})
        pesos = [len(w) + 2 for w in ws]
        tot, t = sum(pesos), s
        for w, p in zip(ws, pesos):
            d = (e - s) * p / tot
            palavras.append({"w": w, "s": round(t, 3), "e": round(t + d * 0.92, 3)})
            t += d
    return {"palavras": palavras, "segmentos": segmentos, "fonte": "vtt"}


if __name__ == "__main__":
    vtt, video = os.path.expanduser(sys.argv[1]), os.path.expanduser(sys.argv[2])
    saida = os.path.join(AQUI, "transcricoes", os.path.splitext(os.path.basename(video))[0] + ".json")
    if os.path.exists(saida) and "--sobrescrever" not in sys.argv:
        sys.exit(f"já existe: {saida} (use --sobrescrever)")
    dados = converter(vtt)
    json.dump(dados, open(saida, "w"), ensure_ascii=False, indent=1)
    print(f"{len(dados['palavras'])} palavras -> {saida}")
