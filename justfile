set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

default:
    @just --list

# uv sync and install pre-commit hooks
setup:
    uv sync
    uv run pre-commit install

# Start Postgres, Qdrant and MLflow
up:
    docker compose up -d --build

# Stop the stack (data volumes are kept)
down:
    docker compose down

lint:
    uv run ruff check
    uv run ruff format --check

typecheck:
    uv run mypy

test:
    uv run pytest

check: lint typecheck test
