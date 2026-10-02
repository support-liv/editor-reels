#!/usr/bin/env python3
"""Banco de trilhas (assets/trilhas/, Git LFS): analisar, sugerir e mixar por baixo da fala.

    python3 editor/trilhas.py analisar "~/Downloads/PACK BG MUSIC"   # mede BPM, tom, energia, brilho (gera _medidas.json)
    python3 editor/trilhas.py sugerir --clima corporativo --marca liv --anuncio [--dur 30]
    python3 editor/trilhas.py mixar VIDEO.mp4 TRILHA.mp3 [-o saida.mp4] [--ss 12]

Regras (ver CLAUDE.md): sempre oferecer trilha ao usuário; a trilha combina com o clima da narrativa
(corporativo, inspirador, emocional, tenso/polêmico, alegre...); a trilha fica SEMPRE bem abaixo da fala
(ducking automático); antes de usar, o agente auditor-de-trilha confere licença, clima, marca e volume.
"""
import argparse, json, os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

AQUI = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(os.path.dirname(AQUI), "assets", "trilhas")
CATALOGO = os.path.join(PASTA, "catalogo.json")
NOTAS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
# perfis de Krumhansl-Kessler (tom maior/menor)
MAIOR = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MENOR = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]


def loudness(arq, ss=0, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-ss", str(ss)] + (["-t", str(dur)] if dur else []) + \
          ["-i", arq, "-vn", "-af", "ebur128", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r)
    return float(m[-1]) if m else None


def medir(arq):
    import numpy as np, librosa
    try:
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", arq],
                                   capture_output=True, text=True).stdout)
        try:
            y, sr = librosa.load(arq, sr=22050, mono=True, offset=min(15.0, max(0.0, dur * 0.1)), duration=75)
        except Exception:                               # extensão errada (ex.: m4a salvo como .mp3): converte antes
            import tempfile
            tmp = os.path.join(tempfile.gettempdir(), "trilha_tmp.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", arq, "-ac", "1", "-ar", "22050", tmp], check=True)
            y, sr = librosa.load(tmp, sr=22050, mono=True, offset=min(15.0, max(0.0, dur * 0.1)), duration=75)
        # BPM pela autocorrelação da curva de ataques (o beat_track do librosa quebra no Python 3.14)
        env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512); env = env - env.mean()
        ac = np.correlate(env, env, "full")[len(env) - 1:]
        lags = np.arange(len(ac)); fps = sr / 512
        bpms = 60 * fps / np.maximum(lags, 1); faixa = (bpms >= 70) & (bpms <= 170)
        tempo = float(60 * fps / lags[faixa][np.argmax(ac[faixa])])
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
        melhor = max([(np.corrcoef(np.roll(MAIOR, k), chroma)[0, 1], NOTAS[k], "maior") for k in range(12)] +
                     [(np.corrcoef(np.roll(MENOR, k), chroma)[0, 1], NOTAS[k], "menor") for k in range(12)])
        rms = librosa.feature.rms(y=y)[0]
        cent = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
        perc = librosa.effects.percussive(y)
        return {"arquivo_origem": os.path.basename(arq), "duracao_s": round(dur, 1), "bpm": round(tempo),
                "tom": f"{melhor[1]} {melhor[2]}", "modo": melhor[2],
                "energia": round(float(rms.mean()), 4), "variacao": round(float(rms.std() / (rms.mean() + 1e-9)), 2),
                "brilho_hz": round(cent), "percussao": round(float(np.abs(perc).mean() / (np.abs(y).mean() + 1e-9)), 2),
                "lufs": loudness(arq, dur=120)}
    except Exception as e:
        return {"arquivo_origem": os.path.basename(arq), "erro": str(e)[:200]}


def analisar(pasta):
    """mede todas as faixas (4 processos, salva a cada faixa: se cair, retoma de onde parou)."""
    pasta = os.path.expanduser(pasta)
    saida = os.path.expanduser("~/Library/Caches/editor-reels/trilhas_medidas.json")   # fora da pasta do usuário
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    feitas = {x["arquivo_origem"]: x for x in (json.load(open(saida)) if os.path.exists(saida) else []) if "erro" not in x}
    arqs = sorted(os.path.join(pasta, f) for f in os.listdir(pasta)
                  if f.lower().endswith((".mp3", ".m4a", ".wav")) and f not in feitas)
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def isolado(a_):                                 # cada faixa num processo próprio: um arquivo ruim não derruba o lote
        try:
            p = subprocess.run([sys.executable, os.path.abspath(__file__), "medir-um", a_], capture_output=True, text=True, timeout=240)
            return json.loads(p.stdout.strip().splitlines()[-1])
        except Exception as e:
            return {"arquivo_origem": os.path.basename(a_), "erro": f"falhou: {str(e)[:120]}"}
    with ThreadPoolExecutor(max_workers=4) as ex:
        fut = {ex.submit(isolado, a_): a_ for a_ in arqs}
        for k, fu in enumerate(as_completed(fut), 1):
            r = fu.result(); feitas[r["arquivo_origem"]] = r
            json.dump(list(feitas.values()), open(saida, "w"), ensure_ascii=False, indent=1)
            print(f"  {k}/{len(arqs)} {r['arquivo_origem'][:60]}", flush=True)
    print(f"{len(feitas)} faixas medidas → {saida}")



