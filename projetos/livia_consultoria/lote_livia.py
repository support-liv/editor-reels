"""LIV · Dra. Lívia em consulta online (HLV_4, HLV_5, HLV_6, out/2026): Reels verticais (legenda + gancho, sem CTA) e
cortes longos horizontais para o YouTube (16:9, vinheta da LIV, sem legenda). Usa a montagem do lote_ti.py (pedaços
pela transcrição literal, alinhamento take a take, trava de repetição), com intermediário 4K 16:9: o vertical recorta
em volta da Dra. Lívia no editor e o horizontal usa o quadro inteiro.

Cuidados (consulta com clientes): nenhum corte leva nome de cliente (Dani/Daniela, César/Céssia, Cleber...), voz de
cliente nem detalhe do caso deles (visto de turista negado, NOID, filhos, percentuais das empresas). Só as explicações
gerais da Dra. Lívia. Sem promessa de prazo.

Uso: python3 projetos/livia_consultoria/lote_livia.py [id ...] [--so-montar] [--esperado]
"""
import os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "imigrar_ti_ads"))
import lote_ti as LT

LT.BRUTOS = "/Users/lucastoledo/Downloads"
LT.W, LT.H = 3840, 2160                          # intermediário 16:9 em 4K (o vertical recorta sem perder nitidez)
SAIDA = "/Users/lucastoledo/Downloads/Livia HLV/_em_revisao"     # só vai pra prontos/ depois da auditoria
H4, H5, H6 = "HLV_4 (1).MP4", "HLV_5 (1).MP4", "HLV_6.MP4"

# grafia da legenda: vistos no formato oficial e termos que o Whisper escreve errado
LT.FRASES += [("L1", "L-1"), ("EB1C,", "EB-1C,"), ("EB1C.", "EB-1C."), ("EB1C", "EB-1C"), ("EBC", "EB-1C"),
              ("Green Car,", "Green Card,"), ("Green Car", "Green Card"), ("como NW,", "como o NIW,"), ("NW,", "NIW,"),
              ("UOL,", "O-1,"), ("UOL", "O-1"), ("quasi -iduintente.", "quasi dual intent."),
              ("quasi-iduintente.", "quasi dual intent."), ("do intento.", "dual intent."), ("Do intento", "Dual intent"),
              ("H1B.", "H-1B."), ("SIS.", "USCIS."), ("SIS,", "USCIS,"), ("SIS", "USCIS"), ("SES?", "USCIS?"),
              ("C640.", "I-140."), ("DS -260,", "DS-260,"), ("acidentes criminais", "antecedentes criminais"),
              ("documentado e qualify.", "documentarily qualified."), ("digerir tudo,", "pra gerir tudo,"),
              ("New Business.", "new business."), ("New Business", "new business"), ("Folha,", "folha,"),
              ("adicionar para você.", "peticionar para você."), ("Ellie.", "L."), ("fazava", "falava"),
              ("UL", "L-1"), ("IOSS aprovou 640,", "USCIS aprovou o I-140,"), ("O IOSS", "O USCIS"),
              ("documentando qualifier.", "documentarily qualified."), ("documento e qualifier", "documentarily qualified,"),
              ("e qualifier", "documentarily qualified,"), ("preencha DS 260,", "preencha a DS-260,"), ("DS 260,", "DS-260,"),
              ("USIS.", "USCIS."), ("USIS", "USCIS"), ("bem ao objetivo.", "bem objetivo."),
              ("É bem mais subjetivo.", "É bem mais objetivo."), ("como OELE,", "como o L,"),
              ("quasi -aido intente.", "quasi dual intent."), ("o Wally,", "o L,"), ("emigratória,", "imigratória,"),
              ("tem um processo de emigrar de tóuro,", "tenho o processo migratório,"), ("eu toco com o L.", "eu estou com o L."),
              ("uma minuma de estrutura", "uma mínima estrutura"), ("quando tenho o mesmo sócio.", "quando tem o mesmo sócio."),
              ("A uma professora", "Uma professora"), ("Nós chamamos affiliate", "Chama affiliate"),
              ("Você pode dizer, quero emigrar,", "Você pode dizer que quer emigrar,"),
              ("E quando ela tem mais de um ano,", "Quando ela tem mais de um ano,"),
              ("a gente recebe o seu caso,", "a gente recebeu seu caso,")]

