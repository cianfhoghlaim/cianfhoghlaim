# Team Workflow Stack — Migration Report (2026-06-06)

## Executive Summary

Successfully migrated the self-hosted Infisical vault from `bunchloch` (MacBook) to `arm1-oci` (Oracle Cloud Free Tier, 24 GB RAM). Established the team-workflow stack (Vikunja + n8n) on `arm1-oci` with Pangolin private resource routing. All services are running and accessible through the Pangolin tunnel.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         arm1-oci (OCI Free Tier)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Vikunja  │  │   n8n    │  │ Infisical│  │ Pangolin Core  │  │
│  │  :3456   │  │  :5678   │  │  :8080   │  │ (EE + PocketID)│  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬────────┘  │
│       │              │             │                 │           │
│  ─────┼──────────────┼─────────────┼─────────────────┼────────  │
│       │    infrastructure Docker network              │           │
│  ─────┼──────────────┼─────────────┼─────────────────┼────────  │
│       │              │             │                 │           │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌───────┴────────┐  │
│  │PG :16    │  │PG :16    │  │PG :14    │  │ Newt-arm1-oci   │  │
│  │Redis :7  │  │Redis :7  │  │Redis :7  │  │ (tunnel agent)  │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         ▲                           ▲
         │ Pangolin tunnel           │ SSH (oci_arm1 key)
         ▼                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    bunchloch (MacBook M4)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ OLM Client   │  │ Komodo Core  │  │ Agent / Browser        │ │
│  │ (desktop)    │  │    :9120     │  │ (Chrome DevTools)      │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Access URLs (all private, require Pangolin client + SSO)

| Service | Domain | Port | Role |
|---------|--------|------|------|
| Vikunja | `vikunja.cianfhoghlaim.ie` | 3456 | Member |
| n8n | `n8n.cianfhoghlaim.ie` | 5678 | Member |
| Infisical | `infisical.cianfhoghlaim.ie` | 8080 | Member |

---

## Infisical Vault (arm1-oci)

### Setup Details

- **Image**: `infisical/infisical:v0.160.10`
- **Project**: `dev-baile` (ID: `f3cff583-b74b-4804-b9d3-db8b68885236`)
- **Environment**: `Development` (slug: `dev-baile`)
- **Machine Identity**: `locket-bunchloch` (Universal Auth + Token Auth)
- **Admin Account**: `admin@cianfhoghlaim.ie` (server console only)

### Seeded Folders (22+ containers)

| Folder | Purpose | Key Secrets |
|--------|---------|-------------|
| `/vikunja` | Task management | db_password, jwt_secret, admin_password |
| `/n8n` | Workflow automation | encryption_key, jwt_secret, db_password, api_key |
| `/calcom` | Team scheduling | db_password, nextauth_secret, webhook_secret |
| `/pocketid-team-workflow` | OIDC SSO | client_id, client_secret |
| `/planetscale` | Cloud DB | username, password |
| `/litellm` | LLM proxy | master_key |
| `/deepseek` | LLM API | api_key |
| `/pangolin` | VPN routing | server_secret, postgres_password, licence |
| `/cloudflare` | CDN | account_id, api_token |
| `/firecrawl` | Web scraping | api_key |
| `/motherduck` | DuckDB cloud | token |
| `/pulumi` | IaC | backend_url, passphrase |
| `/browserbase` | Browser automation | api_key, project_id |
| `/huggingface` | ML models | token |
| `/lakehouse-garage` | S3 storage | rpc_secret, access keys |
| `/crowdsec` | IDS | bouncer_key |
| `/oci-infrastructure` | Cloud infra | arm1_ip |
| `/opencode` | Code AI | go_api, openai_base_url |
| `/pydantic-logfire` | Tracing | write_token |
| `/pocketid-tinyauth` | Auth gateway | client_id, client_secret |

### Screenshots

- [01-infisical-signup.png](screenshots/01-infisical-signup.png) — First super-admin account creation
- [02-infisical-universal-auth-credentials.png](screenshots/02-infisical-universal-auth-credentials.png) — Universal Auth client secret generation
- [03-infisical-folders-no-workflow.png](screenshots/03-infisical-folders-no-workflow.png) — Vault after initial seeding (before team-workflow)
- [08-infisical-vault-seeded.png](screenshots/08-infisical-vault-seeded.png) — Complete vault with all 22 folders

