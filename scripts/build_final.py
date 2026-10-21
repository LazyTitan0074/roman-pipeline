import re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
P = Path(r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara")
TITLES = {1: "Cinderella", 2: "The Lower City", 3: "Two Days", 4: "Madam Lara",
          5: "The Offer", 6: "The Lie", 7: "The Negotiation", 8: "The Conquest",
          9: "The Glass Crown", 10: "The Choice"}
parts = ["# The Glass Crown\n",
         "_Leah Estia, disinherited princess of Valdris, flees a forced marriage and finds refuge with Lara, Queen of Vestalia — who offers her the throne for vassalage._\n",
         "_A novel in ten chapters._\n"]
total = 0
for n in range(1, 11):
    t = (P / ("chapter_%d.md" % n)).read_text(encoding="utf-8").strip()
    # normalize opening heading to ## Chapter N: Title
    t = re.sub(r"^#{1,4}\s*\*?\*?Chapter\s+\d+[^*\n]*\*?\*?", "## Chapter %d: %s" % (n, TITLES[n]), t, count=1, flags=re.I)
    assert t.startswith("## Chapter %d:" % n), "heading nolock ch%d: %s" % (n, t[:80])
    total += len(t.split())
    parts.append("\n\n---\n\n" + t)
ms = "\n".join(parts) + "\n"
(P / "manuscript_final.md").write_text(ms, encoding="utf-8")
Path(r"C:\Users\bizoi\roman\manuscript_final.md").write_text(ms, encoding="utf-8")
print("manuscript_final: chapters 1-10 in order,", total, "words")
