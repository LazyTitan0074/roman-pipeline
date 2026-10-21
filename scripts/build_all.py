""" Build unic, ordine garantata: format(live) -> copy(arhiva) -> epub(din arhiva). """
import shutil
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8")
LIVE = r"C:\Users\bizoi\libriscribe-roman"
A = r"C:\Users\bizoi\roman"
R = [
    ["python", A + r"\scripturi\format_oficial.py"],
    ["python", "-c",
     "import shutil; shutil.copy(r'%s\\manuscript_official_original.md', r'%s\\manuscript_official.md'); print('copied')" % (LIVE, A)],
    ["python3", A + r"\scripturi\make_epub.py"],
]
for cmd in R:
    print(">>", " ".join(cmd)[:100])
    r = subprocess.run(cmd, cwd=LIVE, capture_output=True, text=True)
    print(r.stdout[-600:])
    if r.returncode != 0:
        print("STDERR:", r.stderr[-800:])
        sys.exit(1)
print("BUILD OK")
