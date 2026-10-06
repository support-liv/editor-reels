#!/usr/bin/env python3
"""Servidor MCP do Editor Reels (LIV / Imigrar): as ferramentas do editor como "botões" para o Claude.

Roda no computador da pessoa (Mac ou Windows), por stdio. Os vídeos nunca saem do computador (só os prontos,
quando a pessoa pede para publicar no YouTube). Tarefas demoradas (render, transcrição, instalação, envio) rodam
em segundo plano: a ferramenta devolve um número de tarefa e o Claude acompanha com `ver_tarefa`.
"""
import json, os, re, shutil, subprocess, sys, threading, time, uuid

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDITOR = os.path.join(RAIZ, "editor")
sys.path.insert(0, EDITOR)
import plataforma as PLAT  # noqa: E402

from mcp.server.mcpserver import MCPServer  # noqa: E402

PY = sys.executable
INSTRUCOES = """Editor de vídeos da LIV e da Imigrar. Antes de editar, siga a skill `editor-de-videos` (fluxo guiado:
analisar o vídeo, contar o que dá para fazer, perguntar o que a pessoa quer com opções, mostrar prévia, entregar e
oferecer o próximo passo). Fale sempre em português simples, sem termos técnicos. Os vídeos prontos ficam na Mesa,
pasta "Editor Reels". Tarefas demoradas devolvem um número: acompanhe com ver_tarefa até terminar."""

app = MCPServer(name="editor-reels", title="Editor Reels (LIV / Imigrar)", instructions=INSTRUCOES, version="1.0.0")

# ------------------------------------------------------------------ tarefas em segundo plano
TAREFAS = {}
PASTA_TAREFAS = PLAT.pasta_cache("tarefas")


def _tarefa(titulo, cmd, cwd=RAIZ):
    tid = time.strftime("%H%M%S") + "-" + uuid.uuid4().hex[:4]
    log = os.path.join(PASTA_TAREFAS, f"{tid}.log")
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", HYPERFRAMES_NO_TELEMETRY="1")
    f = open(log, "w", encoding="utf-8")
    p = subprocess.Popen(cmd, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=env)
    TAREFAS[tid] = {"titulo": titulo, "proc": p, "log": log, "inicio": time.time(), "cmd": cmd}
    threading.Thread(target=lambda: (p.wait(), f.close()), daemon=True).start()
    return tid


def _resumo_tarefa(tid):
    t = TAREFAS.get(tid)
    if not t:
        return {"erro": f"tarefa {tid} não encontrada (o servidor pode ter reiniciado)"}
    rc = t["proc"].poll()
    txt = open(t["log"], encoding="utf-8", errors="replace").read() if os.path.exists(t["log"]) else ""
    linhas = [ln for ln in txt.splitlines() if ln.strip()]
    arquivos = re.findall(r"(?:pronto|Pronto|programado|enviado)[^\n]*?((?:/|[A-Za-z]:\\)[^\s|]+\.(?:mp4|mov|png|md|json))", txt)
    return {"tarefa": tid, "titulo": t["titulo"],
            "situacao": "rodando" if rc is None else ("concluída" if rc == 0 else "falhou"),
            "minutos": round((time.time() - t["inicio"]) / 60, 1),
            "arquivos": list(dict.fromkeys(arquivos)), "ultimas_linhas": linhas[-12:]}


@app.tool()
def ver_tarefa(tarefa: str) -> dict:
    """Mostra como está uma tarefa demorada (render, transcrição, instalação, envio): rodando, concluída ou falhou,
    os arquivos gerados e as últimas mensagens. Chame de novo depois de alguns segundos enquanto estiver rodando."""
    return _resumo_tarefa(tarefa)


@app.tool()
def listar_tarefas() -> list:
    """Lista as tarefas desta sessão e a situação de cada uma."""
    return [_resumo_tarefa(t) for t in TAREFAS]


