---
name: daily-dev-summary
description: Generate daily standup summaries for Gustavo by reviewing yesterday’s GitHub, Linear, and Google activity. Use when the user asks for a daily update, what they worked on yesterday, or a summary of completed development work grouped by Linear tasks, pull requests, commits, meetings, and engineering impact.
---

# Daily Dev Summary

When the user asks for their daily, generate a concise standup summary using yesterday’s activity from GitHub, Linear, and Google (Calendar + Chat).

## Sources

Use:
- **Linear activity** from the requested day: assigned issues, updated issues, status changes, comments, and completed tasks.
- **GitHub activity** from the requested day: commits, pull requests, reviews, comments, and merged PRs.
- **Google Calendar** from the requested day: events with attendees (meetings, calls, meets), fetched via the script below.
- **Google Chat** from the requested day: messages sent by Gustavo in organization spaces, fetched via the script below.

Prioritize Linear as the source of product/task context. Use GitHub to enrich the technical details. Use Calendar for meetings and Chat for communication context/decisions.

### Google data script

At the start of every daily, run the script to fetch Google activity:

```
python3 skills/daily-dev-summary/fetch-google-activity.py [date_arg]
```

Where `date_arg` is optional and accepts:
- (no argument) → yesterday
- `today` → today
- `yesterday` → yesterday
- `2026-07-05` → specific day
- `2026-07-01:2026-07-05` → date range (inclusive)
- `2026-07-01..2026-07-05` → date range (alternative syntax)

The script outputs JSON to stdout with this structure:
- `calendar.events[]`: meetings/calls/meets with title, duration, attendees, type, hangoutLink
- `chat.messages[]`: messages sent by Gustavo with space name, text snippet, timestamp

If the script fails or returns empty sections, continue with Linear+GitHub silently (fallback behavior).

### GitHub activity

When checking GitHub activity, look for Gustavo’s activity from the requested day across the configured organization/repositories, including commits, pull requests, reviews, comments, and merged PRs. If GitHub access is unavailable, clearly say that GitHub activity could not be accessed and continue with Linear only.

## Output format

Always return exactly this format:

```md
# Daily Meet Gustavo {fecha_del_dia}

## Qué hice ayer:

- ...
- ...
- ...
```

## Writing rules

- Write in Spanish.
- Summarize by task, feature, or Linear issue.
- Do not list raw commits unless they are important.
- Avoid overly technical noise.
- Mention GitHub PRs only when they clarify the work.
- Make the summary sound natural for a daily standup.
- If there is little activity, produce an honest summary based on the available evidence.
- Do not mention missing data sources in the final daily summary.
- If GitHub activity is unavailable, use Linear as the main source silently.
- Only mention unavailable GitHub access if the user explicitly asks about data sources or debugging.
- Write the summary as if Gustavo is going to say it in a daily meeting, not as an audit log.

### Calendar rules

- Mention meetings inside the “Qué hice ayer” block as narrative items, not a separate section.
- Format: `- Meet con <equipo/cliente> sobre <tema> (30 min)` or `- Llamada con X sobre Y`.
- Show who + topic + type (meet/call/in-person); do not dump the event body.
- Omit routine standups (e.g., “Daily | SH Ledger”) unless the user explicitly asks for them.
- Include the type of meeting (Google Meet, call, in-person) using the `type` field and `hangoutLink`.

### Chat rules

- Only mention Chat messages when they reflect a decision or advancement communicated by Gustavo.
- Do not list every message; summarize and paraphrase.
- Do not reproduce confidential or sensitive content verbatim; rephrase as a decision or update.
- Group messages by space/topic when multiple messages from the same space relate to the same theme.
- If a Chat message relates to a Linear issue or GitHub PR, merge it with that task’s bullet point instead of creating a separate entry.

## Publishing to Google Chat (optional)

If the user explicitly asks to publish the daily to a Google Chat space or DM, run the post script after generating the summary:

```bash
python3 skills/daily-dev-summary/post-to-chat.py --space="<space_name>" --text="<daily_text>"
```

Or for a direct message:
```bash
python3 skills/daily-dev-summary/post-to-chat.py --dm="<email>" --text="<daily_text>"
```

Or without specifying a space (uses `DAILY_CHAT_SPACE` env var):
```bash
python3 skills/daily-dev-summary/post-to-chat.py --text="<daily_text>"
```

Rules:
- Only publish when the user explicitly asks ("publícame el daily en X", "envía el resumen a Y", "postea el daily").
- Never publish automatically or as part of every daily generation.
- Confirm the space name with the user if ambiguous (multiple spaces with similar names).
- If the user doesn't specify a space, use the `DAILY_CHAT_SPACE` env var if set, else ask which space.
- Report success (with messageId) or failure to the user after publishing.
- The message is sent as plain text attributed to Gustavo (user authentication, not a bot).
- Escape quotes in the daily text when passing via `--text` argument.
