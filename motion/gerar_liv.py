#!/usr/bin/env python3
"""Gera o HTML de um B-roll da LIV (clean, só elementos do manual) a partir de um roteiro JSON.

    python3 motion/gerar_liv.py roteiro.json            -> motion/modelos/<nome>.html
    npx hyperframes render . -c modelos/<nome>.html --format mov -o renders/<nome>.mov

Roteiro:
{
  "nome": "live80_S1", "duracao": 34.2, "largura": 1080, "altura": 1920,
  "cenas": [
    {"t0": 5.6, "t1": 13.3, "painel": "cheio",          # cheio | baixo | cima (tela dividida: cobre só uma metade)
     "cor": "azul",                                       # azul | bege | laranja
     "elementos": [
        {"tipo": "rotulo", "texto": "processo consular", "y": 250, "t": 6.0},
        {"tipo": "linha", "texto": "Na prática,", "y": 360, "t": 6.84, "cor": "texto", "tam": 124},
        {"tipo": "linha", "texto": "não muda nada.", "y": 490, "t": 11.75, "cor": "destaque"},
        {"tipo": "sub", "y": 640, "largura": 380, "t": 12.1},
        {"tipo": "risco", "y": 560, "largura": 600, "t": 9.0},
        {"tipo": "icone", "icone": "seta_dupla|seta_contorno|arco_duplo|estrela|losangos|fio_arco", "x": 96, "y": 700, "tam": 180, "t": 8.0}
     ]},
    {"tipo": "cta", "t0": 30.2, "t1": 34.2, "painel": "baixo", "palavra": "PERFIL27", "texto": "para uma análise de perfil gratuita"}
  ]
}
Ritmo (regra do time): a cena entra ~0,3s antes da 1ª palavra que mostra, no máximo 2s entre elementos e sai ~1s
depois do último; se a fala pausa, a cena sai. Tela dividida ("tela_dividida": true): sempre painel "cheio".
CTA depois da fala final: roteiro com "duracao" = fala + cauda e o CTA na cauda (editor --cauda).
Tudo em coordenadas da tela (px). Cores e fonte só as do manual. Cada elemento já leva o som discreto dele.
Zona segura: x 60-1020, y 153-1510, sem o canto dos botões (x > 835, y > 1205). Com o motion na tela o editor tira a
legenda, e o bloco de cada cena é centralizado na vertical entre 200 e 1300 px (as posições y do roteiro valem só
como espaçamento entre os elementos). ~1 em 4 cenas sai centralizada na horizontal ("alinhar": "esquerda"|"centro" força).
"""
import html, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
COR = {"azul": "#2c3642", "laranja": "#ff6e1f", "marrom": "#945943", "bege": "#fff0e6", "branco": "#ffffff"}
# por fundo: (fundo, texto, destaque, rótulo, borda da curva)
FUNDOS = {"azul": ("azul", "bege", "laranja", "bege", "laranja"),
          "bege": ("bege", "azul", "laranja", "marrom", "laranja"),
          "laranja": ("laranja", "branco", "azul", "branco", "azul")}
ICONES = {
    "seta_dupla": ('0 0 300 170', '<path d="M0 0 L85 85 L0 170 H70 L155 85 L70 0 Z M140 0 L225 85 L140 170 H210 L295 85 L210 0 Z" fill="{d}"/>'),
    "seta_contorno": ('0 0 220 130', '<path d="M4 4 L64 65 L4 126 M64 4 L124 65 L64 126 M4 4 H64 M4 126 H64 M64 4 H124 M64 126 H124" stroke="{t}" stroke-width="3" fill="none"/>'),
    "arco_duplo": ('0 0 200 200', '<path d="M0 95V60h40a60 60 0 0 1 120 0h40v35h-40a60 60 0 0 0-120 0zM0 200v-35h40a60 60 0 0 1 120 0h40v35h-40a60 60 0 0 0-120 0z" fill="{d}"/>'),
    "estrela": ('0 0 200 200', '<circle cx="100" cy="100" r="100" fill="{d}"/><path d="M100 8C100 64 136 100 192 100 136 100 100 136 100 192 100 136 64 100 8 100 64 100 100 64 100 8z" fill="{f}"/>'),
    "losangos": ('0 0 46 28', '<path d="M0 14 11 0 22 14 11 28zM24 14 35 0 46 14 35 28z" fill="{d}"/>'),
    "fio_arco": ('0 0 1080 200', '<path d="M0 170 H 1080 M620 170 C 700 150, 760 90, 780 0 C 800 90, 860 150, 940 170" stroke="{r}" stroke-width="3" fill="none"/>'),
}


import unicodedata, re as _re


def _norm(w):
    w = unicodedata.normalize("NFD", w.lower())
    return _re.sub(r"[^a-z0-9]", "", "".join(ch for ch in w if unicodedata.category(ch) != "Mn"))


def sincronizar(texto, t, falas):
    """tempo de cada palavra da linha, casando com a fala (Whisper) a partir de t; o que não foi dito literalmente
    (resumo, bandeira) é distribuído entre os vizinhos. Sem falas: tudo em t."""
    toks = texto.split()
    if not falas:
        return [t] * len(toks)
    cand = [f for f in falas if f["t"] >= t - 0.8][:40]
    tempos, j = [None] * len(toks), 0
    for k, tok in enumerate(toks):
        n = _norm(tok)
        if not n:
            continue
        for jj in range(j, min(len(cand), j + (7 if j else 12))):   # 1ª palavra: janela maior
            if _norm(cand[jj]["w"]) == n:
                tempos[k], j = cand[jj]["t"], jj + 1
                break
    conhecidos = [(k, v) for k, v in enumerate(tempos) if v is not None]
    if not conhecidos:
        return [t + 0.14 * k for k in range(len(toks))]
    prim = min(conhecidos[0][1], t) if conhecidos[0][0] > 0 else conhecidos[0][1]
    for k in range(len(toks)):                           # preenche os buracos
        if tempos[k] is None:
            ant = max([(kk, v) for kk, v in conhecidos if kk < k], default=None)
            pos = min([(kk, v) for kk, v in conhecidos if kk > k], default=None)
            if ant and pos:
                tempos[k] = ant[1] + (pos[1] - ant[1]) * (k - ant[0]) / (pos[0] - ant[0])
            elif ant:
                tempos[k] = ant[1] + 0.14 * (k - ant[0])
            else:
                tempos[k] = prim + 0.12 * k
    for k in range(1, len(tempos)):                      # nunca volta no tempo
        tempos[k] = max(tempos[k], tempos[k - 1] + 0.06)
    return [round(v, 2) for v in tempos]


