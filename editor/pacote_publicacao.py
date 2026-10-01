#!/usr/bin/env python3
"""Pacote de publicação pro YouTube Studio: cada short numa pasta com o vídeo e os textos prontos pra copiar,
mais uma agenda com data e hora sugeridas. A publicação/agendamento é feita por uma pessoa no Studio
(a API do YouTube sem auditoria só sobe vídeo privado).

    python3 editor/pacote_publicacao.py publicacao.json --inicio 2026-10-02 --hora 12:00 --por-dia 1

publicacao.json (o Claude escreve a partir do que foi dito no vídeo):
{
  "canal": "LIV Immigration Law",
  "saida": "~/Desktop/LIVE_80/pacote_youtube",
  "shorts": [
    {"id": "S1", "video": "~/Desktop/LIVE_80/shorts_B/S1B_visa_bulletin_brasil.mp4",
     "titulo": "...", "descricao": "...", "tags": ["visa bulletin", "green card"]}
  ]
}
Regras: título até 100 caracteres (o YouTube corta), descrição até 5.000, tags somando até 500 caracteres.
"""
import argparse, datetime as dt, json, os, shutil, subprocess, sys

DIAS = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]


def checar(s):
    avisos = []
    if len(s["titulo"]) > 100:
        avisos.append(f"título com {len(s['titulo'])} caracteres (máx 100)")
    if len(s["descricao"]) > 5000:
        avisos.append("descrição passa de 5.000 caracteres")
    if len(",".join(s.get("tags", []))) > 500:
        avisos.append("tags passam de 500 caracteres")
    if "<" in s["titulo"] or ">" in s["titulo"]:
        avisos.append("título com < ou > (o YouTube não aceita)")
    return avisos


def datas(n, inicio, hora, por_dia, pular_fds):
    h, m = (int(x) for x in hora.split(":"))
    d, out = dt.datetime.combine(inicio, dt.time(h, m)), []
    while len(out) < n:
        if not (pular_fds and d.weekday() >= 5):
            for k in range(por_dia):
                if len(out) < n:
                    out.append(d + dt.timedelta(hours=4 * k))     # 2+ por dia: de 4 em 4 horas
        d += dt.timedelta(days=1)
    return out


def duracao(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                       capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--inicio", default=(dt.date.today() + dt.timedelta(days=1)).isoformat())
    ap.add_argument("--hora", default="12:00", help="horário da 1ª publicação do dia (fuso do canal no Studio)")
    ap.add_argument("--por-dia", type=int, default=1)
    ap.add_argument("--pular-fim-de-semana", action="store_true")
    ap.add_argument("--copiar", action="store_true", help="copia os vídeos (padrão: link simbólico, não ocupa espaço)")
    a = ap.parse_args()

    cfg = json.load(open(os.path.expanduser(a.json)))
    saida = os.path.expanduser(cfg["saida"])
    os.makedirs(saida, exist_ok=True)
    quando = datas(len(cfg["shorts"]), dt.date.fromisoformat(a.inicio), a.hora, a.por_dia, a.pular_fim_de_semana)
    linhas_md, linhas_csv, problemas = [], ["ordem,data,hora,id,titulo,arquivo"], []
    for i, (s, t) in enumerate(zip(cfg["shorts"], quando), 1):
        video = os.path.expanduser(s["video"])
        if not os.path.exists(video):
            problemas.append(f"{s['id']}: vídeo não encontrado ({video})"); continue
        av = checar(s)
        problemas += [f"{s['id']}: {x}" for x in av]
        pasta = os.path.join(saida, f"{i:02d}_{t:%Y-%m-%d_%Hh%M}_{s['id']}")
        os.makedirs(pasta, exist_ok=True)
        destino = os.path.join(pasta, os.path.basename(video))
        if os.path.lexists(destino):
            os.remove(destino)
        (shutil.copy2 if a.copiar else os.symlink)(video, destino)
        tags = ", ".join(s.get("tags", []))
        open(os.path.join(pasta, "titulo.txt"), "w").write(s["titulo"] + "\n")
        open(os.path.join(pasta, "descricao.txt"), "w").write(s["descricao"].strip() + "\n")
        open(os.path.join(pasta, "tags.txt"), "w").write(tags + "\n")
        dur = duracao(video)
        linhas_md += [f"## {i}. {DIAS[t.weekday()]} {t:%d/%m} às {t:%H:%M} · {s['id']} ({int(dur // 60)}:{int(dur % 60):02d})", "",
                      f"**Arquivo:** `{os.path.basename(pasta)}/{os.path.basename(video)}`", "",
                      f"**Título:** {s['titulo']}", "", "**Descrição:**", "", s["descricao"].strip(), "",
                      f"**Tags:** {tags}", "", "- [ ] Agendado no Studio", ""]
        linhas_csv.append(f'{i},{t:%Y-%m-%d},{t:%H:%M},{s["id"]},"{s["titulo"].replace(chr(34), chr(39))}",{os.path.basename(video)}')
    cab = [f"# Agenda de publicação · {cfg.get('canal', '')}", "",
           f"{len(cfg['shorts'])} shorts, a partir de {quando[0]:%d/%m/%Y}, {a.por_dia} por dia às {a.hora}"
           + (" (sem fim de semana)" if a.pular_fim_de_semana else "") + ".", "",
           "**Como agendar cada um no YouTube Studio** (cerca de 1 min): Criar → Enviar vídeos → arraste o .mp4 da pasta →",
           "cole o título, a descrição e as tags dos .txt → Visibilidade: **Programar** → data e hora desta agenda.",
           "Antes de agendar, assista o short inteiro (a legenda vem do Whisper).", ""]
    open(os.path.join(saida, "AGENDA.md"), "w").write("\n".join(cab + linhas_md))
    open(os.path.join(saida, "agenda.csv"), "w").write("\n".join(linhas_csv) + "\n")
    print(f"pacote em {saida}: {len(cfg['shorts']) - len([p for p in problemas if 'não encontrado' in p])} shorts")
    for p in problemas:
        print("  aviso:", p)


if __name__ == "__main__":
    main()
