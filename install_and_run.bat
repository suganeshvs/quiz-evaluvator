@echo off
TITLE AI Quiz Evaluator - Complete Auto-Installer & Launcher
COLOR 0A

echo =========================================================================
echo              AI Quiz Evaluator - Complete Auto-Installer
echo =========================================================================
echo.

:: 1. Check Python installation and auto-install if missing
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [NOTICE] Python is not detected on this machine.
    echo Downloading and installing Python 3.11 automatically (with Add to PATH enabled)...
    echo.
    powershell -Command "$installer = '$env:TEMP\python-installer.exe'; Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile $installer; Start-Process -FilePath $installer -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; Remove-Item $installer"
    
    :: Refresh Environment PATH variables in current session
    for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
    set "PATH=%SYS_PATH%;%USER_PATH%;C:\Program Files\Python311;C:\Program Files\Python311\Scripts;%PATH%"
    
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python installation requires system restart to update PATH.
        echo Please restart your computer and run install_and_run.bat again.
        pause
        exit /b 1
    )
    echo Python installed successfully!
    echo.
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