# ------------------------------------------------------------------ licença (pela origem/artista; na dúvida, "conferir")
# status: liberada (uso comercial ok) | credito (livre com crédito) | conferir (origem incerta) | bloqueada (direitos de terceiros)
# anuncio_pago: sim | conferir | nao
LICENCAS = [
    (r"spongebob|wii shop|cold war|call of duty|doraemon|mind heist|zack hemsey|sebastian - pleasant|bus rider|john swihart|"
     r"carryminati|teddy gaming|andreobee|proboiz|ryan trahan|palm city|vanoss|bollywood sampled|mario jump|darix togni",
     dict(status="bloqueada", fonte="trilha/tema de terceiros (franquia, filme, jogo, youtuber ou sample)", anuncio_pago="nao")),
    (r"aldenmark niklasson", dict(status="bloqueada", fonte="Epidemic Sound (exige assinatura)", anuncio_pago="nao")),
    (r"mixkit", dict(status="liberada", fonte="Mixkit (licença livre, uso comercial)", anuncio_pago="sim")),
    (r"anno domini|audio hertz|patrick patrikios|quincas moreira|jimena contreras|dj freedem|french fuse|brothers records|"
     r"verified picasso|rage\.mp3|book the rental|yung logos|hanu dixit|otis mcdonald|jazz in paris|eoin mantell",
     dict(status="liberada", fonte="YouTube Audio Library", anuncio_pago="conferir")),
    (r"kevin macleod", dict(status="credito", fonte="Kevin MacLeod (CC BY: creditar)", anuncio_pago="conferir")),
    (r"alex-productions|alex productions|alexander nakarada|sappheiros|pufino|cosimo fogg|kubbi|mokkamusic|aylex|argsound|"
     r"audio library release|mbb - take|tubebackr|land of fire|smarttoaster|unfeel|aoeris|yoitrax|loyalist|ashutosh|artificial\.music",
     dict(status="credito", fonte="criador independente (livre com crédito)", anuncio_pago="conferir")),
    (r"ncs|infraction|oddvision|lensko|akacia|beauz", dict(status="credito", fonte="NCS / Infraction (crédito obrigatório; uso comercial só com licença)", anuncio_pago="nao")),
    (r"type beat|\[free|\(free|free beats|free no copyright beat|deathtown|prod\.|non-commercial|italics|fayzed|groove_day|riddim",
     dict(status="credito", fonte="beat 'free' (em geral só uso não comercial)", anuncio_pago="nao")),
]
CLIMAS = [   # (padrão no nome, climas)
    (r"corporat|business|promotional|uplifting|inspire|motivat|success|arrival|skylines|stand\b|never surrender|sunny days|finally the sun", ["corporativo", "inspirador"]),
    (r"cinematic|epic|heroic|trailer|legendary|orchestra|mind heist|epic shield", ["epico", "inspirador"]),
    (r"lofi|lo-fi|chill|calm|herbal tea|night city|breakfast|cozy|traveller|faraway|aesthetic|blue moon|forgive me|late night", ["calmo"]),
    (r"violin|ave maria|mozart|schubert|piano|hopeless|forget me not|ethereal", ["emocional"]),
    (r"suspense|tension|horror|serial killer|sinister|dark|schizo|warzone|arms dealer|cutthroat|tales from the grave|deathtown|triple six|hidden", ["tenso", "polemico"]),
    (r"trap|hard bass|drop|matrix|heads up|strong|fight|rebel|cyberpunk|dubstep|angry", ["energetico", "polemico"]),
    (r"sport|racing|extreme|chase|full speed|push|punch|rock|metal|bubbles|digital love|goat", ["energetico"]),
    (r"funny|comedy|comical|raost|scheming weasel|happy-go|whirl|bathtub|weasel|tango|spongebob", ["humor"]),
    (r"fashion|lounge|house|stylish|jazz|saxophone|magazines|sunset lounge|circles", ["luxo", "calmo"]),
    (r"funk|groove|upbeat|dance|reggaeton|happy|whistle|tropic|positive|disc|marmalade|sea lion", ["alegre"]),
]
SFX = r"sound effect|transition sounds|swoosh|mario jump|comical question"


