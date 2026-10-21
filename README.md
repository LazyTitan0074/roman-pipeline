# Novel Production Pipeline

A reusable, AI-driven pipeline for writing and verifying novels/novellas.
Originally built for *The Glass Crown* (10-chapter dark political fantasy).

> **Vibe coded.** This pipeline was assembled iteratively with an AI coding
> assistant (Hermes Agent). Expect rough edges; treat it as a starting point,
> not a polished framework.

## What it does

1. **Initial phase (LibriScribe, auto):** concept → outline → characters →
   worldbuilding → scenes. Data lives in `projects/<name>/`.
2. **Per-chapter production** (`capitol_runner.py <N>`):
   - Sync canon → dynamic questions (injects `CANON.md` facts into the writer).
   - Deletes any existing chapter (rejected chapters are **rewritten**, not patched).
   - Writes + internally reviews the chapter (model from `expert-roman.yaml`,
     with fallback chain).
   - Canon check by a **different** model than the writer: compares the chapter
     against every fact in `CANON.md`, returns `{pass, violations}`.
   - Retries up to 4 times on failure; logs to `retry_log.jsonl`.
3. **Post-production:** assemble manuscript → format → EPUB + cover → verify.
4. **Final gate:** PASS verdict **and** human spot-check (reviewers miss ~50%).

## Layout

```
roman-pipeline/
├── scripts/        # production scripts (runner, canon check, build, verify, epub)
├── templates/      # file templates (canon, beat sheet, voice, checklist, outline,
│                   # characters, world, .env, LibriScribe config)
└── README.md
```

## What the agent needs from you (input files)

For a new project, fill in / provide:

| File | Purpose |
|---|---|
| `templates/CANON.md` | Canonical facts: names, ages, parentage, events, numbers, chronological appearances. Format: `- C01: ...`. Only **declared** facts count. |
| `templates/BEAT_SHEET.md` | Chapter structure: scenes in order + canon gates + intimacy level (structural only). |
| `templates/VOICE.md` | Narration style + per-character voice (what they say / never say). |
| `templates/CHAPTER_CHECKLIST.md` | Pre/post-write checklist (grep sweep). |
| `templates/outline.md` | Book summary + chapter details. |
| `templates/characters.json` | Characters (name, age, description, personality, background, motivations, relations, arc). |
| `templates/world.json` | Worldbuilding (geography, culture, history, rules, magic, locations, orgs, economy, religion). |
| `templates/expert-roman.yaml` | LibriScribe config (title, genre, language, chapters, model + fallback chain, workflow). |
| `templates/editor.yml` | Editor template (voice rules, name guard, safety rules). |
| `templates/.env.example` | API keys (OpenRouter, Google AI Studio, Mistral, Groq/Bedrock). Copy to `.env`. |

## Main scripts

- `capitol_runner.py <N>` — run production of one chapter (sync + write + check + retry).
- `canon_check.py <N> [writer_model]` — verify a chapter against `CANON.md`.
- `build_manuscript.py`, `format_oficial.py` — assemble + format.
- `build_all.py`, `build_final.py`, `assemble_repo.py` — aggregate builds.
- `sync_all.py`, `sync_chars.py` — syncs.
- `verify_build.py`, `verify_struct.py`, `verify_epub.py`, `verify_review.py` — verifications.
- `make_epub.py`, `make_cover.py` — EPUB + cover.

## Configuration

Scripts have hardcoded paths (`BASE` / `PROJ`). For a new project, edit in
`capitol_runner.py` and `canon_check.py`:

- `BASE` = working folder (where `CANON.md`, scripts, logs live).
- `PROJ` = LibriScribe project folder (`projects/<name>/`).

## Non-negotiable rules (learned the hard way)

- Reviewer **must differ** from writer (otherwise it misses the same mistakes).
- Rejected chapters are **rewritten**, not patched.
- Canon violation = reject, no smoothing.
- Only **declared** facts count (names/ages/parentage/events/numbers/appearances).
  Behavior, voice, or implied maturity is **never** a violation.
- Name guard: never reuse canonical names for secondary/minor characters.
- Final human spot-check is mandatory (reviewers miss ~50%).

## Notes

- Free models have quotas (OpenRouter ~50/day, Gemini ~20/day). Ministral and
  Groq were widely open. Check quotas before running.
- Recommended production language: English (free models write clean English).
  Translate to Romanian at the end with Gemini.

## License

MIT. Vibe coded — use at your own risk.
