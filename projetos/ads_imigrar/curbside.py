"""Anúncio Imigrar "curbside" (vertical ~37,6 s) no formato ads dinâmico, versão A (texto atrás da pessoa no gancho).
Bruto: IMG_0744.MOV (iPhone HDR, 4K 60p), cortado sem as pausas em ~/Library/Caches/editor-reels/ads/imigrar_curbside_corte.mp4
(trechos do bruto: 3.25-11.32, 16.25-19.92, 24.47-26.4, 28.65-29.5, 31.7-32.7, 36.05-37.45, 39.4-52.85, 57.58-64.8).

    python3 editor/ads_dinamico.py projetos/ads_imigrar/curbside.py --versao A

Tipografia: Inter Tight (marca Imigrar), ênfase pelo peso (Black x Regular). Cores: azul royal, rosa, branco.
Sem B-roll externo: a própria gravação já mostra o assunto; o lettering entra por cima dela com véu suave.
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
TR = os.path.join(AQUI, "..", "..", "assets", "transicoes", "FILM BURNS {}.mp4")


def sp(texto, t, **k):
    return dict({"texto": texto, "t": t}, **k)


def L(texto, t, tam, peso, cor="bege"):
    return {"texto": texto, "t": t, "tam": tam, "peso": peso, "cor": cor}


ROTEIRO = {
    "marca": "imigrar",
    "nome": "imigrar_curbside", "saida": "~/Desktop/Editor Reels/anuncios_imigrar",
    "video": "~/Library/Caches/editor-reels/ads/imigrar_curbside_corte.mp4",
    "palavras": os.path.join(AQUI, "curbside_palavras.json"),
    "trocas": {},
    "zoom": [dict(t0=0, t1=2.85, s=1.0, avanco=0.05), dict(t0=2.85, t1=5.4, s=1.15), dict(t0=5.4, t1=8.07, s=1.0, avanco=0.04)],
    # gancho: só a pergunta, atrás da pessoa
    "atras": [
        {"t0": 0.0, "t1": 2.85, "legenda": True, "linhas": [
            {"y": 370, "tam": 200, "peso": 900, "cor": "bege", "track": -0.04,
             "spans": [sp("De", 0.1), sp("graça", 0.35)]},
            {"y": 520, "tam": 120, "peso": 900, "cor": "rosa", "track": -0.035,
             "spans": [sp("na", 1.2), sp("calçada?", 1.45)]}]},
    ],
    # lettering grande por cima da gravação (ênfase pelo peso)
    "lettering": [
        {"t0": 8.07, "t1": 11.74, "linhas": [L("Do lado de fora,", 8.14, 84, 400), L("pode", 10.3, 170, 900),
                                              L("pegar.", 10.5, 170, 900)]},
        {"t0": 27.0, "t1": 30.37, "entrelinha": 1.1, "linhas": [L("Propriedade", 27.14, 120, 900), L("privada?", 28.1, 120, 900),
                                              L("Não pode.", 29.4, 84, 400)]},
        {"t0": 32.2, "t1": 33.55, "linhas": [L("Eles chamam de", 32.27, 84, 400), L("curbside.", 32.79, 170, 900)]},
    ],
    "broll": [],
    "burns_arquivos": [TR.format(n) for n in (24, 41, 19, 44)],
    "burns": [8.07, 11.74, 16.92, 30.37],
    "burn_forca": 0.9,
    "cta": {"t0": 33.6, "t_seta": 34.5, "linha1": "Faça uma", "linha2": "análise de perfil",
            "linha3": "toque no botão abaixo"},
}
