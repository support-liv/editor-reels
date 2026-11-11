"""Thiago (Cinnaholic, Wesley Chapel FL), entrevista andando gravada em 4K HDR horizontal (IMG_5772.MOV, 10/11/2026).
Mesmo motor do lote_rumo.py (montagem pela transcrição literal + editor seguindo o rosto). Duas marcas:
  rumo.eua: legenda clean, gancho com *palavra*, tela preta "Siga @rumo.eua" no fim (tela_final.py)
  Imigrar (LOTE_MARCA=imigrar): base em Imigrar_cortes/_base; depois finalizar_imigrar.py "imigrar_t*_thiago*" gera
           YouTube ("Inscreva-se no canal") e Instagram ("Siga @imigrar.eua") com o CTA preto animado.
Linha de corte aprovada: um bloco contínuo na ordem da fala, a pergunta do Lucas só quando a resposta precisa dela.
Fora dos cortes: o depoimento sobre a LIV (5:13-6:00, bom pro canal da LIV) e o valor do EB-5 (900 mil, errado).

Uso: python3 projetos/rumoeua_entrevistas/lote_thiago.py [id ...] [--so-montar]
     LOTE_MARCA=imigrar python3 projetos/rumoeua_entrevistas/lote_thiago.py [id ...]
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lote_rumo as R

LT = R.LT
LT.BRUTOS = "/Users/lucastoledo/Downloads"
LT.W, LT.H = 3840, 2160
# áudio limpo no Adobe Enhance Speech (11/11/2026): trilha inteira ao lado do bruto, sincronia conferida (0 ms)
LT.AUDIO = {"IMG_5772.MOV": "/Users/lucastoledo/Downloads/Entrevista - Thiago Cinaholic/IMG_5772_audio_tratado.wav"}                       # horizontal 4K: o editor recorta em pé seguindo o rosto
R.SAIDA = "/Volumes/Untitled/rumoeua_cortes/thiago_cinnaholic"
E = {"pessoa": "esquerda"}                    # o Thiago anda sempre à esquerda do Lucas: o recorte fecha nele
B = "IMG_5772.MOV"

LT.FRASES += [("Tiago", "Thiago"), ("Tiago,", "Thiago,"), ("E2,", "E-2,"), ("E2.", "E-2."), ("E2", "E-2"),
              ("cidadões", "cidadãos"), ("quanta em média", "quanto em média"), ("Quanta em média", "Quanto em média"),
              ("nessa hit supermercado,", "nessa rede de supermercados,"), ("hit supermercado,", "rede de supermercados,"),
              ("Rede de Supermercados,", "rede de supermercados,"), ("na mercadológica.", "mercadológica."),
              ("pôrmites", "permits"), ("soga,", "açougue,"), ("franquiadora,", "franqueadora,"),
              ("de vento e polpa.", "de vento em popa."), ("vento e polpa.", "vento em popa."),
              ("inspections", "inspeções"), ("a sim vir", "a intenção de vir"), ("ali para iniciar.", "ali para iniciar?"), ("pra iniciar.", "pra iniciar?"),
              ("vamos puxar as unidades,", "vamos pros Estados Unidos."), ("vento e polpa,", "vento em popa,"),
              ("SOG,", "açougue,"), ("100 por cento", "100%"),
              ("tem lá no Brasil", "tem lá no Brasil?"), ("Tchau, galera.", "Thiago,"), ("Tchau, galera,", "Thiago,"),
              ("Estados Unidos? Assim, que é totalmente", "Estados Unidos que é totalmente"),
              ("discrepante. O que a gente", "discrepante do que a gente"), ("pra vinte e sete.", "pra 2027?"), ("pra 27.", "pra 2027?"), ("Thiago, Brasil a gente", "Thiago, no Brasil a gente"), ("problemas ali,", "problemas ali."),
              ("pra vinte e sete?", "pra 2027?"), ("O que que você enxergou", "O que você enxergou"), ("seja migratório", "seja imigratório"), ("pra 27?", "pra 2027?"), ("para 27?", "para 2027?"),
              ("trabalhistas,", "trabalhistas."), ("negócio nos Estados Unidos,", "negócio nos Estados Unidos?"),
              ("por que escolher", "Por que escolher"), ("pra iniciar.", "pra iniciar?"), ("para iniciar.", "para iniciar?")]

# pergunta e resposta em pedaços separados. Lucas (11/11): perguntas dele enxutas, só o essencial e sem respiro:
#   t02 "Essa experiência que você teve no negócio dos seus pais, | as dificuldades que você encontrou ali que
#       fizeram você olhar pros EUA?" (sem "nessa rede de supermercado, foi isso de fato")
#   t05 "O que você enxergou aqui nos EUA | que é totalmente discrepante | o que a gente tem lá no Brasil?" (sem o
#       "que você viu" e o "pensando em negócios")
#   t07 pergunta inteira (pedaço curto dentro dela confundia a transcrição): o editor tira as pausas
#   t08 "Projeção de faturamento pra 2027?" (o "Thiago," isolado tem 0,3s e some na transcrição)
#   t09 "Thiago, no Brasil a gente tem CLT, tem vários problemas ali. | Como funciona isso aqui nos EUA?"   t10 sem o "que pode ser um aprendizado..."   t11 "Por que escolher o ramo...?"
# (gancho rumo.eua, [(arquivo, início, fim[, "exato"])], opções): tempos do bruto, conferidos nas palavras
R.REELS = {
    "t01_thiago_visto": ("Como ele conseguiu *empreender nos EUA*?", [
        (B, 54.36, 111.16)], dict(E)),                         # 4 anos -> pandemia, consulado -> E-2 pela Itália, renova a cada 5
    "t02_thiago_roubar": ("O que fez ele *desistir do Brasil*?", [
        (B, 171.40, 175.20, "exato"), (B, 178.32, 181.92, "exato"), (B, 182.18, 209.96)], dict(E)),                        # pergunta do Lucas (dificuldades no negócio dos pais) + resposta
    "t03_thiago_inseguranca": ("O que *pesou mais* na decisão dele?", [
        (B, 210.32, 241.98)], dict(E)),                        # "o objetivo principal foi a insegurança... não queria ter filho no Rio"
    "t04_thiago_franquia": ("Por que ele *não começou do zero*?", [
        (B, 253.16, 279.52)], dict(E)),                        # "A gente definiu: vamos pros EUA. E agora?" -> franquia, risco menor
    "t05_thiago_brasil_eua": ("A diferença de *empreender no Brasil vs EUA*", [
        (B, 380.02, 382.42, "exato"), (B, 382.94, 384.88, "exato"), (B, 385.26, 386.42, "exato"),
        (B, 388.06, 421.38)], dict(E)),                        # pergunta + crédito, juros, renda fixa no Brasil
    "t06_thiago_burocracia": ("A burocracia *nos EUA* é diferente?", [
        (B, 422.30, 464.90)], dict(E)),                        # burocracia pra tudo andar certo, bombeiro em menos de 1 minuto
    "t07_thiago_quanto_precisa": ("Quanto precisa pra *empreender nos EUA*?", [
        (B, 466.00, 474.90), (B, 476.28, 500.22)], dict(E)),                        # pergunta + 100 mil (o que ele ouve dos advogados), sem o EB-5
    "t08_thiago_faturamento": ("Quanto fatura *uma franquia* nos EUA?", [
        (B, 517.20, 519.36, "exato"), (B, 520.48, 532.52)], dict(E)),                        # projeção 2027: primeiro 1 milhão de dólares no ano
    # "É, isso também é um ponto bem interessante, | que eu não respondi naquela outra pergunta, | mas é muito melhor"
    "t09_thiago_clt": ("Como funciona *contratar* nos EUA?", [
        (B, 554.10, 558.04, "exato"), (B, 564.70, 566.66, "exato"),
        (B, 566.88, 568.64, "exato"), (B, 570.74, 624.50)], dict(E)),
    # sem o "Boa pergunta." entre a pergunta e a resposta
    "t10_thiago_ponto": ("A maior dificuldade dele *pra abrir a loja*", [
        (B, 643.86, 647.56, "exato"), (B, 652.86, 689.78)], dict(E)),
    "t11_thiago_experiencia": ("Precisa de *experiência* pra abrir franquia?", [
        (B, 740.36, 742.38, "exato"), (B, 743.04, 769.28)], dict(E)),                        # termina em "a franquia te dá um suporte muito bom"
}
# repetição de estilo, conferida na transcrição literal: "por mais cinco, por mais cinco", "pra poder empreender, pra
# poder investir" (t01); "funcionário/cliente tentando roubar a gente", "tirar um pouco daqui, tirar um pouco dali" (t02);
# "os juros do Brasil, é... Brasil é pra você não fazer negócio", "que que" do Whisper (t05); "não tem rescisão, não tem
# nada disso", "zero, zero, zero" (t09); "eu passei pelo chão de loja, eu passei pela..." (t11)
R.PERMITIR = {"t01_thiago_visto", "t02_thiago_roubar", "t05_thiago_brasil_eua", "t09_thiago_clt", "t11_thiago_experiencia"}

# versão Imigrar (caixa alta, bandeira só no fim; aprovados pelo Lucas em 10/11/2026)
R.GANCHOS_IMIGRAR.update({
    "t01_thiago_visto": "Como ele conseguiu morar e empreender nos EUA 🇺🇸?",
    "t02_thiago_roubar": "O que fez ele desistir de empreender no Brasil 🇧🇷?",
    "t03_thiago_inseguranca": "O motivo que pesou mais na decisão de sair do Brasil 🇧🇷",
    "t04_thiago_franquia": "Por que ele não abriu um negócio do zero nos EUA 🇺🇸?",
    "t05_thiago_brasil_eua": "A diferença de empreender no Brasil vs EUA 🇺🇸",
    "t06_thiago_burocracia": "A burocracia nos EUA 🇺🇸 é menor?",
    "t07_thiago_quanto_precisa": "Quanto precisa pra empreender nos EUA 🇺🇸?",
    "t08_thiago_faturamento": "Quanto fatura uma franquia de doces nos EUA 🇺🇸?",
    "t09_thiago_clt": "E a CLT nos EUA 🇺🇸?",
    "t10_thiago_ponto": "O erro que custa caro pra quem abre negócio nos EUA 🇺🇸",
    "t11_thiago_experiencia": "Precisa ter experiência pra abrir uma franquia nos EUA 🇺🇸?",
})

# B-roll da loja (Downloads/Entrevista - Thiago Cinaholic, recortado em pé e em SDR no cache): tempo da fala no
# intermediário de cada corte; a legenda continua por cima
BROLL = os.path.expanduser("~/Library/Caches/editor-reels/broll_thiago")
for id_, clipe, t in [("t04_thiago_franquia", "IMG_5773", 14.82),        # "porque você investindo numa franquia": interior
                      ("t08_thiago_faturamento", "IMG_5774", 8.61),      # "com a segunda loja agora": fachada com o Thiago
                      ("t11_thiago_experiencia", "IMG_5773", 15.63)]:    # "e hoje eu tenho uma padaria aqui": interior
    R.REELS[id_][2]["extra"] = ["--broll", f"{BROLL}/{clipe}_vertical.mp4@fonte:{t}", "--broll-com-legenda"]

# Na pergunta do Lucas o recorte continua no Thiago (ouvindo): o vertical não cabe os dois lado a lado (o plano aberto
# cortava os dois) e fechar no Lucas, mais perto da câmera, deixava o rosto grande e cortado no topo (teste de 10/11).

if __name__ == "__main__":
    R.main()
