"""LIV · Dra. Lívia em consulta (gravação de 09/11/2026, 4K em pé do iPhone): Reels no padrão aprovado na consulta da
consulta de 10/11 (projetos/liv_consulta_1011/lote_consulta_1011.py): legenda da LIV, sem logo, balão do gancho embaixo, CTA "Comente PERFIL27"
no meio da tela logo após a fala, motion só onde explica o raciocínio (centralizado, componentes grandes).
Cuidados: sem nome ou dado da cliente (sai o nome dela); só as explicações gerais da Dra. Lívia.

Uso: python3 projetos/liv_consulta_0911/lote_consulta.py [final|A|B] [id ...] [--so-montar]
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "liv_consulta_1011"))
import lote_consulta_1011 as M

LT = M.LT
LT.BRUTOS = "/Users/lucastoledo/Downloads"
LT.W, LT.H = 2160, 3840                       # bruto já em pé (4K): o editor só segue o rosto
M.SAIDA = "/Volumes/Untitled/LIV_cortes/consulta_0911"
M.PREFIXO = "liv_consulta"
M.PREFIXO_MOTION = "c0911"
M.ROTEIROS = os.path.join(AQUI, "motion")
B = "2026-11-09_gravacao-09-11-12-08_take-01.mp4"

LT.FRASES += [("Primeiro e vinte,", "Primeiro, o I-20,"), ("e vinte,", "I-20,"), ("vá olhar.", "vai olhar."),
              ("lhe dar o green card,", "lhe dar o Green Card,"), ("green card", "Green Card"),
              ("Quando é O, PT,", "Quando é OPT,"), ("O, PT,", "OPT,"), ("quer que você precisa,", "o que você precisa?"),
              ("tá com o seu", "Tá com o seu"), ("I -20", "I-20"), ("I -20,", "I-20,"), ("I -20.", "I-20."),
              ("I -485?", "I-485?"), ("I -140", "I-140"), ("O, P, T,", "OPT,"), ("C, P, T", "CPT"), ("Cipiti", "CPT"),
              ("o Cipiti", "o CPT"), ("I485.", "I-485?"), ("I485", "I-485"), ("nos 140", "no I-140"), ("pega todos", "pegue todos"), ("O, PT", "OPT"), ("Cipiti?", "CPT?"), ("I485?", "I-485?")]

M.REELS = {
    # "Eu acho que você, | a gente acaba"; "do Brasil. O que é que é, | o que é que é mais forte"; "vai ver, olha... |
    # [nome da cliente] | foi aprovada" (sai o nome); "pegue todos os seus eventos. | ele já tem isso tudo... | é importante"
    "k1_entrevista_ajuste": ("O que o oficial olha na entrevista do Green Card nos EUA 🇺🇸?", [
        (B, 364.50, 383.20, "exato"), (B, 383.90, 391.75, "exato"), (B, 392.16, 410.85), (B, 416.20, 427.60)]),
    # "o I-20 é o vínculo com a escola... OPT... CPT... I-20 válido" + "CPT é só com a escola... dentro da escola"
    "k2_cpt_i20": ("Estudante F-1 com CPT: o que a imigração olha?", [
        (B, 210.10, 226.75), (B, 308.00, 332.15)]),
}
M.COM_MOTION = {"k1_entrevista_ajuste", "k2_cpt_i20"}
M.PERMITIR = {"k1_entrevista_ajuste"}       # "tal data, tal data", "o que é que é mais forte" (estilo)

# Lucas (11/11): sem seguir o rosto da Dra. Lívia, recorte PARADO. O rosto dela fica entre 55% e 74% da largura e a
# ~42% da altura (19 amostras): recorte fixo centrado em 63%, que cabe ela inteira no aberto e no fechado
_cmd = M.cmd_editor
M.cmd_editor = lambda id_, video: _cmd(id_, video) + ["--centro", "0.63,0.42"]
# emendas conferidas na transcrição literal (11/11): "no Brasil." acaba em 383,12, "olha," em 391,48, "prova." em 427,54,
# "CPT" começa em ~308,0 (antes cortava o "Brasil" e o começo do "CPT")

if __name__ == "__main__":
    M.main()