# palavra fraca demais para o corte pelo volume (fica pela metade): sai inteira. (anterior, palavra) na transcrição do corte
TIRAR_PALAVRA = {"v2_nvc": [("acontece", "aqui?")], "h2_l1_green_card": [("acontece", "aqui?")]}

# (gancho, [(arquivo, início, fim[, "exato"])]): tempos do bruto, conferidos no tempo alinhado das palavras
VERTICAIS = {
    "v1_funcao_executiva": ("No L-1, o empresário pode pôr a mão na massa?", [
        (H4, 1046.70, 1071.50), (H4, 1078.45, 1102.80)]),
    "v2_nvc": ("I-140 aprovado: o que acontece depois?", [
        (H4, 623.45, 667.38), (H4, 672.88, 692.40)]),
    # 27-51s: fala de outra pessoa; "o seu L-1" começa em 51,68 (silêncio de 51,42 a 51,66)
    "v3_eb1c": ("O L-1 pode virar Green Card?", [
        (H6, 51.55, 75.45, "exato"), (H6, 87.10, 100.20)]),
    "v4_dupla_intencao": ("Tem processo de Green Card? Dá pra pedir o L-1?", [
        (H5, 1179.95, 1186.09), (H5, 1190.95, 1241.46), (H5, 1275.20, 1281.12)]),
    # "acontecendo lá. | Quem que são os impactantes, | quem é que tá lá": sai a frase embolada do meio
    "v5_empresa_nova": ("Empresa nova ou que já existe: qual é melhor pro L-1?", [
        (H5, 36.00, 60.22), (H5, 62.20, 67.13), (H5, 71.38, 79.53, "exato"), (H5, 80.26, 89.70, "exato"),
        (H4, 1292.66, 1300.25, "exato")]),
    "v6_renovacao": ("L-1 de empresa nova: a renovação é mais difícil?", [
        (H5, 1304.05, 1328.30)]),
    # "Aí eu, aí | chama affiliate": começa no "chama" (233,05)
    "v7_mesmo_grupo": ("Pro L-1, suas empresas precisam ser do mesmo grupo?", [
        (H4, 1670.85, 1682.53), (H5, 233.05, 235.90, "exato"), (H4, 1748.97, 1763.77), (H4, 1772.70, 1778.80)]),
    # "um de dez... | A oficial faz entrevista em português" (sai o "que a mulher faz a...")
    "v8_entrevista_ingles": ("A entrevista do visto é em inglês?", [
        (H6, 530.20, 532.95), (H6, 535.10, 541.45), (H6, 542.10, 548.57), (H6, 306.30, 310.87),
        (H6, 444.00, 463.66)]),
}

