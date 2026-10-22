"""Imigrar · Ednaldo (empresários): 3 anúncios de selfie (A/B no gancho) e Reels cortados da conversa no carro com o
Breno. Usa a mesma montagem do lote_ti.py (pedaços limpos pela transcrição literal + trava de repetição).

Uso: python3 projetos/imigrar_ti_ads/lote_ednaldo.py [id ...]
"""
import os, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import lote_ti as LT

BRUTOS = "/Users/lucastoledo/Downloads/imigrar/celular ednaldo"
LT.BRUTOS = BRUTOS
SAIDA = os.path.join(BRUTOS, "prontos")
E1, E2, E3 = ("054B622E-64CF-407E-BBA5-A787BF1CF635.MOV", "0A859281-2B93-4FD0-8713-99515F6E807C.MOV",
              "EF1C50B1-F220-4DDC-A2ED-3A27C565F688.MOV")      # 464DC331 é cópia do 054B622E

LT.FRASES += [("Livy", "LIV"), ("Toquem", "Toque"), ("descubrem", "descubra"), ("vim", "vir"), ("façam", "faça"),
              ("conge", "cônjuge"), ("congé", "cônjuge"), ("CONJ", "cônjuge"), ("Conj", "cônjuge"), ("CONJI,", "cônjuge,"),
              ("Vixo", "visto"), ("Fisto,", "visto,"), ("visito", "visto"), ("encher", "preencher"),
              ("1 ,8", "1,8"), ("2 ,3", "2,3"), ("B1B2", "B1/B2"),
              ("um ponto oito", "1,8"), ("dois ponto três,", "2,3"), ("dois mil e vinte e cinco,", "2025,"), ("dois mil e vinte e cinco", "2025"),
              ("vidro", "visto"), ("vigiturista", "visto de turista"), ("aprender", "empreender"),
              ("vir em turista,", "vir turistar,"), ("Vistro", "visto"), ("Califórnia maior", "Califórnia é maior"),
              ("o No Brasil.", "o do Brasil."), ("Florida,", "Flórida,"), ("PIB da Flórida Em", "PIB da Flórida em"),
              ("Bib", "PIB"), ("Bibi", "PIB"), ("Florida.", "Flórida."), ("Florida", "Flórida"), ("que E os", "que os"), ("Flórida. Em", "Flórida em")]
R1, R2, R3, R4 = "IMG_9401.MOV", "IMG_9402.MOV", "IMG_9405.MOV", "IMG_9406.MOV"
PERMITIR = {"r4_imposto"}        # "se você tiver resultado, se você tiver lucro": repetição de estilo, não erro
CTA = "Quer saber qual visto combina com você? Link na bio"

# Reels orgânicos da conversa no carro: (gancho, [(arquivo, início, fim)])
REELS = {
    "r1_eleicao": ("Vai sair do Brasil 🇧🇷 por causa da eleição?", [
        (R1, 71.25, 78.40), (R1, 86.90, 91.75), (R1, 106.45, 115.05), (R1, 116.50, 124.35),
        (R1, 124.75, 128.20), (R1, 140.90, 147.30)]),
    "r2_visto_turista": ("Dá pra morar nos EUA 🇺🇸 com visto de turista?", [
        (R1, 275.85, 283.40), (R1, 284.50, 285.40), (R1, 285.45, 289.35), (R1, 291.46, 301.15)]),
    "r3_florida_brasil": ("Flórida 🇺🇸 x Brasil 🇧🇷: qual economia é maior?", [
        (R2, 230.70, 231.62), (R2, 232.88, 237.95), (R2, 238.40, 244.45), (R2, 244.75, 245.90), (R2, 246.64, 257.35), (R2, 257.90, 260.66),
        (R2, 260.86, 261.84), (R2, 261.94, 262.65), (R2, 273.00, 282.35)]),
    "r4_imposto": ("Empresa nos EUA 🇺🇸: quando você paga imposto?", [
        (R3, 1.90, 10.50), (R3, 10.55, 14.45), (R3, 53.55, 66.25), (R3, 67.15, 77.70)]),
    "r5_vistos_empreendedor": ("Quais vistos pra empreendedor ir pros EUA 🇺🇸?", [
        (R3, 209.60, 212.75), (R3, 221.50, 263.30)]),
    "r6_conjuge": ("Seu cônjuge pode trabalhar nos EUA 🇺🇸?", [
        (R4, 3.25, 9.85), (R4, 18.85, 23.05), (R4, 82.95, 96.00), (R4, 99.45, 105.05), (R4, 106.70, 114.00),
        (R4, 114.70, 117.05), (R4, 117.40, 119.62), (R4, 119.80, 121.30), (R4, 126.85, 131.85)]),
}

# anúncios (selfie bem fechada: legenda a 66%, abaixo do queixo; a 55% cobria a boca): ((gancho A, gancho B), [(arquivo, início, fim)])
ANUNCIOS = {
    "e1_empresario_desembarquei": (("Empresário: já pensou em levar sua empresa pros EUA 🇺🇸?",
                                    "Empresário no Brasil 🇧🇷: abrir filial nos EUA 🇺🇸?"), [
        (E1, 1.00, 8.95), (E1, 9.55, 11.60), (E1, 16.70, 25.00), (E1, 25.45, 29.05), (E1, 29.55, 33.80),
        (E1, 36.92, 44.85), (E1, 45.75, 47.40)]),
    "e2_empreendedor_rotas": (("Empreendedor: sua empresa pode crescer nos EUA 🇺🇸?",
                               "Empresário: quais as rotas pra expandir pros EUA 🇺🇸?"), [
        (E2, 0.60, 5.60), (E2, 6.25, 8.95), (E2, 11.75, 22.55), (E2, 23.15, 24.95), (E2, 25.55, 35.10)]),
    "e3_negocio_dificil": (("Empresário: seu negócio no Brasil 🇧🇷 tá difícil?",
                            "Já pensou em levar sua empresa pros EUA 🇺🇸?"), [
        (E3, 0.00, 5.85), (E3, 6.35, 11.25), (E3, 11.65, 15.65), (E3, 21.15, 31.45), (E3, 31.45, 36.75),
        (E3, 37.45, 42.05), (E3, 47.85, 53.00)]),
}


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(ANUNCIOS) + list(REELS)
    for id_ in [i for i in ids if i in REELS]:
        gancho, pedacos = REELS[id_]
        print(f"\n=== {id_}")
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e); continue
        subprocess.run([sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
                        "--gancho", gancho, "--cta", CTA, "--tirar-hesitacoes", "--respiro", "0.22",
                        "--proteger-palavra", "0.15", "--manter-perguntas",
                        "--nome", f"imigrar_ednaldo_{id_}", "--saida", SAIDA], check=True)
    for id_ in [i for i in ids if i in ANUNCIOS]:
        ganchos, pedacos = ANUNCIOS[id_]
        print(f"\n=== {id_}")
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:
            print("  PULADO:", e); continue
        for versao, gancho in zip("AB", ganchos):
            subprocess.run([sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
                            "--gancho", gancho, "--y-legenda", "0.66", "--tirar-hesitacoes", "--respiro", "0.18",
                            "--proteger-palavra", "0.15", "--manter-perguntas",
                            "--nome", f"imigrar_ednaldo_{id_}_{versao}", "--saida", SAIDA], check=True)


if __name__ == "__main__":
    main()
