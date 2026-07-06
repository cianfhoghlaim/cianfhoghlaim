# Tasks: 2026-07-06-deploy-infisical-bunchloch-local

## 1. Rewrite Infisical compose + sidecar + secrets (preflight)

- [ ] 1.1 Read `bonneagar/stacks/infisical/compose.yaml` line-by-line; map every
      `:` shorthand to long form (NO shorthand in the rewritten file)
- [ ] 1.2 Replace `image: infisical/infisical:latest` →
      `image: infisical/infisical:v0.161.12`
- [ ] 1.3 Replace `image: postgres:14-alpine` →
      `image: postgres:16-alpine`
- [ ] 1.4 Replace `image: redis:alpine` →
      `image: redis:7.4-alpine`
- [ ] 1.5 Replace the top-level
      `networks: { stack: { external: true, name: infrastructure } }` →
      `networks: { stack: { external: true, name: bunchloch-infra } }`
- [ ] 1.6 Rewrite `sidecar.yaml` to omit the Locket sidecar entirely
      (Infisical itself does not need Locket — the database + redis services
      read `env_file: /run/secrets/...` directly and the backend reads
      `env_file: .env`)
- [ ] 1.7 Rewrite `secrets.env` — strip all `{{ ... }}` Jinja wrappers; confirm
      every line is `KEY=infisical://dev-baile/infisical/KEY` (this file is
      for documentation only — Infisical's own backend does not resolve via
      Locket; the values are read by `db` + `redis` directly via `${VAR:?}`
      interpolation in compose.yaml)
- [ ] 1.8 Add a fresh `pangolin.yaml` file (currently the stack only has
      `blueprint.yaml`; the agent-observability spec requires both)

## 2. Generate the 5 required env vars

- [ ] 2.1 `openssl rand -hex 16` → captures `ENCRYPTION_KEY` (16-byte hex)
- [ ] 2.2 `openssl rand -base64 32` → captures `AUTH_SECRET` (32-byte base64)
- [ ] 2.3 Generate `POSTGRES_PASSWORD` (`openssl rand -hex 24`)
- [ ] 2.4 Generate `INFISICAL_CLIENT_SECRET` (`openssl rand -hex 32`) — this
      will become the Locket client secret for the consumer stacks in Change 2
- [ ] 2.5 Append all 4 to `.scratch/infisical.env` (NEVER committed — gitignored
      via root `.gitignore`)

## 3. Bring up Infisical

- [ ] 3.1 `docker network create bunchloch-infra` (one-time per host)
- [ ] 3.2 `cd bonneagar/stacks/infisical`
- [ ] 3.3 `docker compose -f compose.yaml up -d db redis`
- [ ] 3.4 `docker compose -f compose.yaml up -d backend`
- [ ] 3.5 `docker logs -f infisical-backend` — confirm `Server started on
      port 8080` message
- [ ] 3.6 `curl -sf http://localhost:8081/api/status | jq` — confirm JSON
      returns `{ "status": "ok" }`
- [ ] 3.7 Open `http://localhost:8081` in browser → sign up (first user IS
      the org admin per upstream docs)

## 4. Seed the local `dev-baile` project + machine identity

- [ ] 4.1 `infisical login --method=universal-auth` — paste the workspace
      URL, paste the email/password from step 3.7
- [ ] 4.2 Via UI: Create a **New Project** named `dev-baile`
- [ ] 4.3 Via UI: **Project Settings → Machine Identities → Create Identity**
      name `bunchloch-locket-machine`; grant at least `Member` on
      `dev-baile/dev`; **copy Client ID and Client Secret NOW** (shown once)
- [ ] 4.4 Capture the **Project ID** (UUID at the end of the project URL)
- [ ] 4.5 Run `bun run scripts/seed-infisical-vault.sh` — writes 7 seed
      secrets under `dev-baile/dev/{infisical,lakehouse,lakehouse-garage,
      lakehouse-clickhouse, lakehouse-redis,litellm,mlflow}` covering every
      URI referenced by the 4 consumer stacks' `secrets.env` files
- [ ] 4.6 Verify with `infisical secrets list --project-id=<UUID> --env=dev`
      — confirm 7 paths have entries
- [ ] 4.7 Save the Project ID + Client ID + Client Secret as 3 keys under
      the Locket vault for Change 2's sidecar config

## 5. Verify + handover to Change 2

- [ ] 5.1 `curl -sf http://localhost:8081/api/status` returns 200
- [ ] 5.2 `docker logs infisical-backend` has no panics in last 100 lines
- [ ] 5.3 The new `bunchloch-infra` network is `docker network ls | grep`
      visible
- [ ] 5.4 Project `dev-baile` exists with 7 seed paths populated
- [ ] 5.5 Add "Last archived: 2026-07-06-deploy-infisical-bunchloch-local" note
      to `.agents/skills/secrets-management/SKILL.md`
- [ ] 5.6 After deployment: `openspec archive 2026-07-06-deploy-infisical-bunchloch-local --yes`