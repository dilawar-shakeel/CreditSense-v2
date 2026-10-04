---
name: phase-kickoff
description: Start a new CreditSense v2 phase. Use when Dilawar says to begin a phase (for example "start Phase 2") or when work moves to the next phase.
---

# Phase kickoff

Use this at the start of every phase, before writing code.

## Steps

1. Confirm the previous phase's exit criteria are met. Run `just check` and any phase-specific command (for example `just data` or `just eval`). If something fails, report it and stop.
2. Read the phase in the plan doc (link in `CLAUDE.md`) and the **Locked decisions** table in `CLAUDE.md`.
3. Write `docs/phases/phase-<n>.md` with:
   - Goal (one sentence, copied from the plan)
   - Deliverables as a checklist
   - Exit criteria as a checklist, each one tied to a command or file that proves it
   - Decisions this phase relies on (from the locked table)
   - Open questions for Dilawar, if any
4. If the phase has open questions, list them for Dilawar and wait for answers. Do not pick defaults on anything that changes scope, data, model behaviour, security or cost.
5. Create the branch `phase-<n>/kickoff` from an up-to-date `main`, commit the phase doc, and open a PR titled `docs: phase <n> kickoff`.
6. Break the deliverables into tasks of about one session each (10 hours a week is the pace), and list them in the PR description in the order you propose to do them.

## Do not

- Start coding deliverables on the kickoff branch.
- Add dependencies or migrations without asking (see `CLAUDE.md`).
