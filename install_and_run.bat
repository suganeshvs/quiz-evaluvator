@echo off
TITLE "AI Quiz Evaluator Setup"
COLOR 0A

:: Launch WPF GUI Installer script cleanly in separate window
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "%~dp0setup_installer.ps1"


