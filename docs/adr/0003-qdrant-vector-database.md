# ADR 0003: Qdrant as the vector database

**Status:** Accepted
**Date:** 2026-10-04

## Context

The compliance step retrieves passages from SBA SOP 50 10 and 13 CFR Part 120. Retrieval is hybrid: OpenAI small embeddings plus local BM25, fused, then reranked by a cross-encoder. Constraints: $0 hosting, about $5 a month of LLM spend, about 10 hours a week, fintech audit needs.

## Options considered

- **pgvector in Postgres.** One fewer service, but hybrid search with sparse vectors and fusion would be built by hand, and vectors would share a database with the audit log.
- **Qdrant (chosen).** Runs in Docker Compose, supports dense and sparse vectors and fusion in the database, and has a free self-hosted option.
- **A hosted vector service.** Less to run, but adds an external dependency and a free-tier limit risk.

## Decision

Use Qdrant for all vectors. Never pgvector. Approved by Dilawar Shakeel; listed under Locked decisions in `CLAUDE.md`.

## Consequences

- `docker-compose.yml` runs Qdrant alongside Postgres and MLflow.
- All retrieval code lives in `src/creditsense/rag/`.
- Vectors are not stored in Postgres. Postgres keeps the document and chunk metadata that the audit log refers to (ADR 0004).
- The demo host must be able to run Qdrant, which is considered when the host is chosen in Phase 7 (ADR 0006).
