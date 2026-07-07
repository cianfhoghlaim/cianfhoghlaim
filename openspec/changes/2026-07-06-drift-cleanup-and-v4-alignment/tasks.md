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

## Phase 6 — Spec retire (12 deletes, inline migration notes)

For each: rm -rf the dir, then add a `## Migrated from: <X>` section to the surviving canonical.

- [ ] 6.1 `openspec/specs/author-archive-credit-budget/` → rm -rf; add migration note to `official-media-pipeline/spec.md`
- [ ] 6.2 `openspec/specs/author-archive-cross-corpus-kg/` → rm -rf; add migration note to `oideachais-cognify-knowledge-graph/spec.md`
- [ ] 6.3 `openspec/specs/author-archive-multi-target/` → rm -rf; add migration note to `oideachais-pipeline/spec.md`
- [ ] 6.4 `openspec/specs/author-archive-pipeline/` → rm -rf; add migration note to `official-media-pipeline/spec.md`
- [ ] 6.5 `openspec/specs/author-archive-ui-grounding/` → rm -rf; add migration note to `agent-fleet-orchestration` skill (no spec equivalent)
- [ ] 6.6 `openspec/specs/author-archive-uog-coursework/` → rm -rf; add migration note to `oideachais-university-deep-extraction/spec.md`
- [ ] 6.7 `openspec/specs/author-archive-web-scraping/` → rm -rf; add migration note to `official-media-pipeline/spec.md`
- [ ] 6.8 `openspec/specs/chunkhound-code-search/` → rm -rf; add migration note to `indexing-and-cognition/spec.md`
- [ ] 6.9 `openspec/specs/cocoindex-v1-migration/` → rm -rf; absorb body into `oideachais-cocoindex-v1-migration/spec.md`
- [ ] 6.10 `openspec/specs/cross-domain-registry/` → rm -rf; add migration note to `agent-memory-systems/spec.md`
- [ ] 6.11 `openspec/specs/stack-audit/` → rm -rf; add migration note to `infrastructure-stacks/spec.md`
- [ ] 6.12 `openspec/specs/tuatha-platform/` → rm -rf; add migration note to `cianfhoghlaim-educational-mmo/spec.md`

## Phase 7 — Spec merge (4 sources → canonicals)

- [ ] 7.1 `ncca-leaving-cert-root-pdfs` → rm -rf; add 1 Requirement + 2 Scenarios to `oideachais-pipeline/spec.md` under "NCCA Root PDFs" subsection
- [ ] 7.2 `retro-game-asset-pipeline` → rm -rf; add 3 Requirements to `retro-game-design-catalogue/spec.md`
- [ ] 7.3 `data-engineering-space` → rm -rf; add 1 Requirement to `data-engineering-pipeline-documentation/spec.md`
- [ ] 7.4 Internal `cocoindex-v1-migration` body → fold into `oideachais-cocoindex-v1-migration/spec.md`

## Phase 8 — Spec repair (4 zero-req → valid)

Extract Requirements + Scenarios from each spec's existing body prose.

- [ ] 8.1 `openspec/specs/bonneagar-iac-merge/spec.md` → extract 3 Requirements + 5 Scenarios (typed clients, discoverers, CLI commands, bootstrap flag)
- [ ] 8.2 `openspec/specs/bonneagar-komodo-gitops/spec.md` → extract 2 Requirements + 4 Scenarios (3 resource-syncs, 60s interval, 2-host topology)
- [ ] 8.3 `openspec/specs/oideachais-email-triage/spec.md` → extract 4 Requirements + 6 Scenarios (MBOX DLT, email.baml, CocoIndex App, ADK agent)
- [ ] 8.4 `openspec/specs/infrastructure-stacks-documentation/spec.md` → extract 2 Requirements + 4 Scenarios (per-stack docs contract, 4-section template, stack-doctor CI gate)

## Phase 9 — Spec new (4 ADDED canonicals)

- [ ] 9.1 Create `openspec/specs/british-isles-education-pipeline/spec.md` (5 Requirements + 8 Scenarios)
- [ ] 9.2 Create `openspec/specs/agent-platform-cluster/spec.md` (3 Requirements + 6 Scenarios)
- [ ] 9.3 Create `openspec/specs/apple-photos-ingestion/spec.md` (4 Requirements + 6 Scenarios)
- [ ] 9.4 Create `openspec/specs/ireland-primary-jc-dlt-baml/spec.md` (3 Requirements + 4 Scenarios)

## Phase 10 — Spec path rewrite (25 specs, mechanical)

Find-replace per the table in A.8 of proposal.md.

- [ ] 10.1 `oideachais-pipeline/spec.md` (108 sruth + ~5 infra/stacks hits)
- [ ] 10.2 `meaisinfhoghlaim-platform/spec.md` (97 hits)
- [ ] 10.3 `croilar-data-engineering/spec.md` (36 hits)
- [ ] 10.4 `agentic-frontend-frameworks/spec.md` (17 hits)
- [ ] 10.5 `data-engineering-pipeline-documentation/spec.md` (15 hits)
- [ ] 10.6 `oideachais-leabharlann/spec.md` (9 hits)
- [ ] 10.7 `meaisinfhoghlaim-agent-frameworks/spec.md` (9 hits)
- [ ] 10.8 `upstream-package-monitoring/spec.md` (9 hits)
- [ ] 10.9 `spaces-cicd-pipeline/spec.md` (8 hits)
- [ ] 10.10 `infrastructure-stacks/spec.md` (8 hits)
- [ ] 10.11 `oideachais-marimo-dashboards/spec.md` (7 hits)
- [ ] 10.12 `indexing-and-cognition/spec.md` (7 hits)
- [ ] 10.13 `agent-registry/spec.md` (7 hits)
- [ ] 10.14 `agent-memory-systems/spec.md` (7 hits)
- [ ] 10.15 `oideachais-baml-schemas/spec.md` (already in Phase 1.1 of existing change; verify complete)
- [ ] 10.16–10.25 Remaining ~10 specs (the agent-platform, observability, dagster-5-layer, dagger-pipelines, meaisinfhoghlaim-ocr-htr, official-media-*, documentation, dev-env-demo-tools, cianfhoghlaim-educational-mmo, cianfhoghlaim-leaving-cert-portal)

