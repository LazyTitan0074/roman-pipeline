"""Unified verification checks."""
from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

from .config import get_settings


def norm(t: str) -> str:
    """Normalize text for comparison."""
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'").replace('&', '&')
    t = re.sub(r"\s+", " ", t)
    return t


def verify_struct(settings) -> bool:
    """Verify project structure: all chapters exist, have content."""
    proj = settings.proj_dir
    base = settings.base_dir
    ok = True
    
    print("=== Structure Verification ===")
    
    # Check chapters
    for n in range(1, settings.num_chapters + 1):
        ch_file = proj / f"chapter_{n}.md"
        if not ch_file.exists():
            print(f"  ❌ ch{n}: MISSING")
            ok = False
        else:
            text = ch_file.read_text(encoding="utf-8")
            words = len(text.split())
            print(f"  ✅ ch{n}: {words} words")
            if words < 1000:
                print(f"    ⚠️  Very short (< 1000 words)")
    
    # Check required files
    required = [
        base / "CANON.md",
        base / "templates" / "VOICE.md",
        base / "templates" / "BEAT_SHEET.md",
        base / "templates" / "CHAPTER_CHECKLIST.md",
    ]
    for f in required:
        status = "✅" if f.exists() else "❌"
        print(f"  {status} {f.name}")
        if not f.exists():
            ok = False
    
    return ok


def verify_build(settings) -> bool:
    """Verify build output matches source."""
    proj = settings.proj_dir
    archive = Path.home() / "roman"
    ok = True
    
    print("\n=== Build Verification ===")
    
    # 1. PROJ vs archive (identical?)
    for n in range(1, settings.num_chapters + 1):
        a = (proj / f"chapter_{n}.md").read_text(encoding="utf-8")
        b = (archive / f"chapter_{n}.md").read_text(encoding="utf-8") if (archive / f"chapter_{n}.md").exists() else ""
        same = (a == b)
        print(f"  ch{n} proj==archive: {same} ({len(a.split())} words)")
        ok &= same
    
    # 2. Manuscript markers present
    ms = (archive / "manuscript_official.md").read_text(encoding="utf-8")
    marks = [
        "Eight years ago", "two taps, then nothing", "cold stone and black tea",
        "Enjoy the cage, little queen", "Eleven crowns, three doors",
        "rock crystal,", "keeper of the glass crown",
        "By the second evening she had learned", "She brought the strip down at first light",
        "Vestalia isn", "single face split by a vertical line",
    ]
    for m in marks:
        hit = m in ms
        print(f"  {'✅' if hit else '❌'} manuscript: {m[:50]}")
        ok &= hit
    
    return ok


def verify_epub(settings) -> bool:
    """Verify EPUB content matches manuscript."""
    archive = Path.home() / "roman"
    epub_path = archive / "publish" / f"{settings.project_name}.epub"
    
    if not epub_path.exists():
        # Try old name
        epub_path = archive / "publish" / "The_Glass_Crown.epub"
    
    if not epub_path.exists():
        print(f"❌ EPUB not found: {epub_path}")
        return False
    
    ok = True
    print("\n=== EPUB Verification ===")
    
    with zipfile.ZipFile(epub_path) as z:
        # Extract all chapter XHTML
        ep = ""
        for i in range(1, settings.num_chapters + 1):
            try:
                ep += z.read(f"OEBPS/ch{i:02d}.xhtml").decode("utf-8")
            except KeyError:
                print(f"  ❌ ch{i}: missing in EPUB")
                ok = False
        
        epn = norm(ep)
        
        # Check each chapter content preserved
        for n in range(1, settings.num_chapters + 1):
            src = norm((settings.proj_dir / f"chapter_{n}.md").read_text(encoding="utf-8"))
            # Split into paragraphs (skip scene headings)
            paras = [
                p.strip() for p in re.split(r"\n\s*\n", src) 
                if len(p.strip()) > 120 and not re.match(r"^#{0,4}\s*\*{0,2}Scene \d+", p.strip())
            ]
            bad = [p for p in paras[:200] if norm(p)[:80] not in epn]
            if bad:
                print(f"  ❌ ch{n}: {len(bad)} paragraphs missing from EPUB (ex: {bad[0][:80]})")
                ok = False
            else:
                print(f"  ✅ ch{n}: all paragraphs found in EPUB")
    
    print(f"  EPUB size: {epub_path.stat().st_size} bytes")
    return ok


def verify_review(settings) -> bool:
    """Verify canon review logs."""
    base = settings.base_dir
    ok = True
    
    print("\n=== Review Verification ===")
    
    registry = base / "canon_registry.json"
    if not registry.exists():
        print("  ❌ canon_registry.json missing")
        return False
    
    import json
    reg = json.loads(registry.read_text(encoding="utf-8"))
    
    for ch_str, data in reg.get("chapters", {}).items():
        status = data.get("status", "UNKNOWN")
        violations = data.get("violations", 0)
        reviewer = data.get("reviewer", "unknown")
        
        icon = "✅" if status == "pass" else "❌"
        print(f"  {icon} ch{ch_str}: {status} (violations: {violations}, reviewer: {reviewer})")
        
        if status != "pass":
            ok = False
    
    # Check all chapters reviewed
    reviewed = set(reg.get("chapters", {}).keys())
    expected = {str(i) for i in range(1, settings.num_chapters + 1)}
    missing = expected - reviewed
    if missing:
        print(f"  ❌ Missing reviews for chapters: {', '.join(sorted(missing))}")
        ok = False
    
    return ok


def run_verification(check: str, settings) -> None:
    """Run selected verification checks."""
    checks = {
        "struct": verify_struct,
        "build": verify_build,
        "epub": verify_epub,
        "review": verify_review,
    }
    
    if check == "all":
        to_run = checks.values()
    else:
        to_run = [checks.get(check)]
        if not to_run[0]:
            print(f"Unknown check: {check}. Options: {', '.join(checks.keys())}, all")
            sys.exit(1)
    
    all_ok = True
    for fn in to_run:
        try:
            result = fn(settings)
            all_ok &= result
        except Exception as e:
            print(f"  ❌ {fn.__name__} failed: {e}")
            all_ok = False
    
    print(f"\n{'='*40}")
    print(f"Result: {'ALL OK' if all_ok else 'PROBLEMS FOUND'}")
    
    if not all_ok:
        sys.exit(1)