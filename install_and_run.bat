@echo off
TITLE AI Quiz Analyzer - Install and Run
cd /d "%~dp0"

echo ======================================================================
echo                  AI Quiz Analyzer - Setup and Launcher
echo ======================================================================
echo.

:: 1. If virtual environment already exists and works, launch immediately!
if exist "%~dp0venv\Scripts\python.exe" (
    echo [INFO] Virtual environment found. Launching AI Quiz Analyzer...
    echo.
    "%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput
    "%~dp0venv\Scripts\python.exe" "%~dp0manage.py" seed_demo
    echo.
    echo [INFO] Starting browser at http://127.0.0.1:8000/ ...
    start "" "http://127.0.0.1:8000/"
    echo.
    echo ======================================================================
    echo  AI Quiz Analyzer is running!
    echo  URL:      http://127.0.0.1:8000/
    echo  Teacher:  teacher1 / password123
    echo  Student:  student1 / password123
    echo.
    echo  Leave this window open while using the app. Press Ctrl+C to stop.
    echo ======================================================================
    echo.
    "%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver 127.0.0.1:8000
    exit /b %ERRORLEVEL%
)

:: 2. First-time setup on a new machine: Detect Python
echo [SETUP] First-time setup detected. Checking Python installation...

set "SYS_PYTHON="

:: Check standard 'python'
python --version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "SYS_PYTHON=python"
    goto PYTHON_FOUND
)

:: Check Python Launcher 'py'
py -3 --version >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "SYS_PYTHON=py -3"
    goto PYTHON_FOUND
)

:: Search common Windows installation paths
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
        goto PYTHON_FOUND
    )
)

:PYTHON_NOT_FOUND
echo.
echo [WARNING] Python 3.10+ was not detected in PATH.
echo Attempting automated environment setup via PowerShell...
echo.
powershell -ExecutionPolicy Bypass -NoProfile -STA -File "%~dp0setup_installer.ps1"
if %ERRORLEVEL% equ 0 exit /b 0

echo.
echo [ERROR] Python 3.10 or higher is required to run AI Quiz Analyzer.
echo Please download and install Python from: https://www.python.org/downloads/
echo Make sure to check "Add python.exe to PATH" during installation.
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [INFO] Using Python: %SYS_PYTHON%
echo.

:: 3. Create virtual environment
echo [1/4] Creating Python virtual environment (venv)...
%SYS_PYTHON% -m venv "%~dp0venv"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:: 4. Install dependencies
echo [2/4] Installing dependencies from requirements.txt...
"%~dp0venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" --no-warn-script-location
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:: 5. Run migrations & demo seed
echo [3/4] Setting up database and demo accounts...
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" seed_demo

:: 6. Launch browser and start Django server
echo [4/4] Launching application...
echo.
echo Opening web browser at http://127.0.0.1:8000/ ...
start "" "http://127.0.0.1:8000/"

echo.
echo ======================================================================
echo  Setup Complete! AI Quiz Analyzer is running at http://127.0.0.1:8000/
echo  Teacher:  teacher1 / password123
echo  Student:  student1 / password123
echo.
echo  Keep this window open while using the application.
echo  Press Ctrl+C to stop the server when finished.
echo ======================================================================
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver 127.0.0.1:8000
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Server exited with code %ERRORLEVEL%.
    pause
)
