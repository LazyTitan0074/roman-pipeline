"""Log viewing utilities."""
from __future__ import annotations

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table


console = Console()


def show_logs(base_dir: Path, chapter: int | None = None, limit: int = 20) -> None:
    """Show retry and canon logs."""
    
    # Retry log
    retry_log = base_dir / "retry_log.jsonl"
    if retry_log.exists():
        console.print("\n[bold cyan]Retry Log[/bold cyan]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Ch", style="yellow", width=4)
        table.add_column("Attempt", width=8)
        table.add_column("Writer", style="green")
        table.add_column("Verdict", width=8)
        table.add_column("Violations", width=10)
        table.add_column("Time", width=20)
        
        lines = retry_log.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-limit:]:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if chapter is not None and entry.get("chapter") != chapter:
                    continue
                verdict_style = "green" if entry.get("verdict") == "PASS" else "red"
                table.add_row(
                    str(entry.get("chapter", "")),
                    str(entry.get("attempt", "")),
                    entry.get("writer", "")[:40],
                    f"[{verdict_style}]{entry.get('verdict', '')}[/{verdict_style}]",
                    str(entry.get("violations", "")),
                    entry.get("at", "")[:19].replace("T", " "),
                )
            except json.JSONDecodeError:
                pass
        console.print(table)
    else:
        console.print("[dim]No retry_log.jsonl found[/dim]")
    
    # Canon registry
    registry = base_dir / "canon_registry.json"
    if registry.exists():
        console.print("\n[bold cyan]Canon Registry[/bold cyan]")
        import json as json_lib
        reg = json_lib.loads(registry.read_text(encoding="utf-8"))
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Ch", style="yellow", width=4)
        table.add_column("Status", width=10)
        table.add_column("Reviewer", style="green", width=30)
        table.add_column("Violations", width=10)
        
        for ch_str, data in sorted(reg.get("chapters", {}).items(), key=lambda x: int(x[0])):
            ch_num = int(ch_str)
            if chapter is not None and ch_num != chapter:
                continue
            status = data.get("status", "UNKNOWN")
            status_style = "green" if status == "pass" else "red"
            table.add_row(
                ch_str,
                f"[{status_style}]{status}[/{status_style}]",
                data.get("reviewer", "")[:30],
                str(data.get("violations", "")),
            )
        console.print(table)
    else:
        console.print("[dim]No canon_registry.json found[/dim]")
    
    # Canon log (detailed)
    canon_log = base_dir / "canon_log.jsonl"
    if canon_log.exists() and chapter is not None:
        console.print(f"\n[bold cyan]Canon Log (Chapter {chapter})[/bold cyan]")
        lines = canon_log.read_text(encoding="utf-8").strip().split("\n")
        for line in lines[-10:]:  # last 10 entries for this chapter
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if entry.get("chapter") != chapter:
                    continue
                console.print(f"  Writer: {entry.get('writer')}")
                console.print(f"  Reviewer: {entry.get('reviewer')}")
                console.print(f"  Pass: {entry.get('pass')}")
                for v in entry.get("violations", []):
                    console.print(f"    [red]Violation[/red] [{v.get('fact')}]: {v.get('why')[:100]}")
                console.print(f"  Time: {entry.get('at')[:19].replace('T', ' ')}")
                console.print()
            except json.JSONDecodeError:
                pass


if __name__ == "__main__":
    from .config import get_settings
    settings = get_settings()
    show_logs(settings.base_dir)