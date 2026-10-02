"""Ad 2 (LIV, EB-2 NIW, vertical 31,5 s) no formato ads dinâmico.
Versão A: "Green card" gigante atrás da pessoa no gancho; versão B: tela dividida no gancho.

    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py --versao A
    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py --versao B

Tipografia: só Darker Grotesque (marca), ênfase pelo peso (Black x Light), tracking apertado, sem sombra.
Legenda: padrão minimalista da LIV (palavra falada em laranja) nas cenas dela; lettering grande nos inserts.
Imagens externas sempre aspiracionais (sonho americano). B-roll: Pexels pelo servidor do time.
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "..", "editor"))
import plataforma as P
BR = os.path.join(P.pasta_cache("broll"), "pexels_{}.mp4")
TR = os.path.join(AQUI, "..", "..", "assets", "transicoes", "FILM BURNS {}.mp4")


def sp(texto, t, **k):
    return dict({"texto": texto, "t": t}, **k)


def L(texto, t, tam, peso, cor="bege"):
    return {"texto": texto, "t": t, "tam": tam, "peso": peso, "cor": cor}


ROTEIRO = {
    "nome": "ad2_eb2niw", "saida": "~/Desktop/ADS_LIV",
    "video": "~/Downloads/ad2 vertical.mp4", "palavras": os.path.join(AQUI, "ad2_palavras.json"),
    "trocas": {"EB2NW": "EB-2 NIW", "pedição": "petição"},
    "zoom": [dict(t0=0, t1=3.34, s=1.0, avanco=0.05), dict(t0=3.34, t1=6.28, s=1.22), dict(t0=7.8, t1=9.3, s=1.0),
             dict(t0=11.66, t1=14.18, s=1.10), dict(t0=14.18, t1=18.62, s=1.0), dict(t0=19.9, t1=21.92, s=1.2),
             dict(t0=21.92, t1=24.4, s=1.06), dict(t0=25.7, t1=27.62, s=1.18), dict(t0=27.62, t1=32, s=1.0, avanco=0.03)],
    # texto entre o fundo e a pessoa
    "atras": [
        {"t0": 0.0, "t1": 3.34, "so_A": True, "legenda": True, "linhas": [
            {"y": 335, "tam": 236, "peso": 900, "cor": "laranja", "track": -0.035,
             "spans": [sp("Green", 0.25), sp("card", 0.45)]}]},
    ],
    # lettering grande nos inserts de imagem (ênfase pelo peso)
    "lettering": [
        {"t0": 6.28, "t1": 7.80, "linhas": [L("Não é só", 6.3, 110, 400), L("formulário.", 6.8, 170, 900)]},
        {"t0": 9.30, "t1": 10.85, "linhas": [L("Estratégia", 9.3, 170, 900), L("jurídica", 9.86, 130, 400)]},
        {"t0": 10.85, "t1": 11.66, "linhas": [L("Prova de", 10.9, 120, 400), L("impacto.", 11.2, 190, 900)]},
        {"t0": 18.62, "t1": 19.90, "linhas": [L("Aqui nos", 18.62, 110, 400), L("Estados Unidos", 18.92, 150, 900)]},
        {"t0": 24.40, "t1": 25.70, "linhas": [L("Um projeto", 24.5, 120, 400), L("de vida.", 25.1, 200, 900)]},
    ],
    "broll": [
        dict(t0=6.28, t1=7.80, arq=BR.format(7247829), ss=1.0),     # "não é só encher formulários"
        dict(t0=9.30, t1=11.66, arq=BR.format(8731320), ss=7.5),    # "estratégia jurídica, prova de impacto"
        dict(t0=18.62, t1=19.90, arq=BR.format(39402632), ss=2.0),  # "aqui nos Estados Unidos": orla de Miami
        dict(t0=24.40, t1=25.70, arq=BR.format(27947592), ss=0.3),  # "projeto de vida": pôr do sol no píer de Santa Monica (EUA)
    ],
    "burns_arquivos": [TR.format(n) for n in (24, 41, 19, 44)],
    "burns": [3.34, 6.28, 9.30, 14.18, 18.62, 24.4],
    "burn_forca": 0.9,
    "cta": {"t0": 27.62, "t_seta": 29.68, "linha1": "Comece pela", "linha2": "análise de perfil",
            "linha3": "sem custo, é só tocar no botão"},
    # versão B: tela dividida no gancho
    "dividido": {"t0": 0.0, "t1": 3.34, "arq": BR.format(35194304), "ss": 0.5, "y_topo": 380, "y_pessoa": 150,
                 "faixa": {"t0": 0.0, "t1": 3.34, "altura": 270, "cor": "bege", "linhas": [
                     {"y": 900, "tam": 70, "peso": 400, "cor": "azul", "track": -0.01,
                      "spans": [sp("Como", 0.15), sp("o", 0.3), sp("seu", 0.45), sp("processo", 1.56), sp("de", 1.8)]},
                     {"y": 1000, "tam": 120, "peso": 900, "track": -0.03,
                      "spans": [sp("green card", 2.02, cor="laranja"), sp("é montado?", 2.42, tam=90, peso=300, cor="azul")]}]}},
}
