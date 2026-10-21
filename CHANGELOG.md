# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **parse_verdict()**: Eliminated dangerous heuristic that accepted truncated JSON with `"pass": true` as PASS. Now requires full JSON parse with empty violations array.
- **ch7 discipline validation**: Now a BLOCKER (exit code 1) with prominent formatting, not just a warning. Detects outline/BEAT_SHEET contradictions (e.g., "correction" vs "non-physical") and references CANON.md C13.
- **Physical keyword matching**: Fixed false positive on "non-physical" by using word-boundary-aware matching for "physical".

### Added
- **Test**: `test_parse_verdict_truncated_after_pass_true` ensures truncated JSON with violations never returns PASS.

## [v0.2.1] - 2026-10-21

### Fixed
- **parse_verdict()**: Eliminated dangerous heuristic that accepted truncated JSON with `"pass": true` as PASS. Now requires full JSON parse with empty violations array.
- **ch7 discipline validation**: Now a BLOCKER (exit code 1) with prominent formatting, not just a warning. Detects outline/BEAT_SHEET contradictions (e.g., "correction" vs "non-physical") and references CANON.md C13.
- **Physical keyword matching**: Fixed false positive on "non-physical" by using word-boundary-aware matching for "physical".

### Added
- **Test**: `test_parse_verdict_truncated_after_pass_true` ensures truncated JSON with violations never returns PASS.

## [v0.2.0] - 2026-10-21

### Added
- **Unified CLI** (`roman-pipeline` command) with 8 subcommands:
  - `config` - Show current configuration
  - `init` - Create new project from templates
  - `chapter` - Run chapter production with retries
  - `check` - Run canon check on existing chapter
  - `build` - Build manuscript, format, EPUB, cover
  - `sync` - Sync project data (scenes, outline, worldbuilding)
  - `verify` - Run verification checks (struct, build, epub, review)
  - `logs` - View retry/canon logs
- **Centralized Configuration** (`scripts/config.py`):
  - Pydantic Settings with `.env` support
  - All paths, models, fallbacks, API keys in one place
  - Zero hardcoded paths or project names
- **Project Templates** with full placeholder support:
  - `CANON.md`, `BEAT_SHEET.md`, `VOICE.md`, `CHAPTER_CHECKLIST.md`
  - `outline.md`, `characters.json`, `world.json`
  - `expert-roman.yaml`, `editor.yml`, `.env.example`
  - Auto-rendered on `roman-pipeline init`
- **Canon Checker v2**:
  - Reviewer fallback chain from config (respects `REVIEWER_FALLBACK_CHAIN`)
  - CANON.md parsing & validation (`parse_canon_md`, `validate_canon_md`)
  - Hedging filter v2: LLM-based re-verification with stronger model
  - Structured `CanonFact` dataclass
- **Writer Fallback Chain**:
  - `capitol_runner.py` tries all models in `WRITER_FALLBACK_CHAIN`
  - Automatic fallback on API errors
- **Non-Destructive Sync**:
  - `sync_registry_dq` merges canon facts with existing DQs
  - `sync_all` preserves chapter metadata
- **Chapter Validation**:
  - Pre-check: file exists, >500 chars, valid encoding
- **Modern Build System**:
  - `ManuscriptBuilder` class with single responsibility
  - EPUB via `markdown-it-py` AST parsing (not regex)
  - Cover generation (default + custom)
  - Full XML validation on output
- **Comprehensive Test Suite** (80 tests):
  - Config validation, canon parsing, verdict parsing
  - Hedge filter (24 parametrized cases)
  - Reviewer selection with mocking
  - Log verdict creation/appending
  - Integration tests
- **GitHub Actions CI**:
  - Multi-Python (3.11, 3.12)
  - Lint with ruff
  - Structure verification
  - Optional integration test on dispatch
- **Documentation**:
  - Updated README with quickstart & CLI reference
  - CHANGELOG (this file)
  - CONTRIBUTING guide

### Changed
- **Breaking**: All hardcoded paths removed - must use `.env` configuration
- **Breaking**: Old entry points (`python scripts/capitol_runner.py`) replaced by `roman-pipeline chapter`
- **Breaking**: `expert-roman.yaml` now uses `{{PLACEHOLDERS}}` rendered at init
- **Improved**: `select_reviewers()` now guarantees reviewer ≠ writer using config
- **Improved**: `parse_verdict()` handles truncated/garbled model output robustly
- **Improved**: EPUB generation uses proper markdown AST parsing

### Fixed
- Unicode em-dash rendering in templates (was showing as `�?`)
- `.env` file encoding issues on Windows (UTF-8 enforced)
- `select_reviewers()` now properly skips writer model from fallback chain
- `sync_registry_dq` no longer overwrites existing dynamic questions

### Removed
- Old standalone scripts: `build_manuscript.py`, `build_all.py`, `build_final.py`, `assemble_repo.py`, `verify_build.py`, `verify_struct.py`, `verify_epub.py`, `verify_review.py`, `format_oficial.py`
- Hardcoded project name `"leah_si_lara"` everywhere
- Hardcoded absolute paths (`C:\Users\bizoi\...`)
- Monkey-patching `typer.confirm` in multiple files (now centralized)

## [v0.1.0] - 2026-08-15 (Original "Vibe Coded" Version)

### Added
- Initial pipeline for *The Glass Crown* (10 chapters)
- Basic canon checking with Gemini Flash-Lite
- LibriScribe integration for chapter writing
- EPUB generation (regex-based)
- Retry logic (max 4 attempts)
- Basic logging (`retry_log.jsonl`, `canon_registry.json`)

### Known Issues (Fixed in v0.2.0)
- Hardcoded paths and project name
- No unified CLI
- No project templating
- Reviewer fallback hardcoded
- Writer fallback not implemented
- EPUB generation fragile (regex-based)
- No test coverage
- No CI/CD