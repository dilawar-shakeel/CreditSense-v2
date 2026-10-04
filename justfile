set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    @just --list

# uv sync and install pre-commit hooks
setup:
    uv sync
    uv run pre-commit install

# Postgres, Qdrant and MLflow arrive with docker-compose.yml (Phase 0, docker task)
up:
    @echo "docker-compose.yml does not exist yet"
    @exit 1

down:
    @echo "docker-compose.yml does not exist yet"
    @exit 1

lint:
    uv run ruff check
    uv run ruff format --check

typecheck:
    uv run mypy

test:
    uv run pytest

check: lint typecheck test
