#!/usr/bin/env python3
"""LIVE 81 (LIV) — Perguntas e Respostas com advogada de imigração.

Cortes longos (YouTube, 16:9, vinheta da LIV) e 6 shorts (tela dividida, Dra. Lívia em cima):
  A = enxuta: gancho + legenda + CTA animado depois da fala final (cauda de 3,8s)
  B = com motion em tela cheia no ritmo da fala + o mesmo CTA no fim

    py -3.12 -X utf8 projetos/live81/lote_live81.py longos
    py -3.12 -X utf8 projetos/live81/lote_live81.py A [S1 S2 ...]
    py -3.12 -X utf8 projetos/live81/lote_live81.py B [S1 S2 ...]
    py -3.12 -X utf8 projetos/live81/lote_live81.py cortes [S1 ...]   (só confere o plano e o olhar)
    py -3.12 -X utf8 projetos/live81/lote_live81.py previa [S1 ...]   (folha do enquadramento, 1 quadro por corte, sem renderizar)
    py -3.12 -X utf8 projetos/live81/lote_live81.py final [S1 ...]    (B se tem motion, senão A, + trilha Skylines)

Os shorts usam a live inteira com trechos em segundos do bruto (transcrição em editor/transcricoes).
"""
import os, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "editor"))
import plataforma as PLAT

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
MOTION = os.path.join(AQUI, "..", "..", "motion", "renders")
LIVE = os.path.expanduser(os.environ.get("LIVE81_VIDEO", "~/Downloads/LIVE 81 _ Perguntas e Respostas com advogada de imigração.mp4"))
SAIDA = PLAT.pasta_renders("LIVE_81")

LONGOS = [
    ("L1_fim_da_pausa_entrevistas", "795.2-1227.0,1978.5-2025.8,2559.0-2575.4,3168.5-3315.4"),  # 13:15-20:27, 32:58-33:46, 42:39-42:55, 52:48-55:15
    ("L2_negativas_revertidas", "114.8-639.2"),                                                  # 1:55-10:39
]

# id, nome, trechos do bruto, gancho, cor da caixa
SHORTS = [
    ("S1", "ingles_entrevista", "3182.7-3229.6",
     "Precisa falar inglês na entrevista do consulado?", "azul"),
    ("S2", "documentos_nova_entrevista", "1078.9-1133.2",
     "O que o consulado está pedindo na nova entrevista?", "laranja"),
    ("S3", "dois_pedidos", "2103.0-2111.9?,2112.4-2116.2,2119.3-2149.1",
     "Vale protocolar dois pedidos ao mesmo tempo?", "bege"),
    ("S4", "ia_no_processo", "3487.0-3525.0",
     "Usar IA no seu processo pode dar negativa?", "marrom"),
    ("S5", "area_eb2_niw", "3870.1-3885.5,360.1-395.0",
     "Sua área é importante o suficiente para o EB-2 NIW?", "azul"),
    ("S6", "estudante_green_card", "2253.56-2273.1,2290.5-2308.0,2311.2-2316.35",
     "Dá pra entrar como estudante e pedir o green card depois?", "laranja"),
]
TIRAR = {"S5": ["3885.38-3885.75"]}     # "como" solto no fim do 1º trecho
CTA = "Veja a live completa no canal"   # YouTube Shorts; texto do motion/…_cta
CAUDA = 3.8
COM_MOTION = {"S2", "S3", "S5"}         # versão B (motion de cena); os outros vão na versão A
TRILHAS = os.path.join(AQUI, "..", "..", "editor", "trilhas.py")
TRILHA = os.path.join(AQUI, "..", "..", "assets", "trilhas", "corporativo__skylines-anno-domini-beats__99bpm__A-maior.mp3")
TRILHA_SS = 4.0                         # os 4s iniciais da Skylines são quase silêncio (auditor-de-trilha)