---

## Vikunja (Task Management)

### Status: **RUNNING** (Healthy, migrations complete)

- **Image**: `vikunja/vikunja:1.0.0-rc2`
- **Database**: PostgreSQL 16 (on same Docker network)
- **Features enabled**: CalDAV, Task Attachments, Email Reminders, TOTP, User Registration
- **Pangolin labels**: Present (`pangolin.private-resources.vikunja.*`)

### Data

| Field | Value |
|-------|-------|
| Admin user | `team-admin` / `team@cianfhoghlaim.ie` |
| Admin password | `admin_2026!` (change on first login) |

### Screenshots

- [04-vikunja-login.png](screenshots/04-vikunja-login.png) — Login page
- [05-vikunja-dashboard.png](screenshots/05-vikunja-dashboard.png) — Dashboard with task list

---

## n8n (Workflow Automation)

### Status: **RUNNING** (Healthy, owner account set up)

- **Image**: `docker.n8n.io/n8nio/n8n:1.94.1`
- **Database**: PostgreSQL 16
- **Queue**: Redis 7 (enables multi-worker scaling)
- **LLM Backend**: OpenCode Go API (via LiteLLM proxy)

### Data

| Field | Value |
|-------|-------|
| Owner account | `team@cianfhoghlaim.ie` / `Team Admin` |
| Owner password | `N8nAdmin2026!` |

### Seeded Workflows (10 JSON files)

These workflows are in the repo at `infrastructure/stacks/engineering/n8n/workflows/` and can be re-imported via `komodo procedure run team-workflow-reload`:

| Workflow | Trigger | LLM Model | Sink |
|----------|---------|-----------|------|
| `team-daily-briefing` | Cron 06:00 Mon–Fri | `kimi-k2.6` | Email + Vikunja |
| `team-email-triage` | IMAP every 5 min | `minimax-m2.5` | Vikunja task |
| `team-booking-to-vikunja` | cal-diy webhook | none | Vikunja task |
| `team-followup-drafter` | Cron every 4h | `deepseek-v4-flash` | Vikunja drafts |
| `team-weekly-summary` | Cron Friday 17:00 | `glm-5.1` | Vikunja report |
| `team-stale-task-nudger` | Cron daily 08:00 | `mimo-v2.5` | Email + Vikunja |
| `team-weekly-digest-brief` | Cron Friday 17:00 | `glm-5.1` | Cross-service digest |
| `team-appointment-diary` | Cron every 6h | `kimi-k2.6` | Vikunja diary task |
| `team-document-digitiser` | Webhook | — | Paperless/firecrawl |
| `team-wiki-page-monitor` | Cron daily | — | Changedetection |

### Screenshots

- [06-n8n-setup.png](screenshots/06-n8n-setup.png) — Owner account setup page
- [07-n8n-dashboard.png](screenshots/07-n8n-dashboard.png) — Dashboard with metrics

---

## cal-diy (Scheduling)

### Status: **PENDING** (compose files ready, deploy after OIDC client setup)

- The cal-diy compose (`infrastructure/stacks/tools/cal-diy/compose.yaml`) is configured and ready
- Requires the `pocketid-team-workflow` OIDC client to be created in Pocket ID before starting
- Will be deployed at `calcom.cianfhoghlaim.ie` port 3000

---

## Key Fixes Applied

### 1. Infisical v0.160.10 Migration
- Added `AUTH_SECRET` env var (required by v0.160.10)
- Renamed `dev` environment slug to `dev-baile` to match all 50+ `infisical://dev-baile/...` references
- Created machine identity `locket-bunchloch` with Universal Auth + Token Auth
- Seeded 22 folders with 60+ secrets from `.infisical.env`

### 2. Locket URL Fix
- Added `--infisical-url=http://infisical-backend:8080` to all three sidecar.yaml files
- Added `--infisical-default-environment=dev-baile` and `--infisical-default-project-id` flags
- Added `INFISICAL_CLIENT_ID` environment block to locket containers
- Added `infrastructure` network to sidecar.yaml for Locket → Infisical communication

