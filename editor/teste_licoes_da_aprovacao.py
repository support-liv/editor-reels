#!/usr/bin/env python3
"""Teste do licoes_da_aprovacao.py contra um liv.ai de mentira (servidor local), sem rede e sem a chave de verdade.

    python3 editor/teste_licoes_da_aprovacao.py

Confere: chave no cabeçalho, paginação, só reprovação que ainda vale, a mais nova de cada vídeo, seção por motivo
(com "também"), texto de dado de cliente fora do guia, motivo novo e sem atalho, placar, nada repetido na 2ª rodada,
--ver sem gravar e as mensagens de erro (chave errada, liv.ai sem chave, rota ainda não publicada).
"""
import contextlib, io, json, os, re, shutil, sys, tempfile, threading, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import licoes_da_aprovacao as L

CHAVE = "chave-de-teste"


def rep(id_, em, motivos, detalhe, video, arquivo, estado="reprovado", marca="LIV", lote="2026-10-29 · Cartas (teste)"):
    return {"id": id_, "em": em, "porNome": "Revisora Teste", "motivos": motivos, "detalhe": detalhe, "marca": marca,
            "lote": {"id": 1, "titulo": lote},
            "video": {"id": video, "titulo": f"Vídeo {video}", "arquivo": arquivo, "formato": "reels", "estadoAtual": estado}}


DADOS = [
    rep(1, "2026-10-20T15:00:00.000Z", ["Gancho"], "Responde a pergunta no gancho.", 10, "R1_antigo.mp4"),
    rep(2, "2026-10-29T13:00:00.000Z", ["Legenda errada"], "Escreveu\n\"wincard\".", 11, "R7B_carta_fraca.mp4"),
    rep(3, "2026-10-29T13:01:00.000Z", ["Corte no meio da fala", "Fala repetida"], None, 12, "R8B_peso.mp4"),
    rep(4, "2026-10-29T13:02:00.000Z", ["Corte no meio da fala"], "texto trocado depois", 12, "R8B_peso.mp4"),
    rep(5, "2026-10-29T13:03:00.000Z", ["Gancho"], "desfeita", 13, "R9_desfeita.mp4", estado="pendente"),
    rep(6, "2026-10-29T13:04:00.000Z", ["Áudio"], "aprovou depois", 14, "R10_aprovado.mp4", estado="aprovado"),
    rep(7, "2026-10-29T13:05:00.000Z", ["Aparece dado de cliente"], "Aparece o nome Fulano de Tal", 15, "TI_01.mp4",
        marca="IMIGRAR", lote="2026-10-29 · Reels (teste)"),
    rep(8, "2026-10-29T13:06:00.000Z", [], "Ficou muito longo.", 16, "R11_longo.mp4"),
    rep(9, "2026-10-29T13:07:00.000Z", ["Motivo que ainda não existe"], "x", 17, "R12.mp4"),
]
pedidos = []
modo = {"resposta": "json"}


class Falso(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        qs = dict(urllib.parse.parse_qsl(url.query))
        pedidos.append(qs)
        if modo["resposta"] == "html":          # rota que não existe no liv.ai: 200 com a página do app
            return self._enviar(200, b"<!doctype html><html></html>", "text/html")
        if modo["resposta"] == "503":
            return self._enviar(503, b'{"error":{}}', "application/json")
        if url.path != "/api/aprovacao/ingest/reprovacoes" or self.headers.get("Authorization") != f"Bearer {CHAVE}":
            return self._enviar(401, b'{"error":{}}', "application/json")
        desde, depois, limite = qs["desde"], int(qs.get("depoisDe", 0)), 2   # página de 2 para exercitar a paginação
        linhas = [r for r in DADOS if r["em"][:len(desde)] >= desde and r["id"] > depois
                  and (not qs.get("marca") or r["marca"] == qs["marca"])]
        corpo = {"reprovacoes": linhas[:limite], "truncado": len(linhas) > limite, "motivosConhecidos": list(L.LICOES)}
        self._enviar(200, json.dumps(corpo).encode(), "application/json; charset=utf-8")

    def _enviar(self, status, corpo, tipo):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)


ok = mal = 0


def check(nome, passou, detalhe=""):
    global ok, mal
    print(("✅ " if passou else "❌ ") + nome + (f" — {detalhe}" if detalhe and not passou else ""))
    if passou:
        ok += 1
    else:
        mal += 1


def rodar(*args):
    saida = io.StringIO()
    with contextlib.redirect_stdout(saida):
        codigo = L.main(list(args))
    return codigo, saida.getvalue()


