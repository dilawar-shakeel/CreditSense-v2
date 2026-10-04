---
name: langgraph-node
description: Add or change a node in the CreditSense v2 LangGraph underwriting workflow. Use whenever a task touches src/creditsense/graph/.
---

# Add or change a LangGraph node

The workflow is a **fixed graph**: intake, eligibility, risk score, compliance, memo, guardrail check, officer sign-off (interrupt), record decision. The LLM works only inside nodes.

## Steps

1. **State first.** Add any new fields to the typed state model in `src/creditsense/graph/state.py` (Pydantic). Every field gets a type and a one-line docstring. Never pass data between nodes outside the state.
2. **Write the node** in `src/creditsense/graph/nodes/<name>.py` as a pure function `(state) -> partial state update`.
   - Deterministic rules come before any LLM call.
   - LLM calls go only through `creditsense.llm` (never import `openai` here) and use a structured output schema.
   - Model scoring goes through the model service; compliance lookups go through `creditsense.rag`. Treat both as tools.
   - Anything the node decides that matters for the decision goes into state so it reaches the audit log.
3. **Wire it** in `src/creditsense/graph/build.py`. Keep the order fixed. Conditional edges are allowed only for: incomplete application (refer to officer), guardrail failure (retry once, then refer), and the officer interrupt.
4. **Never** let a node record a final decision. Only the record-decision node writes it, and only after the officer interrupt returns an approval, decline or override with a reason.
5. **Tests** in `tests/graph/test_<name>.py`:
   - Happy path and at least one failure path, using the mock LLM client from `creditsense.llm.mock`.
   - Assert the exact state fields the node writes.
   - If the node affects the memo or verdict, add or update a case in `tests/golden/`.
6. If the node changes what is written to the audit log, update the audit tests and run the chain verifier.
7. Run `just check`. If the node touches prompts, agent or RAG code, the real-LLM eval subset will run on the PR; check its cost and result.
8. Update the graph diagram in the README if the graph shape changed.
