#!/usr/bin/env python3
"""Envio de shorts pelo YouTube Studio no navegador, com o login de quem usa (editor ou administrador do canal).

Não usa a API: vale a permissão que a pessoa já tem no Studio. O Claude roda os comandos; a pessoa só faz login
uma vez na janela "Chrome do editor" (a senha é digitada por ela, nunca passa pelo Claude).

    python3 editor/studio.py abrir                       # abre o Chrome do editor (login fica salvo nele)
    python3 editor/studio.py status                      # quem está logado e quais canais aparecem
    python3 editor/studio.py fechar                      # fecha a janela; os envios passam a rodar sem janela
    python3 editor/studio.py enviar VIDEO.mp4 --canal liv --titulo "..." --descricao "..." --tags "a,b"
    python3 editor/studio.py lote projetos/live80/publicacao.json --canal liv --agendar --plano   # confere antes
    python3 editor/studio.py lote projetos/live80/publicacao.json --canal liv --agendar [--so S2]

Sem --agendar o vídeo fica privado; com ele, 1 por dia às 12h a partir do dia seguinte ao último short do canal.
Sempre marca: não é para crianças, sem promoção paga, sem conteúdo alterado/sintético. Descrição pelo modelo do
canal (editor/descricoes.py). Canais e IDs em editor/canais_youtube.json.
"""
import argparse, datetime as dt, json, os, re, subprocess, sys, time

AQUI = os.path.dirname(os.path.abspath(__file__))
PERFIL = os.path.expanduser("~/Library/Application Support/editor-reels/chrome-studio")
PORTA = 9333
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CANAIS = os.path.join(AQUI, "canais_youtube.json")
sys.path.insert(0, AQUI)
import descricoes


def canais():
    return json.load(open(CANAIS)) if os.path.exists(CANAIS) else {}


UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/{v} Safari/537.36")


def aberto():
    import urllib.request
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/json/version", timeout=2)
        return True
    except Exception:
        return False


