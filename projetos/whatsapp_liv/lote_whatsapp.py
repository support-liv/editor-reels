#!/usr/bin/env python3
"""Vídeos de boas-vindas da LIV para WhatsApp (quem agendou reunião).
Quadrado 1080x1080, enquadramento fixo, legenda na cor da LIV, sem gancho nem CTA.
Rodar: python3 lote_whatsapp.py [--so-cortes] [W01 W02]
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
PASTA = os.path.expanduser(os.environ.get("WHATS_PASTA", "~/Downloads"))
SAIDA = os.path.expanduser(os.environ.get("WHATS_SAIDA", "~/Desktop/WHATSAPP_LIV"))
TROCAS = ["da Livre=da LIV", "na Livre=na LIV", "na Alive=na LIV", "no Alive=na LIV", "na Alivia=na LIV",
          "com case=com o case", "com o queijo=com o case", "fervo=perfil", "já andou=agendou",
          "Marina Damás=Marinna Damásio", "Mariana Damase=Marinna Damásio"]

VIDEOS = [
    # id, nome, arquivo, trechos (take bom de cada frase), girar (graus), respiro (s; None = padrão 0.25), dinâmico (zoom a cada ~2,5s), extras
    ("W01", "thiago_boas_vindas", "C1251-001.MP4",
     "58.2-60.6,60.8-66.0,66.6-72.7,77.1-87.7,95.0-110.9,118.8-135.5", 5.0, 0.35, True,
     ["--endireitar",                      # mede as verticais e escolhe o ângulo (só gira: nunca distorcer)
      "--tirar", "96.52-97.07",            # "muito de... de como": fica um "de" só
      "--tirar", "128.12-128.36"]),        # travada entre "reunião" e "porque"   # Thiago fala mais pausado: corte seco ficava robótico
    ("W02", "marinna_boas_vindas", "C1253-002.MP4",
     "34.0-41.9,235.1-242.2,246.5-259.1,261.9-270.0,273.6-284.3,286.2-294.0,300.7-304.4,304.8-309.2", 0.0, None, False, []),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(SAIDA, exist_ok=True)
    for vid, nome, arq, trechos, girar, respiro, dinamico, extras in VIDEOS:
        if filtro and vid not in filtro:
            continue
        print(f"\n######## {vid} {nome}", flush=True)
        cmd = [sys.executable, EDITOR, os.path.join(PASTA, arq), "--layout", "quadrado", "--marca", "liv",
               "--girar", str(girar), "--trechos", trechos, "--nome", f"{vid}_{nome}", "--saida", SAIDA]
        cmd += extras
        if dinamico:
            cmd.append("--dinamico")
        if respiro:
            cmd += ["--respiro", str(respiro)]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd.append("--so-cortes")
        subprocess.run(cmd)
