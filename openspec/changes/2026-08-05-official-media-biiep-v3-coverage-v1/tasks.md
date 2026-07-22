# 2026-08-05-official-media-biiep-v3-coverage-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify B4 (web app routes) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Add 5 jurisdiction sub-assets (closes #47)

- [ ] Edit `dlt/official_media/source_resolver.py` — add 5 resolvers:
  - Scotland (Scottish Parliament)
  - Wales (Senedd Cymru)
  - Northern Ireland (already partial — add Tynwald)
  - Jersey
  - Guernsey
- [ ] Edit `dlt/official_media/classifier.py` — add 5 BAML targets
- [ ] Add 5 new Dagster assets under
  `orchestration/defs/2_materials/official_media/` (1 per jurisdiction)

## Stage 2 — side-loadable PWA (closes #48)

- [ ] `mkdir -p web/apps/official-media-pwa/`
- [ ] Create the PWA manifest + service worker
- [ ] Create iOS / Android wrappers via Tauri or Capacitor
- [ ] Wire the PWA to the `official-media` Hono API endpoint
- [ ] Add `mise run pwa:dev` + `mise run pwa:build` tasks

## Stage 3 — HMGCC co-creation sub-asset (closes #49)

- [ ] `mkdir -p dlt/official_media/hmgcc/`
- [ ] Create the 12-week rolling window source
- [ ] Wire to the existing `classifier.py` with `source: hmgcc` tag
- [ ] Add the `hmgcc_rolling_window` Dagster asset

## Stage 4 — Companies House re-identification (closes #50)

- [ ] Create `dlt/official_media/companies_house_crown_filter.py`
- [ ] Add the canonical 6 Crown bodies registry
- [ ] Add the `crown_body: true` filter logic
- [ ] Add the corresponding Dagster asset

## Stage 5 — Deplatforming-thesis paper (closes #51)

- [ ] Create `docs/theses/deplatforming_thesis.md`
- [ ] 1-page executive summary + 10-section outline
- [ ] Cross-reference the existing `regulating_big_tech_in_british_isles.pdf`
- [ ] Add to `docs/THESES.md` index

## Stage 6 — meaisinfhoghlaim web analyzer (closes #35)

- [ ] `mkdir -p web/apps/cianfhoghlaim-web/src/routes/analyzer/`
- [ ] Create the TanStack Start analyzer page
- [ ] Wire to the meaisinfhoghlaim-web Hono endpoint

## Stage 7 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-05-official-media-biiep-v3-coverage-v1/specs/official-media-pipeline/spec.md`
- [ ] Run `openspec validate 2026-08-05-official-media-biiep-v3-coverage-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-05-official-media-biiep-v3-coverage-v1 --yes`

## Stage 8 — Close the GitHub issues

- [ ] `gh issue close 47 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`
- [ ] `gh issue close 48 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`
- [ ] `gh issue close 49 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`
- [ ] `gh issue close 50 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`
- [ ] `gh issue close 51 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`
- [ ] `gh issue close 35 --comment "Closes via 2026-08-05-official-media-biiep-v3-coverage-v1"`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol