"""rumo.eua · entrevistas curtas de rua (nov/2026), brutos em pé 4K do iPhone em ~/Downloads/Entrevistas cortar/<pasta>/.
Mesmo padrão do lote_rumo.py (legenda clean, gancho com bandeira, tela preta "Siga @rumo.eua" no fim), só que o
intermediário já sai em pé. Ganchos aprovados pelo Lucas em 07/11/2026. Paloma (42) e Maria (43) estão seguradas.

Uso: python3 projetos/rumoeua_entrevistas/lote_curtos.py [id ...] [--so-montar]
"""
import lote_rumo as R

LT = R.LT
import os
# o lote_ti acha a transcrição pelo nome do arquivo (editor/transcricoes/IMG_0421.json): os brutos ficam em subpastas,
# então junta tudo numa pasta de atalhos
LT.BRUTOS = os.path.expanduser("~/Library/Caches/editor-reels/rumo_curtos_brutos")
ORIGEM = "/Volumes/Lucas HD2/Rumo EUA/Entrevistas cortar"   # movido pro HD em 09/11
LT.W, LT.H = 2160, 3840                                  # bruto já em pé: o editor só segue o rosto

P41 = "IMG_0423.MOV"
P45 = "IMG_0421.MOV"
LET = "IMG_9478.MOV"
NAT = "IMG_9783.MOV"
ALF = "IMG_9784.MOV"
TRA = "06 - educacao do transito.mov"

LT.FRASES += [("Míterói,", "Niterói,"), ("Míterói", "Niterói"), ("meteo louco", "meter o louco"), ("Dioma", "idioma"),
              ("sínior", "sênior"), ("senior", "sênior"), ("Nanny,", "nanny,"), ("Nanny.", "nanny."), ("Nenny.", "nanny."),
              ("babaca", "babá"), ("Miterói,", "Niterói,"), ("vicho", "visto"), ("escalarando", "escalonando"),
              ("quanta é você estar", "quanto tempo você está"), ("A quanto tempo", "Há quanto tempo"), ("Quanta em média", "Quanto em média"), ("Work work permit", "work permit"), ("Quanto ganha e média", "Quanto ganha em média"),
              ("quanto ganha médio", "quanto ganha em média"), ("Quanto é que você mora", "Quanto tempo você mora")]

