"""LIV · Mari (Marina) na reunião estratégica (IMG_5069, out/2026): 6 Reels só com a fala dela, legenda e gancho.
Sem CTA, sem motion, sem cena extra (pedido do time). Usa a montagem do lote_ti.py: pedaços pela transcrição literal,
alinhamento take a take, trava de repetição e de repetição na emenda.

Cuidados: é uma reunião com cliente. Nenhum corte leva o nome nem dados do cliente (profissão, família), nem preço
(honorários) nem prazo ("dois a três anos"): regra da LIV, sem promessa de prazo.

Uso: python3 projetos/mari_reuniao/lote_mari.py [id ...] [--so-montar] [--esperado]
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "imigrar_ti_ads"))
import lote_ti as LT

LT.BRUTOS = "/Users/lucastoledo/Downloads"
SAIDA = "/Users/lucastoledo/Downloads/Mari IMG_5069/_em_revisao"     # só vai pra prontos/ depois da auditoria
B = "IMG_5069.MOV"

# grafia da legenda (o Whisper escreve "endevo", "AB2NW", "FMG", "I -140")
LT.FRASES += [("endevo,", "endeavor,"), ("endevo.", "endeavor."), ("endevo", "endeavor"), ("endeavour", "endeavor"),
              ("AB2NW,", "EB-2 NIW,"), ("AB2NW", "EB-2 NIW"), ("EB2NW,", "EB-2 NIW,"), ("EB2 NIW,", "EB-2 NIW,"),
              ("I -140,", "I-140,"), ("I -140.", "I-140."), ("I -140", "I-140"), ("e 140", "I-140"), ("I140", "I-140"),
              ("pela FMG.", "pela UFMG."), ("FMG.", "UFMG."), ("coubesse", "coubessem"), ("Green Car", "Green Card"),
              ("expertize", "expertise"), ("Glicard", "Green Card"), ("pra você ser doutor.", "pra ser sedutor."),
              ("ser doutor.", "ser sedutor."), ("ser doutor,", "ser sedutor,"),
              ("meu próximo", "meu processo,"), ("Na verdade não, né, assim,", "Na verdade, não, né? Assim,"),
              ("infelizmente E como", "infelizmente, como"), ("infelizmente E", "infelizmente,"),
              ("infelizmente Como", "infelizmente, como"), ("Na verdade, não, né, assim,", "Na verdade, não, né? Assim,"), ("como se pensasse", "como se você pensasse"),
              ("mostrar o seu lugar", "mostrar seu lugar"),
              ("processo, Se eu", "processo, se eu"), ("currículo. Eu vim", "currículo, eu vim")]

# (gancho, [(arquivo, início, fim)]): tempos do bruto, conferidos no tempo alinhado das palavras
REELS = {
    # "ele tem, ele tem leis" (gaguejada colada): fecha no "método". "E aí, infelizmente | como mexe com o sonho": cortes
    # exatos no fechamento do "c" (229,28 e 233,16), sem o "como isso, isso que eu vou falar" do meio
    "m1_sedutor": ("Te prometeram Green Card rápido e fácil?", [
        (B, 219.00, 224.30), (B, 228.05, 229.28, "exato"), (B, 233.16, 256.45, "exato")]),
    # "Todo o, todo o processo": começa no 2º "todo" (287,76, no fechamento do "t")
    "m2_carro_vida": ("Trocar de carro ou trocar de vida?", [
        (B, 287.76, 293.95, "exato"), (B, 365.70, 386.24)]),
    # "processo, você, se eu falasse, | se eu falasse no Brasil": sai o 1º; "currículo, | ah, eu sou uma, eu, | eu vim"
    "m3_diploma": ("Seu diploma do Brasil 🇧🇷 vale nos EUA 🇺🇸?", [
        (B, 709.95, 717.30, "exato"), (B, 717.95, 720.95, "exato"), (B, 722.16, 756.70, "exato")]),
    "m4_contribuicao": ("Sem faculdade, dá pra ter Green Card nos EUA 🇺🇸?", [
        (B, 619.20, 626.15), (B, 639.10, 659.29), (B, 794.70, 814.65)]),
    # "São, é, | é como se a gente": começa no 2º "é" (134,88)
    "m5_etapas_eb2niw": ("Quais são as etapas do EB-2 NIW?", [
        (B, 120.55, 128.87), (B, 134.88, 148.10, "exato"), (B, 88.20, 101.52)]),
    "m6_estudo_perfil": ("Seu processo de Green Card é feito sob medida?", [
        (B, 1.40, 35.45), (B, 40.80, 44.68)]),
}
# repetição de estilo, conferida uma a uma: "a gente tem acadêmicos, a gente tem pessoas da área de pesquisa..." (m4),
# "qual que é o seu endeavor, qual que é o seu projeto" e "através de técnicas, através de estudos" (m6), "as pessoas
# escutam, as pessoas dão um significado" (m3); "que é o I-140. E o último" (m5: falso alarme, "é o" e "E o"). Gaguejada curta ("uma, uma", "no, no", "de, de") sai no editor.
PERMITIR = {"m3_diploma", "m4_contribuicao", "m5_etapas_eb2niw", "m6_estudo_perfil"}


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(REELS)
    for id_ in ids:
        gancho, pedacos = REELS[id_]
        print(f"\n=== {id_}", flush=True)
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e, flush=True); continue
        if "--so-montar" in sys.argv:
            continue
        LT.rodar_editor([sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "liv",
                         "--gancho", gancho, "--seg-gancho", "4.2", "--alinhar", "--vad", "--tirar-hesitacoes",
                         "--respiro", "0.22", "--proteger-palavra", "0.40", "--manter-perguntas",
                         "--nome", f"liv_mari_{id_}", "--saida", SAIDA], f"liv_mari_{id_}")


if __name__ == "__main__":
    main()
