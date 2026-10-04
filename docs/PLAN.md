# CreditSense v2 Execution Plan (repo copy)

This is the local copy of the plan for Claude Code. The original lives in a Claude Doc that Claude Code cannot open: https://claude.ai/code/artifact/2857b14f-3134-47cd-b2b6-5ca53046cd70. If the two ever disagree, ask Dilawar which one is right, then update this file.

Locked decisions are listed in `CLAUDE.md`. The plain-English task list for each phase is in `STEP_BY_STEP.md`.

## Architecture

```
Analyst UI (Streamlit) ──> FastAPI service (JWT roles, rate limits, request IDs, audit writes)
                                   │
                                   ▼
LangGraph workflow (typed state, checkpointed in Postgres, pauses for the officer)
  Intake → Eligibility → Risk score → Compliance → Memo → Guardrail check → Officer sign-off → Record decision
       │                      │              │          │
       ▼                      ▼              ▼          ▼
 Risk model service      Qdrant          LLM gateway   Postgres
 (scorecard + XGBoost,   (SBA SOP 50 10  (OpenAI,      (loans, decisions, audit log,
  calibrated grades,      + 13 CFR 120    only via      graph checkpoints, MLflow,
  SHAP reason codes)      vectors)        llm/)         model metadata)
```

## Schedule (10 hours a week, approximate)

| Phase | Weeks |
| --- | --- |
| 0 Foundations | 1 |
| 1 Data | 2 |
| 2 Risk model | 3 |
| 3 Compliance RAG | 3 |
| 4 LangGraph workflow (MVP after this, about week 12 to 13) | 3 |
| 5 API, security, audit | 2 |
| 6 Evals and observability | 2 |
| 7 Deploy, demo, case study | 2 |

---

## Phase 0: Product framing and foundations

**Goal:** lock the product scope and the stack before any feature code, so later phases never re-argue them.

**Deliverables**

- `docs/PRODUCT.md`: user (SBA lender credit analyst and credit officer), the job (triage and memo for a 7(a) application), what is out of scope (no automated credit decisions).
- `docs/adr/`: one ADR per Phase 0 decision (LangGraph, Qdrant, Postgres role, OpenAI with the spend cap, $0 hosting, product framing).
- Repo skeleton: uv + Python 3.12, ruff, mypy --strict on core packages, pytest, pre-commit, `.gitattributes`, justfile with the recipes in `CLAUDE.md`.
- `docker-compose.yml` with Postgres, Qdrant and MLflow (Postgres backend), plus `.env.example`.
- GitHub Actions CI running `just check` on every PR.
- `docs/MODEL_RISK.md` stub: intended use, limits, and the rule that the model never makes the final decision.

**Exit criteria**

- CI green on the skeleton.
- `just up` starts Postgres, Qdrant and MLflow.
- Every Phase 0 decision has an ADR.

---

## Phase 1: Data foundation

**Goal:** a clean, versioned, leakage-free SBA loan dataset in Postgres, with tests that fail if anyone breaks it.

**Deliverables**

- Raw Kaggle file (`SBAnational.csv`, about 900k loans, 1987 to 2014) kept out of Git, with its checksum committed.
- Profiling summary in `docs/DATA.md`: rows, columns, types, missing values, loan status counts, loans per approval year.
- Leakage audit in `docs/DATA.md`: every column labelled known at application, at approval, or after outcome. After-outcome columns (charge-off date and amount, outcome-derived balances) are never features, and a test enforces it.
- Target: charged off (`CHGOFF`) vs paid in full (`P I F`) among approved, disbursed loans. Open loans excluded from training; their count reported.
- Prediction point: at approval (approved amount and SBA guarantee share allowed), stated in `DATA.md` and the model card.
- Time-based splits by approval fiscal year (train older, validate next, test most recent). The 2007 to 2010 crisis years are called out as a distribution-shift risk. **The exact years are Dilawar's decision after profiling.**
- Pipeline: raw file → checksum → typed staging tables → feature table, in Postgres with Alembic migrations.
- pandera data contracts run in CI on a fixed sample.
- Synthetic applicant packets built from open loans with templates; the LLM writes only a short business description. Every packet labelled synthetic. 20 of them saved as golden applications in `tests/golden/`.

