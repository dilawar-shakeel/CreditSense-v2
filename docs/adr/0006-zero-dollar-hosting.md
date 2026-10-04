# ADR 0006: $0 hosting on free tiers only

**Status:** Accepted
**Date:** 2026-10-04

## Context

This is a portfolio project built at about 10 hours a week, with about $5 a month for LLM spend and no budget for infrastructure. The demo must be reachable by invited reviewers, and the public showcase is a short video.

## Options considered

- **Paid hosting.** Fewer limits, but breaks the budget.
- **Free tiers only (chosen).** Costs nothing, but limits memory, uptime and storage, so the design has to stay small.
- **Run only locally.** Free, but reviewers cannot try it.

## Decision

Everything runs on free tiers. Local development uses Docker Compose for Postgres, Qdrant and MLflow. Langfuse uses its cloud free tier. The demo is private (invite-only logins), and the two-minute video is the public showcase. The exact free host for the demo is chosen when Phase 7 starts and is an open item for Dilawar.

Approved by Dilawar Shakeel; listed under Locked decisions in `CLAUDE.md`.

## Consequences

- Designs favour small models, small indexes and few services.
- Any service that needs a paid plan is a change to this ADR.
- CI runs on GitHub Actions free minutes (`ubuntu-latest`).
- The demo host must be able to run Postgres, Qdrant and the app within free limits. If none can, the demo shrinks, not the budget.
