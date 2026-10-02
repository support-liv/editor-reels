#!/usr/bin/env python3
"""Reels do Dr. Ricardo (IN26), todos na identidade Imigrar.
Rodar tudo:            python3 lote_ricardo.py
Só conferir os cortes: python3 lote_ricardo.py --so-cortes
Só alguns:             python3 lote_ricardo.py R07 P01
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
# pasta com os vídeos brutos e onde saem os prontos (mude com: export IN26_DIR=/caminho/da/pasta)
IN26 = os.path.expanduser(os.environ.get("IN26_DIR", "~/Desktop/IN26"))
V18, V5, V1 = [os.path.join(IN26, n) for n in ("IMG_3463.MOV", "IMG_3465.MOV", "IMG_3464.MOV")]
CTA = "Quer saber se existe um caminho pro seu perfil? Link na bio"
TROCAS = ["mas aquele não tem=mas aqui não tem", "só dentista=sou dentista", "dr=Dr.", "um gente sério=com gente séria", "uma gente conversou=como a gente conversou",
          "primeira de coisa=primeira coisa", "de governo americano=o governo americano",
          "vcb1=EB-1", "ex -aluno=ex-aluno"]

REELS = [
    # id, nome, vídeo, trechos, gancho
    ("R01", "brasileiro_e_melhor", V18, "129.0-142.8,144.0-166.6",
     "Por que o dentista americano 🇺🇸 ganha mais, se o brasileiro 🇧🇷 é melhor?"),
    ("R02", "ganhar_e_nao_poder_usar", V18, "361.0-404.5",
     "De que adianta ganhar bem e não poder usar o seu dinheiro?"),
    ("R03", "americanos_aprendem_aqui", V5, "5.6-34.9,73.8-82.1",
     "Dentista americano 🇺🇸 vem pro Brasil 🇧🇷 aprender com a gente"),
    ("R04", "falta_dentista", V5, "98.7-123.8,124.3-131.4",
     "A maior rede de clínicas do Brasil 🇧🇷 tentou abrir nos EUA 🇺🇸 Não deu."),
    ("R05", "profissao_e_pra_ganhar_dinheiro", V1, "6.8-21.6,42.9-73.8",
     "Profissão é pra quê? Pra ganhar dinheiro."),
    ("R06", "primeiro_passo", V18, "892.4-901.1,901.7-908.5,918.3-938.0",
     "Dentista que quer ir pros EUA 🇺🇸: o primeiro passo é esse"),
    ("R07", "previsibilidade", V18, "103.4-114.5,421.3-424.8,562.3-569.3,1036.9-1047.3",
     "Por que eu sempre quis morar nos EUA 🇺🇸"),
    ("R08", "uma_janela", V18, "144.0-182.1",
     "Os EUA 🇺🇸 estão precisando de dentista. E isso é uma janela."),
    ("R09", "o_que_falta_aqui", V18, "217.2-237.6,238.2-253.0",
     "O que o dentista encontra nos EUA 🇺🇸 e não encontra aqui"),
    ("R10", "porta_da_frente", V18, "273.0-296.1,297.3-319.0",
     "Quer ir pros EUA 🇺🇸? Entre pela porta da frente"),
    ("R11", "caso_do_ex_aluno", V18, "319.3-344.8",
     "Meu ex-aluno está sozinho numa clínica nos EUA 🇺🇸 Olha o resultado."),
    ("R12", "sem_alianca", V18, "405.4-439.8",
     "No Brasil a gente se acostumou a não sair de aliança"),
    ("R13", "futuro_dos_netos", V18, "542.35-559.0,571.8-594.1",
     "Vou fazer 70 anos. Mas penso no futuro dos meus netos."),
    ("R14", "o_que_organizar", V18, "674.8-717.1",
     "O que o dentista precisa organizar antes de imigrar pros EUA 🇺🇸"),
    ("R15", "como_pagar_a_faculdade", V18, "750.5-793.1",
     "Faculdade de odonto nos EUA 🇺🇸 pode custar 80 mil dólares por ano. Como pagar?"),
    ("R16", "nao_e_passeio", V18, "811.3-846.6",
     "Mudar de país não é passeio"),
    ("R17", "se_aceitam_e_porque_precisam", V18, "905.6-918.3,940.5-958.2",
     "Se os EUA 🇺🇸 aceitam dentista brasileiro, é porque precisam"),
    ("R18", "prova_sem_green_card", V18, "958.2-993.0",
     "Dá pra fazer a prova americana 🇺🇸 sem green card?"),
    ("R19", "presta_atencao", V18, "858.6-874.2,892.4-901.1",
     "Dentista, presta atenção nisso antes de pensar em ir pros EUA 🇺🇸"),
    ("R20", "nao_refaz_a_faculdade", V5, "174.3-185.7,210.7-233.2",
     "Dentista brasileiro não precisa refazer a faculdade inteira nos EUA 🇺🇸"),
    ("R21", "470_mil_dentistas", V5, "118.3-123.8,131.6-152.7",
     "O Brasil tem mais de 470 mil dentistas. Imagina se tivesse 50 mil."),
    ("R22", "muito_com_pouco", V5, "54.1-76.1,78.5-82.1",
     "O dentista brasileiro 🇧🇷 aprendeu a fazer muito com pouco"),
    ("R23", "lucro_e_etica", V1, "22.1-42.7,52.7-73.8",
     "Empresa que não dá lucro não é ética. Vale pro dentista também."),
]

# Série "pergunta como gancho": a pergunta do Lucas abre o vídeo em quadro aberto, depois fecha no Ricardo.
PERGUNTAS = [
    # id, nome, vídeo, trecho da pergunta, trechos da resposta, gancho
    ("P01", "o_que_e_board", V5, "169.8-173.5", "174.3-185.7,210.7-233.2",
     "Sou dentista: o que é o board americano 🇺🇸?"),
    ("P02", "o_que_e_pace", V5, "234.6-237.3", "238.5-268.2",
     "Sou dentista: o que é a PACE dos EUA 🇺🇸?"),
    ("P03", "existe_oportunidade", V5, "91.4-95.3", "98.7-123.8,124.3-131.4",
     "Existe oportunidade pra dentista brasileiro 🇧🇷 nos EUA 🇺🇸?"),
    ("P04", "como_os_eua_veem", V5, "1.0-5.1", "5.6-34.9,73.8-82.1",
     "Como os EUA 🇺🇸 enxergam o dentista brasileiro?"),
    ("P05", "por_que_escolher_os_eua", V1, "1.8-5.4", "6.8-21.6,52.7-73.8",
     "Por que um dentista brasileiro 🇧🇷 escolheria os EUA 🇺🇸?"),
    ("P06", "o_que_la_tem", V18, "195.3-201.5", "217.2-237.6,238.2-253.0",
     "O que o dentista encontra nos EUA 🇺🇸 que falta aqui?"),
    ("P07", "carreira_consolidada", V18, "352.4-359.0", "361.0-397.6",
     "Carreira consolidada no Brasil 🇧🇷 Por que planejar os EUA 🇺🇸?"),
    ("P08", "o_que_organizar", V18, "668.3-674.4", "674.8-717.1",
     "O que o dentista precisa organizar antes de imigrar pros EUA 🇺🇸?"),
    ("P09", "dica_pra_quem_pensa", V18, "886.0-891.5", "892.4-901.1,901.7-908.5,918.3-938.0",
     "Qual a dica pra quem pensa em ir pros EUA 🇺🇸?"),
    ("P10", "por_que_os_eua", V18, "93.8-98.7", "103.4-114.5,124.0-142.8",
     "O que fez você olhar pros EUA 🇺🇸?"),
]

# Série B: "amo o Brasil, mas não vejo futuro" / dentista desvalorizado. Topo de funil, pasta separada.
PASTA_BRASIL = os.path.join(IN26, "prontos", "topo_brasil_sem_futuro")
BRASIL = [
    ("B01", "amo_o_brasil_mas", V18, "571.8-594.1,167.2-182.1",
     "Eu amo o Brasil 🇧🇷 Mas não enxergo futuro aqui"),
    ("B02", "doi_falar_isso", V18, "576.8-594.1,405.4-417.3",
     "Dói falar isso, mas eu não vejo um futuro bom pro Brasil 🇧🇷"),
    ("B03", "desvalorizacao", V1, "56.9-68.3,42.9-51.0,68.6-73.9",
     "A concorrência na odonto brasileira 🇧🇷 ficou muito ruim"),
    ("B04", "ganha_e_nao_pode_usar", V18, "383.5-398.0,405.4-421.2",
     "No Brasil 🇧🇷 você trabalha, ganha bem... e não pode usar o que conquistou"),
    ("B05", "preparado_sem_oportunidade", V18, "129.2-142.8,273.0-281.0,167.2-182.1",
     "O dentista brasileiro 🇧🇷 é muito bem preparado. O que falta é oportunidade."),
    ("B06", "a_conta_nao_fecha", V5, "131.6-152.7,56.1-65.0",
     "Mais de 470 mil dentistas no Brasil 🇧🇷 E a conta não fecha"),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    tarefas = [(r[0], r[1], r[2], r[3], r[4], None, None) for r in REELS]
    tarefas += [(p[0], p[1], p[2], p[4], p[5], p[3], None) for p in PERGUNTAS]
    tarefas += [(b[0], b[1], b[2], b[3], b[4], None, PASTA_BRASIL) for b in BRASIL]
    for rid, nome, video, trechos, gancho, pergunta, pasta in tarefas:
        if filtro and rid not in filtro:
            continue
        print(f"\n######## {rid} {nome}", flush=True)
        cmd = [sys.executable, EDITOR, video, "--pessoa", "direita",
               "--marca", "imigrar", "--trechos", trechos, "--gancho", gancho, "--cta", CTA,
               "--nome", f"{rid}_{nome}"]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if pergunta:
            cmd += ["--pergunta", pergunta]
        if pasta:
            cmd += ["--saida", pasta]
        if so:
            cmd.append("--so-cortes")
        if "--so-checar-caixas" in sys.argv:
            cmd.append("--so-checar-caixas")
        subprocess.run(cmd, cwd=IN26)
