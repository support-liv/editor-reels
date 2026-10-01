#!/usr/bin/env python3
"""Login do time no Supabase do editor (pra usar APIs como a de B-roll sem chave no computador).

    python3 editor/conta.py entrar      # pede o e-mail da empresa, manda um código de 6 dígitos, você cola aqui
    python3 editor/conta.py status      # quem está logado
    python3 editor/conta.py sair        # apaga a sessão deste Mac

A sessão fica no Chaveiro do macOS (criptografada), não em arquivo. Ela se renova sozinha; se ficar muito tempo
sem uso, é só entrar de novo. Nenhuma chave de API passa por aqui: elas ficam no servidor.
"""
import getpass, json, os, subprocess, sys, time, urllib.error, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
CFG = json.load(open(os.path.join(AQUI, "supabase_config.json")))
SERVICO_CHAVEIRO = "editor-reels-supabase"


def _req(caminho, corpo=None, token=None, metodo="POST"):
    cab = {"apikey": CFG["publishable_key"], "Content-Type": "application/json"}
    if token:
        cab["Authorization"] = f"Bearer {token}"
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(CFG["url"] + caminho, data=dados, headers=cab, method=metodo)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
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
    subprocess.run(["security", "add-generic-password", "-U", "-a", getpass.getuser(), "-s", SERVICO_CHAVEIRO,
                    "-w", json.dumps(s)], check=True, capture_output=True)


def _ler():
    r = subprocess.run(["security", "find-generic-password", "-a", getpass.getuser(), "-s", SERVICO_CHAVEIRO, "-w"],
                       capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


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


def entrar():
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
    subprocess.run(["security", "delete-generic-password", "-a", getpass.getuser(), "-s", SERVICO_CHAVEIRO],
                   capture_output=True)
    print("Sessão apagada deste Mac.")


if __name__ == "__main__":
    {"entrar": entrar, "status": status, "sair": sair}.get((sys.argv[1:] or ["status"])[0], status)()
