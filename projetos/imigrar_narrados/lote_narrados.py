"""Imigrar · vídeos narrados (out/2026): narração gravada das cópias "aeroporto e política" + cenas de bastidores
(Terminal 3 de Guarulhos, voo, chegada aos EUA, Orlando) + legenda + trilha. Sem motion: a cena e a narração falam.

Por vídeo:
 1. narração: o melhor take de cada frase (transcrição literal alinhada das gravações), cortado no fim da palavra
    (faixa() do lote_ti) e juntado;
 2. cenas: cada cena começa numa palavra da narração (âncora); HDR do iPhone -> SDR 1080x1920 com leve realce; cena
    curta demais vira câmera lenta (gravação em 60 fps); cena horizontal (Disney) é recortada na vertical, sem distorcer;
 3. intermediário (cenas + narração) -> editor_reels.py: tira pausas e gaguejadas, legenda, gancho e CTA da Imigrar,
    enquadramento parado (a cena já é vertical);
 4. trilha por baixo da voz (trilhas.mixar, ducking).

Uso: python3 projetos/imigrar_narrados/lote_narrados.py [id ...] [--so-montar] [--reusar-montagem] [--esperado] [--sem-trilha]
"""
import json, os, shutil, subprocess, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..", "..")
sys.path.insert(0, os.path.join(RAIZ, "editor"))
sys.path.insert(0, os.path.join(RAIZ, "projetos", "imigrar_ti_ads"))
import plataforma as PLAT
import lote_ti as LT
import trilhas as TR
from auditar_fala import norm, repeticoes

BASE = "/Users/lucastoledo/Downloads/Videos Narrados"
AUDIOS = os.path.join(BASE, "Audios Scripts")
CENAS = os.path.join(BASE, "Aeroporto - Voo - EUA")
SAIDA = os.path.join(BASE, "_em_revisao")             # só vai pra prontos/ depois da auditoria
INTER = PLAT.pasta_cache("narrados_intermediarios")
SEM_TRILHA = PLAT.pasta_cache("narrados_sem_trilha")
TRILHAS = os.path.join(RAIZ, "assets", "trilhas")
LT.BRUTOS = AUDIOS
FPS, W, H = 30, 1080, 1920
COR = "eq=contrast=1.05:saturation=1.10,"               # HLG convertido sai um pouco lavado
CTA = "Comente PERFIL27 e receba sua análise de perfil"  # a narração de todos pede PERFIL27
P1, P2, A8 = "Política 1.m4a", "Política 2.m4a", "AUDIO-2026-10-23-11-13-15.m4a"   # A8: vídeo 8 na voz da Mari

# grafia da legenda: o que o Whisper literal escreve errado nessas gravações
LT.FRASES[:0] = [("perfil 27,", "PERFIL27,"), ("perfil 27.", "PERFIL27."), ("perfil 27", "PERFIL27"),
              ("qual vista americana", "qual visto americano"), ("qual vista", "qual visto"),
              ("o saio do", "sair do"), ("o site do", "sair do"), ("e movida legal", "e uma vinda legal"),
              ("vista americana", "visto americano"), ("te vi um link,", "te envio um link,"),
              ("pré -visibilidade", "previsibilidade"), ("pré-visibilidade", "previsibilidade"),
              ("terminal três", "Terminal 3"), ("terminal 3", "Terminal 3"),
              ("processos imigratórios, levam", "Processos imigratórios levam"), ("Chequiliche", "Checklist"),
              ("Perfiu 27", "PERFIL27"), ("perfus", "perfil"), ("reclamando a política", "reclamando da política"),
              ("reclamando à política", "reclamando da política"),
              ("Melhor momento pra Preparar", "O melhor momento pra preparar"),
              ("O processo de imigratórios leva meses.", "Processos imigratórios levam meses."),
              ("se mexer? Acaba", "se mexer acaba"), ("Momento certo, é agora.", "O momento certo é agora."),
              ("análise Sem", "análise sem"), ("você. Aqui na América.", "você aqui na América."),
              ("avaliação e E descubra", "avaliação e descubra"), ("frustar", "frustrar"),
              ("emergência em dólar.", "emergência em dólar?"), ("Unidos Comente", "Unidos, comente")]

