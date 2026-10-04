# Phase 1: Data foundation

Source: `docs/PLAN.md` (Phase 1) and `STEP_BY_STEP.md` (steps 1.1 to 1.7). Planned length: about 2 weeks at 10 hours a week.

## Goal

A clean, versioned, leakage-free SBA loan dataset in Postgres, with tests that fail if anyone breaks it.

## Deliverables

- [ ] Raw Kaggle file `SBAnational.csv` in `data/raw/`, ignored by Git, with its SHA-256 checksum committed in `data/raw/CHECKSUM.txt`.
- [ ] Profiling summary in `docs/DATA.md`: rows, columns, types, missing values, loan status counts, loans per approval year. Generated from a pipeline-written file, not typed by hand.
- [ ] Leakage audit in `docs/DATA.md`: every column labelled `application`, `approval` or `after_outcome`, and confirmed by Dilawar.
- [ ] Target: charged off (`CHGOFF`) vs paid in full (`P I F`) among approved, disbursed loans. Open loans excluded from training, and their count reported.
- [ ] Prediction point: at approval (approved amount and SBA guarantee share allowed), stated in `docs/DATA.md`.
- [ ] Time-based splits by approval fiscal year (train older, validate next, test most recent), with the 2007 to 2010 crisis years flagged as a distribution-shift risk. Years chosen by Dilawar.
- [ ] Pipeline: raw file → checksum → typed staging table → feature table, in Postgres with Alembic migrations.
- [ ] pandera data contracts and a leakage test, running in CI on a committed scrubbed sample.
- [ ] Minimal LLM gateway in `src/creditsense/llm/`: real OpenAI client, mock client, disk cache, one prompt.
- [ ] Synthetic applicant packets built from open loans with templates; the LLM writes only a short business description. Every packet labelled synthetic. 20 saved as golden applications in `tests/golden/`.

## Exit criteria

| Criterion | Proof |
| --- | --- |
| `just data` rebuilds the dataset from the raw file and the checksum matches | `just data` exits 0 on Dilawar's machine; a changed raw file makes it fail |
| Leakage and contract tests pass in CI | `uv run pytest tests/data -k leakage` and the pandera tests are green in GitHub Actions |
| `DATA.md` lists row counts and default rate per split | The table is generated from `artifacts/data/splits.json`, which the pipeline writes |
| Golden applications exist | 20 files in `tests/golden/`, each marked synthetic |

## Locked decisions this phase relies on

From the **Locked decisions** table and rules in `CLAUDE.md`:

- **Data:** Kaggle SBA national dataset. Prediction point at approval. Target `CHGOFF` vs `P I F`. Open loans excluded from training and used as the demo set.
- **No leakage (rule 4):** after-outcome columns are never features. Splits by approval fiscal year, never random. The `leakage-check` skill runs before any feature change.
- **Postgres** holds loans, applications and model metadata (ADR 0004). Schema changes go through Alembic.
- **pandera** for data contracts.
- **LLM:** OpenAI only through `src/creditsense/llm/`, one small model, a hard cap of about $5 a month, mocked LLM in unit tests (ADR 0005).
- **No hand-typed metrics (rule 2):** every number in `DATA.md` comes from a pipeline-written file.
- **Synthetic applicants only (rule 6).**

## Decisions made at kickoff

- **Dataframes:** pandas.
- **Raw data location:** repo-root `data/raw/`, outside the Python package.
- **LLM gateway:** a minimal `llm/` module is built in Phase 1 for the packet descriptions, and reused from Phase 3 on.
- **CI sample:** a scrubbed real slice of a few hundred rows, with business name, street, city and zip removed. It holds real public loan records but no names or addresses.

## Open questions for Dilawar

Asked when their task starts, not decided ahead of time:

1. **Split years** (task 4): Claude proposes cut-offs from the profile; Dilawar decides.
2. **Postgres schema** (task 5): staging and feature tables approved before the first Alembic migration.
3. **Dependencies:** each approved at its task. Expected: pandas (task 2), sqlalchemy, psycopg and alembic (task 5), pandera (task 6), openai (task 7).
4. **Scrubbed slice columns** (task 6): confirm the exact columns dropped and how rows are sampled.
5. **Column labels** (task 3): Dilawar confirms every timing label, especially disbursement fields.

## Tasks (in proposed order, about one session each)

1. `phase-1/raw-data`: raw file in `data/raw/`, checksum write and verify (`src/creditsense/data/checksum.py`), `.gitignore`, justfile recipe, tests.
2. `phase-1/profiling`: profile script writing `artifacts/data/profile.json` and the profile section of `docs/DATA.md`.
3. `phase-1/leakage-audit`: timing label for every column in `docs/DATA.md`, confirmed by Dilawar.
4. `phase-1/splits`: propose cut-off years with counts per year; stop for Dilawar's decision.
5. `phase-1/postgres-pipeline`: Alembic, staging and feature tables, `just migrate`, `just data`, and `artifacts/data/splits.json` with the per-split table in `DATA.md`.
6. `phase-1/contracts`: pandera contracts, leakage test and scrubbed CI fixture, via the `leakage-check` skill.
7. `phase-1/llm-gateway`: minimal `src/creditsense/llm/` with real and mock clients, disk cache and one prompt.
8. `phase-1/packets`: synthetic packets from open loans, and 20 golden applications in `tests/golden/`.
