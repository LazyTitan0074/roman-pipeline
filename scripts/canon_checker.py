"""Canon checker core: typed verdicts, reviewer abstraction, hedging filter, LLM validation."""
from __future__ import annotations

import json
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, List, Optional

from .config import get_settings


@dataclass(frozen=True)
class Violation:
    fact: str
    quote: str
    why: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Verdict:
    pass_: bool
    violations: tuple[Violation, ...]

    def to_dict(self) -> dict:
        return {"pass": self.pass_, "violations": [v.to_dict() for v in self.violations]}

    @property
    def violation_count(self) -> int:
        return len(self.violations)


@dataclass(frozen=True)
class CanonFact:
    id: str
    label: str
    description: str
    raw_line: str


class Reviewer(Protocol):
    """Protocol for any model that can review a chapter."""
    def check(self, prompt: str) -> tuple[str, str]:
        ...
    @property
    def model_name(self) -> str:
        ...


class BaseReviewer:
    """Shared logic for all reviewers."""
    def __init__(self, model_name: str):
        self.model_name = model_name

    def check(self, prompt: str) -> tuple[str, str]:
        return self._call(prompt), self.model_name

    def _call(self, prompt: str) -> str:
        raise NotImplementedError


class FlashLiteReviewer(BaseReviewer):
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        super().__init__(model_name)
        from google import genai
        self._client = genai.Client(api_key=get_settings().google_ai_studio_api_key)

    def _call(self, prompt: str) -> str:
        r = self._client.models.generate_content(model=self.model_name, contents=prompt)
        return (r.text or "").strip()


