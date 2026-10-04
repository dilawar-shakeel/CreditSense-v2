# CreditSense v2: Model risk

Status: stub, written in Phase 0. It is filled in as the model (Phase 2), RAG (Phase 3) and workflow (Phase 4) are built. Performance figures are not written here by hand; they come from the files listed under **Evidence**.

## Intended use

CreditSense supports a human credit analyst and credit officer reviewing SBA 7(a) applications. It provides:

- a calibrated default-risk score and an A to E grade, with reason codes
- cited answers to SBA eligibility and compliance questions
- a draft credit memo

The output is decision support. It is an input to the officer's judgement, not a replacement for it.

## Rule: the model never makes the final decision

- Only a user with the `credit_officer` role can finalise a decision.
- No code path, MCP tool or agent node may record a final decision on its own.
- The middle risk band is referred to the officer instead of being graded as pass or fail.
- Missing documents mark the application incomplete and refer it to the officer.
- The officer's decision, and any disagreement with the recommendation, is written to the audit log.

## Out-of-scope uses

- Automated approval or decline of any loan.
- Use on real applicants or real personal data.
- Lending programmes other than SBA 7(a), or loans outside the training period and population.
- Use as legal advice on SBA rules.

## Known limits (to confirm and expand later)

- **Data age and shift.** Training data is historical SBA loan history. Economic conditions and lending practice differ today. Out-of-time evaluation is how this is measured.
- **Prediction point.** Scores are made at approval, using only information available then.
- **Target definition.** Charged off versus paid in full. Open loans are excluded from training, so outcomes for loans still open are unknown.
- **Selection bias.** The data contains only loans that were approved. It says nothing about applicants who were declined.
- **Synthetic applicants.** Demo packets are generated from real loan records with templates, so the demo shows the workflow, not real-world data quality.
- **LLM output.** Memo drafts and rule answers use a language model, which can be wrong. Rule answers must cite a passage, and a guardrail check runs before the officer sees the memo.

## Controls

| Risk | Control | Where |
| --- | --- | --- |
| Target leakage | Features limited to approval-time information; splits by approval fiscal year; `leakage-check` before feature changes | Phase 1, 2 |
| Unsupported compliance claims | Verdict, quoted passage and section id required; no source means `needs_human_review` | Phase 3 |
| Automated decision | Fixed workflow graph with an officer sign-off node; role check on the decision | Phase 4, 5 |
| Tampering or missing history | Append-only, hash-chained audit log; no UPDATE or DELETE path | Phase 5 |
| Hand-typed or stale numbers | Every number comes from a pipeline-written metrics file | All phases |
| Real data exposure | Synthetic applicants only; no secrets or personal data committed | All phases |

## Evidence (written by the pipeline)

To be linked as each phase delivers it:

- Model metrics: `artifacts/**/metrics.json`
- RAG metrics: `rag_metrics.json`
- Combined evals: `EVALS.md`
- Model card: `docs/MODEL_CARD.md` (Phase 2)

## Review

- Owner: Dilawar Shakeel
- Revisit at the end of Phases 2, 3, 4 and before the demo is shared.
