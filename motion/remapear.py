#!/usr/bin/env python3
"""Ajusta os tempos de um roteiro de motion quando o plano de cortes muda (ex.: tirar hesitações, respiro).

    python3 editor/editor_reels.py VIDEO [opções antigas] --json-cortes antes.json
    python3 editor/editor_reels.py VIDEO [opções novas]   --json-cortes depois.json
    python3 motion/remapear.py roteiro.json antes.json depois.json [--cauda 3.8]

Cada tempo do roteiro (t0, t1, t, risco_t, destaque_t, t dos itens) vira tempo no bruto pelo plano antigo e volta
pro vídeo pelo plano novo. Trecho que saiu cai no ponto mais próximo que ficou. A duração e o CTA acompanham."""
import json, sys


def saida_para_fonte(cortes, t):
    acc = 0.0
    for c in cortes:
        d = c["e"] - c["s"]
        if t < acc + d:
            return c["s"] + (t - acc)
        acc += d
    return cortes[-1]["e"] + (t - acc)                 # depois da fala (cauda do CTA)


def fonte_para_saida(cortes, f):
    acc = 0.0
    for c in cortes:
        if f < c["s"]:
            return acc                                 # caiu num trecho que saiu: vai pro começo do próximo
        if f <= c["e"]:
            return acc + (f - c["s"])
        acc += c["e"] - c["s"]
    return acc + (f - cortes[-1]["e"])


def main():
    rot, antes, depois = (json.load(open(x)) for x in sys.argv[1:4])
    cauda = float(sys.argv[sys.argv.index("--cauda") + 1]) if "--cauda" in sys.argv else 0.0
    fala_antes = sum(c["e"] - c["s"] for c in antes)
    fala_nova = sum(c["e"] - c["s"] for c in depois)
    m = lambda t: round(fonte_para_saida(depois, saida_para_fonte(antes, t)), 2) if t <= fala_antes else round(fala_nova + (t - fala_antes), 2)
    for c in rot["cenas"]:
        for k in ("t0", "t1"):
            c[k] = m(c[k])
        for e in c.get("elementos", []):
            for k in ("t", "risco_t", "destaque_t"):
                if k in e:
                    e[k] = m(e[k])
            for it in e.get("itens", []):
                for k in ("t", "risco_t", "destaque_t"):
                    if k in it:
                        it[k] = m(it[k])
        if c.get("t1", 0) >= fala_antes - 0.01 and c.get("tipo") != "cta":
            c["t1"] = round(fala_nova, 2)              # cena que ia até o fim da fala continua indo
    rot["fala"] = round(fala_nova, 2)
    rot["duracao"] = round(fala_nova + cauda, 2)
    for c in rot["cenas"]:
        if c.get("tipo") == "cta":
            c["t0"], c["t1"] = round(fala_nova + 0.35, 2), rot["duracao"]
    json.dump(rot, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    print(f"{sys.argv[1]}: fala {fala_antes:.2f}s -> {fala_nova:.2f}s")


if __name__ == "__main__":
    main()