# ------------------------------------------------------------------ instalação e situação
def _lfs_ok():
    arq = os.path.join(RAIZ, "assets", "trilhas", "corporativo__skylines-anno-domini-beats__99bpm__A-maior.mp3")
    try:
        with open(arq, "rb") as f:
            return not f.read(40).startswith(b"version https://git-lfs")
    except OSError:
        return False


@app.tool()
def situacao() -> dict:
    """Confere se o editor está pronto neste computador: programas instalados, arquivos grandes baixados,
    teste piloto feito, login da equipe e pasta dos vídeos prontos. Use no começo, antes de editar."""
    marcador = os.path.join(PLAT.pasta_dados(), "instalado.txt")
    login = None
    try:
        import conta
        s = conta._ler()
        login = s.get("email") if s else None
    except Exception:
        pass
    falta = [n for n, ok in (("ffmpeg", shutil.which("ffmpeg")), ("node (animações)", shutil.which("node")),
                             ("arquivos grandes (git lfs pull)", _lfs_ok())) if not ok]
    atual = {"ok": "atualizado agora", "sem-conexao": "sem internet: usando a última versão baixada",
             "acesso-vencido": "AS ATUALIZAÇÕES PARARAM: o acesso ao GitHub venceu. Peça um acesso novo ao administrador "
                               "e guarde no gerenciador de senhas do Git (o editor continua funcionando na versão atual)."}
    return {"atualizacao": atual.get(os.environ.get("EDITOR_REELS_ATUALIZACAO", ""), "não verificada"),
            "sistema": "Windows" if PLAT.WIN else ("Mac" if PLAT.MAC else "Linux"),
            "pronto": not falta and os.path.exists(marcador), "falta": falta,
            "teste_piloto_feito": os.path.exists(marcador),
            "login_da_equipe": login or "não conectado (só precisa para buscar imagens externas)",
            "pasta_dos_videos_prontos": PLAT.pasta_renders()}


@app.tool()
def instalar() -> dict:
    """Instala tudo que o editor precisa neste computador (programas, pacotes, modelo de transcrição, arquivos
    grandes). Demora na primeira vez. Devolve uma tarefa: acompanhe com ver_tarefa. No Windows, avise a pessoa
    para clicar em "Sim" se aparecer janela de permissão."""
    if PLAT.WIN:
        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-File", os.path.join(RAIZ, "setup.ps1")]
    else:
        cmd = ["bash", os.path.join(RAIZ, "setup.sh")]
    return {"tarefa": _tarefa("instalação", cmd)}


@app.tool()
def teste_piloto() -> dict:
    """Testa, peça por peça, se o editor funciona neste computador (12 testes). Na primeira vez depois de instalar.
    Devolve uma tarefa; no fim, o relatório fica em piloto/. Se tudo passar, o editor marca como instalado."""
    cmd = [PY, "-c", "import runpy,sys,os; sys.argv=['teste_piloto.py']; runpy.run_path(r'%s', run_name='__main__')"
           % os.path.join(EDITOR, "teste_piloto.py")]
    tid = _tarefa("teste piloto", cmd)

    def marca():
        TAREFAS[tid]["proc"].wait()
        txt = open(TAREFAS[tid]["log"], encoding="utf-8", errors="replace").read()
        m = re.search(r"(\d+)/(\d+) ok", txt)
        if m and m.group(1) == m.group(2):
            open(os.path.join(PLAT.pasta_dados(), "instalado.txt"), "w").write(time.strftime("%Y-%m-%d %H:%M"))
    threading.Thread(target=marca, daemon=True).start()
    return {"tarefa": tid}