def abrir():
    """Chrome comum (sem marca de automação, o Google aceita o login), com perfil próprio e porta local de controle."""
    if aberto():
        print("O Chrome do editor já está aberto."); return
    os.makedirs(PERFIL, exist_ok=True)
    subprocess.Popen([CHROME, f"--user-data-dir={PERFIL}", f"--remote-debugging-port={PORTA}",
                      "--remote-debugging-address=127.0.0.1", "--no-first-run", "--no-default-browser-check",
                      "https://studio.youtube.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(30):
        if aberto():
            break
        time.sleep(0.5)
    print("Chrome do editor aberto no YouTube Studio. Se pedir login, a pessoa entra com a conta dela.")


def _versao_chrome():
    r = subprocess.run([CHROME, "--version"], capture_output=True, text=True).stdout
    m = re.search(r"([\d.]+)", r)
    return m.group(1) if m else "140.0.0.0"


def abrir_fundo():
    """o mesmo perfil, sem janela: o envio roda em segundo plano e a pessoa segue usando o Mac."""
    subprocess.Popen([CHROME, "--headless=new", f"--user-data-dir={PERFIL}", f"--remote-debugging-port={PORTA}",
                      "--remote-debugging-address=127.0.0.1", "--no-first-run", "--no-default-browser-check",
                      f"--user-agent={UA.format(v=_versao_chrome())}", "--window-size=1440,1000", "about:blank"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(40):
        if aberto():
            return
        time.sleep(0.5)
    sys.exit("Não consegui abrir o Chrome em segundo plano.")


def fechar():
    """fecha o Chrome do editor (o login continua salvo no perfil)."""
    if not aberto():
        return
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    try:
        pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORTA}").close()
    finally:
        pw.stop()
    for _ in range(20):
        if not aberto():
            break
        time.sleep(0.5)
    time.sleep(1)


def conectar():
    """usa o Chrome do editor se a janela estiver aberta; senão abre um invisível (segundo plano)."""
    from playwright.sync_api import sync_playwright
    if not aberto():
        abrir_fundo()
    pw = sync_playwright().start()
    nav = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORTA}")
    return pw, nav, nav.contexts[0]


def status():
    """se está logado e quais canais a conta enxerga (nome e ID), pra preencher canais_youtube.json."""
    pw, nav, ctx = conectar()
    p = ctx.new_page()
    try:
        p.goto("https://www.youtube.com/account", wait_until="domcontentloaded")
        p.wait_for_timeout(3000)
        if "accounts.google.com" in p.url:
            print("Não logado: abra o Chrome do editor (studio.py abrir) e faça login."); return
        p.goto("https://www.youtube.com/channel_switcher", wait_until="domcontentloaded")
        p.wait_for_timeout(5000)
        lista = p.evaluate("""() => [...document.querySelectorAll('ytd-account-item-renderer, ytd-channel-switcher-page-renderer a')]
            .map(e => ({nome: (e.querySelector('#channel-title, #account-name, yt-formatted-string')||e).innerText.trim(),
                        link: e.href || (e.querySelector('a')||{}).href || ''}))
            .filter(x => x.nome)""")
        print("logado. Canais desta conta:")
        for c in lista:
            print(f"  {c['nome']}  {c['link']}")
    finally:
        p.close(); pw.stop()


def _preencher(campo, texto):
    campo.click()
    campo.press("Meta+A")
    campo.press("Backspace")
    if texto:
        campo.type(texto, delay=5)


MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]


def _data_pt(d):
    """formato do campo de data do Studio em português: "6 de out. de 2026"."""
    return f"{d.day} de {MESES[d.month - 1]}. de {d.year}"


def ultima_data(canal, aba="short"):
    """data mais recente entre os vídeos da aba (programados ou publicados), lida da lista do Studio."""
    cid = canais()[canal]["id"]
    pw, nav, ctx = conectar()
    p = ctx.new_page()
    try:
        p.goto(f"https://studio.youtube.com/channel/{cid}/videos/{aba}", wait_until="domcontentloaded")
        p.wait_for_selector("ytcp-video-row", timeout=60000)
        p.wait_for_timeout(2500)
        datas = p.evaluate("() => [...document.querySelectorAll('ytcp-video-row .tablecell-date')].map(e => e.innerText)")
    finally:
        p.close(); pw.stop()
    achadas = []
    for t in datas:
        m = re.search(r"(\d{1,2}) de (\w{3})\.? de (\d{4})", t)
        if m and m.group(2) in MESES:
            achadas.append(dt.date(int(m.group(3)), MESES.index(m.group(2)) + 1, int(m.group(1))))
    return max(achadas) if achadas else None


def enviar(video, canal, titulo, descricao, tags, publicar_em=None, log=print):
    """sobe pelo Studio. publicar_em (datetime no fuso de São Paulo) programa; sem ele, fica privado."""
    cid = canais().get(canal, {}).get("id")
    if not cid:
        sys.exit(f"canal '{canal}' sem ID em {CANAIS}")
    video = os.path.abspath(os.path.expanduser(video))
    pw, nav, ctx = conectar()
    p = ctx.new_page()
    try:
        p.goto(f"https://studio.youtube.com/channel/{cid}/videos/upload?d=ud", wait_until="domcontentloaded")
        if "accounts.google.com" in p.url:
            sys.exit("O Chrome do editor não está logado: faça login nele e tente de novo.")
        p.wait_for_selector("input[type=file]", state="attached", timeout=60000)
        p.set_input_files("input[type=file]", video)
        log("  arquivo enviado ao Studio, preenchendo os dados…")
        p.wait_for_selector("#title-textarea #textbox", timeout=120000)
        p.wait_for_timeout(1500)
        _preencher(p.locator("#title-textarea #textbox"), titulo)
        _preencher(p.locator("#description-textarea #textbox"), descricao)
        p.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']").click()
        p.locator("#toggle-button").click()                          # "Mostrar mais"
        p.locator("tp-yt-paper-radio-button[name='VIDEO_PAID_PRODUCT_PLACEMENT_NO']").click(timeout=20000)
        p.locator("tp-yt-paper-radio-button[name='VIDEO_HAS_ALTERED_CONTENT_NO']").click(timeout=20000)
        if tags:
            campo = p.locator("#tags-container input#text-input")
            campo.wait_for(timeout=20000)
            campo.click()
            campo.type(",".join(tags) + ",", delay=5)
        for _ in range(3):                                           # Detalhes → Elementos → Verificações → Visibilidade
            p.locator("#next-button").click()
            p.wait_for_timeout(1200)
        if publicar_em:
            p.locator("#second-container-expand-button").click()
            p.wait_for_timeout(800)
            p.locator("#datepicker-trigger").click()
            data = p.locator("ytcp-date-picker tp-yt-paper-input input").first
            data.fill(_data_pt(publicar_em)); data.press("Enter")
            p.wait_for_timeout(600)
            hora = p.locator("#time-of-day-container input").first
            hora.fill(publicar_em.strftime("%H:%M")); hora.press("Enter")
            p.wait_for_timeout(600)
            vista = p.locator("#datepicker-trigger").inner_text().strip(), hora.input_value().strip()
            if vista != (_data_pt(publicar_em), publicar_em.strftime("%H:%M")):
                raise RuntimeError(f"o Studio não aceitou a data: mostra {vista}")
        else:
            p.locator("tp-yt-paper-radio-button[name='PRIVATE']").click()
        link = p.locator("ytcp-video-info a, .video-url-fadeable a").first.get_attribute("href", timeout=30000)
        # espera o envio do arquivo terminar antes de fechar (fechar no meio cancela o upload)
        for _ in range(900):
            txt = (p.locator("ytcp-video-upload-progress .progress-label").first.inner_text(timeout=5000) or "").lower()
            if not re.search(r"enviando|uploading|\d+\s*%", txt):
                break
            p.wait_for_timeout(2000)
        p.locator("#done-button").click()
        p.wait_for_timeout(4000)
        return link
    except Exception:
        os.makedirs(os.path.expanduser("~/Library/Caches/editor-reels"), exist_ok=True)
        p.screenshot(path=os.path.expanduser("~/Library/Caches/editor-reels/studio_erro.png"))
        raise
    finally:
        p.close(); pw.stop()


def plano(cfg, canal, agendar, inicio=None, hora="12:00", tipo="short"):
    """lista (item, descrição, horário) do lote. Agendando: 1 por dia, a partir do dia seguinte ao último do canal."""
    itens = cfg["shorts"]
    horarios = [None] * len(itens)
    if agendar:
        if inicio:
            d0 = dt.date.fromisoformat(inicio)
        else:
            ult = ultima_data(canal, "short" if tipo == "short" else "upload")
            d0 = (ult or dt.date.today()) + dt.timedelta(days=1)
        hh, mm = map(int, hora.split(":"))
        horarios = [dt.datetime.combine(d0 + dt.timedelta(days=i), dt.time(hh, mm)) for i in range(len(itens))]
    return [(s, descricoes.montar(canal, s, tipo), h) for s, h in zip(itens, horarios)]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("abrir"); sub.add_parser("status"); sub.add_parser("fechar")
    u = sub.add_parser("ultima"); u.add_argument("--canal", required=True); u.add_argument("--aba", default="short")
    e = sub.add_parser("enviar"); e.add_argument("video"); e.add_argument("--canal", required=True)
    e.add_argument("--titulo", required=True); e.add_argument("--descricao", default=""); e.add_argument("--tags", default="")
    e.add_argument("--publicar-em", help="AAAA-MM-DDTHH:MM no fuso de São Paulo")
    l = sub.add_parser("lote"); l.add_argument("json"); l.add_argument("--canal", required=True)
    l.add_argument("--so", nargs="*", help="só estes ids (ex.: S2 S3)")
    l.add_argument("--agendar", action="store_true", help="programa 1 por dia a partir do dia seguinte ao último do canal")
    l.add_argument("--inicio", help="AAAA-MM-DD (em vez de ler o último do canal)"); l.add_argument("--hora", default="12:00")
    l.add_argument("--tipo", default="short", choices=["short", "longo"])
    l.add_argument("--plano", action="store_true", help="só mostra o que vai subir (não envia)")
    a = ap.parse_args()
    if a.cmd == "abrir":
        abrir()
    elif a.cmd == "status":
        status()
    elif a.cmd == "fechar":
        fechar(); print("Chrome do editor fechado (login salvo).")
    elif a.cmd == "ultima":
        print(ultima_data(a.canal, a.aba))
    elif a.cmd == "enviar":
        quando = dt.datetime.fromisoformat(a.publicar_em) if a.publicar_em else None
        print("enviado:", enviar(a.video, a.canal, a.titulo, a.descricao,
                                 [t.strip() for t in a.tags.split(",") if t.strip()], quando))
    else:
        cfg = json.load(open(os.path.expanduser(a.json)))
        if a.so:
            cfg["shorts"] = [s for s in cfg["shorts"] if s["id"] in a.so]
        for s, desc, h in plano(cfg, a.canal, a.agendar, a.inicio, a.hora, a.tipo):
            quando = h.strftime("%d/%m/%Y %H:%M") if h else "privado"
            if a.plano:
                print(f"=== {s['id']} | {quando} | {s['titulo']}\n{desc}\ntags: {', '.join(s.get('tags', []))}\n", flush=True)
                continue
            print(f"{s['id']}: enviando ({quando})…", flush=True)
            print(f"{s['id']}: {'programado ' + quando if h else 'enviado (privado)'} "
                  f"{enviar(s['video'], a.canal, s['titulo'], desc, s.get('tags', []), h)}", flush=True)


if __name__ == "__main__":
    main()
