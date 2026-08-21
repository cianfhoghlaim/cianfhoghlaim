# Change: Pangolin + Infisical + Komodo core 24/7 redeploy (arm1-oci) + Locket migration + env-var fallback

## Why

The 4 documented blockers in `bonneagar/DEPLOYMENT-STRATEGY.md` §4 plus the upstream `bpbradley/locket v0.17.3` camelCase bug plus the 88 non-core stacks consuming Oracle Cloud ARM free-tier's 24 GB RAM converge to make the OCI control plane fragile and slow to respond. The operator has been experiencing slow redirects on `infisical.cianfhoghlaim.ie` + `pangolin.cianfhoghlaim.ie` and broken secret hydration across most stacks. The fix is a phased redeploy of the 12-service core 24/7 set, a 71-file Locket migration from broken upstream to the in-house shim, and the introduction of an env-var fallback pattern that replaces the parallel local Infisical instance with a single-source-of-truth (OCI) plus an intermittent `.env` mirror.

## The 4 documented blockers — current state (verified by Phase 0 audit)

| # | Blocker | Current state | Fix in this change |
|:-:|:--|:--|:--|
| 1 | Newt 1.12.5 + Pangolin 1.18.4 incompatibility ("CLIENTS WILL NOT WORK ON THIS VERSION OF NEWT WITH THIS PANGOLIN SERVER") | **ACTIVE** — `pangolin/compose.yaml` uses `fosrl/pangolin:ee-latest` (unpinned); `stacks/newt/newt.yaml` has the Newt image | Pin both to compatible versions per the upstream compat matrix |
| 2 | 4 manually-created private resources (`komodo`, `cal-diy`, `infisical`, `openchamber`) shadow the IaC blueprints | **ACTIVE** — `MANUAL_OVERRIDE_NICE_IDS = new Set(["komodo", "cal-diy", "infisical", "openchamber"])` is set in `iac/commands/sync-resources.ts`; just needs to run | `mise run iac:sync:resources` |
| 3 | `PANGOLIN_API_KEY` + `PANGOLIN_API_KEY_0` in `.env` returns 401 | **ALREADY FIXED** — only `PANGOLIN_API_KEY="e8rr..."` in `.env`; no duplicate | — |
| 4 | `komodo-locket` sidecar fails: `error: invalid value '${INFISICAL_CLIENT_ID}'` (YAML escape) | **ALREADY FIXED** — no `$${INFISICAL_CLIENT_ID}` pattern in `komodo/compose.yaml` or `komodo/sidecar.yaml` | — |

## The Locket coverage crisis (newly discovered by Phase 0 audit)

Empirical `grep` of all 94 `sidecar.yaml` files in `bonneagar/stacks/`:

| Image | Count | Status |
|:--|--:|:--|
| `ghcr.io/bpbradley/locket:infisical` (upstream v0.17.3 — BROKEN) | **71** | Snake_case `project_id`/`secret_path`/`secret_type` → Infisical v0.161+ returns 422 → Locket falls back to "passthrough" mode → writes the raw `{{ infisical://... }}` template instead of the resolved value |
| `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.1` (in-house shim — WORKS) | 11 | Known-good against Infisical v0.161+ |
| `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` (older) | 1 | Slightly stale |

**Critically, the `pangolin` + `infisical` + `forgejo` stacks themselves use the BROKEN upstream** — meaning the secrets that the OCI control plane needs at startup never hydrate. The 11 working stacks are: `cognee`, `hermes`, `komodo`, `langfuse`, `litellm`, `mlflow`, `newt-arm1-oci`, `ocr-router`, `openchamber`, `openclaw`, `unsloth-serve`.

