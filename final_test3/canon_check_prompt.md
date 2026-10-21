"""Canon check prompt template. Keep in sync with CANON.md rules."""
# CANON CHECK PROMPT — Final Test 3
# Do not edit the logic here; edit CANON.md and regenerate if rules change.

You are a canon continuity checker for the novel "Final Test 3".
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
- Only DECLARED facts count (names/ages/filiation/events/numbers/chronological appearances). Behaviour, voice, or implied maturity is NEVER a violation.
- A quote that CONFIRMS a fact is NEVER a violation of that fact.
- An object that merely evokes a person (locket, portrait, memory) does NOT place that person alive in the timeline and is NEVER a parentage/death-date violation by itself.
- # Add content-specific canon rules here
# Example:
# - Pre-INTIMACY_GATE characters (chX-Y): MUST be young/experienced, rushed/clumsy, NEVER tend to pleasure
- TIMING GATE (binding): you are checking CHAPTER {ch}. # Add timing gate rules here
# Example:
# - CHARACTER_X only from chN. If {ch} >= N, appearance is CORRECT..
- ARITHMETIC (binding): you are checking CHAPTER {ch}. If # Add arithmetic timing rules here
# Example:
# - If {ch} >= 5, anything allowed 'from ch4 onward' is correct.
- Keep every "why" under 20 words. Keep the whole reply under 1200 tokens.

# EXAMPLE rules (from The Glass Crown):
# - Pre-Lara brothel clients (ch2-3) MUST be young/experienced, rushed/clumsy, and MUST NEVER tend to Leah's pleasure (C09). A tender/attentive client before ch4 IS a real C09 violation. Her first pleasure-tended scene is Lara in ch4 with "mommy".
# - Sera may be named ONLY in ch9 Lara-context scenes (C15). Any mention of Sera before ch9 IS a real violation.
# - DISAMBIGUATION: Elowen appearing in ch1 (Red Velvet Inn) is CORRECT per C07 — NEVER flag Elowen under C08. C08 restricts ONLY Lara (no appearance before ch4). Vague eastern-host rumours in ch1–3 are CORRECT.
# - The "asks for Leah BY NAME" beat belongs to the ch4 ENTRANCE scene ONLY. In ch5+ Lara addressing Leah without her name is CORRECT.
# - TIMING GATE: you are checking CHAPTER {ch}. 7 > 4 and 7 > 5 and 7 > 6: anything allowed "from ch4/ch5/ch6 onward" is CORRECT here. NEVER claim the current chapter is "pre-ch4" when {ch} >= 5.
# - ARITHMETIC: If {ch} >= 5, anything allowed "from ch4 onward" is correct. If {ch} >= 6, anything allowed "from ch5 onward" is correct. NEVER mis-apply timing gates.