# 2ª rodada (n1, n5, n6, n8): o time achou parado. Skylines picotava 15 dB a cada compasso, Contrast só batia aos 14s e a
# trilha ficava ~30 dB sob a voz (inaudível). Faixas de batida estável + base 12 LU abaixo e ducking 1.3 (~16 LU sob a fala).
# trilhas auditadas (auditor-de-trilha, 23/10): Skylines e Pray começam quase mudas e a batida entra de repente aos 6s/9s
# -> trilha_ss pula a introdução. Anúncio pago: as 4 estão "conferir" (confirmar a licença antes de impulsionar).
# id: gancho (pergunta; a resposta está na narração), trilha, pedaços da narração (arquivo, início, fim) e cenas
# (âncora = palavras onde a cena começa, arquivo, segundo da cena[, centro x do recorte vertical se a cena é horizontal])
VIDEOS = {
    "n1_terminal3_melhor_saida": dict(
        gancho="Qual é a melhor saída do Brasil 🇧🇷?",
        trilha="corporativo__powerful-indie-rock-music-by-alex-productions-promotional-vi__103bpm__D-maior.mp3",
        trilha_ss=21, trilha_abaixo=12, trilha_ducking=1.3,
        pecas=[(P1, 8.30, 10.60), (P1, 11.05, 25.10),
               # CTA: "Se você sonha, | se você tem esse sonho..." e "comente, comente perfil 27 pra fazer uma avaliação, |
               # comente perfil 27 e faça..." (recomeços que só a leitura literal mostra): fica a última versão de cada um
               (P1, 33.45, 36.40), (P1, 42.58, 49.80, "exato")],
        # 2ª versão (pedido de 23/10): cena coerente com cada frase, cortes na batida, punch-in nas longas, versão B
        ritmo=True, gancho_b="Por que todo mundo fala do Terminal 3?",
        abertura_b=("passaporte e terminal 3 03.MOV", 6.0),      # gente indo pro embarque com mala
        cenas=[(None, "terminal 3 01.MOV", 0.3),
               ("melhor saída", "IMG_4255.MOV", 8.4),
               ("Sabe por quê", "bandeira brasil e terminal 3 .MOV", 0.2),
               ("o divisor de águas", "IMG_4256.MOV", 2.0),            # escada rolante subindo pro embarque
               ("entre quem passa", "IMG_9213.MOV", 0.5),             # "reclamando da política": no celular
               ("e quem decide", "terminal 3 corredor e vista com mala caminhando.MOV", 0.5),
               ("no lugar onde", "vista bandeira eua e aguia de fundo hostpital veteranos.MOV", 8.0),
               ("Quando o avião", "aviao taxeando.MOV", 1.5),
               ("a sua única", "vista asa do aviao janela.MOV", 2.0),
               ("Se você tem", "vista sol da manha condominio eua.MOV", 2.0),
               ("comente", "IMG_4897.MOV", 5.5),
               ("e faça uma avaliação", "IMG_4680.MOV", 0.3),
               ("e descubra", "IMG_4659.MOV", 40.0),
               ("aqui nos Estados", "Chegada aroporto orlando.MP4", 0.0)]),
    "n2_pos_eleicoes": dict(
        gancho="Quem ganhar a eleição muda o seu plano?",
        trilha="corporativo__pray-anno-domini-beats__99bpm__Gs-maior.mp3", trilha_ss=9,
        pecas=[(P2, 5.85, 11.85), (P2, 12.35, 23.62), (P2, 27.12, 31.45)],
        cenas=[(None, "IMG_4292.MOV", 1.0),
               ("o Terminal 3 continua", "IMG_4301.MOV", 4.0),
               ("de quem busca", "IMG_4402.MOV", 0.5),
               ("Independente", "bandeira brasil e terminal 3 2.MOV", 0.0),
               ("o seu patrimônio", "banco safra cambio exchange.MOV", 0.5),
               ("Proteger sua família", "Mari familia indo parque disney.MOV", 1.0, 0.5),
               ("não é sobre esquerda", "IMG_4399.MOV", 0.0),
               ("é sobre inteligência", "passaporte mao e terminal 3.MOV", 1.0),
               ("comente", "vista inspiradora vidro e sol aeroporto atlanta.MOV", 1.0),
               ("e faça uma avaliação", "IMG_4679.MOV", 3.5)]),
    "n3_exodo_terminal3": dict(
        gancho="Por que as filas do Terminal 3 dobram?",
        trilha="tenso__contrast-anno-domini-beats__96bpm__D-menor.mp3",
        pecas=[(P2, 39.70, 45.25),                       # "Toda vez, | toda vez que o cenário...": a 2ª
               (P2, 46.10, 52.10), (P2, 52.68, 55.90), (P2, 60.45, 61.75),
               (P2, 63.88, 66.60, "exato"),             # "Se você sonha morar, | se você sonha em morar e trabalhar"
               (P2, 69.00, 75.87)],                     # "comente perfil 27, | comente perfil 27 para fazer..."
        cenas=[(None, "lula e terminal 3.MOV", 2.5),
               ("as filas", "passaporte e terminal 3 03.MOV", 3.5),
               ("A diferença", "IMG_9213.MOV", 0.5),
               ("e quem desembarca", "vista asa pousando.MOV", 5.0),
               ("de primeiro mundo", "250 anos america numeros vista.MOV", 0.5),
               ("Planejamento", "passaporte e terminal 3 fundo.MOV", 0.5),
               ("esperar o resultado", "IMG_4267.MOV", 0.0),
               ("pode ser tarde", "aviao taxeando 2.MOV", 3.0),
               ("Se você sonha", "vista inspiradora sol da manha condominio eua.MOV", 3.0),
               ("comente", "IMG_4665.MOV", 0.5),
               ("fazer a nossa", "aeroporto, carregando passaporte mala e vista da janela do aeroporto para aviao.MOV", 0.0),
               ("e descobrir", "IMG_4848.MOV", 1.0)]),
    "n4_momento_certo": dict(
        gancho="Quando é a hora certa de sair do Brasil 🇧🇷?",
        trilha="corporativo__anno-domini-beats-glass__99bpm__Fs-maior.mp3",
        pecas=[(P2, 471.80, 473.08, "exato"),           # "O melhor momento para | (pre-) ... para preparar"
               (P2, 474.91, 478.30, "exato"), (P2, 482.95, 485.30), (P2, 513.68, 516.20),
               (P2, 523.05, 524.62), (P2, 531.22, 534.25), (P2, 554.33, 556.85),
               (P2, 559.14, 561.85, "exato"),           # sem o "Agora," colado (repetia o "é agora." de antes)
               (P2, 566.62, 571.95, "exato")],          # "(comente aqui abaixo e faça uma análise) | sem custos..."
        cenas=[(None, "departures embarque placa.MOV", 0.5),
               ("não é depois", "IMG_4329.MOV", 0.0),
               ("Processos", "IMG_4330.MOV", 5.0),
               ("Quem espera", "IMG_4294.MOV", 0.0),
               ("acaba adiando", "vista janela.MOV", 2.0),
               ("E tornando", "IMG_4447.MOV", 1.0),
               ("momento certo", "IMG_4408.MOV", 6.0),
               ("Comente", "IMG_4671.MOV", 0.0),
               ("Descubra", "vista turbina chegando orlando.MOV", 5.0)]),
    "n5_custo_incerteza": dict(
        gancho="Qual é a moeda mais cara do Brasil 🇧🇷?",
        trilha="tenso__culture-anno-domini-beats__108bpm__G-menor.mp3", trilha_ss=9.5, trilha_abaixo=10,
        trilha_ducking=1.3,                             # muito grave: some no celular se for mais baixa
        pecas=[(P2, 93.40, 97.45), (P2, 97.82, 103.85),
               (P2, 115.95, 120.20, "exato"),           # 6 tentativas de "está trocando a ansiedade do noticiário": a última
               (P2, 123.25, 125.75, "exato"),           # "Você sonha com, | você sonha em morar..."
               (P2, 125.85, 128.46, "exato"),           # "Comente perfil 27, faça uma avaliação e"
               (P2, 130.57, 132.30, "exato")],          # "(comente perfil 27 e) | descubra qual o melhor caminho"
        ritmo=True, gancho_b="O dólar alto é o seu maior medo?",
        abertura_b=("banco safra cambio exchange.MOV", 0.5),
        cenas=[(None, "IMG_4388.MOV", 0.3),
               ("é a incerteza", "IMG_4261.MOV", 0.5),
               ("Viver no Brasil", "IMG_4310.MOV", 0.3),             # "tensão constante": labirinto de filas
               ("Quem decide", "IMG_4391.MOV", 0.0),                 # mala indo pro embarque
               ("Está trocando", "IMG_9213.MOV", 5.0),               # "ansiedade do noticiário": no celular
               ("por estabilidade", "vista sol da manha condominio eua.MOV", 12.0),
               ("Você sonha", "IMG_4884.MOV", 0.5),
               ("Comente", "IMG_4897.MOV", 6.0),
               ("faça uma avaliação", "IMG_4680.MOV", 3.0),
               ("e descubra", "vista inspiradora vidro e sol aeroporto atlanta.MOV", 5.0)]),
    "n6_nao_dava_mais_pra_esperar": dict(
        gancho="Até quando esperar o Brasil 🇧🇷 mudar?",
        trilha="energetico__sport-future-bass-energy-by-alex-productions-digital-love__99bpm__As-maior.mp3",
        trilha_ss=21, trilha_abaixo=12, trilha_ducking=1.3,
        pecas=[(P2, 152.75, 158.25),
               (P2, 235.90, 252.40),                    # 3ª tentativa de "a gente passa anos esperando a economia"
               (P2, 326.20, 335.12, "exato"), (P2, 337.10, 338.40, "exato")],   # "aqui, | aqui na América"
        ritmo=True, gancho_b="Você ainda espera o Brasil 🇧🇷 mudar?",
        abertura_b=("IMG_4329.MOV", 0.0),
        cenas=[(None, "IMG_4302.MOV", 0.0),
               ("que eu entendi", "IMG_4276.MOV", 0.0),
               ("A gente passa", "IMG_4266.MOV", 2.0),
               ("ou o político", "IMG_4387.MOV", 0.0),               # "esperando": mala parada diante do painel
               ("Até perceber", "IMG_4401.MOV", 0.0),
               ("de buscar um lugar", "IMG_4659.MOV", 25.0),
               ("onde o trabalho", "IMG_4849.MOV", 5.0),             # Orlando: comércio, trânsito
               ("qualidade de vida", "vista sol da manha condominio eua.MOV", 18.0),
               ("segurança", "vista escola criancas eua.MOV", 3.0),
               ("e previsibilidade", "vista carro waymo orlando dirigindo autonomo.MOV", 1.0),
               ("Se você sonha", "aeroporto bandeira eua virando camera.MOV", 2.0),
               ("comente", "IMG_4680.MOV", 5.0),
               ("e faça uma avaliação", "IMG_4679.MOV", 4.0),
               ("e descubra", "IMG_4655.MOV", 12.0)]),
    "n8_futuro_dos_filhos": dict(
        gancho="POV: o futuro dos seus filhos vale mais que qualquer debate político",
        trilha="corporativo__music-aoeris-resonate-bc-release__112bpm__B-maior.mp3", trilha_ss=70.6,
        trilha_abaixo=13, trilha_ducking=1.3,              # forte nos médios: 1 dB mais baixa
        pecas=[(A8, 1.20, 33.30)],
        # gancho fala dos filhos: abre nos filhos; "sair do Brasil" no embarque; "qual visto" com passaporte na mão;
        # "comenta" no celular; fecha na família (antes: Disney em "sair do Brasil", painel em "qual visto")
        ritmo=True, gancho_b="Seus filhos merecem crescer com segurança?",
        abertura_b=("Mari e filhos nos bondinhos da disney.MOV", 0.5, 0.44),
        cenas=[(None, "Mari familia indo parque disney.MOV", 1.0, 0.5),
               ("Estados Unidos", "aeroporto bandeira eua virando camera.MOV", 0.5),
               ("e vê a qualidade", "vista inspiradora sol da manha condominio eua.MOV", 4.0),
               ("as escolas", "vista escola criancas eua.MOV", 4.0),
               ("e a segurança", "Mari e filhos nos bondinhos da disney.MOV", 3.0, 0.44),
               ("qualquer dúvida", "passaporte e terminal 3 fundo.MOV", 0.5),
               ("sair do Brasil", "terminal 3 corredor e vista com mala caminhando.MOV", 2.0),
               ("desaparece", "vista asa do aviao janela.MOV", 3.0),
               ("Mas para garantir", "Mari familia parque disney carros.MOV", 1.0, 0.40),
               ("e uma vinda legal", "IMG_4380.MOV", 0.0),       # só o começo tem o passaporte (depois vira o painel)
               ("para a sua família", "Mari e filhos nos bondinhos da disney.MOV", 12.0, 0.44),
               ("aqui nos Estados", "250 anos america numeros vista.MOV", 0.5),
               ("o primeiro passo", "IMG_4335.MOV", 0.0),
               ("qual visto", "passaporte mao e terminal 3.MOV", 0.3),
               ("Comenta", "IMG_9213.MOV", 0.5),
               ("para fazer uma análise", "IMG_4330.MOV", 6.0),
               ("e te mostrar", "IMG_4680.MOV", 0.5),
               ("para você e", "Mari familia indo parque disney.MOV", 5.0, 0.5)]),
    "n11_erro_da_emocao": dict(
        gancho="Qual o maior erro do brasileiro nesta eleição?",
        trilha="tenso__dark-tranquility-anno-domini-beats__81bpm__Fs-menor.mp3", trilha_ss=6,
        pecas=[(P2, 356.74, 360.88, "exato"),           # "Comprar passagem pro Terminal 3 no impulso, | comprar..."
               (P2, 373.33, 382.20), (P2, 391.72, 399.10),
               (P2, 404.28, 405.62, "exato"),           # "Comente perfil 27" (o "e faça" daqui repetia o seguinte)
               (P2, 408.70, 414.10)],
        cenas=[(None, "IMG_4274.MOV", 0.0),
               ("é o maior erro", "IMG_4406.MOV", 0.5),
               ("Mudar de país", "empurrando mala embarque.MOV", 0.0),
               ("sem um visto", "IMG_9212.MOV", 8.0),
               ("é o caminho mais rápido", "IMG_4450.MOV", 3.0),
               ("Decisões grandes", "passaporte e terminal 3.MOV", 0.0),
               ("o primeiro passo", "IMG_4363.MOV", 1.0),
               ("Comente", "IMG_4668.MOV", 2.0),
               ("faça uma análise", "IMG_4670.MOV", 1.0),
               ("e descubra", "vista carro waymo orlando dirigindo autonomo.MOV", 1.0)]),
    "n12_tres_perguntas": dict(
        gancho="Vai sair do Brasil 🇧🇷 depois da eleição?",
        trilha="corporativo__anno-domini-beats-glass__99bpm__Fs-maior.mp3",
        pecas=[(P2, 422.15, 427.90), (P2, 434.30, 437.70),
               (P2, 440.20, 442.45, "exato"),           # "Você tem reserva de, | você tem reserva de emergência"
               (P2, 447.75, 452.75), (P2, 453.10, 457.50, "exato"),
               (P2, 458.95, 466.55)],                   # "Comente, | comente aqui abaixo o perfil 27...": o 2º
        cenas=[(None, "IMG_4279.MOV", 0.0),
               ("Não embarque", "IMG_4391.MOV", 0.0),
               ("Seu visto", "IMG_4335.MOV", 0.0),
               ("Você tem reserva", "IMG_4411.MOV", 1.0),
               ("seu plano conta", "Mari familia parque disney carros.MOV", 2.5, 0.40),
               ("Se faltar", "IMG_4413.MOV", 0.0),
               ("O primeiro passo", "IMG_9211.MOV", 6.0),
               ("Comente", "IMG_4897.MOV", 6.0),
               ("e descubra", "IMG_4659.MOV", 45.0)]),
}


