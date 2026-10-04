# CreditSense v2: Step-by-Step Guide

This is the whole project broken into small steps you can finish one at a time. Each step says **what to do** and **how you know it's done**. Do them in order. At 10 hours a week the full project takes about 18 weeks.

**How to use this file**

- Work on one step at a time. Tick the box when its "Done when" is true.
- Most steps can be done with Claude Code. Where it helps, a ready-to-paste prompt is given.
- Every step ends with a pull request (PR) into `main`. Never commit to `main` directly.
- If Claude Code asks you a question (new dependency, database change, a locked decision), answer it before it continues. That is by design.

---

## Phase 0: Set up the foundation (about 1 week)

The goal: an empty but professional project that builds, tests and runs its databases with one command.

### 0.1 Install your tools on Windows

- [ ] Install **Git**, **Docker Desktop**, **uv** and **just**. In PowerShell, `winget install astral-sh.uv` and `winget install Casey.Just` should work; if not, use the install page of each tool.
- [ ] Install **Claude Code** if it is not already installed.
- [ ] Open Docker Desktop once so it finishes setup.

**Done when:** `git --version`, `docker --version`, `uv --version` and `just --version` all print a version in PowerShell.

### 0.2 Create the GitHub repo

- [ ] On GitHub, create a new **empty** repo called `creditsense-v2` (public, no README).
- [ ] Clone it to your computer.
- [ ] Copy `CLAUDE.md`, `STEP_BY_STEP.md`, the `.claude` folder and the `docs` folder (it holds `PLAN.md`) from this project into the repo root.
- [ ] Commit them on a branch `phase-0/claude-setup` and open a PR. Merge it.

**Done when:** the repo on GitHub shows `CLAUDE.md`, `STEP_BY_STEP.md`, `docs/PLAN.md` and `.claude/skills/` on `main`.

### 0.3 Kick off Phase 0 with Claude Code

- [ ] Open Claude Code in the repo folder and paste:
  > Use the phase-kickoff skill for Phase 0.
- [ ] Read the phase doc it writes. Answer any questions it asks.
- [ ] Review and merge the kickoff PR.

**Done when:** `docs/phases/phase-0.md` is on `main` with a task list.

### 0.4 Build the project skeleton

- [ ] Ask Claude Code:
  > Create the Python project skeleton from CLAUDE.md: uv with Python 3.12, the src/creditsense layout, ruff, mypy, pytest, pre-commit, .gitattributes and a justfile with the recipes listed in CLAUDE.md.
- [ ] Approve the dependencies it asks about.
- [ ] Run `just setup` then `just check`.

**Done when:** `just check` passes on your machine.

### 0.5 Start the databases with Docker

- [ ] Ask Claude Code for a `docker-compose.yml` with Postgres, Qdrant and MLflow (MLflow stores its data in Postgres), plus a `.env.example` file.
- [ ] Copy `.env.example` to `.env` and fill in passwords. Never commit `.env`.
- [ ] Run `just up`.

**Done when:** Postgres, Qdrant and MLflow are all running in Docker Desktop, and the MLflow page opens in your browser.

### 0.6 Turn on CI

- [ ] Ask Claude Code for a GitHub Actions workflow that runs `just check` on every PR.
- [ ] Open a PR and watch it go green.

**Done when:** the PR shows a green check from GitHub Actions.

### 0.7 Write the product docs and decision records

- [ ] Ask Claude Code to write `docs/PRODUCT.md` (who uses it, what it does, what it does not do) and `docs/MODEL_RISK.md` (intended use, limits, human makes the final decision).
- [ ] Ask it to use the write-adr skill to record each Phase 0 decision: LangGraph, Qdrant, Postgres role, OpenAI with the $5 cap, $0 hosting.
- [ ] Read them and fix anything that sounds wrong.

**Done when:** `docs/adr/` has one file per Phase 0 decision and all of Phase 0's exit criteria are ticked.

---

## Phase 1: Get the data right (about 2 weeks)

The goal: a clean, tested SBA loan dataset in Postgres that cannot leak the answer into the model.

### 1.1 Download the data

- [ ] On Kaggle, find the SBA national loan dataset ("Should This Loan be Approved or Denied?", file `SBAnational.csv`, about 900k rows).
- [ ] Save it to `data/raw/` in the repo. Make sure `data/raw/` is in `.gitignore` (the file is too big for Git).
- [ ] Ask Claude Code to write a script that records the file's checksum in `data/raw/CHECKSUM.txt` (this small file is committed).

