# Phase 0: Product framing and foundations

Source: `docs/PLAN.md` (Phase 0) and `STEP_BY_STEP.md` (steps 0.1 to 0.7). Planned length: about 1 week at 10 hours a week.

## Goal

Lock the product scope and the stack before any feature code, so later phases never re-argue them.

## Deliverables

- [ ] `docs/PRODUCT.md`: the users (SBA lender credit analyst and credit officer), the job (triage and memo for a 7(a) application), and what is out of scope (no automated credit decisions).
- [ ] `docs/adr/`: one ADR per Phase 0 decision, six in total:
  - [ ] 0001 Product framing: human decides, the copilot only recommends
  - [ ] 0002 LangGraph fixed workflow graph
  - [ ] 0003 Qdrant as the vector database
  - [ ] 0004 Role of Postgres (everything except vectors)
  - [ ] 0005 OpenAI behind `src/creditsense/llm/` with a hard cap of about $5 a month
  - [ ] 0006 $0 hosting on free tiers only
- [ ] Repo skeleton:
  - [ ] uv project on Python 3.12, with the `src/creditsense/` package layout from `CLAUDE.md`
  - [ ] ruff (lint and format) and `mypy --strict` on the core packages
  - [ ] pytest with one smoke test
  - [ ] pre-commit hooks
  - [ ] `.gitattributes` with `* text=auto eol=lf`
  - [ ] justfile with `set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]` and the recipes `setup`, `up`, `down`, `lint`, `typecheck`, `test`, `check`
- [ ] `docker-compose.yml` with Postgres, Qdrant and MLflow (Postgres backend store), plus `.env.example`. `.env` is git-ignored.
- [ ] GitHub Actions workflow that runs `just check` on every PR.
- [ ] `docs/MODEL_RISK.md` stub: intended use, limits, and the rule that the model never makes the final decision.

The recipes `data`, `train`, `eval` and `migrate` belong to later phases. They are not added in Phase 0.

## Exit criteria

| Criterion | Proof |
| --- | --- |
| `just check` passes locally | `just check` exits 0 on Dilawar's Windows machine |
| CI green on the skeleton | Green GitHub Actions check on the CI PR (`.github/workflows/ci.yml`) |
| `just up` starts Postgres, Qdrant and MLflow | `docker compose ps` shows all three running, and the MLflow UI opens in the browser |
| Every Phase 0 decision has an ADR | `docs/adr/0001-*.md` to `docs/adr/0006-*.md` exist, each with status Accepted |
| Product scope written down | `docs/PRODUCT.md` and `docs/MODEL_RISK.md` merged on `main` |

## Locked decisions this phase relies on

From the **Locked decisions** table in `CLAUDE.md`:

- **Orchestration:** LangGraph, fixed workflow graph, no supervisor agent (ADR 0002).
- **Vector database:** Qdrant, never pgvector (ADR 0003).
- **Postgres:** everything except vectors (ADR 0004). It also backs MLflow in `docker-compose.yml`.
- **LLM provider and spend:** OpenAI only through `src/creditsense/llm/`, about $5 a month hard cap, mocked LLM in unit tests (ADR 0005).
- **Hosting:** $0, free tiers only (ADR 0006).
- **Experiment tracking:** MLflow, self-hosted, Postgres backend (compose service).
- **Auth roles:** `analyst`, `credit_officer`, `auditor`. Used in PRODUCT.md and ADR 0001 to say who finalises a decision.
- **Environment and tooling:** native Windows, uv, ruff, mypy --strict, pytest, Docker Desktop.

## Decisions already made at kickoff

- Six ADRs, following `docs/PLAN.md`, including product framing.
- The Phase 0 ADRs record decisions that are already locked, so they ship together in one PR (`phase-0/adrs`) instead of one PR each.
- PRs are opened with the GitHub CLI (`gh`).

## Open questions for Dilawar

These are asked when their task starts, not decided ahead of time:

1. **Skeleton dependencies (task 1):** approve the dev dependencies (ruff, mypy, pytest, pre-commit) and their versions before `uv add --dev`.
2. **Docker image versions (task 2):** approve pinned image tags for Postgres, Qdrant and MLflow. Also approve the Postgres driver the MLflow container needs.
3. **CI runner (task 3):** choose `ubuntu-latest` (faster, free minutes go further) or `windows-latest` (matches the dev machine).

## Tasks (in proposed order, about one session each)

1. `phase-0/skeleton`: uv project, `src/creditsense/` packages, ruff, mypy, pytest, pre-commit, `.gitattributes`, justfile, and the smoke test.
2. `phase-0/docker`: `docker-compose.yml`, `.env.example`, `.gitignore` entry for `.env`, and the `just up` and `just down` recipes.
3. `phase-0/ci`: GitHub Actions workflow with uv and just, running `just check` on every PR.
4. `phase-0/product-docs`: `docs/PRODUCT.md` and the `docs/MODEL_RISK.md` stub.
5. `phase-0/adrs`: ADRs 0001 to 0006, using the `write-adr` skill template.
