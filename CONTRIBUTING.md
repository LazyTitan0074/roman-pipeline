# Contributing Guide

Thank you for considering contributing to roman-pipeline! This guide will help you get started.

## Code of Conduct

This project follows a simple principle: **be respectful, constructive, and helpful**. We welcome contributions from everyone regardless of experience level.

## Quick Start for Contributors

### 1. Fork & Clone
```bash
git fork https://github.com/LazyTitan0074/roman-pipeline.git
git clone https://github.com/YOUR_USERNAME/roman-pipeline.git
cd roman-pipeline
```

### 2. Set Up Development Environment
```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode with test dependencies
pip install -e .[dev]

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### 3. Run Tests
```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=scripts --cov-report=term-missing

# Specific test file
pytest tests/test_canon_checker.py -v
```

### 4. Code Style
```bash
# Lint with ruff
ruff check scripts/ tests/

# Auto-fix linting issues
ruff check scripts/ tests/ --fix

# Format with ruff
ruff format scripts/ tests/
```

## Project Structure

```
roman-pipeline/
├── scripts/              # Core modules (12 files)
│   ├── cli.py           # Unified CLI entry point
│   ├── config.py        # Centralized configuration
│   ├── canon_checker.py # Canon verification logic
│   ├── capitol_runner.py# Chapter production orchestrator
│   ├── build.py         # Manuscript building
│   ├── make_epub.py     # EPUB generation
│   ├── make_cover.py    # Cover generation
│   ├── sync_all.py      # Project data sync
│   ├── verify.py        # Verification checks
│   ├── logs.py          # Log viewing
│   └── init_project.py  # Project scaffolding
├── templates/           # Project templates (11 files)
├── tests/              # Test suite (80 tests)
├── .github/workflows/  # CI/CD
└── docs/               # Documentation (if any)
```

## Development Guidelines

### Code Style
- **Python 3.11+** (type hints required for public APIs)
- **Line length**: 100 characters (ruff default)
- **Imports**: Standard library → third-party → local (grouped with blank lines)
- **Docstrings**: Google style for public functions/classes
- **Comments**: English only, explain *why* not *what*

### Adding New Features

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first** (TDD preferred):
   - Add test cases in `tests/test_pipeline.py` or new file
   - Run tests to confirm they fail
   - Implement feature
   - Run tests to confirm they pass

3. **Update documentation**:
   - Update relevant template in `templates/` if applicable
   - Update README if CLI changes
   - Add entry to CHANGELOG.md under `[Unreleased]`

4. **Run full test suite**:
   ```bash
   pytest tests/ -v
   ruff check scripts/ tests/
   ```

5. **Submit PR**:
   - Clear title and description
   - Reference any related issues
   - Ensure CI passes

### Testing Guidelines

- **Unit tests** for pure logic (parsing, validation, filtering)
- **Integration tests** for multi-component workflows
- **Mock external APIs** (LLM calls, file I/O) using `monkeypatch`
- **Parametrize** similar test cases (see `test_is_hedge` for examples)
- **Test edge cases**: empty input, malformed data, boundary conditions

### Configuration Changes

When adding new config options:
1. Add field to `Settings` class in `scripts/config.py`
2. Add default value and `alias` for env var
3. Update `.env.example` in root and `templates/.env.example`
4. Update `README.md` configuration table
5. Add validation if required

### Template Changes

Templates use `{{PLACEHOLDER}}` syntax rendered by `init_project.py`:
1. Add placeholder to template file
2. Add mapping to `TEMPLATE_PLACEHOLDERS` in `scripts/init_project.py`
3. Add default value to `context` dict in `create_project()`
4. Test with `python -m scripts.cli init test_project --title "Test Project"`

## Pull Request Checklist

- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Linting passes (`ruff check scripts/ tests/`)
- [ ] New/updated tests for new functionality
- [ ] Documentation updated (README, CHANGELOG, templates)
- [ ] No hardcoded paths or values
- [ ] English comments and docstrings
- [ ] Type hints for public functions
- [ ] Backward compatibility considered

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md with release notes
3. Create git tag: `git tag v0.x.x`
4. Push tag: `git push origin v0.x.x`
5. GitHub Actions will build and publish (when configured)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/LazyTitan0074/roman-pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/LazyTitan0074/roman-pipeline/discussions)
- **Questions**: Open a discussion or issue with the `question` label

## Recognition

Contributors will be acknowledged in:
- CHANGELOG.md for each release
- GitHub contributors page
- README.md (for significant contributions)

Thank you for making roman-pipeline better! 🎉