# 2026-07-23-biep-v2-marimo-portal-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Changes 1 + 2 + 3 merged on `origin/main`
- [ ] Verify the lakehouse stack is running:
  `docker compose -f bonneagar/stacks/lakehouse/compose.yaml -f sidecar.yaml up -d`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Marimo notebooks

- [ ] Create `notebooks/04_biep_v2/__init__.py`
- [ ] Create `notebooks/04_biep_v2/00_biep_v2_overview.py`:
  - PEP 723 inline-dependency block (`marimo`, `ibis`, `pandas`, `altair`)
  - `## KCG patterns used` docstring referencing `ibis` + `marimo` skills
  - First data cell: `conn = ibis.duckdb.connect("md:oideachais")`
  - Second data cell: `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
  - Cross-jurisdiction filter UI (subject / level / language / year / awarding body)
  - 4 BIEP MotherDuck Dives embedded as iframes
- [ ] Create `notebooks/04_biep_v2/01_junior_cycle_explorer.py`:
  - 18 JC subjects × multi-select
  - Year 1 / Year 2 / Year 3 strand filter
  - Joins the JC LanceDB tables to the LC LC tables for Year 3 → Year 4 progression
- [ ] Create `notebooks/04_biep_v2/02_england_explorer.py`:
  - 3-tab view (AQA / OCR / Edexcel)
  - 9 subjects × multi-select
  - Joins the 3 board LanceDB tables
- [ ] Create `notebooks/04_biep_v2/03_ocr_ensemble_audit.py`:
  - For any BAML-extracted record, show the 8-panel audit trail
  - Source PDF page (rendered as `mo.image` from the S3 URL)
  - Docling DocTags XML (folded `mo.ui.code`)
  - Unstract JSON output (collapsible panel)
  - qwen3-vl-8b raw response (folded markdown)
  - gemma-4-26B-A4B raw response (folded markdown)
  - RAGAS `biiep_extraction_consensus` score bar chart
  - Final BAML Pydantic object (`mo.ui.table` JSON-schema-validated)
  - Langfuse trace link (deep-link)
- [ ] Run `mise run marimo:lint 04_biep_v2_*.py` — must pass

## Stage 2 — ibis-first contract audit

- [ ] Run `mise run ibis:first-contract 04_biep_v2/` — must pass
  (no raw `duckdb.connect()` in the 4 notebooks)
- [ ] Run `mise run ibis:lint 04_biep_v2/` — must pass

## Stage 3 — Hono API endpoints

- [ ] Create `web/hono-api/src/routes/biep-v2/__init__.ts`
- [ ] Create `web/hono-api/src/routes/biep-v2/lc.ts`:
  - `GET /api/v1/biep-v2/lc?subject=mathematics&level=hl&lang=en&page=1`
  - Returns paginated LC LanceDB rows (10 per page default)
- [ ] Create `web/hono-api/src/routes/biep-v2/jc.ts`
- [ ] Create `web/hono-api/src/routes/biep-v2/england.ts`
- [ ] Run `bun run hono:test` — all 3 endpoints return 200 OK with the expected JSON shape

## Stage 4 — TanStack Start public page

- [ ] Create `web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx`:
  - 4 marimo notebook iframes (marimo `embed` mode)
  - 4 BIEP MotherDuck Dive iframes
  - The Hono API endpoints for direct JSON fetching
  - Server-rendered with TanStack Start (RSC + edge runtime)
  - Follows the existing `cianfhoghlaim-web` shell + nav + theming
- [ ] Run `bun run tanstack-build` — must pass
- [ ] Run `bun run tanstack-test` — must pass

## Stage 5 — Spec delta commits + validation

- [ ] Run `openspec validate 2026-07-23-biep-v2-marimo-portal-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-23-biep-v2-marimo-portal-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-23-biep-v2-marimo-portal-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/research/biep_v2_portal_status.md` with the now-green status
- [ ] Verify the public page renders at `cianfhoghlaim.cianfhoghlaim.ie/biep-v2`
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol
