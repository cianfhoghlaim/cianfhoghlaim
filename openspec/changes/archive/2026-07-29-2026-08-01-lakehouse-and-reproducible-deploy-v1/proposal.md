# 2026-08-01-lakehouse-and-reproducible-deploy-v1

## Why

The data plane + the full 91-stack platform each have one critical
gap. Together they block any "bring up the whole platform from a fresh
host" workflow.

1. **The lakehouse external network is wrong.** The lakehouse stack
   declares `lakehouse: driver: bridge` (a local bridge). 9 downstream
   stacks (langfuse, mlflow, litellm, cognee, dagster, marimo,
   oideachais, graphiti, agent-os) declare
   `lakehouse: name: lakehouse_lakehouse, external: true`. The local
   bridge and the external net have **no endpoint** between them.
   This is the #1 critical gap.
2. **MotherDuck token is duplicated; mode knobs not exported.** The
   token lives at 2 different Infisical paths (`lakehouse/token` and
   `oideachais/motherduck/token`); `MOTHERDUCK_MODE` + `MOTHERDUCK_DATABASE`
   + `MOTHERDUCK_S3_*` are not exported by any stack, blocking the
   2026-08-12 `biep-v3-motherduck-flights-v1` change.
3. **DUCKLAKE_BUCKET name doesn't match.** `destinations_cianfhoghlaim.py`
   defaults to `ducklake-cianfhoghlaim`; `garage-init` creates
   `ducklake`. Two different strings — silent bucket-name mismatch
   risk.
4. **No one-command deploy orchestrator.** Closest existing is
   `iac:bootstrap` (covers control plane only). For a fresh bunchloch
   host, the operator must execute 6+ separate commands in the right
   order. The 3 dead standalone stacks (garage, lakekeeper, lakefs)
   are still on disk and would confuse the operator.

This change ships the full data-plane fix + the `deploy:full`
orchestrator (shell entry + TS state machine) + the 3 dead-stack
deletions. All 4 fixes are bundled into one change per the locked
plan (the user explicitly chose "Bundle all 4 fixes into Change 3").

## What changes

### Sub-area A — Lakehouse external network (the #1 critical gap)

- **MODIFIED**: `bonneagar/stacks/lakehouse/compose.yaml` lines 567-572 —
  rename local `lakehouse` bridge to `external: true, name: lakehouse_lakehouse`.
  This unblocks the 9 downstream stacks.

### Sub-area B — MotherDuck token dedup + mode exports

- **MODIFIED**: `bonneagar/stacks/lakehouse/secrets.env` — remove the
  duplicate `MOTHERDUCK_TOKEN=infisical://dev-baile/lakehouse/token`
  line (already exists). The canonical path is
  `dev-baile/motherduck/token` (the KCG-canonical path per the
  motherduck skill).
- **MODIFIED**: 5 data-plane stacks (`lakehouse`, `oideachais`,
  `dagster`, `motherduck`, `marimo`) — add 4 MOTHERDUCK_* env vars to
  each `secrets.env`:
  - `MOTHERDUCK_MODE` (default `byob`)
  - `MOTHERDUCK_DATABASE` (default `cianfhoghlaim`)
  - `MOTHERDUCK_S3_BUCKET` (default `ducklake`)
  - `MOTHERDUCK_S3_ENDPOINT` (default `http://lakehouse-garage:3900`)

### Sub-area C — DUCKLAKE_BUCKET reconciliation

- **MODIFIED**: `bonneagar/stacks/lakehouse/compose.yaml` (the
  `garage-init` service) — rename the auto-created bucket from
  `ducklake` to `ducklake-cianfhoghlaim` (matching the
  destinations_cianfhoghlaim.py default).
- **MODIFIED**: `dlt_sources/common/destinations_cianfhoghlaim.py`
  line 109 — keep the default as `ducklake-cianfhoghlaim` (no change
  to default; just confirming the alignment).

### Sub-area D — Embedder exports

- **MODIFIED**: 5 data-plane stacks (`lakehouse`, `oideachais`,
  `dagster`, `motherduck`, `marimo`) — add 2 env vars to each
  `secrets.env`:
  - `CIANFHOGHLAIM_EMBED_MODEL` (default `BAAI/bge-m3`)
  - `CIANFHOGHLAIM_EMBED_DIM` (default `1024`)
- Only `cocoindex/_shared/_lifespan.py` reads these today; this
  change lets any operator swap embedders via env.

