---
name: daily-dev-summary
description: Generate daily standup summaries for Gustavo using Linear, GitHub, Google Calendar, and Google Chat MCP tools. Use when the user asks for a daily update, what they worked on yesterday, or a summary of completed development work.
---

# Daily Dev Summary

When the user asks for their daily, generate a concise standup summary using the requested day's activity from GitHub, Linear, Google Calendar, and Google Chat. The default requested day is yesterday.

Use the configured MCP tools directly. Do not use non-MCP Google integrations, read local Google tokens, or ask the user to fix authentication outside the MCP connection. If an MCP call fails, continue with the remaining sources according to the fallback rules below.

## Sources

Use:
- **Linear activity** from the requested day: assigned issues, updated issues, status changes, comments, and completed tasks.
- **GitHub activity** from the requested day: commits, pull requests, reviews, comments, and merged PRs.
- **Google Calendar** from the requested day: call `google-workspace_calendar_events` with an exact `timeMin` and `timeMax` range in the calendar timezone. Use the primary calendar unless the user requests a specific calendar.
- **Google Chat** from the requested day: call `google-chat_search_messages` with the exact `time_filter`. Inspect returned authors and retain messages sent by Gustavo; use `google-chat_list_spaces` and `google-chat_get_messages` when a space-specific lookup or pagination is needed.

Prioritize Linear as the source of product/task context. Use GitHub to enrich the technical details. Use Calendar for meetings and Chat for communication context/decisions.

## Google MCP Workflow

1. Resolve the requested date and its start/end in the calendar timezone.
2. Call `google-workspace_calendar_events` for that exact range.
3. Call `google-chat_search_messages` for that exact time range, then filter to Gustavo's messages and relevant spaces.
4. Use `google-workspace_whoami` only when the authenticated identity is needed to identify Gustavo's Chat messages.
5. If Calendar or Chat is unavailable, continue with Linear and GitHub silently.

## GitHub Activity

Look for Gustavo's activity from the requested day across the configured organization/repositories, including commits, pull requests, reviews, comments, and merged PRs. If GitHub access is unavailable, use Linear as the main source silently.

## Output Format

Always return exactly this format:

```md
# Daily Meet Gustavo {fecha_del_dia}

## Qué hice ayer:

- ...
- ...
- ...
```

## Writing Rules

- Write in Spanish.
- Summarize by task, feature, or Linear issue.
- Do not list raw commits unless they are important.
- Avoid overly technical noise.
- Mention GitHub PRs only when they clarify the work.
- Make the summary sound natural for a daily standup.
- If there is little activity, produce an honest summary based on the available evidence.
- Do not mention missing data sources in the final daily summary.
- Only mention unavailable GitHub access if the user explicitly asks about data sources or debugging.
- Write the summary as if Gustavo is going to say it in a daily meeting, not as an audit log.

### Calendar Rules

- Mention meetings inside the “Qué hice ayer” block as narrative items, not a separate section.
- Format: `- Meet con <equipo/cliente> sobre <tema> (30 min)` or `- Llamada con X sobre Y`.
- Show who + topic + type (meet/call/in-person); do not dump the event body.
- Omit routine standups, such as “Daily | SH Ledger”, unless the user explicitly asks for them.
- Include the meeting type using the event data and hangout link when available.

### Chat Rules

- Only mention Chat messages when they reflect a decision or advancement communicated by Gustavo.
- Do not list every message; summarize and paraphrase.
- Do not reproduce confidential or sensitive content verbatim; rephrase as a decision or update.
- Group messages by space/topic when multiple messages from the same space relate to the same theme.
- If a Chat message relates to a Linear issue or GitHub PR, merge it with that task's bullet point instead of creating a separate entry.

## Publishing to Google Chat (Optional)

If the user explicitly asks to publish the daily, use `google-chat_send_message` directly.

- For a named space, call `google-chat_list_spaces`, resolve the exact space ID, and send the text.
- For a direct message, call `google-chat_resolve_dm_space` with the recipient email, then send the text to the returned space.

Rules:
- Only publish when the user explicitly asks, such as “publícame el daily en X” or “envía el resumen a Y”.
- Never publish automatically or as part of every daily generation.
- Confirm the space name with the user if ambiguous.
- If the user does not specify a space, ask which space or recipient to use.
- Report success or failure to the user after publishing.
- The message is sent as plain text attributed to Gustavo through the authenticated MCP connection.
