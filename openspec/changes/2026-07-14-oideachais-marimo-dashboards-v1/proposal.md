# Oideachais Marimo Dashboards v1

## Why

The `oideachais-marimo-dashboards` capability spec defines the
marimo notebook surface for the BIEP v1 + Cognee + cross-archive
+ Gaeilge + Dagster lineage dashboards. The spec carries **10
requirements** (R1–R10) covering:

- **R1** — 5-stage education dashboards
- **R2** — Leabharlann full-stack demo (BIEP BAML + Cognee cognify)
- **R3** — Cross-domain + lakehouse + ducklake dashboards
- **R4** — Marimo on Cloudflare Workers + Container (deployment
  concern, not operator surface; lives outside the notebook dir)
- **R5** — PEP 723 inline dependency blocks
- **R6** — Multi-column layout via `@app.cell(column=N)`
- **R7** — DLT + LanceDB pipeline pattern in notebooks
- **R8** — University courses dashboard (covered by
  `notebooks/04_biep_motherduck/04_university_courses.py`)
- **R9** — BIEP Notebooks Wire to Local Lakehouse (ibis-first)
- **R10** — BIEP Notebooks ibis-first refactor of all 11 files
  (covered by the 11 BIEP notebooks already shipped at
  `notebooks/04_biep_motherduck/01..11_*.py`)

The 3 orchestrating BIEP subject notebooks (chemistry, mathematics,
gaeilge, etc.) shipped via commit `c12f4f4cb` cover R9 + R10 for
the BIEP half. The marimo spec's *follow-up dashboard layer* —
the cross-subject + cross-archive + cross-backend operator surface
that ties them all together — is **not** covered:

- **R1 / R9 corpus overview** — no per-corpus matrix dashboard
- **R2 cognify cohort view** — only a per-subject cognify dashboard at
  `06_observability/03_cognee_knowledge_graph.py`; no cohort roll-up
- **R3 cross-archive** — no `leabharlann_join_to_lc` operator view
- **R3 lakehouse table browser** — only
  `05_lakehouse_inspect/01_ducklake_explorer.py`; no MotherDuck
  schema-aware browser
- **R7 BAML extraction log** — no per-function call-count / latency
  / success-rate view
- **R6 + R9 per-subject analytics roll-up** — the 6 per-subject
  notebooks exist at `leaving_cert/*.py` but there is no
  *composite* multi-column roll-up
- **R2 + R7 Gaeilge language coverage** — only the per-quality
  audit at `06_observability/02_irish_extraction_quality.py`; no
  per-corpus fada-preservation / síneadh-fada / punctum-delens
  coverage dashboard
- **R10 CocoIndex v1 conformance** — the audit at
  `openspec/changes/2026-07-13-cocoindex-v1-non-priority-flows-v1/`
  is a one-off CLI script; no live marimo dashboard
- **R7 agent memory** — no live Cognee + Graphiti + LanceDB +
  Letta backend-counts dashboard
- **R7 + R9 Dagster asset lineage** — the BIC dashboard at
  `04_biep_motherduck/07_subject_full_pipeline.py` only shows the
  per-subject 6-step pipeline; no asset-graph roll-up

This change ships **10 follow-up marimo dashboards** at
`ciolanza/notebooks/10_marimo_dashboards/{01..10}_*.py`, plus the
openspec change artifacts (proposal + tasks + 1 MODIFIED spec
delta).

## What ships

10 dashboards, each ~300–400 LOC, each matching the
`oideachais-marimo-dashboards` spec:

| # | Notebook | Coverage | Spec reqs |
|---|---------|----------|-----------|
| 01 | `01_biep_corpus_overview.py` | per-subject × level × language × year matrix (5 charts) | R1, R9 |
| 02 | `02_cognee_knowledge_graph.py` | cohort-rolled-up KG view + `cognee.search()` box (5 charts) | R2, R7 |
| 03 | `03_cross_archive_navigation.py` | `leabharlann_join_to_lc` operator view (5 charts) | R3 |
| 04 | `04_lakehouse_table_browser.py` | MotherDuck `SHOW TABLES` browser + SQL console (5 charts) | R3 |
| 05 | `05_baml_extraction_log_viewer.py` | per-function call-count / latency / success / retry view + live `b.ExtractCurriculumSyllabus` (5 charts) | R7 |
| 06 | `06_per_subject_analytics.py` | per-subject composite roll-up via `ibis.duckdb.connect()` (5 charts) | R6, R9 |
| 07 | `07_gaeilge_language_coverage.py` | EN vs GA + fada-preservation + síneadh-fada + punctum-delens (5 charts) | R2 |
| 08 | `08_cocoindex_v1_conformance_dashboard.py` | 7-App v1 conformance audit (5 charts) | R10 |
| 09 | `09_agent_memory_dashboard.py` | Cognee + Graphiti + LanceDB + Letta cohort view (5 charts) | R2, R7 |
| 10 | `10_dagster_asset_lineage.py` | Dagster asset success / duration / pending-reattempt view + sensor health (5 charts) | R7, R9 |

Each dashboard follows the canonical KCG pattern:

