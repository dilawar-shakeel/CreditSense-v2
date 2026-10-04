# ADR 0005: OpenAI behind one gateway, with a hard spend cap

**Status:** Accepted
**Date:** 2026-10-04

## Context

LLM calls are needed for nodes such as the memo draft and the rule-answer step, and for embeddings. The project has about $5 a month for LLM spend, $0 hosting and about 10 hours a week. Tests must not cost money or depend on the network.

## Options considered

- **Several providers behind an abstraction.** More flexible, but more code and more keys to manage for a small project.
- **OpenAI only, through one module (chosen).** One provider, one place to count tokens, cache and mock.
- **A local model.** No spend, but it needs hardware the free tier does not provide.

## Decision

Use OpenAI, only through `src/creditsense/llm/`. No other module imports the `openai` SDK. One small model serves every node. A stronger memo model is a config switch and is off by default. The OpenAI account has a hard monthly cap of about $5. Unit tests always use the mocked LLM.

Approved by Dilawar Shakeel; listed under Locked decisions in `CLAUDE.md`.

## Consequences

- `src/creditsense/llm/` holds the real client, the prompts and the mock client.
- Real-LLM evals run only where the plan allows (prompt, agent, RAG or model changes, and the weekly full run). If the spend cap is hit, they are skipped with a visible warning.
- Requests and costs are traced in Langfuse (free tier) in Phase 6.
- The API key lives in `.env` and CI secrets, never in the repo.
