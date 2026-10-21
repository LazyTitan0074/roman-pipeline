import json
P = r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara\project_data.json"
A = r"C:\Users\bizoi\roman\characters.json"
d = json.load(open(P, encoding="utf-8"))
arch = json.load(open(A, encoding="utf-8"))["characters"]
d["characters"] = {c["name"]: c for c in arch}
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("embedded roster:", sorted(d["characters"].keys()))
