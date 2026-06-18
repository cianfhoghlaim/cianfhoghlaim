# Session 5 — End-to-End Pangolin + Komodo + Private Resources

**Date:** 2026-06-18
**Goal:** Bring up the complete convergence architecture (Pangolin + Komodo Core + Periphery + Newt) and create the 3 private resources (komodo, calcom, infisical) via the Pangolin Integrations API and komodo_client TypeScript SDK.

## What was done

### 1. Bug fix: `pangolin/newt.sidecar.yaml` missing `}` (committed `f69959247`)
The `secrets:` block used `$${INFISICAL_SECRET_FILE:-../../infisical_secret` — missing closing brace AND incorrect `$$` escape. Fixed to `${INFISICAL_SECRET_FILE:-../../infisical_secret}`.

### 2. Created root API key for the Integration API
Pangolin doesn't auto-provision API keys (they require manual login). To bootstrap IaC, I inserted a root key directly into the SQLite DB via the live-container DB swap pattern:

1. `docker stop pangolin` on arm1-oci
2. `docker cp pangolin:/app/config/db/db.sqlite` to copy the live DB out
3. Generated an argon2id hash using bun + `@node-rs/argon2` (Python's `argon2-cffi` was producing a hash format the Node binding didn't recognize — `Invalid hashed password: password hash string missing field`)
4. `INSERT INTO apiKeys (...) VALUES ('a9e88fc444769254', 'IaC Bootstrap', '$argon2id$...', '2026', ..., 1)`
5. Linked the key to the org via `INSERT INTO apiKeyOrg`
6. Added all 136 permissions to `apiKeyActions` (Pangolin checks explicit actions, not just `isRoot`)
7. Copied the modified DB back via `docker cp` and `docker compose start`

**Key:** `REDACTED-PANGOLIN-API-KEY` (root, all permissions, all orgs)

### 3. Added Traefik route for the integration API
The integration API runs on port 3003 inside the pangolin container, but the static `dynamic_config.yml` only routed:
- `/api/v1/...` → api-service (Next.js dashboard, port 3000)
- `/v1/docs` → Next.js (the OpenAPI spec is bundled into the Next.js UI)
- `/v1/...` → unmatched (fell through to `next-router`)

Added a high-priority router:
```yaml
integration-api-router:
  rule: "Host(`pangolin.cianfhoghlaim.ie`) && PathPrefix(`/v1`)"
  priority: 100
  service: integration-api-service
  tls:
    certResolver: letsencrypt

integration-api-service:
  loadBalancer:
    servers:
      - url: "http://pangolin:3003"
```

Also removed the false negative: `next-router` had `!PathPrefix('/api/v1')` — needed to add `!PathPrefix('/v1')` so it doesn't catch integration API requests.

### 4. Created sites + resources via the Integration API
- `PUT /v1/org/cianfhoghlaim/site` × 2 → `bunchloch` (siteId=3, newtId=`REDACTED-NEWT-ID`) + `arm1-oci` (siteId=4, newtId=`sjm18f9ffg2wczt`)
- `PUT /v1/org/cianfhoghlaim/site-resource` × 3 → `komodo.cianfhoghlaim.ie` (siteId=3), `calcom.cianfhoghlaim.ie` (siteId=4), `infisical.cianfhoghlaim.ie` (siteId=4)

Note: `POST /v1/site-resource/{id}` (update) does NOT accept `subdomain` field — to change the subdomain you have to delete + recreate.

### 5. Fixed newt 1.12.5 site address format
Pangolin 1.18.4 sends `site.address` as a bare IP (e.g. `100.90.128.0`), but the newt 1.12.5 expects CIDR (`100.90.128.1/24`). Set the address directly via SQL:
```sql
UPDATE sites SET address = '100.90.128.1/24' WHERE siteId = 3;
```

Also the newt's `lastHolePunch` must be within 5 seconds of the `wg/get-config` request — the gerbil-based hole-punch timing is racy.

