# Tasks: 2026-07-06-drift-cleanup-and-v4-alignment

## Phase 1 — Skill rewrites (~58 files)

### Sub-batch 1.1 — KCG core (most important)

- [ ] 1.1.1 Rewrite `.agents/skills/dlt/SKILL.md` — `sruth/oideachais/dlt_sources/` → `cianfhoghlaim/dlt/`; fix `oideachais.data_platform` references; add British-Isles Education DLT examples (NCCA + examinations.ie + gov.ie circulars); add canonical `mo.sql(engine=md:oideachais)` DuckDB + Ibis pattern
- [ ] 1.1.2 Rewrite `.agents/skills/cocoindex/SKILL.md` — `sruth/oideachais/cocoindex_flows/` → `cianfhoghlaim/cocoindex/` (~14 sites); fix `sruth/crypteolas/cocoindex_flows/` (L86); add v1-conformance R1-R4 explanation; add `lancedb.mount_table_target` canonical pattern
- [ ] 1.1.3 Rewrite `.agents/skills/baml/SKILL.md` — `sruth/oideachais/baml_src/` → `cianfhoghlaim/baml/`; add canonical LC extraction example (BAML function from `baml/education/lc_extraction/`)
- [ ] 1.1.4 Rewrite `.agents/skills/dagster/SKILL.md` — `oideachais.data_platform.dagster_defs.definitions` → `cianfhoghlaim.orchestration.definitions`; explain 5-layer architecture (1_ingestion / 2_materials / 3_model_lifecycle / 4_asset_generation / 5_agent_ops); add `@dlt_assets` wrapping example
- [ ] 1.1.5 Rewrite `.agents/skills/secrets-management/SKILL.md` — `infisical://dev-baile/sruth/oideachais/...` → `infisical://dev-baile/oideachais/...` (L33, L200); fix cross-refs to non-existent `stack-ops`, `monorepo` (point at `infrastructure-stacks` and `AGENTS.md`)
- [ ] 1.1.6 Rewrite `.agents/skills/change-detection/SKILL.md` — `sruth/oideachais/sources.yaml` → `cianfhoghlaim/dlt/sources.yaml`; fix sensor paths

### Sub-batch 1.2 — KCG specialised

- [ ] 1.2.1 Rewrite `.agents/skills/agent-fleet-orchestration/SKILL.md` — remove references to deleted `agents/tuatha/agents/adk/*.py` cluster (root_agent, celtic_tutor, mythology_narrator, quest_guide, research_assistant); reflect that the cluster is gone
- [ ] 1.2.2 Rewrite `.agents/skills/agent-memory-systems/SKILL.md` — fix `sruth/oideachais/memory/`, `sruth/meaisinfhoghlaim/agents/`, `sruth/oideachais/graph/`, `sruth/oideachais/cocoindex_flows/` paths → `cianfhoghlaim/<area>/`
- [ ] 1.2.3 Rewrite `.agents/skills/agent-observability/SKILL.md` — fix `sruth/oideachais/observability/`, `sruth/meaisinfhoghlaim/evaluation/` paths; fix broken refs to `pydantic-ai`, `stack-ops`, `monorepo`
- [ ] 1.2.4 Rewrite `.agents/skills/agentic-frontend-frameworks/SKILL.md` — `sruth/oideachais/web/`, `sruth/croilar/apps/`, `sruth/tuatha/ui/` → `cianfhoghlaim/web/apps/<name>/`

### Sub-batch 1.3 — KCG infra + specialists

- [ ] 1.3.1 Update `.agents/skills/garage/SKILL.md` — fix `bonneagar/stacks/` docstring refs (the stacks moved to `bonneagar/stacks/` after v4)
- [ ] 1.3.2 Update `.agents/skills/iceberg-lakekeeper/SKILL.md` — minor `bonneagar/` → `infrastructure/stacks/lakehouse/` refresh
- [ ] 1.3.3 Update `.agents/skills/apple-photos-ingestion/SKILL.md` — confirm current
- [ ] 1.3.4 Update `.agents/skills/komodo/SKILL.md` — add British-Isles context (where in the 94 stacks the LC pipelines run)
- [ ] 1.3.5 Update `.agents/skills/pangolin/SKILL.md` — add British-Isles context

### Sub-batch 1.4 — Canonical pattern injection

