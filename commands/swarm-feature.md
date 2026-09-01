---
description: Build a specified feature.
agent: swarm-orchestrator
---

Run the `feature-team` workflow for this request:

$ARGUMENTS

Team flow:

```text
specifier -> coder -> refactorer -> architect -> final
```

Rules:

- Use the `swarm-pack` skill.
- Inspect repository state before starting.
- Delegate acceptance criteria to `swarm-specifier`.
- Ask the user to approve the spec when criteria are non-trivial before delegating to coder.
- Delegate implementation to `swarm-coder`.
- Commit safe coder-owned changes before refactoring.
- Delegate behavior-preserving cleanup to `swarm-refactorer`.
- Commit safe refactorer-owned changes when there are any.
- Delegate structural review to `swarm-architect`.
- Commit safe architect-owned changes when there are any.
- Loop back to specifier only when the architect finds a missing requirement or unclear criterion.
- Stop on blockers, unexpected files, ambiguous scope, or unsafe git state.
- Final response must summarize roles, commits, verification, and risks.
