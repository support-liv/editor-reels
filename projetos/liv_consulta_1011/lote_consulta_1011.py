"""LIV · Dra. Lívia em consulta com cliente (10/11/2026, 7 partes): 9 Reels verticais, UMA versão cada.

  final (padrão) = com motion só nos cortes em que dá para desenhar o raciocínio (COM_MOTION); nos outros, só legenda
  A = sem motion: gancho + legenda + CTA "Comente PERFIL27" em tela cheia logo após a fala final
  B = com motion: o mesmo, mais cenas de B-roll animado da LIV no ritmo da fala (roteiros em motion/<id>.json)

Cuidados (consulta com cliente): nenhum corte leva o nome, a voz ou dados da cliente (marido, filha, datas, empresa),
nem a voz do consultor que a acompanhava. Só as explicações gerais da Dra. Lívia. Sem promessa de prazo ou aprovação.
Linha de corte aprovada: bloco contínuo na ordem da fala, contexto inteiro, CTA logo após a última palavra.
O balão do gancho da LIV é sempre o padrão (não alterna cor como na Imigrar).

Uso: python3 projetos/liv_consulta_1011/lote_consulta_1011.py [final|A|B] [id ...] [--so-montar] [--esperado]
"""
import json, os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "imigrar_ti_ads"))
import lote_ti as LT

LT.BRUTOS = "/Users/lucastoledo/Downloads/Gravacao Livia"
LT.W, LT.H = 1920, 1080                           # bruto 1080p 16:9: o vertical recorta em volta da Dra. Lívia
# a 1ª entrega (10-11/11/2026) ficou na pasta original do cartão; rodar de novo grava aqui
SAIDA = os.environ.get("LIV_SAIDA", "/Volumes/Untitled/LIV_cortes/consulta_1011")
MOTION = os.path.join(LT.RAIZ, "motion")
ROTEIROS = os.path.join(AQUI, "motion")
CAUDA = 3.8
PREFIXO_MOTION = "c1011"   # nome dos roteiros/HTML/.mov de motion deste lote
PREFIXO = "liv_consulta_1011"     # nome dos arquivos de saída (outro projeto que reusa este lote troca)
ZONA = [300, 1460]        # faixa onde o bloco de cada cena é centralizado (meio ~880 px, acima da interface do Reels)
TAM_COMPONENTE = {"colunas": {"tam": 110, "tam_texto": 64}, "checklist": {"tam": 78, "passo": 120},
                  "etapas": {"tam": 76, "passo": 128}, "barra": {"tam": 56}, "degraus": {"tam": 54}}
PALAVRA, CTA_TEXTO = "PERFIL27", "para uma análise do seu perfil"
# Lucas (10/11): uma linha só pra LIV, motion só onde ilustra o raciocínio (processo, prazo, número, estrutura)
COM_MOTION = {"c1_processing_time", "c4_regra_90_dias", "c5_i94_banimento", "c7_sorteio_h1b", "c9_o1_empregador_estrangeiro"}

# o nome do bruto leva o nome da cliente: o lote acha pelo padrão (o repositório é público, nada de nome de cliente)
import glob
_ach = glob.glob(os.path.join(LT.BRUTOS, "2026-11-10_gravacao-10-11-14-03-reuniao-consulta-*_take-01-006.mp4"))
_P = os.path.basename(_ach[0])[:-len("-006.mp4")] if _ach else "bruto_nao_encontrado"
P1, P2, P3, P5, P6 = (f"{_P}-006.mp4", f"{_P}_parte-02-001.mp4", f"{_P}_parte-03-004.mp4",
                      f"{_P}_parte-05-003.mp4", f"{_P}_parte-06-005.mp4")