- [ ] 1.4.1 Update `.agents/skills/motherduck/SKILL.md` (router) — call out the 6 LC subjects + gov.ie circulars as a primary use case
- [ ] 1.4.2 Update `.agents/skills/duckdb/SKILL.md` — add `lance_scan()` pattern (LanceDB → DuckDB integration)
- [ ] 1.4.3 Update `.agents/skills/ducklake/SKILL.md` — add MotherDuck-DuckLake pattern for the LC lakehouse
- [ ] 1.4.4 Update `.agents/skills/ibis/SKILL.md` — add canonical `ibis.duckdb.connect("md:oideachais")` pattern
- [ ] 1.4.5 Update `.agents/skills/lancedb/SKILL.md` — add `lancedb.mount_table_target` + DuckDB integration
- [ ] 1.4.6 Update `.agents/skills/marimo/SKILL.md` — add the canonical `mo.sql(engine=md:oideachais)` pattern with PEP 723 + `mo.ui.table` + `mo.vstack` examples for LC analytics

### Sub-batch 1.5 — Deprecation banners

- [ ] 1.5.1 Add deprecation banner to `.agents/skills/dlthub/SKILL.md` — point at canonical `dlt/` skill
- [ ] 1.5.2 Add deprecation banner to `.agents/skills/dlthub-router/SKILL.md` — point at canonical `dlt/` skill
- [ ] 1.5.3 Add deprecation banner to `.agents/skills/setup-secrets/SKILL.md` — point at canonical `secrets-management`
- [ ] 1.5.4 Update `.agents/skills/ccc/SKILL.md` — refresh deprecation banner (user retained despite "retires 2026-07-15")
- [ ] 1.5.5 Update `.agents/skills/graphiti-core/SKILL.md` — add banner pointing at `graphiti/`

### Sub-batch 1.6 — Vendor skill families (light update for British-Isles context)

- [ ] 1.6.1 Update `.agents/skills/cloudflare/SKILL.md` + canonical 5 subskills — add British-Isles context (R2 bucket for the LC PDFs)
- [ ] 1.6.2 Update `.agents/skills/copilotkit/SKILL.md` + canonical 5 subskills — add British-Isles context
- [ ] 1.6.3 Update `.agents/skills/huggingface/SKILL.md` + canonical 5 subskills — call out BGE-M3 (the LC embedder) + Unsloth
- [ ] 1.6.4 Update `.agents/skills/marimo/SKILL.md` (root + 4 subskills) — British-Isles context

## Phase 2 — Notebook rewrites (~91 files)

### Sub-batch 2.1 — Hardcoded secret removal (security critical)

- [ ] 2.1.1 `cianfhoghlaim/notebooks/dashboards/duckdb/lakehouse_inspector.py` — remove 4 hardcoded Garage key + PG password defaults
- [ ] 2.1.2 `cianfhoghlaim/notebooks/dashboards/mission_control.py` — remove 6 hardcoded AWS keys + PG password defaults; fix legacy `oideachais/` import paths
- [ ] 2.1.3 `cianfhoghlaim/notebooks/dashboards/observability/pipeline_e2e_test.py` — remove 2 hardcoded AWS keys
- [ ] 2.1.4 `cianfhoghlaim/notebooks/dashboards/education/exam_papers_explorer.py` — remove 2 hardcoded secrets
- [ ] 2.1.5 `cianfhoghlaim/notebooks/dashboards/leabharlann/pdf_download_dashboard.py` — remove 2 hardcoded secrets
- [ ] 2.1.6 `cianfhoghlaim/notebooks/dashboards/pdf_processing/pdf_ocr_model_comparison.py` — remove 1 hardcoded secret

### Sub-batch 2.2 — Per-subject LC notebooks (16 files)

For each `cianfhoghlaim/notebooks/dashboards/leaving_cert/0X_*.py`:

- [ ] 2.2.1 Add PEP 723 inline deps
- [ ] 2.2.2 Replace hardcoded `/Users/cianmacandeisigh/dev/kings_college_galway/...` paths with `os.environ["CIANFHOGHLAIM_LEAVING_CERT_ROOT"]`
- [ ] 2.2.3 Replace pandas-only analytics with DuckDB + Ibis (`mo.sql(engine=md:oideachais)`)
- [ ] 2.2.4 Wire to live lakehouse tables (`md:oideachais.lc.<subject>.<level>_<lang>`, `md:oideachais.leaving_cert.<subject>.*`)
- [ ] 2.2.5 Remove `(Stub: ...)` and `TODO/FIXME` markers (or replace with real queries)
- [ ] 2.2.6 Update docstrings to reflect British-Isles Education pipeline goals