**Note**: Locket v0.17.3 has a template rendering issue with `?path=` query parameters in `infisical://` references. The current stacks use direct `.env` files with resolved secrets (bypassing Locket). A Locket upgrade or template format fix is needed for the long-term.

### 3. Network Fix
- Connected `vikunja`, `vikunja-db`, `n8n` to the `infrastructure` Docker network
- `newt-arm1-oci` (Pangolin tunnel agent) is on the same network
- Pangolin labels on all containers are now visible to the newt agent

### 4. Secrets Format Update
- Updated `secrets.env` files for all three stacks to use Locket-compatible `?path=` query parameter format
- Created team-workflow folders (`/vikunja`, `/n8n`, `/calcom`, `/pocketid-team-workflow`, `/planetscale`, `/litellm`) in the Infisical vault
- All secrets pushed via Infisical API (POST `/api/v3/secrets/raw/<key>`)

---

## Operational Commands

### Health checks (from arm1-oci)
```bash
# Vikunja
curl http://localhost:3456/health        # → "OK"
curl http://localhost:3456/api/v1/info   # → JSON with version + features

# n8n
curl http://localhost:5678/healthz       # → {"status":"ok"}

# Infisical
curl http://localhost:8081/api/status    # → JSON with config status
```

### Deploy / restart (from arm1-oci)
```bash
# Vikunja
cd /tmp/pangolin-deploy/infrastructure/stacks/tools/vikunja
docker compose -f compose.yaml -f pangolin.yaml up -d

# n8n
cd /tmp/pangolin-deploy/infrastructure/stacks/engineering/n8n
docker compose -f compose.yaml -f pangolin.yaml up -d
```

### Re-sync from git + redeploy (from arm1-oci)
```bash
cd /tmp/pangolin-deploy
git pull
# Then redeploy as above
```

### Add a new secret (from arm1-oci)
```bash
TOKEN=$(curl -sS 'http://localhost:8081/api/v1/auth/universal-auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"clientId":"a7287e79-...","clientSecret":"0dcebf1f..."}' | python3 -c 'import sys,json; print(json.load(sys.stdin)["accessToken"])')

curl -sS -X POST "http://localhost:8081/api/v3/secrets/raw/MY_KEY" \
  -H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json" \
  -d '{"workspaceId":"f3cff583-b74b-4804-b9d3-db8b68885236","environment":"dev-baile","secretPath":"/MY_FOLDER","secretValue":"my_value"}'
```

---

## Follow-up Issues

1. **Locket v0.17.3 template bug** — Template substitution fails for `?path=` query params. Current workaround: direct `.env` files with resolved secrets. Fix: report upstream or downgrade to v0.16.x.

2. **`pocketid-team-workflow` OIDC client** — Not yet created in Pocket ID. Required for SSO access through Pangolin. Bootstrap via Pocket ID admin UI.

3. **cal-diy deployment** — Compose files ready. Deploy after OIDC client exists.

4. **n8n-init one-shot container** — The `ghcr.io/cianfhoghlaim/n8n-init` image must be built and deployed to re-import the 10 workflow JSONs.

5. **Vikunja seed container** — `ghcr.io/cianfhoghlaim/vikunja-seed` needs to be built and run to create the `team` group + 6 starter projects.

6. **DNS/OIDC SSO integration** — Pocket ID OIDC SSO needs to be wired into all three services for seamless login. Currently using local auth.

7. **Locket template format migration** — All `.infisical.env` references use `infisical://dev-baile/<path>/<key>` format (init-vault parsing). Locket templates use `{{ infisical:///<key>?path=/<folder> }}` format. These two formats should be unified or a converter script written.

8. **Komodo sync** — The team-workflow stacks on arm1-oci are deployed manually from `/tmp/pangolin-deploy/`. Komodo should be configured to sync from Forgejo and manage deployments properly through the `team-workflow.toml` stack definitions.

---

## Key Credentials (change on first use)

| Service | User | Password |
|---------|------|----------|
| Vikunja admin | `team-admin` | `admin_2026!` |
| n8n owner | `team@cianfhoghlaim.ie` | `N8nAdmin2026!` |
| Infisical admin | `admin@cianfhoghlaim.ie` | `Str0ngP@ssw0rd123` |
| Infisical machine identity | Client ID: `a7287e79-...` | Secret: `0dcebf1f...` |
