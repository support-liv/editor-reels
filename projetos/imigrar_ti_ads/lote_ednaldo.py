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
SAIDA = os.path.join(BRUTOS, "_em_revisao")      # só vai pra prontos/ depois de aprovado na auditoria
E1, E2, E3 = ("054B622E-64CF-407E-BBA5-A787BF1CF635.MOV", "0A859281-2B93-4FD0-8713-99515F6E807C.MOV",
              "EF1C50B1-F220-4DDC-A2ED-3A27C565F688.MOV")      # 464DC331 é cópia do 054B622E

LT.FRASES += [("Livy", "LIV"), ("Toquem", "Toque"), ("descubrem", "descubra"), ("vim", "vir"), ("façam", "faça"),
              ("conge", "cônjuge"), ("congé", "cônjuge"), ("CONJ", "cônjuge"), ("Conj", "cônjuge"), ("CONJI,", "cônjuge,"),
              ("Vixo", "visto"), ("Fisto,", "visto,"), ("visito", "visto"), ("encher", "preencher"),
              ("1 ,8", "1,8"), ("2 ,3", "2,3"), ("B1B2", "B1/B2"),
              ("um ponto oito", "1,8"), ("dois ponto três,", "2,3"), ("dois mil e vinte e cinco,", "2025,"), ("dois mil e vinte e cinco", "2025"),
              ("vidro", "visto"), ("vigiturista", "visto de turista"), ("aprender", "empreender"),
              ("vir em turista,", "vir turistar,"), ("Vistro", "visto"), ("Califórnia maior", "Califórnia é maior"),
              ("o No Brasil.", "o do Brasil."), ("Florida,", "Flórida,"), ("PIB da Flórida Em", "PIB da Flórida em"), ("um a um,", "um O-1,"),
              ("entenerário", "itinerário"), ("zonamento,", "zoneamento,"), ("PTU,", "IPTU,"), ("Tavstop,", "Tavistock,"),
              ("quadros", "quadras"), ("valiu", "avaliou"), ("momento e vou", "momento e voltar?"), ("O A1,", "O O-1,"), ("A1", "O-1"), ("Porque ao", "que é o"), ("QMK,", "Green Card,"), ("da onda que", "da onde"), ("revimorar", "vir morar"), ("a dez anos", "há dez anos"), ("O estimativo", "A estimativa"), ("milha a gasolina", "milha e gasolina"), ("Moto 3.", "O-3."), ("Moto", "O-3"), ("vicho", "visto"), ("lise", "lease"), ("Lizzie", "lease"), ("adição", "decisão"), ("põe a luz", "a luz"), ("O1", "O-1"),
              ("Bib", "PIB"), ("Bibi", "PIB"), ("Florida.", "Flórida."), ("Florida", "Flórida"), ("que E os", "que os"), ("Flórida. Em", "Flórida em")]
R1, R2, R3, R4 = "IMG_9401.MOV", "IMG_9402.MOV", "IMG_9405.MOV", "IMG_9406.MOV"
PERMITIR = {"r4_imposto", "r7_esperar_eleicao", "r9_brasileiros_orlando", "r10_imigrante_sucesso",
            "r11_prestador_empresa", "r14_vaca_imposto", "r15_lake_nona"}   # paralelismo de estilo ("se você tiver resultado, se você tiver lucro"), revisado um a um
