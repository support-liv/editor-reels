"""Modelos de descrição do YouTube por canal (padrão do time).

No publicacao.json, cada short traz só o que é dele:
    "resumo":   2 parágrafos sobre o que é dito no vídeo (separados por linha em branco)
    "hashtags": ["#VisaBulletin", "#EB2NIW", ...]   (as do vídeo; viram a única linha de hashtags)
Vídeo longo: "resumo" (abertura) + "topicos": [["Título do bloco", "o que é explicado"], ...]
  + "capitulos" (opcional): [["0:00", "Nome curto"], ...] -> bloco de capítulos do YouTube (o 1º tem que ser 0:00)
O resto (chamada, link, disclaimer) vem daqui, igual em todos os vídeos do canal.
Estrutura fixa: texto → chamada/links → UMA linha de hashtags → disclaimer (sem hashtags) e acabou.
"""
import re

DISCLAIMER_LIV = ("DISCLAIMER: O conteúdo deste vídeo tem caráter estritamente informativo e não constitui aconselhamento "
                  "jurídico. Assistir a este vídeo não cria relação advogado-cliente. Para orientação jurídica específica, "
                  "agende uma consulta com nossos especialistas.")
RODAPE_LIV = ["#VisaBulletin", "#EB2NIW", "#AjusteDeStatus", "#GreenCard", "#USCIS", "#ConsuladoEUA", "#ImigracaoEUA",
              "#LIVImmigrationLaw", "#EB3", "#EB1A"]          # padrão só quando o vídeo não traz as dele

MODELOS = {
    "liv": {
        "short": ("{resumo}\n\n"
                  "👉 Quer compreender a situação específica do seu processo?\n\n"
                  "Faça uma avaliação com a nossa equipe jurídica nos EUA:\n"
                  "📲 https://to.liv.law/gc-yt\n\n"
                  "{hashtags}\n\n"
                  "{disclaimer}"),
        "longo": ("{resumo}\n\n"
                  "Você vai conferir:\n\n"
                  "{topicos}\n\n"
                  "{capitulos}"
                  "📲 Avalie seu perfil:\n"
                  "https://to.liv.law/analise-perfil-uXQ4\n\n"
                  "👉 Fale com nossos especialistas:\n"
                  "https://to.liv.law/u1uBIT\n\n"
                  "{hashtags}\n\n"
                  "{disclaimer}"),
        "disclaimer": DISCLAIMER_LIV,
        "rodape": RODAPE_LIV,
    },
}


def montar(canal, item, tipo="short"):
    """descrição final do vídeo; sem modelo pro canal (ou sem "resumo"), usa a "descricao" escrita à mão."""
    m = MODELOS.get(canal)
    if not m or not item.get("resumo"):
        return item.get("descricao", "")
    # hashtags só numa linha, logo antes do disclaimer (nunca no meio do texto nem depois do disclaimer)
    tags = item.get("hashtags") or m["rodape"]
    tags = list(dict.fromkeys(h if h.startswith("#") else "#" + h for h in tags))
    topicos = "\n\n".join(f"🔸{t}: {d}" for t, d in item.get("topicos", []))
    caps = item.get("capitulos") or []
    capitulos = ("Capítulos:\n" + "\n".join(f"{t} {n}" for t, n in caps) + "\n\n") if caps else ""
    txt = m[tipo].format(resumo=item["resumo"].strip(), hashtags=" ".join(tags), topicos=topicos,
                         capitulos=capitulos, disclaimer=m["disclaimer"])
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    if len(txt) > 5000 or re.search(r"[<>]", txt):
        raise ValueError(f"{item.get('id')}: descrição passa de 5.000 caracteres ou tem < >")
    if len(re.findall(r"#\w+", txt)) > 60:
        raise ValueError(f"{item.get('id')}: mais de 60 hashtags (o YouTube ignora todas)")
    return txt
