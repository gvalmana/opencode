---
name: daily-focus
description: Generate a prioritized daily focus plan for Gustavo by reviewing Linear tasks, GitHub PRs, Google Calendar, and Chat mentions. Use when the user asks for "foco del día", "prioridades de hoy", "en qué enfocarme", or similar.
---

# Daily Focus

When the user asks for their daily focus, generate a prioritized action plan using today's activity from Linear, GitHub, and Google (Calendar + Chat).

## Sources

Use:
- **Linear activity** from the requested day: assigned issues in progress, todo, or blocked. Consult via the Linear MCP tools.
- **GitHub activity** from today: open PRs, review requests, CI failures, merge conflicts, fetched via `gh` CLI below.
- **Google Calendar** from today: meetings and available time, fetched via the script below.
- **Google Chat** from today: messages where Gustavo is mentioned and active threads, fetched via the script below.

Prioritize Linear as the source of product/task context. Use GitHub to enrich the technical details. Use Calendar for meetings and Chat for communication context/decisions.

### Google data script

At the start of every daily focus, run the script to fetch Google activity:

```
python3 skills/daily-focus/fetch-focus-data.py [--date=YYYY-MM-DD]
```

Where `--date` is optional (defaults to today). The script outputs JSON to stdout with:
- `calendar.events[]`: meetings with duration, type, attendees
- `calendar.total_busy_minutes`: total meeting time
- `chat.mentions[]`: messages where Gustavo is mentioned
- `chat.active_threads[]`: threads where Gustavo is participating

If the script fails, continue with Linear+GitHub silently (fallback behavior).

### GitHub activity (via gh CLI)

After running the Google script, use `gh` CLI to fetch GitHub activity:

```bash
# PRs where I'm author, open
gh search prs --author @me --state open --json repository,title,url,createdAt --limit 50

# PRs where review is requested of me
gh search prs --review-requested @me --state open --json repository,title,url,createdAt --limit 50

# PRs with CI failure (check each of my open PRs)
gh pr checks <repo>#<number> --json state,name --jq '.[] | select(.state == "FAILURE") | .name'

# PRs with merge conflicts
gh pr list --repo <repo> --state open --json number,title,url,mergeable --jq '.[] | select(.mergeable == "CONFLICTING")'
```

If GitHub access is unavailable, continue with Linear only (fallback behavior).

### Linear activity

After running the scripts, use the Linear MCP to get:

1. **Issues in progress**: `Linear_list_issues(assignee="me", state="In Progress")`
2. **Issues to do**: `Linear_list_issues(assignee="me", state="Todo")`
3. **Blocked issues**: Check if any of these issues have blocking relations

For each issue, note: title, priority, state, and whether it's blocking or blocked.

## Output format

Always return exactly this format:

```md
# Daily Focus Gustavo {fecha_del_dia}

## Hoy tengo {X}h disponibles ({N} reuniones)

## Qué haré hoy:

### Foco alto (bloquea a otros o es urgente)
- {issue/task} → {contexto breve}
- ...

### Foco medio (avanzar o responder)
- {issue/task} → {contexto breve}
- ...

### Foco bajo (si alcanza el tiempo)
- {issue/task} → {contexto breve}
- ...

## Pendientes de respuesta
- {mención en chat o review pendiente}
- ...

## Sugerencia del día
> {1-2 oraciones con el foco principal en primera persona, usando "enfocarme en..." o "comenzar con..."}
```

## Writing rules

- Write in Spanish.
- Be concise: 1 line per task maximum.
- Include links when available (PR URLs, Linear issue IDs).
- Do not list more than 5 tasks per category.
- The daily suggestion must be actionable and immediate.
- Prioritize by impact: what unblocks others first, then what advances the most.
- If there is no high-priority work, say so honestly and suggest medium-priority items.
- Do not mention missing data sources in the final output.
- If GitHub or Calendar data is unavailable, continue with what's available silently.
- Write the summary as if Gustavo is planning his day, not as an audit log.

### Prioritization rules

