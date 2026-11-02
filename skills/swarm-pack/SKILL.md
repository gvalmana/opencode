---
name: swarm-pack
description: Use when running Swarm Pack multi-agent workflows such as swarm-delivery, swarm-review, swarm-feature, swarm-assurance, swarm-maintenance, swarm-hotfix, or swarm-mission with small commits.
---

# Swarm Pack Constitution

## Work Discipline

Use `references/workflows/<team-name>.json` as the selected team's structural routing contract. Respect attempt limits, route conditions, and stricter existing stop rules. Metadata is not an execution engine. Blocked/failed HANDOFFs recommend `stop`; never continue automatically.

Concrete HANDOFFs fill every required field using `none` for empty values and indented multiline values. Changed files use an indented `- relative/path` list. Select one next role, `final`, or `stop`, not template alternatives. Existing extensions remain supported: acceptance_criteria, edge_cases_covered, qa_report, architecture_notes, decision, findings.

If available, the coordinator can run `swarm-pack validate-handoff --team <team> --file <handoff> --context <context-json>` with its explicit assignment and complete task history. Exit 1 means invalid input/repository state; exit 2 means stop. Neither permits automatic continuation. Exit 0 still requires approval and work verification; sequential mode does not inspect repository changes. Structural validation never proves native runtime behavior.

Work in small, reviewable increments.

Do not broaden scope.

Do not modify unrelated files.

Before handoff, verify the smallest relevant test, build, or lint command available.

If blocked by ambiguity, contradiction, failing tests outside scope, missing credentials, or unsafe commands, stop and report the blocker.

## Commit Discipline

Only the orchestrator or mission leader creates commits.

Create commits only when the user explicitly authorizes them for this session. Invoking a workflow, requesting implementation, or creating a branch is not commit authorization. This applies to temporary commits in role worktrees as well as integration commits.

Without authorization (or when the user passes `--no-commit`), use sequential execution in the current checkout without per-role worktrees, staging, or commits. Explain this mode before delegation. Each role sees the previous role's uncommitted changes; inspect and record the role-owned delta before continuing. Never silently create temporary commits to obtain isolation. If isolation is required without commits, stop and clarify the trade-off.

When commits are authorized, each verified role-owned change may become a small commit before the next role starts. Only the coordinator stages and commits, including inside role worktrees.

Commit messages must include:

```text
By <role>.
Swarm-Pack: true
Swarm-Workflow: <workflow>
Swarm-Role: <role>
```

Repeat `Swarm-Role` for every role that contributed to the commit. Keep the
existing `By <role>.` line even when multiple roles contributed. These are Git
trailers for searchable metadata, not cryptographic signatures.

Example:

```text
Implement handoff validation

By coder.
Swarm-Pack: true
Swarm-Workflow: delivery
Swarm-Role: coder
```

Do not commit secrets, generated noise, unrelated formatting, or files outside the assigned scope.

## Handoff Format

Every subagent must finish with:

```text
HANDOFF
role: <role>
status: completed|blocked|failed
task: <short-stable-task-name>
worktree_path: <path-or-none>
branch: <branch-or-none>
base_sha: <sha-or-none>
commit_needed: yes|no
changed_files:
verification:
next_recommended_role:
summary:
risks:
```

If `status` is `blocked` or `failed`, the orchestrator must not continue to the next role without resolving the blocker.

`commit_needed` is advisory and never grants commit authorization. Include tracked and untracked role-owned files in `changed_files`. Use literal `none` for `worktree_path`, `branch`, and `base_sha` when no per-role worktree was assigned. In sequential mode, report only this role's delta, not unrelated or previous roles' changes.

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

## Routine Inspection

- Prefer the host's read, glob, and grep tools for file contents and searches. They retain the host's sensitive-file checks; do not replace them with blanket shell reading permissions.
- Set the shell tool's working directory to the assigned checkout/worktree. Avoid `git -C ...`, `cd ... && ...`, and unnecessary compound commands for routine inspection.
- With the npm CLI available on PATH, use `swarm-pack inspect <query>`. Queries are `status`, `diff`, `staged`, `log`, `show`, `files`, `tree`, `head`, `root`, and `branch`. They accept no extra arguments; diffs disable external diff/textconv and Git runs without a pager. Use read tools separately for untracked file contents.
- `pwd`, `ls`, `git status ...`, and `git rev-parse HEAD` also have routine OpenCode permissions. Other shell forms retain normal approval handling. Do not rewrite commands to evade a denial.
- If the installed CLI lacks these commands, report the version mismatch and use normal host-approved tools. Do not install, run `npx`, or broaden permissions automatically. Other targets may restrict shell access entirely for read-only roles; use their available read/search tools.

## Consumer Docker Compose

