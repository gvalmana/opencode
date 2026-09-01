---
description: Coordinate a full mission workflow.
agent: swarm-mission-leader
---

Run the `mission-team` workflow for this request:

$ARGUMENTS

Team flow:

```text
mission-leader -> analyst -> gherkin-writer -> gherkin-reviewer -> qa-procedure-writer -> qa-procedure-reviewer -> implementer -> cleaner -> code-reviewer -> architect -> hardener -> qa -> senior-implementor -> merger -> final
```

Rules:

- Use the `swarm-pack` skill.
- Inspect repository state before starting.
- Clarify mission scope and approval gates before implementation.
- Use mission-team agents for implementation, cleanup, review, architecture, hardening, QA, senior implementation, and merge readiness.
- Stop on blockers, repeated failed iterations, unexpected files, ambiguous scope, or unsafe git state.
- Final response must summarize roles, commits, verification, worktree paths, approvals, findings, and risks.

Options:

- Pass `--no-worktree` in $ARGUMENTS to disable per-role worktree isolation for this session and use the legacy sequential flow.
- Alternatively set `OPENCODE_SWARM_NO_WORKTREE=1` before the session as an escape hatch.