CTA = "Comente PERFIL27 e receba sua análise de perfil"     # CTA da campanha (pedido em 23/10)

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
    # 2ª leva (pedida em 22/10): mais cortes da conversa com o Breno
    "r7_esperar_eleicao": ("Vale esperar a eleição pra decidir imigrar?", [
        (R1, 334.10, 341.35), (R1, 351.75, 359.80), (R1, 371.20, 373.95), (R1, 375.05, 382.80), (R1, 383.90, 387.40)]),
    "r8_primeiro_passo": ("Empreendedor: qual o primeiro passo pros EUA 🇺🇸?", [
        (R2, 143.00, 147.60), (R2, 150.05, 152.60), (R2, 155.90, 157.42), (R2, 159.70, 161.85), (R2, 164.05, 167.40),
        (R2, 168.55, 171.00), (R2, 184.45, 190.05), (R2, 191.30, 192.10)]),
    "r9_brasileiros_orlando": ("Quantos brasileiros moram em Orlando 🇺🇸?", [
        (R2, 195.30, 200.40), (R2, 209.95, 214.55), (R2, 214.60, 218.45), (R2, 220.55, 225.30), (R2, 226.20, 229.95)]),
    "r10_imigrante_sucesso": ("Imigrante tem espaço pra crescer nos EUA 🇺🇸?", [
        (R2, 294.30, 301.60), (R2, 302.55, 310.35), (R2, 319.55, 321.95), (R2, 323.70, 334.85),
        (R2, 336.00, 338.95)]),
    "r11_prestador_empresa": ("Por que tanta gente abre empresa nos EUA 🇺🇸?", [
        (R3, 88.80, 93.30), (R3, 94.15, 108.55), (R3, 108.70, 117.60), (R3, 120.40, 124.25), (R3, 124.60, 126.95),
        (R3, 130.50, 137.10)]),
    "r12_o1_itinerario": ("Visto O-1: quando você pode entrar nos EUA 🇺🇸?", [
        (R4, 232.40, 238.80), (R4, 239.10, 241.20), (R4, 241.85, 244.30), (R4, 245.30, 252.70), (R4, 267.30, 286.40),
        (R4, 287.65, 293.80)]),
    "r13_o1_carimbo": ("Visto O-1: o carimbo no passaporte vale quanto tempo?", [
        (R4, 197.50, 202.20), (R4, 203.50, 209.20), (R4, 209.65, 211.00), (R4, 212.15, 220.20)]),
    "r14_vaca_imposto": ("Por que tem vaca no meio da cidade nos EUA 🇺🇸?", [
        (R4, 422.10, 429.50), (R4, 433.25, 434.30), (R4, 442.70, 443.95), (R4, 445.00, 446.75), (R4, 455.45, 466.40), (R4, 472.95, 473.90)],
        [("vacas_1", R4, 427.0), ("vacas_2", R4, 456.8), ("pasto", R4, 463.2)]),
    "r15_lake_nona": ("Como é um bairro planejado nos EUA 🇺🇸?", [
        (R4, 344.50, 353.40), (R4, 360.10, 364.30), (R4, 379.65, 389.20), (R4, 391.10, 392.45), (R4, 392.80, 396.70), (R4, 399.15, 403.50),
        (R4, 404.70, 410.90)],
        [("casas_1", R4, 345.0), ("casas_2", R4, 360.4), ("rua_planejada", R4, 393.0), ("casa_moderna", R4, 399.4),
         ("fachada", R4, 405.0)]),
}

