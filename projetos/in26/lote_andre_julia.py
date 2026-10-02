#!/usr/bin/env python3
"""Reels do André e da Julia (IN26), identidade Imigrar.
Rodar tudo:            python3 lote_andre_julia.py
Só conferir os cortes: python3 lote_andre_julia.py --so-cortes
Só alguns:             python3 lote_andre_julia.py A01 C03

Trechos: "a-b?" = pergunta do Lucas nessa posição. Na conversa (IMG_3455) o quadro fecha em quem fala (tom de voz).
"""
import subprocess, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
# pasta com os vídeos brutos e onde saem os prontos (mude com: export IN26_DIR=/caminho/da/pasta)
IN26 = os.path.expanduser(os.environ.get("IN26_DIR", "~/Desktop/IN26"))
O = os.path.join(IN26, "videos ja gravados", "outros") + "/"
PASTA = os.path.join(IN26, "prontos", "andre_julia")
TOPO = os.path.join(IN26, "prontos", "topo_brasil_sem_futuro")
CTA = "Quer saber se existe um caminho pro seu perfil? Link na bio"
TROCAS = ["de ploma=diploma", "a dedutista=o dentista", "não é possível que=é possível que",
          "o registro=o dentista", "com o seu PES=com o seu pass", "a gente fala do processo de imigração dos caras=a gente fala do processo de imigração",
          "implanta odontista=implantodontista", "implanto dentista=implantodontista", "implanta dentista=implantodontista",
          "vou com maxílo facial=bucomaxilofacial", "implantando autista=implantodontista", "Visto 1=visto O-1",
          "a Nene=a nenê", "a Julie=a Júlia", "TOFEL=TOEFL"]

