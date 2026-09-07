@echo off
TITLE AI Quiz Evaluator Setup
COLOR 0A
cd /d "%~dp0"

:: Launch WPF GUI Installer script cleanly in separate window
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "%~dp0setup_installer.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] AI Quiz Evaluator Setup script failed to launch or exited with an error.
    echo Please ensure PowerShell is enabled on your Windows system.
    pause
)
