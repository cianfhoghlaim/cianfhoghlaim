# 2026-08-05-marimo-wasm-and-cigrunners-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify B4 (web app) + B5 (notebook dashboards) merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Marimo WASM export (closes #54)

- [ ] Create `scripts/marimo_wasm_export.py` — converts each `.py` notebook
  to a WASM bundle + a JSON manifest
- [ ] Output to `web/apps/cianfhoghlaim-web/public/notebooks/`
- [ ] Add the manifest publisher (`.github/workflows/marimo-wasm-publish.yaml`)
- [ ] Apply the canonical Cianfhoghlaim theme to the WASM bundles
- [ ] Each `notebooks/{18,19,20,21,22,23,40}_*.py` exports to a route at
  `/notebooks/{18,19,20,21,22,23,40}_*` in the web app
- [ ] Add `mise run marimo:wasm:export` + `mise run marimo:wasm:publish` tasks

## Stage 2 — Wire testRuns.ingest to CI runners (closes #34)

- [ ] Create `scripts/test_runs_ingest.py` script
- [ ] Wire testRuns.ingest call to the meaisinfhoghlaim agent fleet
- [ ] Every CI run on `main` calls `testRuns.ingest(passed=..., failed=..., runtime=...)`
- [ ] Add `.github/workflows/test-runs-ingest.yaml` that fires on every
  CI completion
- [ ] Update `AGENTS.md` with the test-runs dashboard URL

## Stage 3 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-05-marimo-wasm-and-cigrunners-v1/specs/marimo/SKILL.md`
  (or whichever canonical spec this belongs to)
- [ ] Run `openspec validate 2026-08-05-marimo-wasm-and-cigrunners-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-05-marimo-wasm-and-cigrunners-v1 --yes`

## Stage 4 — Close the GitHub issues

- [ ] `gh issue close 34 --comment "Closes via 2026-08-05-marimo-wasm-and-cigrunners-v1"`
- [ ] `gh issue close 54 --comment "Closes via 2026-08-05-marimo-wasm-and-cigrunners-v1"`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol