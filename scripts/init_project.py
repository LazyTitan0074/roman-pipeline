"""Create a new project from templates."""
from __future__ import annotations

import shutil
from pathlib import Path


TEMPLATE_PLACEHOLDERS = {
    "{{PROJECT_NAME}}": "project_name",
    "{{TITLE}}": "title",
    "{{NUM_CHAPTERS}}": "num_chapters",
    "{{GENRE}}": "genre",
    "{{LANGUAGE}}": "language",
    "{{AUTHOR}}": "author",
    "{{WRITER_PROVIDER}}": "writer_provider",
    "{{WRITER_MODEL}}": "writer_model",
    "{{WRITER_FALLBACK_CHAIN}}": "writer_fallback_chain",
    "{{DESCRIPTION}}": "description",
    "{{NUM_CHARACTERS}}": "num_characters",
    "{{TONE}}": "tone",
    "{{INSPIRED_BY}}": "inspired_by",
    "{{VOICE_RULES}}": "voice_rules",
    "{{NAME_GUARD}}": "name_guard",
    "{{SAFETY_RULES}}": "safety_rules",
    "{{CONTENT_SPECIFIC_RULES}}": "content_specific_rules",
    "{{TIMING_GATES}}": "timing_gates",
    "{{ARITHMETIC_RULES}}": "arithmetic_rules",
    "{{PROTAGONIST_NAME}}": "protagonist_name",
    "{{PROTAGONIST_AGE}}": "protagonist_age",
    "{{PROTAGONIST_DESCRIPTION}}": "protagonist_description",
    "{{REVEAL_CHAPTER}}": "reveal_chapter",
    "{{ANTAGONIST_NAME}}": "antagonist_name",
    "{{ANTAGONIST_AGE}}": "antagonist_age",
    "{{ANTAGONIST_ROLE}}": "antagonist_role",
    "{{ANTAGONIST_MOTIVATION}}": "antagonist_motivation",
    "{{SECONDARY_CHARACTER}}": "secondary_character",
    "{{SECONDARY_AGE}}": "secondary_age",
    "{{SECONDARY_DESCRIPTION}}": "secondary_description",
    "{{WORLD_RULE_1}}": "world_rule_1",
    "{{WORLD_RULE_2}}": "world_rule_2",
    "{{CONTENT_GUIDELINES}}": "content_guidelines",
    "{{SPECIFIC_CONTENT_RULE}}": "specific_content_rule",
    "{{TIMELINE_RULE_1}}": "timeline_rule_1",
    "{{TIMELINE_RULE_2}}": "timeline_rule_2",
    # Config fields
    "{{BASE_DIR}}": "base_dir",
    "{{PROJ_DIR}}": "proj_dir",
    "{{GROQ_API_KEY}}": "groq_api_key",
    "{{MISTRAL_API_KEY}}": "mistral_api_key",
    "{{OPENROUTER_API_KEY}}": "openrouter_api_key",
    "{{REVIEWER_PRIMARY}}": "reviewer_primary",
    "{{REVIEWER_FALLBACK_CHAIN}}": "reviewer_fallback_chain",
    "{{MAX_ATTEMPTS}}": "max_attempts",
}


