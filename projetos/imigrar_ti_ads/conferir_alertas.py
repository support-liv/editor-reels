"""Confere cada alerta da auditoria numa janela curta (±1,5s) do vídeo pronto, ouvida em modo literal e normal,
ao lado do que deveria ser dito ali. Entrada: o relatório do auditoria.py.

Uso: python3 projetos/imigrar_ti_ads/conferir_alertas.py RELATORIO.txt PASTA_PRONTOS [PASTA ...]
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import auditar_fala as A
from lote_ti import ESPERADO


def main():
    rel, pastas = sys.argv[1], sys.argv[2:]
    video = None
    for ln in open(rel):
        m = re.match(r"=== (\S+): ", ln)
        if m:
            nome = m.group(1)
            video = next((os.path.join(p, nome + ".mp4") for p in pastas if os.path.exists(os.path.join(p, nome + ".mp4"))), None)
            pal = json.load(open(os.path.join(ESPERADO, nome + ".palavras.json"))) if video else []
            print(f"\n=== {nome}")
            continue
        m = re.match(r"\s+([\d.]+)s (\S+ ?\S*)\s+esperado: «(.*)»  ouvido: «(.*?)»", ln)
        if not (m and video):
            continue
        t = float(m.group(1))
        a, b = max(0.0, t - 1.5), t + 1.5
        esp = " ".join(p["w"] for p in pal if a <= p["t"] < b)
        lit = " ".join(w["w"] for w in A.transcrever_janela(video, a, b, literal=True))
        nor = " ".join(w["w"] for w in A.transcrever_janela(video, a, b, literal=False))
        print(f"  {t:6.2f}s {m.group(2)} «{m.group(3)}»→«{m.group(4)[:40]}»\n"
              f"      esperado: {esp}\n      literal : {lit}\n      normal  : {nor}")


if __name__ == "__main__":
    main()