**High priority (foco alto):**
- Issues blocking other team members
- Urgent or priority 1 issues
- PRs with failing CI (blocks merge)
- Chat mentions that require a response before others can proceed
- PRs where Gustavo's review is blocking someone else

**Medium priority (foco medio):**
- Issues in progress that can advance
- PRs awaiting Gustavo's review
- Active chat threads needing input
- Tasks with approaching deadlines

**Low priority (foco bajo):**
- Research or investigation tasks
- Nice-to-have improvements
- Tasks without urgency or dependencies

### Calendar rules

- Calculate available time: 8h minus total meeting time.
- List meetings briefly in the header, not as separate items.
- Exclude focus time blocks, out-of-office, and routine standups from busy time.
- If meetings exceed 6h, warn that the day is meeting-heavy.

### Chat rules

- List only mentions that require a response or action.
- Group related messages from the same thread.
- Do not reproduce sensitive content; summarize the ask.
- If a mention relates to a Linear issue, merge it with that task.

### GitHub rules

- PRs with CI failure are always high priority.
- Review requests are medium priority unless someone is blocked.
- Merge conflicts are high priority if the PR is in progress.
- Do not list more than 3 PRs per category.
- When mentioning a PR, always include the project name and link: `- [ProjectName] PR [#N](url) description`

## Publishing to Google Chat (optional)

If the user explicitly asks to publish the focus to a Google Chat space or DM:

```bash
python3 skills/daily-dev-summary/post-to-chat.py --space="<space_name>" --text="<focus_text>"
```

Or for a direct message:
```bash
python3 skills/daily-dev-summary/post-to-chat.py --dm="<email>" --text="<focus_text>"
```

Or without specifying a space (uses `DAILY_CHAT_SPACE` env var):
```bash
python3 skills/daily-dev-summary/post-to-chat.py --text="<focus_text>"
```

Rules:
- Only publish when the user explicitly asks ("publícame el foco en X", "envía las prioridades a Y", "postea el focus").
- Never publish automatically or as part of every daily focus generation.
- Confirm the space name with the user if ambiguous (multiple spaces with similar names).
- If the user doesn't specify a space, use the `DAILY_CHAT_SPACE` env var if set, else ask which space.
- Report success (with messageId) or failure to the user after publishing.
- The message is sent as plain text attributed to Gustavo (user authentication, not a bot).
- Escape quotes in the text when passing via `--text` argument.

## Horario distribuido (bajo demanda)

When the user explicitly asks to schedule tasks into the calendar ("agéndame las tareas", "programa mi día", "distribuye las tareas en mi calendario", "crea eventos para mis tareas"):

1. Get issues from Linear with estimates (use `estimate` field from Linear MCP).
2. For issues without estimate, ask the user: `"¿Cuánto tiempo estimas para [issue title]?"` with options: `0.5h, 1h, 1.5h, 2h, 3h, 4h`.
3. Prepare the JSON input for the schedule script:

```json
{
  "tasks": [
    {"id": "ACLEDGE-1961", "title": "Implementar X", "estimate_hours": 4, "priority": "high"},
    {"id": "ACLEDGE-1963", "title": "Configurar Y", "estimate_hours": 2.5, "priority": "medium"}
  ]
}
```

4. Run the schedule script:

```bash
echo '<json_input>' | python3 skills/daily-focus/schedule-focus.py [--date=YYYY-MM-DD]
```

5. Display the schedule in this format:

```md
## Horario distribuido para {fecha}:

{HH:MM} - {HH:MM}  [{issue_id}] {título}
{HH:MM} - {HH:MM}  [{issue_id}] {título} (continuación)

✅ {N} eventos creados en Google Calendar
```

### Schedule rules

- Maximum block: 2 hours per task before switching.
- Transition: 15 minutes between tasks (break/context switch).
- Morning (9-12): High priority tasks (deep work).
- Afternoon (14-18): Medium/Low priority, reviews, responses.
- Tasks with estimate > 2h are split into multiple blocks.
- Blocks are interleaved by priority to avoid burning time on one task.
- Events are created with title format: `{issue_id} {title}` (or `↳ {issue_id} {title}` for continuations).
- If the user confirms, events are created in Google Calendar automatically.
