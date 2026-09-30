# Formatos

Os formatos que o time publica, e como cada um é editado. Definidos com o time de marketing (set/2026). Mude só com motivo, e registre no CHANGELOG.

## Por destino

| Formato | Marca | Tela | Legenda | Gancho | CTA | Vinheta |
|---|---|---|---|---|---|---|
| **Corte longo YouTube** | LIV (lives) | 16:9, 1080p (a saída da live) | Não (o YouTube gera) | Não | Não | **Sim**, no começo |
| **Reels / Shorts** | LIV e Imigrar | 9:16, 1080x1920 | Sim, cor da marca | Sim, só a pergunta | Caixa no fim | Não |
| **Stories** | LIV e Imigrar | 9:16 | Sim | Não precisa | Sticker | Não |
| **WhatsApp** | LIV | 1:1, 1080x1080 | Sim, cor da marca | Não | Não | Não |
| **Anúncio** | LIV e Imigrar | 9:16 | Sim, a 55% da altura | Sim | Não (o Meta põe o botão) | Não |
| **Carrossel** | LIV e Imigrar | 4:5, 1080x1350 | — | Capa | Último card | Não |

### Corte longo YouTube
- **8 a 12 minutos.** Uma live boa rende um corte longo; se o conteúdo render, 2 ou 3.
- Cada corte é um assunto fechado, com começo, meio e fim. Não começa no meio de uma frase.
- **Vinheta** `assets/vinheta_cortes_liv.mp4`: 3,80s de imagem (o flash branco da trilha foi tirado) e o som da transição continua ~0,9s por cima do começo da live. **Só no corte longo.**
- Live da **Imigrar não tem introdução**.
- Como fazer: `--layout youtube --marca liv --trechos "..."` (ver OPCOES.md). A Imigrar usa `--sem-vinheta`.
- Entregas junto com o vídeo: título, descrição, capítulos com minutagem (a partir do `.tempos.txt`), tags e sugestão de texto para a thumbnail.

### Reels / Shorts
- 30 a 50s: gancho, desenvolvimento, CTA.
- **Gancho:** só a pergunta ou a curiosidade, nunca a resposta (ver PADROES.md).
- **CTA por canal:** YouTube Shorts (corte de live) = "Veja a live completa no canal"; Instagram = palavra-chave de automação ou link na bio. Perguntar o canal no briefing.
- **CTA:** **depois da fala final**, numa cauda de 3-4s (`--cauda 3.8`), em cena animada de tela cheia (versão enxuta e com motion). Em Reels feitos fora de live, pode ser a caixa de texto no fim. Padrão: "Link na bio". Quando a campanha usa automação, é uma **palavra-chave** ("Comente PERFIL para uma análise do seu perfil"). A palavra **muda por campanha e por vídeo**: sempre confirmar. Às vezes a pessoa também fala o CTA no vídeo.
- Entregas junto: legenda do post e hashtags.

### Stories
- **Curtos e objetivos, com enredo**: uma história com começo, meio e fim em poucos stories. Nunca uma colagem de clipes soltos.
- Como fazer: cada story é um corte vertical curto (5 a 15s) no editor normal, com `--gancho` como texto do story quando precisar. O roteiro (ordem, texto de cada story e sticker) vai num `.md` junto dos vídeos.
- Entregas: os cortes, o texto de cada story e a sugestão de sticker (enquete, caixinha, link, contagem).

### Carrossel
- **Tem que desenvolver uma narrativa**, não é capa + um card + CTA. Em média **7 a 10 cards**:
  1. **Capa:** o gancho (pergunta ou curiosidade, sem entregar a resposta).
  2. **Contexto:** a situação ou a dor de quem lê.
  3. **Desenvolvimento (3 a 5 cards):** um ponto por card, em sequência lógica; cada card puxa o próximo.
  4. **Virada:** o insight ou o erro mais comum.
  5. **Resumo:** o que levar do carrossel.
  6. **CTA:** palavra-chave ou link na bio.
- Como fazer: `python3 editor/carrossel.py roteiro.json` (ver OPCOES.md). A capa pode usar um quadro do vídeo.
- Entregas: os PNGs, o texto de cada card e a legenda do post. Fontes e cores da marca (abaixo).

## Por tipo de cena

| Cena | Enquadramento | Respiros |
|---|---|---|
| Live com 2 pessoas | `--layout dividido`: tela dividida, **fixa**, sem crop | Padrão |
| Live com 3 pessoas lado a lado | Shorts: `--layout dividido --colunas 3 --pessoas 3,1` (as 2 que conversam; quem fala em cima). Corte longo: normal no wide. Trechos com uma pessoa só na tela: vertical em tela cheia | Padrão (live Jornada do dentista) |
| Live com 1 pessoa, 1080p ou 4K | Tela cheia, com crops e zoom | Tira |
| Live com 1 pessoa, **720p** | **Perguntar:** `--layout quadro` (imagem nítida com fundo desfocado, pode ter zoom leve) **ou** tela cheia, perdendo qualidade | Tira |
| Entrevista / fala pra câmera | Dinâmico: zoom alternando por bloco | Tira |
| Quem fala travado | `--dinamico` (zoom a cada ~2,5s) e `--respiro 0.35` | Mais natural |

## Marcas

| | LIV | Imigrar |
|---|---|---|
| Funil | Meio | Topo |
| Fonte | Darker Grotesque (`assets/fontes/`) | Inter Tight (`assets/fontes/`) |
| Destaque | Laranja #FF6E1F | Rosa #F90D5B |
| Apoio | Azul Trust #2C3642, Marrom #945943, Bege #FFF0E6, Branco | Azul #0E59C5, Branco |

- LIV: manual de identidade visual (Manual de Identidade Visual LIV.pdf). Logo nunca rotacionado, deformado ou em cor fora da paleta.
- Todo vídeo da LIV passa pela revisão interna antes de publicar.