- Docker is optional. These helpers manage an existing consumer environment, not a Docker test framework or per-agent containers. Never create or modify consumer Compose files for this workflow.
- Obtain the existing absolute project directory, project name and ordered absolute Compose files from the coordinator. If context is missing, ask the coordinator; never infer it from cwd, worktrees, environment variables or default files. Every role uses the same explicit context, even from another worktree.
- Inspection: `swarm-pack compose-inspect <ps|logs|images|top|config> --project-directory <absolute-dir> --project-name <name> --file <absolute-file> [--file <absolute-file> ...]`. Logs are bounded to `--no-color --tail 100`; config uses `--quiet` (no rendered configuration). Inspection has a 30-second timeout and 1 MiB output buffer limit; no arbitrary Docker flags are accepted.
- Only the orchestrator or mission leader may use `swarm-pack compose-start <start|up>` with the same required options, after explicit user authorization for that consumer environment and operation. `up` means `up -d --no-recreate`; `start` means `start`. Startup has a 120-second timeout and 1 MiB output buffer limit. The CLI does not authenticate roles or store/infer approval. Permission allowance is not user authorization.
- Restart/stop are coordinator-only with approval. Down/rm, volume changes and exec/run still require explicit approval and are not exposed by these helpers. No failure permits automatic startup, cleanup, recreation or destructive recovery. After timeout/failure, daemon work or containers may still be running; inspect and report before further action.
- Helpers preserve native `.env` loading from the explicit original cwd/project directory and inherited Compose/Docker environment and configuration. Explicit directory/name/files pin those selectors; do not sanitize legitimate connection or interpolation settings. Authorization must cover the effective Docker endpoint, profiles and environment/configuration, shared unchanged across role worktrees. The only forced environment override is `COMPOSE_REMOVE_ORPHANS=false`, taking precedence over process and `.env` settings: the helper never automatically removes orphans. Confirm context with the coordinator if uncertain. `config --quiet` suppresses rendered configuration, but error stderr and logs may still expose secrets.
- A consumer container mounting the original checkout does not see role worktree edits. Do not claim worktree changes were tested there, rewrite mounts, or create per-agent containers automatically.
- OpenCode grants only the exact inspection helper pattern to all roles and startup to coordinators. Other targets retain their existing restrictive read-only/no-shell policies: ask a shell-capable coordinator to inspect instead of broadening tools. Logs may contain secrets; do not publish them indiscriminately.

## Worktree Discipline

When worktrees are enabled for the session, the orchestrator assigns each role a worktree and a branch.

- The worktree lives at `.worktrees/swarm-<role>/<task-id>` inside the project.
- Coordinators create it from the integration checkout root with `swarm-pack worktree-create <role> <task-id> <base-sha>`, after the session's existing authorization checks. Use the role name without `swarm-` and a full HEAD SHA from `swarm-pack inspect head`. The helper validates a clean checkout, the current base, new branch/destination and real directory ancestors. It never stages, commits, integrates, removes, or forces. Subagents must not invoke it.
- The branch is `swarm/<role>/<task-id>` based on the current integration checkout HEAD immediately before that role starts, after previous roles have been integrated. Record that exact SHA as `base_sha`.
- Subagents operate only inside their assigned worktree path. They do not run git commands outside that path.
- Subagents do not create, remove, merge, or commit worktrees. The orchestrator owns all of that.
- Subagents report `worktree_path`, `branch`, and `base_sha` in their HANDOFF.
- Before integration, the coordinator inspects status, tracked/staged diffs, and untracked files in the role worktree. A branch diff alone does not include uncommitted work. Verify the HANDOFF and stage only reviewed, assigned paths; stop for unexpected files or changes in a read-only role.
- With explicit commit authorization, the coordinator commits the verified delta inside the role worktree, checks the resulting branch diff against `base_sha`, then squash-merges it into the integration checkout and commits with the role byline and trailers. Do not merge an unchanged branch to transfer uncommitted files.
- Before merging, require the integration checkout to be clean and its HEAD to equal `base_sha`. Serialize integration; if another session changed HEAD or checkout contents, stop and re-evaluate rather than rebasing or resolving conflicts automatically.
- Remove a role worktree only after successful integration, verification that its committed tree matches the integration result, and a clean status including untracked files. Use `git worktree remove` without force. Preserve failed, dirty, or uncertain worktrees and report their paths and branches. Retain the branch as a recovery reference; uncommitted changes are not recoverable from reflog.
- If a session is aborted, the worktree may be orphaned. See `docs/troubleshooting.md` for recovery.

To opt out of isolation for one session, pass `--no-worktree` in the command arguments or set `OPENCODE_SWARM_NO_WORKTREE=1` before the session. This does not authorize commits. `--no-commit` explicitly selects the no-commit sequential mode and takes precedence over commit requests. These are workflow arguments, not installer CLI flags.
