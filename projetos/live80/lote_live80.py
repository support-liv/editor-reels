#!/usr/bin/env python3
"""LIVE 80 (LIV) — Perguntas e Respostas com advogada de imigração.

Cortes longos (YouTube, 16:9, vinheta da LIV) e 6 shorts em duas versões:
  A = enxuta: gancho + legenda + CTA animado depois da fala final (cauda de 3,8s)
  B = com motion em tela cheia no ritmo da fala + o mesmo CTA no fim

    python3 projetos/live80/lote_live80.py longos
    python3 projetos/live80/lote_live80.py A [S1 S2 ...]
    python3 projetos/live80/lote_live80.py B [S1 S2 ...]

Os shorts usam os trechos recortados da live (LIVE80_TRECHOS), cada um transcrito pelo Whisper
(tempo por palavra exato). A live inteira usa a transcrição do .vtt do YouTube (só nos cortes longos).
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
MOTION = os.path.join(AQUI, "..", "..", "motion", "renders")
LIVE = os.path.expanduser(os.environ.get("LIVE80_VIDEO", "~/Downloads/LIVE 80 _ Perguntas e Respostas com advogada de imigração.mp4"))
TRECHOS = os.path.expanduser(os.environ.get("LIVE80_TRECHOS", "~/Desktop/LIVE_80/trechos"))
SAIDA = os.path.expanduser(os.environ.get("LIVE80_SAIDA", "~/Desktop/LIVE_80"))

LONGOS = [
    ("L1_visa_bulletin_outubro", "270.6-868.1"),                                   # 4:30 - 14:28
    ("L2_ajuste_de_status", "1239.6-1609.1,1784.6-1794.8,1801.7-1919.4,1990.8-2016.4"),  # 20:39-26:49, 29:44-31:59, 33:10-33:36
]

# id, arquivo do trecho (recortado da live em "inicio"), trechos relativos ao arquivo, gancho, cor da caixa
SHORTS = [
    ("S1", "S1_visa_bulletin_brasil", "3.39-39.3,90.28-97.1",
     "O Visa Bulletin retrocedeu. Muda algo pra quem está no Brasil 🇧🇷?", "azul"),
    ("S2", "S2_ajuste_plano_a", "3.53-36.05,62.88-71.9,89.85-96.4",
     "Correr pro ajuste de status pode atrapalhar o seu plano?", "laranja"),
    ("S3", "S3_momento_certo", "3.37-46.5",
     "Existe um momento certo pra entrar com o seu processo?", "bege"),
    ("S4", "S4_brasil_eua", "3.65-13.8,21.32-24.1,34.64-78.1",
     "Começou pelo Brasil 🇧🇷. Dá pra terminar o processo nos EUA 🇺🇸?", "marrom"),
    ("S5", "S5_business_plan", "2.79-12.0,25.96-56.0,63.11-81.2",
     "Business plan ou professional plan: qual a imigração prefere?", "azul"),
    ("S6", "S6_filho_18", "3.32-50.3",
     "Seu filho já tem 18 anos? Isso pode mudar o seu plano", "laranja"),
]
CTA = "Comente PERFIL27 para uma análise de perfil gratuita"   # texto do CTA animado (motion/…_cta)
CAUDA = 3.8

TROCAS = ["USIS é a prova=USCIS aprova", "outra pessoa=autorização", "EB2 em Davos=EB-2 NIW",
          "Web2NW=EB-2 NIW", "B2NW=EB-2 NIW", "para estar serviços=é prestar serviços", "chega e mostrar=chegue a mostrar",
          "ter protocolo com caso=protocolar um caso", "FIUM=F-1", "dole=DOL", "USIS=USCIS", "ISIS=USCIS", "brincar=green card", "1 e 2=um E-2",
          "formantes indiscriminadas=forma indiscriminada", "erronea=errônea",
          "está que nos traços=está aqui nos Estados Unidos", "ajustos=ajuste", "consolar=consular",
          "EB2NW=EB-2 NIW", "EB2 em Dav=EB-2 NIW", "EB2 em W=EB-2 NIW", "lidar=lhe dar", "Livia=Lívia",
          "Daniel Abreu=Daniela Abreu", "Live=LIV"]


def rodar(cmd):
    print(" ".join(cmd[:4]), "...", flush=True)
    subprocess.run(cmd, check=True)


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "A"
    filtro = sys.argv[2:]
    if modo == "longos":
        for nome, trechos in LONGOS:
            rodar(["python3", EDITOR, LIVE, "--layout", "youtube", "--marca", "liv", "--trechos", trechos,
                   "--nome", nome, "--saida", os.path.join(SAIDA, "corte_longo")])
        return
    for sid, arq, trechos, gancho, cor in SHORTS:
        if filtro and sid not in filtro:
            continue
        cmd = ["python3", EDITOR, os.path.join(TRECHOS, arq + ".mp4"), "--layout", "dividido", "--cima", "esquerda",
               "--marca", "liv", "--manter-perguntas", "--trechos", trechos, "--gancho", gancho, "--cor-caixa", cor,
               "--tirar-hesitacoes", "--respiro", "0.18"]      # shorts: sem "éé"/"então, assim" e com pausas curtas
        for t in TROCAS:
            cmd += ["--trocar", t]
        # CTA animado depois da fala final, numa cauda de 3,8s (A: só o CTA; B: motion completo + CTA)
        cmd += ["--cauda", str(CAUDA)]
        if modo == "A":
            cmd += ["--broll", os.path.join(MOTION, f"live80_{sid}_cta.mov") + "@0",
                    "--nome", f"{sid}A_{arq[3:]}", "--saida", os.path.join(SAIDA, "shorts_A")]
        else:
            cmd += ["--broll", os.path.join(MOTION, f"live80_{sid}.mov") + "@0",
                    "--nome", f"{sid}B_{arq[3:]}", "--saida", os.path.join(SAIDA, "shorts_B")]
        rodar(cmd)


if __name__ == "__main__":
    main()
