"""Ad 12 (LIV, médicos / EB-2 NIW, vertical 19 s) no formato ads dinâmico.

    python3 editor/ads_dinamico.py projetos/ads_liv/ad12.py --versao A    # "Médico?" atrás dela no gancho
    python3 editor/ads_dinamico.py projetos/ads_liv/ad12.py --versao B    # tela dividida no gancho

Inserts: médicos com postura de autoridade (Pexels, conferidos quadro a quadro: formal, profissional), sonho americano (Miami), estoque interno da LIV
(Dra. Lívia revisando processo em "baseado em mérito").
"""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..")
BR = "~/Library/Caches/editor-reels/broll/pexels_{}.mp4"
EST = os.path.join(RAIZ, "assets", "estoque_liv", "{}")
TR = os.path.join(RAIZ, "assets", "transicoes", "FILM BURNS {}.mp4")


def sp(texto, t, **k):
    return dict({"texto": texto, "t": t}, **k)


def L(texto, t, tam, peso, cor="bege"):
    return {"texto": texto, "t": t, "tam": tam, "peso": peso, "cor": cor}


ROTEIRO = {
    "nome": "ad12_medicos", "saida": "~/Desktop/ADS_LIV",
    "video": "~/Downloads/ad12 - prof medico - vertical.mp4", "palavras": os.path.join(AQUI, "ad12_palavras.json"),
    "trocas": {"EB2NW": "EB-2 NIW"},
    "zoom": [dict(t0=0, t1=2.95, s=1.0, avanco=0.05), dict(t0=4.4, t1=6.44, s=1.2), dict(t0=8.84, t1=10.3, s=1.0),
             dict(t0=11.6, t1=12.3, s=1.15), dict(t0=13.75, t1=20, s=1.0, avanco=0.03)],
    "atras": [
        {"t0": 0.0, "t1": 1.48, "so_A": True, "legenda": True, "linhas": [
            {"y": 335, "tam": 290, "peso": 900, "cor": "laranja", "track": -0.035, "spans": [sp("Médico?", 0.2)]}]},
    ],
    "lettering": [
        {"t0": 2.95, "t1": 4.40, "linhas": [L("5 anos", 3.0, 190, 900), L("de experiência", 3.5, 110, 400)]},
        {"t0": 6.44, "t1": 8.84, "linhas": [L("Viver nos", 6.44, 110, 400), L("Estados Unidos.", 7.38, 150, 900)]},
        {"t0": 10.30, "t1": 11.60, "linhas": [L("Baseado em", 10.4, 110, 400), L("mérito.", 11.1, 200, 900)]},
        {"t0": 12.30, "t1": 13.75, "linhas": [L("Sem vínculo", 12.32, 150, 900), L("com empregador", 12.85, 110, 400)]},
    ],
    "broll": [
        dict(t0=2.95, t1=4.40, arq=BR.format(4769286), ss=2.0),      # "5 anos de experiência": centro cirúrgico
        dict(t0=6.44, t1=8.84, arq=BR.format(39402632), ss=1.0),     # "viver aqui nos EUA": orla de Miami
        dict(t0=10.30, t1=11.60, arq=EST.format(                     # "baseado em mérito": Dra. Lívia (estoque LIV)
            "vertical__dra-livia__revisando-processo-formal__mesa-dela__terno-risca-de-giz__por-cima-do-ombro__9s.mp4"), ss=2.0),
        dict(t0=12.30, t1=13.75, arq=BR.format(5453692), ss=2.0),     # "sem vínculo com empregador": médico de braços cruzados
    ],
    "burns_arquivos": [TR.format(n) for n in (24, 41, 19, 44)],
    "burns": [2.95, 6.44, 8.84, 10.30, 13.75],
    "burns_B": [1.48, 2.95, 6.44, 8.84, 10.30, 13.75],
    "burn_forca": 0.9,
    "cta": {"t0": 14.0, "t_seta": 17.84, "linha1": "Faça sua", "linha2": "análise de perfil",
            "linha3": "sem custo, toque em Saiba Mais"},
    "dividido": {"t0": 0.0, "t1": 1.48, "arq": BR.format(6130565), "ss": 1.0, "y_topo": 300, "y_pessoa": 120,
                 "faixa": {"t0": 0.0, "t1": 1.48, "altura": 230, "cor": "bege", "linhas": [
                     {"y": 960, "tam": 120, "peso": 900, "track": -0.03,
                      "spans": [sp("Você é", 0.1, tam=96, peso=300, cor="azul"), sp("médico?", 0.5, cor="laranja")]}]}},
}