**Exit criteria**

- `just data` rebuilds the dataset from the raw file and the checksum matches.
- Leakage and contract tests pass in CI.
- `DATA.md` lists row counts and default rate per split.

---

## Phase 2: Credit risk model

**Goal:** a calibrated, explainable default model that beats a simple baseline on the out-of-time test years, documented the way a bank would document it.

**Deliverables**

- Baseline: logistic regression scorecard (binned features, WoE).
- Challenger: XGBoost with monotonic constraints where business logic demands them.
- Overfitting guards: early stopping on the validation year, depth and minimum-child limits, row and column subsampling, and a CI check that fails if the train vs out-of-time PR-AUC gap exceeds the agreed tolerance. LightGBM runs side by side only if the gap stays too wide after tuning; the better out-of-time model wins.
- Probability calibration (isotonic or Platt) and a calibration curve.
- Risk grades A to E from calibrated probability. Clear cases get a recommendation; the middle band is referred to the officer. **Cut-offs are Dilawar's decision.**
- Metrics written by the pipeline to `artifacts/model/metrics.json`: ROC-AUC, PR-AUC, KS, Brier, default rate per grade, on the out-of-time test set.
- SHAP explanations translated into plain reason codes.
- Fairness check on proxies the data allows (region, urban/rural, business size), reported as a limitation since there are no protected attributes.
- PSI stability check between train and test years.
- MLflow tracking (Postgres backend) and model metadata (version, data checksum, metrics) in Postgres.
- `docs/MODEL_CARD.md` using only numbers from the metrics files.

**Exit criteria**

- Challenger beats the baseline on out-of-time PR-AUC and Brier, or the README says it did not.
- Every number in the README links to `metrics.json`.

---

## Phase 3: Compliance RAG

**Goal:** answer "does this application meet SBA 7(a) rules?" with quoted, section-level citations, and measure how often it is right.

**Deliverables**

- Corpus: SBA SOP 50 10 (current version, pinned by effective date) and 13 CFR Part 120, stored with document, version, chapter and section metadata. Superseded versions kept but filtered out by default.
- Structure-aware chunking on the documents' own headings and CFR sections (parent section + child paragraphs); every chunk carries a citable section id.
- Hybrid retrieval in Qdrant: OpenAI small embeddings (dense) + local BM25 (sparse), fused.
- Cross-encoder reranker (small, open source), always on. Fallback if it does not fit the free host's memory: reranking with OpenAI inside the spend cap.
- Answer contract: verdict (meets / does not meet / needs human review), quoted passage, section id. No source found means needs human review, never a guess.
- Eval set: about 100 questions drafted by the LLM, reviewed and corrected by Dilawar, with the review logged.
- Metrics to `artifacts/rag/rag_metrics.json`: recall@k, MRR, citation accuracy, faithfulness, with and without the reranker.

**Exit criteria**

- recall@10 and citation accuracy reported from the eval run.
- CI fails if they drop below the agreed floor.

---

## Phase 4: LangGraph underwriting workflow

**Goal:** one durable, inspectable graph that takes an application from intake to a draft decision and pauses for the credit officer.

**Graph** (typed Pydantic state, Postgres checkpointer, fixed order):

1. **Intake:** validate the packet against a schema. Missing documents mark the application incomplete and refer it to the officer.
2. **Eligibility:** deterministic rules first (size, ineligible industries by NAICS); RAG only to cite the rule.
3. **Risk score:** calls the Phase 2 model service; returns probability, grade and reason codes.
4. **Compliance review:** Phase 3 RAG on the specific issues found; each finding carries its citation.
5. **Memo:** the LLM writes the credit memo only from the state, with a structured output schema.
6. **Guardrail check:** the memo may not state numbers or rules that are not in the state. Failures loop back once, then go to the officer.
7. **Officer sign-off (interrupt):** the graph pauses; the officer approves, declines or overrides with a reason; the graph resumes from the checkpoint.
8. **Record decision:** final state, model version and citations written to the audit log.

