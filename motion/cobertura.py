#!/usr/bin/env python3
"""Quanto de cada short fica com motion: variado de propósito dentro de um lote (nunca tudo igual).

    python3 motion/cobertura.py plano --marca imigrar --fala L01=42.7 L02=37.4 ...   # antes de escrever os roteiros
    python3 motion/cobertura.py conferir projetos/<projeto>/motion/*.json              # depois: mede e avisa

`plano` sorteia uma meta de cobertura por short (fração da fala com motion), espalhada em faixas
(pouco / médio / muito) e embaralhada, e sugere quantas cenas. A meta é guia: o motion entra onde o assunto pede
ilustração (lista, número, etapa, comparação, processo, prazo); o resto da fala fica com a pessoa na tela.
Imigrar explora mais (faixa mais alta); LIV é mais contida.
`conferir` lê os roteiros prontos (sem contar o CTA) e reclama se o lote ficou padronizado.
"""
import argparse, glob, json, os, random, statistics as st

FAIXA = {"imigrar": (0.40, 0.90), "liv": (0.25, 0.70)}
SEG_CENA = 7.0                       # duração típica de uma cena de motion


def plano(falas, marca, semente=None):
    lo, hi = FAIXA[marca]
    rnd = random.Random(semente)
    n = len(falas)
    # estratificado: uma meta por faixa igual do intervalo, depois embaralha → o lote sempre varia
    metas = [lo + (hi - lo) * (i + rnd.random()) / n for i in range(n)]
    rnd.shuffle(metas)
    out = {}
    for (cid, fala), m in zip(falas.items(), metas):
        seg = m * fala
        out[cid] = {"meta": round(m, 2), "seg_motion": round(seg, 1), "cenas": max(1, round(seg / SEG_CENA))}
    return out


def cobertura(roteiro):
    r = json.load(open(roteiro))
    cenas = [c for c in r.get("cenas", []) if not any(e.get("tipo") == "cta" for e in c.get("elementos", []))]
    t_cta = min([c["t0"] for c in r.get("cenas", []) if c not in cenas] or [r.get("duracao", 0)])
    fala = t_cta if t_cta else r.get("duracao", 0)
    if not cenas or fala <= 0:
        return None
    return sum(c["t1"] - c["t0"] for c in cenas) / fala


def conferir(arquivos):
    res = [(os.path.basename(f)[:-5], cobertura(f)) for f in arquivos]
    res = [(k, v) for k, v in res if v is not None]
    if not res:
        print("nenhum roteiro com cenas"); return
    for k, v in res:
        print(f"  {k:12s} {v:4.0%} " + "█" * round(v * 30))
    vals = [v for _, v in res]
    dp = st.pstdev(vals) if len(vals) > 1 else 0
    print(f"lote: {len(vals)} shorts | média {st.mean(vals):.0%} | {min(vals):.0%}–{max(vals):.0%} | desvio {dp:.0%}")
    if len(vals) >= 3 and (dp < 0.12 or max(vals) - min(vals) < 0.30):
        print("⚠️  lote padronizado: varie mais (uns com pouco motion, outros com muito). Use `cobertura.py plano`.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plano"); p.add_argument("--marca", choices=FAIXA, required=True)
    p.add_argument("--fala", nargs="+", required=True, help="ID=segundos de fala"); p.add_argument("--semente")
    c = sub.add_parser("conferir"); c.add_argument("roteiros", nargs="+")
    a = ap.parse_args()
    if a.cmd == "plano":
        falas = {x.split("=")[0]: float(x.split("=")[1]) for x in a.fala}
        for cid, v in plano(falas, a.marca, a.semente).items():
            print(f"  {cid:8s} meta {v['meta']:4.0%}  ≈ {v['seg_motion']:4.1f}s de motion em ~{v['cenas']} cena(s)")
    else:
        conferir(sorted(set(sum((glob.glob(x) for x in a.roteiros), []))))
