---
name: run-evals
description: Run CreditSense v2 model, RAG and agent evals and update metrics files and EVALS.md. Use for any task that changes or reports a metric.
---

# Run evals and update metrics

Numbers in this project come only from files the pipeline writes. Never type a metric by hand anywhere (README, docs, model card, PR text, resume lines).

## Steps

1. Make sure `just up` is running (Postgres, Qdrant, MLflow) and `OPENAI_API_KEY` is set in the environment, never in a file in the repo.
2. Pick the scope:
   - Model change: `just train`, then `just eval`.
   - RAG or prompt change: `just eval`.
   - Real-LLM runs cost money. Use the fixed subset (20 golden applications plus the RAG sample) unless this is the weekly or pre-release run. If the spend cap is reached, stop and tell Dilawar.
3. Read the outputs, not your memory:
   - Model: `artifacts/model/metrics.json` (ROC-AUC, PR-AUC, KS, Brier, default rate per grade, train vs out-of-time gap).
   - RAG: `artifacts/rag/rag_metrics.json` (recall@k, MRR, citation accuracy, faithfulness, with and without reranker).
   - Agent: golden-application results (verdict, citations, memo faithfulness).
4. Compare with `main`. If any tracked metric drops beyond its tolerance, the change fails: report it plainly with both numbers. Do not tune thresholds or tolerances to make it pass.
5. Check the overfitting gate: if the train vs out-of-time PR-AUC gap is above tolerance, report it. LightGBM is run side by side only after tuning XGBoost fails to close the gap.
6. Regenerate `docs/EVALS.md` from the run (the command writes it). Commit the metrics files and `EVALS.md` together with the code change.
7. If the README quotes a metric, it must link to the metrics file it came from.

## Report

State what ran, which files changed, and each metric as old vs new, copied from the files.
