---
name: daily-dev-summary
description: Generate daily standup summaries for Gustavo by reviewing yesterday’s GitHub and Linear activity. Use when the user asks for a daily update, what they worked on yesterday, or a summary of completed development work grouped by Linear tasks, pull requests, commits, and engineering impact.
---

# Daily Dev Summary

When the user asks for their daily, generate a concise standup summary using yesterday’s activity from GitHub and Linear.

## Sources

Use:
-GitHub activity from yesterday: commits, pull requests, reviews, comments, and merged PRs.
-Linear activity from yesterday: assigned issues, updated issues, status changes, comments, and completed tasks.

Prioritize Linear as the source of product/task context. Use GitHub to enrich the technical details.

## Output format

Always return exactly this format:

```md
# Daily Meet Gustavo {fecha_del_dia}

## Qué hice ayer:

- ...
- ...
- ...
When checking GitHub activity, look for Gustavo’s activity from yesterday across the configured organization/repositories, including commits, pull requests, reviews, comments, and merged PRs. If GitHub access is unavailable, clearly say that GitHub activity could not be accessed and continue with Linear only.

Writing rules
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
