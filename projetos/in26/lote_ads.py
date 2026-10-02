#!/usr/bin/env python3
"""Anúncios da Julia (pasta ADS) - Teste A: mesmo padrão dos Reels, identidade Imigrar.
Rodar tudo:            python3 lote_ads.py
Só conferir os cortes: python3 lote_ads.py --so-cortes
Só alguns:             python3 lote_ads.py AD1a AD4

Diferenças pro Reels orgânico: sem caixa de CTA (a Julia fala o CTA e o Meta põe o botão)
e legenda um pouco mais alta (0.55), longe do botão e do texto do anúncio. Nas selfies, 0.64 (abaixo do queixo).
Takes escolhidos com a auditoria (auditar.py): só trechos falados olhando pra câmera, nunca lendo o celular.
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
# pasta com os vídeos brutos e onde saem os prontos (mude com: export IN26_DIR=/caminho/da/pasta)
IN26 = os.path.expanduser(os.environ.get("IN26_DIR", "~/Desktop/IN26"))
D = os.path.join(IN26, "ADS") + "/"
PASTA = os.path.join(IN26, "ADS", "prontos", "teste_A")
TROCAS = ["InVin 6=IN26", "pomegamento=planejamento", "Se a dentista=Se você, dentista,",
          "organizando suas redes=organizando suas dúvidas", "Clica em=Clique em", "Deu o primeiro=Dê o primeiro"]

ADS = [
    # id, nome, vídeo, trechos, gancho, aperto (None = padrão)
    # Roteiro 1: sonho adiado
    ("AD1a", "sonho_adiado_selfie", D + "Edits_Ads1_20260925_135010.MP4", "0.0-31.8",
     "Dentista, já pensou em morar nos EUA 🇺🇸?", None),
    ("AD1b", "sonho_adiado_andando", D + "IMG_3442.MOV", "1.2-9.9,22.9-26.8,50.9-60.2,70.0-75.2",
     "Dentista, já pensou em morar nos EUA 🇺🇸?", 0.6),
    # Roteiro 2: primeira pergunta
    ("AD2a", "primeira_pergunta_selfie", D + "Edits_Ads2_20260925_133516.MP4", "0.0-34.6",
     "Se você fosse morar nos EUA 🇺🇸, qual seria sua primeira pergunta?", None),
    ("AD2b", "primeira_pergunta_andando", D + "IMG_3443.MOV", "6.4-13.2,15.4-18.3,52.5-56.8,63.2-70.4,81.2-87.7",
     "Se você fosse morar nos EUA 🇺🇸, qual seria sua primeira pergunta?", 0.6),
    # Roteiro 3: estamos no IN26
    ("AD3a", "in26_selfie", D + "Edits_Ads3_20260925_133817.MP4", "16.85-37.7",
     "Dentista que pensa em viver nos EUA 🇺🇸, esse recado é pra você", None),
    ("AD3b", "in26_andando", D + "IMG_3444.MOV", "11.3-14.9,26.6-29.7,45.2-51.9,72.3-74.9",
     "Dentista que pensa em viver nos EUA 🇺🇸, esse recado é pra você", 0.6),
    # Chamadas do evento online
    ("AD4", "e_hoje", D + "IMG_3447.MOV", "37.2-46.3,69.6-72.3",
     "Dentista, é hoje! Evento online e gratuito", 0.6),
    ("AD5", "e_amanha", D + "IMG_3448.MOV", "0.7-10.5",
     "Dentista, é amanhã! Evento online e gratuito", 0.6),
    ("AD6", "o_que_preciso_fazer", D + "IMG_3449.MOV", "2.1-8.1,8.5-16.3,32.2-36.8,45.6-48.0",
     "Sou dentista no Brasil 🇧🇷 O que preciso pra trabalhar nos EUA 🇺🇸?", 0.6),
    ("AD7", "preciso_revalidar", D + "IMG_3450.MOV", "0.8-5.0,5.6-10.5,44.6-47.8,48.6-50.7",
     "Preciso revalidar meu diploma pra trabalhar nos EUA 🇺🇸?", 0.6),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    for rid, nome, video, trechos, gancho, aperto in ADS:
        y_leg = "0.64" if "Edits_Ads" in video else "0.55"      # selfie: rosto grande, legenda abaixo do queixo
        if filtro and rid not in filtro:
            continue
        print(f"\n######## {rid} {nome}", flush=True)
        cmd = [sys.executable, EDITOR, video, "--marca", "imigrar",
               "--trechos", trechos, "--gancho", gancho, "--nome", f"{rid}_{nome}", "--saida", PASTA,
               "--y-legenda", y_leg, "--checar-olhar"]
        if aperto:
            cmd += ["--aperto", str(aperto)]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd.append("--so-cortes")
        subprocess.run(cmd, cwd=IN26)