def probe(arq):
    st = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", arq],
                                   capture_output=True, text=True).stdout)
    v = next(s for s in st["streams"] if s["codec_type"] == "video")
    return v, float(st["format"]["duration"])


def ancorar(pal, cenas):
    """tempo (no intermediário) em que cada cena começa: o início da palavra-âncora, um pouco antes."""
    tempos, j = [], 0
    toks = [norm(w["w"]) for w in pal]
    for anc, *_ in cenas:
        if anc is None:
            tempos.append(0.0); continue
        alvo = [norm(x) for x in anc.split()]
        for i in range(j, len(toks) - len(alvo) + 1):
            if toks[i:i + len(alvo)] == alvo:
                tempos.append(max(0.0, pal[i]["s"] - 0.10)); j = i + len(alvo); break
        else:
            raise SystemExit(f"âncora não achada: «{anc}» em: {' '.join(w['w'] for w in pal[j:j + 40])}")
    return tempos


def trecho_cena(arq, ss, dur, cx, dst, zoom=1.0):
    """dur segundos da cena a partir de ss, SDR 1080x1920; se a cena acaba antes, câmera lenta até caber.
    zoom > 1: punch-in (recorte central da mesma proporção, nunca distorce)."""
    src = os.path.join(CENAS, arq)
    v, total = probe(src)
    hdr = v.get("color_transfer") in ("arib-std-b67", "smpte2084")
    args, filtro = PLAT.entrada_hdr(v) if hdr else ([], "")
    ss = max(0.0, min(ss, total - 0.3))
    disp = total - ss - 0.05
    lento = max(1.0, dur / disp)
    if lento > 1.0 and ss > 0:                           # antes de desacelerar, recua o começo
        ss = max(0.0, total - dur - 0.05); disp = total - ss - 0.05; lento = max(1.0, dur / disp)
    if lento > 2.5:
        print(f"  ⚠ cena {arq} curta: {disp:.1f}s pra {dur:.1f}s (câmera lenta {lento:.1f}x)")
    rot = next((int(sd.get("rotation", 0)) for sd in v.get("side_data_list", []) if "rotation" in sd), 0) % 360
    deitado = (v["width"] > v["height"]) == (rot in (0, 180))
    recorte = f"crop=ih*9/16:ih:(iw-ih*9/16)*{cx}:0," if deitado else ""     # horizontal: faixa vertical, sem distorcer
    n = max(1, int(round(dur * FPS)))
    punch = f"crop=iw/{zoom:.3f}:ih/{zoom:.3f},scale={W}:{H}," if zoom > 1.0 else ""
    vf = (f"{filtro}{recorte}{COR}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{punch}"
          f"setpts={lento:.4f}*(PTS-STARTPTS),fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-ss", f"{ss:.3f}", "-t", f"{min(disp, dur / lento) + 0.2:.3f}",
                    "-i", src, "-vf", vf, "-frames:v", str(n), "-an", *PLAT.h264("20M"), dst + ".tmp.mp4"], check=True)
    zerar_rotacao(dst + ".tmp.mp4", dst)
    return n


