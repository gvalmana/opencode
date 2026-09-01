---
name: swarm-pack
description: Use when running Swarm Pack multi-agent workflows such as swarm-delivery, swarm-review, swarm-feature, swarm-assurance, or swarm-mission with small commits.
---

# Swarm Pack Constitution

## Work Discipline

Work in small, reviewable increments.

Do not broaden scope.

Do not modify unrelated files.

Before handoff, verify the smallest relevant test, build, or lint command available.

If blocked by ambiguity, contradiction, failing tests outside scope, missing credentials, or unsafe commands, stop and report the blocker.

## Commit Discipline

Only the orchestrator or mission leader creates commits.

Each role-owned change should become a small commit before the next role starts.

Commit messages must include:

```text
By <role>.
```

Example:

```text
Implement handoff validation

By coder.
```

Do not commit secrets, generated noise, unrelated formatting, or files outside the assigned scope.

## Handoff Format

Every subagent must finish with:

```text
HANDOFF
role: <role>
status: completed|blocked|failed
task: <short-stable-task-name>
commit_needed: yes|no
changed_files:
verification:
next_recommended_role:
summary:
risks:
```

If `status` is `blocked` or `failed`, the orchestrator must not continue to the next role without resolving the blocker.

## Communication

Subagents do not talk directly to the user unless they are the orchestrator or mission leader.

Subagents do not delegate to other agents.

Subagents return concise handoffs only.

## Engineering

Prefer Clean Code and SOLID.

Keep business rules separated from IO, frameworks, UI, persistence, network, filesystem, and external systems.

Prefer focused tests close to the behavior changed.

Do not add abstractions unless they reduce current coupling or improve testability.

Preserve user changes. Never revert or overwrite unrelated work.

## Worktree Discipline

When worktrees are enabled for the session, the orchestrator assigns each role a worktree and a branch.

- The worktree lives at `.worktrees/swarm-<role>/<task-id>` inside the project.
- The branch is `swarm/<role>/<task-id>` based on the main worktree HEAD at session start.
- Subagents operate only inside their assigned worktree path. They do not run git commands outside that path.
- Subagents do not create, remove, merge, or commit worktrees. The orchestrator owns all of that.
- Subagents report `worktree_path`, `branch`, and `base_sha` in their HANDOFF.
- The orchestrator squash-merges the role branch into the main worktree between roles and removes the role worktree with `git worktree remove --force`. The branch stays in the reflog.
- If a session is aborted, the worktree may be orphaned. See `docs/troubleshooting.md` for recovery.

To opt out for one session, pass `--no-worktree` in the command arguments or set `OPENCODE_SWARM_NO_WORKTREE=1` before the session.
