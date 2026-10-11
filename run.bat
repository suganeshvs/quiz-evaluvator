@echo off
TITLE AI Quiz Analyzer
cd /d "%~dp0"

:: If first-time run without venv, delegate to install_and_run.bat
if not exist "%~dp0venv\Scripts\python.exe" (
    call "%~dp0install_and_run.bat"
    exit /b %ERRORLEVEL%
)

echo ======================================================================
echo                  AI Quiz Analyzer - Quick Launcher
echo ======================================================================
echo.

echo [INFO] Virtual environment active.
echo [INFO] Checking database migrations...
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" migrate --noinput >nul 2>nul
"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" seed_demo >nul 2>nul

echo [INFO] Launching browser at http://127.0.0.1:8000/ ...
start "" "http://127.0.0.1:8000/"

echo.
echo ======================================================================
echo  AI Quiz Analyzer is running at http://127.0.0.1:8000/
echo  Teacher:  teacher1 / password123
echo  Student:  student1 / password123
echo.
echo  Keep this console window open while using the application.
echo  Press Ctrl+C to stop the server when finished.
echo ======================================================================
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0manage.py" runserver 127.0.0.1:8000
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Server terminated with error code %ERRORLEVEL%.
    pause
)
