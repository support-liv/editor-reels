#!/usr/bin/env python3
"""Lições da aprovação: o que a Dra. Lívia (LIV) e a Marinna (Imigrar) escrevem ao reprovar um vídeo na Video Machine
(liv.ai) vira lição em docs/REPROVACOES.md, agrupada pelo motivo, para o mesmo erro não voltar.

    python3 editor/licoes_da_aprovacao.py                  # traz as reprovações novas e acrescenta no guia
    python3 editor/licoes_da_aprovacao.py --ver            # só mostra o que entraria (não grava)
    python3 editor/licoes_da_aprovacao.py --desde 2026-10-01 --marca LIV
    python3 editor/licoes_da_aprovacao.py --criar-chave    # gera a chave, guarda no Chaveiro e copia (colar no Easypanel)
    python3 editor/licoes_da_aprovacao.py --guardar-chave  # chave que já existe: uma janela pede para colar

A chave é a APROVACAO_INGEST_TOKEN do liv.ai. Fica no Chaveiro do Mac (Gerenciador de Credenciais no Windows), nunca em
arquivo nem no chat: o --criar-chave copia direto para a área de transferência e o --guardar-chave pede numa janela.

O guia só cresce: cada reprovação entra uma vez (pelo id da decisão, anotado na linha) e o texto escrito à mão (a lição
de cada motivo) nunca é mexido. Reprovação desfeita ou trocada por aprovação não entra (a revisora voltou atrás).

Desde 30/10/2026 entram também os "Aprovar com ajustes" (a ideia passou, mas faltou algo: contexto, legenda…), em seções
próprias ("Ajuste · Falta contexto"). Ajuste conta mesmo depois de a versão nova ser aprovada: o erro aconteceu.
"""
import argparse, datetime, json, os, re, secrets, subprocess, sys, urllib.error, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import plataforma as PLAT

SERVICO_CHAVEIRO = "editor-reels-aprovacao-ingest"
URL_PADRAO = "https://ai.liv.law"
GUIA = os.path.join(RAIZ, "docs", "REPROVACOES.md")
INICIO = "2026-10-01"          # a Video Machine começou a aprovar em out/2026
SOBREPOSICAO_DIAS = 3          # pede de novo os últimos dias: decisão gravada fora de ordem não se perde (o id descarta a repetida)
SEM_ATALHO = "Sem atalho (só o texto)"
AJUSTE = "Ajuste · "            # prefixo das seções dos "aprovar com ajustes"
DADO_DE_CLIENTE = "Aparece dado de cliente"
MARCA = re.compile(r"<!-- r:(\d+) v:(\d+) em:([0-9T:.\-Z+]+) -->")

