import shutil
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
SRC = Path(r"C:\Users\bizoi\roman")
DST = Path(r"C:\Users\bizoi\glass-crown-pipeline")
SKIP_FILES = {"reverify.txt", "s3_dump.txt", "tics_dump.txt", "test_scene_or.md",
              ".env", ".libriscribe_status.json", "PROMPT_RELUARE.md"}
if DST.exists():
    shutil.rmtree(DST)
DST.mkdir()
for p in sorted(SRC.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(SRC)
    parts = rel.parts
    if parts[0] == "publish" and p.suffix != ".md":
        continue  # no binaries in repo (rebuild locally)
    if parts[0] == "personaje":
        continue  # RO duplicates of characters.json
    if p.name in SKIP_FILES:
        continue
    dest = DST / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
print("repo files:", sum(1 for _ in DST.rglob("*") if _.is_file()))
