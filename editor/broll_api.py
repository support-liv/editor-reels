#!/usr/bin/env python3
"""B-roll por API, pelo servidor do time (Supabase). Sem chave no computador: precisa só do login (conta.py).

    python3 editor/broll_api.py "airport crowd"                 # lista resultados
    python3 editor/broll_api.py "airport crowd" --baixar 1      # baixa o 1º (vertical, até 1080p) pro cache

Os vídeos vêm do Pexels (licença livre pra uso comercial, sem obrigação de crédito; damos crédito no PUBLICACAO quando der).
Só a palavra de busca sai do Mac; vídeo de cliente nunca sobe.
"""
import json, os, sys, urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import conta
import plataforma as P

CACHE = P.pasta_cache("broll")


def buscar(busca, orientacao="portrait", quantidade=8):
    tk = conta.token()
    if not tk:
        sys.exit("Faça login primeiro: python3 editor/conta.py entrar")
    st, r = conta._req("/functions/v1/broll", {"busca": busca, "orientacao": orientacao, "quantidade": quantidade}, token=tk)
    if st != 200:
        sys.exit(f"Busca falhou ({st}): {r.get('erro') or r}")
    return r["videos"]


def melhor_arquivo(video, altura_max=1920):
    """o maior arquivo que não passa de 1080x1920 (o editor trabalha em 1080 de largura)."""
    arqs = sorted((a for a in video["arquivos"] if (a.get("altura") or 0) <= altura_max), key=lambda a: a.get("altura") or 0)
    return arqs[-1] if arqs else video["arquivos"][0]


def baixar(video, altura_max=1920):
    os.makedirs(CACHE, exist_ok=True)
    destino = os.path.join(CACHE, f"pexels_{video['id']}.mp4")
    if not os.path.exists(destino):
        req = urllib.request.Request(melhor_arquivo(video, altura_max)["link"],
                                     headers={"User-Agent": "Mozilla/5.0 (Macintosh) editor-reels"})   # o CDN recusa o UA padrão do Python
        with urllib.request.urlopen(req, context=conta.SSL, timeout=120) as r, open(destino + ".parcial", "wb") as f:
            f.write(r.read())
        os.replace(destino + ".parcial", destino)
    json.dump({k: video[k] for k in ("id", "pagina", "autor", "autor_url", "fonte", "duracao")},
              open(destino.replace(".mp4", ".json"), "w"), ensure_ascii=False)
    return destino


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    vids = buscar(sys.argv[1])
    for i, v in enumerate(vids, 1):
        a = melhor_arquivo(v)
        print(f"{i:2d}. {v['duracao']:3d}s  {a['largura']}x{a['altura']}  {v['autor']}  {v['pagina']}")
    if "--baixar" in sys.argv:
        n = int(sys.argv[sys.argv.index("--baixar") + 1])
        print("baixado:", baixar(vids[n - 1]))
