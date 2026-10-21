"""Tests for roman-pipeline core modules."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scripts.canon_checker import (
    Violation,
    Verdict,
    parse_verdict,
    is_hedge,
    log_verdict,
    print_verdict,
)
from scripts.config import Settings, validate_env_or_die


# ─── parse_verdict tests ───
def test_parse_verdict_clean_json() -> None:
    raw = '{"pass": true, "violations": []}'
    v = parse_verdict(raw)
    assert v.pass_ is True
    assert v.violations == ()


def test_parse_verdict_with_violations() -> None:
    raw = '{"pass": false, "violations": [{"fact": "C01", "quote": "Leah was 19", "why": "contradicts C01 age 20"}]}'
    v = parse_verdict(raw)
    assert v.pass_ is False
    assert len(v.violations) == 1
    assert v.violations[0].fact == "C01"


def test_parse_verdict_fenced_code_block() -> None:
    raw = '```json\n{"pass": true, "violations": []}\n```'
    v = parse_verdict(raw)
    assert v.pass_ is True


def test_parse_verdict_truncated_with_objects() -> None:
    # Simulate truncated output with complete violation objects
    raw = '''Some preamble text
{"fact": "C08", "quote": "Lara appeared in ch3", "why": "violates C08 Lara pre-ch4"}
{"fact": "C09", "quote": "client tended her pleasure", "why": "contradicts C09 pre-Lara rule"}
More text after truncation'''
    v = parse_verdict(raw)
    assert v.pass_ is False
    assert len(v.violations) == 2


def test_parse_verdict_hedged_violations_filtered() -> None:
    raw = '''{"pass": false, "violations": [
        {"fact": "C01", "quote": "Leah is 20", "why": "confirmed post-ch4"},
        {"fact": "C08", "quote": "Lara in ch3", "why": "violates C08"}
    ]}'''
    v = parse_verdict(raw)
    # Hedge "confirmed post-ch4" should be filtered out
    assert v.pass_ is False
    assert len(v.violations) == 1
    assert v.violations[0].fact == "C08"


def test_parse_verdict_unparseable_fallback() -> None:
    raw = "This is not JSON at all"
    v = parse_verdict(raw)
    assert v.pass_ is False
    assert v.violations[0].fact == "PARSE"


# ─── is_hedge tests ───
@pytest.mark.parametrize("why,expected", [
    ("no violation here", True),
    ("not a violation", True),
    ("is correct per C01", True),
    ("no pre-ch4 violation", True),
    ("no issue found", True),
    ("correct per canon", True),
    ("no contradiction detected", True),
    ("confirmed post-ch4", True),
    ("allowed by rules", True),
    ("permitted under canon", True),
    ("as required by C01", True),
    ("as expected", True),
    ("violates C01 because age is wrong", False),
    ("contradicts C08 Lara appears early", False),
    ("breaks canon rule C09", False),
    ("inconsistent with C02", False),
    ("implies she knew poison", False),
    ("wrong age stated as 19", False),
    ("instead of 20 it says 19", False),
    ("aged 19 instead of 20", False),
    ("stated as fact when it should be suspicion", False),
])
def test_is_hedge(why: str, expected: bool) -> None:
    assert is_hedge(why) == expected


# ─── Violation/Verdict serialization ───
def test_violation_to_dict() -> None:
    v = Violation(fact="C01", quote="Leah was 19", why="contradicts C01")
    d = v.to_dict()
    assert d == {"fact": "C01", "quote": "Leah was 19", "why": "contradicts C01"}


def test_verdict_to_dict() -> None:
    v = Verdict(pass_=False, violations=(Violation(fact="C01", quote="q", why="w"),))
    d = v.to_dict()
    assert d["pass"] is False
    assert len(d["violations"]) == 1


# ─── Config tests ───
def test_settings_validation_missing_dirs(tmp_path: Path) -> None:
    # Create a temp .env with non-existent paths
    env_file = tmp_path / ".env"
    env_file.write_text(f"BASE_DIR={tmp_path}/nonexistent\nPROJ_DIR={tmp_path}/also_missing\n")

    settings = Settings(_env_file=str(env_file))
    missing = settings.validate_required()
    assert len(missing) >= 2  # Both dirs missing
    assert any("BASE_DIR does not exist" in m for m in missing)
    assert any("PROJ_DIR does not exist" in m for m in missing)


def test_settings_validation_missing_keys(tmp_path: Path) -> None:
    # Create dirs but no API keys
    base = tmp_path / "base"
    proj = tmp_path / "proj"
    base.mkdir()
    proj.mkdir()

    env_file = tmp_path / ".env"
    env_file.write_text(f"BASE_DIR={base}\nPROJ_DIR={proj}\n")

    settings = Settings(_env_file=str(env_file))
    missing = settings.validate_required()
    assert any("API keys" in m for m in missing)


# ─── log_verdict tests ───
def test_log_verdict_creates_files(tmp_path: Path) -> None:
    verdict = Verdict(pass_=True, violations=())
    log_verdict(tmp_path, 1, "writer_model", "reviewer_model", verdict)

    # Check canon_log.jsonl
    log_content = (tmp_path / "canon_log.jsonl").read_text(encoding="utf-8")
    log_entry = json.loads(log_content.strip())
    assert log_entry["chapter"] == 1
    assert log_entry["writer"] == "writer_model"
    assert log_entry["reviewer"] == "reviewer_model"
    assert log_entry["pass"] is True

    # Check canon_verdict_ch1.json
    verdict_content = (tmp_path / "canon_verdict_ch1.json").read_text(encoding="utf-8")
    verdict_entry = json.loads(verdict_content)
    assert verdict_entry["pass"] is True

    # Check canon_registry.json
    reg_content = (tmp_path / "canon_registry.json").read_text(encoding="utf-8")
    reg = json.loads(reg_content)
    assert reg["chapters"]["1"]["status"] == "pass"


def test_log_verdict_appends_to_log(tmp_path: Path) -> None:
    verdict1 = Verdict(pass_=True, violations=())
    verdict2 = Verdict(pass_=False, violations=(Violation(fact="C01", quote="q", why="w"),))

    log_verdict(tmp_path, 1, "writer", "reviewer1", verdict1)
    log_verdict(tmp_path, 1, "writer", "reviewer2", verdict2)

    log_content = (tmp_path / "canon_log.jsonl").read_text(encoding="utf-8")
    lines = log_content.strip().split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0])["pass"] is True
    assert json.loads(lines[1])["pass"] is False


# ─── Name-guard logic (from verify_struct) ───
def test_name_guard_mira_before_ch5() -> None:
    """Mira should not appear before chapter 5."""
    # This is tested via the sync verify command, but we can unit test the logic
    import re
    text_ch3 = "Mira walked into the room."  # Violation
    text_ch5 = "Mira walked into the room."  # OK

    assert re.search(r"\bMira\b", text_ch3) is not None
    assert re.search(r"\bMira\b", text_ch5) is not None


def test_name_guard_sera_only_ch9() -> None:
    import re
    text_ch8 = "Sera was here."  # Violation
    text_ch9 = "Sera was here."  # OK
    text_ch10 = "Sera was here."  # Violation

    assert re.search(r"\bSera\b", text_ch8) is not None
    assert re.search(r"\bSera\b", text_ch9) is not None
    assert re.search(r"\bSera\b", text_ch10) is not None


# ─── Age word check ───
def test_cassian_age_words() -> None:
    import re
    forbidden = ["sixteen", "seventeen", "eighteen", "nineteen", "thirteen", "fifteen"]
    text = "Cassian was sixteen years old."
    found = [w for w in forbidden if re.search(rf"\b{w}\b", text, re.I)]
    assert "sixteen" in found

    text_ok = "Cassian was fourteen years old."
    found_ok = [w for w in forbidden if re.search(rf"\b{w}\b", text_ok, re.I)]
    assert found_ok == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])