REELS = [
    # id, nome, vídeo, trechos, gancho, pessoa, pasta
    # --- André, dia 2 (pergunta + resposta)
    ("A01", "precisa_revalidar", O + "IMG_3466.MOV", "2.9-6.6?,7.3-37.8",
     "Dentista brasileiro 🇧🇷 precisa revalidar o diploma nos EUA 🇺🇸?", None, PASTA),
    ("A02", "quanto_ganha", O + "IMG_3467.MOV", "2.2-5.3?,5.8-36.6",
     "Quanto ganha um dentista nos EUA 🇺🇸 e no Brasil 🇧🇷", None, PASTA),
    ("A03", "consultorio_tecnologia", O + "IMG_3468.MOV", "1.3-6.3?,8.9-43.2",
     "A diferença entre um consultório no Brasil 🇧🇷 e nos EUA 🇺🇸", None, PASTA),
    ("A04", "nao_faz_tudo_sozinho", O + "IMG_3468.MOV", "43.3-77.6",
     "Nos EUA 🇺🇸 o dentista não faz tudo sozinho", None, PASTA),
    ("A05", "como_os_eua_veem", O + "IMG_3469.MOV", "1.9-5.8?,6.4-32.1",
     "Como os EUA 🇺🇸 enxergam o dentista brasileiro?", None, PASTA),
    ("A06", "existe_oportunidade", O + "IMG_3470.MOV", "1.6-5.0?,5.5-39.4,47.3-49.5",
     "Existe oportunidade pra dentista brasileiro 🇧🇷 nos EUA 🇺🇸?", None, PASTA),
    ("A07", "poucos_dentistas", O + "IMG_3470.MOV", "17.4-39.4,39.6-47.1",
     "EUA 🇺🇸: 330 milhões de pessoas e só 200 mil dentistas", None, PASTA),
    ("A08", "o_que_incomoda", O + "IMG_3471.MOV", "1.5-5.5?,6.2-13.5,35.8-63.8",
     "O que mais incomoda na odonto brasileira 🇧🇷 hoje", None, TOPO),
    ("A09", "operadoras_e_preco", O + "IMG_3471.MOV", "13.9-35.7,47.0-54.8,64.2-70.2",
     "Na odonto brasileira 🇧🇷: operadora pagando tabela irreal e concorrência desleal", None, TOPO),
    ("A10", "por_onde_comecar", O + "IMG_3377.MOV", "2.4-6.5?,6.9-24.0",
     "Sou dentista e quero ir pros EUA 🇺🇸 Por onde começo?", None, PASTA),
    # --- Julia, dia 1
    ("A11", "julia_tempo_e_ingles", O + "IMG_3386.MOV", "1.0-4.4?,4.9-16.0,19.0-22.0?,22.6-36.8",
     "Quanto tempo estudar pra prova americana 🇺🇸? E com que inglês?", None, PASTA),
    ("A12", "julia_primeiros_passos", O + "IMG_3384.MOV", "2.5-7.7?,7.9-25.7",
     "Sou dentista e quero ir pros EUA 🇺🇸 Quais os primeiros passos?", None, PASTA),
    ("A13", "julia_por_que_sair", O + "IMG_3380.MOV", "1.0-6.9?,7.5-26.6",
     "13 anos de carreira. Por que ela decidiu sair do Brasil 🇧🇷?", None, PASTA),
    ("A14", "julia_valorizacao", O + "IMG_3381.MOV", "5.5-11.6?,12.2-28.2",
     "O que me levou a querer a odonto americana 🇺🇸", None, PASTA),
    ("A15", "julia_bem_estabelecido", O + "IMG_3382.MOV", "1.3-6.7?,7.4-40.9",
     "Pro dentista bem estabelecido que pensa nos EUA 🇺🇸", None, PASTA),
    ("A16", "julia_etapas", O + "IMG_3385.MOV", "1.6-10.5?,10.9-33.5",
     "As etapas pra trabalhar como dentista nos EUA 🇺🇸", None, PASTA),
    # --- André, dia 1
    ("A17", "andre_por_que_imigrar", O + "IMG_3368.MOV", "3.2-9.0?,9.6-41.5",
     "13 anos de carreira no Brasil 🇧🇷 Por que imigrar?", None, PASTA),
    ("A18", "andre_melhor_perfil", O + "IMG_3370.MOV", "1.4-7.1?,7.6-22.5,45.8-62.6",
     "O dentista bem estabelecido é o melhor perfil pros EUA 🇺🇸", None, PASTA),
    ("A19", "andre_especialidade", O + "IMG_3371.MOV", "1.3-7.6?,8.4-23.4,38.1-46.7,50.3-63.7",
     "Implantodontista: por que a especialidade vale mais nos EUA 🇺🇸", None, PASTA),
    ("A20", "andre_primeiros_passos", O + "IMG_3373.MOV", "1.5-5.9?,6.0-25.6,39.3-52.3",
     "Primeiro passo pro dentista que quer ir pros EUA 🇺🇸", None, PASTA),
    ("A21", "andre_tres_portas", O + "IMG_3374.MOV", "2.7-6.6?,30.1-54.6",
     "A prova americana 🇺🇸 que abre 3 portas pro dentista", None, PASTA),
    ("A22", "andre_tempo_de_estudo", O + "IMG_3375.MOV", "1.3-3.7?,4.4-26.4,36.0-40.7",
     "Quanto tempo estudar pra prova americana 🇺🇸?", None, PASTA),
    ("A23", "andre_ingles", O + "IMG_3375.MOV", "41.4-44.3?,44.6-68.0,81.1-89.0",
     "Precisa de inglês fluente pra prova americana 🇺🇸?", None, PASTA),
    ("A24", "andre_familia_e_carreira", O + "IMG_3369.MOV", "2.1-6.3?,19.3-57.1",
     "O que o dentista encontra nos EUA 🇺🇸 pensando em família e carreira", None, PASTA),
    # --- conversa com os dois (IMG_3455): fecha em quem fala
    ("C01", "por_que_decidiram", O + "IMG_3455.MOV", "22.4-24.7?,25.6-39.8,45.3-64.3",
     "Por que um casal de dentistas decidiu ir pros EUA 🇺🇸", "voz", PASTA),
    ("C02", "o_momento_da_decisao", O + "IMG_3455.MOV", "80.8-82.5?,83.1-96.7,97.9-124.3",
     "O momento em que a gente decidiu ir pros EUA 🇺🇸", "voz", PASTA),
    ("C03", "estudar_com_bebe", O + "IMG_3455.MOV", "212.0-216.8?,217.6-254.8@2",
     "Estudar pra prova americana 🇺🇸 com uma bebê que acordava de madrugada", "voz", PASTA),
    ("C04", "as_contas_chegam", O + "IMG_3455.MOV", "256.0-262.9@1,263.1-284.0@1",
     "Dá pra parar de trabalhar pra estudar? As contas chegam.", "voz", PASTA),
    ("C05", "prova_e_visto_juntos", O + "IMG_3455.MOV", "293.8-318.5@2",
     "A gente fez a prova e o processo de visto americano 🇺🇸 ao mesmo tempo", "voz", PASTA),
    ("C06", "a_renda_caiu", O + "IMG_3455.MOV", "319.9-328.2?,328.3-355.2@1,367.9-383.4@1",
     "A renda do brasileiro caiu. E o dentista sente isso 🇧🇷", "voz", TOPO),
    ("C07", "dentista_demais", O + "IMG_3455.MOV", "367.9-400.4@1",
     "O Brasil 🇧🇷 tem dentista demais pra uma população endividada", "voz", TOPO),
    ("C08", "segunda_a_quinta", O + "IMG_3455.MOV", "405.7-412.6?,426.6-447.9@1,454.0-469.3@1",
     "Dentista nos EUA 🇺🇸 trabalha de segunda a quinta", "voz", PASTA),
    ("C09", "preciso_revalidar", O + "IMG_3455.MOV", "490.3-493.9?,494.8-511.6,606.9-619.5",
     "Sou dentista: preciso revalidar o diploma nos EUA 🇺🇸?", "voz", PASTA),
    ("C10", "a_dica", O + "IMG_3455.MOV", "513.1-518.7?,519.3-535.9@1,576.7-597.8@1",
     "A dica pra dentista que pensa em ir pros EUA 🇺🇸", "voz", PASTA),
    ("C11", "nao_existe_caminho_facil", O + "IMG_3455.MOV", "602.5-627.4@2",
     "Não existe caminho fácil. E é igual pra todo mundo.", "voz", PASTA),
]

if __name__ == "__main__":
    so = "--so-cortes" in sys.argv
    filtro = [a for a in sys.argv[1:] if not a.startswith("--")]
    for rid, nome, video, trechos, gancho, pessoa, pasta in REELS:
        if filtro and rid not in filtro:
            continue
        print(f"\n######## {rid} {nome}", flush=True)
        cmd = [sys.executable, EDITOR, video, "--marca", "imigrar",
               "--trechos", trechos, "--gancho", gancho, "--cta", CTA, "--nome", f"{rid}_{nome}", "--saida", pasta]
        if pessoa:
            cmd += ["--pessoa", pessoa]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if so:
            cmd.append("--so-cortes")
        if "--so-checar-caixas" in sys.argv:
            cmd.append("--so-checar-caixas")
        subprocess.run(cmd, cwd=IN26)
