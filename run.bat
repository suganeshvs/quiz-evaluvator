@echo off
TITLE AI Quiz Evaluator
cd /d "%~dp0"

:: Launch graphical launcher and progress bar wizard in STA mode
powershell -ExecutionPolicy Bypass -NoProfile -STA -File "%~dp0setup_installer.ps1"
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Launcher encountered an issue. Exit code: %ERRORLEVEL%
    pause
)
exit /b %ERRORLEVEL%
