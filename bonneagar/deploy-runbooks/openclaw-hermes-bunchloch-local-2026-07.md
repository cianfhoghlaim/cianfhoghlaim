# OpenClaw + Hermes — Bunchloch Local Fallback Deploy (2026-07-24)

## When to use

Use this runbook when:
- `https://infisical.cianfhoghlaim.ie/api/status` returns 502 Bad Gateway
  (the Pangolin private resource on arm1-oci is unhealthy)
- You need to bring up `openclaw` + `hermes` on the `bunchloch` MacBook
  without waiting for the OCI path to be repaired
- You have followed the prerequisite openspec change
  `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`

**Do NOT use this runbook if the OCI path is healthy.** The canonical
path is `km run procedure deploy-openclaw-bunchloch`, which depends
on a working Pangolin mesh + arm1-oci Infisical.

## 5-command quick-start

```bash
# 0. Verify the OCI path is genuinely broken (NOT the bunchloch side)
mise run preflight:arm-oci --skip-namespace  # expect "Infisical health: FAIL (502)"

# 1. Bring up local Infisical
docker network create bunchloch-infra || true
cd bonneagar/stacks/infisical && docker compose -f compose.yaml -f sidecar.yaml up -d
# wait for http://127.0.0.1:8081/api/status -> 200 (browser sign-up first user)

# 2. Seed the fallback vault
INFISICAL_PROJECT_ID=<UUID> INFISICAL_CLIENT_ID=<id> INFISICAL_CLIENT_SECRET=<secret> \
  bun run scripts/seed-bunchloch-fallback-vault.sh

# 3. Install locket + verify it resolves secrets
mise run iac:bootstrap-locket-binary
locket healthcheck  # expect >= 16 secrets resolved

# 4. Bring up the agent surfaces
cd ../openclaw && docker compose -f compose.yaml -f sidecar.yaml up -d
cd ../hermes   && docker compose -f compose.yaml -f sidecar.yaml up -d

# 5. Health checks
curl -fsS http://openclaw:18789/api/health
curl -fsS http://hermes:9119/api/health
```

## Prerequisites

- bunchloch has >= 25 GB free disk + >= 2 GB RAM headroom
- `mise install` has been run (mise.toml pins: bun 1.x, uv 0.x, docker)
- The `infisical` CLI is installed (mise install puts it on PATH)
- The bons-iac Universal Auth credentials have been captured from a
  browser session at `http://127.0.0.1:8081`

## How it works (the 5 layers)

| Layer | Component | Purpose |
|---|---|---|
| 1 | `docker network create bunchloch-infra` | External bridge network shared by Infisical + Locket sidecars + openclaw + hermes |
| 2 | `bonneagar/stacks/infisical/` | Local Infisical backend (port 8081) + postgres 16 + redis 7.4 |
| 3 | `seed-bunchloch-fallback-vault.sh` | Writes 21 secrets under `dev-baile/dev` + the bons-iac credential to `/etc/komodo/secrets/infisical_secret` |
| 4 | Locket sidecar in each stack's `sidecar.yaml` | Watches Infisical, resolves secrets to `stack-secrets:/run/secrets/locket/secrets.env` |
| 5 | `openclaw` + `hermes` containers | `env_file: /run/secrets/locket/secrets.env` resolves at container start (NOT at compose-parse) because Locket has pre-populated the tmpfs volume |

## Tear down (once the OCI path is repaired)

```bash
cd bonneagar/stacks/infisical && docker compose -f compose.yaml -f sidecar.yaml down -v
docker network rm bunchloch-infra || true
docker ps --filter name=infisical  # expect 0
```

The OCI repair itself is the follow-up openspec change
`2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`.

## Related

- Change: `2026-07-24-deploy-openclaw-hermes-bunchloch-local-infisical-fallback-v1`
- Follow-up: `2026-07-24-iac-sync-sites-pangolin-private-infisical-repair-v1`
- Spec: `infrastructure-stacks` §"Bunchloch fallback Infisical vault"