def licenca(nome):
    n = nome.lower()
    for pad, lic in LICENCAS:
        if re.search(pad, n):
            return dict(lic)
    return dict(status="conferir", fonte="origem não identificada pelo nome", anuncio_pago="conferir")


def climas(nome, m):
    n = nome.lower()
    cs = []
    for pad, c in CLIMAS:
        if re.search(pad, n):
            cs += [x for x in c if x not in cs]
    if not cs:                                       # sem pista no nome: pelas medidas
        if m["modo"] == "menor" and m["brilho_hz"] < 1800:
            cs = ["tenso"]
        elif m["bpm"] < 95 and m["energia"] < 0.12:
            cs = ["calmo"]
        elif m["modo"] == "maior" and 95 <= m["bpm"] <= 130:
            cs = ["corporativo", "inspirador"]
        else:
            cs = ["energetico"]
    return cs


REGIONAL = r"indian|bollywood|chinese|japanese|slav|russian|dancehall|reggaeton|latin"


def marcas(cs, lic, nome=""):
    """LIV: corporativo, inspirador, emocional, calmo, luxo, épico contido — e nada com cara de outro país (sonho
    americano). Imigrar: tudo menos humor (pode provocar)."""
    out = []
    if lic["status"] != "bloqueada" and set(cs) & {"corporativo", "inspirador", "emocional", "calmo", "luxo", "epico"} \
            and not set(cs) & {"humor", "polemico"} and not re.search(REGIONAL, nome.lower()):
        out.append("liv")
    if lic["status"] != "bloqueada" and "humor" not in cs:
        out.append("imigrar")
    return out