- PEP 723 inline dependency block
- `connect_biep_lakehouse()` (or raw `duckdb.connect("md:oideachais")`
  in the synthetic fallback) with graceful local-DuckDB fallback
- 3–5 altair charts per notebook
- Live BAML extractor invocation when `litellm.cianfhoghlaim.ie` is
  reachable (try/except-wrapped for offline rendering)
- Uses the canonical `cognee.search(query, top_k)` helper when
  the cognify integration is wired

## What changes

| File | Action | LOC delta |
|:--|:--|--:|
| `ciolanza/notebooks/cli.py` | MODIFIED (`GROUPS` tuple gains `"10_marimo_dashboards"`) | +~10 |
| `ciolanza/notebooks/10_marimo_dashboards/01_biep_corpus_overview.py` | NEW (R1+R9 corpus matrix — 5 panels) | +~343 |
| `ciolanza/notebooks/10_marimo_dashboards/02_cognee_knowledge_graph.py` | NEW (R2 cognify cohort — 5 panels + `cognee.search()`) | +~376 |
| `ciolanza/notebooks/10_marimo_dashboards/03_cross_archive_navigation.py` | NEW (R3 BIEP ↔ leabharlann cross-archive — 5 panels) | +~346 |
| `ciolanza/notebooks/10_marimo_dashboards/04_lakehouse_table_browser.py` | NEW (R3 lakehouse browser + `mo.sql` console — 5 panels) | +~339 |
| `ciolanza/notebooks/10_marimo_dashboards/05_baml_extraction_log_viewer.py` | NEW (R7 BAML call-count / latency / success — 5 panels) | +~349 |
| `ciolanza/notebooks/10_marimo_dashboards/06_per_subject_analytics.py` | NEW (R6+R9 per-subject composite — 5 panels, ibis-first) | +~311 |
| `ciolanza/notebooks/10_marimo_dashboards/07_gaeilge_language_coverage.py` | NEW (R2 GA coverage + fada + síneadh-fada + punctum-delens — 5 panels) | +~346 |
| `ciolanza/notebooks/10_marimo_dashboards/08_cocoindex_v1_conformance_dashboard.py` | NEW (R10 7-App v1 conformance — 5 panels) | +~329 |
| `ciolanza/notebooks/10_marimo_dashboards/09_agent_memory_dashboard.py` | NEW (R2+R7 Cognee + Graphiti + LanceDB + Letta cohort — 5 panels) | +~389 |
| `ciolanza/notebooks/10_marimo_dashboards/10_dagster_asset_lineage.py` | NEW (R7+R9 Dagster asset success / duration / sensor health — 5 panels) | +~374 |
| `openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/proposal.md` | NEW (this file) | +~120 |
| `openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/tasks.md` | NEW (7 task groups) | +~120 |
| `openspec/changes/2026-07-14-oideachais-marimo-dashboards-v1/specs/oideachais-marimo-dashboards/spec.md` | NEW (1 MODIFIED requirement) | +~80 |

Total: 10 dashboards (~3,500 LOC) + 3 change artifacts (~320 LOC).

## Out of scope

- The 6 per-subject notebooks at `ciolanza/notebooks/leaving_cert/*.py`
  (chemistry, mathematics, etc.) are NOT touched — they remain the
  per-subject marimo surface; the new dashboards are the *composite*
  roll-up surface.
- The 11 BIEP subject + leabharlann notebooks at
  `ciolanza/notebooks/04_biep_motherduck/*.py` are NOT touched.
- The 5 BAML+CocoIndex tutorials at
  `ciolanza/notebooks/13_baml_cocoindex_tutorial/*.py` are NOT touched.
- The 9 marimo notebooks at `09_official_media/`, `06_observability/`,
  `05_lakehouse_inspect/`, `07_educational_stages/` are NOT touched.

## Dependencies

Blocked by:

- **None** — this change stands on the existing BIEP v1 + leabharlann
  + cognify + CocoIndex v1 + Dagster wiring that already shipped
  via:
  - `2026-07-06-british-isles-education-pipeline-v1` (the BIEP lakehouse)
  - `2026-07-13-biep-v1-phases-6-7-unblock-v1` (the lc5/lc6 chain)
  - `2026-07-13-cocoindex-v1-non-priority-flows-v1` (the CocoIndex v1
    audit criteria this dashboard surfaces)
  - `2026-07-10-wire-8-subject-agents-cognify-langfuse-v1` (the agent
    fleet backends this dashboard renders)
  - `2026-07-13-official-media-marimo-v1` (the canonical follow-up
    marimo-dashboards precedent — same blueprint template)

This change can be archived immediately after `bun run
spec:validate` passes + the 10 dashboards AST-parse + the CLI
discovers them. There is no cross-repo sync required.

## Cross-repo sync

None. The IaC repo (`bonneagar/`) does not own any of these
notebook files; the comneamh (`leabharlann/`) corpus stays
untouched. The change is fully in-repo (the `ciolanza/notebooks/`
+ `openspec/specs/` + `openspec/changes/` trees all live in
this worktree).
