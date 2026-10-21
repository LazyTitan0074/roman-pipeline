# roman-pipeline Makefile
# Common development tasks

.PHONY: help install test lint format check clean build docs

# Default target
help:
	@echo "roman-pipeline Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install package in development mode with dev deps"
	@echo "  make install-ci    Install for CI (no editable)"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests with verbose output"
	@echo "  make test-cov      Run tests with coverage report"
	@echo "  make test-quick    Run tests without coverage (fast)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          Run ruff linter"
	@echo "  make format        Auto-format code with ruff"
	@echo "  make check         Run all checks (lint + test)"
	@echo ""
	@echo "Pre-commit:"
	@echo "  make precommit     Install pre-commit hooks"
	@echo "  make run-hooks     Run all pre-commit hooks manually"
	@echo ""
	@echo "Build/Package:"
	@echo "  make build         Build wheel and sdist"
	@echo "  make clean         Clean build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  make dev-setup     Full development setup (install + pre-commit)"
	@echo "  make demo          Create demo project and show structure"

# Installation
install:
	pip install -e .[dev]

install-ci:
	pip install .[dev]

# Testing
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=scripts --cov-report=term-missing --cov-report=html

test-quick:
	pytest tests/ -q

# Code Quality
lint:
	ruff check scripts/ tests/

format:
	ruff format scripts/ tests/
	ruff check scripts/ tests/ --fix

check: lint test

# Pre-commit
precommit:
	pip install pre-commit
	pre-commit install

run-hooks:
	pre-commit run --all-files

# Build
build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

# Development
dev-setup: install precommit
	@echo "Development environment ready!"

demo:
	@echo "Creating demo project..."
	@rm -rf demo_project
	@python -m scripts.cli init demo_project --title "Demo Novel" --genre Fantasy
	@echo ""
	@echo "Demo project created at ./demo_project"
	@echo "Structure:"
	@tree demo_project -a -I '__pycache__' 2>/dev/null || find demo_project -type f | head -20

# Version
version:
	@python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"

# Release preparation
release-check:
	@echo "Checking release readiness..."
	@make check
	@make clean
	@make build
	@echo "Release ready! Don't forget to:"
	@echo "  1. Update CHANGELOG.md"
	@echo "  2. Update version in pyproject.toml"
	@echo "  3. git tag vX.Y.Z"
	@echo "  4. git push origin vX.Y.Z"