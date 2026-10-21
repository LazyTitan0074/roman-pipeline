# Agent Handoff Instructions — roman-pipeline

## 🎯 Ce face acest pipeline

**roman-pipeline** este un pipeline automat pentru scrierea și validarea romanelor/novelilor, construit pe **LibriScribe** + **Hermes CLI**. 

**Fluxul principal:**
1. **Concept → Outline → Characters → Worldbuilding → Scenes** (automat, datele în `projects/<name>/`)
2. **Per capitol** (`roman-pipeline chapter <N>`):
   - Sync canon → dynamic questions (injectează fapte din `CANON.md` în writer)
   - Scrie capitolul (re-scrise complete la reject, nu patch-uri)
   - Canon check cu model **diferit** de writer: compară capitolul cu toate faptele din `CANON.md` → `{pass, violations}`
   - Retry până la 4 ori la fail; log în `retry_log.jsonl`
3. **Post-production**: `roman-pipeline build` → manuscript → format → EPUB + cover → verify
4. **Final gate**: PASS verdict **și** human spot-check (reviewer-ii rată ~50% erori)

---

## 🚀 Quick Start (pentru tine, operatorul)

```bash
# 1. Clone & install
git clone https://github.com/LazyTitan0074/roman-pipeline.git
cd roman-pipeline
pip install -e .

# 2. Creează proiect nou
roman-pipeline init my_novel --title "My Novel" --genre Fantasy

# 3. Configurează
cd my_novel
cp .env.example .env
# Editează .env cu cheile API (cel puțin una: GOOGLE_AI_STUDIO_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OPENROUTER_API_KEY)
# Completează: CANON.md, BEAT_SHEET.md, VOICE.md, characters.json, world.json, outline.md

# 4. Rulează capitolul 1
roman-pipeline chapter 1

# 5. La final
roman-pipeline build
roman-pipeline verify
```

---

## 📁 Structura Proiectului

```
roman-pipeline/
├── scripts/          # Core modules (cli, config, canon_checker, build, sync, verify, logs, init_project)
├── templates/        # Fișiere template (CANON.md, BEAT_SHEET.md, VOICE.md, etc.)
├── tests/            # 81 teste (81/81 pass)
├── .github/workflows/ci.yml
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

---

## ⚙️ Configurație Cheie (`.env`)

```bash
# Required paths
BASE_DIR=./workspace              # CANON.md, scripts, logs
PROJ_DIR=./projects/test_final    # LibriScribe project folder

# Writer model (LibriScribe) — recomandat: Nemotron 3 Ultra FREE (1M context)
WRITER_PROVIDER=openrouter
WRITER_MODEL=nvidia/nemotron-3-ultra-550b-a55b:free
WRITER_FALLBACK_CHAIN=google_ai_studio/gemini-2.5-flash, mistral/ministral-8b-latest, mistral/ministral-3b-latest

# Reviewer model (CanonChecker) — must differ from writer!
REVIEWER_PRIMARY=gemini-2.5-flash-lite
REVIEWER_FALLBACK_CHAIN=ollama/qwen2.5:7b,groq/gpt-oss-120b,mistral/ministral-8b-latest

MAX_ATTEMPTS=4
```

**Model writer recomandat**: `nvidia/nemotron-3-ultra-550b-a55b:free` (1M context FREE pe OpenRouter, tool use nativ, reasoning puternic).

---

## 📝 Template-uri de Completat (în proiectul tău)

| Fișier | Scop |
|--------|------|
| `CANON.md` | Fapte canonice: nume, vârste, filiații, evenimente, numere, apariții cronologice. Format: `- C01: LABEL — Description`. Doar fapte **declarate** contează. |
| `BEAT_SHEET.md` | Structură capitole: scene în ordine + canon gates + intimacy level (structural). |
| `VOICE.md` | Stil narativ + voce per personaj (ce spun / nu spun niciodată). |
| `CHAPTER_CHECKLIST.md` | Pre/post-write checklist (grep sweep). |
| `outline.md` | Rezumat carte + detalii capitole. |
| `characters.json` | Personaje (nume, vârstă, descriere, personalitate, background, motivații, relații, arc). |
| `world.json` | Worldbuilding (geografie, cultură, istorie, reguli, magie, locații, organizații, economie, religie). |
| `expert-roman.yaml` | Config LibriScribe (titlu, gen, limbă, capitole, model + fallback chain, workflow). |

---

## 🔴 Reguli Non-Negociabile (învățate greu)

1. **Reviewer ≠ Writer** (altfel ratează aceleași greșeli)
2. **Rejected chapters = re-scris complet**, nu patch-uit
3. **Canon violation = reject**, fără smoothing
4. Doar **fapte declarate** contează (nume/vărste/filiații/evenimente/numere/apariții). Comportament, voce, maturitate implicată = **niciodată** violation.
5. **Name guard**: nu reutiliza nume canonice pentru personaje secundăre/minore
5. **Final human spot-check obligatoriu** (reviewer-i rată ~50%)

---

## 🛠️ Comenzi CLI

```bash
roman-pipeline config              # Afișează config
roman-pipeline init nume --title "Titlu" --genre Fantasy
roman-pipeline chapter 1           # Scrie capitolul 1 cu retry-uri
roman-pipeline chapter 1 --max-attempts 6
roman-pipeline check 1             # Canon check doar
roman-pipeline build               # manuscript + format + EPUB + cover
roman-pipeline build --target manuscript
roman-pipeline sync                # Sync scenes/outline/world → LibriScribe
roman-pipeline verify              # Toate verificările
roman-pipeline verify --check struct
roman-pipeline logs --chapter 1    # Vezi retry/canon logs
```

---

## 🧪 Testare

```bash
pytest tests/ -v          # 81 teste (81/81 pass)
pytest tests/ -v --cov=scripts --cov-report=term-missing
make test                 # Alias pentru pytest
make check                # Lint + test
```

---

## 🐛 Troubleshooting Común

| Problemă | Soluție |
|----------|---------|
| `PROJ_DIR does not exist` | Creează `mkdir -p projects/<name>` și `mkdir workspace` |
| `No reviewer API keys` | Setează cel puțin una: `GOOGLE_AI_STUDIO_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY` |
| `UnicodeDecodeError` pe `.env` | Re-scrie `.env` cu encoding UTF-8 (`echo "KEY=val" > .env`) |
| `SettingsError: writer_fallback_chain` | Verifică `.env` — fallback chains trebuie să fie JSON array sau comma-separated |
| Canon check eșuează la ch7 | Verifică contradicție outline vs BEAT_SHEET (ex: "correction" vs "non-physical") |

---

## 📋 Ce am nevoie de la tine pentru a porni

1. **Chei API** — Cel puțin una din: `GOOGLE_AI_STUDIO_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`, `OPENROUTER_API_KEY`
2. **Conceptul romanului** — Gen, temă, logline, personaje principale
3. **Decizii de design** — POV, tense, limbă de producție (recomandat: English), ton
4. **Timp pentru review** — Final human spot-check la fiecare capitol

---

## 📚 Resurse

- **README.md** — Documentație completă
- **CHANGELOG.md** — Istoric versiuni (v0.2.1 curent)
- **CONTRIBUTING.md** — Ghid contribuție
- **tests/** — 81 teste exemplu pentru validare

---

**Ready to go?** Dacă mi-ai dat cheile API și conceptul, pot să inițializez proiectul și să încep scrierea capitolului 1. 🚀