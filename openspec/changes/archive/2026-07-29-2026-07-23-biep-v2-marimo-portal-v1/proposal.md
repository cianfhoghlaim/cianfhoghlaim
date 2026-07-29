## Superseded by

This BIEP v2 change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all v2 work as part of milestones M0-M4.

## Superseded by

This BIEP v2 change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all v2 work as part of milestones M0-M4.

# 2026-07-23-biep-v2-marimo-portal-v1

## Why

The user explicitly said **"view the processed BAML output"**. After Changes 1
+ 2 + 3 ship the full BIEP v2 pipeline (Junior Cycle + England AQA/OCR/Edexcel +
the 4-path OCR/VLM ensemble), the only way to **inspect any extracted record's
provenance** is via raw DuckLake SQL, Langfuse traces, or RAGAS scoring
dashboards. That's a tool for engineers, not for the curriculum researchers
and teachers who are the actual end users.

This change ships the **BIEP v2 portal** — 4 new marimo notebooks + 3 Hono
API endpoints + 1 TanStack Start public page — that gives a non-engineer
the ability to:

- Browse the full BIEP v2 corpus across LC + JC + A-Level + GCSE in one view
- Drill into JC learning outcomes by strand (Year 1/2/3) + the 36 CBAs
- Compare AQA / OCR / Edexcel specifications for the same subject side by side
- **Open the full audit trail for any BAML-extracted record**: source PDF
  page + Docling DocTags + Unstract JSON + qwen3-vl-8b response +
  gemma-4-26B-A4B response + RAGAS consensus score + the final BAML Pydantic
  object + the Langfuse trace link

The 4 notebooks use the **ibis-first contract** from
`british-isles-education-pipeline/spec.md` Requirement 5 (no raw
`duckdb.connect()`), and read from the canonical Lakehouse via
`ibis.duckdb.connect("md:oideachais")` + `ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`.

## What changes

### 1. Four new marimo notebooks

`notebooks/04_biep_v2/`:

- **`00_biep_v2_overview.py`** — single-pane view across LC + JC + A-Level + GCSE.
  Cross-jurisdiction filter UI: subject / level / language / year / awarding body
  / curriculum region. Reads from
  `cianfhoghlaim.<domain>.british_isles.<jurisdiction>.<scope>.*` Lance tables.
  Renders: subject count, topic coverage histogram, last-sync timestamp, the
  4 BIEP MotherDuck Dives embedded as iframes.
- **`01_junior_cycle_explorer.py`** — drill into JC learning outcomes by strand
  (Year 1/2/3) + the 36 CBAs. Multi-select for the 18 JC subjects. Joins the
  JC LanceDB tables to the LC LC tables for the Year 3 → Year 4 (JC → LC)
  topic progression.
- **`02_england_explorer.py`** — side-by-side AQA / OCR / Edexcel for the
  same subject. 3-tab view (one tab per board). Joins the 3 board LanceDB
  tables and surfaces spec differences since the last sync (the Change 5 sensor's
  outputs).
- **`03_ocr_ensemble_audit.py`** — **the "view the processed BAML output"
  notebook** — for any BAML-extracted record, show side-by-side:
  1. Source PDF page (rendered as a `mo.image` from the S3 URL)
  2. Docling DocTags XML (folded syntax-highlighted `mo.ui.code`)
  3. Unstract JSON output (raw JSON in a collapsible panel)
  4. qwen3-vl-8b raw response (folded markdown)
  5. gemma-4-26B-A4B raw response (folded markdown)
  6. RAGAS `biiep_extraction_consensus` score bar chart
  7. Final BAML Pydantic object (JSON-schema-validated `mo.ui.table`)
  8. Langfuse trace link (deep-link to the trace page)

All 4 notebooks:

- Use `ibis.duckdb.connect("md:oideachais")` + `ibis.lancedb.connect(...)`
  (per the ibis-first contract)