# Lição de cada motivo de reprova (os atalhos de MOTIVOS_DE_REPROVA no liv.ai). Entra só quando a seção é criada; depois
# a seção é de quem edita o guia.
LICOES = {
    "Legenda errada": (
        "Confira a legenda **inteira** antes de entregar: vistos no formato oficial (E-2, O-1, EB-2 NIW, H-1B, Green Card), "
        "nomes em inglês (Lake Nona, Tavistock), concordância. O Whisper escreve \"wincard\", \"Lequinona\", \"QMK\". Palavra "
        "que a revisora apontou vira correção fixa do lote e entra em `docs/CORTE_DE_FALA.md` → Legenda."),
    "Corte no meio da fala": (
        "Nunca cortar palavra, nem no fim: `--proteger-palavra --alinhar --vad`; pedaço escolhido à mão termina no FIM da "
        "última palavra (transcrição literal); auditoria (`auditoria.py` + `conferir_alertas.py` + "
        "`filtrar_confirmados.py`) antes de `prontos/`. Causas conhecidas em `docs/CORTE_DE_FALA.md`."),
    "Fala repetida": (
        "O Whisper normal esconde repetição. Escolha os takes pela transcrição **literal**, use `--tirar-hesitacoes` e "
        "confira as emendas (fim de um take x começo do outro). Ver `docs/CORTE_DE_FALA.md`."),
    DADO_DE_CLIENTE: (
        "Nenhum nome, rosto, voz, caso, documento, preço ou prazo de cliente, nem na fala, nem na tela (tela compartilhada, "
        "chat da live, documento na mesa). Leia a transcrição inteira atrás de nomes e olhe os quadros antes de escolher os "
        "trechos. O texto da revisora **não** é copiado aqui: pode conter o próprio dado (está no liv.ai)."),
    "Enquadramento": (
        "Rosto enquadrado, legenda e caixas sem tapar rosto, verticais retas, nada distorcido. Live em tela dividida: "
        "`--previa-enquadramento` validada e `--exigir-enquadramento`; selfie na mão: `--crop-fixo` e legenda abaixo do "
        "queixo. Ver `docs/ENQUADRAMENTO.md` e `docs/PADROES.md`; confira quadros do vídeo pronto."),
    "Áudio": (
        "Voz clara e no mesmo volume do começo ao fim; trilha bem abaixo da fala (auditor-de-trilha); áudio e vídeo com a "
        "mesma duração (`ffprobe`, diferença acima de 0,05s é bug); `editor/auditar_pronto.py` para buracos e respiros. "
        "Ouça pelo menos um vídeo inteiro de cada tipo antes de mandar."),
    "Gancho": (
        "Gancho só pergunta, nunca responde, e a resposta tem de estar no vídeo. Sem promessa de aprovação ou prazo. Ver "
        "`docs/FORMATOS.md` e `docs/PADROES.md`; mostre os ganchos no plano antes de renderizar."),
    "Não vale publicar": (
        "O trecho não se sustenta sozinho (assunto fraco, sem conclusão, repetido de outro corte, informação sensível). "
        "Cada corte precisa de uma ideia que vale por si, com começo, meio e fim; na dúvida, ofereça menos cortes e mostre "
        "o texto de cada um no plano antes de renderizar."),
    SEM_ATALHO: (
        "A revisora escreveu sem escolher um atalho. Leia o texto: pedido que aparecer duas vezes vira regra no "
        "`CLAUDE.md` ou no doc do assunto, e a seção ganha a lição."),
}


# Lição de cada atalho de "Aprovar com ajustes" (MOTIVOS_DE_AJUSTE no liv.ai): o vídeo passou, mas voltou para refinar.
LICOES_DE_AJUSTE = {
    "Falta contexto": (
        "Aprovado, mas faltou situar quem assiste. Nos primeiros segundos, diga para quem é (visto, fase do processo, "
        "situação) e por que importa; corte que começa no meio da conversa ganha uma frase ou um texto na tela que dê o "
        "contexto. Mostre no plano qual é o contexto de cada corte antes de renderizar."),
    "Legenda": (
        "Aprovado com legenda a corrigir: grafia de nomes e vistos no formato oficial, quebras e sincronia. Confira a "
        "legenda inteira antes de entregar (`docs/CORTE_DE_FALA.md`)."),
    "Gancho": (
        "Aprovado, mas o gancho pode melhorar: pergunta curta, que não responde, ligada ao que o vídeo entrega "
        "(`docs/FORMATOS.md`)."),
    "Corte": (
        "Aprovado com corte a refinar: início e fim no silêncio, sem respiro longo nem palavra cortada; confira as "
        "emendas (`docs/CORTE_DE_FALA.md`)."),
    "Texto na tela": (
        "Aprovado com texto na tela a ajustar: ortografia, tamanho, área segura e nada tapando o rosto "
        "(`docs/PADROES.md`)."),
    "Áudio": "Aprovado com áudio a ajustar: volume da fala, trilha bem abaixo, sem chiado nem estalo.",
    "Enquadramento": "Aprovado com enquadramento a ajustar: rosto centrado, legenda abaixo do queixo, verticais retas.",
    SEM_ATALHO: "Pedido de ajuste só em texto: leia; o que se repetir vira regra no `CLAUDE.md` ou no doc do assunto.",
}


def _secao_da_entrada(r, motivo):
    """Reprovação: a seção do motivo. Ajuste: a seção 'Ajuste · <motivo>'."""
    return AJUSTE + motivo if r.get("tipo") == "ajustar" else motivo