# grafia da legenda (Whisper: "USIS", "AUSIS", "A1" = O-1, "IH -1B", "ready flag")
LT.FRASES += [("USIS,", "USCIS,"), ("USIS.", "USCIS."), ("USIS", "USCIS"), ("AUSIS", "USCIS"), ("o AUSIS", "o USCIS"),
              ("SAS", "USCIS"), ("Processing Time.", "Processing Times."), ("IH -1B.", "H-1B."), ("IH-1B.", "H-1B."),
              ("HMB?", "H-1B?"), ("HMB.", "H-1B."), ("HMB", "H-1B"), ("H1B,", "H-1B,"), ("H1B.", "H-1B."), ("H1B", "H-1B"),
              ("O A1", "O O-1"), ("A1", "O-1"), ("no O.", "no O-1."), ("do O", "do O-1"), ("como O,", "como o O-1,"),
              ("com o O,", "com o O-1,"), ("o O,", "o O-1,"), ("AOL", "O-1"), ("o OCC,", "o O-1,"), ("a H1B,", "o H-1B,"), ("80 %", "80%"), ("ir pra judicado,", "prejudicar,"),
              ("pra judicado,", "prejudicar,"),
              ("vistos de que a gente", "vistos de trabalho que a gente"), ("alugou um carro", "aluga um carro"),
              ("é às vezes Vai", "às vezes vai"), ("às vezes Vai", "às vezes vai"), ("Né? e É, esse", "E esse"), ("Né? E, e É, esse", "E esse"), ("seja migratório.", "seja imigratório."),
              ("tem a Green Card", "tem o Green Card"),
              ("car fraude,", "fraude,"), ("Três anos,", "três anos,"), ("passou -se", "passou-se"),
              ("a migração", "a imigração"), ("e diturismo", "e o de turismo"), ("diturismo", "o de turismo"),
              ("aí, o mais, um", "aí, mais um"), ("o mais,", "mais"), ("maço,", "março,"), ("maço", "março"),
              ("o AOSS", "o USCIS"), ("AOSS", "USCIS"), ("essa leção?", "essa seleção?"), ("leção?", "seleção?"),
              ("do O,", "do O-1,"), ("lhe adicionar", "lhe peticionar"), ("se não é oficial,", "senão o oficial..."),
              ("E a outro tipo", "E o outro tipo"), ("a outro tipo", "o outro tipo"), ("voç,", "você,"), ("OCC,", "O-1,"), ("a H-1B,", "o H-1B,"), ("Green Car ou", "Green Card ou"), ("ready flag", "red flag"),
              ("oficiária...", "oficial..."), ("Foreign Employer.", "foreign employer."), ("for employer", "foreign employer"),
              ("emigratório.", "imigratório."), ("emigratória", "imigratória"), ("Green Car,", "Green Card,"),
              ("Green Car.", "Green Card."), ("Green Car", "Green Card"), ("discrecionário", "discricionário"),
              ("pré -operacional,", "pré-operacional,"), ("traibilidade", "viabilidade"), ("tinerário", "itinerário"),
              ("F2,", "F-2,"), ("F2.", "F-2."), ("F2", "F-2"), ("I -94", "I-94"), ("I -94,", "I-94,"), ("I -94.", "I-94.")]

# (gancho, [(arquivo, início, fim[, "exato"])]): tempos do bruto, conferidos no tempo das palavras
REELS = {
    # "você tá com... vai completar 24" e o "4 ou 6 meses / 12 / 24" são a cliente: saem
    "c1_processing_time": ("Como ler o prazo do seu processo no USCIS?", [
        (P1, 375.88, 398.88), (P1, 414.62, 420.02)]),
    # começa no "hoje em dia" (o "Eu concordo" respondia à cliente); fecha no "trabalhar." (depois vinha
    # "não têm problema, não têm tendo problema", embolado)
    "c2_visto_entrevista": ("Turista e estudante estão difíceis? Qual visto ainda passa na entrevista?", [
        (P2, 90.74, 139.26, "exato")]),
    "c3_acoes_turista": ("O que um turista não pode fazer antes de trocar de visto?", [
        (P3, 340.00, 363.75, "exato"), (P3, 366.20, 411.36)]),      # "às vezes | vai, vai pra, vai, vai pra... | vai alugar"
    "c4_regra_90_dias": ("Quanto tempo esperar para pedir a troca de visto nos EUA 🇺🇸?", [
        (P2, 287.50, 320.72)]),
    # "não volta durante | três meses, | três anos": sai o "três meses" (ela se corrige)
    "c5_i94_banimento": ("Troca de visto negada depois de meses: o que acontece com você?", [
        (P5, 315.82, 354.20, "exato"), (P5, 354.90, 356.00)]),
    # começa no 2º "em algumas situações"; "pode acontecer, | [nome da cliente]. | quando eles desconfiam": sai o nome;
    # "eu | escutei esse relato, | escutei esse relato que": sai o 1º
    "c6_consulado_cancela": ("Pedir outro visto no consulado pode cancelar seu visto de turista?", [
        (P5, 196.35, 198.20, "exato"), (P5, 198.42, 231.12, "exato"), (P5, 232.78, 244.62, "exato")]),   # sem o "e ficar" do fim
    "c7_sorteio_h1b": ("Como funciona hoje o sorteio do H-1B?", [
        (P6, 35.02, 48.36), (P6, 97.76, 114.16), (P6, 136.66, 138.66, "exato"), (P6, 140.80, 155.90)]),
    # "é muito objetivo, | o cara crachar ali pra posição, | a empresa": sai a frase embolada
    "c8_o1_empresa_propria": ("Dá para tirar o O-1 com a sua própria empresa?", [
        (P6, 175.40, 240.38)]),     # começa no "Você ou tem um empregador" ("O O-1 vai ter as duas, as, tem as dois, as duas partes" embolava)
    "c9_o1_empregador_estrangeiro": ("Uma empresa brasileira pode te levar com o O-1 para os EUA 🇺🇸?", [
        (P6, 314.74, 365.12)]),
}
# repetição de estilo conferida uma a uma: "seleciona o formulário, seleciona o tipo", "o prazo. O prazo não é pra
# frente, é pra trás" (c1), "como o O-1, como o H-1B" (c2), "o grande, grande ponto" (c3), "um agente. Um agente é" e "o agente, e o agente é quem?" (c9)
PERMITIR = {"c1_processing_time", "c2_visto_entrevista", "c3_acoes_turista", "c9_o1_empregador_estrangeiro"}


