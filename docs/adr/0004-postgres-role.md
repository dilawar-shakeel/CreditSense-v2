# ADR 0004: Postgres holds everything except vectors

**Status:** Accepted
**Date:** 2026-10-04

## Context

The system stores loan records, applications, decisions, an append-only audit log, workflow checkpoints, experiment tracking data and model metadata. Constraints: $0 hosting, about 10 hours a week, fintech audit needs.

## Options considered

- **Several stores (SQLite, files, a separate checkpoint store).** Each is simple alone, but there is more to run, back up and keep consistent.
- **One Postgres for all relational and checkpoint data (chosen).** One service, transactions across tables, and the LangGraph checkpointer and MLflow both support it.
- **Postgres for everything including vectors.** Rejected in ADR 0003.

## Decision

Postgres stores loans, applications, decisions, the audit log, LangGraph checkpoints, the MLflow backend and model metadata. Vectors live in Qdrant only. Approved by Dilawar Shakeel; listed under Locked decisions in `CLAUDE.md`.

## Consequences

- `docker-compose.yml` runs Postgres 17 with a `creditsense` database and a separate `mlflow` database.
- Schema changes go through Alembic migrations, and each one needs Dilawar's approval first.
- The audit table is append-only and hash-chained. No UPDATE or DELETE path is added to it.
- Data contracts use pandera before data reaches the tables.