Specifically:
- `01_chemistry_analysis.py` (203 LOC, richest — 11 cells, 5 BAML calls)
- `02_computer_science_analysis.py` (101 LOC)
- `03_gaeilge_analysis.py` (114 LOC, handles no-`en/`-subdir quirk)
- `04_geography_analysis.py` (106 LOC)
- `05_mathematics_analysis.py` (117 LOC)
- `06_en_vs_ga_comparison.py` (90 LOC, EN+GA side-by-side)
- `07_syllabus_topic_overlap.py` (80 LOC)
- `08_exam_paper_difficulty.py` (78 LOC)
- `09_marking_scheme_complexity.py` (74 LOC)
- `10_curriculum_evolution.py` (78 LOC)
- `11_ocr_model_comparison.py` (107 LOC)
- `12_layout_extraction.py` (74 LOC)
- `13_dense_ocr_benchmark.py` (75 LOC)
- `14_table_extraction.py` (72 LOC)
- `15_diagram_detection.py` (76 LOC)
- `16_runtime_comparison_llama_swap_vs_cpp.py` (127 LOC)

### Sub-batch 2.3 — Root leaving_cert/ stubs (9 files — user kept, must update)

For each `cianfhoghlaim/notebooks/leaving_cert/<subject>.py`:

- [ ] 2.3.1 Add PEP 723 inline deps
- [ ] 2.3.2 Wire to live `md:oideachais.lc.<subject>.*` lakehouse tables
- [ ] 2.3.3 Use DuckDB + Ibis instead of hardcoded `matplotlib.pyplot` topic lists
- [ ] 2.3.4 Replace in-memory analytics with `mo.sql(engine=md:oideachais)`
- [ ] 2.3.5 Update for British-Isles Education pipeline goals

Files: `chemistry.py`, `mathematics.py`, `gaeilge.py`, `english.py`,
`computer_science.py`, `applied_mathematics.py`, `geography.py`,
`history.py`, `diagram_library.py`.

### Sub-batch 2.4 — Education dashboards (7 files)

For each in `cianfhoghlaim/notebooks/dashboards/education/`:

- [ ] 2.4.1 `curriculum_educator.py` (431 LOC) — switch from in-memory data to `mo.sql(engine=md:oideachais)`
- [ ] 2.4.2 `exam_papers_explorer.py` (430 LOC) — strip 2 hardcoded secrets, switch to lakehouse
- [ ] 2.4.3 `marking_scheme_analyzer.py` (286 LOC) — DuckDB ✓ already; add PEP 723
- [ ] 2.4.4 `syllabus_visualizer.py` (283 LOC) — DuckDB ✓ already; add PEP 723
- [ ] 2.4.5 `university_courses.py` (346 LOC) — switch primary path to `mo.sql(engine=md:oideachais)`, drop stubs
- [ ] 2.4.6 `all_nations.py` (85 LOC) — small fix
- [ ] 2.4.7 Merge 6× `*_full_pipeline.py` (chemistry, biology, business, applied_mathematics, computer_science, french) into 1 parametrised `subject_full_pipeline_runner.py`

### Sub-batch 2.5 — leabharlann / observability (6 files)

- [ ] 2.5.1 `dashboards/leabharlann_full_stack_demo.py` (191 LOC) — add PEP 723, switch to `mo.sql(engine=)`
- [ ] 2.5.2 `dashboards/leabharlann/pdf_download_dashboard.py` (307 LOC) — strip 2 hardcoded secrets, add PEP 723
- [ ] 2.5.3 `dashboards/email_inbox_triage.py` (360 LOC) — drop 2 stubs, add PEP 723
- [ ] 2.5.4 `dashboards/observability/baml_drift_audit.py` (27 LOC) — REWRITE from scratch
- [ ] 2.5.5 `dashboards/observability/irish_extraction_quality.py` (26 LOC) — REWRITE (real RAGAS check on gaeilge extraction)
- [ ] 2.5.6 `dashboards/observability/pipeline_e2e_test.py` (318 LOC) — strip secrets, fix `oideachais/` paths

### Sub-batch 2.6 — DuckDB / lakehouse dashboards (4 files)

- [ ] 2.6.1 `dashboards/duckdb/lakehouse_inspector.py` (341 LOC) — strip secrets, add PEP 723
- [ ] 2.6.2 `dashboards/duckdb/ducklake_explorer.py` (309 LOC) — refresh docstrings
- [ ] 2.6.3 `dashboards/duckdb/dlt_pipeline_overview.py` (26 LOC) — REWRITE
- [ ] 2.6.4 `dashboards/duckdb/cocoindex_embedding_coverage.py` (26 LOC) — REWRITE