def preparar(r, pasta):
    """carrega as palavras da fala (--json-palavras) e resolve o tempo de cada palavra das linhas."""
    falas = json.load(open(os.path.join(pasta, r["palavras"]))) if r.get("palavras") else []
    for c in r["cenas"]:
        for e in c.get("elementos", []):
            if e["tipo"] == "linha" and falas and e.get("sync", True):
                e["_tempos"] = sincronizar(e["texto"], e["t"], falas)
            for it in e.get("itens", []):
                if falas and it.get("texto"):
                    it["_tempos"] = sincronizar(it["texto"], it["t"], falas)
        # fala em outra ordem que o texto: a linha entra seguida (0,12s por palavra) em vez de ficar pela metade,
        # entrar depois da linha seguinte ou depois que a cena sai
        els = c.get("elementos", [])
        objs = [e for e in els if e.get("_tempos")] + [it for e in els for it in e.get("itens", []) if it.get("_tempos")]
        for k, o in enumerate(objs):
            n, teto = len(o["_tempos"]), c["t1"] - 0.45
            prox = [x["_tempos"][0] for x in objs[k + 1:] if x in els and o in els]
            if o["_tempos"][-1] > teto + 0.01 or (prox and o["_tempos"][-1] > min(prox) + 0.3):
                ini = min(o["_tempos"][0], teto - 0.12 * (n - 1))
                o["_tempos"] = [round(ini + 0.12 * q, 2) for q in range(n)]
            o["_tempos"] = [max(v, round(c["t0"] - 0.1 + 0.06 * q, 2)) for q, v in enumerate(o["_tempos"])]   # nada antes do painel chegar
        c["_batidas"] = batidas(c, falas)
    return r


def revelacoes(c):
    """todos os instantes em que algo novo acontece na cena (palavras, itens, traços, batidas)."""
    els = c.get("elementos", [])
    return sorted([tk for e in els for tk in e.get("_tempos", [])] +
                  [e.get("t", c["t0"]) for e in els if "itens" not in e and "_tempos" not in e] +
                  [it[k] for e in els for it in e.get("itens", []) for k in ("t", "risco_t", "destaque_t") if k in it] +
                  [tk for e in els for it in e.get("itens", []) for tk in it.get("_tempos", [])] +
                  [e["t"] + e.get("dur", 0) for e in els if e["tipo"] in ("rota", "anel", "contador")] +
                  [b["t"] for b in c.get("_batidas", [])])


LETRA_ITEM = {"etapas": "t", "checklist": "r", "degraus": "l", "barra": "l", "colunas": "c"}   # id do texto de cada item


def batidas(c, falas):
    """preenche o que sobrou parado (fala seguindo sem texto novo) com acentos discretos no tempo de uma palavra dita:
    'foco' (as linhas anteriores recuam e a última fica em evidência) ou 'fio' (fio fino se desenha sob a última linha).
    Tudo dentro do manual da LIV: nada de elemento novo inventado."""
    if c.get("tipo") == "cta" or c.get("batidas") is False:
        return []
    els = c.get("elementos", [])
    linhas = [(ei, (e.get("_tempos") or [e.get("t", c["t0"])])[0]) for ei, e in enumerate(els) if e["tipo"] == "linha"]
    itens = [(ei, i, it["t"]) for ei, e in enumerate(els) if e["tipo"] in LETRA_ITEM for i, it in enumerate(e.get("itens", [])) if it.get("texto")]
    ja_tem_fio = {e.get("sob") for e in els if e["tipo"] == "sub"}
    usados, out = set(), []
    for _ in range(6):
        ts = revelacoes(dict(c, _batidas=out))
        buracos = [(a, b) for a, b in zip(ts, ts[1:]) if b - a > 1.2] + ([(ts[-1], c["t1"])] if ts and c["t1"] - ts[-1] > 1.1 else [])
        if not buracos:
            break
        a, b = max(buracos, key=lambda ab: ab[1] - ab[0])
        meio = (a + b) / 2
        ditas = [f["t"] for f in falas if a + 0.45 < f["t"] < b - 0.3]
        tb = round(min(ditas, key=lambda x: abs(x - meio)) if ditas else meio, 2)
        antes = [ei for ei, t in linhas if t < tb - 0.2]
        if len(antes) >= 2 and ("foco", antes[-1]) not in usados:
            usados.add(("foco", antes[-1])); out.append({"t": tb, "tipo": "foco", "manter": antes[-1], "recuar": antes[:-1]})
        elif antes and ("fio", antes[-1]) not in usados and antes[-1] not in ja_tem_fio:
            usados.add(("fio", antes[-1])); out.append({"t": tb, "tipo": "fio", "alvo": antes[-1]})
        elif [x for x in itens if x[2] < tb - 0.3 and ("item", x[:2]) not in usados]:
            ei, i, _ = [x for x in itens if x[2] < tb - 0.3 and ("item", x[:2]) not in usados][-1]
            usados.add(("item", (ei, i))); out.append({"t": tb, "tipo": "item", "el": ei, "item": i, "letra": LETRA_ITEM[els[ei]["tipo"]]})
        elif not any(u[0] == "pulso" for u in usados):
            usados.add(("pulso", 0)); out.append({"t": tb, "tipo": "pulso"})
        else:
            break
    return out


def alinhamento(c, i):
    """a maioria alinhada à esquerda; ~1 em 4 cenas centralizada (fixo por cena, reproduzível). CTA: esquerda."""
    if c.get("tipo") == "cta":
        return False
    if "alinhar" in c:
        return c["alinhar"] == "centro"
    return i % 4 == 2


def extensao(e):
    if e["tipo"] == "linha":
        return e["y"], e["y"] + e.get("tam", 124) * 1.05
    if e["tipo"] == "rotulo":
        return e["y"], e["y"] + 44
    if e["tipo"] == "etapas":
        return e["y"], e["y"] + len(e["itens"]) * e.get("passo", 118)
    if e["tipo"] == "checklist":
        return e["y"], e["y"] + len(e["itens"]) * e.get("passo", 104)
    if e["tipo"] == "rota":
        return e["y"], e["y"] + 380
    if e["tipo"] == "anel":
        return e["y"], e["y"] + 300 + (70 if e.get("legenda") else 0)
    if e["tipo"] == "contador":
        return e["y"], e["y"] + e.get("tam", 150) * 1.05
    if e["tipo"] == "cartoes":
        return e["y"], e["y"] + e.get("alt", 300)
    if e["tipo"] == "degraus":
        return e["y"], e["y"] + 420
    if e["tipo"] == "barra":
        return e["y"], e["y"] + 190
    if e["tipo"] == "colunas":
        return e["y"], e["y"] + e.get("alt", 300)
    if e["tipo"] == "numero":
        return e["y"], e["y"] + e.get("tam", 340) * 0.95
    if e["tipo"] == "icone":
        vb = ICONES[e["icone"]][0].split()
        return e["y"], e["y"] + (200 if e["icone"] == "fio_arco" else e.get("tam", 160) * float(vb[3]) / float(vb[2]))
    return e["y"], e["y"] + 10


def centralizar_vertical(els, topo=200, base=1300):
    """sem legenda por cima do motion, o bloco da cena fica no meio da zona segura (não espremido no topo)."""
    if not els:
        return
    textos = [extensao(e)[1] for e in els if e["tipo"] != "icone"]
    if textos:                                       # ícone que ficou lá embaixo (longe da divisa) volta pra perto do texto
        for e in els:
            if e["tipo"] == "icone" and e["y"] > max(textos) + 150:
                e["y"] = round(max(textos) + 70)
    y0 = min(extensao(e)[0] for e in els)
    y1 = max(extensao(e)[1] for e in els)
    desloc = (topo + base) / 2 - (y0 + y1) / 2
    desloc = min(max(desloc, topo - y0), base - y1)
    for e in els:
        e["y"] = round(e["y"] + desloc)


