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

# Record the SHA-256 checksum of data/raw/SBAnational.csv (run after downloading)
checksum:
    uv run python -m creditsense.data.checksum write

# Fail if data/raw/SBAnational.csv does not match data/raw/CHECKSUM.txt
verify-data:
    uv run python -m creditsense.data.checksum verify

# Profile the raw file into artifacts/data/profile.json and docs/DATA.md
profile: verify-data
    uv run python -m creditsense.data.profile
