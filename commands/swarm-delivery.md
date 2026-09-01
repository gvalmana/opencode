---
description: Deliver with coder and cleaner.
agent: swarm-orchestrator
---

Run the `delivery-team` workflow for this request:

$ARGUMENTS

Team flow:

```text
coder -> cleaner -> final
```

Rules:

- Use the `swarm-pack` skill.
- Inspect repository state before starting.
- Delegate implementation to `swarm-coder` in its assigned worktree.
- Commit safe coder-owned changes (squash-merge from the coder branch) before cleanup.
- Delegate behavior-preserving cleanup to `swarm-cleaner` in its assigned worktree.
- Commit safe cleaner-owned changes when there are any.
- Return to coder only if cleaner identifies a functional problem.
- Stop on blockers, unexpected files, ambiguous scope, or unsafe git state.
- Final response must summarize roles, commits, verification, worktree paths, and risks.

Options:

- Pass `--no-worktree` in $ARGUMENTS to disable per-role worktree isolation for this session and use the legacy sequential flow.
- Alternatively set `OPENCODE_SWARM_NO_WORKTREE=1` before the session as an escape hatch.