def _slug(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    t = re.sub(r"\((mp3|m4a)[^)]*\)|\[no copyright[^\]]*\]|\(no copyright[^)]*\)|no copyright music|royalty free|free download|"
               r"copyright free|non copyrighted|ncs release|\(320kbps\)", " ", t)
    t = re.sub(r"[^a-z0-9]+", "-", t).strip("-")
    return re.sub(r"-+", "-", t)[:60].strip("-")


def catalogar(pasta):
    """monta assets/trilhas/: copia (mp3) só o que não está bloqueado, com nome clima__titulo__bpm__tom, e o catalogo.json."""
    import shutil
    pasta = os.path.expanduser(pasta)
    med = {x["arquivo_origem"]: x for x in json.load(open(os.path.expanduser("~/Library/Caches/editor-reels/trilhas_medidas.json")))}
    os.makedirs(PASTA, exist_ok=True)
    cat, vistos, bloq, sfx = [], {}, [], []
    for nome in sorted(med):
        m = med[nome]
        if "erro" in m:
            continue
        lic = licenca(nome)
        if re.search(SFX, nome.lower()):
            sfx.append(nome); continue
        if lic["status"] == "bloqueada":
            bloq.append((nome, lic["fonte"])); continue
        cs = climas(nome, m)
        base = _slug(os.path.splitext(nome)[0])
        chave = " ".join(sorted(set(re.sub(r"-(mp3|m4a).*", "", base).split("-"))))   # mesma música, nome em outra ordem
        if chave in vistos:                           # mesma música em outro bitrate: fica a de maior duração/qualidade
            continue
        vistos[chave] = nome
        arq = f"{cs[0]}__{base}__{m['bpm']}bpm__{m['tom'].replace(' ', '-').replace('#', 's')}.mp3"
        destino = os.path.join(PASTA, arq)
        if not os.path.exists(destino):              # 128 kbps estéreo: trilha vai ~20 dB abaixo da voz, não perde nada
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(pasta, nome), "-vn", "-map_metadata", "-1",
                            "-ac", "2", "-ar", "44100", "-b:a", "128k", destino], check=True)
        cat.append(dict(arquivo=arq, origem=nome, climas=cs, marcas=marcas(cs, lic, nome), licenca=lic,
                        **{k: m[k] for k in ("duracao_s", "bpm", "tom", "modo", "energia", "variacao", "brilho_hz", "percussao", "lufs")}))
    for f_ in os.listdir(PASTA):                      # arquivos gerados que saíram do catálogo (ex.: duplicata)
        if f_.endswith(".mp3") and f_ not in {t["arquivo"] for t in cat}:
            os.remove(os.path.join(PASTA, f_))
    json.dump({"trilhas": cat, "bloqueadas_fora_do_repo": [{"origem": n, "motivo": f} for n, f in bloq],
               "efeitos_sonoros_fora": sfx}, open(CATALOGO, "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(f"{len(cat)} trilhas no banco | {len(bloq)} bloqueadas (fora do repo) | {len(sfx)} efeitos sonoros (fora)")
    print("licença:", Counter(t["licenca"]["status"] for t in cat), "| anúncio pago:", Counter(t["licenca"]["anuncio_pago"] for t in cat))
    print("climas:", Counter(c for t in cat for c in t["climas"]))
    print("marcas:", Counter(mm for t in cat for mm in t["marcas"]))


# ------------------------------------------------------------------ sugestão
def sugerir(clima, marca, anuncio=False, dur=None, n=6):
    cat = json.load(open(CATALOGO))["trilhas"]
    ok = []
    for t in cat:
        if t["licenca"]["status"] == "bloqueada":
            continue
        if anuncio and t["licenca"].get("anuncio_pago") == "nao":
            continue
        if marca not in t.get("marcas", []):
            continue
        if clima not in t.get("climas", []):
            continue
        if dur and t["duracao_s"] < dur:
            continue
        ok.append(t)
    ok.sort(key=lambda t: ({"sim": 0, "conferir": 1}.get(t["licenca"]["anuncio_pago"], 2), abs(t["bpm"] - 100)))
    for t in ok[:n]:
        print(f"  {t['arquivo']:60s} {t['bpm']:>3} bpm  {t['tom']:9s}  {', '.join(t['climas'])}  | {t['licenca']['status']}, anúncio: {t['licenca']['anuncio_pago']}")
    if not ok:
        print("  nenhuma trilha liberada para esse filtro")
    return ok[:n]


# ------------------------------------------------------------------ mixagem
def mixar(video, trilha, saida=None, ss=0.0, abaixo_db=None, fade=1.2):
    """trilha por baixo da fala: nível base ~20 dB abaixo da voz e ducking (abaixa mais quando ela fala).
    Retorna a diferença medida voz × trilha."""
    saida = saida or os.path.splitext(video)[0] + "_trilha.mp4"
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    voz = loudness(video)
    mus = loudness(trilha, ss=ss, dur=dur)
    alvo = (voz if voz is not None else -16) - (abaixo_db or 16)          # base ~16 LU abaixo; com o ducking fica ~20 sob a fala
    ganho = alvo - (mus if mus is not None else -14)
    fc = (f"[1:a]atrim={ss}:{ss + dur},asetpts=PTS-STARTPTS,volume={ganho:.1f}dB,"
          f"afade=t=in:st=0:d=0.6,afade=t=out:st={max(0, dur - fade):.2f}:d={fade}[m];"
          f"[0:a]asplit=2[v][sc];"
          f"[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=450:makeup=1[md];"
          f"[v][md]amix=inputs=2:normalize=0:duration=first[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", trilha, "-filter_complex", fc,
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", saida],
                   check=True)
    return saida, voz, mus, ganho


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("analisar"); a1.add_argument("pasta")
    sub.add_parser("catalogar").add_argument("pasta")
    sub.add_parser("medir-um").add_argument("arq")
    a2 = sub.add_parser("sugerir"); a2.add_argument("--clima", required=True); a2.add_argument("--marca", required=True)
    a2.add_argument("--anuncio", action="store_true"); a2.add_argument("--dur", type=float)
    a3 = sub.add_parser("mixar"); a3.add_argument("video"); a3.add_argument("trilha"); a3.add_argument("-o", "--saida")
    a3.add_argument("--ss", type=float, default=0.0); a3.add_argument("--abaixo-db", type=float)
    a = ap.parse_args()
    if a.cmd == "analisar":
        analisar(a.pasta)
    elif a.cmd == "medir-um":
        print(json.dumps(medir(a.arq), ensure_ascii=False))
    elif a.cmd == "catalogar":
        catalogar(a.pasta)
    elif a.cmd == "sugerir":
        sugerir(a.clima, a.marca, a.anuncio, a.dur)
    else:
        s, voz, mus, g = mixar(a.video, a.trilha, a.saida, a.ss, a.abaixo_db)
        print(f"pronto: {s} | fala {voz} LUFS, trilha original {mus} LUFS, ganho {g:+.1f} dB")
