"""rumo.eua · entrevistas longas (nov/2026): João Paulo no carro e na rua (Miami) e Marinna no condomínio (Orlando).
Brutos horizontais 4K (João em HDR do iPhone). Cada Reel junta pedaços pela transcrição literal (montagem do lote_ti.py)
num intermediário horizontal 4K SDR, e o editor recorta em pé seguindo o rosto, com a legenda clean do rumo.eua.

Regras do perfil: o Lucas ainda não mora nos EUA; nada no texto pode dizer que ele mora. CTA "Siga @rumo.eua" no fim (pedido do Lucas, nov/2026).
Gancho: pergunta curta, *palavra* com seleção do iPhone em amarelo, bandeira 🇺🇸/🇧🇷 sempre (o editor põe sozinho; vídeo da Mari leva 🇺🇸 mesmo sem falar EUA), nunca responde. CTA "Siga @rumo.eua" numa tela preta DEPOIS do vídeo (tela_final.py), nunca durante.

Uso: python3 projetos/rumoeua_entrevistas/lote_rumo.py [id ...] [--so-montar]
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "imigrar_ti_ads"))
import lote_ti as LT

LT.BRUTOS = "/Volumes/Lucas HD2/Rumo EUA/Entrevistas cortar/Videos Longos"   # movido pro HD em 09/11
LT.W, LT.H = 3840, 2160                                  # horizontal: o recorte em pé é do editor (segue o rosto)
SAIDA = "/Users/lucastoledo/Desktop/Editor Reels/rumoeua_entrevistas/_em_revisao"
CARRO, RUA, MARI = "Joao Paulo no Carro.MOV", "Joao Paulo na Rua.MOV", "Entrevista Marinna Condominio.MOV"

# grafia da legenda (a transcrição literal de cada pedaço erra: "Santitária", "mais frases", "efênero")
LT.FRASES += [("Santitária", "Sanitária"), ("É, se, cara Ele pegou", "Esse cara, ele pegou"), ("quatorze", "14"),
              ("Você tem um prazo E, vinte dias", "Você tem um prazo de 20 dias"), ("vinte dias", "20 dias"),
              ("mais frases,", "mais prazo,"), ("mais frases.", "mais prazo."), ("um, um, um pênalti,", "um penalty,"),
              ("pênalti,", "penalty,"), ("quanta é a multa.", "quanto é a multa."), ("e fez Nós", "e fez: nós"), ("E aí, o caramba,", "E aí eu, caramba,"),
              ("Brasil é muito mais fácil", "No Brasil é muito mais fácil"), ("efênero,", "efêmero,"),
              ("dinheiro Não compra essa paz.", "dinheiro compra essa paz."),
              ("dinheiro que os Estados Unidos.", "dinheiro do que nos Estados Unidos."), ("By the Book.", "by the book."),
              # carro (a troca casa palavra por palavra, com a pontuação do jeito que sai do Whisper)
              ("a Brekel,", "Brickell,"), ("downtown Miami.", "Downtown Miami."), ("Metro Mover,", "Metromover,"),
              ("downtown, midtown", "Downtown, Midtown"), ("organogramo", "organograma"), ("dez anos.", "10 anos."),
              ("seria Comprar", "seria comprar"), ("Com o restaurante é com o cliente.", "com restaurante é como cliente."),
              ("deles, eu sugeri", "deles, ele sugeriu"),
              ("com o Ivo e contando, ele já foi um pau,", "comigo e me contando,"),
              ("Sendo que as coisas, que aqui", "Não tô dizendo que aqui"), ("aqui você, o está trabalha", "aqui o Estado trabalha"),
              ("mudar, pelos", "mudar pros"), ("d 'água.", "d'água."), ("sozinha numa,", "sozinho numa,"), ("to fazendo?", "tô fazendo?"),
              # rua ("ligar pra" é um pedaço de 0,3s: o Whisper sozinho inventa "E aí, galera, vamos lá.")
              ("atenção E aí, galera, vamos lá. Marcar", "atenção: ligar pra marcar"), ("visitá -lo.", "visitá-lo."),
              ("proteger -los", "protegê-los"), ("cento e cinquenta mil dólares.", "150 mil dólares."),
              ("network As", "network. As"), ("aquela, aquela Primeiro", "aquela, aquela… Primeiro"),
              ("Brasil Eu também", "Brasil, eu também"), ("isso. É, da rede de apoio.", "isso da rede de apoio."),
              ("seu censo", "seu senso"), ("Censo de", "Senso de"), ("É há 14", "Há 14"),
              # Marinna
              ("precisa de isso.", "precisa disso."), ("meu marido eu ficar", "meu marido ia ficar"),
              ("ia ser não, não é", "ia ser não. Não é"), ("chegou, é não seria", "chegou, ela não seria"),
              ("celular tá visto,", "celular tá à vista,"), ("bolsa tá vista,", "bolsa tá à vista,"), ("eu saí.", "eu saio."),
              ("cabe todos nós,", "cabe a todos nós,"), ("ter um arvorezinho", "tem uma arvorezinha"),
              ("bolsa de tudo", "bolsa de estudos"), ("construído. com", "construído. Com"),
              # 2ª leva
              ("trapalistas,", "trabalhistas,"), ("ao chul", "ao sul"), ("os eles,", "os L's,")]

# id: (gancho, [(arquivo, início, fim[, "exato"])], opções do recorte)
REELS = {
    # "esse cara, ele pegou catorze, | ele pegou catorze itens": fica o 2º; "que você, você tenha, | você tenha um prazo
    # de, | de vinte dias": fica "que | você tenha um prazo | de vinte dias" (cortes na transcrição literal)
    # fiscal da vigilância sanitária que não multa; tira a interrupção ("tô atrapalhando as pessoas") e o "Eu estava
    # pronto pra receber uma multa" repetido
    "r06_fiscal": ("Isso *dificilmente* aconteceria no Brasil", [
        (RUA, 374.10, 384.75), (RUA, 391.68, 392.44, "exato"), (RUA, 395.30, 401.05, "exato"),
        (RUA, 408.40, 411.30), (RUA, 414.25, 417.95, "exato"),
        (RUA, 423.44, 425.24, "exato"), (RUA, 425.78, 430.05, "exato"), (RUA, 430.50, 432.95), (RUA, 447.25, 451.90), (RUA, 453.30, 459.40),
        (RUA, 460.15, 465.95), (RUA, 466.55, 484.60), (RUA, 491.15, 503.90)], {}),
    # "porque o seu dinheiro compra | olha aí | o seu dinheiro compra a, | ele compra essa paz": fica
    # "porque o seu dinheiro | compra essa paz"
    "r11_dinheiro_paz": ("O que o dinheiro compra nos EUA e *não compra* no Brasil", [
        (RUA, 1141.90, 1151.30, "exato"), (RUA, 1152.80, 1154.55, "exato"), (RUA, 1158.65, 1173.60, "exato"),
        (RUA, 1179.42, 1185.90, "exato")], {}),
    "r16_disney_quintal": ("O que os filhos dela vão ter nos EUA que ela *não teve*?", [
        (MARI, 985.97, 1017.80, "exato"), (MARI, 1018.95, 1055.40)], {"pessoa": "esquerda"}),
    # --- carro
    "r01_metromover": ("*De graça* nos EUA, seria um absurdo no Brasil", [
        (CARRO, 13.28, 37.65), (CARRO, 38.96, 49.0)], {}),
    # tira a 2ª menção a "500 funcionários" (123,9-135,8), o "Eu fazer, eu," antes de "eu comprar" e o "Eu nunca tive...
    # minha única experiência como restaurante," (fica "minha única experiência | com restaurante, é como cliente")
    "r02_restaurante_visto": ("O caminho *inesperado* dele pro Green Card nos EUA", [
        (CARRO, 84.50, 101.12), (CARRO, 103.50, 123.83, "exato"), (CARRO, 136.43, 140.85, "exato"),
        (CARRO, 142.04, 143.00, "exato"), (CARRO, 144.20, 171.29)], {}),
    "r03_governador": ("Já imaginou um governador no Brasil perguntar isso *pra você*?", [
        (CARRO, 620.99, 645.63), (CARRO, 646.63, 657.01), (CARRO, 659.89, 678.83)], {}),
    "r04_sequestro": ("Por que ele *trocou o Brasil* pelos EUA?", [   # 08/11: o antigo ("A violência...") entregava a resposta
        (CARRO, 754.72, 761.26), (CARRO, 763.20, 781.59), (CARRO, 789.50, 791.20), (CARRO, 791.88, 847.03)], {}),
    # versão B (ideia do Lucas, 08/11): abre no "aprendi a andar armado / dois motoqueiros", volta pro motivo (sequestro,
    # gota d'água) e fecha nos 2 anos pra desarmar. Sem o "você tá sempre, você tá sempre" e sem o "leva uns 2 anos" repetido
    "r04b_sequestro": ("Por que ele *trocou o Brasil* pelos EUA?", [
        (CARRO, 798.40, 814.10), (CARRO, 821.10, 822.65),
        (CARRO, 754.72, 761.26), (CARRO, 763.20, 781.59), (CARRO, 789.50, 791.20),
        (CARRO, 794.75, 797.25), (CARRO, 823.90, 827.98), (CARRO, 829.10, 842.06)], {}),
    # --- rua
    # "É, ligar pra marcar com... marcar pra ir visitar": fica "ligar pra | marcar pra ir visitar"
    "r05_choque_cultural": ("O choque cultural nos EUA que *ninguém espera*", [
        (RUA, 296.85, 309.84), (RUA, 321.90, 324.40), (RUA, 329.10, 329.43, "exato"), (RUA, 330.81, 348.57)], {}),
    # "Eu não posso dizer que eu comecei do zero aqui. | Eu não comecei do zero aqui.": fica só a 1ª
    "r07_custo_recomeco": ("Quanto ele *gastou* pra recomeçar nos EUA", [
        (RUA, 738.53, 743.30), (RUA, 745.04, 765.0)], {}),
    "r08_networking": ("O jeito brasileiro de fazer networking *não funciona* nos EUA", [
        (RUA, 797.67, 802.35, "exato"), (RUA, 804.19, 837.37)], {}),     # sem o "É, eu..." no meio
    # "eu também teria preocupação sobre... | eu também teria preocupação sobre a segurança deles": fica o 2º
    "r09_porta_destrancada": ("A preocupação que ele *não tem mais* desde que saiu do Brasil", [
        (RUA, 923.31, 925.65), (RUA, 929.15, 945.75), (RUA, 946.53, 949.19, "exato"), (RUA, 954.09, 970.53)], {}),
    "r10_rede_apoio": ("O que ninguém fala antes de *sair do Brasil*", [
        (RUA, 1072.10, 1101.38)], {}),
    "r12_recado_2012": ("O conselho que ele daria pra si *14 anos atrás* nos EUA", [
        (RUA, 1268.81, 1297.17)], {}),
    # --- Marinna
    "r13_achar_trilha": ("O mais difícil de ir pros EUA *não foi o inglês*, foi…", [
        (MARI, 182.16, 202.88), (MARI, 203.18, 215.79), (MARI, 216.39, 223.88), (MARI, 237.79, 247.24), (MARI, 280.89, 298.50)], {"pessoa": "esquerda"}),
    "r14_ser_mae": ("Ela *não queria ter filhos* no Brasil 🇺🇸", [
        (MARI, 322.93, 352.52), (MARI, 352.94, 359.27), (MARI, 362.57, 368.77), (MARI, 390.74, 396.62)], {"pessoa": "esquerda"}),
    "r15_gemeos": ("Como é ser *mãe de gêmeos* nos EUA?", [
        (MARI, 573.21, 616.03), (MARI, 659.00, 676.69)], {"pessoa": "esquerda"}),
    "r17_nada_cai_do_ceu": ("Onde a maioria *se perde* nos EUA", [
        (MARI, 1151.35, 1189.43)], {"pessoa": "esquerda"}),
    "r18_criar_filhos": ("Vale a pena *criar filhos* nos EUA?", [
        (MARI, 1204.75, 1228.01)], {"pessoa": "esquerda"}),
    # --- 2ª leva (ganchos aprovados pelo Lucas em 07/11/2026): João empreendedor, Marinna família
    "r19_500_funcionarios": ("Ele tinha 500 funcionários no Brasil e *largou tudo* pros EUA", [
        (CARRO, 390.40, 404.85), (CARRO, 406.95, 425.55, "exato")], {}),     # sem "A gente tinha, a gente tinha,"
    # tira a 2ª explicação da renovação (270-279, repete); a ressalva "não sei se ainda está assim" fica
    "r20_visto_negado": ("O visto dele foi *negado*, e foi assim que saiu o Green Card", [
        (CARRO, 254.60, 270.05), (CARRO, 280.10, 283.50), (CARRO, 284.15, 295.90), (CARRO, 296.35, 318.40),
        (CARRO, 319.35, 332.15)], {}),
    # sem o tropeço "eles estão cada vez mais difíceis... Tá ruim aqui o Senado, né?"
    "r21_imigrantes": ("Os EUA *não fecham a porta* pra quem faz certo", [
        (RUA, 857.15, 888.20), (RUA, 898.95, 915.10)], {}),
    "r22_rio_que_deu_certo": ("Miami é o *Rio de Janeiro que deu certo*", [
        (RUA, 271.10, 284.25), (RUA, 1022.40, 1039.20)], {}),
    "r23_saudade": ("O que ele *sente falta* do Brasil depois de 14 anos nos EUA", [
        (RUA, 978.25, 1011.20)], {}),
    # sem o "dois lados bons / dois lados diferentes" (527-539, repete)
    "r24_rede_apoio_mae": ("Criar filho longe da família tem um lado que *ninguém mostra* 🇺🇸", [
        (MARI, 476.50, 527.30), (MARI, 538.95, 560.05)], {"pessoa": "esquerda"}),
    # sem o trecho da alimentação (754-777)
    "r25_curriculo": ("Nos EUA você *escolhe o currículo* do seu filho", [
        (MARI, 727.95, 754.00), (MARI, 777.45, 808.95)], {"pessoa": "esquerda"}),
    # sem a pergunta do Lucas (931-942) e a repetição "seja aprendendo..." (965-971)
    "r26_escola_futuro": ("Escola pública, privada ou em casa: *nenhuma limita* meus filhos 🇺🇸", [
        (MARI, 910.45, 930.65), (MARI, 942.65, 959.90), (MARI, 971.25, 985.00)], {"pessoa": "esquerda"}),
    "r27_mae_brasileira": ("O que a mãe brasileira precisa saber *antes de ir* pros EUA", [
        (MARI, 1104.95, 1150.90)], {"pessoa": "esquerda"}),
    "r28_trabalhou_de_tudo": ("Ela trabalhou de *tudo* nos EUA, menos restaurante", [
        (MARI, 111.20, 158.50)], {"pessoa": "esquerda"}),
}

# repetição de estilo, conferida: "by the book. Faça as coisas by the book" (r06), "isso é pra eles. Isso é pra
# qualquer pessoa" (r16)
# gaguejada colada ("mas, mas", "duas, duas", "abre abre", "eu tento, eu tento") o editor tira sozinho
# (--tirar-hesitacoes); "passo a passo", "o que a gente pensa, o que a gente quer" e "a segurança deles" são estilo
PERMITIR = {"r04b_sequestro", "r06_fiscal", "r16_disney_quintal", "r02_restaurante_visto", "r04_sequestro", "r05_choque_cultural",
            "r07_custo_recomeco", "r08_networking", "r09_porta_destrancada", "r13_achar_trilha", "r14_ser_mae",
            # 2ª leva, conferida: "um ano, um ano" / "uma, uma, uma" / "Isso, isso" / "ele, ele" / "a, a, a" (gaguejada que o
            # editor tira); "Miami, Miami é", "o Brasil é caloroso, o Brasil é", "e não dá. Não dá.", "as férias, porque as
            # férias", "numa escola pública, numa escola privada", "é só pra trabalhar, é só pra isso", "as melhores
            # interações, as melhores atividades", "o que deu pra fazer, como deu pra fazer" (estilo)
            "r19_500_funcionarios", "r20_visto_negado", "r22_rio_que_deu_certo", "r23_saudade", "r24_rede_apoio_mae", "r25_curriculo",
            "r26_escola_futuro", "r27_mae_brasileira", "r28_trabalhou_de_tudo"}


IMIGRAR = os.environ.get("LOTE_MARCA") == "imigrar"
SAIDA_IMIGRAR = "/Volumes/Untitled/Imigrar_cortes/_base"
CORES_IMIGRAR = ["branco", "azul", "rosa"]
sys.path.insert(0, AQUI)
from ganchos_imigrar import GANCHOS as GANCHOS_IMIGRAR  # noqa: E402


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(REELS)
    for id_ in ids:
        gancho, pedacos, op = REELS[id_]
        print(f"\n=== {id_}", flush=True)
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:
            print("  PULADO:", e, flush=True); continue
        if "--so-montar" in sys.argv:
            continue
        if IMIGRAR:
            # versão Imigrar (Lucas, 09/11): mesma montagem e câmera, legenda e balão da Imigrar (caixa alta, cor alternando
            # branco/azul/rosa), gancho novo e 2 saídas: CTA do YouTube e CTA do Instagram
            gancho = GANCHOS_IMIGRAR[id_]
            nome, saida_dir = f"imigrar_{id_}", SAIDA_IMIGRAR
            marca = ["--marca", "imigrar", "--cor-caixa", CORES_IMIGRAR[list(REELS).index(id_) % 3]]
        else:
            nome, saida_dir, marca = f"rumo_{id_}", SAIDA, ["--marca", "rumoeua"]
        cmd = [sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, *marca,
               "--gancho", gancho, "--seg-gancho", "4.2", "--alinhar", "--vad", "--tirar-hesitacoes",
               "--respiro", "0.22", "--proteger-palavra", "0.40", "--manter-perguntas", "--crop-fixo",
               "--nome", nome, "--saida", saida_dir]
        if op.get("pessoa"):
            cmd += ["--pessoa", op["pessoa"]]
        cmd += op.get("extra", [])                 # ex.: câmera parada no tripé pede punch-in mais visível
        LT.rodar_editor(cmd, nome)
        final = os.path.join(saida_dir, f"{nome}.mp4")
        if not os.path.exists(final):
            continue
        if IMIGRAR:                            # base sem CTA; o CTA animado (YouTube e Instagram) entra no cta_imigrar.py
            continue
        else:                                  # tela preta "Siga @rumo.eua" com whoosh + sino, depois do vídeo
            subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tela_final.py"), final], check=True)


if __name__ == "__main__":
    main()
