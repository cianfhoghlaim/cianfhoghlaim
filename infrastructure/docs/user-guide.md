# User Guide — Self-Hosted Team Productivity Stack

All 6 services live at `*.cianfhoghlaim.ie` and share a single PocketID SSO login.

## Logging In
1. Go to any service URL (e.g. `n8n.cianfhoghlaim.ie`)
2. You'll be redirected to PocketID at `auth.cianfhoghlaim.ie`
3. Authenticate with your passkey (Face ID / Touch ID / YubiKey)
4. After authentication, you're signed into ALL 6 services

## Services at a Glance

| Service | URL | What It Does |
|:--|:--|:--|
| Vikunja | `vikunja.cianfhoghlaim.ie` | Kanban + Gantt + list task management |
| cal-diy | `calcom.cianfhoghlaim.ie` | Team scheduling + booking pages |
| n8n | `n8n.cianfhoghlaim.ie` | Workflow automation + LLM pipelines |
| Paperless-ngx | `paperless.cianfhoghlaim.ie` | Document ingestion + OCR + categorisation |
| Glance | `glance.cianfhoghlaim.ie` | Single-pane dashboard for all 6 services |
| Changedetection | `changedetection.cianfhoghlaim.ie` | Website change monitoring + alerts |

## Daily Workflow

1. **Morning:** Glance dashboard loads at `glance.cianfhoghlaim.ie` — see today's Vikunja tasks, cal.com bookings, and recent document uploads
2. **Book meetings:** Use cal-diy (`calcom.cianfhoghlaim.ie/team`) — n8n auto-creates Vikunja tasks with dates (visible in Gantt view)
3. **Ingest documents:** Upload papers/PDFs to Paperless-ngx — they're auto-categorised and summarised
4. **Manage tasks:** Vikunja at `vikunja.cianfhoghlaim.ie` shows all your tasks from all sources (client work, internal, support)
5. **Monitor changes:** Changedetection watches 19 wiki/site pages — flagged edits create Vikunja tasks and email alerts

## Weekly Digest

Every Friday at 5 PM, n8n sends a weekly summary email with:
- Tasks completed / blocked this week
- Calendar bookings and cancellations
- Documents ingested and categories
- Wiki pages that changed (with severity scores)
- Workflow execution statistics

Access past digests in Vikunja: `/_reports/weekly/`

## Troubleshooting

- **Can't log in:** Check PocketID at `auth.cianfhoghlaim.ie/healthz`
- **Tasks not appearing:** Check n8n workflow status at `n8n.cianfhoghlaim.ie/workflows`
- **Document not categorised:** Paperless-ngx OCR queue at `paperless.cianfhoghlaim.ie/dashboard`
- **Page not monitored:** Check changedetection watches at `changedetection.cianfhoghlaim.ie`
