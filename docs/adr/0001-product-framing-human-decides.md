# ADR 0001: Product framing: the human decides

**Status:** Accepted
**Date:** 2026-10-04

## Context

CreditSense v2 helps analysts with US SBA 7(a) loan applications. Lending decisions affect real businesses and are regulated, so the system needs audit trails, explainability and clear accountability. Constraints: $0 hosting, about $5 a month of LLM spend, about 10 hours a week of build time, and fintech-grade audit needs.

## Options considered

- **Automated decisioning.** The system approves or declines. Fastest for users, but removes accountability, raises regulatory and fairness risk, and is not defensible for a model trained on historical approved loans only.
- **Copilot with a human decision (chosen).** The system scores, checks rules with citations and drafts a memo. A credit officer decides.
- **Copilot with optional auto-approve for low risk.** Smaller scope of automation, but still needs a validated policy and monitoring that this project cannot provide.

## Decision

CreditSense is an analyst copilot. Code may recommend, grade and explain. Only a user with the `credit_officer` role can finalise a decision. No code path, MCP tool or agent node may record a final decision on its own. Missing documents mark an application incomplete and refer it to the officer. The middle risk band is referred to the officer.

Approved by Dilawar Shakeel (project owner); this is rule 1 in `CLAUDE.md`.

## Consequences

- The LangGraph workflow ends in an officer sign-off node that pauses until a `credit_officer` acts (see ADR 0002).
- The API checks the role before any decision is recorded.
- The audit log records the recommendation and the human decision separately.
- `docs/PRODUCT.md` and `docs/MODEL_RISK.md` state the scope and the limits.
- Any change that lets code decide on its own is a change to this ADR and needs Dilawar's approval first.