def painel_geo(modo, H):
    """(top, altura, path da forma, path da borda, y inicial, y final) do painel."""
    if modo == "cheio":
        # as duas curvas (e o fio laranja de 16px) ficam 30px pra fora da tela quando a cena está parada: sem filete
        h = H + 660
        return (-330, h, f"M0 300 C 300 300, 760 210, 1080 0 L1080 {h - 300} C 760 {h - 90}, 300 {h}, 0 {h} Z",
                "M0 300 C 300 300, 760 210, 1080 0", h, -h)
    if modo == "baixo":
        top = 1020; h = H - top + 40
        return (top, h, f"M0 120 C 300 120, 760 60, 1080 0 L1080 {h} L0 {h} Z", "M0 120 C 300 120, 760 60, 1080 0", h, h)
    h = 900
    return (0, h, f"M0 0 H1080 V{h - 120} C 760 {h - 60}, 300 {h}, 0 {h} Z", f"M1080 {h - 120} C 760 {h - 60}, 300 {h}, 0 {h}", -h, -h)


# ---------------------------------------------------------------- componentes de "jornada" (clean: chapados, traço fino,
# cores do manual, sem sombra/brilho/partícula; movimento leve: traço se desenhando, ponto acendendo, número contando)
SEC = {"azul": "rgba(255,240,230,0.28)", "bege": "rgba(44,54,66,0.22)", "laranja": "rgba(255,255,255,0.35)"}
CARTAO = {"azul": ("bege", "azul"), "bege": ("azul", "bege"), "laranja": ("branco", "azul")}   # (fundo do card, texto)


def _pals(texto, pref, tempos, js, modo="entra"):
    """texto em palavras (spans) animadas cada uma no seu tempo: 'entra' (sobe e aparece) ou 'acende' (de apagada a cheia)."""
    ws = texto.split()
    tempos = tempos or [None] * len(ws)
    out = []
    for k, w in enumerate(ws):
        out.append(f'<span id="{pref}{k}" style="display:inline-block;opacity:{0.35 if modo == "acende" else 0}">{html.escape(w)}</span>')
        if tempos[k] is not None:
            if modo == "acende":
                js.append(f'tl.to("#{pref}{k}", {{ opacity: 1, duration: 0.25 }}, {tempos[k]:.2f});')
            else:
                js.append(f'tl.fromTo("#{pref}{k}", {{ opacity: 0, y: 14 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {tempos[k]:.2f});')
    return "&nbsp;".join(out)


def _etapas(e, eid, top, W, centro, fundo, ctexto, cdest):
    """linha do tempo vertical: cada etapa acende no tempo em que é dita (a jornada inteira aparece apagada antes)."""
    x, passo, n = e.get("x", 96), e.get("passo", 118), len(e["itens"])
    sec, dest, txt = SEC[fundo], COR[cdest], COR[ctexto]
    svg = [f'<svg style="position:absolute;left:0;top:0;width:{W}px;height:{n * passo}px" viewBox="0 0 {W} {n * passo}">']
    divs, js, sons = [], [], []
    for i, it in enumerate(e["itens"]):
        cy = i * passo + 34
        if i:
            svg.append(f'<line x1="{x + 26}" y1="{cy - passo + 26}" x2="{x + 26}" y2="{cy - 26}" stroke="{sec}" stroke-width="5"/>'
                       f'<line id="{eid}l{i}" x1="{x + 26}" y1="{cy - passo + 26}" x2="{x + 26}" y2="{cy - 26}" stroke="{dest}" stroke-width="5" '
                       f'stroke-dasharray="{passo - 52}" stroke-dashoffset="{passo - 52}"/>')
        svg.append(f'<circle cx="{x + 26}" cy="{cy}" r="26" fill="none" stroke="{sec}" stroke-width="4"/>'
                   f'<circle id="{eid}c{i}" cx="{x + 26}" cy="{cy}" r="0" fill="{dest}"/>')
        divs.append(f'<div id="{eid}t{i}" style="position:absolute;left:{x + 80}px;top:{cy - 38}px;width:{W - x - 170}px;'
                    f'font-size:{e.get("tam", 66)}px;font-weight:800;color:{txt};white-space:nowrap">'
                    + _pals(it["texto"], f"{eid}t{i}w", it.get("_tempos") or [it["t"]] * len(it["texto"].split()), js, "acende") + '</div>'
                    f'<div id="{eid}n{i}" style="position:absolute;left:{x}px;top:{cy - 22}px;width:52px;text-align:center;font-size:32px;'
                    f'font-weight:900;color:{sec}">{i + 1}</div>')
        t = it["t"]
        if i:
            js.append(f'tl.to("#{eid}l{i}", {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.inOut" }}, {t - 0.3:.2f});')
        js.append(f'tl.to("#{eid}c{i}", {{ attr: {{ r: 26 }}, duration: 0.35, ease: "back.out(2)" }}, {t:.2f});')
        js.append(f'tl.to("#{eid}n{i}", {{ color: "{COR[fundo]}", duration: 0.2 }}, {t + 0.05:.2f});')
        js.append(f'tl.fromTo("#{eid}t{i}", {{ x: 0 }}, {{ x: 8, duration: 0.35, ease: "power2.out" }}, {t:.2f});')
        sons.append(("tick", t, 0.25, 0.03))
    t_ini = e["itens"][0]["t"] - 0.35
    js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t_ini:.2f});')
    return (f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{n * passo}px">' + "".join(svg) + "</svg>"
            + "".join(divs) + "</div>"), js, sons


def _rota(e, eid, top, W, centro, fundo, ctexto, cdest):
    """dois pontos ligados por um caminho que se desenha, com um ponto viajando (ex.: BR -> EUA)."""
    sec, dest, txt = SEC[fundo], COR[cdest], COR[ctexto]
    t, d = e["t"], e.get("dur", 1.0)
    caminho = "M150 270 C 380 270, 560 70, 930 90"
    svg = (f'<svg style="position:absolute;left:0;top:0;width:{W}px;height:360px" viewBox="0 0 {W} 360">'
           f'<path d="{caminho}" fill="none" stroke="{sec}" stroke-width="5" stroke-dasharray="4 18" stroke-linecap="round"/>'
           f'<path id="{eid}p" class="rota" d="{caminho}" fill="none" stroke="{dest}" stroke-width="7" stroke-linecap="round"/>'
           f'<circle cx="150" cy="270" r="48" fill="{COR[fundo]}" stroke="{txt}" stroke-width="4"/>'
           f'<circle id="{eid}b" cx="930" cy="90" r="48" fill="{COR[fundo]}" stroke="{dest}" stroke-width="4"/>'
           f'<circle id="{eid}v" r="14" fill="{dest}" cx="150" cy="270"/>'
           f'<text x="150" y="282" text-anchor="middle" font-size="34" font-weight="900" fill="{txt}">{html.escape(e.get("de", "BR"))}</text>'
           f'<text id="{eid}bt" x="930" y="102" text-anchor="middle" font-size="34" font-weight="900" fill="{dest}">{html.escape(e.get("para", "EUA"))}</text>'
           '</svg>')
    extra = ""
    for k, (xx, yy) in (("rotulo_de", (150, 350)), ("rotulo_para", (930, 170))):
        if e.get(k):
            extra += (f'<div style="position:absolute;left:{xx - 200}px;top:{yy - 10}px;width:400px;text-align:center;font-size:36px;'
                      f'font-weight:700;color:{txt}">{html.escape(e[k])}</div>')
    js = [f'tl.fromTo("#{eid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.4, ease: "power3.out" }}, {t - 0.35:.2f});',
          f'(() => {{ const p = document.getElementById("{eid}p"), L = p.getTotalLength(), P = Array.from({{length: 41}}, (_, i) => p.getPointAtLength(L * i / 40)); '
          f'p.style.strokeDasharray = L; p.style.strokeDashoffset = L; '
          f'tl.fromTo(p, {{ strokeDashoffset: L }}, {{ strokeDashoffset: 0, duration: {d}, ease: "power2.inOut" }}, {t:.2f}); '
          f'const v = {{ k: 0 }}; tl.to(v, {{ k: 1, duration: {d}, ease: "power2.inOut", onUpdate: () => {{ const q = P[Math.round(v.k * 40)]; '
          f'document.getElementById("{eid}v").setAttribute("cx", q.x); document.getElementById("{eid}v").setAttribute("cy", q.y); }} }}, {t:.2f}); }})();',
          f'tl.to("#{eid}b", {{ fill: "{dest}", duration: 0.25 }}, {t + d:.2f});',
          f'tl.to("#{eid}bt", {{ fill: "{COR[fundo]}", duration: 0.25 }}, {t + d:.2f});']
    return (f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:360px">{svg}{extra}</div>', js,
            [("whoosh", t, 0.25, 0.5), ("tick", t + d, 0.3, 0.03)])


