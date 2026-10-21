# CHAPTER CHECKLIST — Final Test 2
# Pre/post-write grep sweep. Run before and after each chapter.

## Pre-Write (before `capitol_runner.py N`)
- [ ] CANON.md updated with any new facts from previous chapters
- [ ] BEAT_SHEET.md reviewed for this chapter's beats
- [ ] VOICE.md character voices fresh in mind
- [ ] Outline.md chapter summary matches beat sheet
- [ ] Previous chapter read for continuity

## Post-Write (after chapter written, before canon check)
- [ ] **Name Guard**: No reserved names reused (search: `grep -i "reserved_name1\|reserved_name2" chapter_N.md`)
- [ ] **Staging Gates**: No characters appear before their canon introduction chapter
- [ ] **Ages**: All stated ages match CANON.md exactly
- [ ] **Intimacy Rules**: 
  - [ ] Consenting adults only
  - [ ] Pre-{{INTIMACY_GATE_CHARACTER}} rules followed
  - [ ] No fade-to-black violations
- [ ] **POV**: Strict 3rd limited on {{PROTAGONIST}}, no head-hopping
- [ ] **Tense**: Past tense throughout
- [ ] **Formatting**: Markdown, scene breaks with `---`, scene headings `### Scene N`
- [ ] **Length**: Target {{TARGET_WORDS}} words ({{MIN_WORDS}}–{{MAX_WORDS}})

## Canon Check Specific (what reviewer will flag)
- [ ] No contradictions of C## facts
- [ ] No anachronistic appearances (e.g., {{LATE_CHARACTER}} before ch{{LATE_CHARACTER_CHAPTER}})
- [ ] No implied knowledge before reveal chapters
- [ ] Numbers match exactly (ages, dates, counts)

## Quick Grep Commands
```bash
# Check for forbidden names
grep -i "forbidden1\|forbidden2" chapter_N.md

# Check for staging violations
grep -i "late_character" chapter_N.md

# Check age mentions
grep -E "\b(1[0-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|7[0-9]|8[0-9]|9[0-9])\b" chapter_N.md

# Check POV slips (other character's thoughts)
grep -i "she knew\|he knew\|she felt\|he felt\|she thought\|he thought" chapter_N.md
```

# EXAMPLE (The Glass Crown):
# Pre-Write: Check CANON.md C01-C19, BEAT_SHEET Ch1-Ch10, VOICE.md
# Post-Write:
# - Name Guard: search `Mirela|Lara|Leah|Cassian|Varnholt|Elowen|Elara|Mira|Vela|Sera`
# - Staging: Lara before ch4, Mira/Vela before ch5, Sera before ch9
# - Intimacy: Pre-Lara clients (ch2-3) = young/rushed/no pleasure-tending
# - POV: Leah-only, past tense
# - Length: 4500-5500 words