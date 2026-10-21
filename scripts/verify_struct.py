import re, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara\chapter_%d.md"
C = {n: open(P % n, encoding="utf-8").read() for n in range(1, 11)}
print("million:", [(n, len(re.findall(r"\bmillion\b", C[n], re.I))) for n in range(1, 11)])
print("Elowen ch6:", len(re.findall(r"Elowen", C[6])))
print("not-ready ch7:", len(re.findall(r"not ready", C[7], re.I)))
print("Sera:", [(n, len(re.findall(r"\bSera\b", C[n]))) for n in range(1, 11)])
print("oysters/mother-goddess ch5-7:", [(n, len(re.findall(r"Mother of Two Faces|Azara|Vohra", C[n]))) for n in (5, 6, 7)])
# Lara dialogue: lines starting with *"
lara = []
for n in range(1, 11):
    for m in re.finditer(r"\*\"([^*]{1,150})\"", C[n]):
        lara.append((n, m.group(1)))
print("lara-quote-lines:", len(lara))
short = [l for l in lara if len(l[1].split()) <= 6]
print("short(<=6w):", len(short), "pct:", round(100 * len(short) / max(1, len(lara))))