**Done when:** the CSV is on disk, ignored by Git, and its checksum is committed.

### 1.2 Look at the data before using it

- [ ] Ask Claude Code:
  > Profile SBAnational.csv: row count, columns and types, missing values, the loan status values and their counts, and loans per approval year. Write the summary to docs/DATA.md. Do not change any data.
- [ ] Read `docs/DATA.md`. Note anything strange.

**Done when:** you can say how many loans there are, how many were charged off, and which years have the most loans.

### 1.3 Label every column (the leakage audit)

- [ ] Ask Claude Code to add a table to `docs/DATA.md` that labels every column as known **at application**, **at approval**, or **after the outcome**.
- [ ] Check every label yourself. Anything about charge-offs or final balances is "after the outcome" and can never be a feature.

**Done when:** every column has a label you agree with.

### 1.4 Choose the train / validation / test years

- [ ] Ask Claude Code to propose cut-off years based on the profile (older years for training, the next for validation, the most recent for testing), and to point out the 2007 to 2010 crisis years.
- [ ] Decide the years yourself and tell Claude Code. This is your decision, not Claude's.

**Done when:** the years are written in `docs/DATA.md` and the plan doc's "Split years" row says Locked.

### 1.5 Load the data into Postgres

- [ ] Ask Claude Code to build the pipeline: raw CSV → typed staging table → feature table, using Alembic migrations. Approve the schema when it asks.
- [ ] Run `just migrate` then `just data`.

**Done when:** `just data` rebuilds everything from the raw file, and the checksum matches.

### 1.6 Add data tests

- [ ] Ask Claude Code to use the leakage-check skill and add pandera data contracts plus a test that fails if any "after the outcome" column becomes a feature.
- [ ] Run `just test`.

**Done when:** the leakage and contract tests pass in CI.

### 1.7 Build the demo applicant packets

- [ ] Ask Claude Code to generate applicant packets from the **open** loans (the ones without an outcome), using templates, with the LLM writing only a short business description. Every packet is labelled synthetic.
- [ ] Pick 20 of them as the "golden applications" for later tests and save them in `tests/golden/`.

**Done when:** you can open a packet and it clearly says it is synthetic, and 20 golden packets are committed.

---

## Phase 2: Build the risk model (about 3 weeks)

The goal: a model that predicts default, beats a simple baseline, and explains itself.

### 2.1 Build the simple baseline (scorecard)

- [ ] Ask Claude Code to build a logistic regression scorecard on the training years and log it to MLflow.
- [ ] Look at the results in MLflow.

**Done when:** the baseline's metrics are in `metrics.json` and MLflow.

### 2.2 Build the XGBoost model

- [ ] Ask Claude Code to train XGBoost with the overfitting guards from CLAUDE.md (early stopping on the validation year, depth limits, sampling).
- [ ] Compare it with the baseline on the **test years** (out-of-time).

**Done when:** both models' out-of-time numbers are in `metrics.json`.

### 2.3 Check for overfitting

- [ ] Ask Claude Code to add the CI check that fails if the gap between training and out-of-time PR-AUC is too big. Agree the tolerance together.
- [ ] If the gap stays too big after tuning, ask Claude Code to train LightGBM side by side and keep the better one.

**Done when:** the overfitting check passes in CI.

### 2.4 Calibrate and create risk grades

- [ ] Ask Claude Code to calibrate the probabilities and map them to grades A to E.
- [ ] Ask it to propose which grades are "clear" and which middle band goes to the officer. Decide the cut-offs yourself.

**Done when:** every loan in the test set gets a grade, and the default rate rises from A to E.

### 2.5 Add explanations

- [ ] Ask Claude Code to add SHAP explanations and turn the top factors into plain reason codes (for example "low SBA guarantee share").

**Done when:** for any test loan you can see its grade and its top 3 reasons in plain words.

### 2.6 Write the model card

- [ ] Ask Claude Code to write `docs/MODEL_CARD.md` using only numbers from `metrics.json`, including limitations and the fairness check on region, urban/rural and business size.
- [ ] Use the run-evals skill to confirm every number matches the files.

**Done when:** the model card is merged and every number links to a metrics file.

---

## Phase 3: Build the SBA rules search (RAG) (about 3 weeks)

The goal: ask "does this application meet SBA rules?" and get an answer with the exact rule quoted.

### 3.1 Collect the rule documents