Upstream `bpbradley/locket v0.18.0` stable has NOT shipped (only `v0.18.0-rc.1` (2026-07-10) and `v0.18.0-rc.2` (2026-07-17) exist as pre-releases; verified via <https://github.com/bpbradley/locket/releases>). The redeploy MUST migrate the 71 broken sidecars to the in-house shim now; a follow-up task switches to upstream `v0.18.0` once stable ships.

## The local-fallback re-architecture

Currently the local Infisical on `bunchloch` (`infisical-backend` + `infisical-db` + `infisical-redis` — all Up 7 days per `docker ps`) is serving 6+ sidecars via `INFISICAL_URL=http://host.docker.internal:8081`. Maintaining two Infisicals is operationally complex — the 2026-07-24 deployment showed the local instance required multiple manual re-seedings during the OCI repair window. Drift between OCI and local is unbounded.

This change introduces a new pattern: **OCI Infisical = single source of truth**, with a **local `.env` fallback** (the canonical pattern already documented in `SECRETS-MANAGEMENT.md`) hydrated by an **intermittent sync** via a new Dagster asset `secrets_env_refresh`. The drift window is bounded to ~15 min (the sync interval) instead of the unbounded drift of a parallel local Infisical.

The 6 currently-healthy Locket sidecars on bunchloch (`cognee-locket`, `mlflow-locket`, `openclaw-locket`, `litellm-locket`, `hermes-locket`, `infisical-backend`'s deps) get torn down in Phase 2 alongside the rest of the non-core stacks, and the stacks themselves come back via Phase 3 with `INFISICAL_URL=https://infisical.cianfhoghlaim.ie`.

## What changes

8 phases, ~2.5 hours of execution time:

1. **Phase 1** — Repair the 2 remaining blockers (Pangolin + Newt version pinning + `iac:sync:resources`)
2. **Phase 2** — Tear down 88 non-core stacks + the local Infisical via the new `iac:teardown-stack` command
3. **Phase 3** — Redeploy the 12-service core 24/7 (4 core stacks + 2 bundled services + 6 resource-sync-managed services)
4. **Phase 4** — Install the Pangolin machine client (Newt) + Komodo Periphery on `bunchloch`
5. **Phase 5** — Add the missing `pangolin/blueprint.yaml` (the 1 missing GOLD_STANDARD file for the core 4)
6. **Phase 6** — Locket migration: rewrite the 71 broken `sidecar.yaml` files
7. **Phase 6b** — Env-var fallback pattern: new `secrets_env_refresh` Dagster asset + flip every `INFISICAL_URL`
8. **Phase 7** — Validation: `mise run core:ci` + `mise run iac-health` + `probe-public-urls.sh`

The change ships:

- **1 NEW IaC command** — `iac:teardown-stack` (per-host, selective, with `--keep`/`--exclude`/`--include-volumes`/`--force` flags)
- **1 NEW Dagster asset** — `secrets_env_refresh` (every 15 min, in the `secrets` group of the `4_asset_generation` defs tree)
- **71 file edits** — the Locket migration (every `sidecar.yaml` using the broken upstream → in-house shim)
- **1 file creation** — `bonneagar/stacks/pangolin/blueprint.yaml`
- **~10 file edits** — every `sidecar.yaml` + `.env.example` referencing `INFISICAL_URL=http://host.docker.internal:8081` → `https://infisical.cianfhoghlaim.ie`
- **5 spec deltas** — 1 MODIFIED + 3 ADDED to `infrastructure-stacks`; 1 ADDED to `bonneagar-iac-merge`

## Dependencies

`Blocked by: 2026-08-13-bonneagar-infra-remediation-v3` (the prerequisite change that fixes the `storage-infrastructure.toml:14` repo drift and adds the `Resource-sync repo-namespace consistency` requirement). The Phase 0 audit confirms all 4 resource-sync TOML files at `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting,storage-infrastructure}.toml` now declare `repo = "cianfhoghlaim/bonneagar"`, so the constraint is satisfied.

`Affected repos: cianfhoghlaim (single repo)`.

## Impact

- **Specs affected**:
  - MODIFIED `infrastructure-stacks/spec.md` — `Requirement: Three-Tier Host Convergence` (add the core-24-7 row to the table) + `Requirement: Locket Sidecar Contract` (add the `bons-locket-shim:infisical-0.2.1` + upstream-v0.18.0+ allow-list)
  - ADDED `infrastructure-stacks/spec.md` — 2 new Requirements (`Core 24/7 stack subset on arm1-oci`, `Env-var fallback pattern`)
  - ADDED `bonneagar-iac-merge/spec.md` — 1 new Requirement (`iac:teardown-stack per-host selective teardown`)
- **Code affected**:
  - 1 NEW IaC command: `bonneagar/iac/commands/teardown-stack.ts` + registration in `iac/cli.ts` + `bonneagar/package.json` `scripts` block
  - 1 NEW Dagster asset: `orchestration/defs/secrets_env_refresh.py` + registration in the defs tree
  - 71 file edits: every `sidecar.yaml` using `bpbradley/locket:infisical` → `bons-locket-shim:infisical-0.2.1`
  - 1 file creation: `bonneagar/stacks/pangolin/blueprint.yaml`
  - ~10 file edits: every `sidecar.yaml` + `.env.example` referencing `INFISICAL_URL=http://host.docker.internal:8081` → `https://infisical.cianfhoghlaim.ie`
  - The local Infisical containers torn down (postgres + redis + backend) per the env-var fallback decision
- **Risk**: medium — tears down 88 stacks + the local Infisical; re-deployable from the 6-file GOLD_STANDARD files on disk + the IaC; the new `secrets_env_refresh` asset covers offline dev (15-min drift window).
- **Drift bound**: the env-var fallback drift is bounded to ~15 min (the `secrets_env_refresh` schedule); the parallel-local-Infisical pattern would have unbounded drift.
- **Compatibility**: stays on the in-house shim (`bons-locket-shim:infisical-0.2.1`) until upstream `bpbradley/locket v0.18.0` ships stable; a follow-up GitHub issue tracks the upstream migration.

## Cross-references

- `bonneagar/DEPLOYMENT-STRATEGY.md` — the 4 documented blockers (now 2 active, 2 already fixed)
- `bonneagar/PANGOLIN-SETUP.md` — the canonical Pangolin bring-up (Pangolin EE + Traefik + Gerbil + Pocket ID + Tinyauth)
- `bonneagar/SECRETS-MANAGEMENT.md` — the Infisical + mise + Locket 3-way contract
- `bonneagar/deploy-runbooks/repair-pangolin-private-infisical-2026-07.md` — the 1-command repair (`km run procedure repair-pangolin-private-infisical-arm1-oci-v1`)
- `bonneagar/deploy-runbooks/local-infisical-as-permanent-dev-env.md` — the prior local-fallback decision (now superseded by the env-var fallback pattern)
- `bonneagar/iac/commands/sync-resources.ts` — the DELETE-then-CREATE for the 4 manually-created resources
- `bonneagar/iac/commands/bootstrap-pangolin-client.ts` — the canonical Newt install path (Phase 4)
- `bonneagar/locket-shim/cianfhoghlaim-locket-shim.py` — the in-house Locket (v0.2.1, camelCase-correct)
- `openspec/specs/infrastructure-stacks/spec.md` — the canonical spec (gets 1 MODIFIED + 2 ADDED Requirements)
- `openspec/specs/bonneagar-iac-merge/spec.md` — the IaC spec (gets 1 ADDED Requirement)
- `openspec/changes/2026-08-13-bonneagar-infra-remediation-v3/` — the `Blocked by` prerequisite
