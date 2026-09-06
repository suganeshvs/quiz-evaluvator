@echo off
TITLE AI Quiz Evaluator - Setup & Installer (0-100%)
COLOR 0A

:: Run PowerShell setup script with ExecutionPolicy Bypass
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0setup_installer.ps1"

pause