### Sub-batch 2.7 — Stage / corpus overviews (10 files)

For each:
- [ ] 2.7.1 `dashboards/{primary, junior_cycle, senior_cycle, tertiary, aistear}.py` — wire to live lakehouse tables
- [ ] 2.7.2 `dashboards/{culture, medical, medicine, other, politics, technology}/01_*_corpus_overview.py` — strip hardcoded `/Users/...` paths, use env vars
- [ ] 2.7.3 `dashboards/site_analysis/dashboard.py` (58 LOC) — small DuckDB fix
- [ ] 2.7.4 `dashboards/cross_domain.py` (103 LOC) — DuckDB ✓ already; add PEP 723
- [ ] 2.7.5 `dashboards/official_media/official_media.py` (263 LOC) — add PEP 723

### Sub-batch 2.8 — Law dashboards (6 files)

- [ ] 2.8.1 `dashboards/law/{01_law_corpus_overview,02_cross_corpus_timeline,03_jurisdictional_map,04_pattern_detection}.py` — strip hardcoded paths, fix `app._unparsable_cell` blocks
- [ ] 2.8.2 `dashboards/law/all_nations.py` (112 LOC) — DuckDB ✓
- [ ] 2.8.3 `dashboards/law/statute_book.py` (59 LOC) — switch to live `oideachais.law.{nation}.acts` table

### Sub-batch 2.9 — speedrun/ (9 files, ~9,343 LOC — user kept, must update)

For each `cianfhoghlaim/notebooks/speedrun/notebooks/speedrun/{00..08}_*.py`:

- [ ] 2.9.1 Add PEP 723 inline deps
- [ ] 2.9.2 Replace `import pandas as pd` with DuckDB + Ibis where applicable
- [ ] 2.9.3 Update references from `sruth/<quadrant>/...` to `cianfhoghlaim/<area>/...`
- [ ] 2.9.4 Update content to reflect current project goals (these were crypto MMO planning; user kept them, so we keep the content but make it conform to current stack)

### Sub-batch 2.10 — Other

- [ ] 2.10.1 `notebooks/root_pdfs_explorer.py` (125 LOC) — REPLACE placeholder matplotlib with real `lance_scan('s3://...')` query
- [ ] 2.10.2 `notebooks/cli.py` (65 LOC) — fix 9 hardcoded fictional notebook names; make it actually `subprocess.run(["marimo", "edit", notebook])`
- [ ] 2.10.3 `notebooks/sources_load.py` (413 LOC) — already healthy; minor scan-path refresh
- [ ] 2.10.4 `notebooks/meaisinfhoghlaim/{01_leabharlann_descriptive,02_dpre_lag_analysis}.py` — already healthy; minor `to_pandas()` removal
- [ ] 2.10.5 `notebooks/meaisinfhoghlaim/03_pdf_processing.py` (202 LOC) — wire to live `leabharlann_pdf_processing` DuckLake table
- [ ] 2.10.6 `notebooks/dashboards/author_archive/unified_dashboard.py` (125 LOC) — refresh to current structure

## Phase 3 — OpenSpec cleanup

### Sub-batch 3.1 — Archive fully-done changes (8)

- [ ] 3.1.1 `openspec archive 2026-06-29-bonneagar-v4-canonical-and-stack-migration --yes`
- [ ] 3.1.2 `openspec archive modern-meaisin-cliste --yes`
- [ ] 3.1.3 `openspec archive skills-metadata-cleanup --yes`
- [ ] 3.1.4 `openspec archive 2026-07-03-specs-and-session-9-health-report --yes`
- [ ] 3.1.5 `openspec archive 2026-06-29-restore-heritage-corpus-and-expand-readme --yes`
- [ ] 3.1.6 `openspec archive extend-culture-heritage-to-8-articles --yes`
- [ ] 3.1.7 `openspec archive ingest-culture-heritage --yes`
- [ ] 3.1.8 `openspec archive 2026-06-28-browserbase-phase-{1a,1b,2,3}-decisions --yes` (×4)

### Sub-batch 3.2 — Archive superseded-by-v4 changes (~22)

