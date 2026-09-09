@echo off
TITLE AI Quiz Evaluator Setup
cd /d "%~dp0"

:: Display Native Windows GUI Pop-up Dialog Box (Yes / No)
set "VBS_POPUP=%TEMP%\ai_quiz_setup_popup_%RANDOM%.vbs"
echo res = MsgBox("Do you want to install and run AI Quiz Analyzer now?", 36, "AI Quiz Analyzer Setup") > "%VBS_POPUP%"
echo WScript.Quit(res) >> "%VBS_POPUP%"

cscript //nologo "%VBS_POPUP%"
set "POPUP_RESULT=%ERRORLEVEL%"
if exist "%VBS_POPUP%" del /f /q "%VBS_POPUP%"

if %POPUP_RESULT% NEQ 6 (
    exit /b 0
)

:: Launch WPF GUI Installer script cleanly in separate window
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "%~dp0setup_installer.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] AI Quiz Evaluator Setup script failed to launch or exited with an error.
    echo Please ensure PowerShell is enabled on your Windows system.
    pause
)

