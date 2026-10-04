---
name: leakage-check
description: Check for target leakage and data-contract breaks before any change to features, the target, splits or the data pipeline in CreditSense v2.
---

# Leakage and data-contract check

Run this before merging any change under `src/creditsense/data/` or any change to model features.

## Rules (locked)

- Prediction point is **at approval**. A feature is allowed only if it is known at application or at approval.
- Target: charged off (`CHGOFF`) vs paid in full (`P I F`), among approved, disbursed loans. Open loans are excluded from training.
- Splits are by approval fiscal year. Never random splits, never shuffling across years.

## Steps

1. For every column the change adds or touches, find its row in `docs/DATA.md` and confirm its timing label: `application`, `approval` or `after_outcome`. If it has no row, add one and ask Dilawar to confirm the label before using it.
2. Reject any `after_outcome` column as a feature. Known examples in the Kaggle data: charge-off date, charged-off amount, and any balance derived from the outcome. Also be suspicious of disbursement fields: confirm they are known at the prediction point before use.
3. Check derived features: a feature built from an `after_outcome` column is also `after_outcome`.
4. Run the leakage test suite (`uv run pytest tests/data -k leakage`) and the pandera contracts.
5. Sanity check: if a single feature gives a very high out-of-time AUC on its own, treat it as leakage until proven otherwise, and report it.
6. If splits changed, regenerate the row counts and default rate per split in `docs/DATA.md` from the pipeline, not by hand.
7. Report in the PR: the columns checked, their labels, and the test results.

## Do not

- Change the split years. They are an open item that Dilawar decides after the profiling run.
- Silence or loosen a failing leakage or contract test to make CI pass.
