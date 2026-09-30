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
                    f'font-size:{e.get("tam", 66)}px;font-weight:800;color:{txt};opacity:0.35;white-space:nowrap">{html.escape(it["texto"])}</div>'
                    f'<div id="{eid}n{i}" style="position:absolute;left:{x}px;top:{cy - 22}px;width:52px;text-align:center;font-size:32px;'
                    f'font-weight:900;color:{sec}">{i + 1}</div>')
        t = it["t"]
        if i:
            js.append(f'tl.to("#{eid}l{i}", {{ strokeDashoffset: 0, duration: 0.3, ease: "power2.inOut" }}, {t - 0.3:.2f});')
        js.append(f'tl.to("#{eid}c{i}", {{ attr: {{ r: 26 }}, duration: 0.35, ease: "back.out(2)" }}, {t:.2f});')
        js.append(f'tl.to("#{eid}n{i}", {{ color: "{COR[fundo]}", duration: 0.2 }}, {t + 0.05:.2f});')
        js.append(f'tl.fromTo("#{eid}t{i}", {{ opacity: 0.35, x: 0 }}, {{ opacity: 1, x: 8, duration: 0.35, ease: "power2.out" }}, {t:.2f});')
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
                 f'<span style="font-size:{e.get("tam", 66)}px;font-weight:800;color:{txt};white-space:nowrap">{html.escape(it["texto"])}</span></div>')
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
                 f'<div class="fit" data-max="{larg - 68}" style="font-size:{it.get("tam", 68)}px;font-weight:900;line-height:1.0;color:{COR[ct]};white-space:nowrap;display:inline-block">{html.escape(it["titulo"])}</div>'
                 + (f'<div style="margin-top:20px;font-size:50px;font-weight:700;line-height:1.08;color:{COR[ct]}">{html.escape(it["texto"])}</div>' if it.get("texto") else "")
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
              f'<path d="{borda}" stroke="{COR[cborda]}" stroke-width="16" fill="none"/></svg>']
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
                base = 560                                   # sem legenda competindo: o CTA desce pro meio da tela
            c["elementos"] = [
                {"tipo": "icone", "icone": "losangos", "x": 96, "y": base + 10, "tam": 60, "t": t0 + 0.15},
                {"tipo": "linha", "texto": "Comente", "y": base + 50, "t": t0 + 0.2, "cor": "texto", "tam": 84},
                {"tipo": "linha", "texto": c["palavra"], "y": base + 140, "t": t0 + 0.4, "cor": "destaque", "tam": 132},
                {"tipo": "linha", "texto": c["texto"], "y": base + 285, "t": t0 + 0.75, "cor": "texto", "tam": 52, "peso": 700},
                {"tipo": "sub", "y": base + 360, "largura": 300, "t": t0 + 1.0},
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
                el.append(f'<div class="linha" style="{caixa_l};top:{loc(e["y"])}px"><span id="{eid}" class="fit" data-max="{larg_l}" '
                          f'style="color:{COR[cor]};font-size:{tam}px;font-weight:{peso}">{html.escape(e["texto"])}</span></div>')
                js.append(f'tl.fromTo("#{eid}", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out" }}, {t:.2f});')
                if e.get("som", True):
                    som("tick", t, 0.22, 0.03)
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
        el.append("</div>")
        corpo.append("\n".join(el))

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
      .linha span {{ display: inline-block; line-height: 1.0; white-space: nowrap; letter-spacing: -0.01em; }}
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
        // risco do tamanho exato do texto que ele risca (funciona alinhado à esquerda ou centralizado)
        document.querySelectorAll(".barra[data-alvo]").forEach((b) => {{
          const alvo = document.getElementById(b.dataset.alvo); if (!alvo) return;
          const caixa = alvo.parentElement;
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
        ts = sorted([e.get("t", c["t0"]) for e in c.get("elementos", []) if "itens" not in e] +
                    [it[k] for e in c.get("elementos", []) for it in e.get("itens", []) for k in ("t", "risco_t", "destaque_t") if k in it] +
                    [e["t"] + e.get("dur", 0) for e in c.get("elementos", []) if e["tipo"] in ("rota", "anel", "contador")])
        if not ts:
            continue
        nome = f"cena {i + 1} ({c['t0']:.1f}-{c['t1']:.1f}s)"
        if ts[0] - c["t0"] > 0.8:
            avisos.append(f"{nome}: {ts[0] - c['t0']:.1f}s até o 1º elemento (máx 0,8)")
        for a, b in zip(ts, ts[1:]):
            if b - a > 2.0:
                avisos.append(f"{nome}: {b - a:.1f}s parado entre {a:.2f} e {b:.2f} (máx 2,0)")
        if c["t1"] - ts[-1] > 1.6:
            avisos.append(f"{nome}: {c['t1'] - ts[-1]:.1f}s parado no fim (máx 1,6)")
        els = [dict(e) for e in c.get("elementos", [])]   # confere já centralizado, como vai sair
        if c.get("painel", "cheio") == "cheio":
            centralizar_vertical(els)
        for e in els:
            y0, y1 = extensao(e)
            if y0 < 160 or y1 > 1480:
                avisos.append(f"{nome}: '{e.get('texto', e['tipo'])}' sai da zona segura ({y0:.0f}-{y1:.0f}px)")
        if r.get("tela_dividida") and c.get("painel", "cheio") != "cheio":
            avisos.append(f"{nome}: tela dividida pede motion em tela cheia (painel 'cheio')")
    for av in avisos:
        print("  aviso:", av)
    return avisos


def main():
    r = json.load(open(sys.argv[1]))
    conferir_ritmo(r)
    saida = os.path.join(AQUI, "modelos", r["nome"] + ".html")
    open(saida, "w").write(gerar(r))
    print(saida)


if __name__ == "__main__":
    main()
