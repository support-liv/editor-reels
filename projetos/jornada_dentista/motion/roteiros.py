#!/usr/bin/env python3
"""Roteiros de motion (Imigrar) dos 15 shorts da live Jornada do dentista. Gera S01.json ... S15.json aqui.

    python3 projetos/jornada_dentista/motion/roteiros.py
    python3 motion/gerar_liv.py projetos/jornada_dentista/motion/S01.json

Tempos em segundos do short pronto (palavras/S##.json, exportado com `lote.py palavras`). DUR = duração da fala
(`--tempos-palavras`); o motion dura fala + cauda de 3,8s, com o CTA "Veja a live completa no canal" na cauda.
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
DUR = {"S01": 37.65, "S02": 31.37, "S03": 35.05, "S04": 27.86, "S05": 52.32, "S06": 50.45, "S07": 68.28, "S08": 12.00,
       "S09": 56.57, "S10": 63.10, "S11": 67.48, "S12": 82.14, "S13": 46.19, "S14": 68.07, "S15": 27.48}
BASE = {"largura": 1080, "altura": 1920, "tela_dividida": True, "marca": "imigrar"}


def L(texto, t, y, **k):
    return dict({"tipo": "linha", "texto": texto, "t": t, "y": y}, **k)


def R(texto, t, y=250):
    return {"tipo": "rotulo", "texto": texto, "t": t, "y": y}


def cta(k):
    return {"tipo": "cta", "t0": round(DUR[k] + 0.05, 2), "t1": round(DUR[k] + 3.88, 2), "painel": "cheio",
            "acima": "Veja a", "palavra": "live completa", "texto": "no canal", "tam_texto": 84}


def cena(t0, t1, cor, fundo, *els):
    return {"t0": t0, "t1": t1, "cor": cor, "fundo_anim": fundo, "elementos": list(els)}


ROTEIROS = {
    "S01": [
        cena(3.6, 10.4, "azul", "pontos", R("você investiu em", 3.7),
             {"tipo": "checklist", "y": 320, "tam": 70, "passo": 100, "itens": [
                 {"texto": "graduação", "t": 3.7}, {"texto": "curso", "t": 5.3}, {"texto": "especialização", "t": 5.5},
                 {"texto": "novas tecnologias", "t": 6.9}, {"texto": "técnicas", "t": 8.4}, {"texto": "várias coisas", "t": 9.3}]}),
        cena(17.3, 22.0, "preto", "grade", L("quantas vezes", 17.7, 300, tam=110), L("por semana", 18.4, 420, tam=110),
             L("você fica frustrado", 18.9, 560, cor="destaque", tam=100), L("com a sua carreira?", 20.9, 700, tam=80)),
        cena(24.9, 29.8, "rosa", "circulos", R("o pensamento", 25.0),
             {"tipo": "chat", "y": 320, "tam": 60, "itens": [{"texto": "É só isso que tem pra mim?", "t": 25.0},
                                                            {"texto": "Fiz tudo isso pra chegar aqui?", "t": 26.3},
                                                            {"texto": "Tô com um teto na cabeça.", "t": 28.3}]}),
        cena(30.9, 37.65, "azul", "faixas",
             {"tipo": "status", "titulo": "e daqui pra frente?", "y": 300, "tam": 58, "itens": [
                 {"texto": "vida futura", "t": 31.3, "status": "andamento", "selo": "?"},
                 {"texto": "atendimentos", "t": 32.6, "status": "andamento", "selo": "?"},
                 {"texto": "carreira", "t": 34.0, "status": "andamento", "selo": "?"},
                 {"texto": "família", "t": 36.9, "status": "andamento", "selo": "?"}]}),
    ],
    "S02": [
        cena(3.6, 8.4, "rosa", "pontos", R("você sabe da sua", 3.7),
             {"tipo": "checklist", "y": 320, "tam": 78, "passo": 112, "itens": [{"texto": "qualificação", "t": 4.8},
                                                                               {"texto": "potencial", "t": 6.8}]}),
        cena(10.1, 16.9, "preto", "grade", L("o ambiente", 10.6, 300, tam=120), L("não permite crescer", 11.6, 430, cor="destaque", tam=100),
             L("profissão sucateada", 15.6, 580, tam=90)),
        cena(17.3, 24.6, "azul", "circulos", R("a conta não fecha", 17.4),
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Você cobra", "texto": "cada vez mais barato", "t": 17.8, "tam": 90},
                 {"titulo": "Você investiu", "texto": "muito para aprender", "t": 20.2, "tam": 90}]},
             L("concorrência que não bate com a sua qualidade", 22.5, 680, tam=56, peso=700)),
        cena(27.8, 31.37, "rosa", "faixas", L("se você não se diminuir,", 28.0, 300, tam=90),
             L("talvez você não caiba", 29.4, 430, cor="destaque", tam=96), L("nessa esfera.", 30.3, 580, tam=110)),
    ],
    "S03": [
        cena(3.4, 10.1, "azul", "pontos", R("a trajetória da Júlia", 3.5),
             {"tipo": "etapas", "y": 320, "tam": 64, "passo": 124, "itens": [
                 {"texto": "formada em Santa Catarina", "t": 3.5}, {"texto": "Cuiabá (MT)", "t": 5.8},
                 {"texto": "residência em bucomaxilo", "t": 8.2}]}),
        cena(11.0, 15.9, "preto", "grade", R("de volta", 11.1),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 110, "itens": [
                 {"texto": "pronto-socorro", "t": 12.0}, {"texto": "hospitais", "t": 12.7}, {"texto": "aulas de pós", "t": 13.7}]}),
        cena(21.8, 26.0, "rosa", "circulos", L("conheci o André,", 22.2, 300, tam=110), L("São Paulo", 23.6, 430, cor="destaque", tam=140),
             L("a gente casou", 24.3, 610, tam=96)),
        cena(27.5, 35.05, "branco", "faixas", L("oficial do", 27.9, 300, tam=110),
             L("Exército Brasileiro", 28.7, 430, cor="destaque", tam=110), L("até fevereiro deste ano:", 30.0, 590, tam=84),
             L("hospital militar", 32.3, 710, tam=110)),
    ],
    "S04": [
        cena(4.8, 11.9, "azul", "grade", R("o André", 4.9),
             {"tipo": "etapas", "y": 320, "tam": 64, "passo": 124, "itens": [
                 {"texto": "residência", "t": 5.4}, {"texto": "implantodontia", "t": 7.9}, {"texto": "10 anos de aula", "t": 8.8}]}),
        cena(12.6, 21.6, "preto", "circulos", R("a vida clínica", 12.9),
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Consultório", "texto": "consultório particular", "t": 14.1, "tam": 90, "sync_t": 15.0, "destaque_t": 17.8},
                 {"titulo": "Hospital", "texto": "pronto-socorro, plantão", "t": 19.5, "tam": 90, "sync_t": 20.3}]}),
        cena(24.0, 27.86, "rosa", "pontos", L("minha paixão:", 24.5, 300, tam=110),
             L("ministrar aula", 25.6, 430, cor="destaque", tam=120), L("sempre da docência.", 26.5, 590, tam=90)),
    ],
    "S05": [
        cena(3.6, 10.2, "azul", "grade", R("o sonho", 3.65), L("algo a mais", 3.7, 310, tam=120),
             L("pra nossa família", 4.0, 440, cor="destaque", tam=110), L("mesmo bem posicionados", 8.3, 600, tam=76, peso=700)),
        cena(14.0, 17.9, "preto", "circulos", R("a decisão", 14.3),
             {"tipo": "cartoes", "y": 320, "alt": 280, "itens": [
                 {"titulo": "Familiar", "texto": "vocês juntos", "t": 15.8, "destaque_t": 16.1},
                 {"titulo": "De futuro", "texto": "daqui a 10 anos", "t": 16.9, "destaque_t": 17.4}]}),
        cena(19.6, 23.4, "rosa", "pontos",
             {"tipo": "contador", "de": 0, "ate": 10, "prefixo": "daqui a ", "sufixo": " anos", "t": 19.9, "dur": 0.5, "y": 300, "tam": 130},
             L("graças a Deus", 22.1, 500, tam=110), L("a gente fez isso.", 22.7, 630, cor="destaque", tam=100)),
        cena(36.2, 43.8, "azul", "faixas",
             {"tipo": "status", "titulo": "o que pesa na decisão", "y": 300, "tam": 58, "itens": [
                 {"texto": "só dinheiro", "t": 36.7, "status": "negado", "selo": "não só", "selo_t": 38.0},
                 {"texto": "sociedade", "t": 39.8, "status": "ok", "selo": "sim"},
                 {"texto": "tranquilidade", "t": 41.1, "status": "ok", "selo": "sim"},
                 {"texto": "qualidade de vida", "t": 42.0, "status": "ok", "selo": "sim"}]}),
        cena(50.0, 52.32, "branco", "grade", L("poder ficar mais", 50.4, 300, tam=110), L("com a família", 51.0, 430, cor="destaque", tam=120)),
    ],
    "S06": [
        cena(3.6, 7.9, "azul", "pontos", R("a prova do Board", 3.65), L("a prova que inicia", 3.9, 310, tam=110),
             L("a vida nos EUA 🇺🇸", 5.1, 440, cor="destaque", tam=110), L("ano passado", 6.6, 590, tam=90)),
        cena(11.0, 16.8, "rosa", "grade", R("a partir daí", 11.1), L("fundar a empresa", 12.1, 310, tam=110),
             L("auxiliar nossos alunos", 13.1, 440, cor="destaque", tam=96), L("a passar por esse processo", 15.3, 590, tam=70, peso=700)),
        cena(17.3, 23.3, "preto", "circulos", R("hoje", 17.4),
             {"tipo": "contador", "de": 0, "ate": 95, "sufixo": "%", "t": 18.4, "dur": 0.8, "y": 300, "tam": 240},
             L("de aprovação", 19.3, 580, cor="destaque", tam=110), L("um número bem alegre", 20.8, 730, tam=80)),
        cena(33.6, 47.3, "branco", "faixas",
             {"tipo": "status", "titulo": "essa porta é só pra…", "y": 300, "tam": 56, "itens": [
                 {"texto": "privilegiados", "t": 34.2, "status": "negado", "selo": "não"},
                 {"texto": "quem está na prática", "t": 36.4, "status": "negado", "selo": "não", "sync_t": 36.3},
                 {"texto": "quem está na docência", "t": 38.4, "status": "negado", "selo": "não", "sync_t": 38.3},
                 {"texto": "quem está na pesquisa", "t": 41.0, "status": "negado", "selo": "não", "sync_t": 40.9},
                 {"texto": "o Einstein", "t": 45.0, "status": "negado", "selo": "não!", "selo_t": 47.4}]}),
        cena(47.6, 50.45, "rosa", "grade", L("é uma porta", 47.8, 300, tam=120), L("pra todo mundo", 48.2, 430, cor="destaque", tam=120),
             L("que se organiza.", 48.9, 580, tam=100)),
    ],
    "S07": [
        cena(3.6, 8.4, "azul", "pontos", R("o jeito comum", 3.65),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Alguém fez…", "t": 3.6},
                                                            {"texto": "Poxa, podia ser interessante.", "t": 5.2},
                                                            {"texto": "Quem sabe me cabe?", "t": 6.8}]}),
        cena(9.2, 14.0, "rosa", "grade", L("mirando o processo", 9.6, 300, tam=100), L("do outro:", 10.4, 420, tam=100),
             L("o primeiro erro", 11.4, 560, cor="destaque", tam=110), L("cada processo é individual.", 12.7, 710, tam=70, peso=700)),
        cena(20.0, 27.3, "preto", "faixas", R("sempre tem alguém", 20.3), L("com receita pronta:", 21.1, 310, cor="destaque", tam=90),
             {"tipo": "chat", "y": 470, "tam": 62, "itens": [{"texto": "Todo dentista é EB-1!", "t": 23.2, "lado": "esq"},
                                                            {"texto": "Todo dentista é EB-2 NIW!", "t": 24.5, "lado": "esq"},
                                                            {"texto": "Todo nada.", "t": 26.4}]}),
        cena(34.7, 38.1, "branco", "circulos", R("em paralelo", 34.9),
             {"tipo": "colunas", "y": 320, "alt": 260, "itens": [{"titulo": "Imigração", "t": 36.9, "tam": 100},
                                                               {"titulo": "Carreira", "t": 37.5, "tam": 100}]}),
        cena(45.4, 56.2, "azul", "pontos", R("vocês precisam de", 45.6), L("duas engrenagens", 46.2, 310, cor="destaque", tam=110),
             {"tipo": "cartoes", "y": 470, "alt": 300, "itens": [
                 {"titulo": "Imigração", "texto": "autorização de trabalho", "t": 47.9, "destaque_t": 49.6},
                 {"titulo": "Carreira", "texto": "licenciamento", "t": 51.4, "destaque_t": 53.8}]},
             L("no caso da odonto", 53.2, 820, tam=70, peso=700)),
        cena(56.2, 68.28, "rosa", "grade", R("André e Júlia", 56.3), L("especialistas", 56.9, 310, tam=120),
             L("nessa jornada", 59.4, 440, tam=110), L("do licenciamento.", 61.2, 570, tam=96),
             L("as duas coisas", 64.2, 720, tam=96), L("se complementam", 65.0, 840, cor="destaque", tam=110),
             L("pra mais portas se abrirem.", 66.2, 990, tam=64, peso=700)),
    ],
    "S09": [
        cena(3.5, 6.0, "rosa", "pontos", L("o que faltava", 4.1, 300, tam=120), L("era tempo.", 4.6, 430, cor="destaque", tam=130)),
        cena(13.3, 21.6, "azul", "grade", L("se preparar pra prova,", 13.6, 300, tam=84), L("a nossa filha tinha", 14.9, 410, tam=84),
             {"tipo": "numero", "numero": "1", "rotulo": "aninho", "t": 16.2, "t_rotulo": 16.4, "y": 520, "tam": 280, "tam_rotulo": 96},
             L("bebê de um ano", 18.0, 820, cor="destaque", tam=90), L("não dorme direito", 18.7, 950, tam=70, peso=700),
             L("acorda várias vezes à noite", 20.5, 1040, tam=64, peso=700)),
        cena(28.1, 34.2, "preto", "faixas", R("o André", 28.5),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Você não tem obrigação de passar.", "t": 30.6, "lado": "esq"},
                                                            {"texto": "Vai e faz sem pressão.", "t": 33.0, "lado": "esq"}]}),
        cena(34.4, 40.0, "branco", "circulos", R("mas ela", 34.5), L("boa leonina,", 35.1, 310, cor="destaque", tam=120),
             L("me coloco um desafio", 36.5, 460, tam=84), L("eu vou conseguir,", 38.4, 580, tam=100), L("vou até o final.", 39.0, 700, tam=100)),
        cena(43.1, 51.2, "azul", "pontos",
             {"tipo": "status", "titulo": "o dia da Júlia", "y": 300, "tam": 58, "itens": [
                 {"texto": "exército", "t": 43.6, "status": "andamento", "selo": "meio período", "selo_t": 44.5},
                 {"texto": "filha", "t": 45.5, "status": "andamento", "selo": "meio período", "selo_t": 47.2},
                 {"texto": "estudo", "t": 48.4, "status": "ok", "selo": "quando ela dorme", "selo_t": 50.3}]}),
        cena(53.6, 56.57, "rosa", "grade", L("me dedicar a estudar", 53.9, 300, tam=96),
             {"tipo": "notificacao", "app": "resultado da prova", "titulo": "Aprovada", "texto": "prova do Board (INBDE)", "t": 55.3, "y": 470}),
    ],
    "S08": [
        cena(4.0, 6.9, "azul", "pontos", L("agora eu vou", 4.5, 300, tam=120), L("nesse caminho.", 6.2, 430, cor="destaque", tam=120)),
        cena(7.0, 12.0, "rosa", "grade", R("a Marinna pergunta", 7.05),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Tinha tempo, Júlia?", "t": 7.2},
                                                            {"texto": "Tava sobrando?", "t": 8.2},
                                                            {"texto": "De férias na praia?", "t": 9.7},
                                                            {"texto": "“É agora que eu vou fazer minha prova!”", "t": 10.7}]}),
    ],
    "S10": [
        cena(4.2, 10.2, "azul", "pontos", L("a gente mira", 4.6, 300, tam=120), L("no futuro", 5.0, 430, cor="destaque", tam=130),
             L("o que isso vai me trazer", 8.1, 600, tam=76, peso=700), L("daqui a dez anos?", 9.1, 700, tam=96)),
        cena(12.6, 25.4, "preto", "grade", L("não tinha tempo livre", 12.8, 300, tam=84),
             {"tipo": "status", "titulo": "onde cabia o estudo", "y": 430, "tam": 54, "passo": 104, "itens": [
                 {"texto": "o tempo que eu tinha", "t": 15.2, "status": "ok", "selo": "estudo", "selo_t": 16.9},
                 {"texto": "entre pacientes", "t": 17.4, "status": "ok", "selo": "estudo"},
                 {"texto": "paciente faltou", "t": 19.3, "status": "ok", "selo": "estudo", "sync_t": 19.2, "selo_t": 20.8},
                 {"texto": "à noite", "t": 22.3, "status": "ok", "selo": "estudo", "selo_t": 23.5},
                 {"texto": "fim de semana", "t": 24.4, "status": "ok", "selo": "estudo"}]}),
        cena(25.6, 29.8, "rosa", "circulos", L("eu consegui.", 25.8, 300, cor="destaque", tam=150), L("é possível.", 26.9, 500, tam=120)),
        cena(38.2, 48.9, "branco", "faixas", R("vale ressaltar", 38.4), L("meu inglês era muito básico", 40.2, 310, tam=80),
             {"tipo": "barra", "y": 450, "tam": 50, "itens": [{"texto": "básico", "t": 41.2},
                                                           {"texto": "preparação", "t": 43.4}, {"texto": "aprovada", "t": 48.3}]},
             L("adquiri o inglês que precisava", 45.7, 700, tam=70, peso=700)),
        cena(49.3, 55.4, "azul", "grade", R("pra prova, o inglês é", 49.5),
             {"tipo": "colunas", "y": 320, "alt": 260, "itens": [
                 {"titulo": "Dia a dia", "t": 50.6, "tam": 100, "risco_t": 51.8},
                 {"titulo": "Técnico", "t": 53.6, "tam": 100, "destaque_t": 54.2}]}),
        cena(55.4, 60.3, "rosa", "pontos", R("durante a preparação", 55.5),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 110, "itens": [
                 {"texto": "li tudo que podia", "t": 56.1}, {"texto": "estudava inglês", "t": 57.3}, {"texto": "lia em inglês", "t": 58.2}]}),
    ],
    "S11": [
        cena(3.6, 8.4, "preto", "pontos", R("a dúvida", 3.65),
             {"tipo": "busca", "texto": "o que é o INBDE?", "t": 3.8, "dur": 1.0, "y": 320, "tam": 64, "ate": 8.4},
             L("com o que comparo no Brasil?", 5.2, 520, tam=70, peso=700), L("pra que serve?", 7.3, 620, cor="destaque", tam=100)),
        cena(16.6, 24.4, "azul", "grade", R("INBDE", 17.1), L("exame nacional", 18.8, 310, tam=110), L("integrado de", 20.6, 430, tam=110),
             L("licenciamento", 21.7, 560, cor="destaque", tam=120), L("em odontologia", 22.5, 710, tam=90)),
        cena(24.5, 30.7, "rosa", "circulos", L("é como a prova", 24.8, 300, tam=110),
             L("do conselho americano", 27.4, 430, cor="destaque", tam=96), L("pra dentistas.", 30.1, 580, tam=90)),
        cena(34.9, 41.8, "branco", "faixas", R("dentista internacional", 35.2), L("precisa fazer a prova", 35.5, 310, tam=96),
             {"tipo": "checklist", "y": 470, "tam": 70, "passo": 104, "itens": [
                 {"texto": "pra aplicar na faculdade", "t": 38.3}, {"texto": "antes de aplicar", "t": 40.5}]}),
        cena(42.0, 48.5, "preto", "grade", R("a diferença", 42.1),
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Americanos", "texto": "ao sair da faculdade", "t": 42.6, "tam": 90, "sync_t": 45.0},
                 {"titulo": "Internacionais", "texto": "antes de aplicar", "t": 47.0, "tam": 90}]}),
        cena(55.8, 67.48, "azul", "pontos", R("o caminho", 55.9),
             {"tipo": "degraus", "y": 330, "tam": 40, "itens": [{"texto": "candidatura", "t": 56.8}, {"texto": "entrevista", "t": 58.0},
                                                              {"texto": "aprovação", "t": 60.1}, {"texto": "revalida 2-3 anos", "t": 61.2}]},
             L("varia de estado para estado", 64.1, 800, tam=64, peso=700),
             L("cada estado, sua lei", 66.1, 880, cor="destaque", tam=84, marcador=False)),
    ],
    "S12": [
        cena(3.2, 9.9, "azul", "pontos", R("tipos de licença", 3.3), L("precisamos observar", 4.2, 310, tam=96),
             L("a legislação estadual", 5.4, 430, tam=96), L("cada estado", 7.4, 560, tam=120),
             L("tem sua legislação", 8.9, 690, cor="destaque", tam=100)),
        cena(11.3, 14.9, "rosa", "grade", L("o que ele exige", 11.8, 300, tam=110), L("do dentista internacional", 12.5, 430, cor="destaque", tam=90)),
        cena(15.1, 25.0, "preto", "grade", R("a via tradicional", 15.2), L("revalidação mais tradicional", 16.1, 310, tam=70, peso=700),
             L("DDS", 18.6, 400, cor="destaque", tam=200), L("certificado federal", 20.7, 630, tam=84),
             {"tipo": "contador", "de": 0, "ate": 50, "sufixo": " estados", "t": 24.1, "dur": 0.7, "y": 770, "tam": 150}),
        cena(26.0, 31.6, "azul", "faixas", L("a via mais", 26.5, 300, tam=110), L("segura", 28.7, 420, cor="destaque", tam=140),
             {"tipo": "busca", "texto": "onde eu quero morar?", "t": 29.2, "dur": 1.3, "y": 620, "tam": 60, "ate": 31.6}),
        cena(35.5, 43.4, "rosa", "circulos", R("outra via", 35.8), L("AIGD", 36.5, 310, cor="destaque", tam=200),
             L("trabalhar licenciado em", 39.0, 540, tam=80),
             {"tipo": "contador", "de": 0, "ate": 12, "sufixo": " estados", "t": 40.8, "dur": 0.6, "y": 650, "tam": 150},
             L("12 bons estados.", 42.5, 850, tam=84)),
        cena(50.2, 56.4, "branco", "pontos", R("alguns dos 12", 50.4),
             {"tipo": "checklist", "y": 320, "tam": 66, "passo": 92, "itens": [
                 {"texto": "Flórida", "t": 50.6}, {"texto": "Illinois", "t": 53.0}, {"texto": "Oregon", "t": 53.7},
                 {"texto": "Washington", "t": 54.4}, {"texto": "Virgínia", "t": 55.0}, {"texto": "New Hampshire", "t": 55.7}]}),
        cena(62.3, 76.4, "azul", "faixas", R("a grande diferença", 62.6), L("custo de revalidação", 64.4, 310, tam=90),
             L("certificação federal", 67.0, 430, tam=76, peso=700),
             {"tipo": "colunas", "y": 560, "alt": 300, "itens": [
                 {"titulo": "DDS", "texto": "via mais custosa", "t": 69.0, "tam": 120, "sync_t": 70.0, "destaque_t": 71.8},
                 {"titulo": "AIGD", "texto": "licença mais restrita", "t": 72.5, "tam": 120, "sync_t": 72.5, "destaque_t": 75.4}]},
             L("50 estados × 12 estados", 75.4, 900, tam=70, peso=700)),
        cena(78.2, 82.14, "rosa", "grade", L("observe a legislação", 78.5, 300, tam=100), L("de cada estado", 80.7, 430, cor="destaque", tam=120)),
    ],
    "S13": [
        cena(4.6, 9.8, "azul", "pontos", R("a partir do momento", 5.0), L("com o green card 🇺🇸", 6.5, 310, tam=100),
             L("financiamento estudantil", 8.7, 440, cor="destaque", tam=96)),
        cena(10.3, 15.0, "preto", "grade", R("muita gente pergunta", 10.8),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Não vou poder trabalhar?", "t": 11.7},
                                                            {"texto": "Como vou me sustentar?", "t": 12.8},
                                                            {"texto": "Como vou pagar a faculdade?", "t": 14.0}]}),
        cena(15.2, 24.0, "rosa", "circulos", R("como funciona", 15.4),
             {"tipo": "etapas", "y": 320, "tam": 64, "passo": 124, "itens": [
                 {"texto": "financiamento estudantil", "t": 16.1}, {"texto": "estuda na faculdade", "t": 18.0},
                 {"texto": "paga depois de formado", "t": 19.6}]}),
        cena(28.4, 35.0, "azul", "faixas", L("sociedade de crédito", 28.8, 300, cor="destaque", tam=100),
             L("dentista bem remunerado", 30.6, 450, tam=90), L("financiamento fácil", 34.1, 580, tam=100)),
        cena(36.9, 46.19, "branco", "grade",
             {"tipo": "status", "titulo": "o que abre o crédito", "y": 300, "tam": 58, "itens": [
                 {"texto": "green card", "t": 37.4, "status": "ok", "selo": "acesso", "selo_t": 38.2},
                 {"texto": "visto válido", "t": 39.0, "status": "ok", "selo": "acesso"},
                 {"texto": "crédito", "t": 42.5, "status": "ok", "selo": "liberado"}]},
             L("faculdade sem preocupação", 44.2, 720, cor="destaque", tam=76, marcador=False)),
    ],
    "S14": [
        cena(3.4, 7.1, "rosa", "pontos", L("não é passe de mágica.", 3.5, 300, tam=96), L("cuidado", 6.5, 430, cor="destaque", tam=140)),
        cena(7.6, 14.5, "azul", "grade",
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Verdade", "texto": "que dói", "t": 8.1, "tam": 110, "sync_t": 10.0, "destaque_t": 10.8},
                 {"titulo": "Mentira", "texto": "te põe num buraco", "t": 12.2, "tam": 110, "risco_t": 14.2}]}),
        cena(15.3, 21.4, "preto", "circulos", R("existe planejamento", 15.6),
             {"tipo": "checklist", "y": 320, "tam": 78, "passo": 112, "itens": [{"texto": "financeiro", "t": 18.0},
                                                                               {"texto": "emocional", "t": 19.5}]},
             L("talvez até mais o emocional", 19.0, 580, tam=64, peso=700)),
        cena(27.4, 37.5, "branco", "pontos", L("não tem limite", 27.7, 300, cor="destaque", tam=120), L("de idade.", 29.3, 450, tam=120),
             L("pessoas se licenciando", 32.2, 610, tam=84), L("em idades avançadas", 36.6, 730, tam=84)),
        cena(38.3, 43.6, "azul", "grade", L("fazendo green card", 38.7, 300, tam=96),
             {"tipo": "numero", "numero": "70", "rotulo": "anos", "t": 40.1, "t_rotulo": 40.6, "y": 440, "tam": 300, "tam_rotulo": 110},
             L("a imigração não coloca limite", 41.5, 760, tam=64, peso=700)),
        cena(43.6, 51.6, "preto", "faixas", R("a imigração quer saber", 43.7),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Você pode contribuir?", "t": 44.8, "lado": "esq"},
                                                            {"texto": "Vou usufruir do seu melhor?", "t": 47.1, "lado": "esq"},
                                                            {"texto": "Tem capacidade ativa?", "t": 50.1, "lado": "esq"}]}),
        cena(53.6, 61.2, "branco", "circulos",
             {"tipo": "status", "titulo": "a história dela", "y": 300, "tam": 58, "itens": [
                 {"texto": "idade", "t": 54.1, "status": "andamento", "selo": "quase 70"},
                 {"texto": "carreira pela frente", "t": 55.6, "status": "ok", "selo": "+20 anos"}]},
             L("e você pensando em limite?", 59.5, 640, cor="destaque", tam=80, marcador=False)),
        cena(63.6, 68.07, "rosa", "grade", R("é cultural", 64.0), L("no Brasil 🇧🇷", 65.0, 310, tam=110),
             L("data de validade", 66.9, 440, cor="destaque", tam=110)),
    ],
    "S15": [
        cena(3.9, 10.7, "azul", "pontos", L("a ideia desta live:", 4.1, 300, tam=96), L("trazer a perspectiva", 5.5, 420, tam=90),
             L("não é distante", 7.9, 550, cor="destaque", tam=120), L("nem fora do comum", 9.1, 700, tam=96)),
        cena(10.8, 13.4, "rosa", "circulos", L("não é um", 11.1, 300, tam=110), L("gênio da lâmpada", 11.8, 430, cor="destaque", tam=120)),
        cena(17.8, 23.8, "preto", "grade", L("não tem gênio", 18.2, 300, tam=100), L("pra esfregar", 19.0, 420, tam=100),
             L("o gênio é você", 20.5, 570, cor="destaque", tam=120), L("o esfregão é sua carreira", 22.4, 720, tam=76, peso=700)),
        cena(24.0, 27.48, "azul", "pontos", L("a gente tem condição", 24.1, 300, tam=90), L("de olhar o repertório", 25.2, 420, tam=96), L("profissional", 26.4, 550, cor="destaque", tam=130)),
    ],
}

if __name__ == "__main__":
    for k, cenas in ROTEIROS.items():
        r = dict(BASE, nome=f"dentista_{k}", duracao=round(DUR[k] + 3.88, 2), palavras=f"palavras/{k}.json",
                 cenas=cenas + [cta(k)])
        json.dump(r, open(os.path.join(AQUI, f"{k}.json"), "w"), ensure_ascii=False, indent=1)
    print(", ".join(sorted(ROTEIROS)))
