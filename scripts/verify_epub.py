import re, sys, zipfile, html as H
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara\chapter_%d.md"
z = zipfile.ZipFile(r"C:\Users\bizoi\roman\publish\The_Glass_Crown.epub")
ep = ""
for i in range(1, 11):
    ep += z.read("OEBPS/ch%02d.xhtml" % i).decode("utf-8")

def norm(t, is_html):
    if is_html:
        t = re.sub(r"<[^>]+>", "", t)
        t = H.unescape(t)
    t = t.replace("\u201c", '"').replace("\u201d", '"').replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u2014", "-").replace("\u2013", "-")
    t = re.sub(r"\*+", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

epn = norm(ep, True)
ok = True
for n in range(1, 11):
    src = open(P % n, encoding="utf-8").read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", src)
             if len(p.strip()) > 120 and not re.match(r"^#{0,4}\s*\*{0,2}Scene \d+", p.strip())]
    bad = []
    for p in paras:
        key = norm(p, False)
        if key[:100] not in epn and key[-100:] not in epn and key not in epn:
            bad.append(p)
    print("ch%d: %d/%d paras in epub%s" % (n, len(paras) - len(bad), len(paras), "" if not bad else " MISS: " + bad[0][:100]))
    ok &= (not bad)
print("ALL OK" if ok else "PROBLEMS FOUND")