def _checklist(e, eid, top, W, centro, fundo, ctexto, cdest):
    """itens recebendo ✓ (ou ×) no tempo da fala."""
    x, passo = e.get("x", 96), e.get("passo", 104)
    sec, dest, txt = SEC[fundo], COR[cdest], COR[ctexto]
    h, js, sons = [], [], []
    for i, it in enumerate(e["itens"]):
        y, t = i * passo, it["t"]
        marca = "M14 32 L27 45 L48 18" if it.get("ok", True) else "M17 17 L45 45 M45 17 L17 45"
        h.append(f'<div id="{eid}r{i}" style="position:absolute;left:{x}px;top:{y}px;display:flex;align-items:center;gap:28px;opacity:0">'
                 f'<svg width="62" height="62" viewBox="0 0 62 62"><rect x="2" y="2" width="58" height="58" rx="14" fill="none" stroke="{sec}" stroke-width="4"/>'
                 f'<path id="{eid}m{i}" d="{marca}" fill="none" stroke="{dest}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" '
                 f'stroke-dasharray="60" stroke-dashoffset="60"/></svg>'
                 f'<span style="font-size:{e.get("tam", 66)}px;font-weight:800;color:{txt};white-space:nowrap">'
                 + _pals(it["texto"], f"{eid}r{i}w", it.get("_tempos") or [t] * len(it["texto"].split()), js) + '</span></div>')
        js.append(f'tl.fromTo("#{eid}r{i}", {{ opacity: 0, x: -30 }}, {{ opacity: 1, x: 0, duration: 0.35, ease: "power3.out" }}, {t - 0.2:.2f});')
        js.append(f'tl.to("#{eid}m{i}", {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.out" }}, {t + 0.1:.2f});')
        sons.append(("tick", t + 0.1, 0.25, 0.03))
    n = len(e["itens"])
    return f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{n * passo}px">' + "".join(h) + "</div>", js, sons


def _anel(e, eid, top, W, centro, fundo, ctexto, cdest):
    """anel de progresso enchendo, com o número contando (0 -> 100%)."""
    sec, dest, txt = SEC[fundo], COR[cdest], COR[ctexto]
    t, d, lado = e["t"], e.get("dur", 1.2), 300
    x = (W - lado) // 2 if centro or e.get("centro", True) else e.get("x", 96)
    circ = 2 * 3.14159 * 120
    leg = (f'<div style="position:absolute;left:0;top:{lado + 14}px;width:{W}px;text-align:center;font-size:44px;font-weight:700;color:{txt}">'
           f'{html.escape(e["legenda"])}</div>') if e.get("legenda") else ""
    h = (f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{lado + 70}px">'
         f'<svg style="position:absolute;left:{x}px;top:0" width="{lado}" height="{lado}" viewBox="0 0 300 300">'
         f'<circle cx="150" cy="150" r="120" fill="none" stroke="{sec}" stroke-width="22"/>'
         f'<circle id="{eid}a" cx="150" cy="150" r="120" fill="none" stroke="{dest}" stroke-width="22" stroke-linecap="round" '
         f'transform="rotate(-90 150 150)" stroke-dasharray="{circ:.1f}" stroke-dashoffset="{circ:.1f}"/></svg>'
         f'<div id="{eid}n" style="position:absolute;left:{x}px;top:0;width:{lado}px;height:{lado}px;display:grid;place-items:center;'
         f'font-size:84px;font-weight:900;color:{txt}">0%</div>{leg}</div>')
    js = [f'tl.fromTo("#{eid}", {{ opacity: 0, scale: 0.94 }}, {{ opacity: 1, scale: 1, duration: 0.4, ease: "power3.out" }}, {t - 0.35:.2f});',
          f'tl.to("#{eid}a", {{ strokeDashoffset: 0, duration: {d}, ease: "power2.inOut" }}, {t:.2f});',
          f'(() => {{ const v = {{ k: 0 }}; tl.to(v, {{ k: 100, duration: {d}, ease: "power2.inOut", onUpdate: () => '
          f'{{ document.getElementById("{eid}n").textContent = Math.round(v.k) + "%"; }} }}, {t:.2f}); }})();']
    return h, js, [("sino", t + d, 0.28, 1.2)] if e.get("sino", True) else []


def _contador(e, eid, top, W, centro, fundo, ctexto, cdest):
    """número subindo até o valor dito (formato brasileiro)."""
    t, d, tam = e["t"], e.get("dur", 0.9), e.get("tam", 150)
    cor = COR[cdest] if e.get("cor", "destaque") == "destaque" else COR[ctexto]
    alinha = "left:96px;width:888px;text-align:center" if centro else f"left:{e.get('x', 96)}px;width:{W - e.get('x', 96) - 90}px"
    fmt = f'"{e.get("prefixo", "")}" + Math.round(v.k).toLocaleString("pt-BR") + "{e.get("sufixo", "")}"'
    h = (f'<div id="{eid}" style="position:absolute;{alinha};top:{top}px;font-size:{tam}px;font-weight:900;color:{cor};'
         f'font-variant-numeric:tabular-nums;white-space:nowrap">{html.escape(e.get("prefixo", ""))}{e.get("de", 0)}{html.escape(e.get("sufixo", ""))}</div>')
    js = [f'tl.fromTo("#{eid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {t - 0.2:.2f});',
          f'(() => {{ const v = {{ k: {e.get("de", 0)} }}; tl.to(v, {{ k: {e["ate"]}, duration: {d}, ease: "power2.out", onUpdate: () => '
          f'{{ document.getElementById("{eid}").textContent = {fmt}; }} }}, {t:.2f}); }})();']
    return h, js, [("tick", t + i * d / 5, 0.2, 0.03) for i in range(5)]