def _contexto_ssl():
    """certificados: o Python do python.org no Mac vem sem eles; usa o certifi quando existir."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


class Falha(Exception):
    """Erro com a frase para a pessoa (sem detalhe técnico)."""


# ------------------------------------------------------------------ chave (Chaveiro)
def _copiar(texto):
    if PLAT.MAC:
        subprocess.run(["pbcopy"], input=texto, text=True, check=True)
    else:
        subprocess.run(["clip"], input=texto, text=True, check=True)


def criar_chave(substituir=False):
    if PLAT.ler_segredo(SERVICO_CHAVEIRO) and not substituir:
        print("Já existe uma chave guardada neste computador. Para trocar: --criar-chave --substituir "
              "(a do Easypanel tem de ser trocada junto).")
        return 1
    chave = secrets.token_urlsafe(32)
    PLAT.guardar_segredo(SERVICO_CHAVEIRO, chave)
    _copiar(chave)
    print("Chave nova guardada no Chaveiro e copiada. Cole no Easypanel (liv.ai → Environment) como "
          "APROVACAO_INGEST_TOKEN e salve; depois copie qualquer outra coisa para tirar a chave da área de transferência.")
    return 0


def guardar_chave():
    if PLAT.MAC:
        r = subprocess.run(["osascript", "-e",
                            'text returned of (display dialog "Cole a chave da aprovação do liv.ai '
                            '(APROVACAO_INGEST_TOKEN). Ela vai direto para o Chaveiro." default answer "" '
                            'with hidden answer buttons {"Cancelar", "Guardar"} default button "Guardar" '
                            'with title "Editor Reels")'], capture_output=True, text=True)
        chave = r.stdout.strip() if r.returncode == 0 else ""
    else:
        import getpass
        chave = getpass.getpass("Cole a chave da aprovação do liv.ai (não aparece na tela): ").strip()
    if not chave:
        print("Nada foi guardado.")
        return 1
    PLAT.guardar_segredo(SERVICO_CHAVEIRO, chave)
    print("Chave guardada no Chaveiro.")
    return 0


# ------------------------------------------------------------------ liv.ai
def _pedir(url, chave):
    pedido = urllib.request.Request(url, headers={"Authorization": f"Bearer {chave}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(pedido, timeout=60, context=_contexto_ssl()) as resp:
            tipo = resp.headers.get("Content-Type", "")
            corpo = resp.read()
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise Falha("A chave guardada neste computador não é a mesma do liv.ai. Guarde a certa com --guardar-chave.")
        if e.code == 503:
            raise Falha("O liv.ai ainda não tem a chave da aprovação (APROVACAO_INGEST_TOKEN no Easypanel).")
        raise Falha(f"O liv.ai respondeu com erro ({e.code}). Tente de novo em alguns minutos.")
    except urllib.error.URLError:
        raise Falha("Não consegui falar com o liv.ai. Confira a internet e tente de novo.")
    # rota que não existe no liv.ai responde 200 com a página do app, não 404
    if "json" not in tipo:
        raise Falha("O liv.ai no ar ainda não tem a lista de reprovações (falta publicar a versão nova).")
    return json.loads(corpo)


def buscar(base, chave, desde, marca=None):
    """Todas as reprovações desde a data, página a página (pelo id da última)."""
    todas, depois_de = [], 0
    while True:
        # o liv.ai de antes de 30/10/2026 ignora `tipos` e manda só as reprovações (sem o campo `tipo`)
        qs = {"desde": desde, "depoisDe": depois_de, "tipos": "reprovado,ajustar"}
        if marca:
            qs["marca"] = marca
        dados = _pedir(f"{base.rstrip('/')}/api/aprovacao/ingest/reprovacoes?{urllib.parse.urlencode(qs)}", chave)
        todas += dados["reprovacoes"]
        if not dados.get("truncado") or not dados["reprovacoes"]:
            return todas, dados.get("motivosConhecidos", [])
        depois_de = dados["reprovacoes"][-1]["id"]


# ------------------------------------------------------------------ guia (docs/REPROVACOES.md)
def _data_br(em):
    instante = datetime.datetime.fromisoformat(em.replace("Z", "+00:00"))
    try:
        from zoneinfo import ZoneInfo
        instante = instante.astimezone(ZoneInfo("America/Sao_Paulo"))
    except Exception:
        instante = instante.astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
    return instante.strftime("%d/%m/%Y")


def _uma_linha(texto):
    return re.sub(r"\s+", " ", texto or "").strip()


def linha_do_guia(r, motivo):
    marca = "Imigrar" if r["marca"] == "IMIGRAR" else r["marca"]
    partes = [_data_br(r["em"]), marca, _uma_linha(r["lote"]["titulo"]),
              f"`{r['video']['arquivo']}` ({_uma_linha(r['video']['titulo'])})"]
    outros = [m for m in r["motivos"] if m != motivo]
    if outros:
        partes.append("também: " + ", ".join(outros))
    quem = r.get("porNome") or "revisão"
    if DADO_DE_CLIENTE in r["motivos"] and r.get("detalhe"):
        texto = "(texto só no liv.ai: pode ter dado de cliente)"
    elif r.get("detalhe"):
        texto = "“" + _uma_linha(r["detalhe"]) + "”"
    else:
        texto = "(sem texto)"
    return f"- {' · '.join(partes)} · {quem}: {texto} <!-- r:{r['id']} v:{r['video']['id']} em:{r['em']} -->"


def ler_guia(caminho):
    if os.path.exists(caminho):
        return open(caminho, encoding="utf-8").read()
    return ""


def ja_no_guia(texto):
    """ids das decisões que já estão no guia e o instante da mais nova."""
    achados = MARCA.findall(texto)
    ids = {int(a[0]) for a in achados}
    ultima = max((a[2] for a in achados), default=None)
    return ids, ultima


def novas(reprovacoes, ids):
    """Só reprovação que ainda vale; do mesmo vídeo, a mais nova (trocar o texto grava outra), e só se ela não está no guia.
    A mais nova é escolhida antes de olhar o guia: escolhida depois, a antiga voltava na rodada seguinte.
    Ajuste vale sempre (a versão nova pode ter sido aprovada depois, mas o pedido aconteceu); do mesmo vídeo, o mais novo."""
    por_video = {}
    for r in reprovacoes:
        ajuste = r.get("tipo") == "ajustar"
        if not ajuste and r["video"]["estadoAtual"] != "reprovado":
            continue
        chave = (ajuste, r["video"]["id"])
        atual = por_video.get(chave)
        if atual is None or r["id"] > atual["id"]:
            por_video[chave] = r
    return sorted((r for r in por_video.values() if r["id"] not in ids), key=lambda r: r["id"])


def _secoes(texto):
    """Posição (início, fim) de cada seção '## <motivo>' no texto."""
    titulos = [(m.start(), m.group(1).strip()) for m in re.finditer(r"^## (.+)$", texto, re.M)]
    return {t: (ini, titulos[i + 1][0] if i + 1 < len(titulos) else len(texto)) for i, (ini, t) in enumerate(titulos)}


def acrescentar(texto, motivo, linhas):
    secoes = _secoes(texto)
    if motivo not in secoes:
        licao = (LICOES_DE_AJUSTE.get(motivo[len(AJUSTE):]) if motivo.startswith(AJUSTE) else LICOES.get(motivo)) \
            or "Motivo novo no liv.ai: escreva aqui a lição para o editor."
        bloco = f"## {motivo}\n\n**Lição:** {licao}\n\n" + "\n".join(linhas) + "\n"
        return texto.rstrip("\n") + "\n\n" + bloco
    ini, fim = secoes[motivo]
    corpo = texto[ini:fim].rstrip("\n")
    resto = texto[fim:]
    return texto[:ini] + corpo + "\n" + "\n".join(linhas) + "\n" + ("\n" + resto if resto else "")


def placar(texto):
    """Tabela de quantas vezes cada motivo apareceu (refeita a cada rodada, entre os marcadores)."""
    linhas = []
    for motivo, (ini, fim) in _secoes(texto).items():
        achados = MARCA.findall(texto[ini:fim])
        if achados:
            linhas.append((len(achados), max(a[2] for a in achados), motivo))
    if not linhas:
        return "Nenhuma reprovação importada ainda."
    linhas.sort(key=lambda l: (-l[0], l[2]))
    return "\n".join(["| Motivo | Vezes | Última |", "|---|---|---|"] +
                     [f"| {m} | {n} | {_data_br(u)} |" for n, u, m in linhas])


def com_placar(texto):
    return re.sub(r"(<!-- placar -->\n).*?(\n<!-- /placar -->)",
                  lambda m: m.group(1) + placar(texto) + m.group(2), texto, flags=re.S)


def atualizar_guia(texto, entradas):
    """Acrescenta cada reprovação na seção de cada motivo dela (sem atalho: na seção do texto livre); ajuste, na seção
    'Ajuste · <motivo>'."""
    por_motivo = {}
    for r in entradas:
        for motivo in (r["motivos"] or [SEM_ATALHO]):
            por_motivo.setdefault(_secao_da_entrada(r, motivo), []).append(linha_do_guia(r, motivo))
    for motivo, linhas in por_motivo.items():
        texto = acrescentar(texto, motivo, linhas)
    return com_placar(texto), por_motivo


# ------------------------------------------------------------------ principal
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--desde", help="AAAA-MM-DD (padrão: a última do guia menos alguns dias; guia vazio: %s)" % INICIO)
    ap.add_argument("--marca", choices=["LIV", "IMIGRAR"])
    ap.add_argument("--ver", action="store_true", help="só mostra o que entraria no guia")
    ap.add_argument("--url", default=URL_PADRAO)
    ap.add_argument("--guia", default=GUIA)
    ap.add_argument("--criar-chave", action="store_true")
    ap.add_argument("--substituir", action="store_true")
    ap.add_argument("--guardar-chave", action="store_true")
    a = ap.parse_args(argv)

    if a.criar_chave:
        return criar_chave(a.substituir)
    if a.guardar_chave:
        return guardar_chave()

    chave = PLAT.ler_segredo(SERVICO_CHAVEIRO)
    if not chave:
        print("Este computador ainda não tem a chave da aprovação do liv.ai. Guarde com --guardar-chave "
              "(ou crie uma nova com --criar-chave).")
        return 1

    texto = ler_guia(a.guia)
    ids, ultima = ja_no_guia(texto)
    desde = a.desde
    if not desde:
        if ultima:
            instante = datetime.datetime.fromisoformat(ultima.replace("Z", "+00:00"))
            desde = (instante - datetime.timedelta(days=SOBREPOSICAO_DIAS)).date().isoformat()
        else:
            desde = INICIO

    try:
        reprovacoes, _ = buscar(a.url, chave, desde, a.marca)
    except Falha as e:
        print(e)
        return 1

    entradas = novas(reprovacoes, ids)
    if not entradas:
        print(f"Nenhuma reprovação nova desde {desde}.")
        return 0

    novo, por_motivo = atualizar_guia(texto, entradas)
    resumo = ", ".join(f"{m} ({len(l)})" for m, l in sorted(por_motivo.items(), key=lambda x: -len(x[1])))
    n_ajustes = sum(1 for r in entradas if r.get("tipo") == "ajustar")
    tipo = f"{len(entradas) - n_ajustes} reprovação(ões) e {n_ajustes} ajuste(s)" if n_ajustes else f"{len(entradas)} reprovação(ões)"
    print(f"{tipo} novo(s) desde {desde}: {resumo}.")
    for motivo, linhas in por_motivo.items():
        print(f"\n## {motivo}")
        for l in linhas:
            print(MARCA.sub("", l).rstrip())
    if a.ver:
        print("\n(--ver: nada foi gravado)")
        return 0
    with open(a.guia, "w", encoding="utf-8") as f:
        f.write(novo)
    onde = os.path.relpath(a.guia, RAIZ) if os.path.abspath(a.guia).startswith(RAIZ + os.sep) else a.guia
    print(f"\nGuia atualizado: {onde}. Erro que se repete vira regra no editor ou no CLAUDE.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
