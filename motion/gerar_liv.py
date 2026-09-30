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
Tudo em coordenadas da tela (px). Cores e fonte só as do manual. Cada elemento já leva o som discreto dele.
Zona segura: x 60-1020, y 153-1510, sem o canto dos botões (x > 835, y > 1205). Na tela dividida a legenda fica
na divisa (860-1060): nada ali. Painel "baixo" começa em 1020; "cima" termina em 900.
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


def painel_geo(modo, H):
    """(top, altura, path da forma, path da borda, y inicial, y final) do painel."""
    if modo == "cheio":
        h = H + 600
        return (-300, h, f"M0 300 C 300 300, 760 210, 1080 0 L1080 {h - 300} C 760 {h - 90}, 300 {h}, 0 {h} Z",
                "M0 300 C 300 300, 760 210, 1080 0", h, -h)
    if modo == "baixo":
        top = 1020; h = H - top + 40
        return (top, h, f"M0 120 C 300 120, 760 60, 1080 0 L1080 {h} L0 {h} Z", "M0 120 C 300 120, 760 60, 1080 0", h, h)
    h = 900
    return (0, h, f"M0 0 H1080 V{h - 120} C 760 {h - 60}, 300 {h}, 0 {h} Z", f"M1080 {h - 120} C 760 {h - 60}, 300 {h}, 0 {h}", -h, -h)


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
            c["elementos"] = [
                {"tipo": "icone", "icone": "losangos", "x": 96, "y": base + 10, "tam": 60, "t": t0 + 0.15},
                {"tipo": "linha", "texto": "Comente", "y": base + 50, "t": t0 + 0.2, "cor": "texto", "tam": 84},
                {"tipo": "linha", "texto": c["palavra"], "y": base + 140, "t": t0 + 0.4, "cor": "destaque", "tam": 132},
                {"tipo": "linha", "texto": c["texto"], "y": base + 285, "t": t0 + 0.75, "cor": "texto", "tam": 52, "peso": 700},
                {"tipo": "sub", "y": base + 360, "largura": 300, "t": t0 + 1.0},
            ]
            som("sino", t0 + 0.4, 0.3, 1.2)
        for ei, e in enumerate(c.get("elementos", [])):
            eid = f"{pid}e{ei}"
            t = e.get("t", t0)
            x = e.get("x", 96)
            if e["tipo"] == "rotulo":
                lz = ICONES["losangos"][1].format(d=COR[cdest])
                el.append(f'<div class="rotulo" id="{eid}" style="left:{x}px;top:{loc(e["y"])}px;color:{COR[crot]}">'
                          f'<svg viewBox="0 0 46 28">{lz}</svg><span>{html.escape(e["texto"])}</span></div>')
                js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, x: -20 }}, {{ opacity: 1, x: 0, duration: 0.4, ease: "power3.out" }}, {t:.2f});')
            elif e["tipo"] == "linha":
                cor = {"texto": ctexto, "destaque": cdest}.get(e.get("cor", "texto"), e.get("cor"))
                tam, peso = e.get("tam", 124), e.get("peso", 800)
                el.append(f'<div class="linha" style="left:{x}px;top:{loc(e["y"])}px"><span id="{eid}" class="fit" data-max="{W - x - 90}" '
                          f'style="color:{COR[cor]};font-size:{tam}px;font-weight:{peso}">{html.escape(e["texto"])}</span></div>')
                js.append(f'tl.fromTo("#{eid}", {{ yPercent: 110 }}, {{ yPercent: 0, duration: 0.6, ease: "expo.out" }}, {t:.2f});')
                if e.get("som", True):
                    som("tick", t, 0.22, 0.03)
            elif e["tipo"] in ("sub", "risco"):
                alt = 7 if e["tipo"] == "sub" else 9
                cor = COR[cdest]
                el.append(f'<div class="barra" id="{eid}" style="left:{x}px;top:{loc(e["y"])}px;width:{e["largura"]}px;height:{alt}px;background:{cor}"></div>')
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
                xx = 0 if e["icone"] == "fio_arco" else x
                el.append(f'<svg class="icone" id="{eid}" viewBox="{vb}" style="left:{xx}px;top:{loc(e["y"])}px;width:{larg}px;height:{alt}px">{svg}</svg>')
                js.append(f'tl.fromTo("#{eid}", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.6, ease: "power3.out" }}, {t:.2f});')
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
      .linha span {{ display: block; line-height: 1.0; white-space: nowrap; letter-spacing: -0.01em; }}
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
        const tl = gsap.timeline({{ paused: true }});
{chr(10).join("        " + j for j in js)}
        window.__timelines["main"] = tl;
      }});
    </script>
  </body>
</html>
"""


def main():
    r = json.load(open(sys.argv[1]))
    saida = os.path.join(AQUI, "modelos", r["nome"] + ".html")
    open(saida, "w").write(gerar(r))
    print(saida)


if __name__ == "__main__":
    main()
