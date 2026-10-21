"""Central configuration for roman-pipeline. Single source of truth for paths, keys, models."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource
from pydantic import Field, field_validator
from pydantic_settings import EnvSettingsSource


class ProjectEnvSource(PydanticBaseSettingsSource):
    """Load settings from .env file in the project directory (found by searching)."""
    def __init__(self, settings_cls):
        super().__init__(settings_cls)
        # Skip in test mode
        if os.getenv("ROMAN_PIPELINE_TEST_MODE") == "1":
            self.env_file = None
        else:
            self.env_file = self._find_project_env_file()

    def _find_project_env_file(self) -> Path | None:
        """Find .env file in current dir, parents, or subdirectories."""
        # Check explicit env file from env var
        env_file_path = os.getenv("ROMAN_PIPELINE_ENV_FILE")
        if env_file_path:
            env_file = Path(env_file_path).expanduser().resolve()
            if env_file.exists():
                return env_file
        
        cwd = Path.cwd()
        
        # Check current directory and parents
        for path in [Path.cwd()] + list(Path.cwd().parents):
            env_file = path / ".env"
            if env_file.exists():
                try:
                    content = env_file.read_text(encoding="utf-8")
                    if "PROJECT_NAME" in content or "WRITER_MODEL" in content:
                        return env_file
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
                            return env_file
                    except Exception:
                        pass
        
        return None

    def get_field_value(self, field, field_name):
        if not self.env_file or not self.env_file.exists():
            return None, None, False
        from dotenv import dotenv_values
        env_vars = dotenv_values(self.env_file, encoding="utf-8")
        value = env_vars.get(field_name)
        if value is not None:
            return value, value, True
        return None, None, False

    def prepare_field_value(self, field_name, field, value, value_is_complex):
        return value

    def __call__(self):
        if not self.env_file or not self.env_file.exists():
            return {}
        from dotenv import dotenv_values
        return dotenv_values(self.env_file, encoding="utf-8")


class Settings(BaseSettings):
    # ─── Required paths ───
    base_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("BASE_DIR", "./workspace")).expanduser().resolve(),
        description="Working folder with CANON.md, scripts, logs",
        alias="BASE_DIR",
    )
    proj_dir: Path = Field(
        default_factory=lambda: Path(os.getenv("PROJ_DIR", "./projects/my_novel")).expanduser().resolve(),
        description="LibriScribe project folder (projects/<name>/)",
        alias="PROJ_DIR",
    )

    # ─── Project metadata ───
    project_name: str = Field(default="my_novel", alias="PROJECT_NAME")
    num_chapters: int = Field(default=10, alias="NUM_CHAPTERS")

    # ─── API keys (at least one required for reviewer) ───
    google_ai_studio_api_key: str | None = Field(default=None, alias="GOOGLE_AI_STUDIO_API_KEY")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")

    # ─── Writer model (LibriScribe) ───
    writer_provider: str = Field(default="openrouter", alias="WRITER_PROVIDER")
    writer_model: str = Field(default="nvidia/nemotron-3-ultra-550b-a55b:free", alias="WRITER_MODEL")
    writer_fallback_chain: List[str] = Field(
        default_factory=lambda: [
            "google_ai_studio/gemini-2.5-flash",
            "mistral/ministral-8b-latest",
            "mistral/ministral-3b-latest",
        ],
        alias="WRITER_FALLBACK_CHAIN",
    )

    # ─── Reviewer model (CanonChecker) ───
    reviewer_primary: str = Field(default="gemini-2.5-flash-lite", alias="REVIEWER_PRIMARY")
    reviewer_fallback_chain: List[str] = Field(
        default_factory=lambda: [
            "ollama/qwen2.5:7b",
            "groq/gpt-oss-120b",
            "mistral/ministral-8b-latest",
        ],
        alias="REVIEWER_FALLBACK_CHAIN",
    )

    # ─── Runtime ───
    max_attempts: int = Field(default=4, alias="MAX_ATTEMPTS")

    # ─── Derived paths (computed) ───
    templates_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent / "templates")
    scripts_dir: Path = Field(default_factory=lambda: Path(__file__).parent)

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        # Disable automatic env file loading to avoid JSON parsing of comma-separated values
        env_nested_delimiter="__",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        # Priority: init > env vars > explicit .env file (_env_file) > project .env > file secrets
        sources = (
            init_settings,
            env_settings,
            dotenv_settings,  # Handles _env_file parameter
        )
        if os.getenv("ROMAN_PIPELINE_TEST_MODE") != "1":
            sources += (ProjectEnvSource(settings_cls),)  # Auto-discover project .env
        sources += (file_secret_settings,)
        return sources

    @field_validator("base_dir", "proj_dir", "templates_dir", "scripts_dir", mode="before")
    @classmethod
    def expand_path(cls, v: str | Path) -> Path:
        if isinstance(v, str):
            v = v.strip('"').strip("'")
        return Path(v).expanduser().resolve()

    @field_validator("writer_fallback_chain", "reviewer_fallback_chain", mode="before")
    @classmethod
    def parse_fallback_chain(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    @field_validator("max_attempts", mode="before")
    @classmethod
    def parse_max_attempts(cls, v):
        if isinstance(v, str):
            return int(v)
        return v

    def validate_required(self) -> list[str]:
        """Return list of missing required config. Empty = OK."""
        missing = []
        if not self.base_dir.exists():
            missing.append(f"BASE_DIR does not exist: {self.base_dir}")
        if not self.proj_dir.exists():
            missing.append(f"PROJ_DIR does not exist: {self.proj_dir}")
        keys = [
            self.google_ai_studio_api_key,
            self.groq_api_key,
            self.mistral_api_key,
            self.openrouter_api_key,
        ]
        if not any(k for k in keys if k):
            missing.append(
                "No reviewer API keys set (need at least one of "
                "GOOGLE_AI_STUDIO_API_KEY, GROQ_API_KEY, MISTRAL_API_KEY, OPENROUTER_API_KEY)"
            )
        return missing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached singleton. Call once per process."""
    s = Settings()
    missing = s.validate_required()
    if missing:
        raise RuntimeError("Configuration errors:\n  - " + "\n  - ".join(missing))
    return s


def validate_env_or_die() -> Settings:
    """Call at script entrypoint. Prints errors and exits if invalid."""
    try:
        return get_settings()
    except RuntimeError as e:
        print(f"❌ Configuration error:\n{e}", file=sys.stderr)
        sys.exit(1)


# Back-compat: allow `from config import BASE, PROJ, MAX_ATTEMPTS, PROJECT_NAME, NUM_CHAPTERS`
_BASE = None
_PROJ = None
_MAX_ATTEMPTS = None
_PROJECT_NAME = None
_NUM_CHAPTERS = None

def _ensure_settings():
    global _BASE, _PROJ, _MAX_ATTEMPTS, _PROJECT_NAME, _NUM_CHAPTERS
    if _BASE is None:
        _settings = validate_env_or_die()
        _BASE = _settings.base_dir
        _PROJ = _settings.proj_dir
        _MAX_ATTEMPTS = _settings.max_attempts
        _PROJECT_NAME = _settings.project_name
        _NUM_CHAPTERS = _settings.num_chapters

@property
def BASE():
    _ensure_settings()
    return _BASE

@property
def PROJ():
    _ensure_settings()
    return _PROJ

@property
def MAX_ATTEMPTS():
    _ensure_settings()
    return _MAX_ATTEMPTS

@property
def PROJECT_NAME():
    _ensure_settings()
    return _PROJECT_NAME

@property
def NUM_CHAPTERS():
    _ensure_settings()
    return _NUM_CHAPTERS