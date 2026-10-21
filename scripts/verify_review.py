import re, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara\chapter_%d.md"
ch = {n: open(P % n, encoding="utf-8").read() for n in range(1, 11)}

def find(n, pat, ctx=120):
    t = ch[n]
    out = []
    for m in re.finditer(pat, t, re.I | re.S):
        out.append(t[max(0, m.start()-ctx):m.end()+ctx].replace("\n", " | "))
    return out

def rep(tag, desc, hits):
    print(("CONFIRMED " if hits else "STALE/FALSE ") + tag + " :: " + desc + ("  [%d]" % len(hits) if hits else ""))
    for h in hits[:2]:
        print("   > " + h[:260])

print("===== BLOCKERS =====")
rep("B1", "Twelve years ago ch5 + twelve global", find(5, r"twelve years ago") + [("ch%d: "%n + x) for n in range(1, 11) for x in find(n, r"\btwelve\b")])
rep("B2", "Mother with two faces ch3", find(3, r"mother with two faces|one that warms"))
rep("B3a", "in Vestalian (language) ch8", find(8, r"in vestalian"))
rep("B3b", "heir of the flame ch8", find(8, r"heir of the flame"))
rep("B4", "Elowen interiority para ch4s1", find(4, r"two nights past|debt she would collect"))
rep("B5", "essay 'changes began' ch9", find(9, r"changes began with the smallest"))
print("===== MAJOR =====")
rep("M1a", "archives ch6", find(6, r"archives"))
rep("M1b", "supreme mother sends regards ch6", find(6, r"sends her regards"))
rep("M2a", "two flames crimson gold ch5", find(5, r"two flames"))
rep("M2b", "two-faced sigil ch7", find(7, r"two-faced sigil"))
rep("M2c", "double-faced goddess ch9", find(9, r"double-faced goddess"))
rep("M3a", "last jewel ch8", find(8, r"last jewel"))
rep("M3b", "understood later ch8", find(8, r"understood later"))
rep("M4a", "diadem on table ch9", find(9, r"diadem resting on the table|diadem.{0,40}table"))
rep("M4b", "weight crown pressing ch9", find(9, r"weight of the crown pressing"))
rep("M5", "Corrects Her First Time title ch7", find(7, r"corrects her for the first time"))
rep("M6", "drop it into brazier ch10", find(10, r"drop it into the brazier"))
print("===== MINOR =====")
rep("m2", "groaned open x2 ch4", find(4, r"groaned open"))
rep("m3a", "burnt sugar ch6", find(6, r"burnt sugar"))
rep("m3b", "burnt sugar ch7", find(7, r"burnt sugar"))
rep("m4a", "too bright ch8", find(8, r"too bright"))
rep("m5a", "dying man breath ch6", find(6, r"dying man.s breath"))
rep("m5b", "unsheathed and then sheathed ch7", find(7, r"unsheathed and then sheathed"))
rep("m5c", "sickly, sickly ch8", find(8, r"sickly, sickly"))
rep("m7", "ill-fitting parens ch8", find(8, r"clearly ill-fitting"))
rep("m8a", "written in haste ch5", find(5, r"written in haste"))
rep("m8b", "precise measured handwriting", [("ch%d: " % n + x) for n in range(1, 11) for x in find(n, r"precise, measured")])
rep("m9", "colour/rumour/neighbour", [("ch%d: " % n + x) for n in range(1, 11) for x in find(n, r"\b(colour|rumour|neighbour|favour|honour)\b")])
rep("m10", "running from a wedding ch10", find(10, r"from a wedding"))
rep("m11", "shutters ch8", find(8, r"shutters"))
rep("Halvard", "lord halvard ch3", find(3, r"halvard"))
print("===== KEYWORDS =====")
for kw in ["sandalwood", "amber", "weight of", "air smelled of", "choose", "decide"]:
    tot = sum(len(re.findall(kw, ch[n], re.I)) for n in range(1, 11))
    print("%s -> %d" % (kw, tot))
print("===== BEATS =====")
rep("smile-crack", "smile not reaching ch8", find(8, r"did not reach her eyes|didn.t reach"))
rep("cass-human", "cassian hope/stays ch8", find(8, r"\bhope\b|He stays"))
rep("tally", "tally ch9", find(9, r"\btally\b|escape routes|guards at the door"))
rep("mirror", "mirror/facets ch10", find(10, r"\bmirror\b|facets"))
rep("epilogue", "ship sails dawn ch10", find(10, r"sails at dawn|shadow on the water"))
print("===== NAME-GUARD =====")
for nm, allowed in [("Mira", [5, 6, 7, 8, 9, 10]), ("Vela", [5, 6, 7, 8, 9, 10]), ("Sera", [9])]:
    bad = []
    for n in range(1, 11):
        if n not in allowed:
            for x in find(n, r"\b" + nm + r"\b"):
                bad.append("ch%d: %s" % (n, x))
    rep("guard-" + nm, nm + " outside allowed", bad)
print("===== SCENES =====")
for n in range(1, 11):
    k = len(re.findall(r"(?m)^#{1,4} .*Scene \d+", ch[n]))
    print("ch%d scenes: %d" % (n, k))
