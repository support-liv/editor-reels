#!/usr/bin/env python3
"""Envio de shorts pro YouTube pelo servidor do time (a credencial e a autorização do canal ficam no Supabase).

    python3 editor/youtube.py canais                                   # canais conectados
    python3 editor/youtube.py conectar --canal liv --nome "LIV Immigration Law"   # só administrador, uma vez por canal
    python3 editor/youtube.py enviar VIDEO.mp4 --canal liv --titulo "..." --descricao "..." --tags "a,b" [--publicar-em 2026-10-02T12:00]
    python3 editor/youtube.py lote projetos/live80/publicacao.json --canal liv [--inicio 2026-10-02 --hora 12:00 --por-dia 1] [--so 1]

Os vídeos sobem como PRIVADOS (projeto sem auditoria do Google). Com --publicar-em/--inicio, vai junto o horário de
publicação; se o canal estiver sob a restrição, alguém programa depois pelo Studio. Horários no fuso de São Paulo.
"""
import argparse, base64, datetime as dt, hashlib, http.server, json, os, secrets, sys, threading, urllib.parse, urllib.request, webbrowser

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import conta
from pacote_publicacao import datas, checar

FUSO = dt.timezone(dt.timedelta(hours=-3))      # São Paulo (sem horário de verão)


def chamar(corpo):
    tk = conta.token()
    if not tk:
        sys.exit("Faça login primeiro: python3 editor/conta.py entrar")
    st, r = conta._req("/functions/v1/youtube", corpo, token=tk)
    if st != 200:
        sys.exit(f"Servidor recusou ({st}): {r.get('erro') or r} {r.get('detalhe') or ''}")
    return r


def conectar(canal, nome):
    """OAuth do Google com PKCE e retorno local: o código vai pro servidor, que troca pelo refresh token e guarda no Vault."""
    verificador = secrets.token_urlsafe(64)
    desafio = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode()
    estado = secrets.token_urlsafe(16)
    recebido = {}

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
            if q.get("state") == estado:
                recebido.update(q)
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write("<h3>Pronto, pode voltar pro terminal.</h3>".encode())

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    redirect = f"http://127.0.0.1:{srv.server_port}"
    url = chamar({"acao": "url_autorizacao", "canal": canal, "redirect_uri": redirect, "code_challenge": desafio, "state": estado})["url"]
    print("Abrindo o Google no navegador. Entre com a conta que administra o canal e autorize o envio de vídeos.")
    webbrowser.open(url)
    t = threading.Thread(target=srv.handle_request); t.start(); t.join(timeout=300); srv.server_close()
    if "code" not in recebido:
        sys.exit("Não recebi a autorização do Google (tempo esgotado ou cancelado).")
    chamar({"acao": "conectar", "canal": canal, "nome": nome or canal, "code": recebido["code"],
            "code_verifier": verificador, "redirect_uri": redirect})
    print(f"Canal '{canal}' conectado. A autorização ficou guardada só no servidor.")


def enviar(video, canal, titulo, descricao, tags, publicar_em=None):
    video = os.path.expanduser(video)
    tam = os.path.getsize(video)
    corpo = {"acao": "iniciar_envio", "canal": canal, "titulo": titulo, "descricao": descricao, "tags": tags, "tamanho": tam}
    if publicar_em:
        corpo["publicar_em"] = publicar_em.astimezone(dt.timezone.utc).isoformat()
    r = chamar(corpo)
    with open(video, "rb") as f:
        req = urllib.request.Request(r["upload_url"], data=f, method="PUT",
                                     headers={"Content-Type": "video/mp4", "Content-Length": str(tam)})
        try:
            with urllib.request.urlopen(req, timeout=1800, context=conta.SSL) as resp:
                vid = json.loads(resp.read().decode()).get("id")
        except urllib.error.HTTPError as e:
            chamar({"acao": "concluir", "envio_id": r["envio_id"], "video_id": ""})
            sys.exit(f"YouTube recusou o arquivo ({e.code}): {e.read().decode()[:300]}")
    chamar({"acao": "concluir", "envio_id": r["envio_id"], "video_id": vid})
    return vid


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("canais")
    c = sub.add_parser("conectar"); c.add_argument("--canal", required=True); c.add_argument("--nome")
    e = sub.add_parser("enviar"); e.add_argument("video"); e.add_argument("--canal", required=True)
    e.add_argument("--titulo", required=True); e.add_argument("--descricao", default=""); e.add_argument("--tags", default="")
    e.add_argument("--publicar-em", help="AAAA-MM-DDTHH:MM no fuso de São Paulo")
    l = sub.add_parser("lote"); l.add_argument("json"); l.add_argument("--canal", required=True)
    l.add_argument("--inicio"); l.add_argument("--hora", default="12:00"); l.add_argument("--por-dia", type=int, default=1)
    l.add_argument("--pular-fim-de-semana", action="store_true"); l.add_argument("--so", type=int, help="só os N primeiros (teste)")
    a = ap.parse_args()

    if a.cmd == "canais":
        for x in chamar({"acao": "canais"})["canais"] or [{"canal": "(nenhum)", "nome": "", "conectado_em": ""}]:
            print(f"{x['canal']:10s} {x.get('nome') or ''}  {x.get('conectado_em') or ''}")
    elif a.cmd == "conectar":
        conectar(a.canal, a.nome)
    elif a.cmd == "enviar":
        quando = dt.datetime.fromisoformat(a.publicar_em).replace(tzinfo=FUSO) if a.publicar_em else None
        vid = enviar(a.video, a.canal, a.titulo, a.descricao, [t.strip() for t in a.tags.split(",") if t.strip()], quando)
        print(f"enviado (privado): https://studio.youtube.com/video/{vid}/edit")
    else:
        cfg = json.load(open(os.path.expanduser(a.json)))
        shorts = cfg["shorts"][: a.so] if a.so else cfg["shorts"]
        for s in shorts:
            problemas = checar(s)
            if problemas:
                sys.exit(f"{s['id']}: " + "; ".join(problemas))
        horarios = ([h.replace(tzinfo=FUSO) for h in datas(len(shorts), dt.date.fromisoformat(a.inicio), a.hora, a.por_dia,
                                                           a.pular_fim_de_semana)] if a.inicio else [None] * len(shorts))
        for s, h in zip(shorts, horarios):
            vid = enviar(s["video"], a.canal, s["titulo"], s["descricao"], s.get("tags", []), h)
            print(f"{s['id']}: enviado (privado{', publicar ' + h.strftime('%d/%m %H:%M') if h else ''}) "
                  f"https://studio.youtube.com/video/{vid}/edit", flush=True)


if __name__ == "__main__":
    main()
