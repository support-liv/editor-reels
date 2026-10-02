#!/bin/bash
# Instala e confere tudo que o editor precisa (macOS).
set -e
cd "$(dirname "$0")"
ok() { echo "  ✓ $1"; }
falta() { echo "  ✗ $1"; exit 1; }

echo "Conferindo o sistema..."
[ "$(uname)" = "Darwin" ] || falta "precisa de macOS (usa Vision e VideoToolbox)"
command -v swiftc >/dev/null && ok "swiftc" || falta "instale: xcode-select --install"
command -v ffmpeg >/dev/null && ok "ffmpeg" || falta "instale: brew install ffmpeg"
ffmpeg -hide_banner -filters 2>/dev/null | grep -q scale_vt && ok "ffmpeg com VideoToolbox" || falta "ffmpeg sem scale_vt: atualize (brew upgrade ffmpeg)"
command -v python3 >/dev/null && ok "python3" || falta "instale o Python 3.10+"
command -v git-lfs >/dev/null || brew install git-lfs
git lfs install --local >/dev/null && git lfs pull && ok "Git LFS (estoque de vídeos, trilhas, transições)"

echo "Instalando pacotes Python..."
python3 -m pip install -r requirements.txt --quiet && ok "pacotes"

echo "Compilando os utilitários do macOS..."
swiftc -O editor/rostos.swift -o editor/rostos && ok "detector de rostos"
swiftc -O editor/emoji.swift -o editor/emoji && ok "gerador de emoji"
mkdir -p ~/Library/Caches/editor-reels/ads && swiftc -O editor/recorte_pessoa.swift -o ~/Library/Caches/editor-reels/ads/recorte_pessoa && ok "recorte da pessoa (texto atrás)"

echo "Baixando o modelo do Whisper (medium, ~1,5 GB, só na primeira vez)..."
python3 -c "import whisper; whisper.load_model('medium')" && ok "modelo medium" \
  || echo "  ! não baixou. Se der erro de certificado SSL, rode: /Applications/Python*/Install\ Certificates.command"

echo "Instalando o motion (HyperFrames, animações)..."
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge 22 ]; then
  (cd motion && HYPERFRAMES_NO_TELEMETRY=1 npm install --no-fund --no-audit --silent) && ok "HyperFrames" \
    && (cd motion && HYPERFRAMES_NO_TELEMETRY=1 npx hyperframes telemetry disable >/dev/null 2>&1; true)
else
  echo "  ! motion desligado: instale o Node 22+ (brew install node) e rode o setup de novo"
fi
[ -d "/Applications/Google Chrome.app" ] && ok "Chrome (render das animações)" || echo "  ! instale o Google Chrome para renderizar animações"

echo "Pronto. Falta só o login de cada pessoa (o Claude dispara): conta do time (python3 editor/conta.py entrar --email ...)"
echo "e, para publicar, o YouTube Studio (python3 editor/studio.py abrir)."
