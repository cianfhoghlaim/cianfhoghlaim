# n8n — Workflow Automation + LLM Pipelines

Workflow engine at `https://n8n.cianfhoghlaim.ie`. Login via PocketID SSO.

## Seeded Workflows (10 total)
| Workflow | Trigger | LLM Model |
|:--|:--|:--|
| wiki-page-monitor | Changedetection webhook | deepseek-v4-pro |
| document-digitiser | Paperless webhook | opencode-go/deepseek-v4-flash |
| appointment-diary | Every 6 hours | opencode-go/kimi-k2.6 |
| weekly-digest-brief | Friday 17:00 | opencode-go/glm-5.1 |
| daily-briefing | 06:00 weekdays | opencode-go/kimi-k2.6 |
| email-triage | Every 5 min | opencode-go/minimax-m2.5 |
| booking-to-vikunja | cal-diy webhook | (none) |
| followup-drafter | Every 4 hours | opencode-go/deepseek-v4-flash |
| weekly-summary | Friday 17:00 | opencode-go/glm-5.1 |
| stale-task-nudger | Daily 08:00 | opencode-go/mimo-v2.5 |

All LLM calls route through the LiteLLM gateway at `http://litellm:4000/v1`.

Backed by PlanetScale "bunchloch" (schema: `n8n`).
