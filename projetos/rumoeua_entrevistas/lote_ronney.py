"""Imigrar · Ronney (Frinhani Custom Woodwork, Kissimmee), nov/2026.
Brutos horizontais 4K no HD (IMG_6160 = estacionamento, 35 min; IMG_6161 = dentro da fábrica, 14 min). As cenas da
fábrica (cenas_empresa/) viram B-roll em pé (_broll_ronney/ no cartão).

Regras desta entrevista:
- ele pediu pra cortar o processo de visto (EB3, "corta isso aí": 1174-1220 do IMG_6160); nada de visto/processo;
- nada de política (o trecho do governo, 117-157);
- gancho no padrão Imigrar (caixa alta, bandeira escrita) que NÃO entrega a resposta (loop); abertura que provoca.
Saída: base sem CTA em /Volumes/Untitled/Imigrar_cortes/_base; o CTA preto (YouTube e Instagram) entra no cta_imigrar.py.

Uso: python3 projetos/rumoeua_entrevistas/lote_ronney.py [id ...] [--so-montar]
"""
import json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "imigrar_ti_ads"))
import lote_ti as LT  # noqa: E402
sys.path.insert(0, AQUI)
import vento  # noqa: E402

ORIGEM = ["/Volumes/Lucas HD2/Ronney/ENTREVISTA RONNEY", "/Volumes/Lucas HD2/Ronney/Gravacao Ronney COndominio"]
LT.BRUTOS = os.path.expanduser("~/Library/Caches/editor-reels/ronney_brutos")
LT.W, LT.H = 3840, 2160
SAIDA = "/Volumes/Untitled/Imigrar_cortes/_base"
BROLL = "/Volumes/Untitled/Imigrar_cortes/_broll_ronney"
CORES = ["branco", "azul", "rosa"]
P, F = "IMG_6160.MOV", "IMG_6161-001.MOV"
K1, K3 = "IMG_5991.MOV", "IMG_5993.MOV"
LT.FRASES += [("Rony", "Ronney"), ("Rony,", "Ronney,"), ("Rony.", "Ronney."), ("Rony?", "Ronney?"), ("Ronny,", "Ronney,"), ("Ronny", "Ronney"), ("Ronnie", "Ronney"), ("Honey,", "Ronney,"), ("Friñani", "Frinhani"),
              ("Friani.", "Frinhani."), ("burocasias", "burocracias"), ("nessa perda", "nessa terra"), ("flota", "Flórida"),
              ("neglicenciar", "negligenciar"), ("Plaiude", "plywood"), ("marcineiros", "marceneiros"),
              ("carga horário", "carga horária"), ("trabalhado,", "trabalhada,"), ("amobilhada.", "mobiliada."),
              ("a multiobra", "a mão de obra"), ("afirmado", "firmado"), ("Fânico?", "Ronney?"), ("mercenaria", "marcenaria"), ("Ronei,", "Ronney,"), ("Bosto,", "Boston,"), ("enfestem", "enfeitam"), ("miliantes", "meliantes"),
              ("ôrnico?", "Ronney?"), ("aqui, Manoel?", "aqui, Ronney?"), ("maçanaria", "marcenaria"), ("lembra pra minha vida.", "lema pra minha vida."),
              ("mante obra", "mão de obra"), ("reciclano.", "ciclano."), ("Quid", "Kwid"), ("inscrição de segurança", "questão de segurança"), ("Breno, da Lívia,", "Breno, da LIV,")]

# áudio limpo no Adobe Enhance Speech (10/11/2026), trilha inteira ao lado de cada bruto, sincronia conferida (0 ms).
# Com ele o filtro de vento (vento.py) não roda mais: o Adobe já tirou o vento.
LT.AUDIO = {P: "/Volumes/Lucas HD2/Ronney/ENTREVISTA RONNEY/IMG_6160_audio_tratado.wav",
            K1: "/Volumes/Lucas HD2/Ronney/Gravacao Ronney COndominio/IMG_5991_audio_tratado.wav",
            K3: "/Volumes/Lucas HD2/Ronney/Gravacao Ronney COndominio/IMG_5993_audio_tratado.wav"}

_SEG = {}


def _segs(arq):
    if arq not in _SEG:
        _SEG[arq] = json.load(open(os.path.join(LT.TRANSC, os.path.splitext(arq)[0] + ".json")))["segmentos"]
    return _SEG[arq]


def S(arq, de, ate):
    """pedaço por segmentos da transcrição: do segmento que começa em ~de (s) até o que começa em ~ate (inclusive)."""
    sg = _segs(arq)
    idx = [i for i, s in enumerate(sg) if de <= round(s["s"]) <= ate]
    assert idx, (arq, de, ate)
    i0, i1 = idx[0], idx[-1]
    fim = sg[i1 + 1]["s"] if i1 + 1 < len(sg) else sg[i1]["e"] + 0.3
    return (arq, sg[i0]["s"] - 0.05, min(fim, sg[i1]["e"] + 0.6))


def W(arq, a, b):
    """pedaço por tempo de palavra: da palavra que começa em a até antes da que começa em b."""
    return (arq, a - 0.05, b)