# ------------------------------------------------------------------ entender o vídeo
@app.tool()
def analisar_video(caminho: str) -> dict:
    """Primeira olhada num vídeo: duração, resolução, orientação, se é HDR do iPhone, se tem áudio, quantos rostos
    aparecem e 6 quadros salvos (abra as imagens para ver o conteúdo). Use antes de propor a edição."""
    caminho = os.path.expanduser(caminho)
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                   "format=duration:stream=codec_type,width,height,r_frame_rate,color_transfer:stream_side_data=rotation",
                                   "-of", "json", caminho], capture_output=True, text=True).stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), {})
    rot = next((int(sd.get("rotation", 0)) for sd in v.get("side_data_list", []) or [] if "rotation" in sd), 0)
    w, h = v.get("width", 0), v.get("height", 0)
    if abs(rot) % 180 == 90:
        w, h = h, w
    dur = float(d["format"]["duration"])
    pasta = PLAT.pasta_cache("analise", re.sub(r"\W+", "_", os.path.basename(caminho))[:50])
    quadros = []
    for k in range(6):
        t = dur * (k + 0.5) / 6
        out = os.path.join(pasta, f"quadro_{k + 1}_{int(t)}s.jpg")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", caminho, "-frames:v", "1",
                        "-vf", "scale=-2:540", out])
        if os.path.exists(out):
            quadros.append(out)
    rostos = PLAT.rostos(quadros) if quadros else []
    return {"duracao_s": round(dur, 1), "resolucao": f"{w}x{h}",
            "orientacao": "vertical" if h > w else "horizontal",
            "hdr_iphone": v.get("color_transfer") in ("arib-std-b67", "smpte2084"),
            "tem_audio": any(s["codec_type"] == "audio" for s in d["streams"]),
            "rostos_por_quadro": [len(r) for r in rostos], "quadros": quadros}


@app.tool()
def transcrever(caminho: str) -> dict:
    """Transcreve a fala do vídeo no próprio computador (Whisper), com o tempo de cada palavra. Demora alguns
    minutos em vídeo longo: devolve uma tarefa. O resultado fica em editor/transcricoes/<nome do vídeo>.json (palavras com tempo)."""
    return {"tarefa": _tarefa("transcrição", [PY, os.path.join(EDITOR, "transcrever_lote.py"), os.path.expanduser(caminho)])}


# ------------------------------------------------------------------ editar
OPCOES_VIDEO = {"marca": "--marca", "gancho": "--gancho", "cta": "--cta", "trechos": "--trechos", "nome": "--nome",
                "layout": "--layout", "cta_animado": "--cta-animado", "cta_rotulo": "--cta-rotulo", "pessoa": "--pessoa",
                "cima": "--cima", "cor_caixa": "--cor-caixa", "cauda": "--cauda"}


@app.tool()
def criar_video(caminho: str, marca: str, nome: str = "", gancho: str = "", cta: str = "", trechos: str = "",
                layout: str = "", cta_animado: str = "", projeto: str = "", opcoes_extras: list[str] | None = None) -> dict:
    """Cria um vídeo (short vertical com legenda, gancho e CTA, ou corte longo do YouTube com layout="youtube").
    marca: "liv" ou "imigrar". trechos: faixas do original em segundos, ex. "12.5-40.2,55-71". layout: vazio
    (vertical seguindo o rosto), "dividido" (duas pessoas), "quadro", "youtube" (corte longo 16:9).
    cta_animado: palavra-chave do Instagram (ex. "GREENCARD"). projeto: nome da subpasta em Mesa/Editor Reels.
    opcoes_extras: outras opções do editor (ex. ["--dinamico", "--sem-legenda"]). Devolve uma tarefa."""
    args = {"marca": marca, "nome": nome, "gancho": gancho, "cta": cta, "trechos": trechos, "layout": layout,
            "cta_animado": cta_animado}
    cmd = [PY, os.path.join(EDITOR, "editor_reels.py"), os.path.expanduser(caminho)]
    for k, v in args.items():
        if v:
            cmd += [OPCOES_VIDEO[k], v]
    cmd += ["--saida", PLAT.pasta_renders(projeto or "prontos")] + list(opcoes_extras or [])
    return {"tarefa": _tarefa(f"vídeo {nome or os.path.basename(caminho)}", cmd)}


