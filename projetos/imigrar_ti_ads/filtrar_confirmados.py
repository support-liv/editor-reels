"""Segunda peneira da auditoria: de cada alerta conferido (conferir_alertas.py), fica só o que as DUAS leituras curtas
(literal e normal) mostram igual em relação ao esperado: a mesma palavra faltando ou sobrando."""
import difflib, re, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
from auditar_fala import norm
from auditoria import NUMERICAS

def toks(t):
    return [n for n in (norm(w) for w in t.split()) if n]

def difs(esp, ouv):
    out = set()
    sm = difflib.SequenceMatcher(a=esp, b=ouv, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        e, o = tuple(esp[i1:i2]), tuple(ouv[j1:j2])
        if any(x in NUMERICAS or any(ch.isdigit() for ch in x) for x in e + o):
            continue
        out.add((op, e, o))
    return out

bloco, video = [], None
for ln in open(sys.argv[1]):
    if ln.startswith("=== "):
        video = ln[4:].strip(); continue
    m = re.match(r"\s+esperado: (.*)", ln)
    if m: esp = m.group(1); continue
    m = re.match(r"\s+literal : (.*)", ln)
    if m: lit = m.group(1); continue
    m = re.match(r"\s+normal  : (.*)", ln)
    if m:
        nor = m.group(1)
        e = toks(esp)
        # descarta a 1ª e a última palavra (a janela corta no meio delas)
        a, b = difs(e, toks(lit)), difs(e, toks(nor))
        comuns = {d for d in a & b if not (d[0] == "insert" and len(d[2]) == 1 and len(d[2][0]) <= 1)}
        # só conta diferença no miolo (não nas 2 primeiras/últimas palavras esperadas, que a janela corta)
        miolo = set(e[2:-2])
        comuns = {d for d in comuns if (d[1] and set(d[1]) & miolo) or (d[0] == "insert")}
        if comuns:
            print(f"{video} | esperado: {esp}\n   literal: {lit}\n   normal : {nor}\n   -> {sorted(comuns)}")
    m = re.match(r"\s+([\d.]+)s ", ln)
    if m: t = m.group(1); print_t = t
