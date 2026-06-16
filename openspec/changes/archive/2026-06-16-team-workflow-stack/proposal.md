# Team Workflow Stack — n8n + Vikunja + cal-diy

## Why

The monorepo has 65+ stacks but no end-to-end team workflow toolset. Users (admins, research teams, editorial staff, support teams) have no canonical place to:

- Capture inbound requests from a shared mailbox
- Triage them into a structured backlog
- Schedule appointments that automatically populate that backlog
- Run a daily/weekly review with LLM-generated briefings and summaries
- Get nudged on stale work

This change introduces three new stacks (n8n, Vikunja, cal-diy) wired together as a private, zero-trust, LLM-augmented team workflow loop. The OpenCode Go API (`https://opencode.ai/zen/go/v1`) is the LLM backbone — one bill, one rate-limit pool, one model catalogue shared with the rest of the monorepo.

## What Changes

### New Stacks (all follow `infrastructure/stacks/GOLD_STANDARD.md`)

| Stack | Path | Services | Pangolin resource |
|:--|:--|:--|:--|
| **n8n** | `infrastructure/stacks/engineering/n8n/` | n8n + postgres:16-alpine + redis:7-alpine + locket + n8n-init | `n8n.cianfhoghlaim.ie` → port 5678 |
| **Vikunja** | `infrastructure/stacks/tools/vikunja/` | vikunja + postgres:16-alpine + locket + vikunja-seed | `vikunja.cianfhoghlaim.ie` → port 3456 |
| **cal-diy** | `infrastructure/stacks/tools/cal-diy/` | calcom-web (built from `stedding/repos/cal.diy/`) + postgres:16-alpine + redis:7-alpine + locket | `calcom.cianfhoghlaim.ie` → port 3000 |

### New Komodo procedures (5 in `infrastructure/komodo/procedures/`)

`team-stack-up`, `team-stack-down`, `team-stack-health`, `team-workflow-reload`, `team-backup`

### New seeded n8n workflows (6 in `infrastructure/stacks/engineering/n8n/workflows/`)

| Workflow | Trigger | LLM call | Sink |
|:--|:--|:--|:--|
| `team-daily-briefing` | Cron 06:00 Mon–Fri | `kimi-k2.6` | Email + Vikunja `/_briefings` |
| `team-email-triage` | IMAP poll every 5 min | `minimax-m2.5` categorise | Vikunja task (assignees=[team]) |
| `team-booking-to-vikunja` | cal-diy `booking.created` webhook | none (router) | Vikunja task with start/end (Gantt) |
| `team-followup-drafter` | Cron every 4h | `deepseek-v4-flash` | Vikunja `/_drafts/` |
| `team-weekly-summary` | Cron Friday 17:00 | `glm-5.1` | Vikunja `/_reports/weekly/` |
| `team-stale-task-nudger` | Cron daily 08:00 | `mimo-v2.5` | Email + Vikunja comment |

### New one-shot init containers

- `n8n-init` (oven/bun) — walks `workflows/`, POSTs each JSON to n8n REST API, activates
- `vikunja-seed` (oven/bun) — creates the `team` group + 6 starter projects (`_briefings`, `_drafts`, `_reports`, `client-work`, `internal`, `support`)

### New Infisical items (19 items in `dev-baile/`, all under the team-workflow folder tree)

- `n8n/`: encryption_key, jwt_secret, postgres_password, webhook_secret, api_key
- `vikunja/`: postgres_password, service_jwt_secret, admin_password
- `calcom/`: database_url, postgres_password, nextauth_secret, encryption_key, webhook_secret, cron_api_key
- `team-mailbox/`: imap_user, imap_password, smtp_password, from_email

### New 22 lines in root `.infisical.env`

All `infisical://dev-baile/...` references (no plaintext). The OpenAI / OpenCode Go LLM backbone env vars are **reused** — no new LLM secrets.

### New OpenSpec capability specs (3)

- `openspec/specs/task-management/spec.md` — Vikunja kanban + Gantt + list + team sharing
- `openspec/specs/scheduling/spec.md` — cal-diy booking + team + per-member pages
- `openspec/specs/workflow-automation/spec.md` — n8n + OpenCode Go + LLM pipelines

## Impact

| Surface | Before | After |
|:--|:--|:--|
| Stacks | 65+ | 68+ (3 new) |
| Workflow automation | none (n8n available as a one-off) | Full team workflow loop with 6 seeded workflows |
| Task management | none in monorepo (only external) | Self-hosted Vikunja with kanban + Gantt + list |
| Scheduling | none in monorepo | Self-hosted cal-diy with team + per-member pages |
| LLM workflow surface | LiteLLM proxy only | LiteLLM + n8n (HTTP Request node) + Vikunja sink + cal-diy webhook |
| Secret items in Infisical | 14 | 18 (19 new items, 14 existing) |
| Komodo procedures | 30+ | 35+ |
| `.infisical.env` lines | 96 | 118 |

## Cross-service wiring (hostnames on the shared `cianfhoghlaim` Docker network)

```
cal-diy ──webhook──▶ n8n ──REST──▶ vikunja  (assignees=[team group])
                  │
                  └────LLM────▶ opencode-go API  (kimi-k2.6, glm-5.1, minimax-m2.5, mimo-v2.5, deepseek-v4-flash)
```

## Pangolin routing (all private, behind Olm VPN + Pocket ID SSO)

| Resource | Domain | Internal port | Site | Role |
|:--|:--|:--|:--|:--|
| `n8n` | `n8n.cianfhoghlaim.ie` | 5678 | `arm1-oci` | Member |
| `vikunja` | `vikunja.cianfhoghlaim.ie` | 3456 | `arm1-oci` | Member |
| `cal-diy` | `calcom.cianfhoghlaim.ie` | 3000 | `arm1-oci` | Member |

## Validation

- `docker compose -f compose.yaml config --quiet` passes for all 3 stacks (exit 0)
- `openspec validate team-workflow-stack --strict` passes
- 19 new Infisical items created in `dev-baile` (verified via REST API)
- `bun run secrets:init` re-runs cleanly (no broken `infisical://` refs)

## Out of scope (follow-up issues to file)

- Add `.agents/skills/n8n/` skill (workflow authoring, debugging)
- Patch `litellm/config/prometheus.yml` to scrape `n8n:5678/metrics`
- Wire Pocket ID OIDC SSO into n8n, Vikunja, cal-diy
- Create the `team-backups` Garage S3 bucket (auto-created on first `team-backup.toml` run)
- Pin `latest` versions in workflow JSONs after team validation
- Build + push the `ghcr.io/cianfhoghlaim/n8n-init` and `ghcr.io/cianfhoghlaim/vikunja-seed` images
