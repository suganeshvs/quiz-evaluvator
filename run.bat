@echo off
TITLE AI Quiz Analyzer
cd /d "%~dp0"

:: If environment not initialized, delegate to full auto-installer
if not exist "%~dp0venv\Scripts\python.exe" (
    call "%~dp0install_and_run.bat"
    exit /b %ERRORLEVEL%
)

echo ======================================================================
echo                  AI Quiz Analyzer - Quick Launcher
echo ======================================================================
echo.

:: 1. Validate dependencies are intact
"%~dp0venv\Scripts\python.exe" -c "import django, pypdf, pptx, PIL, openai" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Detected missing dependencies. Updating packages...
    "%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" --quiet --no-warn-script-location
)

:: 2. Auto-detect / Auto-install Ollama AI Engine
set "OLLAMA_EXE="
where ollama >nul 2>nul
if %ERRORLEVEL% equ 0 (
    for /f "tokens=*" %%i in ('where ollama') do set "OLLAMA_EXE=%%i"
) else (
    for %%o in (
        "%LocalAppData%\Programs\Ollama\ollama.exe"
        "C:\Program Files\Ollama\ollama.exe"
        "%ProgramFiles%\Ollama\ollama.exe"
    ) do (
        if exist %%o set "OLLAMA_EXE=%%~o"
    )
)

if not defined OLLAMA_EXE (
    echo [AI ENGINE] Ollama AI engine not detected on this machine.
    echo [AI ENGINE] Downloading and installing Ollama automatically...
    powershell -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $installer = Join-Path $env:TEMP 'OllamaSetup.exe'; (New-Object Net.WebClient).DownloadFile('https://ollama.com/download/OllamaSetup.exe', $installer); Start-Process $installer -ArgumentList '/silent' -Wait; Remove-Item $installer -Force -ErrorAction SilentlyContinue"
    if exist "%LocalAppData%\Programs\Ollama\ollama.exe" (
        set "OLLAMA_EXE=%LocalAppData%\Programs\Ollama\ollama.exe"
    )
)

if defined OLLAMA_EXE (
    powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [INFO] Starting local Ollama background service...
        start "" /B "%OLLAMA_EXE%" serve
        timeout /t 2 /nobreak >nul
    )

    powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 2; if ($r.models.name -match 'llama3.2') { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [INFO] Triggering background pull for llama3.2:1b model...
        start "" /B "%OLLAMA_EXE%" pull llama3.2:1b
    )
)

:: 3. Database migrations & seed
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput >nul 2>nul
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" seed_demo >nul 2>nul

echo.
echo ======================================================================
echo  AI Quiz Analyzer is running at http://127.0.0.1:8000/
echo  Teacher:  teacher1 / password123
echo  Student:  student1 / password123
echo.
echo  Keep this console open while using the app. Press Ctrl+C to stop.
echo ======================================================================
echo.

start "" "http://127.0.0.1:8000/"
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver 127.0.0.1:8000
