# Tasks: 2026-08-01-lakehouse-and-reproducible-deploy-v1

15 actions across 8 sub-areas. Each task is independently shippable as a commit.

## Sub-area A — Lakehouse external network (#1 critical gap)

- [ ] **A.1** Edit `bonneagar/stacks/lakehouse/compose.yaml` lines 567-572: rename local `lakehouse` bridge to `external: true, name: lakehouse_lakehouse`

## Sub-area B — MotherDuck token dedup + mode exports

- [ ] **B.1** Edit `bonneagar/stacks/lakehouse/secrets.env`: remove duplicate `MOTHERDUCK_TOKEN=infisical://dev-baile/lakehouse/token` line (keep the canonical `dev-baile/motherduck/token` from oideachais)
- [ ] **B.2** Edit 5 data-plane stacks `secrets.env` to add `MOTHERDUCK_MODE` + `MOTHERDUCK_DATABASE` + `MOTHERDUCK_S3_BUCKET` + `MOTHERDUCK_S3_ENDPOINT`:
  - `lakehouse/secrets.env`
  - `oideachais/secrets.env`
  - `dagster/secrets.env`
  - `motherduck/secrets.env`
  - `marimo/secrets.env`

## Sub-area C — DUCKLAKE_BUCKET reconciliation

- [ ] **C.1** Edit `bonneagar/stacks/lakehouse/compose.yaml` (the `garage-init` service): rename auto-created bucket from `ducklake` to `ducklake-cianfhoghlaim`

## Sub-area D — Embedder exports

- [ ] **D.1** Edit the same 5 data-plane stacks `secrets.env` to add `CIANFHOGHLAIM_EMBED_MODEL=BAAI/bge-m3` + `CIANFHOGHLAIM_EMBED_DIM=1024`

## Sub-area E — Skill refresh

- [ ] **E.1** Refresh `.agents/skills/dlt/SKILL.md` — align the 5 env-var contract with current destinations_cianfhoghlaim.py + motherduck_options.py
- [ ] **E.2** Refresh `.agents/skills/dagster/SKILL.md` — align with post-v7 `dg.toml` (1 location, not 5); update Lance Namespace port `:9000` → `:8182`
- [ ] **E.3** Refresh `.agents/skills/motherduck/SKILL.md` — align with canonical `md:cianfhoghlaim` alias (was `md:oideachais`)

## Sub-area F — deploy:full orchestrator (shell + TS)

- [ ] **F.1** Write `scripts/deploy-full.sh` (~300 LOC) — 7-phase state machine + healthchecks + resumability hooks
- [ ] **F.2** Write `scripts/deploy-full.ts` (~500 LOC) — TypeScript orchestrator with a 7-phase state machine + `~/.cianfhoghlaim/deploy-state.json` checkpoints; calls `cianfhoghlaim-cli.ts` + `iac:*` commands
- [ ] **F.3** Edit `mise.toml`: add `[tasks.deploy:full]` alias to `scripts/deploy-full.sh` (the TS orchestrator is internal; the shell entry is the user-facing surface)

## Sub-area G — Standalone stack deletions

- [ ] **G.1** Delete `bonneagar/stacks/garage/` (predecessor dxflrs/garage:v1.0.1; superseded by lakehouse)
- [ ] **G.2** Delete `bonneagar/stacks/lakekeeper/` (predecessor; superseded)
- [ ] **G.3** Delete `bonneagar/stacks/lakefs/` (never wired; superseded by Lakekeeper)

## Sub-area H — External-network dedup verification

- [ ] **H.1** Verify `langfuse/compose.yaml`, `mlflow/compose.yaml`, `litellm/compose.yaml` already declare `lakehouse: name: lakehouse_lakehouse, external: true` (Sub-area A makes the declaration match reality). No code change needed; just a verification line in the commit message.

## Final verification

- [ ] `openspec validate 2026-08-01-lakehouse-and-reproducible-deploy-v1 --strict` passes
- [ ] `mise run stack-doctor:strict` reports zero grammar regressions
- [ ] `docker compose -f lakehouse/compose.yaml -f lakehouse/sidecar.yaml config --quiet` passes
- [ ] `bash -n scripts/deploy-full.sh` succeeds
- [ ] `bun run scripts/deploy-full.ts --dry-run` succeeds
- [ ] `mise run lint:skills` passes (53/53 skills still validate)
- [ ] Git commit lands; push succeeds

## Dependency graph

```
A.1 ────────────────────────────────────┐
                                        │
B.1 ──► B.2 (5 stacks) ──┐               │
                         ├──► C.1 ──────┤
D.1 (same 5 stacks) ─────┤               │
                         │               │
E.1 ──► E.2 ──► E.3 ──────┤               │
                         │               ▼
F.1 ──► F.2 ──► F.3 ──────┼──► H.1 ──► openspec validate --strict
                         │               │
G.1 ──► G.2 ──► G.3 ──────┘               ▼
                                          commit + push