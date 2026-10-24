"""Auditoria de fala do vídeo PRONTO: compara o que ele deveria dizer (palavras do plano de cortes, salvas pelo
lote com --esperado) com o que o Whisper ouve no arquivo final, palavra a palavra.

- Palavra OUVIDA a mais = sobra de tentativa anterior / repetição ("sabia que, sabia que").
- Palavra ESPERADA que não foi ouvida = corte indevido (palavra comida na emenda).
O áudio é transcrito em janelas que começam e terminam ANTES de uma palavra e longe das emendas (a janela nunca corta
uma palavra no meio nem cai em cima de um corte). Cada janela é ouvida duas vezes (modo literal e modo normal):
só vira alerta o que aparece nas duas leituras. Cada alerta é conferido de novo numa janela curta em volta dele.

Uso: python3 projetos/imigrar_ti_ads/auditoria.py VIDEO.mp4 [...]     (o esperado vem de ~/Library/Caches/.../auditoria_esperado)
"""
import difflib, json, os, re, subprocess, sys
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import auditar_fala as A
from lote_ti import ESPERADO, FPS

# números e palavras que o Whisper escreve de outro jeito: não contam como diferença
NUMERICAS = set("cem cento mil vinte trinta seis cinco oito tres dois dez quinze ponto um uma por cento percent".split())
MULETAS = {"ne", "ta", "e", "ai", "ah", "eh", "hum", "assim"}


def tokens(ws):
    out = []
    for w in ws:
        n = A.norm(w["w"])
        if n:
            out.append((n, w))
    return out


def esperado(nome):
    pal = json.load(open(os.path.join(ESPERADO, nome + ".palavras.json")))
    cortes = json.load(open(os.path.join(ESPERADO, nome + ".cortes.json")))
    emendas, t = [], 0.0
    for c in cortes:
        t += round((c["e"] - c["s"]) * FPS) / FPS
        emendas.append(t)
    return pal, emendas[:-1]


def janelas(pal, emendas, dur, alvo=6.0):
    """pontos de divisão logo antes de uma palavra, a mais de 0,7s de qualquer emenda."""
    candidatos = [p["t"] - 0.06 for p in pal[1:] if all(abs(p["t"] - e) > 0.7 for e in emendas)]
    cortes, ini = [], 0.0
    for c in candidatos:
        if c - ini >= alvo:
            cortes.append((ini, c)); ini = c
    cortes.append((ini, dur))
    return cortes


def comparar(esp, ouv):
    """blocos (tipo, esperado, ouvido) que diferem, ignorando números e muletas soltas."""
    a, b = [t for t, _ in esp], [t for t, _ in ouv]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    difs = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        e, o = esp[i1:i2], ouv[j1:j2]
        if any(any(ch.isdigit() for ch in t) or t in NUMERICAS for t, _ in e + o):
            continue
        if not e and all(t in MULETAS for t, _ in o):
            continue
        if op == "replace" and len(e) == len(o) and all(
                difflib.SequenceMatcher(a=x, b=y).ratio() >= 0.6 for (x, _), (y, _) in zip(e, o)):
            continue                                      # grafia diferente da mesma palavra
        difs.append((op, e, o))
    return difs


TRANSC = os.path.join(AQUI, "..", "..", "editor", "transcricoes")
HESIT = {"e", "ah", "eh", "hum", "hm", "ahn", "uhm", "ee", "eee", "aa", "ne", "entao", "assim"}


def id_do_video(nome):
    for pre in ("imigrar_ti_", "imigrar_ednaldo_", "imigrar_narrado_", "liv_mari_", "liv_livia_"):
        if nome.startswith(pre):
            base = nome[len(pre):]
            return base[:-2] if base.endswith(("_A", "_B")) else base
    return "IMG_4811" if "4811" in nome else nome