- [ ] Download the current **SBA SOP 50 10** from sba.gov and **13 CFR Part 120** from ecfr.gov.
- [ ] Save them in `data/corpus/` with their version or effective date in the file name.

**Done when:** both documents are saved and their versions are written down.

### 3.2 Split the documents by section

- [ ] Ask Claude Code to split them along their own headings and sections, so every chunk carries its section id (for example "13 CFR 120.110").

**Done when:** you can pick any chunk and see which section it came from.

### 3.3 Load them into Qdrant

- [ ] Ask Claude Code to create OpenAI small embeddings plus BM25 keyword vectors and load both into Qdrant with the section metadata.

**Done when:** a test search for "ineligible businesses" returns the right section near the top.

### 3.4 Add the reranker

- [ ] Ask Claude Code to add the small open-source cross-encoder reranker (always on).
- [ ] If it does not fit in memory later on the free host, the fallback is reranking with OpenAI inside the cap.

**Done when:** searches go through the reranker and the results still make sense.

### 3.5 Make answers cite their source

- [ ] Ask Claude Code to make every answer return: a verdict (meets / does not meet / needs human review), the quoted text, and the section id. No source means "needs human review".

**Done when:** you ask 5 test questions and every answer has a quote and a section id.

### 3.6 Build the test questions

- [ ] Ask Claude Code to draft about 100 questions from the documents, each with the correct section id.
- [ ] **Review every question yourself** and fix wrong ones. Keep a note of what you changed.

**Done when:** the reviewed question set and your review log are committed.

### 3.7 Measure retrieval quality

- [ ] Ask Claude Code to use the run-evals skill to measure recall@10, citation accuracy and faithfulness, with and without the reranker.
- [ ] Agree a minimum score with Claude Code and add it to CI.

**Done when:** `rag_metrics.json` exists and CI fails if quality drops below the minimum.

---

## Phase 4: Build the LangGraph workflow (about 3 weeks)

The goal: one workflow that takes an application from intake to a draft decision and stops for the credit officer.

### 4.1 Define the workflow state

- [ ] Ask Claude Code to define the typed state (all the data that moves between steps) using the langgraph-node skill.

**Done when:** the state model exists and has tests.

### 4.2 Build the steps one by one

Do one PR per step. For each, ask Claude Code: "Use the langgraph-node skill to build the <name> step."

- [ ] **Intake:** checks the packet; missing documents mark it incomplete and send it to the officer.
- [ ] **Eligibility:** fixed rules first, then the rules search to cite them.
- [ ] **Risk score:** calls the Phase 2 model.
- [ ] **Compliance:** calls the Phase 3 search for each issue found.
- [ ] **Memo:** the LLM writes the credit memo only from what is in the state.
- [ ] **Guardrail check:** blocks any number or rule in the memo that is not in the state.

**Done when:** each step has its own tests passing with the mocked LLM.

### 4.3 Add the officer pause

- [ ] Ask Claude Code to add the officer sign-off pause (approve, decline or override with a reason), saved in Postgres so it survives a restart.
- [ ] Test it: start a run, stop the app, start it again, and finish the run.

**Done when:** a paused run resumes correctly after a restart.

### 4.4 Run the 20 golden applications

- [ ] Ask Claude Code to run all 20 golden applications end to end in CI with the mocked LLM.

**Done when:** all 20 pass in CI.

### 4.5 Publish the MVP

- [ ] Ask Claude Code to update the README with what it does, the workflow diagram, the real metrics (linked to their files) and the limitations.
- [ ] Record a rough screen video of one application going through the workflow.

**Done when:** the README is merged. **You now have an MVP you can show clients (around week 12 to 13).**

---

## Phase 5: Add the API, security and audit log (about 2 weeks)

The goal: a service a bank's security reviewer would take seriously.

### 5.1 Build the API

- [ ] Ask Claude Code to build the FastAPI service: submit an application, check its status, see progress, submit the officer decision, and fetch the memo and audit trail.

**Done when:** the API docs page opens and every route works in a test.

### 5.2 Add login and roles

- [ ] Ask Claude Code to add JWT login with three roles: analyst, credit officer, auditor. Ask for an ADR saying where a real login provider would plug in.
- [ ] Ask for a test proving an analyst **cannot** finalise a decision.

**Done when:** the role tests pass.

### 5.3 Add the tamper-proof audit log