One small OpenAI model for every node; a stronger memo model is a config switch, off unless evals show weak memos.

**Deliverables:** the graph, unit tests per node with the mocked LLM, replay of any past run from its checkpoint, and a graph diagram in the README.

**Exit criteria**

- The 20 golden applications run end to end in CI with the mocked LLM.
- A paused run survives a restart and resumes correctly.
- README updated: this is the public MVP.

---

## Phase 5: API, security and audit

**Goal:** a service a bank's security reviewer would not reject on first read.

**Deliverables**

- FastAPI service: submit application, get status, stream graph progress, submit officer decision, fetch memo and audit trail. OpenAPI spec published.
- Self-issued JWT with roles `analyst`, `credit_officer`, `auditor`. Only a credit officer can finalise a decision. An ADR documents where a real identity provider (for example Keycloak) would plug in.
- Append-only audit log in Postgres (no UPDATE or DELETE grants), each row hash-chained to the previous one, plus a script that verifies the chain.
- PII handling: synthetic applicant fields only; redaction before any LLM call; secrets via environment only; gitleaks in CI.
- Rate limiting, request IDs, structured JSON logs, idempotency keys on submit.
- Stretch: MCP server with read-only tools (score, explain, look up a rule) under the same JWT roles. It can never record a decision.

**Exit criteria**

- Role tests prove an analyst cannot finalise.
- The audit chain verifier passes, and catches a hand-edited row in a test.
- bandit, pip-audit and gitleaks are green in CI.

---

## Phase 6: Evals, observability and CI gates

**Goal:** prove the system works and keep it working. Every PR is measured, not just tested.

**Deliverables**

- Langfuse (free cloud tier) tracing of every graph run: node inputs, outputs, latency, tokens, cost. Self-hosting documented as the bank-ready option.
- Three eval suites: model (Phase 2 metrics), retrieval (Phase 3 metrics), end-to-end agent (memo faithfulness, correct verdict, correct citations on the 20 golden applications).
- Real-LLM evals on every PR, with cost guards for the roughly $5/month cap: run only when a PR touches prompts, agent, RAG or model code; small model on a fixed subset (20 golden applications plus a RAG sample); identical calls cached; skip with a visible warning if the cap is reached. Mocked unit tests still run on every PR.
- Full suite with the judge weekly and before releases.
- Faithfulness judge: a stronger OpenAI model used only on eval runs, checked against 30 memos Dilawar labels.
- Regression gates: a PR that lowers any tracked metric beyond its tolerance fails CI.
- Drift check: PSI on input features and score distribution.
- `docs/EVALS.md` generated from the latest run and linked from the README.

**Exit criteria**

- CI shows all three eval suites.
- A deliberately broken retriever makes CI fail.

---

## Phase 7: Deploy, demo and case study

**Goal:** a two-minute video as the main showcase, a private live demo given on request, and a write-up that sells the engineering.

**Deliverables**

- Streamlit analyst UI: application list, run progress, memo with clickable citations, approve / decline with reason, audit trail view.
- Private live demo on free hosting with invite-only logins. The exact free app host, managed Postgres and Qdrant Cloud tier are checked and chosen when this phase starts, and recorded as an ADR.
- Two-minute screen recording of one application from intake to signed decision.
- README that leads with the problem, the architecture diagram, the video, real metrics (each linked to its file) and the limits, plus a "v1 to v2: what changed and why" section.
- Case study (LinkedIn and blog) for a non-technical lending audience.
- Resume and profile lines updated only with numbers from the metrics files.

**Exit criteria**

- An invited client can log in, run the sample application and see the cited memo without help.
- The video shows the same flow end to end.

---

## Open items (Dilawar decides, not Claude Code)

- Train / validation / test cut-off years: proposed after the first profiling run.
- Risk grade cut-offs: proposed from validation data.
- Free host for the demo: chosen when Phase 7 starts.