# cortes longos 16:9 (YouTube): só a fala da Dra. Lívia, na ordem do assunto
HORIZONTAIS = {
    "h1_l1_empresa": [                            # o que a imigração avalia na empresa (grupo, função executiva, empresa nova)
        (H4, 1670.85, 1682.53), (H5, 233.05, 235.90, "exato"), (H4, 1748.97, 1763.77), (H4, 1772.70, 1778.80),
        (H4, 1781.90, 1793.42), (H4, 1046.70, 1071.50), (H4, 1078.45, 1102.80), (H4, 1237.90, 1275.01),
        (H4, 1278.15, 1292.52), (H4, 1292.66, 1300.25, "exato"), (H5, 36.00, 60.22), (H5, 62.20, 67.13),
        (H5, 71.38, 79.53, "exato"), (H5, 80.26, 89.70, "exato"), (H5, 1304.05, 1328.30)],
    "h2_l1_green_card": [                         # dupla intenção, EB-1C, NVC e entrevista em inglês
        (H5, 1179.95, 1186.09), (H5, 1190.95, 1241.46), (H5, 1275.20, 1281.12), (H6, 51.55, 75.45, "exato"),
        (H6, 87.10, 100.20), (H4, 623.45, 667.38), (H4, 672.88, 692.40), (H6, 530.20, 532.95),
        (H6, 535.10, 541.45), (H6, 542.10, 556.04, "exato"), (H6, 272.70, 286.88), (H6, 301.90, 310.87),
        (H6, 314.90, 319.14), (H6, 444.00, 479.56), (H6, 568.80, 589.78)],
}
# recomeço colado ("é que, é que", "tem, tem", "processo administrativo, processo administrativo") o editor tira sozinho
# (--tirar-hesitacoes); o que sobra no aviso do lote é paralelismo de estilo, conferido um a um: "quem é que tá lá, quem é
# que tá na folha", "já tem o lugar, já tem as coisas", "não é isso que ele quer ver. Então, ele quer ver funções",
# "dual intent. Dual intent é duas intenções", "o mínimo, mas o mínimo você consegue"
PERMITIR = set(VERTICAIS) | set(HORIZONTAIS)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(VERTICAIS) + list(HORIZONTAIS)
    for id_ in ids:
        print(f"\n=== {id_}", flush=True)
        if id_ in PERMITIR and "--forcar" not in sys.argv:
            sys.argv.append("--forcar")
        elif id_ not in PERMITIR and "--forcar" in sys.argv:
            sys.argv.remove("--forcar")
        pedacos = VERTICAIS[id_][1] if id_ in VERTICAIS else HORIZONTAIS[id_]
        try:
            video, _ = LT.montar(id_, pedacos)
        except SystemExit as e:                          # repetição: segue com os outros e relata
            print("  PULADO:", e, flush=True); continue
        if "--so-montar" in sys.argv:
            continue
        tirar = []
        if id_ in TIRAR_PALAVRA:                 # "como é que acontece aqui?": o "aqui" sussurrado ficava cortado no meio
            import json, subprocess
            from auditar_fala import norm
            arq_t = os.path.join(LT.TRANSC, id_ + ".json")          # alinha antes (o tempo do Whisper erra 0,1-0,5s)
            subprocess.run([os.path.join(LT.RAIZ, ".venv-whisperx", "bin", "python"),
                            os.path.join(LT.RAIZ, "editor", "alinhar.py"), video, arq_t], check=True)
            dados = json.load(open(arq_t))
            P = dados["palavras"]
            for ant, alvo in TIRAR_PALAVRA[id_]:
                for k in range(len(P) - 1, 0, -1):
                    if norm(P[k - 1]["w"]) == norm(ant) and P[k]["w"] == alvo:
                        tirar += ["--tirar", f"{max(P[k - 1]['e'] + 0.02, P[k]['s'] - 0.08):.2f}-{P[k]['e'] + 0.10:.2f}"]
                        P[k - 1]["w"] = P[k - 1]["w"].rstrip(",.") + alvo[-1] if alvo[-1] in "?.!" else P[k - 1]["w"]
                        del P[k]                         # sai da legenda junto com o áudio
            json.dump(dados, open(arq_t, "w"), ensure_ascii=False, indent=1)
            print("  tirar:", tirar, flush=True)
        editor = [sys.executable, os.path.join(LT.RAIZ, "editor", "editor_reels.py"), video, "--marca", "liv",
                  "--alinhar", "--vad", "--tirar-hesitacoes", "--proteger-palavra", "0.40", "--manter-perguntas",
                  "--nome", f"liv_livia_{id_}", "--saida", SAIDA, *tirar]
        if id_ in VERTICAIS:
            editor += ["--gancho", VERTICAIS[id_][0], "--seg-gancho", "4.2", "--respiro", "0.22"]
        else:
            editor += ["--layout", "youtube", "--sem-inscreva", "--planos", "--respiro", "0.5"]
        LT.rodar_editor(editor, f"liv_livia_{id_}")


if __name__ == "__main__":
    main()
