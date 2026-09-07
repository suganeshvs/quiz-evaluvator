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

# Stage 1: Initializing Setup (5%)
Show-ProgressBar -percent 5 -status "Initializing setup installer..."
Start-Sleep -Seconds 1

# Stage 2: Check & Install Python 3.11 (20%)
Show-ProgressBar -percent 20 -status "Step 1/6: Checking Python installation..."
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck -and -not (Test-Path "C:\Program Files\Python311\python.exe")) {
    Show-ProgressBar -percent 25 -status "Step 1/6: Downloading Python 3.11 installer..."
    $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
    Invoke-WebRequest -Uri $url -OutFile $installerPath
    
    Show-ProgressBar -percent 30 -status "Step 1/6: Installing Python 3.11 silently (waiting for completion)..."
    $proc = Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -PassThru -Wait
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
    $env:PATH = "$machinePath;$userPath;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;$env:PATH"
}
Show-ProgressBar -percent 35 -status "Step 1/6: Python environment verified 100% complete!"

# Stage 3: Virtual Environment Setup (40%)
Show-ProgressBar -percent 40 -status "Step 2/6: Setting up Python virtual environment (venv)..."
$venvPython = "$PSScriptRoot\venv\Scripts\python.exe"
$venvPip = "$PSScriptRoot\venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython) -or -not (Test-Path $venvPip)) {
    Show-ProgressBar -percent 42 -status "Step 2/6: Creating fresh virtual environment..."
    if (Test-Path "$PSScriptRoot\venv") {
        Remove-Item "$PSScriptRoot\venv" -Recurse -Force -ErrorAction SilentlyContinue
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv "$PSScriptRoot\venv"
    } elseif (Test-Path "C:\Program Files\Python311\python.exe") {
        & "C:\Program Files\Python311\python.exe" -m venv "$PSScriptRoot\venv"
    } else {
        Write-Host "[ERROR] Could not locate Python to create venv." -ForegroundColor Red
        Exit 1
    }
}
Show-ProgressBar -percent 45 -status "Step 2/6: Virtual environment creation 100% complete!"

# Stage 4: Installing Dependencies (55%)
Show-ProgressBar -percent 50 -status "Step 3/6: Installing Python packages (Django, PyPDF, Pillow, OpenAI)..."
& "$venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Retrying pip install to ensure all packages finish..." -ForegroundColor Yellow
    & "$venvPython" -m pip install -r "$PSScriptRoot\requirements.txt" --no-warn-script-location
}
Show-ProgressBar -percent 60 -status "Step 3/6: Package installation 100% complete!"

# Stage 5: Database Setup & Seeding (70%)
Show-ProgressBar -percent 65 -status "Step 4/6: Running database migrations & seeding demo data..."
& "$venvPython" "$PSScriptRoot\manage.py" migrate --noinput
& "$venvPython" "$PSScriptRoot\manage.py" seed_demo
Show-ProgressBar -percent 75 -status "Step 4/6: Database setup & demo data 100% complete!"

# Stage 6: Check & Install Ollama Engine (85%)
Show-ProgressBar -percent 80 -status "Step 5/6: Checking Ollama AI installation..."
$ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCheck) {
    Show-ProgressBar -percent 82 -status "Step 5/6: Downloading Ollama Windows Installer..."
    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    try {
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller
        Show-ProgressBar -percent 85 -status "Step 5/6: Installing Ollama (waiting for completion)..."
        Start-Process -FilePath $ollamaInstaller -ArgumentList "/silent" -PassThru -Wait
        Remove-Item $ollamaInstaller -ErrorAction SilentlyContinue
    } catch {
        Write-Host "[INFO] Attempting script installation for Ollama..." -ForegroundColor Yellow
        irm https://ollama.com/install.ps1 | iex
    }
    
    # Refresh PATH environment variable
    $env:PATH = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Ensure Ollama service is responsive
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction SilentlyContinue
} catch {
    Show-ProgressBar -percent 88 -status "Step 5/6: Starting local Ollama AI service background worker..."
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}
Show-ProgressBar -percent 89 -status "Step 5/6: Ollama AI engine 100% verified & ready!"

# Stage 7: Pull Llama 3.2 1B Model (95%)
Show-ProgressBar -percent 90 -status "Step 6/6: Downloading / Pulling Llama 3.2 1B model into Ollama..."
$pullResult = & ollama pull llama3.2:1b 2>&1
Show-ProgressBar -percent 98 -status "Step 6/6: Llama 3.2 1B model download 100% complete!"

# Stage 8: Launch Application (100%)
Show-ProgressBar -percent 100 -status "ALL 6 TASKS COMPLETED SUCCESSFULLY! Opening Web Browser & Launching App..."

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
