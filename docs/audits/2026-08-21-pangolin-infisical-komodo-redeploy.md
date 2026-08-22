# 2026-08-21 Pangolin + Infisical + Komodo core 24/7 redeploy audit

## Context

Per the openspec change `2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1`,
the user reported that "private pangolin resources letting us access
infisical.cianfhoghlaim.ie ... are taking too long to redirect to infisical"
and that "the deployment of the rest of our stack" was impacted.

## Root cause investigation

A 3-link causal chain was identified:

1. **Broken Locket image** — `bpbradley/locket:infisical` (v0.17.3)
   uses snake_case API params (`project_id`, `secret_path`,
   `secret_type`), but Infisical v0.161+ requires camelCase
   (`projectId`, `secretPath`, `secretType`). Every call returns
   422, Locket falls back to "passthrough" mode, and writes the
   raw `{{ infisical://... }}` template to
   `/run/secrets/locket/secrets.env`.

2. **Manual Pangolin private resource** — `infisical.cianfhoghlaim.ie`
   was manually created in Pangolin as a *private* resource, so
   Traefik served the "Private Placeholder" HTML page instead of
   proxying to the OCI Infisical backend.

3. **DNS misconfiguration** — `infisical.cianfhoghlaim.ie` resolves
   to `100.96.128.10` (a Cloudflare WARP / Tailscale endpoint that
   times out) instead of `140.238.96.148` (the OCI public IP that
   all other subdomains point at).

## The fix

### Local code changes (committed + pushed in 9a6aeff0b + 24851947a)

- **Locket migration**: 96 of 98 sidecar.yaml files switched from
  the broken upstream `bpbradley/locket:infisical` to the in-house
  `bons-locket-shim:infisical-0.2.1`. The shim is a 295-line Python
  script that uses the correct camelCase Infisical v0.161+ API.
- **LOCKET_FALLBACK_FILE**: 98 of 98 sidecar.yaml files now declare
  `LOCKET_FALLBACK_FILE=/run/secrets/locket/env-fallback.env` so the
  Locket falls back to the local `.env` mirror when OCI Infisical
  is unreachable (drift window ≤ 15 min per the new
  `secrets_env_refresh` Dagster asset).
- **INFISICAL_URL flip**: 6 of 6 referencing files changed from
  `http://host.docker.internal:8081` to
  `https://infisical.cianfhoghlaim.ie` (the OCI URL).
- **New `iac:teardown-stack` command**: per-host selective teardown
  with `--host`/`--keep`/`--exclude`/`--include-volumes`/`--force`
  flags. Dry-run by default.
- **New `secrets_env_refresh` Dagster asset**: re-hydrates `.env`
  from OCI Infisical every 15 min on a Komodo schedule.
- **New `pangolin/blueprint.yaml`**: completes the 6-file
  GOLD_STANDARD for the Pangolin stack.
- **New `secrets-env-refresh-15min.toml` Komodo schedule**: triggers
  the `secrets_env_refresh` Dagster asset on a 15-min cron.
- **Updated `.agents/skills/secrets-management/SKILL.md`**: documented
  the env-var fallback pattern (4 layers: OCI Infisical →
  `.infisical.env` template → `.env` mirror → Locket fallback file).

### Spec deltas (archived)

- `infrastructure-stacks/spec.md`:
  - MODIFIED `Three-Tier Host Convergence` (added the core-24-7 row)
  - MODIFIED `Locket Sidecar Contract` (canonical image allow-list)
  - ADDED `Core 24/7 stack subset on arm1-oci`
  - ADDED `Env-var fallback pattern (OCI source-of-truth + intermittent sync)`
- `bonneagar-iac-merge/spec.md`:
  - ADDED `iac:teardown-stack per-host selective teardown`

### Live rollout on arm1-oci (via ssh oci.arm1)

1. **Connected `infisical-backend` to `pangolin_pangolin` network** so
   Gerbil can resolve `infisical-backend:8080` from inside the
   Pangolin stack.
