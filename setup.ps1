# Instala e confere tudo que o editor precisa (Windows 10/11).
# Rodar no PowerShell, na pasta do repositório:  powershell -ExecutionPolicy Bypass -File .\setup.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
function Ok($m) { Write-Host "  OK $m" -ForegroundColor Green }
function Aviso($m) { Write-Host "  !  $m" -ForegroundColor Yellow }

function Garantir($cmd, $id, $nome) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { Ok $nome; return }
    Write-Host "  instalando $nome..."
    winget install --id $id -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    if (Get-Command $cmd -ErrorAction SilentlyContinue) { Ok $nome } else { Aviso "$nome instalado: feche e abra o terminal e rode o setup de novo" }
}

Write-Host "Conferindo o sistema..."
Garantir "git" "Git.Git" "Git"
Garantir "git-lfs" "GitHub.GitLFS" "Git LFS"
Garantir "ffmpeg" "Gyan.FFmpeg" "ffmpeg (versao full, com zscale para HDR)"
Garantir "node" "OpenJS.NodeJS.LTS" "Node.js (motion)"
if (-not (Get-Command "py" -ErrorAction SilentlyContinue) -or -not (py -3.12 --version 2>$null)) {
    Write-Host "  instalando Python 3.12 (o MediaPipe ainda nao tem versao para Python mais novo)..."
    winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
}
Ok "Python 3.12"
if (-not (Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe") -and -not (Test-Path "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe")) {
    winget install --id Google.Chrome -e --accept-source-agreements --accept-package-agreements --silent | Out-Null
}
Ok "Chrome (Studio do YouTube e render das animacoes)"

Write-Host "Baixando os arquivos grandes (estoque de videos, trilhas, transicoes)..."
git lfs install --local | Out-Null
git lfs pull
Ok "Git LFS"

Write-Host "Instalando pacotes Python..."
py -3.12 -m pip install --upgrade pip --quiet
py -3.12 -m pip install -r requirements.txt --quiet
Ok "pacotes (Whisper, OpenCV, MediaPipe, librosa, Playwright, keyring)"

Write-Host "Baixando o modelo do Whisper (medium, ~1,5 GB, so na primeira vez)..."
py -3.12 -c "import whisper; whisper.load_model('medium')"
Ok "modelo medium"

Write-Host "Instalando o motion (HyperFrames)..."
Push-Location motion
$env:HYPERFRAMES_NO_TELEMETRY = "1"
npm install --no-fund --no-audit --silent
npx hyperframes telemetry disable 2>$null | Out-Null
Pop-Location
Ok "HyperFrames"

Write-Host "Conferindo o codificador de video..."
py -3.12 -c "import sys; sys.path.insert(0,'editor'); import plataforma as P; print('  codificador:', P.codificador())"

Write-Host ""
Write-Host "Pronto. Falta so o login de cada pessoa (o Claude dispara): conta do time"
Write-Host "(py -3.12 editor\conta.py entrar --email ...) e, para publicar, o YouTube Studio (py -3.12 editor\studio.py abrir)."