def _cartoes(e, eid, top, W, centro, fundo, ctexto, cdest):
    """dois cards lado a lado pra comparar, chapados (sem sombra). risco_t: risca e apaga; destaque_t: vira laranja."""
    cf, ct = CARTAO[fundo]
    alt, gap = e.get("alt", 300), 30
    larg = (W - 192 - gap) // 2
    h, js, sons = [], [], []
    for i, it in enumerate(e["itens"][:2]):
        x = 96 + i * (larg + gap)
        h.append(f'<div id="{eid}k{i}" style="position:absolute;left:{x}px;top:0;width:{larg}px;height:{alt}px;border-radius:28px;'
                 f'background:{COR[cf]};padding:36px 34px;box-sizing:border-box;opacity:0">'
                 f'<div class="fit" data-max="{larg - 68}" data-grupo="{eid}" style="font-size:{it.get("tam", 68)}px;font-weight:900;line-height:1.0;color:{COR[ct]};white-space:nowrap;display:inline-block">{html.escape(it["titulo"])}</div>'
                 + (f'<div style="margin-top:20px;font-size:50px;font-weight:700;line-height:1.08;color:{COR[ct]}">'
                    + _pals(it["texto"], f"{eid}k{i}w", it.get("_tempos") or [it["t"] + 0.2] * len(it["texto"].split()), js) + '</div>' if it.get("texto") else "")
                 + f'<div id="{eid}x{i}" style="position:absolute;left:24px;right:24px;top:{alt // 2 - 5}px;height:10px;border-radius:5px;'
                 f'background:{COR[cdest]};transform:scaleX(0);transform-origin:left center"></div></div>')
        js.append(f'tl.fromTo("#{eid}k{i}", {{ opacity: 0, y: 40 }}, {{ opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }}, {it["t"] - 0.15:.2f});')
        sons.append(("tick", it["t"], 0.22, 0.03))
        if it.get("risco_t"):
            js.append(f'tl.to("#{eid}x{i}", {{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, {it["risco_t"]:.2f});')
            js.append(f'tl.to("#{eid}k{i}", {{ opacity: 0.45, duration: 0.3 }}, {it["risco_t"] + 0.15:.2f});')
            sons.append(("tick", it["risco_t"], 0.3, 0.03))
        if it.get("destaque_t"):                    # acende este e o outro volta ao normal: a comparação fica clara
            js.append(f'tl.to("#{eid}k{i}", {{ backgroundColor: "{COR["laranja"] if fundo != "laranja" else COR["azul"]}", duration: 0.3 }}, {it["destaque_t"]:.2f});')
            outro = 1 - i
            if len(e["itens"]) > 1 and e["itens"][outro].get("destaque_t", 1e9) < it["destaque_t"]:
                js.append(f'tl.to("#{eid}k{outro}", {{ backgroundColor: "{COR[cf]}", duration: 0.3 }}, {it["destaque_t"]:.2f});')
    return f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{alt}px">' + "".join(h) + "</div>", js, sons


COMPONENTES = {"etapas": _etapas, "rota": _rota, "checklist": _checklist, "anel": _anel, "contador": _contador, "cartoes": _cartoes}

def _degraus(e, eid, top, W, centro, fundo, ctexto, cdest):
    """a escada do manual como jornada: cada degrau sobe e acende no tempo da fala, com o nome em cima."""
    n = len(e["itens"]); gap = 18
    larg = (W - 192 - gap * (n - 1)) // n
    alt_max, sec, dest, txt = 300, SEC[fundo], COR[cdest], COR[ctexto]
    h, js, sons = [], [], []
    for i, it in enumerate(e["itens"]):
        x = 96 + i * (larg + gap)
        a = int(alt_max * (i + 1) / n)
        yb = 120 + alt_max - a
        h.append(f'<div style="position:absolute;left:{x}px;top:{yb}px;width:{larg}px;height:{a}px;background:{sec};border-radius:10px 10px 0 0"></div>'
                 f'<div id="{eid}d{i}" style="position:absolute;left:{x}px;top:{yb}px;width:{larg}px;height:{a}px;background:{dest};'
                 f'border-radius:10px 10px 0 0;transform:scaleY(0);transform-origin:bottom"></div>'
                 f'<div id="{eid}l{i}" style="position:absolute;left:{x - 20}px;bottom:{a + 14}px;width:{larg + 40}px;text-align:center;'
                 f'font-size:{e.get("tam", 44)}px;font-weight:800;line-height:1.0;color:{txt};opacity:0">'
                 + _pals(it["texto"], f"{eid}l{i}w", it.get("_tempos") or [it["t"] + 0.1] * len(it["texto"].split()), js) + '</div>')
        js.append(f'tl.to("#{eid}d{i}", {{ scaleY: 1, duration: 0.45, ease: "power3.out" }}, {it["t"]:.2f});')
        js.append(f'tl.fromTo("#{eid}l{i}", {{ opacity: 0, y: 16 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {it["t"] + 0.1:.2f});')
        sons.append(("tick", it["t"], 0.25, 0.03))
    js.append(f'tl.fromTo("#{eid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {e["itens"][0]["t"] - 0.3:.2f});')
    return f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{120 + alt_max}px">' + "".join(h) + "</div>", js, sons


def _barra(e, eid, top, W, centro, fundo, ctexto, cdest):
    """barra de progresso segmentada: cada trecho enche no tempo da fala, com o nome embaixo."""
    n = len(e["itens"]); gap = 10
    larg = (W - 192 - gap * (n - 1)) // n
    sec, dest, txt = SEC[fundo], COR[cdest], COR[ctexto]
    h, js, sons = [], [], []
    for i, it in enumerate(e["itens"]):
        x = 96 + i * (larg + gap)
        h.append(f'<div style="position:absolute;left:{x}px;top:0;width:{larg}px;height:28px;border-radius:14px;background:{sec}"></div>'
                 f'<div id="{eid}b{i}" style="position:absolute;left:{x}px;top:0;width:{larg}px;height:28px;border-radius:14px;background:{dest};'
                 f'transform:scaleX(0);transform-origin:left center"></div>'
                 f'<div id="{eid}l{i}" style="position:absolute;left:{x}px;top:52px;width:{larg}px;font-size:{e.get("tam", 42)}px;font-weight:800;'
                 f'line-height:1.05;color:{txt}">' + _pals(it["texto"], f"{eid}l{i}w", it.get("_tempos") or [it["t"]] * len(it["texto"].split()), js, "acende") + '</div>')
        js.append(f'tl.to("#{eid}b{i}", {{ scaleX: 1, duration: 0.5, ease: "power2.inOut" }}, {it["t"] - 0.2:.2f});')
        sons.append(("tick", it["t"], 0.25, 0.03))
    js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {e["itens"][0]["t"] - 0.45:.2f});')
    return f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:190px">' + "".join(h) + "</div>", js, sons


