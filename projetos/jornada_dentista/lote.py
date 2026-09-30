#!/usr/bin/env python3
"""Live "Jornada do dentista nos EUA" (14/09, Imigrar): Marinna Damásio + Dra. Júlia e Dr. André (casal de dentistas).

Formato novo: live com 3 pessoas. A live alterna entre a Marinna sozinha (08:14-10:19) e 3 colunas
(Júlia | Marinna | André). Lista de cortes da equipe (docx "corte longo"): 1 corte longo com cold open + os 15 trechos, e cada
um dos 15 trechos vira um short.

    python3 projetos/jornada_dentista/lote.py longo            # corte longo 16:9 (YouTube), sem vinheta (Imigrar)
    python3 projetos/jornada_dentista/lote.py trechos [S01..]      # recorta os 15 trechos dos shorts
    python3 projetos/jornada_dentista/lote.py transcrever [S01..]  # Whisper em cada trecho (confira palavras esticadas!)
    python3 projetos/jornada_dentista/lote.py palavras [S01..]     # exporta palavras e duração (pro roteiro do motion)
    python3 projetos/jornada_dentista/lote.py shorts [S01..]       # 15 shorts 9:16 com motion (motion/renders/dentista_<id>.mov)

Shorts: com a Marinna sozinha, vertical em tela cheia; com as 3 colunas, tela dividida com quem conversa
(colunas da live: 1 = Júlia, 2 = Marinna, 3 = André). CTA do YouTube: "Veja a live completa no canal".

Transcrição do corte longo: legenda .vtt do YouTube (editor/vtt_para_json.py).
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
EDITOR = os.path.join(AQUI, "..", "..", "editor", "editor_reels.py")
MOTION = os.path.join(AQUI, "..", "..", "motion", "renders")
LIVE = os.path.expanduser(os.environ.get("JORNADA_VIDEO", "~/Downloads/JORNADA DO DENTISTA NOS EUA- 14_09 às 20h.mp4"))
SAIDA = os.path.expanduser(os.environ.get("JORNADA_SAIDA", "~/Desktop/JORNADA_DENTISTA"))

# (início, fim) em segundos da live, na ordem da lista da equipe; o 1º é o cold open
LONGO = [
    (598.5, 619.75),    # 09:58 cold open: "Você é uma pessoa que hoje a vida está boa..." -> "...para os seus filhos?"
    (493.0, 536.75),    # 08:14 "Mas eu quero que você pense..." -> "...espaço para minha família"
    (563.4, 598.2),     # 09:23 "Profissionais qualificados..." -> "...não caiba nessa esfera mais"
    (848.4, 890.7),     # 14:08 Júlia: "Bom, eu me formei em odontologia..." -> "...cirurgia bucomaxilofacial"
    (922.9, 955.1),     # 15:23 André: "Eu me formei também já tem treze anos..." -> "...área da docência"
    (985.2, 1047.4),    # 16:25 "E surgiu esse sonho..." -> "...ficar mais com a nossa família, tudo isso"
    (1047.9, 1107.5),   # 17:28 "Então, nós fomos aprovados na prova do NBD..." -> "...se organiza para aquilo"
    (1356.4, 1435.1),   # 22:36 "Porque geralmente é assim..." -> "...mais portas se abram para vocês"
    (1554.9, 1568.9),   # 25:55 "De resolver que essa era uma oportunidade..." -> "...vou fazer minha prova"
    (1572.1, 1638.4),   # 26:12 "Não, gente, não tinha tempo sobrando." -> "...alcançar o meu objetivo"
    (1687.6, 1760.5),   # 28:07 "Foi um processo bem cansativo..." -> "...o inglês que eu precisava para a prova"
    (2155.3, 2238.5),   # 35:54 "O que que é o INBDE?" -> "...cada estado tem sua legislação"
    (2365.5, 2456.9),   # 39:25 "Aqui nós vamos ter diferentes tipos de licenças..." -> "...cada estado nos Estados Unidos"
    (2697.0, 2749.8),   # 44:57 "Por isso que eu falo que o processo imigratório..." -> "...a faculdade sem preocupação, gente"
    (3850.6, 3931.0),   # 64:10 "Então, que não é imediato..." -> "...a gente tem data de validade, né gente?"
    (4314.9, 4345.7),   # 71:54 "Porque a gente está aqui falando..." -> "...olhar para o repertório profissional e entender"
]
TRECHOS = os.path.join(SAIDA, "trechos")
CAUDA = 3.8
# Os 15 shorts: cada trecho da lista (menos o cold open), do começo ao fim da frase do documento.
# id, nome, frase de início, frase de fim, gancho, pessoas (colunas cima,baixo; None = Marinna sozinha, vertical em
# tela cheia), tarja. Colunas da live: 1 = Júlia, 2 = Marinna, 3 = André. O arquivo do trecho vem de LONGO[1:].
SHORTS = [
    ("S01", "voce_investiu_na_carreira", "mas eu quero que você pense", "espaço pra minha família",
     "Você investiu tanto na carreira. É só isso que tem pra você?", None, "rosa"),
    ("S02", "profissionais_qualificados", "profissionais qualificados", "não caiba nessa esfera mais",
     "Qualificado, experiente… e sem espaço pra crescer?", None, "azul"),
    ("S03", "a_carreira_da_julia", "bom eu me formei em odontologia", "buco maxilo facial",
     "Cirurgiã do Exército no Brasil. Por que ela mudou de rota?", "1,2", "branco"),
    ("S04", "a_carreira_do_andre", "eu me formei também", "área da docência",
     "13 anos de carreira e professor. Por que sonhar com os EUA 🇺🇸?", "3,2", "rosa"),
    ("S05", "sonho_pela_familia", "e surgiu esse sonho", "com a nossa família tudo isso",
     "Bem posicionados no Brasil. Por que olhar pros EUA 🇺🇸?", "3,1", "azul"),
    ("S06", "aprovados_no_board", "então nós fomos aprovados", "se organiza para aquilo",
     "A prova do Board é só pra quem é gênio?", "3,2", "branco"),
    ("S07", "imigrar_e_revalidar", "porque geralmente é assim", "portas se abram para vocês",
     "Imigrar e revalidar o diploma: qual vem primeiro?", "2,1", "rosa"),
    ("S08", "tinha_tempo_sobrando", "que essa era uma oportunidade", "fazer minha prova",
     "Ela tinha tempo sobrando pra estudar pra prova?", "2,1", "azul"),
    ("S09", "bebe_e_a_prova", "não gente não tinha tempo", "alcançar o meu objetivo",
     "Bebê de 1 ano e a prova do Board: como ela estudou?", "1,2", "branco"),
    ("S10", "ingles_basico", "foi um processo bem cansativo", "que eu precisava para a prova",
     "Inglês básico dá pra passar na prova do Board?", "1,2", "rosa"),
    ("S11", "o_que_e_o_inbde", "o que que é o", "cada estado tem sua legislação",
     "Dentista brasileiro: você sabe o que é o INBDE?", "1,2", "azul"),
    ("S12", "dds_ou_aigd", "aqui nós vamos ter diferentes tipos", "dentro de cada estado nos estados unidos",
     "DDS ou AIGD: qual licença pra atuar nos EUA 🇺🇸?", "3,2", "branco"),
    ("S13", "financiamento_estudantil", "por isso que eu falo que o processo", "faculdade sem preocupação gente",
     "Sem trabalhar, como pagar a faculdade de odontologia nos EUA 🇺🇸?", "2,1", "rosa"),
    ("S14", "nao_e_imediato", "então que não é imediato", "data de validade",
     "Existe limite de idade pro dentista imigrar?", "2,1", "azul"),
    ("S15", "genio_da_lampada", "porque a gente está aqui falando", "o repertório profissional e entender",
     "Existe gênio da lâmpada pra carreira nos EUA 🇺🇸?", "2,1", "branco"),
]

TROCAS = ["Imigrarê=Imigrar", "Emigrareua=Imigrar", "Livre Immigration Law=LIV Immigration Law",
          "Marina Damasio=Marinna Damásio", "Marina=Marinna", "Green Car=green card", "plantodontia=implantodontia",
          "implanta odontia=implantodontia",
          "INBD=INBDE", "DTS=DDS", "custa de revalidação=custo de revalidação", "beber de um ano=bebê de um ano",
          "Julia=Júlia", "que é valida=revalida", "se aprovado=ser aprovado",
          "investirão=investiram", "implanto da ontia=implantodontia", "buco maxilo facial=bucomaxilofacial",
          "Júlio=Júlia", "estímulos estudantis=empréstimos estudantis",
          "NVIDIA=INBDE", "Marino=Marinna", "EB1=EB-1", "EB2NW=EB-2 NIW", "pode ser abrir=pode se abrir",
          "IGD=AIGD", "desses dois estados=desses 12 estados", "passo de mágica=passe de mágica", "não imediato=não é imediato",
          "não um passe=não é um passe", "que eu acho que é muito importante culto cultural=cultural", "tenha condição=tem a condição"]




def rodar(cmd):
    print(" ".join(cmd[:4]), "...", flush=True)
    subprocess.run(cmd, check=True)


def rel_por_frases(arq, ini_frase, fim_frase):
    """trecho exato dentro do arquivo recortado, pelas palavras do Whisper: da 1ª palavra da frase de início até o fim
    da frase de fim (com folga, sem pegar a palavra seguinte). A legenda do YouTube vem ~0,8s adiantada."""
    import json, re, unicodedata
    norm = lambda w: re.sub(r"[^a-z0-9 ]", "", "".join(c for c in unicodedata.normalize("NFD", w.lower()) if unicodedata.category(c) != "Mn"))
    cache = os.path.join(AQUI, "..", "..", "editor", "transcricoes", os.path.splitext(os.path.basename(arq))[0] + ".json")
    P = json.load(open(cache))["palavras"]
    toks = [norm(p["w"]) for p in P]

    def achar(frase, depois=0, do_fim=False):
        """a frase inteira; se o Whisper escreveu diferente, as últimas (fim) ou primeiras (início) palavras dela."""
        pal = norm(frase).split()
        for n in range(len(pal), 0, -1):
            alvo = pal[-n:] if do_fim else pal[:n]
            if n < len(pal) and n < 2 and len(alvo[0]) < 5:
                break
            achados = [i for i in range(depois, len(toks) - len(alvo) + 1) if toks[i:i + len(alvo)] == alvo]
            if achados:                               # início: a 1ª vez; fim: a última (a frase fecha o trecho)
                return (achados[-1] if do_fim else achados[0]), len(alvo)
        sys.exit(f'{os.path.basename(arq)}: não achei "{frase}" na transcrição do trecho')
    i, _ = achar(ini_frase)
    e, n = achar(fim_frase, i, do_fim=True)
    e = e + n - 1
    fim = P[e]["e"] + 0.35
    if e + 1 < len(P):
        fim = min(fim, P[e + 1]["s"] - 0.03)
    return f"{max(0, P[i]['s'] - 0.08):.2f}-{fim:.2f}"


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "longo"
    if modo == "longo":
        trechos = ",".join(f"{a}-{b}" for a, b in LONGO)
        cmd = ["python3", EDITOR, LIVE, "--layout", "youtube", "--marca", "imigrar", "--sem-vinheta", "--manter-perguntas",
               "--trechos", trechos, "--nome", "jornada_dentista_corte_longo", "--saida", os.path.join(SAIDA, "corte_longo")]
        for t in TROCAS:
            cmd += ["--trocar", t]
        rodar(cmd)
        return
    filtro = sys.argv[2:]
    os.makedirs(TRECHOS, exist_ok=True)
    os.makedirs(os.path.join(AQUI, "motion", "palavras"), exist_ok=True)
    for (sid, nome, f_ini, f_fim, gancho, pessoas, cor), (a, b) in zip(SHORTS, LONGO[1:]):
        if filtro and sid not in filtro:
            continue
        arq = os.path.join(TRECHOS, f"{sid}_{nome}.mp4")
        if modo == "trechos":                       # recorte exato (reencodado) pra o Whisper transcrever só o trecho
            rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{a - 1.5:.3f}", "-to", f"{b + 2.0:.3f}", "-i", LIVE,
                   "-c:v", "h264_videotoolbox", "-b:v", "24M", "-c:a", "aac", "-b:a", "192k", arq])
            continue
        if modo == "transcrever":                   # só o Whisper (o editor guarda a transcrição do trecho)
            rodar(["python3", EDITOR, arq, "--marca", "imigrar", "--so-cortes"])
            continue
        rel = rel_por_frases(arq, f_ini, f_fim)
        cmd = ["python3", EDITOR, arq, "--marca", "imigrar", "--manter-perguntas", "--trechos", rel, "--gancho", gancho,
               "--cor-caixa", cor, "--tirar-hesitacoes", "--respiro", "0.18", "--cauda", str(CAUDA)]
        if pessoas:
            cmd += ["--layout", "dividido", "--colunas", "3", "--pessoas", pessoas]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if modo == "palavras":
            rodar(cmd + ["--json-palavras", os.path.join(AQUI, "motion", "palavras", f"{sid}.json")])
            rodar(cmd + ["--tempos-palavras"])
        else:
            rodar(cmd + ["--broll", os.path.join(MOTION, f"dentista_{sid}.mov") + "@0",
                         "--nome", f"{sid}_{nome}", "--saida", os.path.join(SAIDA, "shorts")])


if __name__ == "__main__":
    main()
