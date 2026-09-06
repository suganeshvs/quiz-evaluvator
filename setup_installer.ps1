# AI Quiz Evaluator - Complete Auto-Installer & Launcher with Visual 0-100% Progress Bar

$Host.UI.RawUI.WindowTitle = "AI Quiz Evaluator - Setup & Installer (0-100%)"

function Show-ProgressBar {
    param (
        [int]$percent,
        [string]$status
    )
    $width = 40
    $filled = [math]::Floor(($percent / 100) * $width)
    $unfilled = $width - $filled
    
    $filledChar = [char]0x2588
    $unfilledChar = [char]0x2591
    
    $bar = ("$filledChar" * $filled) + ("$unfilledChar" * $unfilled)
    
    Write-Host ""
    Write-Host "------------------------------------------------------------------------" -ForegroundColor Gray
    Write-Host "  PROGRESS: [$bar] " -NoNewline -ForegroundColor Yellow
    Write-Host "$percent%" -ForegroundColor Green
    Write-Host "  STATUS  : $status" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------------------" -ForegroundColor Gray
    Write-Host ""
}

Clear-Host
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "            AI QUIZ EVALUATOR - AUTOMATED SETUP INSTALLER               " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

# Stage 1: Initializing
Show-ProgressBar -percent 5 -status "Initializing setup installer..."

# Stage 2: Check & Install Python 3.11 (20%)
Show-ProgressBar -percent 20 -status "Checking Python installation..."
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck -and -not (Test-Path "C:\Program Files\Python311\python.exe")) {
    Show-ProgressBar -percent 25 -status "Downloading Python 3.11 installer from Python.org..."
    $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile $installerPath
    
    Show-ProgressBar -percent 30 -status "Installing Python 3.11 silently (with Add to PATH enabled)..."
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
    $env:PATH = "$machinePath;$userPath;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;$env:PATH"
}
Show-ProgressBar -percent 35 -status "Python environment ready!"

# Stage 3: Virtual Environment & Dependencies (50%)
Show-ProgressBar -percent 40 -status "Setting up Python virtual environment (venv)..."
$venvPython = "$PSScriptRoot\venv\Scripts\python.exe"
$venvPip = "$PSScriptRoot\venv\Scripts\pip.exe"

# If venv is missing or pip corrupted, recreate fresh venv
if (-not (Test-Path $venvPython) -or -not (Test-Path $venvPip)) {
    Show-ProgressBar -percent 42 -status "Creating fresh virtual environment..."
    if (Test-Path "$PSScriptRoot\venv") {
        Remove-Item "$PSScriptRoot\venv" -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -m venv "$PSScriptRoot\venv"
    } elseif (Test-Path "C:\Program Files\Python311\python.exe") {
        & "C:\Program Files\Python311\python.exe" -m venv "$PSScriptRoot\venv"
    } else {
        Write-Host "[ERROR] Could not locate Python to create venv." -ForegroundColor Red
        Exit 1
    }
}

Show-ProgressBar -percent 50 -status "Installing requirements (Django, PyPDF, Pillow, OpenAI)..."
& "$venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location --quiet

# Stage 4: Database Setup (65%)
Show-ProgressBar -percent 65 -status "Configuring database migrations & seeding demo data..."
& "$venvPython" "$PSScriptRoot\manage.py" migrate --noinput
& "$venvPython" "$PSScriptRoot\manage.py" seed_demo

# Stage 5: Check & Install Ollama (80%)
Show-ProgressBar -percent 80 -status "Checking Ollama AI installation..."
$ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCheck) {
    Show-ProgressBar -percent 82 -status "Downloading & Installing Ollama automatically..."
    irm https://ollama.com/install.ps1 | iex
}

# Stage 6: Pull Llama 3.2 1B Model (95%)
Show-ProgressBar -percent 90 -status "Checking / Pulling Llama 3.2 1B model into Ollama..."
ollama pull llama3.2:1b

# Stage 7: Complete (100%)
Show-ProgressBar -percent 100 -status "ALL INSTALLATIONS COMPLETE! Opening Chrome & Launching App..."

Write-Host "========================================================================" -ForegroundColor Green
Write-Host "               SETUP COMPLETE! Launching Application...                 " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  URL     : http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "  Teacher : teacher1 / password123" -ForegroundColor Gray
Write-Host "  Student : student1 / password123" -ForegroundColor Gray
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""

# Open Chrome specifically if available, otherwise default browser
$chromePath = "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe"
$chromePathx86 = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"

if (Test-Path $chromePath) {
    Start-Process $chromePath "http://127.0.0.1:8000/"
} elseif (Test-Path $chromePathx86) {
    Start-Process $chromePathx86 "http://127.0.0.1:8000/"
} else {
    Start-Process "http://127.0.0.1:8000/"
}

# Launch Django server using venv Python
& "$venvPython" "$PSScriptRoot\manage.py" runserver 127.0.0.1:8000
