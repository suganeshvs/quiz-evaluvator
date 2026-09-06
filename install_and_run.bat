@echo off
TITLE AI Quiz Evaluator - Installer & Launcher
COLOR 0A

echo =========================================================================
echo               AI Quiz Evaluator - Setup & Launch Script
echo =========================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://www.python.org/ and try again.
    pause
    exit /b 1
)

echo [1/5] Python detected! Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

:: 2. Activate virtual environment and install requirements
call venv\Scripts\activate.bat

echo.
echo [2/5] Installing Python dependencies...
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

:: 3. Setup database migrations and demo data
echo.
echo [3/5] Setting up database and demo data...
python manage.py migrate
python manage.py seed_demo

:: 4. Check & Install Ollama
echo.
echo [4/5] Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama not found on this system. Installing Ollama automatically via PowerShell...
    powershell -Command "irm https://ollama.com/install.ps1 | iex"
) else (
    echo Ollama is already installed!
)

:: 5. Pull Llama 3.2 1B Model
echo.
echo [5/5] Checking / Pulling Ollama Model (llama3.2:1b)...
echo Download in progress... Please wait.
ollama pull llama3.2:1b

echo.
echo =========================================================================
echo                SETUP COMPLETE! Launching Web Application...
echo =========================================================================
echo App URL: http://127.0.0.1:8000/
echo Demo Teacher Credentials: teacher1 / password123
echo Demo Student Credentials: student1 / password123
echo =========================================================================
echo.

:: Open browser automatically after 3 seconds
start "" "http://127.0.0.1:8000/"

:: Run Django server
python manage.py runserver 127.0.0.1:8000

pause
