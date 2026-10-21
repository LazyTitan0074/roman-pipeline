import re, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara\chapter_%d.md"
A = r"C:\Users\bizoi\roman\chapter_%d.md"
ok = True

# 1. surse PROJ vs arhiva (identice?)
for n in range(1, 11):
    a = open(P % n, encoding="utf-8").read()
    b = open(A % n, encoding="utf-8").read()
    same = (a == b)
    ok &= same
    print("ch%d proj==archive: %s (%d words)" % (n, same, len(a.split())))

# 2. markeri de repair in manuscris
ms = open(r"C:\Users\bizoi\roman\manuscript_official.md", encoding="utf-8").read()
marks = ["Eight years ago", "two taps, then nothing", "cold stone and black tea",
         "Enjoy the cage, little queen", "Eleven crowns, three doors",
         " rock crystal,", "keeper of the glass crown",
         "By the second evening she had learned", "She brought the strip down at first light",
         "Vestalia isn", "single face split by a vertical line"]
for m in marks:
    hit = m in ms
    ok &= hit
    print(("OK  " if hit else "MISS") + " manuscript: " + m[:50])

# 3. EPUB == manuscris (text, fara formatare)
z = zipfile.ZipFile(r"C:\Users\bizoi\roman\publish\The_Glass_Crown.epub")
ep = ""
for i in range(1, 11):
    ep += z.read("OEBPS/ch%02d.xhtml" % i).decode("utf-8")
def norm(t):
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&quot;", '"').replace("&#x27;", "'").replace("&amp;", "&")
    t = re.sub(r"\s+", " ", t)
    return t
epn, msn = norm(ep), norm(ms)
missing = 0
for n in range(1, 11):
    src = norm(open(P % n, encoding="utf-8").read())
    # scene headings sunt stripuite in epub; restul trebuie sa existe bucati
    paras = [p.strip() for p in re.split(r"\n\s*\n", open(P % n, encoding="utf-8").read()) if len(p.strip()) > 120 and not re.match(r"^#{0,4}\s*\*{0,2}Scene \d+", p.strip())]
    bad = [p for p in paras[:200] if norm(p)[:80] not in epn]
    if bad:
        ok = False
        print("EPUB MISS ch%d: %d paras (ex: %s)" % (n, len(bad), bad[0][:80]))
print("epub-size:", len(epn), "ms-size:", len(msn))
print("ALL OK" if ok else "PROBLEMS FOUND")
