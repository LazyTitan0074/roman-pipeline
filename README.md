# Novel Production Pipeline

[![CI](https://github.com/LazyTitan0074/roman-pipeline/workflows/CI/badge.svg)](https://github.com/LazyTitan0074/roman-pipeline/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-81%2F81%20pass-brightgreen)](https://github.com/LazyTitan0074/roman-pipeline/actions)
[![Version](https://img.shields.io/badge/version-0.2.1-blue)](https://github.com/LazyTitan0074/roman-pipeline/releases)

---

A reusable, AI-driven pipeline for writing and verifying novels/novellas.
Originally built for *The Glass Crown* (10-chapter dark political fantasy).

> **Vibe coded.** This pipeline was assembled iteratively with an AI coding assistant (Hermes Agent). Expect rough edges; treat it as a starting point, not a polished framework.

---

## 🎯 What It Does

| Phase | Description |
|-------|-------------|
| **1. Initial** (LibriScribe, auto) | concept → outline → characters → worldbuilding → scenes |
| **2. Per-chapter** (`roman-pipeline chapter <N>`) | Sync canon → write → canon check (different model) → retry up to 4× |
| **3. Post-production** (`roman-pipeline build`) | Assemble → format → EPUB + cover → verify |
| **4. Final gate** | PASS verdict **and** human spot-check (reviewers miss ~50%) |

### Key Principles
- 🔄 **Rewrites, not patches** — rejected chapters are fully rewritten
- 🚫 **Reviewer ≠ Writer** — different models catch different errors
- ⚖️ **Canon violation = reject** — no smoothing, only declared facts count
- 👁️ **Human spot-check mandatory** — reviewers miss ~50% of issues

---

## 🚀 Quick Start

```bash
# 1. Clone & install
git clone https://github.com/LazyTitan0074/roman-pipeline.git
cd roman-pipeline
pip install -e .

# 2. Create a new project
roman-pipeline init my_novel --title "My Novel" --genre Fantasy

# 3. Configure
cd my_novel
cp .env.example .env
# Edit .env with your API keys (at least one reviewer key required)
# Fill in: CANON.md, BEAT_SHEET.md, VOICE.md, characters.json, world.json, outline.md

# 4. Write chapters
roman-pipeline chapter 1
roman-pipeline chapter 2
# ...

# 5. Build final outputs
roman-pipeline build    # manuscript + format + EPUB + cover
roman-pipeline verify   # all verification checks
```

---

## 🎨 Unified CLI

```bash
roman-pipeline config              # Show current configuration
roman-pipeline init my_novel --title "My Novel" --genre Fantasy
roman-pipeline chapter 1           # Write chapter 1 with auto-retry
roman-pipeline chapter 1 --max-attempts 6
roman-pipeline check 1             # Canon check only
roman-pipeline build               # All: manuscript, format, EPUB, cover
roman-pipeline sync                # Sync scenes/outline/world → LibriScribe
roman-pipeline verify              # All checks (struct, build, epub, review)
roman-pipeline logs --chapter 1    # View retry/canon logs
```

---

## ⚙️ Configuration (`.env`)

```bash
# Required paths
BASE_DIR=./workspace                    # Working folder (CANON.md, logs, scripts)
PROJ_DIR=./projects/my_novel            # LibriScribe project folder
PROJECT_NAME=my_novel
NUM_CHAPTERS=10

# Reviewer API keys (at least ONE required)
GOOGLE_AI_STUDIO_API_KEY=
GROQ_API_KEY=
MISTRAL_API_KEY=
OPENROUTER_API_KEY=

# Writer model (LibriScribe) — recommended: Nemotron 3 Ultra FREE (1M context)
WRITER_PROVIDER=openrouter
WRITER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
WRITER_FALLBACK_CHAIN=google_ai_studio/gemini-2.5-flash, mistral/ministral-8b-latest, mistral/ministral-3b-latest

# Reviewer model (CanonChecker) — must differ from writer!
REVIEWER_PRIMARY=gemini-2.5-flash-lite
REVIEWER_FALLBACK_CHAIN=ollama/qwen2.5:7b,groq/gpt-oss-120b,mistral/ministral-8b-latest

MAX_ATTEMPTS=4
```

### 🏆 Recommended Free Writer Model
| Model | Context | Cost | Notes |
|-------|---------|------|-------|
| **Nemotron 3 Ultra FREE** | **1M** | **FREE** | Best overall: 1M context, tool use, reasoning |
| Nemotron 3 Super FREE | ~256K | FREE | Good fallback |
| MiniMax M3 FREE | 1M | FREE | Multimodal, check availability |

---

## 📁 Project Templates (fill these in)

| File | Purpose |
|------|---------|
| `CANON.md` | Canonical facts: names, ages, parentage, events, numbers, appearances. Format: `- C01: LABEL — Description`. Only **declared** facts count. |
| `BEAT_SHEET.md` | Chapter structure: scenes in order + canon gates + intimacy level. |
| `VOICE.md` | Narration style + per-character voice (what they say / never say). |
| `CHAPTER_CHECKLIST.md` | Pre/post-write checklist (grep sweep). |
| `outline.md` | Book summary + chapter details. |
| `characters.json` | Characters (name, age, description, personality, background, motivations, relations, arc). |
| `world.json` | Worldbuilding (geography, culture, history, rules, magic, locations, orgs, economy, religion). |
| `expert-roman.yaml` | LibriScribe config (title, genre, language, chapters, model + fallback chain, workflow). |
| `editor.yml` | Editor template (voice rules, name guard, safety rules). |
| `.env` | API keys and runtime config. |

---

## 🔴 Non-Negotiable Rules (learned the hard way)

1. **Reviewer ≠ Writer** — otherwise it misses the same mistakes
2. **Rejected chapters are rewritten**, not patched
3. **Canon violation = reject**, no smoothing
4. Only **declared** facts count (names/ages/parentage/events/numbers/appearances). Behavior, voice, or implied maturity is **never** a violation.
5. **Name guard**: never reuse canonical names for secondary/minor characters
6. **Final human spot-check is mandatory** (reviewers miss ~50%)

---

## 🧪 Testing

```bash
# All tests (81 passing)
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=scripts --cov-report=term-missing

# Linting
ruff check scripts/ tests/
ruff format scripts/ tests/

# Quick test
make test
```

---

## 🔧 Makefile Shortcuts

```bash
make test          # Run all tests
make lint          # Ruff lint
make format        # Auto-format
make check         # Lint + test
make build         # Build wheel/sdist
make clean         # Clean build artifacts
make dev-setup     # Full dev setup (install + pre-commit)
make demo          # Create demo project
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `PROJ_DIR does not exist` | `mkdir -p projects/<name> && mkdir workspace` |
| `No reviewer API keys` | Set at least one: `GOOGLE_AI_STUDIO_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY` |
| `UnicodeDecodeError` on `.env` | Re-save `.env` as UTF-8: `echo "KEY=val" > .env` |
| `SettingsError: writer_fallback_chain` | Use JSON array or comma-separated in `.env` |
| `ch7 discipline contradiction` | Align `outline.md` and `BEAT_SHEET.md` (see `CANON.md C13`) |

---

## 📜 License

MIT. Vibe coded — use at your own risk.

---

## 🙏 Acknowledgments

- Built with [LibriScribe](https://github.com/LazyTitan0074/LibriScribe) + [Hermes CLI](https://github.com/nesquena/hermes-webui)
- Models: Nemotron (NVIDIA), Gemini (Google), Ministral (Mistral), Groq, Ollama
- Inspired by the writing workflow for *The Glass Crown*