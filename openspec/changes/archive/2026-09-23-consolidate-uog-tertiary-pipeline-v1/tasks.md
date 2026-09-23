# Tasks: 2026-09-23-consolidate-uog-tertiary-pipeline-v1

## 1. Group A — Rename + move

- [ ] **A1** `git mv dlt_sources/british_isles/ireland/university/ dlt_sources/british_isles/ireland/tertiary/` (5 sources + `__init__.py`)
- [ ] **A2** `mkdir -p baml_src/british_isles/ireland/tertiary/` (move from `baml_src/british_isles/ireland/education/university/`)
- [ ] **A3** Rename `course_catalog.py` → `programme_catalog.py` (KCG → cianfhoghlaim naming)
- [ ] **A4** Rename `university_council_minutes.py` → `governance_minutes.py`
- [ ] **A5** Update all `from .university` imports → `from .tertiary` in BIEP consumers
- [ ] **A6** Update `openspec/specs/british-isles-education-pipeline-v3/spec.md:698` stage taxonomy `'university'` → `'tertiary'`
- [ ] **A7** Update `mise.toml`: replace `oideachais:university:*` aliases with `oideachais:tertiary:*`
- [ ] **A8** Update `meaisinfhoghlaim/models/registry.py:236` "browser" suffix comment

## 2. Group B — Extract SU package from ciandlithe

- [ ] **B1** `mkdir -p agents/meaisinfhoghlaim/educational/students_union/`
- [ ] **B2** Copy 14 SU files from `~/dev/ciandlithe/agents/adk/students_union/` → `agents/meaisinfhoghlaim/educational/students_union/`
- [ ] **B3** Rewrite all internal imports from `.tools.X` → `.tools.X` (no path change, just verify)
- [ ] **B4** Re-license: replace `BUSL-1.1 v2 CIANDLITHE edition` reference with `BUSL-1.1 Cianfhoghlaim edition` in all 14 files' docstrings
- [ ] **B5** Update `agents/agent_registry.py` to register `students_union_root_agent` as the 13th specialist in the 12-agent fleet
- [ ] **B6** Update `agents/meaisinfhoghlaim/AGENTS.md` routing table to include the SU package
- [ ] **B7** Open `openspec/changes/<YYYY-MM-DD>-remove-students-union-from-ciandlithe-v1/` in ciandlithe (the removal change)
- [ ] **B8** Copy `notebooks/students_union_adk_case_studies.py` → `notebooks/_shared/tertiary/students_union_adk_case_studies.py` (remove cross-repo `sys.path` hack)
- [ ] **B9** Copy `notebooks/students_union_kcg_integration.py` → `notebooks/_shared/tertiary/students_union_tertiary_integration.py` (rename; rewrite imports to `dlt_sources.british_isles.ireland.tertiary.uog`)
- [ ] **B10** Copy `_smoke_test.py` → `tests/agents/students_union/test_smoke.py` (rename; rewire paths)

## 3. Group C — Schema consolidation

- [ ] **C1** Refactor `baml_src/british_isles/ireland/tertiary/university_extraction.baml`: replace the existing CourseDescriptor/ModuleDescriptor/ProgrammeDescriptor with College + School + Programme + Module (merge KCG CourseOutline into Module; add 4 new Module fields)
- [ ] **C2** Move `academic_calendar.baml` from KCG → `baml_src/british_isles/ireland/tertiary/`
- [ ] **C3** Move `governance_minute.baml` from KCG → `baml_src/british_isles/ireland/tertiary/`
- [ ] **C4** Move `press_release.baml` from KCG → `baml_src/british_isles/ireland/tertiary/`
- [ ] **C5** Write `research_output.baml` (NEW — research publications + theses extraction)
- [ ] **C6** Write `module_handbook.baml` (NEW — per-module PDF extraction)
- [ ] **C7** Write `reading_list.baml` (NEW — per-module reading list extraction)
- [ ] **C8** Write `past_paper.baml` (NEW — per-module past paper extraction)
- [ ] **C9** Write `uoa_portal_content.baml` (NEW — the ADK vision-language extraction for the authenticated portal)
- [ ] **C10** `baml-cli generate --from baml_src` exits 0
- [ ] **C11** `bun run ccc:search "Module class"` returns exactly 1 hit (no duplicates)

## 4. Group D — DLT sources