TROCAS = ["USIS=USCIS", "ISIS=USCIS", "iOSAS=USCIS", "USAS=USCIS", "EB2NW=EB-2 NIW", "EB2MW=EB-2 NIW", "B2NW=EB-2 NIW",
          "B2MW=EB-2 NIW", "NW=NIW", "brincar=green card", "Livia=Lívia", "Livy=Lívia", "Live=LIV", "consolar=consular",
          "operatório=obrigatório", "2 e 140 GC=dois I-140", "para o autoavolado=autopeticionado", "Refië=RFE", "refier=RFE",
          "Final Medics=final merits", "Final Match=final merits", "public child=public charge", "prum=rumo"]


def rodar(cmd):
    print(" ".join(cmd[:4]), "...", flush=True)
    subprocess.run(cmd, check=True)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "A"
    filtro = sys.argv[2:]
    if modo == "longos":
        for nome, trechos in LONGOS:
            if filtro and nome[:2] not in filtro:
                continue
            rodar([sys.executable, EDITOR, LIVE, "--layout", "youtube", "--marca", "liv", "--manter-perguntas",
                   "--trechos", trechos, "--nome", nome, "--saida", os.path.join(SAIDA, "corte_longo")])
        return
    if modo == "final":                          # versão B (motion) quando existe, senão A; + trilha
        for sid, nome, *_ in SHORTS:
            if filtro and sid not in filtro:
                continue
            b = os.path.join(SAIDA, "shorts_B", f"{sid}B_{nome}.mp4")
            base = b if sid in COM_MOTION else os.path.join(SAIDA, "shorts_A", f"{sid}A_{nome}.mp4")
            os.makedirs(os.path.join(SAIDA, "shorts_final"), exist_ok=True)
            rodar([sys.executable, TRILHAS, "mixar", base, TRILHA, "--ss", str(TRILHA_SS),
                   "-o", os.path.join(SAIDA, "shorts_final", f"{sid}_{nome}.mp4")])
        return
    for sid, nome, trechos, gancho, cor in SHORTS:
        if filtro and sid not in filtro:
            continue
        cmd = [sys.executable, EDITOR, LIVE, "--layout", "dividido", "--cima", "esquerda",
               "--marca", "liv", "--manter-perguntas", "--trechos", trechos, "--gancho", gancho, "--cor-caixa", cor,
               "--tirar-hesitacoes", "--respiro", "0.18",      # shorts: sem "éé"/"então, assim" e com pausas curtas
               "--sem-sobreposicao"]                           # a LIVE 81 não tem chat/banner na tela (conferido no mosaico)
        if modo == "previa":                                   # folha de enquadramento pra validar ANTES do render
            os.makedirs(os.path.join(SAIDA, "previas"), exist_ok=True)
            for t in TIRAR.get(sid, []):
                cmd += ["--tirar", t]
            rodar(cmd + ["--previa-enquadramento", os.path.join(SAIDA, "previas", f"{sid}_enquadramento.jpg")])
            continue
        if modo in ("A", "B"):
            cmd += ["--exigir-enquadramento"]                  # guardrail: não renderiza com cabeça cortada / teto demais
        for t in TROCAS:
            cmd += ["--trocar", t]
        for t in TIRAR.get(sid, []):
            cmd += ["--tirar", t]
        if modo == "cortes":
            rodar(cmd + ["--so-cortes", "--checar-olhar"])
            continue
        if modo == "palavras":
            rodar(cmd + ["--json-palavras", os.path.join(AQUI, "motion", "palavras", f"{sid}.json")])
            continue
        cmd += ["--cauda", str(CAUDA)]
        if modo == "A":
            cmd += ["--broll", os.path.join(MOTION, f"live81_{sid}_cta.mov") + "@0",
                    "--nome", f"{sid}A_{nome}", "--saida", os.path.join(SAIDA, "shorts_A")]
        else:
            cmd += ["--broll", os.path.join(MOTION, f"live81_{sid}.mov") + "@0",
                    "--nome", f"{sid}B_{nome}", "--saida", os.path.join(SAIDA, "shorts_B")]
        rodar(cmd)


if __name__ == "__main__":
    main()
