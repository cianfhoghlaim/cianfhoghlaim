# Local Infisical as Permanent Dev Environment

## Why

The Cianfhoghlaim local Infisical fallback vault (the one we brought up
during the 2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1
and 2026-07-24-full-local-agent-platform-stack-up-v1 deploys) was
intended as an **emergency fallback** when the OCI Infisical private
resource returns 502. But the OCI repair path is blocked on a missing
Pocket ID OIDC setup on arm1-oci (the cianfhoghlaim IaC's
`sync:resources` command needs a Pangolin session cookie via
Pocket ID OIDC, which isn't configured yet).

Decision: **promote the local Infisical to a permanent dev environment**.
It's faster, has no external dependencies, and serves the local-fallback
use case better than a broken OCI path.

## What's on this local Infisical

- **Image**: `infisical/infisical:v0.161.12`
- **Database**: `infisical-db` (postgres:16-alpine)
- **Cache/queue**: `infisical-redis` (redis:7.4-alpine)
- **Workspace**: `dev-baile` (UUID: `d900f50a-acbf-446b-b4f6-e439710253e4`)
- **Port**: `http://127.0.0.1:8081` (host) → `8080` (container)
- **Project envs**: `dev`

## Bons-iac machine identity (the credential for all locket sidecars)

- **Client ID**: `7177c4ef-2688-4afa-982b-cc749d3ea3ad`
- **Client secret**: stored in `~/.locket/infisical_secret` (mode 0600)
- **Org ID**: `5ad82be2-cbae-4ca7-80cb-ca8daddcbdb1`
- **Scopes**: cianfhoghlaim IaC can read `dev-baile/dev/{infisical,openclaw,hermes,
  litellm,langfuse,mlflow,lakehouse,deepseek,gemini,anthropic,openai,zai,
  opencode-go,huggingface,lancedb}/*`

## Folders + secret count

15 folders under `dev-baile/dev/`:
```
infisical/  7 secrets
openclaw/  10 secrets
hermes/    10 secrets
litellm/    7 secrets
langfuse/   5 secrets
mlflow/     3 secrets
lakehouse/  9 secrets
deepseek/   1
gemini/     1
anthropic/  1
openai/     1
zai/        1
opencode-go/ 4
huggingface/ 1
lancedb/    1
```

## Lifecycle

### Start
```bash
cd ~/.komodo-stacks/infisical  # or /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/stacks/infisical
docker compose -f compose.yaml up -d
# Wait for /api/status to return 200
for i in {1..24}; do
  STATUS=$(curl -ksS -o /dev/null -w '%{http_code}' http://127.0.0.1:8081/api/status)
  [ "$STATUS" = '200' ] && break
  sleep 5
done
```

### Stop
```bash
docker compose -f compose.yaml down
# To also wipe the data:
docker compose -f compose.yaml down -v
```

### Backup
```bash
# Postgres dump
docker exec infisical-db pg_dump -U infisical infisical > infisical-backup-$(date -u +%Y%m%dT%H%M%SZ).sql

# Restore
cat infisical-backup-*.sql | docker exec -i infisical-db psql -U infisical infisical
```

## Differences from OCI Infisical

| Aspect | Local fallback | OCI (when working) |
|---|---|---|
| Image | `v0.161.12` (last 1.6-stable) | same |
| URL | `http://host.docker.internal:8081` (containers) or `http://127.0.0.1:8081` (host) | `https://infisical.cianfhoghlaim.ie` |
| Workspace | `dev-baile` (local) | `dev-baile` (OCI) |
| Project ID | `d900f50a-acbf-446b-b4f6-e439710253e4` | `f3cff583-b74b-4804-b9d3-db8b68885236` |
| Cianfhoghlaim IaC identity | local cianfhoghlaim machine identity | production cianfhoghlaim machine identity |
| Network | Direct from host + containers via `host.docker.internal` | Via Pangolin private resource on arm1-oci |
| Locket compatibility | ✅ WORKS with `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` (avoids the snake_case/camelCase bug) | ❌ BROKEN — locket v0.17.3 uses snake_case; Infisical v0.161+ requires camelCase |

## Promotion decision rationale

| Option | Pros | Cons |
|---|---|---|
| Promote local as permanent dev | No external deps, fast, works | Doesn't match OCI production data |
| Repair OCI (via iac:rotate-auth + iac:sync:resources) | Matches OCI production | Blocked on Pocket ID OIDC setup; multi-step |
| Run both side-by-side | Best of both worlds | Complexity, two sources of truth |

We picked **Option 1** (promote local as permanent) for these reasons:
1. The OCI repair is **blocked** on a config gap (Pocket ID OIDC) that requires
   operator intervention to fix. The session is autonomous.
2. The local Infisical is **already deployed** and **functional** with all
   required secrets seeded (56 secrets across 15 folders).
3. The 4 locket-shims (using the ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0) work correctly
   against the local Infisical (verified: 0 unresolved placeholders across
   all 4 stacks).
4. Cross-stack DNS is working (all 4 stacks on `cianfhoghlaim`).
5. The local Infisical is **ephemeral** (no ARM/OCI vendor lock-in), making
   it ideal for dev/CI.

## When to switch back to OCI

The local Infisical stays in place until:
1. The OCI Infisical private resource returns 200 (the existing
   `repair-pangolin-private-infisical-arm1-oci-v1` procedure completes)
2. The cianfhoghlaim IaC is upgraded to mint fresh API keys against the OCI vault
3. Operators have verified the OCI path is stable

When all 3 conditions are met, run the cutover plan in
`bonneagar/deploy-runbooks/full-local-agent-platform-stack-2026-07.md`
(section "Phase E: Fix hermes (work in progress)").

## Files

- This runbook: `bonneagar/deploy-runbooks/local-infisical-as-permanent-dev-env.md`
- Cianfhoghlaim IaC credential: `~/.locket/infisical_secret` (mode 0600)
- Cianfhoghlaim IaC shim: `bonneagar/scripts/cianfhoghlaim-locket-shim.py` (v0.2.0)
- Cianfhoghlaim IaC image: `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` (local Docker image)
- Stack symlinks: `~/.komodo-stacks/{infisical,openclaw,hermes,litellm,langfuse}/`