# 08/11 (pedido do Lucas): nenhum abre com "qual seu nome". 10/11: SEM trechinho puxado pro início (cold open): em vídeo
# curto quebrava o contexto (c02: o "no Brasil" ia pra frente e o resto parecia falar dos EUA). O gancho fica só no balão;
# os pedaços tocam na ordem em que foram falados (ordenados abaixo).
# 10/11 (Lucas aprovou o c02 da Patrícia como modelo): UM bloco contínuo por corte, na ordem da fala, sem cold open; a
# pergunta do Lucas só entra se a resposta não se sustenta sem ela. Cortes por palavra (tempos do IMG_*.json).
# 10/11: ganchos que entregavam a resposta (c02, c03, c05, c06, c08) trocados pelos de loop aprovados no Imigrar
R.REELS = {
    # Patrícia: a 41 (regravação, ela mais no centro do quadro) tem as falas mais limpas; o c02 é da 45
    "c01_patricia_salario": ("Quanto ganha uma coordenadora de operações *nos EUA*?", [
        (P41, 23.54, 45.20)], {}),                               # tempo + profissão -> quanto ganha -> 65 a 120 mil/ano
    "c02_patricia_empresaria": ("Por que ela desistiu de *empreender no Brasil*?", [
        (P45, 59.50, 87.40)], {}),                               # sem pergunta: "No Brasil eu fui empresária..." até "não tem preço"
    "c03_patricia_seguranca": ("O que ela faz nos EUA que *no Brasil não fazia*", [
        (P41, 124.82, 127.40), (P41, 128.85, 182.94)], {}),      # "O que me surpreendeu, a segurança" (sem o "que é a segurança") + escola e saúde
    "c04_patricia_filha": ("A filha dela teve nos EUA o que *o Brasil não daria*", [
        (P41, 183.38, 200.80)], {}),                             # "você tem filho?" -> veio com 15 -> high school, faculdade, master
    "c12_patricia_ingles": ("Green card *não basta* nos EUA", [
        (P41, 98.52, 124.28)], {}),                              # sem pergunta: "o mais difícil foi a língua"
    "c13_patricia_dica": ("A dica dela pra quem quer *morar nos EUA*", [
        (P41, 201.88, 226.64)], {}),                             # dica -> planejar, visto adequado, advogado licenciado, inglês
    # Letícia: o "qual a melhor coisa de morar aqui" repetia a resposta anterior (Lucas, 10/11): fora
    "c05_leticia_baba": ("Quanto ela ganha *por mês* nos EUA?", [
        (LET, 28.66, 56.38)], {}),                               # "Eu sou nanny, babá" -> quanto ganha -> quanto precisa pra viver bem
    "c10_leticia_brasil_eua": ("O que ela tem nos EUA que *não teria no Brasil*", [
        (LET, 113.90, 135.80)], {}),                             # o que te surpreendeu -> segurança, andar à noite, não trancar a casa
    "c06_nathalia_qi": ("No Brasil é quem você conhece. *E nos EUA?*", [
        (NAT, 30.70, 48.98)], {}),                               # diferenças -> violência, oportunidade sem depender de conhecer alguém
    "c11_nathalia_salario": ("Quanto ganha uma gerente comercial *nos EUA*?", [
        (NAT, 9.80, 17.50), (NAT, 18.15, 27.10)], {}),   # sem o recomeço "quanto ganha um, quanto ganha"; 23 anos, gerente sênior comercial -> 150 a 200 e poucos mil/ano
    "c14_nathalia_dica": ("O erro de quem *vem pros EUA* sem plano", [
        (NAT, 55.20, 80.62)], {}),                               # dica -> não meter o louco como turista; vários vistos
    "c07_alfredo_piso": ("Quanto *lucra por mês* um empresário brasileiro nos EUA?", [
        (ALF, 18.10, 21.85), (ALF, 30.70, 33.30), (ALF, 37.60, 41.00), (ALF, 47.00, 57.54)], {}),   # enxuto, na ordem
    "c08_alfredo_empreender": ("As 2 maiores diferenças entre *Brasil e EUA* pra ele", [
        (ALF, 73.70, 91.85), (ALF, 94.70, 108.10)], {}),         # diferenças -> filha de bicicleta -> empreender (sem o "mais algum ponto?" do Lucas)
    "c15_alfredo_dica": ("O que ninguém conta sobre *o começo nos EUA*", [
        (ALF, 115.20, 144.00)], {}),                             # dica -> planejamento, o começo é difícil, documento, língua
    # o Lucas fala: legenda só com a fala dele, nada dizendo que ele mora lá
    "c09_transito": ("A educação no trânsito nos EUA, *um país que funciona*", [(TRA, 0.0, 24.0)], {}),
}
for _id, (_g, _p, _op) in R.REELS.items():          # ordem natural da fala (sem cold open)
    _p.sort(key=lambda x: (x[0], x[1]))
# câmera parada no tripé (diferente do João no carro e da Mari andando): punch-in alternado a cada corte de fala,
# bem visível (0,72 = plano fechado com 72% do aberto), pra a cena não ficar estática. O trânsito é na mão: fica o padrão

