#!/usr/bin/env python3
"""Live "Jornada do dentista nos EUA" (14/09, Imigrar): Marinna Damásio + Dra. Júlia e Dr. André (casal de dentistas).

Formato novo: live com 3 pessoas. A live alterna entre a Marinna sozinha (08:14-10:19) e 3 colunas
(Júlia | Marinna | André). Lista de cortes da equipe: docs "corte longo" (cold open + 15 trechos).

    python3 projetos/jornada_dentista/lote.py longo            # corte longo 16:9 (YouTube), sem vinheta (Imigrar)
    python3 projetos/jornada_dentista/lote.py trechos          # recorta os trechos dos shorts (o Whisper transcreve cada um)
    python3 projetos/jornada_dentista/lote.py palavras [D1..]  # exporta palavras e duração (pro roteiro do motion)
    python3 projetos/jornada_dentista/lote.py shorts [D1..]    # shorts 9:16 com motion (motion/renders/dentista_<id>.mov)

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
# id, nome, trechos (segundos da live), gancho, pessoas (colunas cima,baixo; None = Marinna sozinha em tela cheia), tarja
SHORTS = [
    ("D1", "e_daqui_a_dez_anos", [(493.0, 536.75), (598.5, 619.75)],
     "Dentista: você investiu tanto pra chegar só até aqui?", None, "rosa"),
    ("D2", "sonho_pela_familia", [(985.2, 1047.4)],
     "Bem posicionados no Brasil. Por que olhar pros EUA 🇺🇸?", "3,1", "azul"),
    ("D3", "bebe_e_a_prova", [(1564.7, 1568.9), (1572.1, 1638.4)],
     "Bebê de 1 ano e a prova do Board: como ela estudou?", "1,2", "branco"),
    ("D4", "o_que_e_o_inbde", [(2155.3, 2166.2), (2180.3, 2238.5)],
     "Dentista brasileiro: você sabe o que é o INBDE?", "1,2", "rosa"),
    ("D5", "dds_ou_aigd", [(2383.0, 2412.9), (2436.0, 2450.8)],
     "DDS ou AIGD: qual licença pra atuar nos EUA 🇺🇸?", "3,2", "azul"),
    ("D6", "limite_de_idade", [(3883.5, 3931.0)],
     "Existe limite de idade pro dentista imigrar?", "2,1", "branco"),
]

# cortes finos dentro de cada trecho, pelas palavras do Whisper (a legenda do YouTube vem ~0,8s adiantada)
REL = {"D1": "1.58-45.6,107.0-128.35", "D2": "1.42-64.2", "D3": "0.6-5.56,8.76-76.6",
       "D4": "1.4-12.4,25.4-56.6,64.7-84.8", "D5": "1.3-33.2,54.2-69.3", "D6": "1.4-48.9"}

TROCAS = ["Imigrarê=Imigrar", "Emigrareua=Imigrar", "Livre Immigration Law=LIV Immigration Law",
          "Marina Damasio=Marinna Damásio", "Marina=Marinna", "Green Car=green card", "plantodontia=implantodontia",
          "implanta odontia=implantodontia",
          "INBD=INBDE", "DTS=DDS", "custa de revalidação=custo de revalidação", "beber de um ano=bebê de um ano",
          "Julia=Júlia", "que é valida=revalida", "se aprovado=ser aprovado"]


def rodar(cmd):
    print(" ".join(cmd[:4]), "...", flush=True)
    subprocess.run(cmd, check=True)


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
    for sid, nome, faixas, gancho, pessoas, cor in SHORTS:
        if filtro and sid not in filtro:
            continue
        ini, fim = faixas[0][0] - 1.5, faixas[-1][1] + 1.5
        arq = os.path.join(TRECHOS, f"{sid}_{nome}.mp4")
        if modo == "trechos":                       # recorte exato (reencodado) pra o Whisper transcrever só o trecho
            rodar(["ffmpeg", "-v", "error", "-y", "-ss", f"{ini:.3f}", "-to", f"{fim:.3f}", "-i", LIVE,
                   "-c:v", "h264_videotoolbox", "-b:v", "24M", "-c:a", "aac", "-b:a", "192k", arq])
            continue
        rel = REL.get(sid) or ",".join(f"{a - ini:.2f}-{b - ini:.2f}" for a, b in faixas)
        cmd = ["python3", EDITOR, arq, "--marca", "imigrar", "--manter-perguntas", "--trechos", rel, "--gancho", gancho,
               "--cor-caixa", cor, "--tirar-hesitacoes", "--respiro", "0.18", "--cauda", str(CAUDA)]
        if pessoas:
            cmd += ["--layout", "dividido", "--colunas", "3", "--pessoas", pessoas]
        for t in TROCAS:
            cmd += ["--trocar", t]
        if modo == "palavras":
            cmd += ["--json-palavras", os.path.join(AQUI, "motion", "palavras", f"{sid}.json")]
            rodar(cmd)
            rodar([c for c in cmd if c != "--json-palavras" and not c.endswith(f"{sid}.json")] + ["--tempos-palavras"])
        else:
            cmd += ["--broll", os.path.join(MOTION, f"dentista_{sid}.mov") + "@0",
                    "--nome", f"{sid}_{nome}", "--saida", os.path.join(SAIDA, "shorts")]
            rodar(cmd)


if __name__ == "__main__":
    main()
