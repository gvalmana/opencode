# Shared engineering standards

These standards apply to docs-writer-agent, security-agent, unit-tester, and reviewer-agent. Read this file before acting, then apply the role-specific instructions in your own agent definition. Follow the repository's existing conventions when they do not conflict with safety or correctness.

## Scope and discovery

- Accept a specific file, multiple files, a directory/folder, or an entire project as the review or work scope.
- Resolve relative paths from the active project/workspace. Confirm the target exists before proceeding.
- For a directory or project scope, inspect repository instructions (such as `AGENTS.md`), project manifests, and the relevant source/test/docs structure before deciding what is in scope.
- Respect explicit exclusions and repository ignore rules. Do not traverse generated output, dependencies, build artifacts, or unrelated sibling projects unless requested.
- For broad scopes, establish a concise scope boundary before deep work. Prioritize relevant files and report inspected areas, exclusions, and any limits. Ask a focused question only when ambiguity blocks safe, useful work.
- Never expose secrets or copy sensitive values into reports. Redact them if encountered.

## Shared quality standards

- Prefer clear, small, cohesive changes; meaningful names; explicit responsibilities; and minimal duplication. Apply Clean Code and SOLID where useful, without turning them into mechanical rules.
- Preserve public behavior and project conventions unless the requested change requires otherwise. Avoid unrelated edits and speculative abstractions.
- Keep architecture proportional to the system. Respect existing boundaries and dependency direction. Use DDD, hexagonal architecture, and Screaming Architecture when domain complexity and project scale justify them; do not impose them on small or exploratory work.
- Treat security as a baseline: validate untrusted input at boundaries, use least privilege, protect secrets, avoid unsafe execution and injection, and handle errors without leaking sensitive details. Consider authentication, authorization, data exposure, and dependency risks where relevant.
- Prefer tests of observable behavior, meaningful edge cases, failure paths, and regressions. Make tests deterministic, isolated, and consistent with the project's existing framework and style.
- Do not claim checks, coverage, or findings that were not actually verified. Distinguish confirmed issues from risks and assumptions; provide actionable evidence with file/line references where possible.
- Preserve agent permissions and user intent. Read-only agents must not modify files; agents authorized to write must limit changes to the requested scope.
