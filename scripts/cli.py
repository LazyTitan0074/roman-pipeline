"""Unified CLI for roman-pipeline. Single entry point for all operations."""
from __future__ import annotations

import os
import sys
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

# Lazy imports - avoid triggering config validation at import time
def _get_settings():
    from .config import get_settings
    return get_settings()

def _validate_env_or_die():
    from .config import validate_env_or_die
    return validate_env_or_die()

def _find_project_root() -> Path:
    """Find the project directory by looking for .env file in current, parent, or subdirectories."""
    # If ROMAN_PIPELINE_ENV_FILE is set, use its directory
    env_file_path = os.getenv("ROMAN_PIPELINE_ENV_FILE")
    if env_file_path:
        env_file = Path(env_file_path).expanduser().resolve()
        if env_file.exists():
            return env_file.parent
    
    cwd = Path.cwd()
    
    # Check current directory and parents
    for path in [Path.cwd()] + list(Path.cwd().parents):
        env_file = path / ".env"
        if env_file.exists():
            try:
                content = env_file.read_text(encoding="utf-8")
                if "PROJECT_NAME" in content or "WRITER_MODEL" in content:
                    return path
            except Exception:
                pass
    
    # Check subdirectories (project folders)
    for subdir in Path.cwd().iterdir():
        if subdir.is_dir() and not subdir.name.startswith("."):
            env_file = subdir / ".env"
            if env_file.exists():
                try:
                    content = env_file.read_text(encoding="utf-8")
                    if "PROJECT_NAME" in content or "WRITER_MODEL" in content:
                        return subdir
                except Exception:
                    pass
    
    return Path.cwd()

def _chdir_to_project():
    """Change to project directory if not already there."""
    project_root = _find_project_root()
    if project_root != Path.cwd():
        os.chdir(project_root)
        print(f"[dim]Changed to project directory: {project_root}[/dim]")


app = typer.Typer(
    name="roman-pipeline",
    help="AI-driven novel production pipeline",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


# ─── Helpers ───
def _settings() -> "Settings":
    return _validate_env_or_die()


def _print_config() -> None:
    s = _settings()
    table = Table(title="Pipeline Configuration", show_header=True, header_style="bold cyan")
    table.add_column("Setting", style="yellow")
    table.add_column("Value", style="green")
    table.add_row("BASE_DIR", str(s.base_dir))
    table.add_row("PROJ_DIR", str(s.proj_dir))
    table.add_row("PROJECT_NAME", s.project_name)
    table.add_row("NUM_CHAPTERS", str(s.num_chapters))
    table.add_row("WRITER", f"{s.writer_provider}/{s.writer_model}")
    table.add_row("REVIEWER_PRIMARY", s.reviewer_primary)
    table.add_row("MAX_ATTEMPTS", str(s.max_attempts))
    console.print(table)


# ─── Commands ───
@app.command()
def config() -> None:
    """Show current configuration."""
    _chdir_to_project()
    _print_config()


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name (folder name)"),
    target: Path = typer.Option(Path("."), "--target", "-t", help="Target directory"),
    title: str | None = typer.Option(None, "--title", help="Book title (defaults to name)"),
    genre: str = typer.Option("Fantasy", "--genre", "-g", help="Genre"),
    language: str = typer.Option("English", "--language", "-l", help="Language"),
    author: str = typer.Option("Author Name", "--author", "-a", help="Author name"),
    num_chapters: int = typer.Option(10, "--chapters", "-c", help="Number of chapters"),
) -> None:
    """Create a new project from templates."""
    from scripts.init_project import create_project
    create_project(name, target, title or name.replace("_", " ").title(), genre, language, author, num_chapters)


@app.command()
def chapter(
    n: int = typer.Argument(..., help="Chapter number (1-based)"),
    max_attempts: int = typer.Option(None, "--max-attempts", "-m", help="Override max retry attempts"),
) -> None:
    """Run production for one chapter: sync → write → canon check → retry."""
    _chdir_to_project()
    from scripts.capitol_runner import run_chapter
    s = _settings()
    attempts = max_attempts or s.max_attempts
    run_chapter(n, attempts, s)


@app.command()
def check(
    n: int = typer.Argument(..., help="Chapter number to verify"),
    writer: str = typer.Option("unknown", "--writer", "-w", help="Writer model identifier"),
) -> None:
    """Run canon check on an existing chapter."""
    _chdir_to_project()
    from scripts.canon_check import check_chapter
    s = _settings()
    check_chapter(n, writer, s)


@app.command()
def build(
    target: str = typer.Option("all", "--target", "-t", help="Target: manuscript | format | epub | all"),
) -> None:
    """Build manuscript, format, and/or EPUB."""
    _chdir_to_project()
    from scripts.build import ManuscriptBuilder
    s = _settings()
    builder = ManuscriptBuilder(s)
    
    if target in ("manuscript", "all"):
        console.print("[cyan]Assembling manuscript...[/cyan]")
        builder.assemble()
    
    if target in ("format", "all"):
        console.print("[cyan]Formatting official manuscript...[/cyan]")
        builder.format_official()
    
    if target in ("epub", "all"):
        console.print("[cyan]Generating EPUB...[/cyan]")
        builder.make_epub()
    
    if target in ("all",):
        console.print("[cyan]Building cover...[/cyan]")
        builder.make_cover()
    
    console.print("[green]Build complete![/green]")


@app.command()
def sync() -> None:
    """Sync all project data: scenes, outline, worldbuilding → LibriScribe project_data.json."""
    _chdir_to_project()
    from scripts.sync_all import sync_all
    s = _settings()
    sync_all(s)


@app.command()
def verify(
    check: str = typer.Option("all", "--check", "-c", help="What to verify: struct | build | epub | review | all"),
) -> None:
    """Run verification checks."""
    _chdir_to_project()
    from scripts.verify import run_verification
    s = _settings()
    run_verification(check, s)


@app.command()
def logs(
    chapter: int | None = typer.Option(None, "--chapter", "-ch", help="Filter by chapter"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of entries to show"),
) -> None:
    """Show retry / canon logs."""
    _chdir_to_project()
    from scripts.logs import show_logs
    s = _settings()
    show_logs(s.base_dir, chapter, limit)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        _chdir_to_project()
        _print_config()
        console.print("\n[dim]Use --help for commands[/dim]")


if __name__ == "__main__":
    app()