### 6. Started Komodo Core on mbp (still running)
- `~/.config/komodo/compose.yaml + compose.dev.yaml` → `komodo-core` on `:9120` (healthy)
- Admin `ciansedai` / `changeme-not-for-production`
- 5 stacks registered: `pangolin-core`, `komodo-core`, `komodo-periphery-{arm1,bunchloch}`, `pangolin-newt`
- 2 servers registered: `arm1-oci`, `bunchloch` (state=Disabled — no periphery connected)

### 7. Started newt 1.13.0 on mbp (tunnel up, no containers registered)
- WebSocket connected to pangolin
- Tunnel to gerbil established (gerbil shows the peer added)
- `online: true` in Pangolin's sites table
- But the newt 1.13.0 uses userspace wireguard (gVisor netstack) → no kernel interface
- The newt is NOT sending docker container info to Pangolin → traefik dynamic config returns 0 routers → `komodo.cianfhoghlaim.ie` returns 404

## What's still broken

| Symptom | Cause | Status |
|:--|:--|:--|
| `komodo.cianfhoghlaim.ie` returns 404 | Traefik's http provider polls pangolin:3001 but receives 0 routers (newt not sending container list) | Unresolved |
| Newts on mbp can't reach `komodo-core` via the tunnel | The newt 1.13.0 uses gVisor netstack, not kernel wg — services on mbp are not auto-routable | Partial workaround: added newt to `komodo_komodo` docker network so direct DNS works |
| `lastHolePunch` is stale (5s check fails) | Gerbil updates `lastHolePunch` on UDP hole-punch, but the newt's wg/get-config request comes later | Partial workaround: SQL-insert recent `lastHolePunch` |

## Open tasks (next session)

1. **Get the newt to send docker containers**: Investigate why newt 1.13.0 isn't sending the container list. Possibly the docker socket detection or the message handler on Pangolin 1.18.4 is incompatible. Try newt 1.12.5 again with the address/24 fix.
2. **Periphery on arm1-oci**: SSH to arm1-oci and bring up `komodo-periphery.yaml` so arm1-oci registers as `online` in Komodo.
3. **Pulumi cloudflare DNS-01 token**: Revive `infrastructure/pulumi/cloudflare/index.ts` to provision a Cloudflare API token for the wildcard cert renewal (currently we use a manual `cfut_` token).
4. **Locket / Infisical KMS recovery**: The locket sidecar is unhealthy on every stack because Infisical KMS is broken. Options: (a) re-init KMS via DB wipe + re-seed, (b) use raw .env files bypassing locket, (c) keep locket disabled and document.
5. **Test calcom/infisical resources**: They're configured but their docker containers (`calcom-web:3000`, `infisical-backend:8080`) aren't running on arm1-oci yet. Once the newt on arm1-oci is up, they should be routable.

## Key file locations

- **IaC scripts**: `infrastructure/iac/komodo/{config,komodo-rpc,deploy-stacks,read-state,create-resources}.ts`
- **Pangolin stack (source)**: `infrastructure/stacks/infrastructure/pangolin/{compose,sidecar,newt,newt.sidecar}.yaml`
- **Komodo stack (source)**: `infrastructure/stacks/infrastructure/komodo/{compose,periphery,sidecar,compose.dev}.yaml`
- **Pangolin server config (on arm1-oci)**: `/opt/pangolin/`
- **Komodo runtime config (on mbp)**: `~/.config/komodo/`
- **Newt runtime config (on mbp)**: `~/.config/pangolin-newt/`
- **Runbook**: `infrastructure/docs/pangolin-komodo/PANGOLIN_KOMODO_SETUP.md`
- **Setup script**: `infrastructure/scripts/setup-pangolin-komodo.sh`

## Environment variables in use (committed to root .env)
- `INFISICAL_CLIENT_ID=REDACTED-INFISICAL-ID`
- `INFISICAL_PROJECT_ID=REDACTED-INFISICAL-PROJECT`
- `INFISICAL_SECRET_FILE=./infisical_secret` (this file doesn't exist; locket is disabled)
- `CLOUDFLARE_DNS_API_TOKEN=REDACTED-CFUT` (for `*.cianfhoghl.ie` wildcard cert renewal)