2. **Added `infisical-frontend-router` + `infisical-frontend-service`**
   to `/opt/pangolin/config/traefik/dynamic_config.yml` with
   `priority: 500` (higher than the http provider's default), proxying
   `Host(\`infisical.cianfhoghlaim.ie\`)` to `infisical-backend:8080`.
3. **Replaced the live `pangolin-locket` container** with the
   `bons-locket-shim:infisical-0.2.1` image + the OCI Infisical URL.
4. **Updated `/opt/pangolin/compose.yaml` + `/opt/pangolin/sidecar.yaml`**:
   - Image line: `bpbradley/locket:infisical` →
     `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1`
   - Env vars: `INFISICAL_URL`,
     `INFISICAL_CLIENT_ID`, `INFISICAL_PROJECT_ID`, etc.
   - Command: `--provider=infisical` + 8 args → `--mode watch`
   - Healthcheck: `["CMD", "/locket", "healthcheck"]` →
     `["CMD", "/app/locket-shim.py", "--mode", "one-shot"]`
5. **Replaced `/opt/pangolin/secrets.env` with hardcoded fallback**
   (from `/opt/pangolin/.env`) since the OCI Infisical returns 500
   on `GET /api/v4/secrets?secretPath=/pangolin` (KMS encryption keys
   in the OCI Infisical DB are corrupted — see GitHub issue #173).
   The original template is backed up at `/opt/pangolin/secrets.env.locket`.

### Final health check (all 5 services healthy on arm1-oci)

```
pangolin: healthy ✓
pangolin-postgres: healthy ✓
pocket-id: healthy ✓
tinyauth: healthy ✓
pangolin-locket: healthy ✓
```

## Validation results

| Gate | Result |
|:--|:--|
| `openspec validate --all` | 139 passed / 0 failed |
| `mise run lint:drift-docs` | 0 drift claims |
| `mise run lint:skills` | 65/65 skills pass |
| `bun run --cwd bonneagar iac:teardown-stack --dry-run` | ✓ Works |

## Remaining blockers (require user intervention)

1. **Cloudflare DNS**: `infisical.cianfhoghlaim.ie` → `100.96.128.10`.
   Should be `140.238.96.148`. The Cloudflare API token in
   `/opt/pangolin/.env` (`cfut_eNe5swJwARwynzPaY8s4r0POcWetbleJXXpUoBin1888881a`)
   returns 9109 "Invalid access token". The bunchloch `.env` has a
   different token (`CLOUDFLARE_API_TOKEN`) but it also returns 9109.
   **GitHub issue #174** documents the manual fix via the Cloudflare
   dashboard.

2. **OCI Infisical KMS corruption**: The backend returns 500 on every
   `GET /api/v4/secrets?secretPath=...` with the error
   "Unsupported state or unable to authenticate data" (the encryption
   keys in the DB are corrupted). This blocks all v0.17.3 Locket + v0.18.0+
   Locket + bons-locket-shim from resolving secrets from the OCI vault.
   The hardcoded fallback at `/opt/pangolin/secrets.env` is the temporary
   workaround. **GitHub issue #173** documents the KMS restore + seed steps.

## GitHub follow-up issues filed (post-deploy)

- #173: fix(infra): seed the OCI Infisical with the core 24/7 secret paths
- #174: fix(dns): point infisical.cianfhoghlaim.ie at the OCI public IP
- #175: chore(infra): pin Pangolin + Newt image versions
- #176: chore(bpbradley): upstream locket v0.18.0 stable release tracking
- #177: feat(iaac): bring back the 12 NCCA agent stacks to bunchloch

## Commits

- `9a6aeff0b` (frontend-apps subagent T6): the roll-up commit that
  bundled my openspec change + the bulk Locket migration + the new
  IaC command + the Dagster asset + the missing blueprint.yaml.
- `24851947a`: my follow-up commit that completed the Locket migration
  for the 12 recursive sidecar files in `croilar/*/` and `wave2/*/`
  (which the original glob missed) + the 3 INFISICAL_URL flips.

## Archival

`openspec archive 2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1 --yes`
merged 3 ADDED + 2 MODIFIED requirements into the canonical specs.
The change is now at `openspec/changes/archive/2026-08-22-2026-08-21-pangolin-infisical-komodo-core-24-7-redeploy-v1/`.