def zerar_rotacao(src, dst):
    """o -noautorotate (HDR do iPhone) leva a matriz de rotação pro arquivo novo, que já saiu de pé: sem zerar, o editor
    gira de novo e a cena sai DEITADA (aconteceu no 1º render dos narrados)."""
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-display_rotation:v", "0", "-i", src, "-c", "copy", dst], check=True)
    os.remove(src)


def montar(id_, cfg):
    """narração (pedaços dos takes) + cenas ancoradas nas palavras -> intermediário e a transcrição dele."""
    pal, total, narr = narracao(id_, cfg)
    inicios = ancorar(pal, cfg["cenas"]) + [total]
    segs = [(inicios[k], inicios[k + 1], arq, ss, cx[0] if cx else 0.5, 1.0)
            for k, (anc, arq, ss, *cx) in enumerate(cfg["cenas"])]
    return montar_cenas(id_, segs, narr)


def narracao(id_, cfg):
    """pedaços dos takes -> narração (wav) e a transcrição (editor/transcricoes/<id>.json)."""
    pal, segs, t, filtros, entradas = [], [], 0.0, [], []
    for k, (arq, a, b, *modo) in enumerate(cfg["pecas"]):
        ini, fim, ws = LT.faixa(arq, a, b, exato="exato" in modo)
        dur = fim - ini
        entradas += ["-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", os.path.join(AUDIOS, arq)]
        filtros.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=mono,atrim=duration={dur:.3f},asetpts=PTS-STARTPTS,"
                       f"afade=t=in:d=0.012,afade=t=out:st={max(0, dur - 0.012):.3f}:d=0.012[a{k}]")
        s0 = len(pal)
        for w in ws:
            pal.append({"w": w["w"], "s": round(w["s"] - ini + t, 3), "e": round(min(w["e"], fim) - ini + t, 3)})
        segs.append({"s": round(t, 3), "e": round(t + dur, 3), "t": " ".join(p["w"] for p in pal[s0:])})
        t += dur
    total = t
    narr = os.path.join(INTER, id_ + ".narracao.wav")
    n = len(cfg["pecas"])
    subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex",
                    ";".join(filtros) + ";" + "".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1[a]",
                    "-map", "[a]", "-c:a", "pcm_s16le", narr], check=True)
    pal = LT.juntar_numeros(LT.nomes(LT.green_card(LT.corrigir_frases(pal))))
    for w in pal:                                      # take de cada palavra: alinhamento e corte não passam da emenda
        w["pedaco"] = max([k for k, sg in enumerate(segs) if sg["s"] <= max(w["s"], 0.0) + 0.001] or [0])
    reps = repeticoes(pal)
    for i, m in reps:
        print(f"  ⚠ REPETIÇÃO em {id_}: '{' '.join(p['w'] for p in pal[i:i + m])}' em {pal[i]['s']:.2f}s")
    if reps and "--forcar" not in sys.argv:
        raise SystemExit(f"{id_}: fala repetida nos pedaços, corrija antes de renderizar")
    texto = " ".join(p["w"] for p in pal)
    print(f"  narração ({total:.1f}s): {texto}")
    json.dump({"texto": texto, "palavras": pal, "segmentos": segs, "pedacos": [[sg["s"], sg["e"]] for sg in segs]},
              open(os.path.join(LT.TRANSC, id_ + ".json"), "w"), ensure_ascii=False, indent=1)
    return pal, total, narr


