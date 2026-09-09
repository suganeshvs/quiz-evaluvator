import subprocess
import tempfile
import os

vbs_path = os.path.join(tempfile.gettempdir(), 'test_dialog.vbs')
with open(vbs_path, 'w', encoding='utf-8') as f:
    f.write('res = MsgBox("Do you want to install and run AI Quiz Analyzer now?", 36, "AI Quiz Analyzer Setup")\n')
    f.write('WScript.Quit(res)\n')

print(f"Created VBS file at {vbs_path}")
proc = subprocess.run(['cscript', '//nologo', vbs_path], capture_output=True, text=True)
print(f"VBS Exit Code: {proc.returncode}")
# 6 = Yes, 7 = No
if proc.returncode == 6:
    print("User clicked YES!")
else:
    print("User clicked NO or closed!")