def checagem_exata(nome):
    """com o tempo das palavras ALINHADO (WhisperX), checa sem ouvir: corte caindo dentro de palavra e palavra do trecho
    que sumiu do vídeo pronto (fora hesitação)."""
    arq = os.path.join(TRANSC, id_do_video(nome) + ".json")
    if not os.path.exists(arq):
        return []
    P = json.load(open(arq))["palavras"]
    if not any(p.get("alinhada") for p in P):
        return []
    cortes = json.load(open(os.path.join(ESPERADO, nome + ".cortes.json")))
    esperadas = json.load(open(os.path.join(ESPERADO, nome + ".palavras.json")))
    alertas, t_out = [], 0.0
    # voz de fato no ponto do corte (o fim alinhado às vezes inclui o silêncio seguinte: sem voz, não é corte na palavra)
    iid = id_do_video(nome)
    fonte = (os.path.expanduser(f"~/Library/Caches/editor-reels/ti_intermediarios/{iid}.mov") if iid != "IMG_4811"
             else "/Users/lucastoledo/Downloads/imigrar/ads/TI/IMG_4811.mov")
    if not os.path.exists(fonte):                      # vídeos narrados (projetos/imigrar_narrados)
        fonte = os.path.expanduser(f"~/Library/Caches/editor-reels/narrados_intermediarios/{iid}.mov")
    sys.path.insert(0, os.path.join(AQUI, "..", "..", "editor"))
    import editor_reels as E
    vn, _ = E.mascaras_vad(fonte)
    db, lim = E.energia_db(fonte)
    nn = min(len(vn), len(db))
    voz = vn[:nn] & (db[:nn] > lim - 8)          # os dois: o Silero sozinho ouve o burburinho do fundo como fala
    # o corte só come som se a voz CONTINUA do lado de fora: depois do fim do corte ou antes do começo (o fim alinhado de
    # "pra" engolia 0,8s de silêncio e todo corte nesse silêncio virava alerta falso)
    fora_fim = lambda t: bool(voz[int(t / 0.02) + 1:int(t / 0.02) + 4].any())
    fora_ini = lambda t: bool(voz[max(0, int(t / 0.02) - 4):max(0, int(t / 0.02) - 1)].any())
    lo, hi = min(c["s"] for c in cortes), max(c["e"] for c in cortes)
    for c in cortes:
        for w in P:
            if not w.get("alinhada"):
                continue
            if w["s"] + 0.03 < c["s"] < w["e"] - 0.03 and fora_ini(c["s"]):
                alertas.append((t_out, "CORTE NA PALAVRA", f"início do corte em {c['s']:.2f}s corta «{w['w']}»", ""))
            if w["s"] + 0.03 < c["e"] < w["e"] - 0.03 and fora_fim(c["e"]):
                alertas.append((t_out + c["e"] - c["s"], "CORTE NA PALAVRA", f"fim do corte em {c['e']:.2f}s corta «{w['w']}»", ""))
        t_out += round((c["e"] - c["s"]) * FPS) / FPS
    if id_do_video(nome) == "IMG_4811":                 # bruto inteiro com trechos: o intervalo tem fala de propósito fora
        return alertas
    # FALA FORA DO CORTE: voz no intermediário (que só tem os trechos escolhidos) que não entrou no vídeo. No R1 o
    # alinhador jogou a frase final pra trás e o corte acabou antes dela.
    dentro_corte = np.zeros(nn, bool)
    for c in cortes:
        dentro_corte[int(c["s"] / 0.02):int(c["e"] / 0.02) + 1] = True
    fora = voz & ~dentro_corte[:nn]
    i = 0
    while i < nn:
        if fora[i]:
            j = i
            while j < nn and fora[j]:
                j += 1
            a_, b_ = i * 0.02, j * 0.02
            ws = [w["w"] for w in P if w["s"] < b_ and w["e"] > a_]
            fala = [w for w in ws if A.norm(w) and A.norm(w) not in HESIT]
            if (b_ - a_ >= 0.30 and fala) or b_ - a_ >= 0.8:
                alertas.append((a_, "FALA FORA DO CORTE", f"{a_:.2f}-{b_:.2f}s: «{' '.join(ws)[:60]}»", ""))
            i = j
        i += 1
    # palavra que estava dentro do intermediário e não está no pronto (o editor tirou): só hesitação pode sair
    dentro = [w for w in P if lo <= (w["s"] + w["e"]) / 2 <= hi]
    usadas = [A.norm(p["w"]) for p in esperadas]
    from collections import Counter
    faltam = Counter(A.norm(w["w"]) for w in dentro) - Counter(usadas)
    for palavra, n in faltam.items():
        if palavra and palavra not in HESIT:
            alertas.append((0.0, "PALAVRA TIRADA", f"«{palavra}» x{n}", ""))
    return alertas