- [ ] 3.2.1 `openspec archive refactor-quadrants-to-sruth --yes`
- [ ] 3.2.2 `openspec archive refactor-dlt-dagster-2026-stack-align --yes`
- [ ] 3.2.3 `openspec archive consolidate-external-libs-into-tuatha --yes`
- [ ] 3.2.4 `openspec archive croilar-personas-to-streams --yes`
- [ ] 3.2.5 `openspec archive lateralise-dlt-sources-to-domains --yes`
- [ ] 3.2.6 `openspec archive ireland-primary-jc-dlt-baml-and-full-stack-demo --yes`
- [ ] 3.2.7 `openspec archive consolidate-embedding-batcher --yes`
- [ ] 3.2.8 `openspec archive fix-broken-imports-and-baml --yes`
- [ ] 3.2.9 `openspec archive stale-pipelines-cleanup --yes`
- [ ] 3.2.10 `openspec archive datasets-cleanup --yes`
- [ ] 3.2.11 `openspec archive archive-celtic-baml-orphans --yes`
- [ ] 3.2.12 `openspec archive oideachais-stack-polish --yes`
- [ ] 3.2.13 `openspec archive oideachais-agent-services --yes`
- [ ] 3.2.14 `openspec archive complete-cognee-knowledge-graph --yes`
- [ ] 3.2.15 `openspec archive four-directory-indexing-and-standards --yes`
- [ ] 3.2.16 `openspec archive docs-skills-consolidation-pipeline --yes`
- [ ] 3.2.17 `openspec archive celtic-data-engineering-patterns --yes`
- [ ] 3.2.18 `openspec archive refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline --yes`
- [ ] 3.2.19 `openspec archive croilar-revitalisation --yes`
- [ ] 3.2.20 `openspec archive baml-reorganize-by-cluster --yes`
- [ ] 3.2.21 `openspec archive dagger-monorepo-integration --yes`
- [ ] 3.2.22 `openspec archive leaving-cert-2026 --yes`

### Sub-batch 3.3 — Spec housekeeping

- [ ] 3.3.1 Write `Purpose:` paragraphs for 12 `TBD` specs (`celtic-asset-generation`, `official-media-{pipeline,marimo,fediverse}`, `author-archive-{credit-budget,cross-corpus-kg,multi-target,pipeline,ui-grounding,uog-coursework,web-scraping}`)
- [ ] 3.3.2 Remove phantom-spec rows from `openspec/AGENTS.md` L143-144 + `openspec/project.md` §117-118 (`celtic-data-engineering-pipeline`, `gradio-ensemble-pattern`)
- [ ] 3.3.3 Path-only rewrite of `openspec/specs/infrastructure-stacks/spec.md` — `infrastructure/stacks/<x>` → `bonneagar/stacks/<x>` (~31 hits)
- [ ] 3.3.4 Path-only rewrite of `openspec/specs/oideachais-baml-schemas/spec.md` — remove 2 `sruth/*` refs
- [ ] 3.3.5 Path-only rewrite of `openspec/AGENTS.md` — `infrastructure/stacks/` → `bonneagar/stacks/` (180 + 12 hits); `../sruth/.../AGENTS.md` references → real quadrant AGENTS.md paths

## Phase 4 — Validate

- [ ] 4.1 `openspec validate 2026-07-06-drift-cleanup-and-v4-alignment --strict`
- [ ] 4.2 `mise run lint:skills` (validates all 58 skill metadata)
- [ ] 4.3 `python -m py_compile <each notebook>` for all 91 notebook files
- [ ] 4.4 `marimo parse <each notebook>` for all marimo notebooks
- [ ] 4.5 `git grep 'sruth/' cianfhoghlaim/notebooks/ openspec/specs/` returns 0 hits
- [ ] 4.6 `git grep 'sruth/' .agents/skills/` returns 0 hits in the rewritten files (only `.agents/skills_backup/` may contain it)
- [ ] 4.7 `git grep 'infisical://dev-baile/sruth/'` returns 0 hits
- [ ] 4.8 `git grep -E 'os\.getenv\(.*"GK[A-Z0-9]{20,}"|"devpassword"' cianfhoghlaim/notebooks/` returns 0 hits
- [ ] 4.9 `openspec list --specs | wc -l` should drop from 56 to ~54 (after removing 2 phantom specs from AGENTS.md + project.md)

## Phase 5 — Commit + archive

- [ ] 5.1 `git add .agents/skills/ cianfhoghlaim/notebooks/ openspec/`
- [ ] 5.2 `git commit -m "drift-cleanup: rewrite 58 skills + 91 notebooks + archive 30 stale changes (2026-07-06)"`
- [ ] 5.3 `openspec archive 2026-07-06-drift-cleanup-and-v4-alignment --yes`
- [ ] 5.4 `git push`