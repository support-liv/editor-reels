#!/usr/bin/env python3
"""Live "Plano EUA 2027": cortes solo da Marinna (primeiros 43 min, antes da Dra. Lívia entrar).
Layout "quadro": imagem da live nítida no meio (sem a faixa de baixo, onde aparece o chat),
fundo desfocado, gancho acima e legenda abaixo. Enquadramento fixo.
Rodar tudo:            python3 lote_mari_solo.py
Só conferir os cortes: python3 lote_mari_solo.py --so-cortes
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
VIDEO = os.path.expanduser(os.environ.get("LIVE_VIDEO", "~/Downloads/PLANO EUA 2027 - 28_09 - 20H.mp4"))
SAIDA = os.path.expanduser(os.environ.get("LIVE_SAIDA", "~/Desktop/PLANO_EUA_2027/prontos"))
CTA = "Quer saber se existe um caminho pro seu perfil? Link na bio"
CORES = ["azul", "rosa", "branco"]
TROCAS = ["ninguém chega que fluente=ninguém chega fluente", "gafel=gafe", "o Toro de Viva=a doutora Lívia",
          "Vocês já se quiseram muito em um carro=Vocês já quiseram muito um carro", "revéu=réveillon"]

CORTES = [
    ("M01", "quer_e_nao_sai_do_lugar", "183.5-217.1",
     "Por que tanta gente quer morar nos EUA 🇺🇸 e não sai do lugar?"),
    ("M02", "que_canseira", "621.8-662.3",
     "Você também sente essa canseira?"),
    ("M03", "querendo_demais", "794.7-812.8,817.7-845.8",
     "Já te disseram que você está querendo demais?"),
    ("M04", "o_momento_certo", "905.2-921.9,926.2-956.05",
     "Você está esperando o momento certo pra mudar de vida?"),
    ("M05", "medo_numero_um", "989.9-1037.3",
     "Qual é o medo número um de quem quer morar nos EUA 🇺🇸?"),
    ("M06", "sorry_about_my_english", "1080.1-1098.1,1098.5-1130.9",
     "Eu pedi desculpas pelo meu inglês. Olha o que a americana respondeu"),
    ("M07", "precisa_chegar_fluente", "1180.3-1226.7",
     "Precisa chegar nos EUA 🇺🇸 falando inglês fluente?"),
    ("M08", "americano_repete_a_frase", "1422.8-1454.8,1461.8-1464.8",
     "Por que o americano repete o que você acabou de falar?"),
    ("M09", "so_pra_quem_e_rico", "1542.4-1565.9,1576.5-1597.8,1622.9-1626.3",
     "Morar nos EUA 🇺🇸 é só pra quem é rico?"),
    ("M10", "o_primeiro_carro", "1658.4-1691.8,1742.9-1754.95",
     "O que o meu primeiro carro me ensinou sobre o visto americano 🇺🇸"),
    ("M11", "precisa_visto_de_turismo", "1870.2-1879.6,1883.5-1913.7",
     "Precisa ter visto de turismo pra imigrar pros EUA 🇺🇸?"),
    ("M12", "comecar_do_zero", "2040.2-2083.3",
     "Vou chegar nos EUA 🇺🇸 e começar do zero?"),
    ("M13", "trabalho_que_americano_nao_quer", "2179.5-2191.7,2196.5-2198.9,2211.0-2242.7",
     "Imigrante só pega o trabalho que o americano não quer?"),
    ("M14", "dinheiro_vem_facil", "2445.5-2477.4",
     "Nos EUA 🇺🇸 o dinheiro vem fácil?"),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(SAIDA, exist_ok=True)
    for i, (cid, nome, trechos, gancho) in enumerate(CORTES):
        if filtro and cid not in filtro:
            continue
        print(f"\n######## {cid} {nome} (tarja {CORES[i % 3]})", flush=True)
        cmd = [sys.executable, EDITOR, VIDEO, "--layout", "quadro", "--marca", "imigrar", "--cor-caixa", CORES[i % 3],
               "--trechos", trechos, "--gancho", gancho, "--cta", CTA, "--nome", f"{cid}_{nome}", "--saida", SAIDA]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd.append("--so-cortes")
        subprocess.run(cmd)