def montar_cenas(nome, segs, narr):
    """segs = [(início, fim no intermediário, arquivo, segundo da cena, centro x, zoom)] -> INTER/<nome>.mov."""
    partes, lista = [], os.path.join(INTER, nome + ".cenas.txt")
    for k, (t0, t1, arq, ss, cx, zoom) in enumerate(segs):
        f0, f1 = int(round(t0 * FPS)), int(round(t1 * FPS))
        if f1 <= f0:
            continue
        dst = os.path.join(INTER, f"{nome}.cena{k:02d}.mp4")
        trecho_cena(arq, ss, (f1 - f0) / FPS, cx, dst, zoom)
        partes.append(dst)
        print(f"  cena {k:2d} {f0 / FPS:6.2f}-{f1 / FPS:6.2f}s  {arq}{'  (punch-in)' if zoom > 1 else ''}")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in partes))
    out = os.path.join(INTER, nome + ".mov")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-i", narr,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "pcm_s16le", "-shortest", out], check=True)
    return out


# ------------------------------------------------------------------ ritmo: corte na batida da trilha + versão B
PLANO_ARGS = ["--alinhar", "--vad", "--tirar-hesitacoes", "--respiro", "0.28", "--proteger-palavra", "0.40",
              "--manter-perguntas"]                    # o que decide o plano de cortes (igual no plano e no render)


