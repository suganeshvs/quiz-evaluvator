# AI Quiz Evaluator - PowerShell Installer & Launcher Script

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "              AI Quiz Evaluator - Setup & Launch Script" -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python and auto-install Python 3.11 with PrependPath=1 if missing
$pythonCheck = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCheck) {
    Write-Host "[NOTICE] Python is not installed. Auto-downloading and installing Python 3.11..." -ForegroundColor Yellow
    $url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    $installerPath = "$env:TEMP\python-3.11.9-amd64.exe"
    
    Write-Host "Downloading Python installer from Python.org..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $url -OutFile $installerPath
    
    Write-Host "Installing Python 3.11 silently with 'Add Python to PATH' enabled..." -ForegroundColor Yellow
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item $installerPath -ErrorAction SilentlyContinue
    
    # Refresh PATH in current process
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    $userPath = [System.Environment]::GetEnvironmentVariable("Path","User")
    $env:PATH = "$machinePath;$userPath;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;$env:PATH"
    
    Write-Host "Python 3.11 installed successfully!" -ForegroundColor Green
} else {
    $pythonVersion = python --version 2>&1
    Write-Host "[1/5] Python detected: $pythonVersion" -ForegroundColor Green
}

# 2. Virtual Environment
if (-not (Test-Path "venv")) {
    Write-Host "[2/5] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "[2/5] Virtual environment already exists." -ForegroundColor Green
}

# Activate venv
$env:PATH = "$PSScriptRoot\venv\Scripts;$env:PATH"

# Install Dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip | Out-Null
pip install -r requirements.txt

# 3. Database Setup
Write-Host "[3/5] Migrating database & seeding demo data..." -ForegroundColor Yellow
python manage.py migrate
python manage.py seed_demo

# 4. Ollama Check & Install
Write-Host "[4/5] Checking Ollama installation..." -ForegroundColor Yellow
$ollamaCheck = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCheck) {
    Write-Host "Ollama is not installed. Installing Ollama automatically..." -ForegroundColor Cyan
    irm https://ollama.com/install.ps1 | iex
} else {
    Write-Host "Ollama is installed." -ForegroundColor Green
}

# 5. Pull Model
Write-Host "[5/5] Pulling llama3.2:1b model..." -ForegroundColor Yellow
ollama pull llama3.2:1b

Write-Host ""
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "               SETUP COMPLETE! Launching Application..." -ForegroundColor Green
Write-Host "=========================================================================" -ForegroundColor Green
Write-Host "URL: http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "Teacher: teacher1 / password123" -ForegroundColor Gray
Write-Host "Student: student1 / password123" -ForegroundColor Gray
Write-Host "=========================================================================" -ForegroundColor Green

# Open browser and start server
Start-Process "http://127.0.0.1:8000/"
python manage.py runserver 127.0.0.1:8000