- [ ] **D1** Copy `dlt_sources/uog/__init__.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/__init__.py`
- [ ] **D2** Copy `dlt_sources/uog/_base.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/_base.py`; refactor to subsume TertiaryPipelineBase
- [ ] **D3** Copy `academic_calendar.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/academic_calendar.py`
- [ ] **D4** Copy `governance_minutes.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/governance_minutes.py` (renamed from `university_council_minutes.py`)
- [ ] **D5** Copy `press_releases.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/press_releases.py`
- [ ] **D6** Copy `programme_catalog.py` from KCG (renamed from `course_catalog.py`)
- [ ] **D7** Copy `research_outputs.py` from KCG → `dlt_sources/british_isles/ireland/tertiary/uog/research_outputs.py`
- [ ] **D8** Write `colleges.py` (NEW — 4 UoG colleges)
- [ ] **D9** Write `schools.py` (NEW — per-college schools)
- [ ] **D10** Write `programmes.py` (NEW — per-programme listings)
- [ ] **D11** Write `modules.py` (NEW — per-module deep listing)
- [ ] **D12** Write `module_handbooks.py` (NEW — PDF download + OCR)
- [ ] **D13** Write `reading_lists.py` (NEW — graceful null on schools that don't publish)
- [ ] **D14** Write `past_papers.py` (NEW — uses per-user regexam credential vault)
- [ ] **D15** Write `regexam_papers.py` (NEW — the regexam authenticated scraper, mirror of `examinations_papers.py`)
- [ ] **D16** Write `canvas_materials.py` (NEW — Canvas REST primary + M365 OAuth fallback)
- [ ] **D17** Update `dlt_sources/common/site_crawler.py` (+4 ScrapePolicy rows for regexam + canvas)
- [ ] **D18** Copy `scripts/osint_allowlist.yaml` from KCG → `scripts/osint_allowlists/ireland_tertiary.yaml`
- [ ] **D19** Extend `scripts/lint_osint_allowlists.py` (was `lint_osint_allowlist.py`) to handle all 8 jurisdiction allowlists
- [ ] **D20** `pn dlt_pipeline --source uog_<name>` runs end-to-end for all 14 sources

## 5. Group E — BAML

- [ ] **E1** Write `university_extraction.baml` (refactored: 4 classes + 5 functions)
- [ ] **E2** Write `academic_calendar.baml` (from KCG)
- [ ] **E3** Write `governance_minute.baml` (from KCG)
- [ ] **E4** Write `press_release.baml` (from KCG)
- [ ] **E5** Write `research_output.baml` (NEW)
- [ ] **E6** Write `module_handbook.baml` (NEW)
- [ ] **E7** Write `reading_list.baml` (NEW)
- [ ] **E8** Write `past_paper.baml` (NEW)
- [ ] **E9** Write `uoa_portal_content.baml` (NEW)
- [ ] **E10** `baml-cli generate --from baml_src` exits 0

## 6. Group F — CocoIndex factory

- [ ] **F1** Write `_shared.py` with `create_uog_module_flow(config: UoGTertiaryConfig)` + `UoGTertiaryConfig` dataclass
- [ ] **F2** Write `_modules.yaml` (~1,500-row module config; Phase 1 ships ~50 stub rows)
- [ ] **F3** Write `colleges_flow.py`
- [ ] **F4** Write `schools_flow.py`
- [ ] **F5** Copy + rename `programme_flow.py` (from KCG `courses_flow.py`; embedder upgrade to BGE-m3)
- [ ] **F6** Copy `governance_flow.py` (embedder upgrade)
- [ ] **F7** Write `press_releases_flow.py`
- [ ] **F8** Write `research_outputs_flow.py`
- [ ] **F9** Write `module_flow.py` (the factory-rendered flow)
- [ ] **F10** Write `module_handbook_flow.py`
- [ ] **F11** Write `reading_list_flow.py`
- [ ] **F12** Write `past_paper_flow.py`
- [ ] **F13** Factory emits ≥1,500 module Apps (validated via `pn` end-to-end)

## 7. Group G — Authenticated stacks + ADK vision-language agent

- [ ] **G1** Write `bonneagar/stacks/regexam-nuig/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`
- [ ] **G2** Write `bonneagar/stacks/canvas-nuig/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`
- [ ] **G3** Write `bonneagar/stacks/uo-portal-vault/{compose,sidecar,secrets.env,pangolin,blueprint}.yaml` + `.env.example`
- [ ] **G4** Add 2 Locket `InfisicalSecret` entries for `regexam-nuig/{username,password}` and 2 for `canvas-nuig/{username,password}` in `bonneagar/dagger/cianfhoghlaim_dagger/__init__.py`
- [ ] **G5** Write `agents/uoa_portal/portal_agent.py` (the 5-stage SequentialAgent)
- [ ] **G6** Write `agents/uoa_portal/tools/uoa_browse.py` (Patchright + vision)
- [ ] **G7** Write `agents/uoa_portal/tools/uoa_vision.py` (Gemini 2.5 Pro)
- [ ] **G8** Write `agents/uoa_portal/tools/stream_to_lakehouse.py`
- [ ] **G9** Write `agents/uoa_portal/tools/baml_extract_uoa_portal.py`
- [ ] **G10** Write `agents/uoa_portal/tools/cocoindex_upsert.py`
- [ ] **G11** Register `uoa_portal_pipeline` + `students_union_root_agent` in `opencode.json`
- [ ] **G12** `komodo deploy regexam-nuig && komodo deploy canvas-nuig && komodo deploy uo-portal-vault` succeed

## 8. Group H — Dagster orchestration

- [ ] **H1** Write `orchestration/defs/1_ingestion/tertiary/uog/{14 DLT assets}.py`
- [ ] **H2** Write `orchestration/defs/2_materials/tertiary/uog/{14 BAML extraction assets}.py` (6 RAGAS asset checks)
- [ ] **H3** Write `orchestration/defs/3_model_lifecycle/tertiary/uog/{embedder routing, OCR ensemble}.py`
- [ ] **H4** Write `orchestration/defs/4_asset_generation/tertiary/uog/{10 CocoIndex assets + firecrawl_budget_asset}.py`
- [ ] **H5** Write `orchestration/defs/5_agent_ops/tertiary/uog/{uoa_portal_agent, students_union_root_agent, schedule, sensor, RAGAS evaluator}.py`
- [ ] **H6** Update `orchestration/defs/4_budget/firecrawl_budget_asset.py` (+4 budget rows)
- [ ] **H7** Update `orchestration/partitions.py` (+1 partition for `uoa_portal`)
- [ ] **H8** Update `mise.toml` (`oideachais:tertiary:*` + `oideachais:uoa-portal:*` task namespaces)
- [ ] **H9** Update `scripts/cognee_ingest_uoa_portal.py` (NEW; `uoa_portal` cluster)
- [ ] **H10** Update `meaisinfhoghlaim/models/model_registry.py` (+qwen3-vl-8b, +gemini-2.5-pro)

## 9. Group I — marimo + validation + retirement

- [ ] **I1** Copy KCG `notebooks/uog_doc_processing_pipeline.py` → `notebooks/_shared/tertiary/uog_explorer.py` (rename)
- [ ] **I2** Write `notebooks/_shared/tertiary/00_uog_tertiary_overview.py` (6 tabs)
- [ ] **I3** Write 4 college-level notebooks (`01_uog_college_<college-id>.py`)
- [ ] **I4** Write 20 programme-level notebooks (`02_uog_programme_<programme-id>_top_20.py`)
- [ ] **I5** Write `notebooks/_shared/tertiary/03_uog_past_papers_explorer.py`
- [ ] **I6** Write `notebooks/_shared/tertiary/04_uog_module_handbook_explorer.py`
- [ ] **I7** Update `web/apps/cianfhoghlaim-leaving-cert/apps/api/src/copilotkit/actions.ts` (+2 actions)
- [ ] **I8** Update `openspec/AGENTS.md` priority specs table (add `cianfhoghlaim-tertiary-pipeline`)
- [ ] **I9** Write `.agents/skills/uoa-tertiary-pipeline/SKILL.md`
- [ ] **I10** Update `openspec/specs/cianfhoghlaim-university-deep-extraction/spec.md` (DEPRECATED notice)
- [ ] **I11** `openspec validate 2026-09-23-consolidate-uog-tertiary-pipeline-v1 --strict` exits 0
- [ ] **I12** `mise run lint:osint && mise run lint:skills && mise run lint:drift-docs && mise run lint:firecrawl-budget && mise run sync:all && mise run lint:openspec` all exit 0
- [ ] **I13** `python tests/tertiary/test_uog_smoke.py` exits 0
- [ ] **I14** `python agents/meaisinfhoghlaim/educational/students_union/_smoke_test.py` exits 0
- [ ] **I15** `pn` runs the 5-phase pattern end-to-end on UoG College of Science + Engineering
- [ ] **I16** `git grep kings_college_galway` returns 0
- [ ] **I17** `git grep ollscoil-na-gaillimhe` returns 0
- [ ] **I18** `git grep students_union` returns 0 in ciandlithe (only in updated README/AGENTS/LICENSE)
- [ ] **I19** `gh repo delete cianfhoghlaim/ollscoil-na-gaillimhe` returns 204
- [ ] **I20** `rm -rf ~/dev/kings_college_galway` succeeds

## 10. Final validation

- [ ] **Z1** `openspec validate --all --strict` exits 0
- [ ] **Z2** `mise run openspec:archive 2026-09-23-consolidate-uog-tertiary-pipeline-v1` (archives the change)
- [ ] **Z3** Archive the ciandlithe removal change in ciandlithe (per the cross-repo-sync.md ordering)
- [ ] **Z4** `mise run sync:all` exits 0 (the 14-layer sync)
