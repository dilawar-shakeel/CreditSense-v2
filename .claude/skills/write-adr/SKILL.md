---
name: write-adr
description: Write an Architecture Decision Record for CreditSense v2. Use when Dilawar approves a new decision or a change to a locked decision.
---

# Write an ADR

Locked decisions live in `CLAUDE.md` and the plan doc. Changing one needs Dilawar's explicit approval first. This skill records it.

## Steps

1. Confirm Dilawar approved the decision in their own words. If not, stop and ask, presenting the options with one line each and your recommendation.
2. Create `docs/adr/NNNN-<short-title>.md`, numbered after the highest existing ADR, with these sections:
   - **Status:** Accepted, or Superseded by ADR-NNNN
   - **Date:** today
   - **Context:** the problem, constraints ($0 hosting, about $5/month LLM cap, 10 hours a week, fintech audit needs)
   - **Options considered:** each with its trade-off in one or two lines
   - **Decision:** what was chosen, and who approved it
   - **Consequences:** what changes in code, cost, risk and docs
3. If it replaces an earlier ADR, set the old one's status to `Superseded by ADR-NNNN`.
4. Update the **Locked decisions** table in `CLAUDE.md` in the same PR.
5. Branch `adr/NNNN-<short-title>`, commit as `docs: ADR NNNN <title>`, and open a PR.
