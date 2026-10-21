import sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
P = Path(r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara")
parts = ["# The Glass Crown\n\n_A novel in ten chapters._\n"]
total = 0
for n in range(1, 11):
    t = (P / ("chapter_%d.md" % n)).read_text(encoding="utf-8").strip()
    total += len(t.split())
    parts.append("\n\n---\n\n" + t)
ms = "\n".join(parts) + "\n"
(P / "manuscript.md").write_text(ms, encoding="utf-8")
Path(r"C:\Users\bizoi\roman\manuscript.md").write_text(ms, encoding="utf-8")
print("manuscript: 10/10 chapters,", total, "words")
