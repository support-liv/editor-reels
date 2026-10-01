"""Ad 2 (LIV, EB-2 NIW, vertical 31,5 s) no formato ads dinâmico. Versão A: texto atrás da pessoa no gancho;
versão B: tela dividida no gancho (Estátua da Liberdade em cima, ela embaixo).

    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py --versao A
    python3 editor/ads_dinamico.py projetos/ads_liv/ad2.py --versao B

Palavras: Whisper local (scratchpad/ad2/palavras.json → copiado pra projetos/ads_liv/ad2_palavras.json).
B-roll: Pexels pelo servidor do time (cache ~/Library/Caches/editor-reels/broll). Film burns: assets/transicoes/.
"""
import os
AQUI = os.path.dirname(os.path.abspath(__file__))
BR = "~/Library/Caches/editor-reels/broll/pexels_{}.mp4"
TR = os.path.join(AQUI, "..", "..", "assets", "transicoes", "FILM BURNS {}.mp4")


def sp(texto, t, tam=None, cor=None):
    d = {"texto": texto, "t": t}
    if tam: d["tam"] = tam
    if cor: d["cor"] = cor
    return d


ROTEIRO = {
    "nome": "ad2_eb2niw", "saida": "~/Desktop/ADS_LIV",
    "video": "~/Downloads/ad2 vertical.mp4", "palavras": os.path.join(AQUI, "ad2_palavras.json"),
    "trocas": {"EB2NW": "EB-2 NIW", "pedição": "petição"},
    "destaques": ["green", "card", "aprovado", "formulários", "eb2", "niw", "estratégia", "jurídica", "impacto",
                  "narrativa", "liv", "licenciado", "perfil", "projeto", "vida", "análise", "custos", "botão"],
    # enquadramento: punch-in por frase (s = zoom), com leve avanço de câmera dentro de cada trecho
    "zoom": [dict(t0=0, t1=3.34, s=1.0, avanco=0.05), dict(t0=3.34, t1=6.28, s=1.22), dict(t0=7.8, t1=9.3, s=1.0),
             dict(t0=11.66, t1=14.18, s=1.10), dict(t0=14.18, t1=18.62, s=1.0), dict(t0=18.62, t1=21.92, s=1.2),
             dict(t0=21.92, t1=24.5, s=1.06), dict(t0=25.7, t1=27.62, s=1.18), dict(t0=27.62, t1=32, s=1.0, avanco=0.03)],
    # gancho A: texto entre o fundo e a pessoa (palavra por palavra no tempo da fala)
    "atras": [
        {"t0": 0.0, "t1": 3.34, "so_A": True, "linhas": [
            {"y": 190, "tam": 70, "cor": "azul", "spans": [sp("COMO", 0.15), sp("O", 0.3), sp("SEU", 0.45), sp("PROCESSO", 1.56), sp("DE", 1.8)]},
            {"y": 390, "tam": 345, "cor": "laranja", "spans": [sp("GREEN", 2.02)]}]},
        {"t0": 12.1, "t1": 14.18, "legenda": True, "linhas": [
            {"y": 360, "tam": 250, "cor": "laranja", "spans": [sp("NARRATIVA", 12.2)]}]},
    ],
    "frente": [
        {"t0": 2.28, "t1": 3.34, "so_A": True, "linhas": [
            {"y": 1000, "tam": 300, "cor": "laranja", "spans": [sp("CARD", 2.28)]},
            {"y": 1250, "tam": 96, "caixa": "azul", "spans": [sp("É MONTADO?", 2.42)]}]},
    ],
    "broll": [
        dict(t0=6.28, t1=7.80, arq=BR.format(7247829), ss=1.0),     # "não é só encher formulários"
        dict(t0=9.30, t1=11.66, arq=BR.format(8731320), ss=7.5),    # "estratégia jurídica, prova de impacto"
        dict(t0=24.5, t1=25.7, arq=BR.format(7646536), ss=0.3),     # "é um projeto de vida"
    ],
    "burns_arquivos": [TR.format(n) for n in (24, 41, 19, 44)],
    "burns": [3.34, 6.28, 9.30, 14.18, 24.5],
    "burn_forca": 0.9,
    "y_legenda": 1330,
    "cta": {"t0": 27.62, "t_seta": 29.68, "y": 1400, "linha1": "Análise de perfil", "linha2": "sem custo", "tam2": 84},
    # versão B: tela dividida no gancho
    "dividido": {"t0": 0.0, "t1": 3.34, "arq": BR.format(35194304), "ss": 0.5, "y_topo": 380, "y_pessoa": 150,
                 "faixa": {"t0": 0.0, "t1": 3.34, "altura": 270, "cor": "bege", "linhas": [
                     {"y": 905, "tam": 72, "cor": "azul", "spans": [sp("Como", 0.15), sp("o", 0.3), sp("seu", 0.45), sp("processo", 1.56), sp("de", 1.8)]},
                     {"y": 1000, "tam": 110, "spans": [sp("GREEN CARD", 2.02, cor="laranja"), sp("é montado?", 2.42, tam=84, cor="azul")]}]}},
}
