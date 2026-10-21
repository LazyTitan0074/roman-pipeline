"""Runner cu retry capat (max 4/capitol), log per model, registru canon -> dq."""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import os
BASE = Path(os.getenv("BASE_DIR", r"C:\Users\bizoi\libriscribe-roman"))
PROJ = Path(os.getenv("PROJ_DIR", r"C:\Users\bizoi\AppData\Roaming\Python\Python314\projects\leah_si_lara"))
MAX_ATTEMPTS = 4


def log_attempt(ch, attempt, writer, verdict, n_viol):
    with open(BASE / "retry_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"chapter": ch, "attempt": attempt, "writer": writer,
                            "verdict": verdict, "violations": n_viol,
                            "at": datetime.now(timezone.utc).isoformat()},
                           ensure_ascii=False) + "\n")


def sync_registry_dq():
    from libriscribe.knowledge_base import ProjectKnowledgeBase
    facts = {}
    for line in (BASE / "CANON.md").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("- C") and ":" in line:
            fid, ftxt = line[2:].split(":", 1)
            facts["CANON-" + fid.strip()] = "CANON (must respect): " + ftxt.strip()[:320]
    pkb = ProjectKnowledgeBase.load_from_file(str(PROJ / "project_data.json"))
    dq = dict(pkb.dynamic_questions or {})
    dq.update(facts)
    pkb.dynamic_questions = dq
    pkb.save_to_file(str(PROJ / "project_data.json"))
    print("dq synced: %d canon facts injected for next chapters" % len(facts))


def write_chapter(ch):
    import typer
    typer.confirm = lambda *a, **k: True
    import libriscribe.main as m
    m.typer.confirm = lambda *a, **k: True
    from libriscribe.agents.project_manager import ProjectManagerAgent
    import os
    project_name = os.getenv("LIBRISCRIBE_PROJECT_NAME", "my_novel")
    pm = ProjectManagerAgent(llm_client=None)
    pm.load_project_data(project_name)
    pkb = pm.project_knowledge_base
    pm.initialize_llm_client(pkb.llm_provider, pkb.model)
    writer = pkb.llm_provider + "/" + str(pkb.model)
    pm.write_and_review_chapter(ch)
    pm.checkpoint()
    return writer


def main():
    ch = int(sys.argv[1])
    sync_registry_dq()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print("--- ch%s attempt %d/%d ---" % (ch, attempt, MAX_ATTEMPTS), flush=True)
        f = PROJ / ("chapter_" + str(ch) + ".md")
        if f.exists():
            f.unlink()
        writer = write_chapter(ch)
        r = subprocess.run(["python", str(BASE / "canon_check.py"), str(ch), writer],
                           capture_output=True, text=True, cwd=str(BASE))
        out = r.stdout if r.stdout else r.stderr
        print(out[-1500:])
        v = json.loads((BASE / ("canon_verdict_ch" + str(ch) + ".json")).read_text(encoding="utf-8"))
        log_attempt(ch, attempt, writer, "PASS" if v["pass"] else "FAIL", len(v["violations"]))
        if v["pass"]:
            print("ch%s PASS din incercarea %d" % (ch, attempt))
            return
        print("ch%s RESPINS (%d abateri), reincerc..." % (ch, len(v["violations"])))
    print("ch%s ESUAT dupa %d incercari — interventie umana necesara" % (ch, MAX_ATTEMPTS))


def run_chapter(ch: int, max_attempts: int, settings):
    """Wrapper for CLI compatibility."""
    import os
    os.environ["BASE_DIR"] = str(settings.base_dir)
    os.environ["PROJ_DIR"] = str(settings.proj_dir)
    
    global BASE, PROJ, MAX_ATTEMPTS
    BASE = settings.base_dir
    PROJ = settings.proj_dir
    MAX_ATTEMPTS = max_attempts
    
    # Re-implement main logic with passed parameters
    sync_registry_dq()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print("--- ch%s attempt %d/%d ---" % (ch, attempt, MAX_ATTEMPTS), flush=True)
        f = PROJ / ("chapter_" + str(ch) + ".md")
        if f.exists():
            f.unlink()
        writer = write_chapter(ch)
        r = subprocess.run(["python", str(BASE / "canon_check.py"), str(ch), writer],
                           capture_output=True, text=True, cwd=str(BASE))
        out = r.stdout if r.stdout else r.stderr
        print(out[-1500:])
        v = json.loads((BASE / ("canon_verdict_ch" + str(ch) + ".json")).read_text(encoding="utf-8"))
        log_attempt(ch, attempt, writer, "PASS" if v["pass"] else "FAIL", len(v["violations"]))
        if v["pass"]:
            print("ch%s PASS din incercarea %d" % (ch, attempt))
            return
        print("ch%s RESPINS (%d abateri), reincerc..." % (ch, len(v["violations"])))
    print("ch%s ESUAT dupa %d incercari — interventie umana necesara" % (ch, MAX_ATTEMPTS))
    raise SystemExit(1)


if __name__ == "__main__":
    main()
