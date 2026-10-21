"""Unified build system: manuscript assembly, formatting, EPUB, cover."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from .config import get_settings
from .make_epub import generate_epub
from .make_cover import generate_cover


class ManuscriptBuilder:
    def __init__(self, settings):
        self.settings = settings
        self.proj = settings.proj_dir
        self.base = settings.base_dir
        self.num_chapters = settings.num_chapters

    def assemble(self) -> Path:
        """Assemble chapters → manuscript.md in base_dir."""
        parts = ["# The Glass Crown\n\n_A novel in ten chapters._\n"]
        total_words = 0
        
        for n in range(1, self.num_chapters + 1):
            ch_file = self.proj / f"chapter_{n}.md"
            if not ch_file.exists():
                raise FileNotFoundError(f"Missing chapter {n} at {ch_file}")
            text = ch_file.read_text(encoding="utf-8").strip()
            total_words += len(text.split())
            parts.append("\n\n---\n\n" + text)
        
        ms = "\n".join(parts) + "\n"
        out = self.base / "manuscript.md"
        out.write_text(ms, encoding="utf-8")
        print(f"manuscript: {self.num_chapters}/{self.num_chapters} chapters, {total_words} words")
        return out

    def format_official(self) -> Path:
        """Run LibriScribe format_book on manuscript.md → manuscript_official.md."""
        # Monkey-patch typer.confirm for non-interactive runs
        import typer
        typer.confirm = lambda *a, **k: True
        import libriscribe.main as m
        m.typer.confirm = lambda *a, **k: True
        from libriscribe.agents.project_manager import ProjectManagerAgent

        pm = ProjectManagerAgent(llm_client=None)
        pm.load_project_data(self.settings.project_name)
        pkb = pm.project_knowledge_base
        
        # Use writer model for formatting
        pm.initialize_llm_client(self.settings.writer_provider, self.settings.writer_model)
        print(f"format client: {self.settings.writer_provider} / {self.settings.writer_model}")
        
        pm.format_book("manuscript.md")  # reads base/manuscript.md, writes base/manuscript_official.md
        pm.checkpoint()
        
        official = self.base / "manuscript_official.md"
        if not official.exists():
            raise FileNotFoundError("Formatting failed: manuscript_official.md not created")
        
        # Also copy to archive location
        archive = Path.home() / "roman" / "manuscript_official.md"
        archive.parent.mkdir(exist_ok=True)
        import shutil
        shutil.copy2(official, archive)
        print(f"copied to archive: {archive}")
        
        return official

    def make_epub(self) -> Path:
        """Generate EPUB from formatted manuscript."""
        epub_path = generate_epub(self.base, self.settings.project_name, self.num_chapters)
        print(f"EPUB generated: {epub_path}")
        return epub_path

    def make_cover(self) -> Path:
        """Generate cover image."""
        cover_path = generate_cover(self.base, self.settings.project_name)
        print(f"Cover generated: {cover_path}")
        return cover_path


def build_all(settings) -> None:
    """Run complete build pipeline."""
    builder = ManuscriptBuilder(settings)
    builder.assemble()
    builder.format_official()
    builder.make_cover()
    builder.make_epub()
    print("BUILD OK")


if __name__ == "__main__":
    settings = get_settings()
    build_all(settings)