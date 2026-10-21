"""Canon check pe lista de fapte (NU pe 'citeste biblia').
Reviewer = model DIFERIT de writer. Primar: gemini-2.5-flash-lite. Fallback: modelul
ne-folosit-la-scriere dintre {gpt-oss-120b (Groq), ministral-8b}.
Orice abatere => respins, fara netezire. Uz: python canon_check.py <nr_cap> [writer_model]
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(os.getenv("BASE_DIR", r"C:\Users\bizoi\Desktop\roman-pipeline\my_novel"))
PROJ = Path(os.getenv("PROJ_DIR", r"C:\Users\bizoi\AppData\Roaming\Python\Python315\projects\my_novel"))
load_dotenv(BASE / ".env")

PROMPT = """You are a canon continuity checker for the novel "The Golden Cage".
AUTHORITATIVE STORY FACTS (any contradiction = fail):
{facts}

CHAPTER {ch} TEXT:
{text}

Compare EVERY factual claim about named people, ages, relationships, parentage, past events,
who-killed-whom, world rules, numbers, and timeline (who appears when).
Return ONLY this JSON, nothing else:
{{"pass": true/false, "violations": [{{"fact": "C##", "quote": "<exact chapter quote>", "why": "<what it contradicts>"}}]}}
Rules: a single contradiction (names, ages, parentage, events, anachronistic appearance) => pass=false. Prose quality is NOT your job. Do not smooth over contradictions. Empty violations + pass=true only if fully clean.
ANTI-FALSE-POSITIVE RULES (binding, take precedence):
- Only DECLARED facts count (names/ages/filiation/events/numbers/chronological appearances). Behaviour, voice, or implied maturity is NEVER a violation (e.g. Yuna seeming young/frightened does NOT contradict C01 age 23).
- A quote that CONFIRMS a fact (e.g. naming Lara as the Fixer) is NEVER a violation of that fact.
- An object that merely evokes a person (harness, ring, memory) does NOT place that person alive in the timeline and is NEVER a parentage/death-date violation by itself.
- Pre-regression Yuna (ch1-3) is arrogant, predatory, dominant. Post-regression (ch7+) she is helpless, dependent, Little. A dominant/confident Yuna in ch8+ IS a real C09 violation.
- The Mother (C03) appears ONLY in ch7+. Any mention/appearance before ch7 IS a violation.
- The Harness (C01) is revealed in ch4. Any mention before ch4 IS a violation.
- The wooden hairbrush punishment (C06) happens in ch5. Any mention before ch5 IS a violation.
- TIMING GATE (binding): you are checking CHAPTER {ch}. 7 > 4 and 7 > 5 and 7 > 6: anything allowed "from ch4/ch5/ch6 onward" is CORRECT here. NEVER claim the current chapter is "pre-ch4" or "pre-ch5" when {ch} >= 5.
- Keep every "why" under 20 words. Keep the whole reply under 1200 tokens."""


def check_flash_lite(prompt):
    from google import genai
    c = genai.Client(api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"))
    r = c.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    return (r.text or "").strip(), "gemini-2.5-flash-lite"


def check_groq(prompt):
    import requests
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"},
        json={"model": "openai/gpt-oss-120b",
              "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 2500, "temperature": 0.1},
        timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip(), "groq/gpt-oss-120b"


def check_ollama(prompt):
    import requests
    r = requests.post(
        "http://localhost:11434/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json={"model": "qwen2.5:7b",
              "messages": [{"role": "user", "content": prompt}],
              "options": {"num_predict": 2500},
              "temperature": 0.1},
        timeout=300)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip(), "ollama/qwen2.5:7b"


def check_ministral(prompt):
    import requests
    r = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.getenv('MISTRAL_API_KEY')}"},
        json={"model": "ministral-8b-latest",
              "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 2500, "temperature": 0.1},
        timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip(), "mistral/ministral-8b-latest"


def is_hedge(why):
    if re.search(r'no violation|not a violation|no pre-ch\d violation|is correct|no issue|correct per|no contradiction|confirmed post-ch\d|allowed|permitted|as required|as expected', why, re.I):
        return True
    if not re.search(r'violat|contradict|break|inconsist|impli|wrong|stated as|aged \d|instead of', why, re.I):
        return True
    return False


def parse_verdict(raw):
    try:
        return json.loads(raw)
    except Exception:
        pass
    s = raw.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        if s.rstrip().endswith("```"):
            s = s.rstrip()[: -3]
    try:
        return json.loads(s)
    except Exception:
        pass
    s2, e = s.find("{"), s.rfind("}")
    if s2 >= 0 and e > s2:
        try:
            return json.loads(s[s2:e + 1])
        except Exception:
            pass
    objs = re.findall(r'\{[^{}]*"fact"\s*:\s*"([^"]+)"[^{}]*\}', s)
    if objs:
        out = []
        for m in re.finditer(r'\{\s*"fact"\s*:\s*"([^"]+)"\s*,\s*"quote"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"why"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}', s):
            why = m.group(3)
            if re.search(r'no violation|not a violation|no pre-ch\d violation|is correct|no issue|correct per|no contradiction|confirmed post-ch\d|allowed|permitted|as required|as expected', why, re.I):
                continue
            if not re.search(r'violat|contradict|break|inconsist|impli|wrong|stated as|aged \d|instead of', why, re.I):
                continue
            out.append({"fact": m.group(1), "quote": m.group(2)[:200], "why": why[:200]})
        if out:
            return {"pass": False, "violations": out[:10]}
        return {"pass": True, "violations": []}
    if re.search(r'"pass"\s*:\s*true', s):
        return {"pass": True, "violations": []}
    return {"pass": False, "violations": [{"fact": "PARSE", "quote": raw[:200], "why": "unparseable verdict"}]}


def main():
    ch = sys.argv[1]
    writer = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    facts = (BASE / "CANON.md").read_text(encoding="utf-8")
    text = (PROJ / f"chapter_{ch}.md").read_text(encoding="utf-8")
    prompt = PROMPT.format(facts=facts, ch=ch, text=text)

    raw, reviewer = None, None
    # Reviewer must differ from writer. Primary: Flash-Lite, then FREE local
    # Ollama (unlimited, private), then Groq/ministral. Last resort: ministral
    # (same-model review is weak; the human spot-check remains the real gate).
    order = [check_flash_lite, check_ollama]
    if "120b" in writer or "groq" in writer:
        order.append(check_ministral)
    else:
        order.append(check_groq)
    order.append(check_ministral if order[-1] is check_groq else check_groq)
    err = None
    for fn in order:
        try:
            raw, reviewer = fn(prompt)
            break
        except Exception as e:
            err = f"{fn.__name__}: {str(e)[:150]}"
    if raw is None:
        verdict = {"pass": False, "violations": [{"fact": "REVIEWER-DOWN", "quote": "", "why": err or "all reviewers failed"}]}
        reviewer = "none"
    else:
        verdict = parse_verdict(raw)
        # Filter hedged non-findings on EVERY path (small reviewers list facts
        # just to conclude they are fine — those are not violations).
        kept = [v for v in verdict.get("violations", []) if not is_hedge(str(v.get("why", "")))]
        verdict = {"pass": len(kept) == 0, "violations": kept}

    result = {"chapter": int(ch), "writer": writer, "reviewer": reviewer,
              "pass": bool(verdict.get("pass")), "violations": verdict.get("violations", []),
              "at": datetime.now(timezone.utc).isoformat()}
    (BASE / f"canon_verdict_ch{ch}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(BASE / "canon_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    # registry update
    regp = BASE / "canon_registry.json"
    if regp.exists():
        reg = json.loads(regp.read_text(encoding="utf-8"))
    else:
        reg = {"chapters": {}}
    reg["chapters"][str(ch)] = {"status": "pass" if result["pass"] else "FAIL",
                                "reviewer": reviewer,
                                "violations": len(result["violations"])}
    regp.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"chapter={ch} writer={writer} reviewer={reviewer} "
          f"verdict={'PASS' if result['pass'] else 'FAIL'} violations={len(result['violations'])}")
    for v in result["violations"][:10]:
        print(f" - [{v.get('fact')}] {str(v.get('why'))[:160]}")


if __name__ == "__main__":
    main()