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

echo "Instalando pacotes Python..."
python3 -m pip install -r requirements.txt --quiet && ok "pacotes"

echo "Compilando os utilitários do macOS..."
swiftc -O editor/rostos.swift -o editor/rostos && ok "detector de rostos"
swiftc -O editor/emoji.swift -o editor/emoji && ok "gerador de emoji"

echo "Baixando o modelo do Whisper (medium, ~1,5 GB, só na primeira vez)..."
python3 -c "import whisper; whisper.load_model('medium')" && ok "modelo medium" \
  || echo "  ! não baixou. Se der erro de certificado SSL, rode: /Applications/Python*/Install\ Certificates.command"

echo "Pronto. Teste: python3 editor/editor_reels.py --help"