# id: (gancho, pedaços, b-rolls [(arquivo do _broll_ronney, bruto, segundo no bruto)])
REELS = {
    # 10/11 (Lucas aprovou a linha do c02 da Patrícia): UM bloco contínuo por corte, na ordem da fala, sem cold open e sem
    # emendar trecho de outra parte da conversa. A pergunta do Lucas só entra se a resposta não se sustenta sem ela, e
    # enxuta (sem "Ô, Ronney", "legal", "te interrompendo", "tem ideia?"). Tempos por palavra (IMG_*.json).
    "n01_vendeu_tudo": ("Ele vendeu tudo no Brasil 🇧🇷 em 3 meses. Se arrepende?", [
        W(P, 567.06, 612.30), W(P, 612.38, 618.70), W(P, 625.08, 631.80)], []),   # sem as 2 repetições do "não ter tomado antes"
    "n02_por_que_saiu": ("Ele tinha casa e empresa no Brasil. Por que saiu? 🇧🇷", [
        S(P, 170, 178), S(P, 189, 212)], []),                 # sem o "o que foram esses incidentes?" do Lucas; turismo -> 2 incidentes -> assaltos -> "decidi que não queria mais viver no Brasil"
    "n03_cliente_confia": ("O que um cliente americano fez que nenhum brasileiro faria 🇺🇸", [
        W(P, 864.52, 927.10), W(P, 933.78, 950.28)], []),     # sem pergunta: "o cliente americano confia em você" -> código da casa -> cheque
    "n04_abrir_empresa": ("Quanto tempo leva pra abrir uma empresa nos EUA 🇺🇸?", [
        S(P, 1500, 1539)], [("escritorio", P, 1517.0)]),    # sem pergunta: "a burocracia de abrir uma empresa aqui é mínima"
    "n05_imposto": ("O que acontece com quem sonega imposto nos EUA 🇺🇸?", [
        W(P, 1559.20, 1617.30)], []),                         # sem pergunta: "a vida aqui é menos burocrática" -> sonegar = cadeia
    "n06_filha_ingles": ("Em quanto tempo uma criança aprende inglês nos EUA 🇺🇸?", [
        W(P, 1290.46, 1346.30)], []),                         # sem pergunta: "sua filha com 30 dias vai estar falando inglês"
    "n07_america_pra_todos": ("Os EUA 🇺🇸 são pra todo mundo?", [
        W(P, 1389.36, 1421.20), W(P, 1427.00, 1434.40)], []), # "Aqui você cresce" ... (sem a questão migratória)
    "n08_corvette": ("Quanto custa um Corvette nos EUA 🇺🇸?", [
        W(P, 69.74, 76.50), W(P, 77.30, 115.80)], []),        # pergunta enxuta; sem o trecho de carro-bem do fim (outra parte)
    "n09_dois_anos": ("O que ele precisou aprender antes de empreender nos EUA 🇺🇸", [
        W(P, 669.40, 700.20)], []),                           # sem pergunta: "Em dois anos eu decidi aprender muita coisa"
    "n10_california": ("Como uma marcenaria brasileira chegou até a Califórnia 🇺🇸?", [
        W(P, 777.24, 780.40), W(P, 782.36, 847.20)], [("armario_pronto", P, 834.0)]),
    "n11_pastor": ("O que o pastor disse antes dele sair do Brasil 🇧🇷", [
        W(P, 1955.88, 2027.00), W(P, 2033.58, 2048.70)], []), # sem pergunta: "minha mãe ficou até surpresa"
    "n12_medo_tentar": ("A frase que fez ele arriscar tudo de novo nos EUA 🇺🇸", [
        W(P, 1877.66, 1937.70)], [("coladeira_borda", P, 1914.0)]),   # sem pergunta: "eu nunca tive medo de tentar"
    "f01_primeiro_cliente": ("O serviço pequeno que abriu o mercado americano pra ele 🇺🇸", [
        W(F, 275.86, 314.00)], [("montagem_dupla", F, 296.0)]),   # "um dos meus primeiros clientes foi a dona Heidi e o seu Jay"
    "f02_sem_clt": ("Como funciona trabalhar sem CLT nos EUA 🇺🇸?", [
        S(F, 495, 540)], [("bancada", F, 512.0)]),           # sem pergunta: "a carga horária aqui depende do ramo"
    "f03_ia": ("Empreender com IA nos EUA: funciona? 🇺🇸", [
        W(F, 571.98, 609.50), W(F, 621.48, 631.00), W(F, 631.14, 651.00)], [("ronney_3d", F, 584.0), ("ronney_desenho", F, 642.0)]),
    "f04_conselho": ("Quer empreender nos EUA? Faça isso antes... 🇺🇸", [
        W(F, 664.05, 723.30)], []),                           # pergunta sem o "Ronney,"
    "f05_pesadelo": ("Por que o sonho americano vira pesadelo pra tanta gente? 🇺🇸", [
        W(F, 764.38, 802.30)], []),                           # sem pergunta: "se você pensar muito, você não faz"
    "f06_concorrencia": ("O erro dos brasileiros que empreendem nos EUA 🇺🇸", [
        W(F, 314.82, 389.30)], [("galpao", F, 370.0)]),      # pergunta sem o "Ô, Ronney"
    "f07_bem_feito": ("A regra que fez o negócio dele crescer nos EUA 🇺🇸", [
        W(F, 230.80, 264.40)], [("montagem_furadeira", F, 250.0)]),   # sem pergunta: "adotei o seguinte lema pra minha vida"
    "k01_boston_inverno": ("Um carioca no inverno de Boston 🇺🇸: deu certo?", [
        W(K1, 408.24, 446.30), W(K1, 456.50, 467.70), (K1, 486.35, S(K1, 481, 512)[2])], []),   # sem perguntas, sem Halloween
    "k02_grama_hoa": ("A regra de condomínio nos EUA que brasileiro não imagina 🇺🇸", [
        W(K1, 355.12, 399.60)], []),                          # sem o "inclusive isso aqui é muito interessante"
    "k03_sem_raiz": ("Ele pensa em voltar pro Brasil 🇧🇷?", [
        W(K3, 21.11, 49.60), W(K3, 63.76, 79.80)], []),       # sem pergunta; sem o "cenário do Brasil hoje" (política)
    "k04_poder_compra": ("O que dá pra comprar nos EUA 🇺🇸 que no Brasil 🇧🇷 é coisa de milionário?", [
        S(K3, 231, 279)], []),                                # sem a fala do Lucas: "o poder de compra então nem se fala"
    "k05_sente_falta": ("Do que ele sente falta do Brasil 🇧🇷 depois de 9 anos?", [
        W(K3, 170.52, 172.40), W(K3, 178.12, S(K3, 169, 207)[2])], []),   # pergunta + "minha esposa fala que eu sou atípico"
    "k06_acordar_perdendo": ("Por que empreender no Brasil 🇧🇷 é acordar perdendo?", [
        W(K1, 243.58, 275.95), (K1, 279.45, S(K1, 222, 298)[2])], []),   # sem pergunta e sem "nas eleições agora"
    "k07_paz_sem_muro": ("O que mais impressiona quem chega nos EUA 🇺🇸?", [
        W(K1, 66.10, 150.50)], []),                           # pergunta sem "Ronney,"; inteiro, com o "legalmente" (antes cortado)
}
for _id, (_g, _p, _b) in REELS.items():               # 10/11: sem cold open, a fala toca na ordem em que foi dita
    _p.sort(key=lambda x: (x[0], x[1]))