@app.tool()
def criar_anuncio(roteiro: str, versao: str = "A", previa_ate_segundos: float = 0, quadros: str = "") -> dict:
    """Monta um anúncio no formato dinâmico (texto atrás da pessoa, imagens com lettering, transições, legenda,
    CTA) a partir de um roteiro .py (veja projetos/ads_liv/ad2.py). versao: "A" (texto atrás) ou "B" (tela
    dividida no gancho). Para validar antes: previa_ate_segundos=3 e quadros="1.1,2.5" geram só imagens de
    conferência. Devolve uma tarefa."""
    cmd = [PY, os.path.join(EDITOR, "ads_dinamico.py"), os.path.expanduser(roteiro), "--versao", versao]
    if previa_ate_segundos:
        cmd += ["--ate", str(previa_ate_segundos)]
    if quadros:
        cmd += ["--quadros", quadros]
    return {"tarefa": _tarefa(f"anúncio {os.path.basename(roteiro)} ({versao})", cmd)}


# ------------------------------------------------------------------ imagens e música
@app.tool()
def buscar_imagens_externas(busca: str, orientacao: str = "portrait", quantidade: int = 8) -> list:
    """Busca vídeos de banco de imagens (Pexels, uso comercial liberado) pelo servidor da equipe. Precisa do login
    da equipe. Escreva a busca em inglês (ex. "miami skyline aerial"). Na LIV: imagens formais, profissionais e de
    sonho americano; confira os quadros antes de usar (o título do banco às vezes erra o lugar)."""
    import broll_api
    return [{"id": v["id"], "duracao_s": v["duracao"], "autor": v["autor"], "pagina": v["pagina"]}
            for v in broll_api.buscar(busca, orientacao, quantidade)]


@app.tool()
def baixar_imagem_externa(busca: str, id: int) -> dict:
    """Baixa um vídeo do banco de imagens (o id vem de buscar_imagens_externas, com a mesma busca)."""
    import broll_api
    v = next((x for x in broll_api.buscar(busca) if x["id"] == id), None)
    if not v:
        return {"erro": "não achei esse id nessa busca"}
    return {"arquivo": broll_api.baixar(v), "autor": v["autor"]}


@app.tool()
def buscar_no_estoque_liv(termos: list[str]) -> list:
    """Procura no estoque interno de vídeos da LIV (Dra. Lívia, equipe, escritório, processo). Só para vídeos da
    LIV; quando a fala é processo, equipe ou atendimento, prefira o estoque ao banco externo.
    Ex.: ["processo", "vertical"]."""
    cat = json.load(open(os.path.join(RAIZ, "assets", "estoque_liv", "catalogo.json"), encoding="utf-8"))
    t = [x.lower() for x in termos]
    return [dict(v, caminho=os.path.join(RAIZ, "assets", "estoque_liv", v["arquivo"])) for v in cat["videos"]
            if all(x in v["arquivo"].lower().replace("-", " ") for x in t)]


@app.tool()
def sugerir_trilha(clima: str, marca: str, anuncio: bool = False, duracao_s: float = 0) -> list:
    """Sugere trilhas do banco da equipe. clima: corporativo, inspirador, emocional, calmo, luxo, epico, alegre,
    energetico, tenso, polemico. marca: liv ou imigrar. anuncio=True tira as que não podem ir em anúncio pago.
    Sempre pergunte antes se a pessoa quer trilha, e passe pelo agente auditor-de-trilha antes de usar."""
    import trilhas
    return [{"arquivo": t["arquivo"], "caminho": os.path.join(trilhas.PASTA, t["arquivo"]), "bpm": t["bpm"],
             "tom": t["tom"], "climas": t["climas"], "licenca": t["licenca"]}
            for t in trilhas.sugerir(clima, marca, anuncio, duracao_s or None)]


