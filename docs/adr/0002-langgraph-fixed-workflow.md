# ADR 0002: LangGraph with a fixed workflow graph

**Status:** Accepted
**Date:** 2026-10-04

## Context

Each application passes through intake, eligibility, risk scoring, compliance, memo drafting, a guardrail check and officer sign-off. The run must pause for the officer, survive a restart, and be fully auditable. Constraints: $0 hosting, about $5 a month of LLM spend, about 10 hours a week, fintech audit needs.

## Options considered

- **Plain Python functions.** Simple, but pause and resume, state persistence and step tracing would be written by hand.
- **LangGraph with a fixed graph (chosen).** Typed state, built-in checkpointing and interrupts, and every step is a named node.
- **LangGraph or another framework with a supervisor agent choosing tools.** Flexible, but the path varies per run, costs more LLM calls, and is harder to audit and test.

## Decision

Use LangGraph with a fixed workflow graph. The LLM works only inside nodes; there is no supervisor agent choosing tools. Run state and checkpoints are stored with the LangGraph Postgres checkpointer, so a paused run survives a restart.

Approved by Dilawar Shakeel; listed under Locked decisions in `CLAUDE.md`.

## Consequences

- The graph order is the same for every application, which makes runs reproducible and testable. New nodes follow the `langgraph-node` skill.
- Checkpoints live in Postgres (ADR 0004), so the graph needs that database running.
- Each node's inputs, outputs and retrieved passages are written to the audit log.
- Adding a step means changing the graph in code and in review, not asking an agent to pick one.