- [ ] Ask Claude Code to build the append-only, hash-chained audit log in Postgres and a script that verifies the chain. Approve the schema change.
- [ ] Try editing a row by hand in a test database and run the verifier.

**Done when:** the verifier catches your edit.

### 5.4 Add the security basics

- [ ] Ask Claude Code to add rate limiting, request IDs, structured logs, and the security scans (bandit, pip-audit, gitleaks) to CI.

**Done when:** the security scans are green in CI.

### 5.5 Add the MCP server (stretch goal)

- [ ] If you have time, ask Claude Code to expose read-only MCP tools (score, explain, look up a rule) using the same login roles.

**Done when:** an MCP client can score a loan but cannot record a decision.

---

## Phase 6: Measure everything (about 2 weeks)

The goal: every PR shows whether the system got better or worse.

### 6.1 Turn on tracing

- [ ] Create a free Langfuse cloud account and add its keys to `.env` and to GitHub secrets.
- [ ] Ask Claude Code to trace every workflow run (steps, time, tokens, cost).

**Done when:** you can open Langfuse and see a full run step by step.

### 6.2 Set up the OpenAI spend guard

- [ ] In your OpenAI account, set a **hard monthly limit of about $5**.
- [ ] Add your OpenAI key to GitHub secrets.

**Done when:** the limit shows in your OpenAI billing settings.

### 6.3 Run real-LLM tests on every PR

- [ ] Ask Claude Code to add the real-LLM test job with the guards in CLAUDE.md: runs only when prompts, agent, RAG or model code change; uses the small model on the 20 golden applications plus a sample of rule questions; caches repeat calls; skips with a warning if the cap is reached.

**Done when:** a PR that changes a prompt runs the job, and a PR that only changes docs does not.

### 6.4 Add the memo judge

- [ ] Label 30 memos yourself as faithful or not.
- [ ] Ask Claude Code to add the stronger-model judge for eval runs and check how often it agrees with your 30 labels.

**Done when:** the judge's agreement with your labels is reported in `EVALS.md`.

### 6.5 Weekly full run and drift check

- [ ] Ask Claude Code for a weekly scheduled job that runs the full test suite with the judge, plus a drift check on the input data.
- [ ] Ask it to regenerate `EVALS.md` from the run.

**Done when:** `EVALS.md` updates automatically, and breaking the retriever on purpose makes CI fail.

---

## Phase 7: Deploy, demo and tell the story (about 2 weeks)

The goal: a private demo you can show on request, a 2-minute video, and a case study that wins clients.

### 7.1 Build the Streamlit app

- [ ] Ask Claude Code to build the Streamlit app: application list, run progress, memo with clickable citations, approve / decline with a reason, and audit trail view.

**Done when:** you can process one application start to finish in the app on your computer.

### 7.2 Choose the free hosting

- [ ] Ask Claude Code to check the current free tiers (app host, managed Postgres, Qdrant Cloud) and recommend a setup. Decide together.

**Done when:** the hosting choice is recorded as an ADR.

### 7.3 Deploy the private demo

- [ ] Deploy the app with invite-only logins. Do not make it open to everyone.
- [ ] Create one test login and try it from another device.

**Done when:** an invited login can run the sample application and see the cited memo.

### 7.4 Record the 2-minute video

- [ ] Show one application going from intake to the officer's signed decision, pointing out the citations and the audit trail.
- [ ] Upload it (YouTube unlisted or Loom) and link it in the README.

**Done when:** the video link is in the README.

### 7.5 Polish the README

- [ ] Lead with the problem, then the architecture diagram, the video, the real metrics (each linked to its file) and the limits.
- [ ] Add a short "v1 to v2: what changed and why" section linking to the old repo.

**Done when:** a stranger can understand the project in 2 minutes from the README.

### 7.6 Write the case study and update your profiles

- [ ] Write a LinkedIn post and a blog-style case study for a non-technical lending audience.
- [ ] Update your resume and GitHub profile **only with numbers from the metrics files**.
- [ ] Pin `creditsense-v2` on your GitHub profile.

**Done when:** the post is live and every number on your resume matches a metrics file.

---

## Quick reference: the rules that never change

1. The credit officer makes every final decision.
2. No metric is typed by hand; numbers come from the metrics files.
3. Every rule-based answer quotes its source.
4. No data from after the loan outcome is ever used as a feature.
5. Everything is logged in the tamper-proof audit log.
6. Applicants are synthetic; no real personal data, no secrets in Git.
