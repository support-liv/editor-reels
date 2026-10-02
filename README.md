# editor-reels

Editor automático de Reels e anúncios em vídeo vertical. Pega o vídeo bruto do iPhone e entrega o arquivo pronto para postar:

- corta as perguntas do entrevistador, os silêncios e os respiros, pelo áudio
- enquadra em 9:16 seguindo o rosto de quem fala (inclusive numa conversa com várias pessoas)
- converte a cor do HDR do iPhone para o padrão das redes
- queima a legenda palavra a palavra, com a palavra falada destacada na cor da marca
- coloca o gancho em caixa alta no começo, sem tapar o rosto
- normaliza o áudio para o volume do Instagram (-14 LUFS)
- tem auditorias antes (takes lidos do celular) e depois (buracos entre falas)

Roda 100% local no **Mac ou no Windows**, sem serviço pago: ffmpeg, Whisper, Python e o detector de rostos do sistema (Vision no Mac, OpenCV no Windows).

## Começo rápido

Mac:
```bash
git clone https://github.com/support-liv/editor-reels.git
cd editor-reels
./setup.sh
```

Windows (PowerShell):
```powershell
git clone https://github.com/support-liv/editor-reels.git
cd editor-reels
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Depois, abra o Claude **dentro da pasta `editor-reels`** (assim ele lê o `CLAUDE.md`, as skills e os agentes do projeto)
e arraste o vídeo para a conversa. O Claude roda os comandos; você só faz os logins (link no e-mail e o YouTube Studio).

Um vídeo, com uma pessoa só:
```bash
python3 editor/editor_reels.py ~/Videos/IMG_1234.MOV --gancho "Dentista, já pensou em morar nos EUA 🇺🇸?"
```
O arquivo sai em `./prontos/`.

## Documentação

| Documento | Para quê |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Como o Claude trabalha aqui: briefing curto, regras, conferência |
| [docs/FORMATOS.md](docs/FORMATOS.md) | Formatos (corte longo, Reels, stories, WhatsApp, anúncio, carrossel), estilo por cena e marcas |
| [docs/FLUXO.md](docs/FLUXO.md) | Passo a passo do time: do bruto ao vídeo aprovado |
| [docs/OPCOES.md](docs/OPCOES.md) | Todas as opções do editor e dos comandos de auditoria |
| [docs/PADROES.md](docs/PADROES.md) | Padrões visuais validados (legenda, gancho, bandeira, cor, anúncio x orgânico) e o porquê de cada um |
| [docs/GRAVACAO.md](docs/GRAVACAO.md) | Como gravar para a edição sair melhor |
| [docs/NOVO_PROJETO.md](docs/NOVO_PROJETO.md) | Como montar o lote de um projeto novo |
| [CHANGELOG.md](CHANGELOG.md) | O que mudou e por quê |

## Estrutura

```
editor/                 a ferramenta
  editor_reels.py       editor principal
  auditar.py            auditoria do bruto (frase por frase, % do tempo olhando pra baixo)
  auditar_pronto.py     auditoria do vídeo pronto (buracos e olhar)
  transcrever_lote.py   transcreve vários vídeos de uma vez
  rostos.swift          detector de rostos (Vision do macOS), compilado sozinho
  emoji.swift           gera a imagem das bandeiras
projetos/
  in26/                 lotes do evento IN26 (exemplo real de uso)
  _modelo/lote_modelo.py  ponto de partida para um projeto novo
docs/                   documentação
```

## Requisitos
- macOS 13+ (usa o Vision e o VideoToolbox do sistema)
- Xcode Command Line Tools (`xcode-select --install`)
- Homebrew + ffmpeg (`brew install ffmpeg`)
- Python 3.10+
- ~2 GB para o modelo do Whisper e espaço para os vídeos