- Have a `## KCG patterns used` docstring referencing the `ibis` skill
  + the `marimo` skill
- Are PEP 723 inline-dependency marimo notebooks
- Run on `marimo edit <path>` (dev) + `marimo run <path> --headless`
  (production, behind the Hono API proxy)

### 2. Three Hono API endpoints

`web/hono-api/src/routes/biep-v2/` — 3 JSON endpoints that back the marimo
notebooks with paginated data:

- `lc.ts` — paginated LC LanceDB queries
  (`GET /api/v1/biep-v2/lc?subject=mathematics&level=hl&lang=en&page=1`)
- `jc.ts` — paginated JC LanceDB queries
- `england.ts` — paginated England LanceDB queries

Each endpoint uses the canonical Hono + oRPC stack pattern from the existing
`web/hono-api/`.

### 3. One TanStack Start public page

`web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx` — a public TanStack
Start page at `/biep-v2` that embeds:

- The 4 marimo notebooks as iframes (the marimo `embed` mode)
- The 4 BIEP MotherDuck Dives as iframes
- The 3 Hono API endpoints (for direct JSON fetching)

The route is server-rendered with TanStack Start (RSC + edge runtime),
follows the existing `cianfhoghlaim-web` shell + nav + theming.

### 4. Spec deltas

2 spec deltas:

- `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` — add 1 new requirement:
  "Requirement: BIEP v2 cross-jurisdiction notebooks" for the 4 new notebooks
- `openspec/specs/british-isles-education-pipeline/spec.md` Requirement 5
  (ibis-first contract) — extend the scope from "6 BIEP subject notebooks"
  to "all 4 BIEP v2 notebooks"

## Dependencies

```yaml
Blocked by: 2026-07-20-biep-v2-junior-cycle-extraction-v1
            (needs the JC LanceDB tables)
            2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1
            (needs the England LanceDB tables)
Blocked by (soft): 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1
                   (the audit notebook reads the 4-path per-path DuckLake
                    tables from the ensemble pipeline)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-23-biep-v2-marimo-portal-v1 --strict` passes
- `mise run marimo:lint 04_biep_v2_*.py` (the marimo lint task) passes
- `mise run ibis:first-contract 04_biep_v2/` (the ibis-first-contract
  audit) passes — no raw `duckdb.connect()` in the 4 notebooks
- The 4 marimo notebooks run end-to-end against the dev lakehouse:
  `marimo run notebooks/04_biep_v2/00_biep_v2_overview.py --headless`
- The 3 Hono API endpoints return 200 OK with the expected JSON shape
- The TanStack Start public page renders at `cianfhoghlaim.cianfhoghlaim.ie/biep-v2`
- All 4 notebooks work with the Change 3 ensemble audit trail (the
  `biiep_ocr_ensemble` DAG asset is the data source for `03_ocr_ensemble_audit.py`)
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that this change extends with the v2 portal surface
- [`ireland-primary-jc-dlt-baml`](../../specs/ireland-primary-jc-dlt-baml/spec.md) —
  the JC capability whose LanceDB tables this change queries
- [`british-isles-education-pipeline` Change 2](../2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1/) —
  the England pipeline whose LanceDB tables this change queries
- [`british-isles-education-pipeline` Change 3](../2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1/) —
  the OCR ensemble whose 4-path per-path DuckLake tables the audit notebook reads
- [`cianfhoghlaim-marimo-dashboards`](../../specs/cianfhoghlaim-marimo-dashboards/spec.md) —
  the marimo dashboard capability that this change extends
- [`agentic-frontend-frameworks`](../../specs/agentic-frontend-frameworks/spec.md) —
  the umbrella spec for TanStack Start + CopilotKit + Hono + oRPC
- `.agents/skills/marimo/SKILL.md` — marimo notebook patterns
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract
- `.agents/skills/tanstack-start/SKILL.md` — TanStack Start patterns
- `.agents/skills/hono/SKILL.md` — Hono API patterns
