# Tasks — 2026-08-22-dagster-biiep-ireland-lc-materialization-v1

## 1. Inventory

- [ ] 1.1 `curl http://localhost:3335/graphql -d '{"query":"{ assetsOrError { ... on AssetConnection { nodes { key { path } } } }"}'` to enumerate the 557 assets.
- [ ] 1.2 Find the Ireland-LC asset subset (the 62 lc5_* assets).
- [ ] 1.3 Find the canonical Dagster job that wraps the LC assets.

## 2. Materialize

- [ ] 2.1 Trigger the canonical LC job via `dagster job launch` (CLI).
- [ ] 2.2 Monitor the run via the Dagster UI at `http://localhost:3335/runs`.
- [ ] 2.3 Capture the run IDs + per-asset output rows.

## 3. Verify

- [ ] 3.1 For each layer (1–5), verify the assets produced the expected outputs:
  - Layer 1: 80 PDF records in the filesystem scanner output
  - Layer 2: 6 per-subject ingestion assets (chemistry, compsci, english, gaeilge, geography, mathematics) with the 80 rows total
  - Layer 3: 6 per-subject + per-stage extracted assets (syllabus, exam, marking, diagrams) with the BAML outputs
  - Layer 4: 6 per-subject cognified assets
  - Layer 5: 1 umbrella asset

- [ ] 3.2 Verify the BIEP Ireland LC pipeline end-to-end (the same 80 rows + sub-second extraction as the direct DLT run).

## 4. Document

- [ ] 4.1 Write `stedding/audit/2026-08-22-dagster-materialization.md` with the run IDs + output counts.
- [ ] 4.2 Update this openspec change with the actual asset counts after the materialization.

## 5. openspec

- [ ] 5.1 `openspec validate 2026-08-22-dagster-biiep-ireland-lc-materialization-v1 --strict`
- [ ] 5.2 `openspec archive 2026-08-22-dagster-biiep-ireland-lc-materialization-v1 --yes`

## 6. Commit + push

- [ ] 6.1 Stage any code fixes + the audit doc + the openspec archive.
- [ ] 6.2 `git push origin HEAD`