## Phase 11 — Spec Purpose rewrite (12 specs)

Replace `Purpose: TBD - created by archiving change <X>. Update Purpose after archive.` with real 3-8 sentence Purpose paragraphs.

- [ ] 11.1 `celtic-asset-generation`
- [ ] 11.2 `oideachais-cocoindex-v1-migration`
- [ ] 11.3 `official-media-pipeline`
- [ ] 11.4 `official-media-marimo`
- [ ] 11.5 `official-media-fediverse`
- [ ] 11.6 `documentation`
- [ ] 11.7 `dev-env-demo-tools`
- [ ] 11.8 `oideachais-leabharlann`
- [ ] 11.9 `oideachais-marimo-dashboards`
- [ ] 11.10 `oideachais-cognify-knowledge-graph`
- [ ] 11.11 `oideachais-semantic-search`
- [ ] 11.12 `oideachais-baml-schemas`

## Phase 12 — Root doc sweep

- [ ] 12.1 `openspec/AGENTS.md` → sweep sruth/ paths (L143-205); fix spec count "36/37" → 48; remove the 2 phantom-spec rows; drop the tuatha-platform deprecated-alias note
- [ ] 12.2 `openspec/project.md` → refresh §180-202 in-flight changes table; update spec count to 48; add the 4 new canonicals from A.7 to the right groups

## Phase 13 — Plans directory

- [ ] 13.1 Refresh frontmatter on the 6 kept plans: STATUS.md, education_audit_plan.md, gcp_ai_optimization_strategy.md, infrastructure_deep_dive.md, final_exponential_strategy.md, package-updates.md
- [ ] 13.2 Move 6 plans to `openspec/plans/archive/2026-07-06-plans-refresh/`: data_engineering_deep_dive.md, deployment_and_ai_strategy.md, deployment_stack_strategy.md, exponential_improvement_roadmap.md, machine_learning_deep_dive.md, web_and_dashboards_deep_dive.md
- [ ] 13.3 Update `openspec/plans/STATUS.md` to reflect the new 6+6 split and refresh links

## Phase 14 — Extended change archive (12 additional)

- [ ] 14.1 `openspec archive add-openclaw-stack-and-channel-fanout --yes`
- [ ] 14.2 `openspec archive add-openchamber-stack-and-opencode-ui --yes`
- [ ] 14.3 `openspec archive consolidate-cianfhoghlaim-subdirs --yes`
- [ ] 14.4 `openspec archive deploy-llama-swap-v166-stack --yes`
- [ ] 14.5 `openspec archive deploy-v4-ocr-vlm-on-m4-max --yes`
- [ ] 14.6 `openspec archive wire-6-stage-pdf-pipeline-to-production --yes`
- [ ] 14.7 `openspec archive wire-baml-to-consolidated-pipelines --yes`
- [ ] 14.8 `openspec archive wire-baml-with-known-consumers --yes`
- [ ] 14.9 `openspec archive wire-unwired-dlt-sources --yes`
- [ ] 14.10 `openspec archive wire-v4-models-into-litellm-config --yes`
- [ ] 14.11 Verify `celtic-data-engineering-patterns` is in Phase 3.2.17 of original tasks; skip if duplicate
- [ ] 14.12 Verify `refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline` is in Phase 3.2.18; skip if duplicate

## Phase 15 — Validate (8 gates)

- [ ] 15.1 `openspec validate 2026-07-06-drift-cleanup-and-v4-alignment --strict`
- [ ] 15.2 `openspec list --specs | wc -l` should be 49 (48 specs + 1 `__pycache__`)
- [ ] 15.3 `mise run lint:skills`
- [ ] 15.4 `bun run ccc:index` (rebuild after sruth/ paths removed)
- [ ] 15.5 `grep -r 'sruth/' openspec/specs/` returns 0 hits
- [ ] 15.6 `grep -r 'infisical://dev-baile/sruth/' .` returns 0 hits
- [ ] 15.7 `grep -r 'infrastructure/stacks/' openspec/specs/` returns 0 hits
- [ ] 15.8 `grep -r 'Purpose: TBD' openspec/specs/` returns 0 hits

## Phase 16 — Final commit + archive + push

- [ ] 16.1 `git add openspec/`
- [ ] 16.2 `git commit -m "drift-cleanup: retire 12 specs, add 4 canonicals, refresh plans, archive 12 more changes (2026-07-06)"`
- [ ] 16.3 `openspec archive 2026-07-06-drift-cleanup-and-v4-alignment --yes`
- [ ] 16.4 `git push`

(Combined with the original Phases 5.1-5.4, the work lands in two commits:
one for the spec + plans + archives, one for the archive of the change itself.)
- [ ] 5.3 `openspec archive 2026-07-06-drift-cleanup-and-v4-alignment --yes`
- [ ] 5.4 `git push`