### Sub-area E — Skill refresh

- **MODIFIED**: `.agents/skills/dlt/SKILL.md` — align the 5 env-var
  contract with current code (the canonical destinations_cianfhoghlaim.py
  helpers + motherduck_options.py)
- **MODIFIED**: `.agents/skills/dagster/SKILL.md` — align with the
  post-v7 `dg.toml` (1 location, not 5); update the KCG port list
  (Lance Namespace `:9000` → `:8182`)
- **MODIFIED**: `.agents/skills/motherduck/SKILL.md` — align with
  `md:cianfhoghlaim` canonical alias (was `md:oideachais`)

### Sub-area F — `deploy:full` orchestrator (shell + TS)

- **NEW**: `scripts/deploy-full.sh` (~300 LOC) — 7-phase state machine
  + healthchecks + resumability hooks:
  1. preflight-arm-oci
  2. control-plane-up (infisical + pangolin + komodo + pocket-id + tinyauth)
  3. lakehouse-up (postgres + garage + clickhouse + redis + lakekeeper + lance-namespace)
  4. data-stacks-up (litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb)
  5. agent-surfaces-up (openclaw + openchamber + hermes)
  6. dagster-materialize (BIEP v3 upstream + downstream)
  7. dagster-sensor-health-gate (ocr_completion_sensor + 5 others active)
- **NEW**: `scripts/deploy-full.ts` (~500 LOC) — TypeScript orchestrator
  with a 7-phase state machine, resumable checkpoints
  (`~/.cianfhoghlaim/deploy-state.json`), and the full set of
  `iac:*` calls. Calls existing `cianfhoghlaim-cli.ts` commands.
- **MODIFIED**: `mise.toml` — add the `[tasks.deploy:full]` alias
  pointing at the shell entry.

### Sub-area G — Standalone stack deletions

- **REMOVED**: `bonneagar/stacks/garage/` (predecessor dxflrs/garage:v1.0.1;
  superseded by lakehouse's v2.3.0)
- **REMOVED**: `bonneagar/stacks/lakekeeper/` (predecessor standalone;
  superseded by lakehouse's `lakekeeper-migrate` + `lakekeeper` services)
- **REMOVED**: `bonneagar/stacks/lakefs/` (never wired to the data
  plane; superseded by Lakekeeper)

### Sub-area H — External-network dedup verification

- **VERIFIED**: `langfuse/compose.yaml`, `mlflow/compose.yaml`,
  `litellm/compose.yaml` all declare `lakehouse: name: lakehouse_lakehouse,
  external: true` — Sub-area A makes this declaration match reality.

## Definition of done

- [ ] All 8 sub-areas above land
- [ ] `openspec validate 2026-08-01-lakehouse-and-reproducible-deploy-v1 --strict` passes
- [ ] `mise run stack-doctor:strict` reports zero grammar regressions
- [ ] `docker compose -f lakehouse/compose.yaml -f lakehouse/sidecar.yaml config --quiet` passes
- [ ] `bash -n scripts/deploy-full.sh` succeeds
- [ ] `bun run scripts/deploy-full.ts --dry-run` succeeds
- [ ] 1 commit lands on the working branch
- [ ] Push succeeds

## Dependencies

- **Blocked by**: `2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1`
  (the `deploy:full` orchestrator depends on the agentic mesh being
  coherent — the openclaw/openchamber/hermes cluster must be handoff-
  aware before the orchestrator brings it up)
- **Blocks**: any future change that wants to swap embedders, add a
  new BIEP v3 jurisdiction, or migrate to `managed` MotherDuck hosting

## Why a single change (not 4)?

Sub-areas A–H are deeply co-dependent:

- (B) requires (C) — MOTHERDUCK_S3_BUCKET and DUCKLAKE_BUCKET share the
  same Garage bucket; reconciling one forces the other
- (F) requires all of (A)/(B)/(D)/(E) — the orchestrator needs the
  lakehouse network + MotherDuck knobs + embedder envs + skill
  refresh before it can confidently bring up the platform
- (G) requires (H) — the 3 dead-stack deletions must happen alongside
  the network externalisation (otherwise langfuse/mlflow/litellm
  might still reference the standalone garage network name)

Splitting into 8 PRs would require 8 rebases against this same
change. One PR, ~22 file diffs (with 3 deletions), lands cleanly.

## Cross-repo sync

This change touches only this repo (cianfhoghlaim). No
`cross-repo-sync.md` needed.