@app.tool()
def colocar_trilha(video: str, trilha: str, inicio_na_musica_s: float = 0, quanto_abaixo_da_fala_db: float = 0) -> dict:
    """Coloca a trilha por baixo da fala (sempre mais baixa, e abaixa mais quando a pessoa fala). Gera
    <video>_com_trilha.mp4 ao lado do vídeo. inicio_na_musica_s pula introdução fraca da música."""
    import trilhas
    video = os.path.expanduser(video)
    saida = os.path.splitext(video)[0] + "_com_trilha.mp4"
    s, voz, mus, g = trilhas.mixar(video, os.path.expanduser(trilha), saida, inicio_na_musica_s, quanto_abaixo_da_fala_db or None)
    return {"arquivo": s, "fala_lufs": voz, "ganho_trilha_db": round(g, 1)}


# ------------------------------------------------------------------ login da equipe
@app.tool()
def entrar_na_conta_da_equipe(email: str) -> dict:
    """Login da equipe (só para buscar imagens externas). Manda um link para o e-mail da empresa; a pessoa clica e
    pronto. Devolve uma tarefa que termina quando ela clicar (até 15 minutos)."""
    return {"tarefa": _tarefa("login da equipe", [PY, os.path.join(EDITOR, "conta.py"), "entrar", "--email", email.strip().lower()])}


# ------------------------------------------------------------------ YouTube
@app.tool()
def youtube_ultima_data(canal: str) -> dict:
    """Data do último short programado ou publicado no canal (liv ou imigrar), lida do YouTube Studio."""
    r = subprocess.run([PY, os.path.join(EDITOR, "studio.py"), "ultima", "--canal", canal], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=300)
    return {"ultima_data": r.stdout.strip().splitlines()[-1] if r.stdout.strip() else None, "erro": r.stderr[-300:] or None}


@app.tool()
def youtube_publicar(publicacao_json: str, canal: str, tipo: str = "short", agendar: bool = True,
                     so_previa: bool = True, inicio: str = "", ids: list[str] | None = None) -> dict:
    """Publica no YouTube pelo Studio, em segundo plano, com título, descrição no padrão, tags e marcações.
    SEMPRE rode antes com so_previa=True e mostre à pessoa a lista (títulos e datas); só depois do "ok" rode com
    so_previa=False. LIV: shorts programados um por dia às 12h a partir do último; longos sobem privados
    (tipo="longo", agendar=False). Imigrar: pergunte a data e passe inicio="AAAA-MM-DD". Devolve uma tarefa."""
    cmd = [PY, os.path.join(EDITOR, "studio.py"), "lote", os.path.expanduser(publicacao_json), "--canal", canal, "--tipo", tipo]
    if agendar and tipo == "short":
        cmd.append("--agendar")
    if inicio:
        cmd += ["--inicio", inicio]
    if ids:
        cmd += ["--so"] + ids
    if so_previa:
        cmd.append("--plano")
    return {"tarefa": _tarefa(("prévia do " if so_previa else "") + f"envio ao YouTube ({canal})", cmd)}


@app.tool()
def youtube_abrir_login() -> dict:
    """Abre a janela do YouTube Studio para a pessoa fazer login com a conta dela (uma vez por computador)."""
    r = subprocess.run([PY, os.path.join(EDITOR, "studio.py"), "abrir"], capture_output=True, text=True, timeout=120)
    return {"mensagem": (r.stdout or r.stderr).strip()[-300:]}


@app.tool()
def pasta_dos_videos_prontos(projeto: str = "") -> str:
    """Caminho da pasta onde ficam os vídeos prontos (Mesa > Editor Reels > projeto)."""
    return PLAT.pasta_renders(projeto) if projeto else PLAT.pasta_renders()


def main():
    try:
        PLAT.limpar_temporarios(avisar=False)
    except Exception:
        pass
    app.run("stdio")


if __name__ == "__main__":
    main()
