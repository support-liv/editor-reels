#!/usr/bin/env python3
"""Roteiros de motion (Imigrar) dos shorts da live Plano EUA 2027. Gera L##.json / M##.json aqui.

    python3 projetos/plano_eua_2027/motion/roteiros.py
    python3 motion/gerar_liv.py projetos/plano_eua_2027/motion/L01.json

L05, L10 e L12 foram os testes (JSON escritos à mão, não estão aqui). Tempos em segundos do short pronto
(palavras/<id>.json, `lote_motion.py palavras`); DUR = duração da fala (`lote_motion.py duracao`). O motion dura
fala + cauda de 3,8s, com o CTA "Veja a live completa no canal" na cauda.
"""
import json, os

AQUI = os.path.dirname(os.path.abspath(__file__))
DUR = {"L01": 42.69, "L02": 37.42, "L03": 25.88, "L04": 33.57, "L06": 27.77, "L07": 44.74, "L08": 45.08, "L09": 23.60,
       "L11": 44.74, "L13": 34.72, "L14": 33.13, "L15": 39.00, "L16": 37.84, "L17": 45.43,
       "M01": 27.96, "M02": 35.92, "M03": 43.07, "M04": 39.77, "M05": 40.51, "M06": 44.71, "M07": 41.25, "M08": 32.44,
       "M09": 40.55, "M10": 39.14, "M11": 34.78, "M12": 38.04, "M13": 40.52, "M14": 28.64}
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
    "L01": [
        cena(3.5, 9.5, "azul", "pontos", R("do lado de lá", 3.6), L("muita humanização", 3.6, 310, cor="destaque", tam=110),
             L("sentindo todo o processo", 7.8, 460, tam=84)),
        cena(10.3, 20.1, "preto", "grade", R("a história dela", 10.4),
             {"tipo": "etapas", "y": 320, "tam": 64, "passo": 110, "itens": [
                 {"texto": "imigrante", "t": 11.1}, {"texto": "vários vistos", "t": 13.6}, {"texto": "obstáculos", "t": 16.6},
                 {"texto": "green card", "t": 18.5}, {"texto": "cidadania", "t": 19.3}]}),
        cena(20.3, 23.3, "rosa", "circulos", L("hoje morando", 20.5, 300, tam=120), L("e trabalhando nos EUA 🇺🇸", 22.0, 430, cor="destaque", tam=90)),
        cena(27.2, 34.4, "branco", "faixas", L("consigo linkar", 27.7, 300, tam=110), L("um propósito", 28.6, 430, cor="destaque", tam=120),
             L("fazer diferença", 30.7, 590, tam=100), L("na vida das pessoas", 33.0, 710, tam=90)),
        cena(34.4, 42.69, "azul", "pontos", R("cada cliente faz parte", 34.5),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 108, "itens": [
                 {"texto": "da minha história", "t": 36.7}, {"texto": "do meu dia a dia", "t": 37.7},
                 {"texto": "das conquistas", "t": 40.7}, {"texto": "e das lutas", "t": 41.5}]}),
    ],
    "L02": [
        cena(3.6, 9.6, "rosa", "pontos", R("ainda escuto muito", 3.7), L("muitas pessoas falam:", 4.0, 310, tam=84),
             {"tipo": "chat", "y": 440, "tam": 62, "itens": [{"texto": "Eu não sabia que era possível!", "t": 6.8, "lado": "esq"},
                                                            {"texto": "Achava que era só com casamento.", "t": 8.2, "lado": "esq"}]}),
        cena(10.6, 15.3, "azul", "grade", L("muita gente não vê", 11.2, 300, tam=110), L("tantos caminhos", 14.0, 430, cor="destaque", tam=120)),
        cena(15.4, 22.4, "preto", "circulos", R("existem vários tipos", 15.5),
             {"tipo": "busca", "texto": "visto pros EUA", "t": 18.0, "dur": 0.9, "y": 320, "tam": 64, "ate": 22.4},
             L("e acha que é distante", 21.2, 520, cor="destaque", tam=90)),
        cena(24.9, 34.4, "branco", "faixas", R("entendendo cada visto", 25.1), L("vai desmistificando", 26.4, 310, tam=100),
             L("é possível", 30.6, 440, cor="destaque", tam=140), L("só preciso ajustar a rota", 32.2, 620, tam=80)),
    ],
    "L03": [
        cena(3.3, 8.6, "azul", "pontos", R("a pergunta", 3.35),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Eu quero amanhã.", "t": 3.4},
                                                            {"texto": "O que eu preciso fazer?", "t": 5.2},
                                                            {"texto": "Quais são as portas legais?", "t": 6.4}]}),
        cena(13.8, 25.88, "rosa", "grade", L("a primeira coisa que eu faço:", 14.0, 300, tam=76, peso=700), L("separar os caminhos", 16.7, 400, cor="destaque", tam=100),
             {"tipo": "colunas", "y": 470, "alt": 300, "itens": [
                 {"titulo": "Temporários", "texto": "objetivo específico", "t": 19.0, "tam": 90, "sync_t": 22.6},
                 {"titulo": "Green card", "texto": "o caminho pra ficar", "t": 24.1, "tam": 90}]}),
    ],
    "L04": [
        cena(3.4, 12.0, "azul", "grade", R("visto temporário", 3.5), L("consegue aplicar", 4.0, 310, tam=110),
             L("em média:", 7.5, 440, tam=90),
             {"tipo": "contador", "de": 6, "ate": 8, "sufixo": " meses", "t": 8.0, "dur": 1.2, "y": 560, "tam": 170},
             L("já está aqui com o visto", 10.0, 780, cor="destaque", tam=80, marcador=False)),
        cena(15.0, 24.9, "preto", "circulos", R("por que dividir?", 15.1),
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Green card", "texto": "longo prazo", "t": 17.5, "tam": 100, "sync_t": 19.0},
                 {"titulo": "Temporário", "texto": "a oportunidade agora", "t": 21.0, "tam": 100, "sync_t": 22.4}]}),
        cena(25.0, 33.57, "rosa", "pontos", R("aqui você pode", 25.1),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 108, "itens": [
                 {"texto": "desenvolver-se", "t": 25.2}, {"texto": "criar vínculos", "t": 26.7}, {"texto": "fazer networking", "t": 27.7}]},
             L("green card: o segundo passo", 31.6, 680, cor="destaque", tam=76, marcador=False)),
    ],
    "L06": [
        cena(3.3, 10.2, "azul", "pontos", R("no planejamento", 3.4),
             {"tipo": "numero", "numero": "2", "rotulo": "vistos em paralelo", "t": 6.3, "t_rotulo": 6.7, "y": 300, "tam": 300, "tam_rotulo": 80},
             L("tem gente que faz", 3.4, 640, tam=80), L("é possível", 9.5, 760, cor="destaque", tam=120)),
        cena(10.4, 19.9, "rosa", "grade", L("a lei não exclui", 10.6, 300, tam=110),
             {"tipo": "colunas", "y": 460, "alt": 280, "itens": [
                 {"titulo": "Em paralelo", "t": 12.0, "tam": 96, "destaque_t": 13.7},
                 {"titulo": "Em sequência", "t": 16.9, "tam": 96, "destaque_t": 17.6}]}),
        cena(20.8, 27.77, "branco", "faixas", L("é o seu planejamento", 21.2, 300, cor="destaque", tam=100),
             L("o que fica melhor pra você", 23.0, 450, tam=84), L("os 2 caminhos mais comuns", 25.1, 580, tam=76, peso=700)),
    ],
    "L07": [
        cena(3.6, 10.9, "rosa", "pontos", R("a pergunta", 3.65),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Sou engenheiro?", "t": 4.4}, {"texto": "Desenvolvedor?", "t": 6.6},
                                                            {"texto": "Área da saúde?", "t": 8.0},
                                                            {"texto": "Todo mundo começa do mesmo lugar?", "t": 9.2}]}),
        cena(10.9, 19.6, "azul", "grade", L("não.", 11.1, 300, cor="destaque", tam=160), L("muda menos", 11.5, 500, tam=110),
             L("do que as pessoas imaginam", 12.3, 630, tam=80), L("nem todos vão se qualificar", 17.2, 750, tam=80)),
        cena(20.3, 27.4, "preto", "circulos", L("a profissão", 20.6, 300, tam=120), L("raramente define", 24.4, 430, cor="destaque", tam=110),
             L("o caminho do visto", 26.6, 580, tam=96)),
        cena(28.2, 39.4, "branco", "faixas", L("dois dentistas,", 28.4, 300, tam=100), L("caminhos diferentes", 31.2, 420, cor="destaque", tam=96),
             {"tipo": "status", "titulo": "dentistas, vistos diferentes", "y": 570, "tam": 56, "itens": [
                 {"texto": "dentista 1", "t": 32.9, "status": "ok", "selo": "EB-1A", "selo_t": 34.9},
                 {"texto": "dentista 2", "t": 36.1, "status": "ok", "selo": "EB-2 NIW", "selo_t": 37.0},
                 {"texto": "dentista 3", "t": 38.1, "status": "ok", "selo": "O-1A", "selo_t": 38.8}]}),
        cena(39.6, 44.74, "rosa", "grade", L("não é a profissão", 39.9, 300, tam=110), L("que muda o caminho", 41.4, 430, cor="destaque", tam=100)),
    ],
    "L08": [
        cena(3.3, 10.9, "azul", "pontos", R("o inglês", 3.35), L("cada categoria de visto", 5.8, 310, tam=84),
             L("não exige inglês", 7.7, 430, cor="destaque", tam=110)),
        cena(11.5, 16.6, "preto", "grade", {"tipo": "busca", "texto": "nota mínima do TOEFL?", "t": 11.9, "dur": 1.2, "y": 300, "tam": 60, "ate": 16.6},
             L("não existe isso", 13.7, 500, cor="destaque", tam=120), L("nos critérios do visto", 15.6, 650, tam=76, peso=700)),
        cena(17.1, 26.3, "rosa", "circulos", L("na prática, no consulado", 17.4, 300, tam=84),
             {"tipo": "status", "titulo": "o oficial quer entender", "y": 440, "tam": 56, "itens": [
                 {"texto": "sua petição", "t": 22.3, "status": "andamento", "selo": "entende?"},
                 {"texto": "seu preparo", "t": 23.6, "status": "andamento", "selo": "pronto?"},
                 {"texto": "o que vai fazer", "t": 25.7, "status": "andamento", "selo": "?"}]}),
        cena(27.2, 36.0, "branco", "faixas", L("vindo trabalhar numa empresa", 27.8, 300, tam=76, peso=700),
             L("e não se comunica", 32.8, 410, cor="destaque", tam=100),
             {"tipo": "chat", "y": 570, "tam": 62, "itens": [{"texto": "Como você vai trabalhar, então?", "t": 34.2, "lado": "esq"}]}),
        cena(39.2, 45.08, "azul", "grade", L("outra leitura:", 39.3, 300, tam=100), L("ele não espera", 41.8, 430, tam=110),
             L("que você seja proficiente", 43.4, 560, cor="destaque", tam=90)),
    ],
    "L09": [
        cena(3.4, 11.8, "rosa", "pontos", R("uma cliente", 3.45),
             {"tipo": "etapas", "y": 320, "tam": 62, "passo": 108, "itens": [
                 {"texto": "entrevista marcada", "t": 3.8}, {"texto": "professora particular", "t": 6.2}, {"texto": "todos os dias", "t": 7.5},
                 {"texto": "sobre o próprio processo", "t": 9.2}, {"texto": "foi suficiente", "t": 11.2}]}),
        cena(12.4, 23.6, "azul", "grade", L("não precisa ser", 12.7, 300, tam=110), L("proficiente", 13.0, 430, cor="destaque", tam=130),
             L("mas ter coerência", 14.6, 590, tam=96), L("o inglês é importante,", 16.3, 710, tam=84),
             L("mas não determinante", 18.4, 820, cor="destaque", tam=90, marcador=False)),
    ],
    "L11": [
        cena(3.2, 10.5, "azul", "pontos", R("vistos temporários", 3.25),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 108, "itens": [
                 {"texto": "filhos menores de 21", "t": 6.1}, {"texto": "cônjuge", "t": 8.1}]},
             L("vêm como dependentes", 4.0, 560, cor="destaque", tam=84, marcador=False), L("você vem junto", 9.8, 660, tam=84)),
        cena(12.6, 18.4, "preto", "grade",
             {"tipo": "status", "titulo": "alguns vistos não deixam", "y": 300, "tam": 58, "itens": [
                 {"texto": "cônjuge trabalhar", "t": 13.2, "status": "negado", "selo": "barreira"},
                 {"texto": "filho trabalhar", "t": 15.3, "status": "negado", "selo": "barreira"}]},
             L("vão ter algumas barreiras", 17.5, 560, tam=76, peso=700)),
        cena(18.9, 30.0, "rosa", "circulos",
             {"tipo": "numero", "numero": "21", "rotulo": "anos", "t": 19.4, "t_rotulo": 19.9, "y": 300, "tam": 300, "tam_rotulo": 110},
             L("debaixo do guarda-chuva", 20.8, 620, tam=84), L("depois dos 21, sai", 22.6, 740, cor="destaque", tam=100),
             L("no temporário e no green card", 25.0, 880, tam=64, peso=700)),
        cena(31.9, 38.8, "branco", "faixas",
             {"tipo": "colunas", "y": 320, "alt": 300, "itens": [
                 {"titulo": "Antes dos 21", "texto": "green card junto", "t": 32.4, "tam": 90, "destaque_t": 34.6},
                 {"titulo": "Depois dos 21", "texto": "não recebe junto", "t": 35.9, "tam": 90, "risco_t": 37.9}]}),
        cena(39.0, 44.74, "azul", "grade", R("por isso", 39.1),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Meu filho já tem 19!", "t": 40.8},
                                                            {"texto": "Tenho que resolver minha vida!", "t": 42.5}]},
             L("pro filho não ficar de fora", 43.5, 640, cor="destaque", tam=80, marcador=False)),
    ],
    "L13": [
        cena(3.3, 8.2, "rosa", "pontos", L("capaz de vir por essa via", 3.5, 300, tam=84), L("muitas vezes é", 5.7, 420, tam=100),
             L("discricionariedade", 7.6, 550, cor="destaque", tam=90)),
        cena(8.4, 18.6, "azul", "grade", R("o texto da negativa", 8.6),
             {"tipo": "notificacao", "app": "consulado", "titulo": "Visto negado", "texto": "leia o texto da carta", "t": 10.5, "y": 320},
             L("não prejudica", 12.5, 620, cor="destaque", tam=110), L("futuras aplicações", 13.0, 750, tam=96),
             L("nem as chances de aprovação", 16.2, 870, tam=64, peso=700)),
        cena(21.8, 29.4, "preto", "circulos", R("esteja preparado", 22.2),
             {"tipo": "cartoes", "y": 320, "alt": 280, "itens": [
                 {"titulo": "Plano A", "texto": "o caminho principal", "t": 23.4, "destaque_t": 23.6},
                 {"titulo": "Plano B", "texto": "a alternativa", "t": 24.1, "destaque_t": 24.3}]},
             L("eu falo muito:", 25.8, 640, tam=76), L("não desistir por um obstáculo", 27.8, 760, cor="destaque", tam=76, marcador=False)),
        cena(29.6, 34.72, "rosa", "grade", L("vai até o fim", 29.6, 300, tam=120), L("maximiza as chances", 31.7, 430, cor="destaque", tam=100),
             L("de conseguir o objetivo.", 33.4, 580, tam=84)),
    ],
    "L14": [
        cena(3.2, 7.4, "azul", "pontos", L("discricionariedade", 3.3, 300, cor="destaque", tam=90), L("nas mãos do oficial", 5.1, 430, tam=96),
             L("da análise dele", 6.5, 560, tam=96)),
        cena(10.5, 23.3, "preto", "grade", L("o mesmo processo", 10.8, 300, tam=100), L("contanto que seja", 13.6, 420, tam=84),
             L("bem feito e coerente", 14.4, 530, cor="destaque", tam=96),
             {"tipo": "colunas", "y": 690, "alt": 260, "itens": [
                 {"titulo": "Oficial 1", "texto": "negado", "t": 17.4, "tam": 96, "sync_t": 18.0, "risco_t": 19.5},
                 {"titulo": "Oficial 2", "texto": "aprovado", "t": 20.8, "tam": 96, "destaque_t": 21.6}]}),
        cena(24.6, 32.5, "rosa", "circulos", R("o nosso trabalho", 25.0),
             {"tipo": "checklist", "y": 320, "tam": 74, "passo": 108, "itens": [
                 {"texto": "o mais coerente possível", "t": 26.6}, {"texto": "o mais evidente", "t": 27.8}, {"texto": "com provas", "t": 29.1}]},
             L("pro oficial ser convencido", 30.6, 680, cor="destaque", tam=76, marcador=False)),
    ],
    "L15": [
        cena(3.2, 11.0, "azul", "pontos", R("premium processing", 3.3), L("a USCIS disponibiliza", 4.6, 310, tam=84), L("se você quiser pagar", 6.4, 420, tam=96),
             L("tantos dias úteis", 9.0, 540, cor="destaque", tam=110), L("pra analisar", 10.6, 690, tam=96)),
        cena(12.4, 21.0, "preto", "grade",
             {"tipo": "status", "titulo": "prazo de análise", "y": 300, "tam": 58, "itens": [
                 {"texto": "EB-1", "t": 12.6, "status": "ok", "selo": "15 dias", "selo_t": 13.3},
                 {"texto": "EB-2 NIW", "t": 14.2, "status": "ok", "selo": "40 a 45 dias", "selo_t": 16.6},
                 {"texto": "temporários", "t": 17.9, "status": "ok", "selo": "15 dias", "selo_t": 20.2}]}),
        cena(29.0, 39.0, "rosa", "circulos", R("atenção", 29.2), L("não é que você", 29.9, 310, tam=90), L("está pagando mais", 31.1, 420, tam=100),
             L("ele não tem que aprovar", 32.0, 540, cor="destaque", tam=90),
             {"tipo": "status", "titulo": "a decisão pode ser", "y": 690, "tam": 56, "itens": [
                 {"texto": "pedido de provas", "t": 35.9, "status": "andamento", "selo": "RFE"},
                 {"texto": "aprovação", "t": 36.9, "status": "ok", "selo": "sim"},
                 {"texto": "negativa", "t": 37.9, "status": "negado", "selo": "não"}]}),
    ],
    "L16": [
        cena(3.5, 6.7, "rosa", "pontos", L("vai me ajudar?", 4.0, 300, tam=110), L("não entra na análise", 5.5, 430, cor="destaque", tam=96)),
        cena(9.6, 14.0, "azul", "grade",
             {"tipo": "numero", "numero": "2", "rotulo": "fases", "t": 10.1, "t_rotulo": 10.4, "y": 300, "tam": 300, "tam_rotulo": 110},
             L("elegibilidade:", 11.4, 620, cor="destaque", tam=100), L("os critérios do visto", 12.6, 750, tam=84)),
        cena(14.1, 25.8, "preto", "circulos", L("não se pergunta", 14.5, 300, tam=100),
             {"tipo": "busca", "texto": "qual a sua nacionalidade?", "t": 15.6, "dur": 1.2, "y": 440, "tam": 56, "ate": 25.8},
             L("exceção: visto E-2", 17.6, 640, cor="destaque", tam=96), L("tratados entre países", 20.5, 780, tam=84),
             L("só se o seu país está na lista", 23.6, 890, tam=64, peso=700)),
        cena(27.4, 37.84, "branco", "faixas", L("não entra na elegibilidade", 27.8, 300, tam=84),
             {"tipo": "status", "titulo": "aprovado no…", "y": 430, "tam": 58, "itens": [
                 {"texto": "EB-2", "t": 32.6, "status": "ok", "selo": "qualquer cidadania"},
                 {"texto": "EB-3", "t": 33.8, "status": "ok", "selo": "qualquer cidadania"},
                 {"texto": "EB-1A", "t": 35.0, "status": "ok", "selo": "qualquer cidadania"}]}),
    ],
    "L17": [
        cena(3.4, 8.7, "azul", "pontos", L("porque sou engenheiro", 3.7, 300, tam=100), L("isso é um mito", 7.8, 430, cor="destaque", tam=120)),
        cena(9.6, 19.4, "rosa", "grade", R("a gente vê muito", 9.9),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Eu sou tal coisa…", "t": 11.2}, {"texto": "Tenho tal profissão.", "t": 13.0},
                                                            {"texto": "Tá faltando nos EUA!", "t": 16.3},
                                                            {"texto": "Então vou ser aprovado.", "t": 18.4}]}),
        cena(20.3, 25.2, "preto", "circulos", L("foi vendido", 20.6, 300, tam=120), L("erroneamente", 22.7, 430, cor="destaque", tam=120),
             L("pelas mídias", 24.0, 580, tam=100)),
        cena(27.6, 33.3, "branco", "faixas",
             {"tipo": "colunas", "y": 320, "alt": 280, "itens": [
                 {"titulo": "Pro visto", "texto": "não quer dizer nada", "t": 28.0, "tam": 96, "sync_t": 27.8},
                 {"titulo": "Pra carreira", "texto": "é bom pra você", "t": 29.4, "tam": 96, "destaque_t": 30.2}]},
             L("não compre essa ideia", 31.1, 680, cor="destaque", tam=90, marcador=False)),
        cena(34.1, 45.43, "azul", "pontos", L("mesma profissão", 34.6, 300, tam=100),
             {"tipo": "status", "titulo": "duas pessoas", "y": 430, "tam": 56, "itens": [
                 {"texto": "projetos", "t": 37.2, "status": "andamento", "selo": "diferentes"},
                 {"texto": "caminhos", "t": 40.0, "status": "andamento", "selo": "diferentes"},
                 {"texto": "pessoa 1", "t": 42.5, "status": "negado", "selo": "negado", "selo_t": 43.6},
                 {"texto": "pessoa 2", "t": 44.0, "status": "ok", "selo": "aprovado", "selo_t": 44.3}]}),
    ],
    "M01": [
        cena(4.8, 7.4, "azul", "pontos",
             {"tipo": "numero", "numero": "2", "rotulo": "extremos", "t": 5.2, "t_rotulo": 5.5, "y": 300, "tam": 300, "tam_rotulo": 110},
             L("que deixam a gente paralisado", 6.2, 620, cor="destaque", tam=76, marcador=False)),
        cena(7.8, 15.3, "rosa", "grade",
             {"tipo": "colunas", "y": 300, "alt": 280, "itens": [
                 {"titulo": "Pouca informação", "texto": "parece impossível", "t": 8.1, "tam": 76, "sync_t": 10.2},
                 {"titulo": "Informação demais", "texto": "parece complexo", "t": 11.3, "tam": 76, "sync_t": 12.1}]},
             L("dá certo pra todo mundo, menos pra você", 13.6, 640, tam=60, peso=700)),
        cena(18.8, 24.5, "preto", "circulos", R("e vêm as dúvidas", 18.85),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Será que eu tenho perfil?", "t": 18.9},
                                                            {"texto": "Dou conta do investimento?", "t": 20.6},
                                                            {"texto": "Tenho inglês pra isso?", "t": 22.9}]}),
        cena(24.8, 27.96, "branco", "faixas", L("e você se segura", 25.1, 300, tam=110), L("nas suas faltas", 26.9, 430, cor="destaque", tam=120)),
    ],
    "M02": [
        cena(3.3, 14.0, "rosa", "pontos", R("que canseira. eu queria", 3.35),
             {"tipo": "checklist", "y": 320, "tam": 70, "passo": 104, "itens": [
                 {"texto": "uma perspectiva melhor", "t": 3.4}, {"texto": "ganhar mais", "t": 7.1}, {"texto": "ser reconhecida", "t": 8.2},
                 {"texto": "carreira internacional", "t": 10.1}, {"texto": "falar um inglês bonito", "t": 12.3}]}),
        cena(14.3, 21.3, "azul", "grade", L("que o mundo entendesse", 14.6, 300, tam=90), L("que sou sensacional", 16.4, 420, cor="destaque", tam=100),
             L("que sou o que quero ser", 17.8, 570, tam=76, peso=700)),
        cena(21.7, 28.4, "preto", "circulos", L("isso vai cansando", 21.9, 300, tam=110), L("ou eu saio daqui", 25.7, 430, cor="destaque", tam=110),
             L("ou a vida não tem sentido", 26.9, 580, tam=84)),
        cena(28.7, 35.92, "branco", "faixas", L("mudar de país", 28.9, 300, cor="destaque", tam=120),
             {"tipo": "status", "titulo": "vira uma resposta pra", "y": 460, "tam": 58, "itens": [
                 {"texto": "esse cansaço", "t": 31.4, "status": "ok", "selo": "resposta"},
                 {"texto": "a falta de perspectiva", "t": 34.2, "status": "ok", "selo": "resposta"}]}),
    ],
    "M03": [
        cena(3.4, 13.5, "azul", "pontos", R("até por amor, falavam", 3.45),
             {"tipo": "chat", "y": 320, "tam": 58, "itens": [
                 {"texto": "Você não tá querendo demais?", "t": 4.5, "lado": "esq"},
                 {"texto": "Sua vida aqui já não é boa?", "t": 6.0, "lado": "esq"},
                 {"texto": "Sua carreira não tá crescendo?", "t": 8.3, "lado": "esq"},
                 {"texto": "Não tá sendo ambiciosa demais?", "t": 10.4, "lado": "esq"},
                 {"texto": "Audaciosa demais?", "t": 12.1, "lado": "esq"}]}),
        cena(17.4, 26.7, "rosa", "grade", L("quem criou", 17.6, 300, tam=110), L("seus limites?", 18.3, 420, cor="destaque", tam=120),
             {"tipo": "status", "titulo": "quem definiu", "y": 580, "tam": 56, "itens": [
                 {"texto": "até que ponto", "t": 21.5, "status": "andamento", "selo": "?"},
                 {"texto": "até que país", "t": 23.9, "status": "andamento", "selo": "?"},
                 {"texto": "até que carreira", "t": 26.0, "status": "andamento", "selo": "?"}]}),
        cena(27.9, 38.7, "preto", "circulos", L("suas habilidades,", 28.4, 300, tam=100), L("suas competências", 29.2, 420, tam=100),
             L("podem se multiplicar", 30.5, 540, cor="destaque", tam=100), L("se empenhar um tempo", 32.3, 690, tam=80),
             L("pra tudo trabalhar por você", 36.5, 790, tam=76, peso=700)),
        cena(39.0, 43.07, "rosa", "pontos", L("no fundo,", 39.1, 300, tam=110), L("ninguém.", 39.8, 430, cor="destaque", tam=160),
             L("a gente mesmo é que cria.", 41.9, 630, tam=84)),
    ],
    "M04": [
        cena(3.3, 10.5, "rosa", "pontos", L("não tomar uma atitude", 3.3, 300, tam=90), L("não dar o primeiro passo", 4.8, 410, tam=90),
             L("não colocar um basta", 6.4, 520, tam=90), L("também é escolher", 8.3, 650, cor="destaque", tam=110)),
        cena(10.8, 15.6, "azul", "grade", L("enquanto não entende isso", 10.9, 300, tam=84),
             L("tudo continua no mesmo lugar", 12.8, 420, cor="destaque", tam=84)),
        cena(16.9, 24.7, "preto", "circulos",
             {"tipo": "numero", "numero": "10", "rotulo": "anos aqui fora", "t": 17.3, "t_rotulo": 17.6, "y": 300, "tam": 280, "tam_rotulo": 84},
             L("quase ninguém da minha geração", 19.4, 600, tam=70, peso=700), L("continuou no Brasil", 21.9, 700, cor="destaque", tam=96)),
        cena(24.8, 35.4, "branco", "faixas", L("as pessoas experimentam", 25.0, 300, tam=84), L("o mundo", 26.4, 410, cor="destaque", tam=130),
             {"tipo": "colunas", "y": 590, "alt": 260, "itens": [
                 {"titulo": "Antes", "texto": "coisas limitadoras", "t": 30.5, "tam": 96, "sync_t": 31.0, "risco_t": 32.2},
                 {"titulo": "Depois", "texto": "consequência do esforço", "t": 32.5, "tam": 96, "sync_t": 33.5, "destaque_t": 35.0}]}),
        cena(35.7, 39.77, "rosa", "grade", L("dificilmente você quer", 35.9, 300, tam=90), L("voltar", 36.6, 420, cor="destaque", tam=150),
             L("e se reduzir de novo", 38.1, 610, tam=84)),
    ],
    "M05": [
        cena(3.3, 7.1, "azul", "pontos", R("o medo número 1", 3.35), L("vou fazer isso tudo", 3.6, 310, tam=96),
             L("e não vou me comunicar?", 5.0, 440, cor="destaque", tam=90)),
        cena(9.4, 17.0, "rosa", "grade", L("não é só isso", 9.9, 300, tam=110), L("o medo de não ser", 13.4, 430, tam=100),
             L("o bom profissional", 14.9, 560, cor="destaque", tam=100), L("que você é em português", 15.7, 700, tam=76, peso=700)),
        cena(17.3, 27.9, "preto", "circulos", R("em inglês", 17.35),
             {"tipo": "etapas", "y": 320, "tam": 62, "passo": 112, "itens": [
                 {"texto": "medo do patamar", "t": 17.9}, {"texto": "vergonha", "t": 20.8}, {"texto": "se sentir julgado", "t": 22.4},
                 {"texto": "como se devesse algo", "t": 25.5}]}),
        cena(30.6, 39.8, "branco", "faixas",
             {"tipo": "numero", "numero": "2", "rotulo": "personalidades", "t": 31.0, "t_rotulo": 31.5, "y": 300, "tam": 280, "tam_rotulo": 84},
             {"tipo": "colunas", "y": 620, "alt": 260, "itens": [
                 {"titulo": "Português", "texto": "a que vocês conhecem", "t": 33.6, "tam": 96, "sync_t": 34.7},
                 {"titulo": "Inglês", "texto": "mais recatada", "t": 36.8, "tam": 96, "sync_t": 37.6}]}),
    ],
    "M06": [
        cena(3.4, 6.4, "azul", "pontos", R("um treinamento", 3.45), L("equipes multipaíses", 4.1, 310, cor="destaque", tam=100)),
        cena(6.6, 15.0, "preto", "grade", R("e eu pensando", 7.0),
             {"tipo": "status", "titulo": "o que eles vão achar", "y": 320, "tam": 56, "itens": [
                 {"texto": "meu inglês", "t": 8.4, "status": "negado", "selo": "péssimo?", "selo_t": 8.7},
                 {"texto": "capacidade técnica", "t": 10.3, "status": "negado", "selo": "fraca?", "selo_t": 11.2},
                 {"texto": "como em português", "t": 12.8, "status": "andamento", "selo": "não é igual", "selo_t": 14.8}]}),
        cena(17.5, 21.6, "rosa", "circulos", L("a primeira coisa que eu falei:", 17.8, 300, tam=76, peso=700),
             {"tipo": "chat", "y": 420, "tam": 66, "itens": [{"texto": "I'm sorry about my English.", "t": 20.2}]}),
        cena(21.8, 30.7, "branco", "faixas", R("a americana respondeu", 22.0),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Acho que a gente devia começar por aqui.", "t": 24.6, "lado": "esq"},
                                                            {"texto": "Isso é uma vantagem.", "t": 28.0, "lado": "esq"}]}),
        cena(31.1, 39.3, "azul", "pontos",
             L("eu não sei falar uma frase", 31.2, 300, tam=84), L("em português", 33.0, 410, cor="destaque", tam=100),
             {"tipo": "checklist", "y": 560, "tam": 64, "passo": 92, "itens": [
                 {"texto": "dar um treinamento", "t": 34.7}, {"texto": "se comunicar", "t": 36.1}, {"texto": "falar com um cliente", "t": 37.4},
                 {"texto": "ler um e-mail", "t": 38.6}]}),
        cena(39.4, 44.71, "rosa", "grade", L("você tem uma capacidade", 39.5, 300, tam=90), L("uma coisa a mais", 42.9, 430, cor="destaque", tam=110),
             L("e não a menos", 43.8, 580, tam=100)),
    ],
    "M07": [
        cena(5.4, 9.9, "rosa", "pontos", R("entenda", 5.8), L("o inglês é", 6.4, 310, tam=110),
             L("ferramenta de trabalho", 7.0, 440, cor="destaque", tam=100), L("ninguém chega fluente", 8.7, 590, tam=84)),
        cena(10.4, 17.7, "azul", "grade", L("ninguém precisa ser fluente", 10.8, 300, tam=84),
             {"tipo": "checklist", "y": 430, "tam": 74, "passo": 108, "itens": [
                 {"texto": "pra ser funcional", "t": 14.4}, {"texto": "compatível", "t": 15.6}, {"texto": "competitivo", "t": 16.0}]}),
        cena(18.8, 29.3, "preto", "circulos", L("dar o peso", 19.2, 300, tam=110), L("que o inglês precisa", 20.5, 420, tam=96),
             {"tipo": "chat", "y": 560, "tam": 60, "itens": [{"texto": "Vem com um inglêszinho, tá tudo resolvido.", "t": 23.8, "lado": "esq"}]},
             L("não dá pra ter essa postura", 27.8, 800, cor="destaque", tam=76, marcador=False)),
        cena(29.4, 40.4, "branco", "faixas", L("nem colocar o inglês", 29.6, 300, tam=90), L("num pedestal", 30.5, 420, cor="destaque", tam=120),
             L("duvidar demais", 34.8, 580, tam=100), L("de você, pessoa qualificada", 38.2, 700, tam=76, peso=700)),
    ],
    "M08": [
        cena(3.4, 10.4, "azul", "pontos", R("uma gafe", 3.8), L("eles não compreendem", 6.1, 310, tam=90),
             L("e refazem a sua frase", 9.3, 440, cor="destaque", tam=90)),
        cena(10.6, 19.8, "rosa", "grade",
             {"tipo": "colunas", "y": 300, "alt": 300, "itens": [
                 {"titulo": "Não é", "texto": "deixa eu te corrigir", "t": 10.8, "tam": 110, "sync_t": 11.6, "risco_t": 12.8},
                 {"titulo": "É", "texto": "deixa eu ver se entendi", "t": 12.8, "tam": 110, "sync_t": 13.1, "destaque_t": 14.0}]},
             L("ele tá confirmando", 18.1, 660, cor="destaque", tam=84, marcador=False)),
        cena(22.2, 32.3, "preto", "circulos", L("aspecto cultural", 22.6, 300, cor="destaque", tam=110), L("no Brasil 🇧🇷", 23.7, 440, tam=110),
             L("brasileiro questiona brasileiro", 27.3, 580, tam=76, peso=700), L("isso não precisa te travar", 30.8, 690, tam=84)),
    ],
    "M09": [
        cena(3.4, 8.8, "azul", "pontos", R("o \"é caro\"", 3.45), L("já passou na minha cabeça", 4.3, 310, tam=84),
             L("câmbio desfavorável", 8.2, 440, cor="destaque", tam=100)),
        cena(9.6, 18.9, "rosa", "grade", L("o é caro faz parte", 9.8, 300, tam=90),
             {"tipo": "colunas", "y": 440, "alt": 300, "itens": [
                 {"titulo": "Não é só", "texto": "questão financeira", "t": 14.3, "tam": 100, "sync_t": 15.3, "risco_t": 16.9},
                 {"titulo": "É também", "texto": "mentalidade", "t": 17.1, "tam": 100, "destaque_t": 18.7}]}),
        cena(20.9, 29.0, "preto", "circulos",
             {"tipo": "busca", "texto": "vale o que eu vou pagar?", "t": 21.4, "dur": 1.3, "y": 300, "tam": 58, "ate": 29.0},
             L("tive aqui os aprendizados:", 25.3, 500, tam=76, peso=700),
             L("entender aonde", 27.5, 600, tam=100), L("aquilo te leva", 28.3, 720, cor="destaque", tam=110)),
        cena(29.1, 40.55, "branco", "faixas",
             {"tipo": "colunas", "y": 300, "alt": 300, "itens": [
                 {"titulo": "Custo", "texto": "não abre portas", "t": 29.6, "tam": 110, "sync_t": 32.8, "risco_t": 37.3},
                 {"titulo": "Investimento", "texto": "o que te proporciona", "t": 37.5, "tam": 110, "sync_t": 38.2, "destaque_t": 39.4}]},
             L("daqui a um tempo?", 40.0, 660, cor="destaque", tam=90, marcador=False)),
    ],
    "M10": [
        cena(3.4, 9.6, "rosa", "pontos", R("o primeiro carro", 3.45),
             {"tipo": "chat", "y": 320, "tam": 62, "itens": [{"texto": "Nunca mais transporte público!", "t": 3.6}]},
             L("andei de transporte público", 6.5, 480, tam=76, peso=700), L("grande parte da minha vida", 7.9, 580, cor="destaque", tam=84)),
        cena(10.3, 22.9, "azul", "grade", L("vou juntar cada centavo", 10.4, 300, tam=84),
             {"tipo": "status", "titulo": "nunca mais", "y": 420, "tam": 56, "itens": [
                 {"texto": "dois ônibus", "t": 14.1, "status": "negado", "selo": "nunca mais"},
                 {"texto": "ônibus com goteira", "t": 16.8, "status": "negado", "selo": "nunca mais"},
                 {"texto": "metrô sem sentar", "t": 19.6, "status": "negado", "selo": "nunca mais", "sync_t": 20.0}]}),
        cena(22.8, 33.4, "preto", "circulos", L("todo gasto:", 22.8, 300, tam=100), L("vou juntar pra parcela", 24.9, 420, cor="destaque", tam=90),
             L("meu primeiro carro", 27.7, 560, tam=100), L("resolvia um problema", 32.5, 690, tam=90)),
        cena(33.7, 39.14, "branco", "faixas", L("o custo passou", 34.1, 300, tam=100), L("a fazer sentido", 35.6, 420, tam=100),
             L("a mesma coisa pro visto", 37.3, 560, cor="destaque", tam=90)),
    ],
    "M11": [
        cena(3.5, 10.8, "azul", "pontos", R("visto de turismo", 3.6), L("é um benefício", 5.1, 310, tam=110),
             L("nem garantia de entrar", 8.8, 440, cor="destaque", tam=96)),
        cena(11.1, 15.0, "rosa", "grade",
             {"tipo": "colunas", "y": 300, "alt": 280, "itens": [
                 {"titulo": "Ajuda?", "texto": "não é isso", "t": 11.3, "tam": 110, "risco_t": 11.8},
                 {"titulo": "Benefício", "texto": "a mais", "t": 12.8, "tam": 110, "destaque_t": 13.5}]}),
        cena(15.1, 21.5, "preto", "circulos", L("gente que começa o processo", 15.3, 300, tam=80),
             L("sem nunca ter pisado lá", 17.8, 420, cor="destaque", tam=96)),
        cena(21.7, 28.5, "branco", "faixas",
             {"tipo": "status", "titulo": "essa pessoa nunca", "y": 300, "tam": 58, "itens": [
                 {"texto": "ganhou em dólar", "t": 22.3, "status": "negado", "selo": "nunca"},
                 {"texto": "pisou nos EUA", "t": 25.4, "status": "negado", "selo": "nunca"}]}),
        cena(28.6, 34.78, "azul", "grade", L("mas essa pessoa venceu", 28.8, 300, tam=90), L("essas barreiras", 30.0, 430, cor="destaque", tam=110),
             L("e foi levando perspectivas melhores", 32.2, 580, tam=70, peso=700)),
    ],
    "M12": [
        cena(8.9, 23.2, "rosa", "pontos", R("a primeira coisa na cabeça", 9.0),
             {"tipo": "chat", "y": 320, "tam": 54, "itens": [{"texto": "Vou começar do zero.", "t": 9.4},
                                                            {"texto": "Vou ser desvalorizado.", "t": 11.0},
                                                            {"texto": "As portas estão fechadas.", "t": 14.2},
                                                            {"texto": "Vou ter que dar um jeito.", "t": 16.8},
                                                            {"texto": "O que eu sou bom não é suficiente lá.", "t": 19.9}]}),
        cena(24.2, 33.9, "azul", "grade", L("existe um aspecto cultural", 24.4, 300, tam=84), L("do brasileiro", 26.4, 410, cor="destaque", tam=110),
             L("é comum", 28.3, 560, tam=96), L("se colocar nesse lugar", 29.8, 670, tam=84), L("de devoção a outras culturas", 32.2, 780, tam=70, peso=700)),
        cena(34.4, 38.04, "preto", "circulos", L("mas é uma", 34.7, 300, tam=110), L("incompreensão", 36.0, 430, cor="destaque", tam=120),
             L("do mercado de trabalho.", 37.0, 580, tam=90)),
    ],
    "M13": [
        cena(3.3, 9.8, "azul", "pontos", L("o lugar que americano não quer?", 3.6, 300, tam=76, peso=700),
             L("não.", 6.8, 400, cor="destaque", tam=170), L("isso existe, é uma possibilidade", 7.4, 610, tam=76, peso=700)),
        cena(10.5, 20.9, "rosa", "grade", L("existe compatibilidade", 10.8, 300, tam=96), L("pra qualquer pessoa", 12.2, 420, tam=96),
             L("o mercado americano", 16.0, 560, tam=90), L("valoriza o que você traz", 18.8, 680, cor="destaque", tam=90)),
        cena(23.1, 27.9, "preto", "circulos",
             {"tipo": "busca", "texto": "não sou bom o suficiente", "t": 23.5, "dur": 1.2, "y": 300, "tam": 58, "ate": 27.9},
             L("síndrome do impostor", 25.2, 500, cor="destaque", tam=96), L("fica para trás", 27.3, 640, tam=100)),
        cena(28.0, 40.52, "branco", "faixas", R("na cultura americana, você é", 28.2),
             {"tipo": "checklist", "y": 320, "tam": 70, "passo": 104, "itens": [
                 {"texto": "seu principal encorajador", "t": 30.4}, {"texto": "seu principal vendedor", "t": 32.9},
                 {"texto": "quem mostra o seu valor", "t": 34.5}]},
             L("como vai mudar aquele ambiente", 38.5, 680, cor="destaque", tam=70, marcador=False)),
    ],
    "M14": [
        cena(3.3, 10.6, "rosa", "pontos", L("dólar não cai em árvore", 3.4, 300, cor="destaque", tam=90),
             {"tipo": "numero", "numero": "10", "rotulo": "anos aqui", "t": 4.8, "t_rotulo": 5.1, "y": 440, "tam": 260, "tam_rotulo": 90},
             L("nunca plantei um dólar", 6.2, 720, tam=84), L("nunca vi ninguém que conseguiu", 9.3, 830, tam=64, peso=700)),
        cena(10.8, 20.0, "azul", "grade", R("é sempre", 11.1),
             {"tipo": "etapas", "y": 320, "tam": 66, "passo": 118, "itens": [
                 {"texto": "causa", "t": 11.7}, {"texto": "consequência", "t": 12.3}, {"texto": "esforço", "t": 13.2}]},
             L("em qualquer lugar", 15.7, 700, cor="destaque", tam=96), L("EUA, Brasil, Europa, Ásia", 16.6, 830, tam=70, peso=700)),
        cena(21.8, 28.64, "preto", "circulos", L("o esforço que você faz hoje", 22.1, 300, tam=80),
             L("chega aonde você quer?", 23.6, 410, cor="destaque", tam=96), L("essa é a perspectiva", 26.6, 560, tam=90)),
    ],
}

if __name__ == "__main__":
    for k, cenas in ROTEIROS.items():
        r = dict(BASE, nome=f"plano27_{k}", duracao=round(DUR[k] + 3.88, 2), palavras=f"palavras/{k}.json",
                 cenas=cenas + [cta(k)])
        json.dump(r, open(os.path.join(AQUI, f"{k}.json"), "w"), ensure_ascii=False, indent=1)
    print(", ".join(sorted(ROTEIROS)))