def _colunas(e, eid, top, W, centro, fundo, ctexto, cdest):
    """duas colunas separadas por um fio fino (comparação sem card). risco_t risca; destaque_t sublinha."""
    larg, alt = (W - 192 - 60) // 2, e.get("alt", 300)
    dest, txt = COR[cdest], COR[ctexto]
    h = [f'<div id="{eid}f" style="position:absolute;left:{W // 2 - 2}px;top:0;width:4px;height:{alt}px;background:{SEC[fundo]};'
         f'transform:scaleY(0);transform-origin:top"></div>']
    js = [f'tl.to("#{eid}f", {{ scaleY: 1, duration: 0.5, ease: "power2.out" }}, {e["itens"][0]["t"] - 0.3:.2f});']
    sons = []
    for i, it in enumerate(e["itens"][:2]):
        x = 96 if i == 0 else W // 2 + 30
        h.append(f'<div id="{eid}c{i}" style="position:absolute;left:{x}px;top:10px;width:{larg}px;opacity:0">'
                 f'<div class="fit" data-max="{larg}" data-grupo="{eid}" style="display:inline-block;white-space:nowrap;font-size:{it.get("tam", 70)}px;font-weight:900;'
                 f'line-height:1.0;color:{dest}">{html.escape(it["titulo"])}</div>'
                 + (f'<div style="margin-top:18px;font-size:48px;font-weight:700;line-height:1.1;color:{txt}">'
                    + _pals(it["texto"], f"{eid}c{i}w", it.get("_tempos") or [it["t"] + 0.2] * len(it["texto"].split()), js) + '</div>' if it.get("texto") else "")
                 + f'<div id="{eid}s{i}" style="margin-top:22px;width:180px;height:8px;border-radius:4px;background:{dest};transform:scaleX(0);transform-origin:left"></div>'
                 f'<div id="{eid}x{i}" style="position:absolute;left:-10px;top:30px;width:{larg}px;height:9px;border-radius:5px;background:{dest};'
                 f'transform:scaleX(0);transform-origin:left"></div></div>')
        js.append(f'tl.fromTo("#{eid}c{i}", {{ opacity: 0, x: {-30 if i == 0 else 30} }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {it["t"] - 0.1:.2f});')
        sons.append(("tick", it["t"], 0.22, 0.03))
        if it.get("destaque_t"):
            js.append(f'tl.to("#{eid}s{i}", {{ scaleX: 1, duration: 0.4, ease: "power2.out" }}, {it["destaque_t"]:.2f});')
        if it.get("risco_t"):
            js.append(f'tl.to("#{eid}x{i}", {{ scaleX: 1, duration: 0.3, ease: "power2.out" }}, {it["risco_t"]:.2f});')
            js.append(f'tl.to("#{eid}c{i}", {{ opacity: 0.45, duration: 0.3 }}, {it["risco_t"] + 0.15:.2f});')
            sons.append(("tick", it["risco_t"], 0.3, 0.03))
    return (f'<div id="{eid}" data-colunas="{eid}" data-x0="96" data-x1="{W - 96}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{alt}px">'
            + "".join(h) + "</div>", js, sons)


def _numero(e, eid, top, W, centro, fundo, ctexto, cdest):
    """numeral grande (ex.: 2) com o rótulo ao lado; entra com máscara e o rótulo em seguida."""
    tam = e.get("tam", 340)
    x = (W - tam) // 2 - 140 if centro else e.get("x", 96)
    h = (f'<div id="{eid}" style="position:absolute;left:0;top:{top}px;width:{W}px;height:{int(tam * 0.95)}px">'
         f'<div style="position:absolute;left:{x}px;top:0;overflow:hidden;height:{int(tam * 0.95)}px">'
         f'<div id="{eid}n" style="font-size:{tam}px;font-weight:900;line-height:0.95;color:{COR[cdest]}">{html.escape(str(e["numero"]))}</div></div>'
         f'<div id="{eid}r" style="position:absolute;left:{x + int(tam * 0.62 * len(str(e["numero"]))) + 30}px;top:{int(tam * 0.36)}px;'
         f'font-size:{e.get("tam_rotulo", 96)}px;font-weight:800;color:{COR[ctexto]};opacity:0;white-space:nowrap">{html.escape(e.get("rotulo", ""))}</div></div>')
    js = [f'tl.fromTo("#{eid}n", {{ yPercent: 100 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out" }}, {e["t"]:.2f});',
          f'tl.fromTo("#{eid}r", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {e.get("t_rotulo", e["t"] + 0.3):.2f});']
    return h, js, [("tick", e["t"], 0.3, 0.03)]


COMPONENTES.update({"degraus": _degraus, "barra": _barra, "colunas": _colunas, "numero": _numero})