# condomínio (Lucas, 10/11): estava fechado demais (zoom de ~2x num 4K tremido = qualidade ruim). Plano aberto quase na
# altura toda (resolução nativa no 1080) e fechado leve
EXTRA = {k: ["--pessoa", "esquerda", "--perguntas-auto", "--aperto", "0.92", "--punch", "0.85"] for k in REELS if k.startswith("k")}


def atalhos():
    os.makedirs(LT.BRUTOS, exist_ok=True)
    for pasta in ORIGEM:
        for a in os.listdir(pasta):
            if a.upper().endswith(".MOV") and not a.startswith("._"):
                dest = os.path.join(LT.BRUTOS, a)
                if os.path.lexists(dest) and not os.path.exists(dest):
                    os.remove(dest)
                if not os.path.exists(dest):
                    os.symlink(os.path.join(pasta, a), dest)


def main():
    atalhos()
    os.makedirs(SAIDA, exist_ok=True)
    if "--forcar" not in sys.argv:
        sys.argv.append("--forcar")                         # repetição de estilo é dele; os recomeços foram tirados acima
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(REELS)
    for id_ in ids:
        gancho, pedacos, brolls = REELS[id_]
        print(f"\n=== {id_}", flush=True)
        try:
            video, mapa = LT.montar(id_, pedacos)
        except SystemExit as e:
            print("  PULADO:", e, flush=True); continue
        if "--so-montar" in sys.argv:
            print("  ", json.load(open(os.path.join(LT.TRANSC, id_ + ".json")))["texto"][:600], flush=True)
            continue
        nome = f"imigrar_ronney_{id_}"
        cmd = [sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
               "--cor-caixa", CORES[list(REELS).index(id_) % 3], "--gancho", gancho, "--seg-gancho", "4.2",
               "--alinhar", "--vad", "--tirar-hesitacoes", "--respiro", "0.22", "--proteger-palavra", "0.40",
               "--manter-perguntas", "--crop-fixo", "--dinamico", "--broll-com-legenda", "--nome", nome, "--saida", SAIDA]
        cmd += EXTRA.get(id_, [])
        for arq_b, arq, tb in brolls:
            cmd += ["--broll", f"{os.path.join(BROLL, arq_b + '.mp4')}@fonte:{LT.no_intermediario(mapa, arq, tb):.2f}"]
        LT.rodar_editor(cmd, nome)
        saida = os.path.join(SAIDA, nome + ".mp4")
        if os.path.exists(saida) and not any(p[0] in LT.AUDIO for p in pedacos):
            vento.limpar(saida)                             # só sem trilha tratada; com o Adobe o vento já saiu


if __name__ == "__main__":
    main()
