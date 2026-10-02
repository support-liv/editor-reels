#!/usr/bin/env python3
"""Live "Plano EUA 2027" (28/09/2026), Marinna Damásio (Imigrar) + Dra. Lívia Leite (LIV).
Layout dividido: Dra. Lívia em cima, Marinna embaixo, legenda e tarja na divisa. Enquadramento fixo.
Só o trecho em que as duas aparecem juntas (43:30 a 81:30).
Rodar tudo:            python3 lote_live.py
Só conferir os cortes: python3 lote_live.py --so-cortes
Só alguns:             python3 lote_live.py L01 L07
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
VIDEO = os.path.expanduser(os.environ.get("LIVE_VIDEO", "~/Downloads/PLANO EUA 2027 - 28_09 - 20H.mp4"))
SAIDA = os.path.expanduser(os.environ.get("LIVE_SAIDA", "~/Desktop/PLANO_EUA_2027/prontos"))
CTA = "Quer saber se existe um caminho pro seu perfil? Link na bio"
CORES = ["branco", "azul", "rosa"]              # a tarja alterna entre os cortes
TROCAS = ["Green Car=green card", "Green Kind=green card", "o Brincar=o green card", "na cidade da Andes=a cidadania",
          "EB2MW=EB-2 NIW", "EB2NW=EB-2 NIW", "AB2NW=EB-2 NIW", "EB2-NW=EB-2 NIW", "web2nw=EB-2 NIW", "EB1A=EB-1A",
          "EB1=EB-1", "EB2=EB-2", "EB3=EB-3", "EB5=EB-5", "H1B=H-1B", "L1=L-1", "O1=O-1", "O1A=O-1A", "E2=E-2",
          "USAS=USCIS", "iOSAS=USCIS", "TOF=TOEFL", "dra. Livre=doutora Lívia", "elegebilidade=elegibilidade",
          "discrecionariedade=discricionariedade", "conge=cônjuge", "congé=cônjuge", "detista=dentista",
          "E tem o uso outros dois=E tem outros dois", "bem contemporâneo=vem com o temporário",
          "Eu estou dizendo que todos=Eu não estou dizendo que todos",
          "separar os temporários=separar os caminhos em grupos. Tem os vistos temporários",
          "cachorro para pagar a periquí=cachorro, papagaio, periquito", "Tudo é igual.=Tudo é igual?",
          "Visa Bollarding=Visa Bulletin", "desnistificar=desmistificar", "Tancan é um multinacional comum à Johnson=tem que ser uma multinacional como a Johnson"]

CORTES = [
    # id, nome, trechos ("a-b?" = pergunta), gancho
    ("L01", "ela_ja_foi_imigrante", "2675.9-2703.5,2704.9-2727.5",
     "Ela já foi imigrante. Hoje é advogada de imigração nos EUA 🇺🇸"),
    ("L02", "achava_que_era_so_casando", "2745.5-2772.7,2773.0-2788.5",
     "Achava que só dava pra morar nos EUA 🇺🇸 casando?"),
    ("L03", "caminhos_legais", "2846.9-2856.3?,2857.8-2877.3",
     "Quero morar e trabalhar nos EUA 🇺🇸. Quais são os caminhos legais?"),
    ("L04", "visto_temporario_tempo", "3013.4-3053.5",
     "Visto temporário: em quanto tempo você está nos EUA 🇺🇸?"),
    ("L05", "green_card_sem_emprego", "3068.4-3110.1",
     "Dá pra ter green card 🇺🇸 sem oferta de emprego?"),
    ("L06", "dois_vistos_ao_mesmo_tempo", "3118.7-3151.2",
     "Dá pra aplicar pra dois vistos americanos 🇺🇸 ao mesmo tempo?"),
    ("L07", "profissao_nao_define", "3173.0-3185.5?,3190.5-3196.6,3215.7-3226.2,3240.5-3259.6",
     "Sua profissão define o seu visto americano 🇺🇸?"),
    ("L08", "ingles_pesa_no_visto", "3345.2-3347.6?,3382.8-3397.9,3398.3-3418.5,3419.2-3429.3",
     "Precisa falar inglês pra tirar o visto americano 🇺🇸?"),
    ("L09", "professora_de_ingles", "3452.2-3471.4,3502.7-3510.3",
     "Ela contratou uma professora de inglês só pra entrevista do consulado 🇺🇸"),
    ("L10", "conjuge_e_filhos", "3600.2-3608.9?,3610.7-3639.0,3642.6-3651.0",
     "Cônjuge e filhos vão junto no visto americano 🇺🇸?"),
    ("L11", "filho_perto_dos_21", "3658.5-3673.7,3677.4-3710.4",
     "Seu filho tem 19 anos? Presta atenção nisso 🇺🇸"),
    ("L12", "visto_negado_lista_negra", "3881.0-3892.8?,3894.0-3931.3",
     "Visto americano 🇺🇸 negado: você entra numa lista negra?"),
    ("L13", "negativa_nao_define_voce", "4214.6-4236.0,4242.3-4261.3",
     "Seu visto americano 🇺🇸 foi negado. E agora?"),
    ("L14", "um_oficial_nega_outro_aprova", "4148.0-4155.8,4183.2-4211.9",
     "O mesmo processo com dois oficiais diferentes. O que acontece?"),
    ("L15", "premium_processing", "4322.2-4345.4,4358.8-4377.5",
     "Vale pagar o premium processing no visto americano 🇺🇸?"),
    ("L16", "outra_cidadania_ajuda", "4414.4-4418.9?,4453.7-4490.0",
     "Ter cidadania europeia 🇪🇺 ajuda no green card 🇺🇸?"),
    ("L17", "mito_da_profissao", "4525.3-4530.4?,4534.7-4565.7,4603.9-4619.6",
     "Falta engenheiro nos EUA 🇺🇸, então vou ser aprovado?"),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    os.makedirs(SAIDA, exist_ok=True)
    for i, (cid, nome, trechos, gancho) in enumerate(CORTES):
        if filtro and cid not in filtro:
            continue
        print(f"\n######## {cid} {nome} (tarja {CORES[i % 3]})", flush=True)
        cmd = [sys.executable, EDITOR, VIDEO, "--layout", "dividido", "--cima", "direita", "--marca", "imigrar", "--cor-caixa", CORES[i % 3],
               "--trechos", trechos, "--gancho", gancho, "--cta", CTA, "--nome", f"{cid}_{nome}", "--saida", SAIDA]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd.append("--so-cortes")
        subprocess.run(cmd)