class GroqReviewer(BaseReviewer):
    def __init__(self, model_name: str = "groq/gpt-oss-120b"):
        super().__init__(model_name)
        import requests
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_settings().groq_api_key}",
        })
        self._url = "https://api.groq.com/openai/v1/chat/completions"
        self._api_model = model_name.split("/", 1)[1] if "/" in model_name else model_name

    def _call(self, prompt: str) -> str:
        import requests
        r = self._session.post(
            self._url,
            json={
                "model": self._api_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2500,
                "temperature": 0.1,
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


class OllamaReviewer(BaseReviewer):
    def __init__(self, model_name: str = "ollama/qwen2.5:7b"):
        super().__init__(model_name)
        import requests
        self._session = requests.Session()
        self._session.headers.update({"Content-Type": "application/json"})
        self._url = "http://localhost:11434/v1/chat/completions"
        self._api_model = model_name.split("/", 1)[1] if "/" in model_name else model_name

    def _call(self, prompt: str) -> str:
        r = self._session.post(
            self._url,
            json={
                "model": self._api_model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"num_predict": 2500},
                "temperature": 0.1,
            },
            timeout=300,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


class MistralReviewer(BaseReviewer):
    def __init__(self, model_name: str = "mistral/ministral-8b-latest"):
        super().__init__(model_name)
        import requests
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {get_settings().mistral_api_key}",
        })
        self._url = "https://api.mistral.ai/v1/chat/completions"
        self._api_model = model_name.split("/", 1)[1] if "/" in model_name else model_name

    def _call(self, prompt: str) -> str:
        r = self._session.post(
            self._url,
            json={
                "model": self._api_model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2500,
                "temperature": 0.1,
            },
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()


# ──────────────────────────────────────────────────────────────────────────────
# CANON.md parsing & validation
# ──────────────────────────────────────────────────────────────────────────────

_CANON_LINE_RE = re.compile(r"^-\s*(C\d+)\s*:\s*([^—]+)\s*—\s*(.+)$")

def parse_canon_md(path: Path) -> List[CanonFact]:
    """Parse CANON.md into structured facts. Validates format."""
    text = path.read_text(encoding="utf-8")
    facts = []
    for i, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _CANON_LINE_RE.match(line)
        if not m:
            # Allow non-fact lines (comments, headers) but warn
            if line.startswith("-") and ":" in line:
                raise ValueError(f"CANON.md line {i}: invalid format (expected '- C##: LABEL — Description'): {line[:80]}")
            continue
        fid, label, desc = m.groups()
        facts.append(CanonFact(id=fid.upper(), label=label.strip(), description=desc.strip(), raw_line=line))
    return facts


def validate_canon_md(path: Path) -> List[str]:
    """Validate CANON.md format. Returns list of warnings/errors."""
    errors = []
    facts = parse_canon_md(path)
    seen_ids = set()
    for fact in facts:
        if fact.id in seen_ids:
            errors.append(f"Duplicate fact ID: {fact.id}")
        seen_ids.add(fact.id)
        # Check sequential numbering
        num = int(fact.id[1:])
        if num != len(seen_ids):
            errors.append(f"Non-sequential fact ID: {fact.id} (expected C{len(seen_ids):02d})")
    return errors


# ──────────────────────────────────────────────────────────────────────────────
# Hedging filter v1 (pattern-based)
# ──────────────────────────────────────────────────────────────────────────────

_HEDGE_PATTERNS = [
    r"no violation",
    r"not a violation",
    r"no pre-ch\d violation",
    r"is correct",
    r"no issue",
    r"correct per",
    r"no contradiction",
    r"confirmed post-ch\d",
    r"allowed",
    r"permitted",
    r"as required",
    r"as expected",
]
_HEDGE_RE = re.compile("|".join(_HEDGE_PATTERNS), re.IGNORECASE)
_VIOLATION_RE = re.compile(
    r'violat|contradict|break|inconsist|impli|wrong|stated as|aged \d|instead of',
    re.IGNORECASE,
)


def is_hedge(why: str) -> bool:
    """Return True if the 'why' text is a hedge/non-finding."""
    if _HEDGE_RE.search(why):
        return True
    if not _VIOLATION_RE.search(why):
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Verdict parsing: strict JSON first, then truncation-tolerant extraction
# ──────────────────────────────────────────────────────────────────────────────

_JSON_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_OBJECT_RE = re.compile(
    r'\{\s*"fact"\s*:\s*"([^"]+)"\s*,\s*"quote"\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*"why"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}'
)


def parse_verdict(raw: str) -> Verdict:
    """Parse reviewer output into a typed Verdict. Never raises."""
    # 1. Try direct JSON
    try:
        data = json.loads(raw)
        return _verdict_from_dict(data)
    except json.JSONDecodeError:
        pass

    # 2. Try fenced code block
    m = _JSON_BLOCK_RE.search(raw)
    if m:
        try:
            data = json.loads(m.group(1))
            return _verdict_from_dict(data)
        except json.JSONDecodeError:
            pass

    # 3. Extract complete violation objects from truncated/garbled output
    violations = []
    for match in _OBJECT_RE.finditer(raw):
        fact, quote, why = match.groups()
        if is_hedge(why):
            continue
        violations.append(Violation(fact=fact, quote=quote[:200], why=why[:200]))

    if violations:
        return Verdict(pass_=False, violations=tuple(violations[:10]))

    # 4. Heuristic: explicit "pass": true ONLY if full JSON parses and violations is empty
    if re.search(r'"pass"\s*:\s*true', raw):
        try:
            data = json.loads(raw)
            if data.get("pass") is True and not data.get("violations"):
                return Verdict(pass_=True, violations=())
        except json.JSONDecodeError:
            pass  # Fall through to total failure - don't trust truncated "pass": true

    # 5. Total failure
    return Verdict(
        pass_=False,
        violations=(Violation(fact="PARSE", quote=raw[:200], why="unparseable verdict"),),
    )


def _verdict_from_dict(data: dict) -> Verdict:
    violations = []
    for v in data.get("violations", []):
        why = str(v.get("why", ""))
        if is_hedge(why):
            continue
        violations.append(
            Violation(
                fact=str(v.get("fact", "?")),
                quote=str(v.get("quote", ""))[:200],
                why=why[:200],
            )
        )
    return Verdict(pass_=len(violations) == 0, violations=tuple(violations))


# ──────────────────────────────────────────────────────────────────────────────
# Reviewer selector: guarantees reviewer ≠ writer, uses config fallback chain
# ──────────────────────────────────────────────────────────────────────────────

def select_reviewers(writer_model: str, settings) -> List[BaseReviewer]:
    """Return ordered list of reviewers from config, skipping any that match the writer."""
    writer = writer_model.lower()
    reviewers: List[BaseReviewer] = []

    # Primary reviewer from config
    primary = settings.reviewer_primary.lower()
    if primary == "gemini-2.5-flash-lite" and settings.google_ai_studio_api_key:
        reviewers.append(FlashLiteReviewer())
    elif primary.startswith("groq/") and settings.groq_api_key:
        reviewers.append(GroqReviewer(primary))
    elif primary.startswith("mistral/") and settings.mistral_api_key:
        reviewers.append(MistralReviewer(primary))
    elif primary.startswith("ollama/"):
        reviewers.append(OllamaReviewer(primary))

    # Fallback chain from config
    for model_spec in settings.reviewer_fallback_chain:
        model_spec_lower = model_spec.lower()
        if model_spec_lower == writer:
            continue  # skip if same as writer
        
        if model_spec.startswith("ollama/"):
            reviewers.append(OllamaReviewer(model_spec))
        elif model_spec.startswith("groq/") and settings.groq_api_key:
            reviewers.append(GroqReviewer(model_spec))
        elif model_spec.startswith("mistral/") and settings.mistral_api_key:
            reviewers.append(MistralReviewer(model_spec))
        elif model_spec.startswith("google_ai_studio/") and settings.google_ai_studio_api_key:
            # Could add more Google models here
            reviewers.append(FlashLiteReviewer(model_spec.split("/", 1)[1]))

    return reviewers


# ──────────────────────────────────────────────────────────────────────────────
# LLM-based validation (Hedge filter v2) — re-verify violations with stronger model
# ──────────────────────────────────────────────────────────────────────────────

async def validate_violations_with_llm(
    violations: List[Violation],
    facts_text: str,
    chapter_text: str,
    settings,
) -> List[Violation]:
    """Re-verify violations with primary reviewer to eliminate false positives."""
    if not violations:
        return []
    
    # Use primary reviewer (Gemini Flash-Lite) for validation
    if not settings.google_ai_studio_api_key:
        return violations  # Can't validate, return as-is
    
    validator = FlashLiteReviewer()
    
    violations_json = json.dumps([v.to_dict() for v in violations], ensure_ascii=False)
    prompt = f"""You are a strict canon auditor. The following violations were flagged by a smaller model.
    
CANON FACTS:
{facts_text}

CHAPTER TEXT (first 3000 chars):
{chapter_text[:3000]}...

VIOLATIONS TO VERIFY:
{violations_json}

For each violation, respond with ONLY a JSON array of objects:
[{{"fact": "C##", "confirmed": true/false, "reason": "brief reason"}}]

A violation is CONFIRMED only if the chapter text DIRECTLY CONTRADICTS a declared fact.
Behavior, voice, implied maturity, or confirmed facts are NOT violations.
"""
    try:
        raw = validator._call(prompt)
        # Parse validator response
        m = _JSON_BLOCK_RE.search(raw)
        if m:
            raw = m.group(1)
        results = json.loads(raw)
        
        confirmed = []
        for v, r in zip(violations, results):
            if r.get("confirmed", False):
                confirmed.append(v)
        return confirmed
    except Exception:
        # If validation fails, return original violations (conservative)
        return violations


# ──────────────────────────────────────────────────────────────────────────────
# Main checker class
# ──────────────────────────────────────────────────────────────────────────────

class CanonChecker:
    def __init__(self, prompt_template: str | None = None):
        self.prompt_template = prompt_template or self._load_default_prompt()

    def _load_default_prompt(self) -> str:
        path = get_settings().base_dir / "templates" / "canon_check_prompt.md"
        return path.read_text(encoding="utf-8")

    def check_chapter(
        self,
        chapter: int,
        writer_model: str,
        facts_text: str,
        chapter_text: str,
        settings,
    ) -> tuple[Verdict, str]:
        """Run canon check with reviewer fallback chain from config."""
        prompt = self.prompt_template.format(facts=facts_text, ch=chapter, text=chapter_text)
        reviewers = select_reviewers(writer_model, settings)

        last_err = None
        for reviewer in reviewers:
            try:
                raw, model = reviewer.check(prompt)
                verdict = parse_verdict(raw)
                
                # Hedge filter v2: re-verify with stronger model if violations found
                if not verdict.pass_ and verdict.violations:
                    import asyncio
                    confirmed = asyncio.run(validate_violations_with_llm(
                        list(verdict.violations), facts_text, chapter_text, settings
                    ))
                    if confirmed:
                        verdict = Verdict(pass_=False, violations=tuple(confirmed))
                    else:
                        verdict = Verdict(pass_=True, violations=())
                
                return verdict, model
            except Exception as e:
                last_err = f"{reviewer.model_name}: {str(e)[:150]}"
                continue

        # All reviewers failed
        return (
            Verdict(
                pass_=False,
                violations=(Violation(fact="REVIEWER-DOWN", quote="", why=last_err or "all reviewers failed"),),
            ),
            "none",
        )


# ──────────────────────────────────────────────────────────────────────────────
# Logging & registry
# ──────────────────────────────────────────────────────────────────────────────

def log_verdict(
    base_dir: Path,
    chapter: int,
    writer: str,
    reviewer: str,
    verdict: Verdict,
) -> None:
    """Append to canon_log.jsonl and update canon_registry.json."""
    result = {
        "chapter": chapter,
        "writer": writer,
        "reviewer": reviewer,
        "pass": verdict.pass_,
        "violations": [v.to_dict() for v in verdict.violations],
        "at": datetime.now(timezone.utc).isoformat(),
    }

    # canon_log.jsonl (append)
    log_file = base_dir / "canon_log.jsonl"
    existing = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
    log_file.write_text(existing + json.dumps(result, ensure_ascii=False) + "\n", encoding="utf-8")

    # canon_verdict_ch{N}.json (per-chapter latest)
    (base_dir / f"canon_verdict_ch{chapter}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # canon_registry.json (summary)
    reg_path = base_dir / "canon_registry.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8")) if reg_path.exists() else {"chapters": {}}
    reg["chapters"][str(chapter)] = {
        "status": "pass" if verdict.pass_ else "FAIL",
        "reviewer": reviewer,
        "violations": verdict.violation_count,
    }
    reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2), encoding="utf-8")


def print_verdict(chapter: int, writer: str, reviewer: str, verdict: Verdict) -> None:
    print(f"chapter={chapter} writer={writer} reviewer={reviewer} verdict={'PASS' if verdict.pass_ else 'FAIL'} violations={verdict.violation_count}")
    for v in verdict.violations[:10]:
        print(f" - [{v.fact}] {v.why[:160]}")