import json
from pathlib import Path
P = Path(r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara")
A = Path(r"C:\Users\bizoi\roman")
d = json.load(open(P / "project_data.json", encoding="utf-8"))

# 1. scenes -> embedded chapters (keep chapter titles/summaries, replace scene lists)
disk = json.loads((A / "scenes.json").read_text(encoding="utf-8"))
for ch, scenes in disk.items():
    if ch in d.get("chapters", {}):
        d["chapters"][ch]["scenes"] = [
            {"scene_number": s["scene_number"], "summary": s["summary"],
             "characters": s.get("characters", []), "setting": s.get("setting", ""),
             "goal": s.get("goal", ""), "emotional_beat": s.get("emotional_beat", "")}
            for s in scenes
        ]
print("scenes synced:", {k: len(v["scenes"]) for k, v in d["chapters"].items()})

# 2. outline.md -> outline str
d["outline"] = (A / "outline.md").read_text(encoding="utf-8")

# 3. world.json -> worldbuilding dict
w = json.loads((A / "world.json").read_text(encoding="utf-8"))["worldbuilding"]
d["worldbuilding"] = w

json.dump(d, open(P / "project_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("outline + worldbuilding synced")
