# CreditSense v2: Product

CreditSense is an analyst copilot for US SBA 7(a) small-business lending. It scores default risk, checks an application against SBA rules with cited sources, and drafts a credit memo. **A human credit officer always makes the final decision.**

## Who uses it

| Role | What they do in CreditSense |
| --- | --- |
| `analyst` | Opens an application, reviews the risk grade, the rule checks and the draft memo, and sends it to the officer. |
| `credit_officer` | Reads the analyst's package and records the final decision. The only role that can. |
| `auditor` | Read-only access to the audit log and to how each decision was reached. |

## The job

An SBA lender's analyst spends hours on each 7(a) application: judging risk, checking SBA eligibility rules and writing the credit memo. CreditSense does the first pass of that work.

For each application it:

1. **Triages.** Checks that the application is complete. If documents are missing, it marks the application incomplete and refers it to the officer.
2. **Scores risk.** Gives a calibrated default probability and an A to E grade, with reason codes. The middle band is referred to the officer, not graded as a pass or fail.
3. **Checks the rules.** Answers SBA eligibility and compliance questions against SBA SOP 50 10 and 13 CFR Part 120. Every answer has a verdict, the quoted passage and its section id. If no source is found, the answer is `needs_human_review`.
4. **Drafts the memo.** Writes a credit memo from the score, the rule checks and the application, for the officer to edit.
5. **Waits for the officer.** The workflow pauses until a `credit_officer` records the decision.

## What it does not do

- **No automated credit decisions.** The system recommends, grades and explains. It never approves or declines a loan. No code path, tool or agent step records a final decision on its own.
- **No real applicants.** All applicant packets are template-generated from real loan records and labelled synthetic. No real personal data is stored.
- **No guessing on compliance.** Unsupported rule questions go to a human.
- **Not a production lending system.** It is a portfolio project with a private demo. It has not been validated for use in real lending.
- **Nothing outside SBA 7(a) rules.** The rule corpus is SBA SOP 50 10 and 13 CFR Part 120 only.

## Principles

- **Human decides.** See `docs/MODEL_RISK.md` for the controls.
- **Cited or escalated.** Every compliance claim carries its source, or goes to a human.
- **Auditable.** Inputs, model version, retrieved passages, workflow steps and the human decision are written to an append-only, hash-chained audit log.
- **Measured honestly.** Every published number comes from a file the pipeline writes (`artifacts/**/metrics.json`, `rag_metrics.json`, `EVALS.md`).

## Related docs

- `docs/PLAN.md`: phases, deliverables and exit criteria
- `docs/MODEL_RISK.md`: intended use, limits and controls
- `docs/adr/`: decision records (added in task `phase-0/adrs`)