def secao(texto, motivo):
    ini, fim = L._secoes(texto)[motivo]
    return texto[ini:fim]


def main():
    servidor = ThreadingHTTPServer(("127.0.0.1", 0), Falso)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}"
    pasta = tempfile.mkdtemp(prefix="licoes_")
    guia = os.path.join(pasta, "REPROVACOES.md")
    # o guia do repositório já tem reprovações de verdade: o teste parte do modelo, sem as linhas e com o placar zerado
    modelo = open(os.path.join(L.RAIZ, "docs", "REPROVACOES.md"), encoding="utf-8").read()
    modelo = "\n".join(l for l in modelo.splitlines() if not L.MARCA.search(l)) + "\n"
    modelo = re.sub(r"(<!-- placar -->\n).*?(\n<!-- /placar -->)", lambda m: m.group(1) + "Nenhuma reprovação importada ainda." + m.group(2),
                    modelo, flags=re.S)
    with open(guia, "w", encoding="utf-8") as f:
        f.write(modelo)
    original = open(guia, encoding="utf-8").read()
    chave = {"valor": CHAVE}
    L.PLAT.ler_segredo = lambda servico: chave["valor"] if servico == L.SERVICO_CHAVEIRO else None
    try:
        # ── sem chave, chave errada, liv.ai sem chave, rota ainda não publicada ──
        chave["valor"] = None
        c, s = rodar("--url", base, "--guia", guia)
        check("sem chave no Chaveiro: avisa e não pede nada", c == 1 and "--guardar-chave" in s and not pedidos)
        chave["valor"] = "outra"
        c, s = rodar("--url", base, "--guia", guia)
        check("chave errada: frase simples", c == 1 and "não é a mesma do liv.ai" in s, s)
        chave["valor"] = CHAVE
        modo["resposta"] = "503"
        c, s = rodar("--url", base, "--guia", guia)
        check("liv.ai sem a chave configurada (503)", c == 1 and "APROVACAO_INGEST_TOKEN" in s, s)
        modo["resposta"] = "html"
        c, s = rodar("--url", base, "--guia", guia)
        check("rota ainda não publicada (200 com página): não quebra", c == 1 and "falta publicar" in s, s)
        modo["resposta"] = "json"
        check("nada foi gravado nos erros", open(guia, encoding="utf-8").read() == original)

        # ── --ver não grava ──────────────────────────────────────────────────
        pedidos.clear()
        c, s = rodar("--url", base, "--guia", guia, "--ver")
        check("--ver mostra e não grava", c == 0 and "R7B_carta_fraca.mp4" in s and open(guia, encoding="utf-8").read() == original)
        check("guia vazio: começa em %s" % L.INICIO, pedidos and pedidos[0]["desde"] == L.INICIO, str(pedidos[:1]))
        check("pagina pelo id da última até o fim", len(pedidos) == 5 and [p["depoisDe"] for p in pedidos] == ["0", "2", "4", "6", "8"],
              str([p.get("depoisDe") for p in pedidos]))
        check("a chave vai no cabeçalho, nunca na URL", all(CHAVE not in json.dumps(p) for p in pedidos))
        check("a saída não mostra a chave", CHAVE not in s)

        # ── 1ª rodada ────────────────────────────────────────────────────────
        c, s = rodar("--url", base, "--guia", guia)
        texto = open(guia, encoding="utf-8").read()
        check("1ª rodada grava", c == 0 and "Guia atualizado" in s, s)
        check("6 reprovações que valem entraram (ids 1, 2, 4, 7, 8, 9)",
              {int(i) for i, *_ in L.MARCA.findall(texto)} == {1, 2, 4, 7, 8, 9}, str(L.MARCA.findall(texto)))
        check("desfeita e trocada por aprovação ficam de fora", "R9_desfeita" not in texto and "R10_aprovado" not in texto)
        check("do mesmo vídeo, só a mais nova", "r:3 " not in texto and "texto trocado depois" in texto)
        leg = secao(texto, "Legenda errada")
        check("na seção do motivo, com data, marca, lote, arquivo, título e quem",
              "- 29/10/2026 · LIV · 2026-10-29 · Cartas (teste) · `R7B_carta_fraca.mp4` (Vídeo 11) · Revisora Teste:" in leg, leg)
        check("texto da revisora numa linha só, entre aspas", "“Escreveu \"wincard\".”" in leg, leg)
        check("a lição escrita continua lá, antes das linhas", leg.index("**Lição:**") < leg.index("R7B_carta_fraca"))
        cli = secao(texto, "Aparece dado de cliente")
        check("dado de cliente: o texto não vem para o guia", "Fulano" not in texto and "texto só no liv.ai" in cli, cli)
        check("Imigrar escrita como marca", "· Imigrar ·" in cli)
        check("sem atalho vai para a seção do texto livre", "R11_longo.mp4" in secao(texto, L.SEM_ATALHO))
        check("motivo novo ganha seção própria no fim", texto.rstrip().endswith("<!-- r:9 v:17 em:2026-10-29T13:07:00.000Z -->")
              and "## Motivo que ainda não existe" in texto and "escreva aqui a lição" in texto)
        check("placar refeito", "| Gancho | 1 | 20/10/2026 |" in texto and "| Legenda errada | 1 | 29/10/2026 |" in texto
              and "Nenhuma reprovação importada ainda." not in texto, texto[:1500])
        check("as seções seguem separadas por linha em branco", "\n\n## Corte no meio da fala" in texto and "\n\n## Fala repetida" in texto)

        # ── 2ª rodada: nada repetido; desde = última do guia menos a sobreposição ──
        pedidos.clear()
        c, s = rodar("--url", base, "--guia", guia)
        check("2ª rodada: nada novo e o guia não muda", c == 0 and "Nenhuma reprovação nova" in s
              and open(guia, encoding="utf-8").read() == texto, s)
        check("2ª rodada pede desde a última menos %d dias" % L.SOBREPOSICAO_DIAS, pedidos[0]["desde"] == "2026-10-26", str(pedidos[:1]))

        # ── reprovação nova no liv.ai: entra uma vez, no fim da seção ────────
        DADOS.append(rep(10, "2026-10-30T10:00:00.000Z", ["Gancho"], "Gancho fraco.", 18, "R13.mp4"))
        c, s = rodar("--url", base, "--guia", guia)
        texto2 = open(guia, encoding="utf-8").read()
        gancho = secao(texto2, "Gancho")
        check("nova entra uma vez, depois da anterior", texto2.count("r:10 ") == 1 and gancho.index("R1_antigo") < gancho.index("R13.mp4"))
        check("placar conta 2 no Gancho", "| Gancho | 2 | 30/10/2026 |" in texto2)
        check("o resto do guia ficou igual", texto2.replace(gancho, "").split("<!-- /placar -->")[1]
              == texto.replace(secao(texto, "Gancho"), "").split("<!-- /placar -->")[1])

        # ── aprovar com ajustes (30/10/2026): seções próprias; valem mesmo depois de a versão nova ser aprovada ──
        pedidos.clear()
        DADOS.append(dict(rep(11, "2026-10-30T11:00:00.000Z", ["Falta contexto"], "Dizer para quem é.", 19, "R14.mp4",
                              estado="aprovado"), tipo="ajustar"))
        DADOS.append(dict(rep(12, "2026-10-30T11:01:00.000Z", ["Gancho"], "Gancho pode ser mais curto.", 20, "R15.mp4",
                              estado="ajustar"), tipo="ajustar"))
        c, s = rodar("--url", base, "--guia", guia)
        texto3 = open(guia, encoding="utf-8").read()
        check("pede reprovações e ajustes", pedidos and pedidos[0].get("tipos") == "reprovado,ajustar", str(pedidos[:1]))
        check("ajuste entra mesmo com a versão nova já aprovada", "R14.mp4" in secao(texto3, L.AJUSTE + "Falta contexto"))
        check("ajuste de Gancho vai para 'Ajuste · Gancho', não para a reprova",
              "R15.mp4" in secao(texto3, L.AJUSTE + "Gancho") and "R15.mp4" not in secao(texto3, "Gancho"))
        check("seção de ajuste nasce com a lição", "faltou situar quem assiste" in secao(texto3, L.AJUSTE + "Falta contexto"))
        check("placar mostra os ajustes", "| Ajuste · Falta contexto | 1 | 30/10/2026 |" in texto3, texto3[:1500])
        check("a saída separa reprovações e ajustes", "0 reprovação(ões) e 2 ajuste(s)" in s, s)
        c, s = rodar("--url", base, "--guia", guia)
        check("ajuste não entra duas vezes", c == 0 and "Nenhuma reprovação nova" in s and open(guia, encoding="utf-8").read() == texto3, s)
    finally:
        servidor.shutdown()
        shutil.rmtree(pasta, ignore_errors=True)

    print(f"\n{ok} ok, {mal} com problema")
    return 1 if mal else 0


if __name__ == "__main__":
    sys.exit(main())