def saida_de(cortes, t):
    """tempo do intermediário -> tempo do vídeo pronto (o editor tira as pausas)."""
    acc = 0.0
    for c in cortes:
        if t < c["s"]:
            return acc
        if t < c["e"]:
            return acc + t - c["s"]
        acc += c["e"] - c["s"]
    return acc


def intermediario_de(cortes, T):
    acc = 0.0
    for c in cortes:
        d = c["e"] - c["s"]
        if T < acc + d:
            return c["s"] + T - acc
        acc += d
    return cortes[-1]["e"]


def batidas(trilha, ss, dur):
    """tempos das batidas da trilha a partir de ss (= tempo do vídeo pronto, a trilha entra no 0)."""
    import librosa
    y, sr = librosa.load(trilha, sr=22050, mono=True, offset=ss, duration=dur + 2)
    _, b = librosa.beat.beat_track(y=y, sr=sr, units="time")
    return [float(x) for x in b]


def no_ritmo(id_, cfg, pal, total, narr):
    """1) plano de cortes do editor (narração sobre fundo preto); 2) cada troca de cena vai pra batida mais próxima da
    palavra-âncora (até 0,30s antes / 0,15s depois); 3) cena longa (>2,4s) ganha um punch-in na batida do meio.
    Devolve os trechos no tempo do intermediário (o editor só tira pausa: a troca cai na batida no vídeo pronto)."""
    preto = os.path.join(INTER, id_ + ".mov")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s={W}x{H}:r={FPS}", "-i", narr,
                    "-map", "0:v", "-map", "1:a", "-shortest", *PLAT.h264("2M"), "-c:a", "pcm_s16le", preto], check=True)
    plano = os.path.join(INTER, id_ + ".plano.json")
    subprocess.run([sys.executable, os.path.join(RAIZ, "editor", "editor_reels.py"), preto, *PLANO_ARGS,
                    "--json-cortes", plano], check=True, capture_output=True)
    cortes = json.load(open(plano))
    dur = sum(c["e"] - c["s"] for c in cortes)
    bat = batidas(os.path.join(TRILHAS, cfg["trilha"]), cfg.get("trilha_ss", 0.0), dur)
    pal = json.load(open(os.path.join(LT.TRANSC, id_ + ".json")))["palavras"]      # já alinhada pelo editor
    ancoras = [saida_de(cortes, t) for t in ancorar(pal, cfg["cenas"])]
    pontos = [0.0]
    for T in ancoras[1:]:
        perto = [b for b in bat if -0.30 <= b - T <= 0.15]
        Tn = min(perto, key=lambda b: abs(b - T)) if perto else T
        pontos.append(Tn if Tn - pontos[-1] >= 0.7 else T)
    pontos.append(dur)
    trechos = []                                         # (T0, T1, k da cena, zoom, avanço dentro da cena)
    for k in range(len(cfg["cenas"])):
        T0, T1, zoom, avanco = pontos[k], pontos[k + 1], 1.0, 0.0
        while T1 - T0 > 2.4:
            meio = (T0 + min(T1, T0 + 4.0)) / 2 if T1 - T0 > 4.0 else (T0 + T1) / 2
            ok = [b for b in bat if T0 + 0.9 <= b <= T1 - 0.9]
            corte = min(ok, key=lambda b: abs(b - meio)) if ok else meio
            trechos.append((T0, corte, k, zoom, avanco))
            avanco += corte - T0; T0 = corte; zoom = 1.12 if zoom == 1.0 else 1.0
        trechos.append((T0, T1, k, zoom, avanco))
    print(f"  ritmo: {len(bat)} batidas, {len(trechos)} trechos de cena em {dur:.1f}s")
    return [(intermediario_de(cortes, T0) if T0 > 0 else 0.0, intermediario_de(cortes, T1) if T1 < dur else total,
             k, zoom, avanco) for T0, T1, k, zoom, avanco in trechos]