def create_project(name: str, target_dir: Path, title: str, genre: str = "Fantasy", language: str = "English", author: str = "Author Name", num_chapters: int = 10) -> Path:
    """Create a new project from templates."""
    templates_dir = Path(__file__).parent.parent / "templates"
    proj_dir = target_dir / name
    
    if proj_dir.exists():
        raise FileExistsError(f"Project already exists: {proj_dir}")
    
    proj_dir.mkdir(parents=True)
    
    # Create workspace and projects directories
    (proj_dir / "workspace").mkdir(parents=True, exist_ok=True)
    (proj_dir / "projects" / name).mkdir(parents=True, exist_ok=True)
    
    # Context for template rendering
    context = {
        "project_name": name,
        "title": title,
        "num_chapters": str(num_chapters),
        "genre": genre,
        "language": language,
        "author": author,
        "writer_provider": "openrouter",
        "writer_model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "writer_fallback_chain": "google_ai_studio/gemini-2.5-flash, mistral/ministral-8b-latest, mistral/ministral-3b-latest",
        "description": f"A {genre.lower()} novel about {title}.",
        "num_characters": "6",
        "tone": "Serious",
        "inspired_by": "",
        "voice_rules": "# Add character voice rules here\n# Example:\n# PROTAGONIST:\n# - Style: ...\n# - Never says: ...",
        "name_guard": "# Add name guard rules here\n# Example:\n# - Character X: never named Y",
        "safety_rules": "# Add safety rules here\n# Example:\n# - Minors: strictly non-sexual",
        "content_specific_rules": "# Add content-specific canon rules here\n# Example:\n# - Pre-INTIMACY_GATE characters (chX-Y): MUST be young/experienced, rushed/clumsy, NEVER tend to pleasure",
        "timing_gates": "# Add timing gate rules here\n# Example:\n# - CHARACTER_X only from chN. If {ch} >= N, appearance is CORRECT.",
        "arithmetic_rules": "# Add arithmetic timing rules here\n# Example:\n# - If {ch} >= 5, anything allowed 'from ch4 onward' is correct",
        # Config fields
        "base_dir": str((Path.cwd() / name / "workspace").resolve()),
        "proj_dir": str((Path.cwd() / name / "projects" / name).resolve()),
        "groq_api_key": "",
        "mistral_api_key": "",
        "openrouter_api_key": "",
        "reviewer_primary": "gemini-2.5-flash-lite",
        "reviewer_fallback_chain": "ollama/qwen2.5:7b,groq/gpt-oss-120b,mistral/ministral-8b-latest",
        "max_attempts": "4",
        # CANON.md placeholders
        "protagonist_name": "Protagonist",
        "protagonist_age": "20",
        "protagonist_description": "Main character description.",
        "reveal_chapter": "4",
        "antagonist_name": "Antagonist",
        "antagonist_age": "40",
        "antagonist_role": "Villain",
        "antagonist_motivation": "Power and control.",
        "secondary_character": "Secondary Character",
        "secondary_age": "14",
        "secondary_description": "Supporting character description.",
        "world_rule_1": "World rule 1.",
        "world_rule_2": "World rule 2.",
        "content_guidelines": "Explicit content allowed between consenting adults.",
        "specific_content_rule": "Content-specific rule.",
        "timeline_rule_1": "Timeline rule 1.",
        "timeline_rule_2": "Timeline rule 2.",
    }
    
    # Copy and render templates
    for tmpl in templates_dir.glob("*"):
        if tmpl.name == "__pycache__":
            continue
        
        if tmpl.is_dir():
            shutil.copytree(tmpl, proj_dir / tmpl.name)
            continue
        
        # Determine destination name
        if tmpl.name == ".env.example":
            dst_name = ".env"
        else:
            dst_name = tmpl.name
        
        dst = proj_dir / dst_name
        
        if tmpl.suffix in (".md", ".json", ".yaml", ".yml", ".txt", ".example"):
            # Text file - render placeholders
            content = tmpl.read_text(encoding="utf-8")
            for placeholder, ctx_key in TEMPLATE_PLACEHOLDERS.items():
                content = content.replace(placeholder, context[ctx_key])
            dst.write_text(content, encoding="utf-8")
        else:
            # Binary - copy as-is
            shutil.copy2(tmpl, dst)
    
    # Create chapters folder
    (proj_dir / "chapters").mkdir(exist_ok=True)
    
    print(f"✅ Project created: {proj_dir}")
    print(f"📝 Next steps:")
    print(f"  1. Edit {proj_dir / '.env'} with your API keys")
    print(f"  2. Fill in CANON.md, BEAT_SHEET.md, VOICE.md")
    print(f"  3. Edit characters.json, world.json, outline.md")
    print(f"  4. Run: roman-pipeline chapter 1")
    
    return proj_dir


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python init_project.py <project_name> [target_dir]")
        sys.exit(1)
    
    name = sys.argv[1]
    target = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(".")
    create_project(name, target, name.replace("_", " ").title())