# Change: 2026-07-06-deploy-infisical-bunchloch-local

## Why

The Cianfhoghlaim `infrastructure-stacks` capability requires Infisical as the
single root-of-trust for all 5 consumer stacks (lakehouse, litellm, mlflow,
unstract, plus the deferred paddleocr). Today Infisical is documented to run on
`arm1-oci` (per `bonneagar/AGENTS.md` "5-group model"); running it on
`bunchloch` lets the MacBook operator develop + demo the data plane without
tunneling through Pangolin/WireGuard.

Verified 2026-07-06:
- `docker ps` shows 0 infisical-* containers on bunchloch
- `bonneagar/stacks/infisical/compose.yaml` uses `infisical/infisical:latest`
  (forbidden by Image Pinning Policy in `infrastructure-stacks/spec.md`)
- The same file declares `network: infrastructure` external — that net does
  NOT exist on bunchloch (it exists only on arm1-oci)
- `bonneagar/stacks/infisical/secrets.env` uses the forbidden Jinja
  `{{ infisical://... }}` form (forbidden by `agent-observability/spec.md`
  §"Infisical URI Format Conformance")
- Research at https://github.com/Infisical/infisical/releases confirms
  `v0.161.12` is the latest stable (2026-07-03), tracks the CLI release line
  the `secrets-management` skill documents (v0.161.9 from 2026-06-26)

## What changes

- 1 new `compose.yaml` rewrite: 3 semver-pinned images, replaced `infrastructure`
  external network with `bunchloch-infra` external network, added 5 required
  env vars (`ENCRYPTION_KEY`, `AUTH_SECRET`, `DB_CONNECTION_URI`, `REDIS_URL`,
  `SITE_URL`, `HOST=0.0.0.0`)
- 1 new `secrets.env` rewrite: drops the Jinja wrapper, uses raw
  `infisical://dev-baile/infisical/...` form (compatible with the Locket
  sidecar — though Infisical itself does NOT use a Locket sidecar; the
  `infisical/secrets.env` only declares backend env vars for `db` + `redis`
  which read them directly)
- 1 new `pangolin.yaml` file (currently the stack only has `blueprint.yaml`;
  the agent-observability spec requires both)
- 1 new runbook `bonneagar/deploy-runbooks/bunchloch-infisical-data-plane-2026-07.md`
  (cold-boot instructions for Infisical + Phase 2-4 lakehouse + consumer stacks)
- 1 new bootstrap script `bonneagar/scripts/seed-infisical-vault.sh` —
  openssl-random-generator for every secret + `infisical secrets` CLI push
  into the new `dev-baile` project
- 0 Komodo / Pangolin routing changes (Infisical on bunchloch stays
  Locket-less, port 8081 exposed to host only — not routed via Pangolin
  WireGuard)

## Impact

- **Affected specs:** `infrastructure-stacks` (shared) + `agent-observability`
  (shared, for the §"Infisical URI Format Conformance" Scenario)
- **Affected hosts:** `bunchloch` only
- **Risk:** low (fresh-infra, no production secrets written; rolled back with
  `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`)
- **Audit gates:** `openspec validate <id> --strict` + `bun run validate-stacks`
  + `mise run lint:skills`
- **Disk:** ~750 MB pulled (infisical backend image ~250 MB, postgres 16 ~80 MB,
  redis 7.4 ~40 MB; rest from layer cache)
- **RAM headroom:** Infisical backend uses ~250 MB resident idle; postgres + redis
  ~150 MB combined. Comfortable on M4.

## Non-goals

- Not exposing Infisical via Pangolin (arm1-oci only)
- Not migrating the existing production `dev-baile` vault — we are creating a
  fresh, local-only vault with fresh secrets
- Not yet wiring Infisical into the 5 consumer stacks (Change 2)
- Not switching the mise tool pin `infisical = "latest"` to a semver — the
  CLI release line is tracked separately at the user level

## Spec delta

See `specs/infrastructure-stacks/spec.md` for the ADDED Requirements
governing the local Infisical vault + the MODIFIED Requirements to
`agent-observability` §"Infisical URI Format Conformance" (the Scenario
count grows from 1 to 4 to cover the 4 spec-violations already on disk).

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Switch mise `infisical = "latest"` pin to `= "v0.161.x"` | `2026-07-XX-mise-pin-infisical-semver` |
| Re-vendor Infisical compose whenever v0.162 ships | `2026-07-XX-infisical-v0.162-bump` |
| Cross-host shared vault (so bunchloch ↔ arm1-oci share secrets) | `2026-07-XX-shared-infisical-vault` |
| PaddleOCR remediation (deferred from Change 2) | `2026-07-XX-paddleocr-remediation` |