def versoes(id_, cfg):
    """[(sufixo, gancho, cenas)]: vídeo com "gancho_b" tem versão B (outro gancho e outra cena de abertura)."""
    if not cfg.get("gancho_b"):
        return [("", cfg["gancho"], cfg["cenas"])]
    b = list(cfg["cenas"])
    b[0] = (None, *cfg["abertura_b"])
    return [("_A", cfg["gancho"], cfg["cenas"]), ("_B", cfg["gancho_b"], b)]


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(VIDEOS)
    for id_ in ids:
        cfg = VIDEOS[id_]
        print(f"\n=== {id_}")
        try:
            if cfg.get("ritmo"):
                pal, total, narr = narracao(id_, cfg)
                trechos = no_ritmo(id_, cfg, pal, total, narr)
                videos = []
                for suf, gancho, cenas in versoes(id_, cfg):
                    shutil.copy(os.path.join(LT.TRANSC, id_ + ".json"), os.path.join(LT.TRANSC, id_ + suf + ".json"))
                    segs = [(t0, t1, cenas[k][1], cenas[k][2] + avanco, (cenas[k][3:] or [0.5])[0], zoom)
                            for t0, t1, k, zoom, avanco in trechos]
                    videos.append((suf, gancho, montar_cenas(id_ + suf, segs, narr)))
            else:
                pronto = os.path.join(INTER, id_ + ".mov")
                videos = [("", cfg["gancho"], pronto if "--reusar-montagem" in sys.argv and os.path.exists(pronto)
                           else montar(id_, cfg))]
        except SystemExit as e:
            print("  PULADO:", e); continue
        if "--so-montar" in sys.argv:
            continue
        for suf, gancho, video in videos:
            nome = f"imigrar_narrado_{id_}{suf}"
            tem_trilha = cfg.get("trilha") and "--sem-trilha" not in sys.argv
            LT.rodar_editor([sys.executable, os.path.join(RAIZ, "editor", "editor_reels.py"), video, "--marca", "imigrar",
                             "--gancho", gancho, "--seg-gancho", "4.2", "--cta", CTA, "--aperto", "1.0", "--punch", "1.0",
                             "--crop-fixo", *PLANO_ARGS, "--y-legenda", "0.62",
                             "--nome", nome, "--saida", SEM_TRILHA if tem_trilha else SAIDA], nome)
            if tem_trilha and "--esperado" not in sys.argv:
                _, voz, mus, ganho = TR.mixar(os.path.join(SEM_TRILHA, nome + ".mp4"), os.path.join(TRILHAS, cfg["trilha"]),
                                              os.path.join(SAIDA, nome + ".mp4"), ss=cfg.get("trilha_ss", 0.0),
                                              abaixo_db=cfg.get("trilha_abaixo"), ducking=cfg.get("trilha_ducking", 6))
                print(f"  trilha {cfg['trilha'][:40]}: voz {voz} LUFS, trilha {mus} -> {ganho:+.1f} dB")


if __name__ == "__main__":
    main()