# B-roll de contexto dos Reels (banco de cenas da pasta Downloads, preparar_broll.py): (cena, arquivo, tempo no bruto)
# no momento em que a fala cita aquilo. Sem áudio; a legenda continua por cima.
BROLLS_REELS = {
    "r1_eleicao": [("pessoas_calcada", R1, 116.7), ("casas_rua", R1, 120.6), ("rua_bandeiras", R1, 125.8)],
    "r2_visto_turista": [("homem_mochila", R1, 278.0), ("rua_bandeiras", R1, 287.3), ("casas_rua", R1, 298.8)],
    "r3_florida_brasil": [("rodovia_placas", R2, 234.0), ("rodovia_transito", R2, 241.6), ("comercio_estacionamento", R2, 277.6)],
    "r4_imposto": [("escritorio_equipe", R3, 5.5), ("escritorio_computador", R3, 57.2), ("escritorio_mesa", R3, 70.6)],
    "r5_vistos_empreendedor": [("documento_vistos", R3, 222.6), ("escritorio_duas", R3, 240.5), ("escritorio_analista", R3, 250.6)],
    "r6_conjuge": [("pessoas_calcada", R4, 7.2), ("casas_lago", R4, 86.2), ("escritorio_conversa", R4, 107.2)],
    "r7_esperar_eleicao": [("documento_vistos", R1, 338.0), ("condominio_lago", R1, 355.0), ("rua_bandeiras", R1, 375.5)],
    "r8_primeiro_passo": [("rodovia_placas", R2, 145.0), ("homem_mochila", R2, 164.3), ("pessoas_calcada", R2, 185.6)],
    "r9_brasileiros_orlando": [("rodovia_placas", R2, 210.5), ("comercio_estacionamento", R2, 221.5),
                               ("escritorio_computador", R2, 226.9)],
    "r10_imigrante_sucesso": [("predio_moderno", R2, 295.5), ("predio_hospital", R2, 299.7), ("pessoas_calcada", R2, 303.4),
                              ("rua_bandeiras", R2, 336.3)],
    "r11_prestador_empresa": [("escritorio_analista", R3, 95.5), ("dirigindo", R3, 109.2), ("rodovia_transito", R3, 113.5),
                              ("estacionamento_carros", R3, 121.0)],
    "r12_o1_itinerario": [("documento_vistos", R4, 242.0), ("escritorio_equipe", R4, 268.0), ("rua_bandeiras", R4, 280.5)],
    "r13_o1_carimbo": [("documento_vistos_2", R4, 198.5), ("escritorio_mesa", R4, 215.5)],
    "r14_vaca_imposto": [("vacas_1", R4, 427.0), ("vacas_2", R4, 456.8), ("pasto", R4, 463.2)],
    "r15_lake_nona": [("casas_1", R4, 345.0), ("placa_lake_nona", R4, 361.0), ("predio_moderno", R4, 380.0),
                      ("predio_hospital", R4, 383.0), ("rua_planejada", R4, 393.0), ("casa_moderna", R4, 399.4),
                      ("fachada", R4, 405.0)],
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
        gancho, pedacos, *extra = REELS[id_]
        brolls = BROLLS_REELS.get(id_, extra[0] if extra else [])   # B-roll de contexto (sem áudio, legenda continua)
        print(f"\n=== {id_}")
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        try:
            video, mapa = LT.montar(id_, pedacos)
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e); continue
        extra_args = ["--broll-com-legenda"] if brolls else []
        for nome, arq, tb in brolls:
            extra_args += ["--broll", f"{os.path.join(LT.BROLL, nome + '.mp4')}@fonte:{LT.no_intermediario(mapa, arq, tb):.2f}"]
        LT.rodar_editor([sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar", *extra_args,
                         "--gancho", gancho, "--seg-gancho", "4.2", "--cta", CTA, "--crop-fixo", "--punch", "0.80", "--alinhar", "--vad", "--tirar-hesitacoes", "--respiro", "0.22",
                         "--proteger-palavra", "0.40", "--manter-perguntas",
                         "--nome", f"imigrar_ednaldo_{id_}", "--saida", SAIDA], f"imigrar_ednaldo_{id_}")
    for id_ in [i for i in ids if i in ANUNCIOS]:
        ganchos, pedacos = ANUNCIOS[id_]
        print(f"\n=== {id_}")
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:
            print("  PULADO:", e); continue
        for versao, gancho in zip("AB", ganchos):
            LT.rodar_editor([sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
                             "--gancho", gancho, "--seg-gancho", "4.2", "--y-legenda", "0.66", "--crop-fixo", "--punch", "0.80", "--alinhar", "--vad", "--tirar-hesitacoes", "--respiro", "0.22",
                             "--proteger-palavra", "0.40", "--manter-perguntas",
                             "--nome", f"imigrar_ednaldo_{id_}_{versao}", "--saida", SAIDA], f"imigrar_ednaldo_{id_}_{versao}")
            if "--esperado" in sys.argv:
                break


if __name__ == "__main__":
    main()
