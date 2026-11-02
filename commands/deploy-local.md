---
description: Prepare and, after explicit approval, deploy from local to a named target
agent: devops-agent
---

Prepare a deployment from the current local project to this target:

$ARGUMENTS

The arguments must identify the provider/host and environment (for example, AWS staging or a named SSH host). If either is missing, ask before proceeding. Inspect repository instructions, deployment tooling, current branch/worktree state, target configuration, and relevant changes. First provide a deployment plan: target/account/environment, prerequisites, commands or workflow, expected changes, risks, and rollback approach. Default to read-only inspection and dry-run/plan commands when supported. Do not deploy, provision, publish, alter live resources, or expose secrets until the user has reviewed the plan and explicitly approved that specific deployment. Never infer approval from invoking this command alone. Use existing project tooling; do not install tools or change provider configuration without authorization. After approval, run only the approved steps, stop on unexpected changes or errors, and report exactly what was executed and its result.
