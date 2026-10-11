@echo off
TITLE AI Quiz Analyzer - Install and Run
cd /d "%~dp0"

echo ======================================================================
echo                  AI Quiz Analyzer - Auto Setup ^& Launcher
echo ======================================================================
echo.

:: ----------------------------------------------------------------------
:: STEP 1: Detect or Auto-Download Python 3.10+
:: ----------------------------------------------------------------------
set "SYS_PYTHON="

python --version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "SYS_PYTHON=python"
    goto PYTHON_READY
)

py -3 --version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "SYS_PYTHON=py -3"
    goto PYTHON_READY
)

for %%p in (
    "%LocalAppData%\Programs\Python\Python313\python.exe"
    "%LocalAppData%\Programs\Python\Python312\python.exe"
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "%LocalAppData%\Programs\Python\Python310\python.exe"
    "C:\Program Files\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%p (
        set "SYS_PYTHON=%%~p"
        goto PYTHON_READY
    )
)

:: If Python is not on this computer, download and install silently
echo [SETUP] Python was not detected on this computer.
echo [SETUP] Automatically downloading and installing Python 3.11...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $installer = Join-Path $env:TEMP 'python-3.11.9-amd64.exe'; (New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe', $installer); Start-Process $installer -ArgumentList '/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1' -Wait; Remove-Item $installer -Force -ErrorAction SilentlyContinue"

for %%p in (
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "C:\Program Files\Python311\python.exe"
) do (
    if exist %%p (
        set "SYS_PYTHON=%%~p"
        goto PYTHON_READY
    )
)

:: Secondary fallback to graphical PowerShell wizard if needed
powershell -ExecutionPolicy Bypass -NoProfile -STA -File "%~dp0setup_installer.ps1"
if %ERRORLEVEL% equ 0 exit /b 0

echo [ERROR] Python installation could not be completed automatically.
pause
exit /b 1

:PYTHON_READY

:: ----------------------------------------------------------------------
:: STEP 2: Virtual Environment Setup
:: ----------------------------------------------------------------------
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [SETUP] Creating Python virtual environment (venv)...
    %SYS_PYTHON% -m venv "%~dp0venv"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: ----------------------------------------------------------------------
:: STEP 3: Auto-Check and Auto-Install Python Dependencies
:: ----------------------------------------------------------------------
"%~dp0venv\Scripts\python.exe" -c "import django, pypdf, pptx, PIL, openai" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [SETUP] Dependencies missing or incomplete. Installing from requirements.txt...
    "%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
    "%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" --no-warn-script-location
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
    echo [SETUP] Python packages installed successfully.
)

:: ----------------------------------------------------------------------
:: STEP 4: AI Engine (Ollama) Detection, Auto-Download & Auto-Start
:: ----------------------------------------------------------------------
set "OLLAMA_EXE="
where ollama >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%i in ('where ollama') do (
        set "OLLAMA_EXE=%%i"
        goto OLLAMA_CHECKED
    )
)

for %%o in (
    "%LocalAppData%\Programs\Ollama\ollama.exe"
    "C:\Program Files\Ollama\ollama.exe"
    "%ProgramFiles%\Ollama\ollama.exe"
    "C:\ProgramData\Ollama\ollama.exe"
) do (
    if exist %%o (
        set "OLLAMA_EXE=%%~o"
        goto OLLAMA_CHECKED
    )
)

:: If Ollama is not installed on this machine, auto-download and install silently
echo [AI ENGINE] Ollama AI engine not detected on this computer.
echo [AI ENGINE] Automatically downloading and installing Ollama...
powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $installer = Join-Path $env:TEMP 'OllamaSetup.exe'; (New-Object Net.WebClient).DownloadFile('https://ollama.com/download/OllamaSetup.exe', $installer); Start-Process $installer -ArgumentList '/silent' -Wait; Remove-Item $installer -Force -ErrorAction SilentlyContinue"

if exist "%LocalAppData%\Programs\Ollama\ollama.exe" (
    set "OLLAMA_EXE=%LocalAppData%\Programs\Ollama\ollama.exe"
) else (
    where ollama >nul 2>nul
    if %ERRORLEVEL% equ 0 (
        for /f "tokens=*" %%i in ('where ollama') do set "OLLAMA_EXE=%%i"
    )
)

:OLLAMA_CHECKED
if defined OLLAMA_EXE (
    :: Verify Ollama daemon is active
    powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [AI ENGINE] Starting local Ollama background service...
        start "" /B "%OLLAMA_EXE%" serve
        timeout /t 3 /nobreak >nul
    )

    :: Check if required llama3.2:1b model exists; auto-pull in background if missing
    powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2; if ($r.models.name -match 'llama3.2') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [AI ENGINE] Model llama3.2:1b not found. Triggering automatic background download...
        start "" /B "%OLLAMA_EXE%" pull llama3.2:1b
    )
) else (
    echo [AI ENGINE] Ollama background setup will continue automatically in the background.
)

:: ----------------------------------------------------------------------
:: STEP 5: Database Migrations & Demo Data Seeding
:: ----------------------------------------------------------------------
echo [SETUP] Verifying database schema and demo accounts...
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput >nul 2>nul
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" seed_demo >nul 2>nul

:: ----------------------------------------------------------------------
:: STEP 6: Launch Web Browser and Start Server
:: ----------------------------------------------------------------------
echo.
echo ======================================================================
echo  AI Quiz Analyzer is running!
echo  URL:      http://127.0.0.1:8000/
echo  Teacher:  teacher1 / password123
echo  Student:  student1 / password123
echo.
echo  Keep this console open while using the app. Press Ctrl+C to stop.
echo ======================================================================
echo.

start "" "http://127.0.0.1:8000/"
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver 127.0.0.1:8000
