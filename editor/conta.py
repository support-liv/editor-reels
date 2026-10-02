#!/usr/bin/env python3
"""Login do time no Supabase do editor (pra usar APIs como a de B-roll sem chave no computador).

    python3 editor/conta.py entrar --email nome@liv.law   # manda o link de acesso; a pessoa só clica no e-mail
    python3 editor/conta.py entrar --codigo               # alternativa: digitar o código de 6 dígitos no terminal
    python3 editor/conta.py status      # quem está logado
    python3 editor/conta.py sair        # apaga a sessão deste Mac

A sessão fica no Chaveiro do macOS ou no Gerenciador de Credenciais do Windows (criptografada), não em arquivo. Ela se renova sozinha; se ficar muito tempo
sem uso, é só entrar de novo. Nenhuma chave de API passa por aqui: elas ficam no servidor.
"""
import getpass, http.server, json, os, subprocess, sys, time, urllib.error, urllib.parse, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import plataforma as P
CFG = json.load(open(os.path.join(AQUI, "supabase_config.json")))
SERVICO_CHAVEIRO = "editor-reels-supabase"


def _contexto_ssl():
    """certificados: o Python do python.org no Mac vem sem eles; usa o certifi quando existir."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL = _contexto_ssl()


def _req(caminho, corpo=None, token=None, metodo="POST"):
    cab = {"apikey": CFG["publishable_key"], "Content-Type": "application/json"}
    if token:
        cab["Authorization"] = f"Bearer {token}"
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(CFG["url"] + caminho, data=dados, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(r, timeout=60, context=SSL) as resp:
            txt = resp.read().decode()
            return resp.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"erro": txt}


def _guardar(sessao):
    s = {k: sessao[k] for k in ("access_token", "refresh_token", "expires_at") if k in sessao}
    s["email"] = sessao.get("user", {}).get("email") or sessao.get("email")
    P.guardar_segredo(SERVICO_CHAVEIRO, json.dumps(s))     # Chaveiro (Mac) / Gerenciador de Credenciais (Windows)


def _ler():
    v = P.ler_segredo(SERVICO_CHAVEIRO)
    return json.loads(v) if v else None


def token():
    """access token válido (renova pelo refresh token quando está perto de vencer). None se não há login."""
    s = _ler()
    if not s:
        return None
    if s.get("expires_at", 0) - time.time() > 120:
        return s["access_token"]
    st, nova = _req("/auth/v1/token?grant_type=refresh_token", {"refresh_token": s["refresh_token"]})
    if st != 200 or "access_token" not in nova:
        return None
    nova.setdefault("email", s.get("email"))
    _guardar(nova)
    return nova["access_token"]


PORTA_LINK = 8723          # o link do e-mail volta pra cá (cadastrado em Auth → URL Configuration → Redirect URLs)

PAGINA = """<!doctype html><meta charset="utf-8"><title>Editor</title>
<body style="font-family:-apple-system,sans-serif;padding:48px"><h2 id="m">Conectando…</h2>
<script>
const h = location.hash.slice(1);
fetch("/sessao", {method: "POST", body: h}).then(r => r.text()).then(t => { document.getElementById("m").textContent = t; });
</script></body>"""


def entrar_por_link(email, espera=900):
    """manda o link de acesso e espera a pessoa clicar: o link volta pro 127.0.0.1 com a sessão (fica só neste Mac)."""
    pronto = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(PAGINA.encode())

        def do_POST(self):
            corpo = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode()
            q = dict(urllib.parse.parse_qsl(corpo))
            ok = "access_token" in q and "refresh_token" in q
            if ok:
                q["expires_at"] = int(q.get("expires_at") or time.time() + int(q.get("expires_in", 3600)))
                q["email"] = email
                _guardar(q); pronto["ok"] = True
            self.send_response(200); self.send_header("Content-Type", "text/plain; charset=utf-8"); self.end_headers()
            self.wfile.write(("Pronto, pode fechar esta aba." if ok else "Link inválido ou expirado. Peça um novo.").encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", PORTA_LINK), H)
    destino = urllib.parse.quote(f"http://127.0.0.1:{PORTA_LINK}/", safe="")
    st, r = _req(f"/auth/v1/otp?redirect_to={destino}", {"email": email, "create_user": True})
    if st not in (200, 204):
        sys.exit(f"Não deu para enviar o link: {r.get('msg') or r.get('message') or r.get('error_description') or r}")
    print(f"Link de acesso enviado para {email}. Esperando o clique no e-mail…", flush=True)
    fim = time.time() + espera
    srv.timeout = 5
    while not pronto and time.time() < fim:
        srv.handle_request()
    srv.server_close()
    if not pronto:
        sys.exit("O link não foi clicado a tempo. Peça um novo.")
    print(f"Pronto: {email} conectado neste Mac.")


def entrar():
    if "--email" in sys.argv:
        return entrar_por_link(sys.argv[sys.argv.index("--email") + 1].strip().lower())
    email = input("E-mail da empresa: ").strip().lower()
    st, r = _req("/auth/v1/otp", {"email": email, "create_user": True})
    if st not in (200, 204):
        sys.exit(f"Não deu para enviar o código: {r.get('msg') or r.get('message') or r.get('error_description') or r}")
    print(f"Mandei um código de 6 dígitos para {email} (confira o spam).")
    codigo = getpass.getpass("Código: ").strip()
    st, sessao = _req("/auth/v1/verify", {"type": "email", "email": email, "token": codigo})
    if st != 200 or "access_token" not in sessao:
        sys.exit(f"Código não aceito: {sessao.get('msg') or sessao.get('message') or sessao}")
    _guardar(sessao)
    print(f"Pronto: {email} conectado neste Mac.")


def status():
    s = _ler()
    if not s:
        print("Ninguém conectado. Rode: python3 editor/conta.py entrar")
    else:
        print(f"Conectado: {s.get('email')}" + ("" if token() else " (sessão expirada: entre de novo)"))


def sair():
    P.apagar_segredo(SERVICO_CHAVEIRO)
    print("Sessão apagada deste Mac.")


if __name__ == "__main__":
    {"entrar": entrar, "status": status, "sair": sair}.get((sys.argv[1:] or ["status"])[0], status)()