# Enquadramento (Lucas, 08/11): pergunta do Lucas = plano aberto com os dois; entrevistado falando = só nele, alternando
# plano médio (--aperto 0,60 da largura) e perto do rosto (--punch 0,70 disso). Ponto fixo no rosto do entrevistado
# (medido no bruto já endireitado): o detector perdia a Patrícia de perfil/óculos e fechava no Lucas.
# y = altura do ROSTO no bruto: o editor põe esse ponto a 38% do topo do recorte. Pôr abaixo do rosto (como estava)
# subia a cara e cortava a cabeça no fechado (Alfredo, 10/11) — e o topo do Reels/Shorts ainda cobre uns 12%
ROSTO = {P45: "0.10,0.33", P41: "0.31,0.38", LET: "0.31,0.33", NAT: "0.31,0.37", ALF: "0.21,0.33"}
# Patrícia na 45 está colada na borda esquerda: com 0,60 entrava o Lucas e o espaço atrás dele (Lucas, 10/11).
# 0,32 pegava só ela mas cortava a cabeça no fechado; 0,40 + fechado leve (0,85) dá respiro em cima (Lucas, 10/11)
APERTO = {P45: "0.40", P41: "0.50", LET: "0.50", NAT: "0.50", ALF: "0.45"}   # só o entrevistado (o Alfredo tem o Lucas perto)
PUNCH = {P45: "0.85", P41: "0.85", LET: "0.85", NAT: "0.85", ALF: "0.85"}
for _id, (_g, _p, _op) in R.REELS.items():
    if _id != "c09_transito":
        _op["extra"] = ["--dinamico", "--perguntas-auto", "--pessoa", "esquerda", "--centro", ROSTO[_p[0][0]], "--aperto", APERTO.get(_p[0][0], "0.60"), "--punch", PUNCH.get(_p[0][0], "0.70")]
R.REELS["c09_transito"][2]["extra"] = ["--sem-legenda"]   # pedido do Lucas: só a fala dele e o balão do gancho no início
# conferido na transcrição literal: os recomeços de verdade foram cortados acima ("da pessoa, da pessoa", "é uma, é uma",
# "o que que", "quanto ganha um, quanto ganha", "porque a gente tem...", "cada equipe pode te... cada equipe",
# "é mais, eu... acho"); o resto é estilo ou gaguejada colada que o editor tira: "a carga tributária... a carga de
# impostos, a carga trabalhista", "muito mais simples, muito mais fácil", "a saúde. A saúde é", "Não, não.",
# "cinco, cinco, seis mil", "dez, dez mil", "Natália. Natália,", "Alfredo. Alfredo,", "eu acho que, eu acho que",
# pergunta "nos Estados Unidos?" repetida em pedaços diferentes
R.PERMITIR = set(R.REELS) - {"c09_transito"}

# câmera torta no tripé (Lucas, 08/11): gira o bruto antes de cortar, com zoom só o bastante pra não aparecer canto preto.
# Graus medidos pela mediana das verticais da cena (positivo = horário no ffmpeg). Nathália e Alfredo (Epcot) estão retos
ROTACAO = {P45: 3.0, P41: 3.4, LET: -1.5}


def girar_bruto(orig, dest, graus):
    import math, subprocess
    a = math.radians(abs(graus))
    zoom = math.cos(a) + (LT.H / LT.W) * math.sin(a)            # em pé: cobre o quadro inteiro depois de girar
    tmp = dest + ".tmp.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", orig, "-vf",
                    f"rotate={math.radians(graus):.5f},scale=iw*{zoom:.4f}:-2,crop={LT.W}:{LT.H}",
                    "-c:v", "hevc_videotoolbox", "-b:v", "45M", "-tag:v", "hvc1", "-c:a", "copy", tmp], check=True)
    os.replace(tmp, dest)
    open(dest + ".graus", "w").write(str(graus))


def atalhos():
    os.makedirs(LT.BRUTOS, exist_ok=True)
    for raiz, _, arqs in os.walk(ORIGEM):
        for a in arqs:
            if a not in (P41, P45, LET, NAT, ALF, TRA):
                continue
            dest, orig = os.path.join(LT.BRUTOS, a), os.path.join(raiz, a)
            g = ROTACAO.get(a)
            feito = open(dest + ".graus").read() if os.path.exists(dest + ".graus") else None
            if g and feito != str(g):
                if os.path.islink(dest):
                    os.remove(dest)
                print(f"  girando {a} {g:+}°")
                girar_bruto(orig, dest, g)
            elif not g and not os.path.exists(dest):           # atalho quebrado (bruto mudou de pasta): refaz
                if os.path.lexists(dest):
                    os.remove(dest)
                os.symlink(orig, dest)


if __name__ == "__main__":
    atalhos()
    R.main()
