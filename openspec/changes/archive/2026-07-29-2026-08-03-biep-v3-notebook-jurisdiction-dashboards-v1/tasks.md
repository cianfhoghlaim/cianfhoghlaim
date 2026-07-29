# 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Create the 5 missing jurisdiction dashboard notebooks

- [ ] Create `notebooks/19_ireland_pipeline_dashboard.py` — 544 Ireland
  cohorts + 4 sub-tabs (LC / JC / short / CBA)
- [ ] Create `notebooks/20_england_pipeline_dashboard.py` — 276 England
  cohorts (3 boards × 92 subjects matrix)
- [ ] Create `notebooks/21_sct_wls_ni_pipeline_dashboard.py` — 380
  SCT/WLS/NI cohorts split
- [ ] Create `notebooks/22_crown_dependencies_dashboard.py` — 360 Crown
  cohorts split Jersey / Guernsey / Isle of Man
- [ ] Create `notebooks/23_8_jurisdiction_overview.py` — all 1,560
  cohorts side-by-side

## Stage 2 — Rename sweep across 57 notebooks

- [ ] `find notebooks -name "*.py" ! -name "__init__.py" ! -path "*__pycache__*"
  -exec sed -i '' 's/oideachais\./cianfhoghlaim\./g' {} \;`

## Stage 3 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1/specs/oideachais-marimo-dashboards/spec.md`
  (or the renamed `cianfhoghlaim-marimo-dashboards` spec)
- [ ] Run `openspec validate 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-03-biep-v3-notebook-jurisdiction-dashboards-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol