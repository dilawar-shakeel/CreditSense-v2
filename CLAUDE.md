# CreditSense v2

Analyst copilot for US SBA 7(a) small-business lending. It scores default risk on real SBA loan history, checks each application against SBA rules with cited sources, and drafts a credit memo. **A human credit officer always makes the final decision.**

Full plan for every phase (goals, deliverables, exit criteria): `docs/PLAN.md`. Plain-English task list: `STEP_BY_STEP.md`. Always read these local files; the original plan is a Claude Doc you cannot open.
v1 (synthetic Pakistan/SBP data) lives at github.com/dilawar-shakeel/Creditsense and stays as the predecessor. Do not copy its metrics.

## Non-negotiable rules

1. **Human decides.** Code may recommend, grade and explain. Only a user with the `credit_officer` role can finalise a decision. No code path, MCP tool or agent node may record a final decision on its own.
2. **No hand-typed metrics.** Every number in README, docs, model card or resume text must come from a file the pipeline writes (`artifacts/**/metrics.json`, `rag_metrics.json`, `EVALS.md`). If a number is not in a metrics file, do not write it.
3. **Every compliance claim is cited.** RAG answers return a verdict, the quoted passage and its section id. No source found means `needs_human_review`, never a guess.
4. **No leakage.** Columns known only after the loan outcome are never features. Splits are by approval fiscal year, never random. Run the `leakage-check` skill before any feature change.
5. **Everything is auditable.** Inputs, model version, retrieved passages, graph steps and the human decision go to the audit log. The audit table is append-only and hash-chained; never add UPDATE or DELETE paths to it.
6. **Synthetic applicants only.** Applicant packets are template-generated from real loan records and labelled synthetic. Never commit real personal data or secrets.

## Ask before you do any of these

Stop and ask Dilawar first. Do not proceed on your own judgement.

- Adding, removing or upgrading any dependency (`uv add`, `uv remove`, version bumps).
- Changing the database schema (any new Alembic migration, or editing an existing one).
- Changing anything listed under **Locked decisions** below. If a task seems to need it, explain why and propose an ADR with the `write-adr` skill.