def cmd_editor(id_, video):
    gancho = REELS[id_][0]
    return [sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "liv",
            "--gancho", gancho, "--seg-gancho", "4.2", "--alinhar", "--vad", "--tirar-hesitacoes",
            "--respiro", "0.22", "--proteger-palavra", "0.40", "--manter-perguntas",
            # menos espaço acima da cabeça sem ficar "caruda" (Lucas, 10/11): aberto 88% da altura, fechado 0,9 dele
            "--aperto", "0.82", "--punch", "0.90", "--gancho-embaixo"]     # balão longe da testa (Lucas, 10/11)


def fala_e_palavras(id_, video):
    """duração da fala no vídeo pronto e as palavras no tempo do pronto (pro motion sincronizar)."""
    os.makedirs(os.path.join(ROTEIROS, "palavras"), exist_ok=True)
    arq = os.path.join(ROTEIROS, "palavras", id_ + ".json")
    base = cmd_editor(id_, video)
    subprocess.run(base + ["--json-palavras", arq], check=True, capture_output=True)
    out = subprocess.run(base + ["--tempos-palavras"], check=True, capture_output=True, text=True).stdout
    fala = float([l for l in out.splitlines() if l.startswith("DURACAO")][0].split()[1])
    return fala, arq


def cena_cta(fala):
    # a "fala" do editor já inclui ~0,6s de respiro depois da última palavra: o CTA entra 0,3s antes do fim dela
    # (~0,35s depois da última palavra), sem cena parada (linha de corte aprovada)
    return {"tipo": "cta", "t0": round(fala - 0.3, 2), "t1": round(fala + CAUDA, 2), "painel": "cheio",
            "acima": "Comente", "palavra": PALAVRA, "texto": CTA_TEXTO, "tam_texto": 84,
            "base": 700}                                   # bloco do CTA no meio da tela (Lucas, 10/11), não no topo


def render_motion(nome, roteiro):
    """roteiro -> HTML (gerar_liv) -> .mov transparente (HyperFrames, local)."""
    caminho = os.path.join(ROTEIROS, nome + ".json")
    json.dump(roteiro, open(caminho, "w"), ensure_ascii=False, indent=1)
    subprocess.run([sys.executable, os.path.join(MOTION, "gerar_liv.py"), caminho], check=True)
    mov = os.path.join(MOTION, "renders", nome + ".mov")
    subprocess.run(["npx", "hyperframes", "render", ".", "-c", f"modelos/{nome}.html", "--format", "mov", "--workers", "1", "-o", mov],
                   cwd=MOTION, check=True)
    return mov



def main():
    modo = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("A", "B", "final") else "final"
    ids = [a for a in sys.argv[1:] if not a.startswith("--") and a not in ("A", "B", "final")] or list(REELS)
    for id_ in ids:
        versao = modo if modo != "final" else ("B" if id_ in COM_MOTION else "A")
        pasta = os.path.join(SAIDA, {"A": "A_sem_motion", "B": "B_com_motion"}[versao] if modo != "final" else "")
        os.makedirs(pasta, exist_ok=True)
        print(f"\n=== {id_} ({versao})", flush=True)
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        try:
            video, _ = LT.montar(id_, REELS[id_][1])
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e, flush=True); continue
        if "--so-montar" in sys.argv:
            continue
        fala, arq_pal = fala_e_palavras(id_, video)
        if versao == "A":
            nome_m = f"{PREFIXO_MOTION}_{id_}_cta"
            mov = render_motion(nome_m, {"nome": nome_m, "duracao": round(fala + CAUDA, 2), "fala": fala,
                                         "cenas": [cena_cta(fala)]})
        else:
            rot = json.load(open(os.path.join(ROTEIROS, id_ + ".json")))      # cenas de motion escritas à mão
            rot.update({"nome": f"{PREFIXO_MOTION}_{id_}", "duracao": round(fala + CAUDA, 2), "fala": fala,
                        "palavras": os.path.relpath(arq_pal, ROTEIROS)})
            rot["cenas"] = [c for c in rot["cenas"] if c.get("tipo") != "cta"] + [cena_cta(fala)]
            # pedido do Lucas (10/11): motion no centro da tela, na vertical e na horizontal, componentes maiores
            rot.update({"zona": ZONA, "centralizar_componentes": True})
            for c in rot["cenas"]:
                if c.get("tipo") != "cta":
                    c.setdefault("alinhar", "centro")
                    for e in c.get("elementos", []):
                        for k, v in TAM_COMPONENTE.get(e["tipo"], {}).items():
                            e.setdefault(k, v)
            mov = render_motion(f"{PREFIXO_MOTION}_{id_}", rot)
        nome = f"{PREFIXO}_{id_}" if modo == "final" else f"{PREFIXO}_{id_}_{versao}"
        LT.rodar_editor(cmd_editor(id_, video) + ["--cauda", str(CAUDA), "--broll", mov + "@0",
                                                  "--nome", nome, "--saida", pasta], nome)


if __name__ == "__main__":
    main()