def gerar(r):
    W, H, dur = r.get("largura", 1080), r.get("altura", 1920), r["duracao"]
    corpo, js, sons = [], [], []
    n = 0

    def som(arq, t, vol, d):
        nonlocal n
        n += 1
        sons.append(f'<audio id="s{n:02d}" src="sfx/{arq}.wav" data-start="{max(0, t):.2f}" data-duration="{d}" data-volume="{vol}"></audio>')

    cenas = r["cenas"]
    for ci, c in enumerate(cenas):
        modo = c.get("painel", "cheio")
        if c.get("tipo") == "cta":
            c = dict(c, cor=c.get("cor", "laranja"))
        fundo, ctexto, cdest, crot, cborda = FUNDOS[c.get("cor", "azul")]
        top, h, forma, borda, y_ini, y_fim = painel_geo(modo, H)
        pid = f"p{ci}"
        el = [f'<div class="painel" id="{pid}" style="top:{top}px;height:{h}px">',
              f'<svg class="forma" viewBox="0 0 {W} {h}" style="height:{h}px"><path d="{forma}" fill="{COR[fundo]}"/>'
              f'<path d="{borda}" stroke="{COR[cborda]}" stroke-width="16" fill="none"/></svg>',
              f'<div class="cont" id="{pid}m" style="position:absolute;left:0;top:0;width:{W}px;height:{h}px">']
        loc = lambda y: y - top                          # tela -> coordenada dentro do painel
        t0, t1 = c["t0"], c["t1"]
        entra, sai = max(0.0, t0 - 0.35), t1 - 0.1
        seguinte = cenas[ci + 1] if ci + 1 < len(cenas) else None
        coberto = (seguinte and seguinte.get("painel", "cheio") == modo and seguinte["t0"] - t1 < 0.25)
        js.append(f'tl.fromTo("#{pid}", {{ y: {y_ini} }}, {{ y: 0, duration: 0.55, ease: "power3.out" }}, {entra:.2f});')
        som("whoosh", entra, 0.35, 0.5)
        if t1 < dur - 0.05:
            if coberto:                                  # o próximo painel sobe por cima: este some depois
                js.append(f'tl.set("#{pid}", {{ y: {y_ini} }}, {seguinte["t0"] + 0.35:.2f});')
            else:
                js.append(f'tl.to("#{pid}", {{ y: {y_fim}, duration: 0.5, ease: "power3.in" }}, {sai:.2f});')
                som("whoosh", sai, 0.3, 0.5)
        if c.get("tipo") == "cta":
            base = 1130 if modo == "baixo" else (330 if modo == "cheio" else 250)
            if modo == "cheio" and r.get("tela_dividida"):
                base = 680                                   # sem legenda competindo: o CTA fica no meio da zona segura
            c["elementos"] = [
                {"tipo": "icone", "icone": "losangos", "x": 96, "y": base + 10, "tam": 60, "t": t0 + 0.15},
                {"tipo": "linha", "texto": c.get("acima", "Comente"), "y": base + 50, "t": t0 + 0.2, "cor": "texto", "tam": 84, "sync": False},
                {"tipo": "linha", "texto": c["palavra"], "y": base + 140, "t": t0 + 0.4, "cor": "destaque", "tam": 132, "sync": False},
                {"tipo": "linha", "texto": c["texto"], "y": base + 285, "t": t0 + 0.75, "cor": "texto", "tam": c.get("tam_texto", 52), "peso": 700, "sync": False},
                {"tipo": "sub", "y": base + 285 + int(c.get("tam_texto", 52) * 1.05) + 22, "largura": 300, "t": t0 + 1.0},
            ]
            som("sino", t0 + 0.4, 0.3, 1.2)
        centro = alinhamento(c, ci)
        if modo == "cheio" and c.get("tipo") != "cta":
            centralizar_vertical(c.get("elementos", []))
        for ei, e in enumerate(c.get("elementos", [])):
            eid = f"{pid}e{ei}"
            t = e.get("t", t0)
            x = e.get("x", 96)
            if e["tipo"] == "rotulo":
                lz = ICONES["losangos"][1].format(d=COR[cdest])
                estilo = f"left:0;width:{W}px;justify-content:center" if centro else f"left:{x}px"
                el.append(f'<div class="rotulo" id="{eid}" style="{estilo};top:{loc(e["y"])}px;color:{COR[crot]}">'
                          f'<svg viewBox="0 0 46 28">{lz}</svg><span>{html.escape(e["texto"])}</span></div>')
                js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {t:.2f});')
            elif e["tipo"] == "linha":
                cor = {"texto": ctexto, "destaque": cdest}.get(e.get("cor", "texto"), e.get("cor"))
                tam, peso = e.get("tam", 124), e.get("peso", 800)
                if centro:
                    caixa_l, larg_l = f"left:96px;width:{W - 192}px;text-align:center", W - 192
                else:
                    caixa_l, larg_l = f"left:{x}px;width:{W - x - 90}px", W - x - 90
                tempos = e.get("_tempos") or [t] * len(e["texto"].split())
                pals = "&nbsp;".join(f'<span class="pal" id="{eid}w{k}">{html.escape(w)}</span>' for k, w in enumerate(e["texto"].split()))
                el.append(f'<div class="linha" style="{caixa_l};top:{loc(e["y"])}px"><span id="{eid}" class="fit" data-max="{larg_l}" '
                          f'style="color:{COR[cor]};font-size:{tam}px;font-weight:{peso}">{pals}</span></div>')
                for k, tk in enumerate(tempos):          # a linha se monta junto com a fala
                    js.append(f'tl.fromTo("#{eid}w{k}", {{ yPercent: 115 }}, {{ yPercent: 0, duration: 0.5, ease: "expo.out" }}, {tk:.2f});')
                if e.get("som", True):
                    som("tick", tempos[0], 0.22, 0.03)
            elif e["tipo"] in ("sub", "risco"):
                alt = 7 if e["tipo"] == "sub" else 9
                cor = COR[cdest]
                bx = (W - e["largura"]) // 2 if centro else x
                alvo = f' data-alvo="{pid}e{e["apaga"]}"' if e["tipo"] == "risco" and e.get("apaga") is not None else ""
                el.append(f'<div class="barra" id="{eid}"{alvo} style="left:{bx}px;top:{loc(e["y"])}px;width:{e["largura"]}px;height:{alt}px;background:{cor}"></div>')
                js.append(f'tl.to("#{eid}", {{ scaleX: 1, duration: {0.5 if e["tipo"] == "sub" else 0.3}, ease: "power2.out" }}, {t:.2f});')
                if e["tipo"] == "risco":
                    som("tick", t, 0.3, 0.03)
                    if e.get("apaga") is not None:
                        js.append(f'tl.to("#{pid}e{e["apaga"]}", {{ opacity: 0.45, duration: 0.3 }}, {t + 0.15:.2f});')
            elif e["tipo"] == "icone":
                vb, svg = ICONES[e["icone"]]
                svg = svg.format(d=COR[cdest], t=COR[ctexto], f=COR[fundo], r=COR["marrom"] if fundo == "bege" else COR[ctexto])
                tam = e.get("tam", 160)
                larg = W if e["icone"] == "fio_arco" else tam
                alt = 200 if e["icone"] == "fio_arco" else int(tam * float(vb.split()[3]) / float(vb.split()[2]))
                xx = 0 if e["icone"] == "fio_arco" else ((W - larg) // 2 if centro else x)
                el.append(f'<svg class="icone" id="{eid}" viewBox="{vb}" style="left:{xx}px;top:{loc(e["y"])}px;width:{larg}px;height:{alt}px">{svg}</svg>')
                js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, {t:.2f});')
            elif e["tipo"] in COMPONENTES:
                h_, j_, s_ = COMPONENTES[e["tipo"]](e, eid, loc(e["y"]), W, centro, fundo, ctexto, cdest)
                el.append(h_); js.extend(j_)
                for a in s_:
                    som(*a)
        for bi, b in enumerate(c.get("_batidas", [])):
            if b["tipo"] == "foco":
                for ei in b["recuar"]:
                    js.append(f'tl.to("#{pid}e{ei}", {{ opacity: 0.4, duration: 0.45, ease: "power2.out" }}, {b["t"]:.2f});')
                js.append(f'tl.fromTo("#{pid}e{b["manter"]}", {{ x: 0 }}, {{ x: {0 if centro else 10}, duration: 0.45, ease: "power2.out" }}, {b["t"]:.2f});')
            elif b["tipo"] == "fio":
                el.append(f'<div class="barra" id="{pid}b{bi}" data-alvo="{pid}e{b["alvo"]}" data-sob="1" style="height:6px;background:{COR[cdest]}"></div>')
                js.append(f'tl.to("#{pid}b{bi}", {{ scaleX: 1, duration: 0.6, ease: "power2.out" }}, {b["t"]:.2f});')
            elif b["tipo"] == "item":                     # o item de que a fala está tratando acende na cor de destaque
                js.append(f'tl.to(\'[id^="{pid}e{b["el"]}{b["letra"]}{b["item"]}w"]\', {{ color: "{COR[cdest]}", duration: 0.3, yoyo: true, repeat: 1, repeatDelay: 0.9 }}, {b["t"]:.2f});')
            else:                                         # pulso: a cena inteira respira um pouco mais
                js.append(f'tl.to("#{pid}", {{ scale: 1.012, duration: 0.35, yoyo: true, repeat: 1, ease: "sine.inOut", transformOrigin: "50% 50%" }}, {b["t"]:.2f});')
            som("tick", b["t"], 0.12, 0.03)
        el.append("</div></div>")
        corpo.append("\n".join(el))
        # respiro de câmera bem sutil durante a cena (ambient, 1,5%): nada fica congelado esperando a próxima palavra
        js.append(f'tl.fromTo("#{pid}m", {{ y: 10, scale: 1 }}, {{ y: -10, scale: 1.015, duration: {max(0.5, t1 - t0 + 0.6):.2f}, '
                  f'ease: "sine.inOut", transformOrigin: "50% {960 - top}px" }}, {entra:.2f});')

    return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{html.escape(r["nome"])} (LIV clean, gerado por gerar_liv.py)</title>
    <script src="vendor/gsap.min.js"></script>
    <style>
      @font-face {{ font-family: "Darker Grotesque"; src: url("fontes/DarkerGrotesque[wght].ttf") format("truetype"); font-weight: 300 900; }}
      html, body {{ margin: 0; background: transparent; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: transparent; font-family: "Darker Grotesque", sans-serif; }}
      .painel {{ position: absolute; left: 0; width: {W}px; }}
      .painel > svg.forma {{ position: absolute; left: 0; top: 0; width: {W}px; }}
      .rotulo {{ position: absolute; display: flex; align-items: center; gap: 18px; font-size: 40px; font-weight: 700; }}
      .rotulo svg {{ width: 46px; height: 28px; }}
      .linha {{ position: absolute; overflow: hidden; padding-bottom: 10px; }}
      .linha > span {{ display: inline-block; line-height: 1.0; white-space: nowrap; letter-spacing: -0.01em; }}
      .linha .pal {{ display: inline-block; }}
      .barra {{ position: absolute; border-radius: 5px; transform-origin: left center; transform: scaleX(0); }}
      .icone {{ position: absolute; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-width="{W}" data-height="{H}" data-duration="{dur}">
      <div id="tudo" class="clip" style="position:absolute;inset:0" data-start="0" data-duration="{dur}">
{chr(10).join(corpo)}
      </div>
{chr(10).join("      " + s for s in sons)}
    </div>
    <script>
      document.fonts.ready.then(() => {{
        // texto ajustado à largura (nunca corta na lateral), medido uma vez
        document.querySelectorAll(".fit").forEach((el) => {{
          const max = Number(el.dataset.max); let tam = parseFloat(el.style.fontSize);
          while (el.scrollWidth > max && tam > 30) {{ tam -= 2; el.style.fontSize = tam + "px"; }}
        }});
        // títulos de uma mesma comparação (colunas, cartões) no mesmo tamanho: o menor que coube
        const grupos = {{}};
        document.querySelectorAll(".fit[data-grupo]").forEach((el) => {{ (grupos[el.dataset.grupo] = grupos[el.dataset.grupo] || []).push(el); }});
        Object.values(grupos).forEach((els) => {{
          const menor = Math.min(...els.map((el) => parseFloat(el.style.fontSize)));
          els.forEach((el) => {{ el.style.fontSize = menor + "px"; }});
        }});
        // colunas: o fio fica no meio do vão real entre as duas colunas (mesma margem dos dois lados),
        // medido pelo fim do conteúdo da esquerda, não pelo meio da tela
        document.querySelectorAll("[data-colunas]").forEach((box) => {{
          const id = box.dataset.colunas, x0 = Number(box.dataset.x0), x1 = Number(box.dataset.x1);
          const esq = document.getElementById(id + "c0"), dir = document.getElementById(id + "c1"), fio = document.getElementById(id + "f");
          if (!esq || !dir || !fio) return;
          const largura = (col) => {{
            let m = 0;
            col.querySelectorAll("div, span").forEach((n) => {{
              if (getComputedStyle(n).position === "absolute" || n.id.endsWith("s0") || n.id.endsWith("s1")) return;
              const r = n.getBoundingClientRect(), c = col.getBoundingClientRect();
              if (n.children.length === 0 || n.classList.contains("fit")) m = Math.max(m, r.right - c.left);
            }});
            return m;
          }};
          const we = largura(esq), wd = largura(dir);
          const vao = Math.min(64, Math.max(28, (x1 - x0 - we - wd - 4) / 2));
          const xf = x0 + we + vao;
          fio.style.left = xf + "px";
          dir.style.left = (xf + 4 + vao) + "px"; dir.style.width = (x1 - xf - 4 - vao) + "px";
          esq.style.width = we + "px";
        }});
        // risco do tamanho exato do texto que ele risca (funciona alinhado à esquerda ou centralizado)
        document.querySelectorAll(".barra[data-alvo]").forEach((b) => {{
          const alvo = document.getElementById(b.dataset.alvo); if (!alvo) return;
          const caixa = alvo.parentElement;
          if (b.dataset.sob) {{
            b.style.left = (caixa.offsetLeft + alvo.offsetLeft) + "px"; b.style.width = alvo.offsetWidth + "px";
            b.style.top = (caixa.offsetTop + alvo.offsetTop + alvo.offsetHeight + 2) + "px"; return;
          }}
          b.style.left = (caixa.offsetLeft + alvo.offsetLeft - 12) + "px"; b.style.width = (alvo.offsetWidth + 24) + "px";
        }});
        const tl = gsap.timeline({{ paused: true }});
{chr(10).join("        " + j for j in js)}
        window.__timelines["main"] = tl;
      }});
    </script>
  </body>
</html>
"""


def conferir_ritmo(r):
    """o motion acompanha a fala: nada de cena parada esperando a próxima palavra."""
    avisos = []
    for i, c in enumerate(r["cenas"]):
        if c.get("tipo") == "cta":
            continue
        ts = revelacoes(c)
        if not ts:
            continue
        nome = f"cena {i + 1} ({c['t0']:.1f}-{c['t1']:.1f}s)"
        if ts[0] - c["t0"] > 0.6:
            avisos.append(f"{nome}: {ts[0] - c['t0']:.1f}s até o 1º elemento (máx 0,6)")
        for a, b in zip(ts, ts[1:]):
            if b - a > 1.3:
                avisos.append(f"{nome}: {b - a:.1f}s parado entre {a:.2f} e {b:.2f} (máx 1,3)")
        if c["t1"] - ts[-1] > 1.2:
            avisos.append(f"{nome}: {c['t1'] - ts[-1]:.1f}s parado no fim (máx 1,2)")
        els = [dict(e) for e in c.get("elementos", [])]   # confere já centralizado, como vai sair
        if c.get("painel", "cheio") == "cheio":
            centralizar_vertical(els)
        for e in els:
            y0, y1 = extensao(e)
            if y0 < 160 or y1 > 1480:
                avisos.append(f"{nome}: '{e.get('texto', e['tipo'])}' sai da zona segura ({y0:.0f}-{y1:.0f}px)")
        if r.get("tela_dividida") and c.get("painel", "cheio") != "cheio":
            avisos.append(f"{nome}: tela dividida pede motion em tela cheia (painel 'cheio')")
    # variedade: o mesmo recurso não vira padrão do vídeo
    from collections import Counter
    uso = Counter(e["tipo"] for c in r["cenas"] for e in c.get("elementos", []) if e["tipo"] in COMPONENTES)
    for tipo, n in uso.items():
        if n > (1 if tipo == "rota" else 2):
            avisos.append(f"'{tipo}' usado {n}x no vídeo: varie a forma de mostrar (degraus, barra, colunas, número...)")
    for av in avisos:
        print("  aviso:", av)
    return avisos


def main():
    r = preparar(json.load(open(sys.argv[1])), os.path.dirname(os.path.abspath(sys.argv[1])))
    conferir_ritmo(r)
    saida = os.path.join(AQUI, "modelos", r["nome"] + ".html")
    open(saida, "w").write(gerar(r))
    print(saida)


if __name__ == "__main__":
    main()