Everything else (code, tests, docs, refactors inside the task's scope) you may do freely.

## Locked decisions (do not re-argue)

| Area | Decision |
| --- | --- |
| Orchestration | LangGraph, fixed workflow graph. The LLM works only inside nodes; no supervisor agent choosing tools. |
| State and checkpoints | LangGraph Postgres checkpointer. A paused run must survive a restart. |
| Vector database | Qdrant. Never pgvector. |
| Postgres | Everything except vectors: loans, applications, decisions, audit log, checkpoints, MLflow backend, model metadata. |
| LLM provider | OpenAI, only through `src/creditsense/llm/`. No other module imports the `openai` SDK. One small model for every node; a stronger memo model is a config switch, off by default. |
| LLM spend | Hard monthly cap of about $5 on the OpenAI account. Unit tests always use the mocked LLM. |
| Data | Kaggle SBA national dataset (about 900k loans, 1987 to 2014). Prediction point is **at approval**. Target is charged off (`CHGOFF`) vs paid in full (`P I F`). Open loans are excluded from training and used as the demo set. |
| Model | Logistic regression scorecard baseline plus XGBoost challenger, calibrated. A to E grades; the middle band is referred to the officer. LightGBM only as a side-by-side if the train vs out-of-time gap stays too wide after tuning. |
| Experiment tracking | MLflow, self-hosted, Postgres backend. |
| RAG | Corpus is SBA SOP 50 10 and 13 CFR Part 120 only. OpenAI small embeddings plus local BM25, fused in Qdrant. Cross-encoder reranker always on. Eval set is about 100 LLM-drafted questions reviewed by Dilawar. |
| Missing documents | Mark the application incomplete and refer it to the officer. Do not pause and request documents. |
| Auth | Self-issued JWT with roles `analyst`, `credit_officer`, `auditor`. |
| MCP server | Phase 5 stretch. Read-only tools only (score, explain, look up a rule). |
| Tracing | Langfuse cloud free tier. |
| Evals in CI | Mocked unit tests on every PR. Real-LLM evals on every PR that touches prompts, agent, RAG or model code, on a fixed subset, with caching; full suite with the judge weekly and before releases. If the spend cap is hit, skip with a visible warning. |
| UI and demo | Streamlit. Demo is private (invite-only logins); the two-minute video is the public showcase. |
| Hosting | $0, free tiers only. |

## Environment: Windows (native)

- Dilawar works on **native Windows** (not WSL). Write commands that work in PowerShell.
- Use `pathlib.Path` for every path; never hard-code `/` or `\` separators.
- The `justfile` must set `set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]`.
- Postgres, Qdrant and MLflow run in Docker Desktop via `docker compose`.
- Keep `.gitattributes` with `* text=auto eol=lf` so line endings stay consistent.
- Open text files with `encoding="utf-8"` explicitly.

## Tooling

- Python 3.12, managed with **uv** (`uv sync`, `uv run`). Never use `pip install` directly.
- Lint and format: `ruff`. Types: `mypy --strict` on `src/creditsense/` core packages. Tests: `pytest`.
- Database migrations: Alembic.
- Data contracts: `pandera`.

## Commands (recipes created in Phase 0)

| Command | What it does |
| --- | --- |
| `just setup` | `uv sync` and install pre-commit hooks |
| `just up` / `just down` | Start or stop Postgres, Qdrant and MLflow with Docker Compose |
| `just lint` | `ruff check` and `ruff format --check` |
| `just typecheck` | `mypy --strict` on core packages |
| `just test` | Unit tests with the mocked LLM |
| `just check` | lint + typecheck + test; run this before every commit |
| `just data` | Rebuild the dataset from the raw file and verify its checksum |
| `just train` | Train baseline and challenger, write `metrics.json`, log to MLflow |
| `just eval` | Run model, RAG and agent evals and regenerate `EVALS.md` |
| `just migrate` | Apply Alembic migrations |

If a recipe does not exist yet, say so instead of inventing a different command.

## Repo layout

```
src/creditsense/
  data/      ingestion, staging, features, pandera contracts
  model/     scorecard, XGBoost challenger, calibration, grades, SHAP reason codes
  rag/       corpus loading, chunking, Qdrant indexing, retrieval, reranker
  graph/     LangGraph state, nodes, edges, checkpointer wiring
  llm/       the only OpenAI client; prompts; mock client for tests
  api/       FastAPI app, auth, routes
  audit/     hash-chained audit log writer and verifier
  ui/        Streamlit app
tests/       mirrors src/ ; tests/golden/ holds the 20 golden applications
docs/        PLAN.md, PRODUCT.md, DATA.md, MODEL_CARD.md, MODEL_RISK.md, EVALS.md, adr/, phases/
artifacts/   pipeline outputs (metrics files, model bundles); never edit by hand
```

## Git workflow

- Never commit to `main`. One feature branch and one PR per task: `phase-<n>/<short-topic>`, for example `phase-1/leakage-audit`.
- Conventional commit messages: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`.
- Run `just check` before every commit. Do not push if it fails.
- PR description: what changed, how it was tested, and which phase exit criterion it moves.

## How to work on a task

1. Use the `phase-kickoff` skill when starting a new phase.
2. Read the relevant section of `docs/` before changing a module.
3. Write or update tests in the same change. New graph nodes follow the `langgraph-node` skill.
4. Feature or split changes go through the `leakage-check` skill.
5. Any metric change goes through the `run-evals` skill.
6. A change to a locked decision needs Dilawar's approval and an ADR (`write-adr` skill).

## Open items (do not decide these yourself)

- Exact train / validation / test cut-off years: propose after the first data profiling run, then wait for Dilawar.
- Exact free host for the demo: chosen when Phase 7 starts.