def auditar(video):
    nome = os.path.splitext(os.path.basename(video))[0]
    pal, emendas = esperado(nome)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    alertas = []
    for ini, fim in janelas(pal, emendas, dur):
        esp = tokens([{"w": p["w"], "s": p["t"]} for p in pal if ini <= p["t"] < fim])
        literal = A.transcrever_janela(video, ini, fim, literal=True)
        normal = A.transcrever_janela(video, ini, fim, literal=False)
        ok_lit, ok_nor = A.max_iguais(literal) < 5, A.max_iguais(normal) < 5      # >= 5 iguais = alucinação
        if not ok_lit and not ok_nor:
            alertas.append((ini, "ILEGÍVEL", "", "")); continue
        d_lit = comparar(esp, tokens(literal)) if ok_lit else []
        d_nor = comparar(esp, tokens(normal)) if ok_nor else []
        chave = lambda d: (d[0], tuple(t for t, _ in d[1]), tuple(t for t, _ in d[2]))
        faltas_nor = {chave(d) for d in d_nor}
        # palavra A MAIS: vale a leitura literal (a normal apaga repetição). FALTA/TROCA: só se as duas leituras
        # concordam (uma leitura sozinha erra palavra com frequência)
        for d in d_lit if ok_lit else d_nor:
            op, e, o = d
            if op == "insert" or chave(d) in faltas_nor or not ok_nor:
                t = (e[0][1]["s"] if e else o[0][1]["s"])
                alertas.append((t, {"insert": "A MAIS", "delete": "FALTA", "replace": "TROCA"}[op],
                                " ".join(w["w"] for _, w in e), " ".join(w["w"] for _, w in o)))
    alertas += checagem_exata(nome)
    # FIM DA FALA: a última palavra esperada tem que estar inteira nos últimos 2,5s (alguma das duas leituras)
    ult = [t for t, _ in tokens(pal[-3:] and [{"w": p["w"]} for p in pal[-3:]])]
    fim_ws = A.transcrever_janela(video, max(0.0, dur - 2.5), dur, literal=False) + \
        A.transcrever_janela(video, max(0.0, dur - 2.5), dur, literal=True)
    ouvidas = {t for t, _ in tokens(fim_ws)}
    if ult and ult[-1] not in ouvidas and not any(difflib.SequenceMatcher(a=ult[-1], b=o).ratio() >= 0.75 for o in ouvidas):
        alertas.append((dur - 1.0, "FIM CORTADO", " ".join(p["w"] for p in pal[-3:]), " ".join(w["w"] for w in fim_ws[-4:])))
    print(f"\n=== {nome}: {'OK' if not alertas else str(len(alertas)) + ' alerta(s)'}")
    for t, tipo, e, o in alertas:
        perto = min([abs(t - x) for x in emendas] or [9])
        print(f"  {t:6.2f}s {tipo:7s} esperado: «{e}»  ouvido: «{o}»{'  (na emenda)' if perto < 0.8 else ''}")
    return alertas


if __name__ == "__main__":
    total = 0
    for v in sys.argv[1:]:
        total += len(auditar(v))
    print(f"\nTOTAL: {total} alerta(s)")
