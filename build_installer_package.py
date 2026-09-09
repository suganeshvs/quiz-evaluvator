import os
import zipfile
import base64

def create_installer_zip():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "static", "downloads")
    deploy_dir = os.path.join(base_dir, "deploy_landing")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(deploy_dir, exist_ok=True)

    zip_filename = "AI_Quiz_Analyzer_Setup.zip"
    target_zip_path = os.path.join(output_dir, zip_filename)
    root_zip_path = os.path.join(base_dir, zip_filename)

    included_dirs = ['ai_quiz_analyzer', 'quiz_app', 'templates', 'static', 'media']
    included_files = ['install_and_run.bat', 'setup_installer.ps1', 'manage.py', 'requirements.txt', 'db.sqlite3', 'logo.ico', 'README.md']

    print(f"Creating installer ZIP package: {zip_filename}...")

    def archive_files(zip_obj):
        # Top-level files
        for f in included_files:
            file_path = os.path.join(base_dir, f)
            if os.path.exists(file_path):
                zip_obj.write(file_path, arcname=f)

        # Top-level directories
        for d in included_dirs:
            dir_path = os.path.join(base_dir, d)
            if os.path.exists(dir_path):
                for root, _, files in os.walk(dir_path):
                    for file in files:
                        if file.endswith('.pyc') or '__pycache__' in root or zip_filename in file or 'deploy_landing' in root:
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, base_dir)
                        zip_obj.write(full_path, arcname=rel_path)

    # Write to static downloads
    with zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        archive_files(zipf)

    # Write to root
    with zipfile.ZipFile(root_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        archive_files(zipf)

    print(f"ZIP package created successfully!\n - {target_zip_path}\n - {root_zip_path}")

    # Build Self-Extracting One-Click Launcher Batch (AI_Quiz_Analyzer_Installer.bat)
    print("Building Self-Extracting One-Click Launcher Batch...")
    with open(root_zip_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")

    sfx_bat_content = f"""@echo off
TITLE AI Quiz Analyzer Setup Launcher
cd /d "%~dp0"

:: 1. Display Native Windows GUI Pop-up Dialog Box (Yes / No)
set "VBS_POPUP=%TEMP%\\ai_quiz_setup_popup_%RANDOM%.vbs"
echo res = MsgBox("Do you want to install and run AI Quiz Analyzer now?", 36, "AI Quiz Analyzer Setup") > "%VBS_POPUP%"
echo WScript.Quit(res) >> "%VBS_POPUP%"

cscript //nologo "%VBS_POPUP%"
set "POPUP_RESULT=%ERRORLEVEL%"
if exist "%VBS_POPUP%" del /f /q "%VBS_POPUP%"

if %POPUP_RESULT% NEQ 6 (
    exit /b 0
)


:: 2. Auto-Extract embedded files to %TEMP%\\AI_Quiz_Analyzer_Setup
set "EXTRACT_DIR=%TEMP%\\AI_Quiz_Analyzer_Setup"
if exist "%EXTRACT_DIR%" rmdir /s /q "%EXTRACT_DIR%"
mkdir "%EXTRACT_DIR%"

powershell -ExecutionPolicy Bypass -NoProfile -Command "$b64 = '{b64_data}'; $bytes = [System.Convert]::FromBase64String($b64); $zipPath = '%EXTRACT_DIR%\\package.zip'; [System.IO.File]::WriteAllBytes($zipPath, $bytes); Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, '%EXTRACT_DIR%'); Remove-Item $zipPath -Force"

:: 3. Automatically execute setup_installer.ps1
powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "%EXTRACT_DIR%\\setup_installer.ps1"
"""

    sfx_bat_path = os.path.join(base_dir, "AI_Quiz_Analyzer_Installer.bat")
    sfx_deploy_path = os.path.join(deploy_dir, "AI_Quiz_Analyzer_Installer.bat")
    sfx_static_path = os.path.join(output_dir, "AI_Quiz_Analyzer_Installer.bat")

    with open(sfx_bat_path, "w", encoding="utf-8") as f:
        f.write(sfx_bat_content)
    with open(sfx_deploy_path, "w", encoding="utf-8") as f:
        f.write(sfx_bat_content)
    with open(sfx_static_path, "w", encoding="utf-8") as f:
        f.write(sfx_bat_content)

    print(f"Self-Extracting One-Click Launcher created successfully!\n - {sfx_bat_path}\n - {sfx_deploy_path}")

if __name__ == "__main__":
    create_installer_zip()
