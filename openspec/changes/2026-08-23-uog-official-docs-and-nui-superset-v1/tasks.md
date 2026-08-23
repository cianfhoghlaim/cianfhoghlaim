# Tasks — 2026-08-23-uog-official-docs-and-nui-superset-v1

## WS1 — openspec contract (this change)

- [x] `proposal.md`
- [x] `tasks.md`
- [ ] 5 sub-specs (each with `### Requirement` + `#### Scenario`):
  - [ ] `specs/cianfhoghlaim-uog-official-docs/spec.md`
  - [ ] `specs/cianfhoghlaim-british-isles-tertiary-factory/spec.md`
  - [ ] `specs/cianfhoghlaim-ducklake-tertiary/spec.md`
  - [ ] `specs/cianfhoghlaim-tertiary-embeddings/spec.md`
  - [ ] `specs/cianfhoghlaim-tertiary-marimo/spec.md`
- [ ] 2 design notes:
  - [ ] `design/cianext-uog-stage-0-firecrawl-agent.md` — Firecrawl `/agent` URL discovery flow
  - [ ] `design/stages-vocabulary.md` — canonical Stage-0..Stage-3 vocabulary

## WS2 — BAML schema

- [ ] `baml_src/british_isles/ireland/education/university/uog_official_docs_extraction.baml`
  - 4 new classes (UoGNUIMemberDescriptor, UoGStudentsUnionDocument,
    UoGNUISyllabusDescriptor, UoGOfficialDocument)
  - 3 new enums (UoGOfficialDocumentType, UoGNUIMemberKind, UoGSUResourceKind)
  - 4 new functions (ExtractUoGOfficialDocument, ExtractUoGNUIMemberPage,
    ExtractUoGStudentsUnionDocument, ExtractUniversityOfficialDocUniversal)
  - All routed through `ExtractEn`

## WS3 — DLT sources + British Isles factory

- [ ] `dlt_sources/british_isles/ireland/education/university/official_docs/__init__.py`
- [ ] `dlt_sources/british_isles/ireland/education/university/official_docs/uog_official_docs_source.py`
  - 3 resources: `official_documents`, `key_pages`, `url_discovery_log`
- [ ] `dlt_sources/british_isles/ireland/education/university/official_docs/nui_federation_source.py`
  - 3 resources: `nui_members`, `nui_constituent_circulars`, `nui_archive`
- [ ] `dlt_sources/british_isles/ireland/education/university/official_docs/uog_students_union_source.py`
  - 2 resources: `students_union_documents`, `class_rep_handbooks`
- [ ] `dlt_sources/british_isles/university/__init__.py`
- [ ] `dlt_sources/british_isles/university/british_isles_tertiary_factory.py`
  - `BITertiaryDeepExtractionConfig(university_id, base_url, nation, ..., sso_required)`
  - Factory emits a 6-resource DLT source (extends `UniversityDeepExtractionConfig`)
- [ ] `dlt_sources/british_isles/university/bitertiary_universities_factory.py`
  - Concrete wrappers: `bitertiary_qub_source()`, `bitertiary_ulster_source()`, etc.

## WS4 — Secret resolver extensions

- [ ] `bonneagar/stacks/browser/sruth_browser/core/secrets.py` —
  add `UniversitySsoConfig(BaseSsoConfig)` (the BASE config with NUI + SU + QUB variants)
- [ ] Same Infisical → `.env` → `op` priority chain
- [ ] Secret name whitelist extended to `UNIVERSITY_SSO_*`

## WS5 — Dagster assets (4 sub-groups, ~15 assets)

- [ ] Extend `orchestration/defs/uog_exam.py` (the existing 5 assets) — no changes needed
- [ ] `orchestration/defs/uog_official_docs.py`
  - 5 assets: `uog_official_docs_stage0_audit`,
    `uog_official_docs_stage1_collect`, `uog_official_docs_baml_extract`,
    `uog_official_docs_embed_lance`, `uog_official_docs_duckdb_sink`
- [ ] `orchestration/defs/nui_federation.py`
  - 3 assets: `nui_federation_audit`, `nui_constituents_scrape`,
    `nui_archive_ingest`
- [ ] `orchestration/defs/uog_students_union.py`
  - 2 assets: `uog_su_stage0_audit`, `uog_su_collect`
- [ ] `orchestration/defs/british_isles_tertiary.py`
  - 5 assets: `bitertiary_pre_research`, `bitertiary_bulk_scrape`,
    `bitertiary_extract_courses`, `bitertiary_extract_modules`,
    `bitertiary_extract_programmes`
- [ ] Wire all 4 sub-groups into `orchestration/definitions.py`

## WS6 — VLM extractor extension

- [ ] `dlt_sources/.../university/exam_papers/uog_exam_vlm.py`
  - add `UniversityOfficialDocVLMExtractor` class (mirrors `UoGExamVLMConfig`)

## WS7a — DuckLake destinations

- [ ] `dlt_sources/_lakehouse/__init__.py`
- [ ] `dlt_sources/_lakehouse/destinations.py`
  - `LocalDuckLakeDestination(path=DUCKDB_PATH)`
  - `MotherDuckLakeDestination(uri="md:cianfhoghlaim", mtoken_secret="MOTHERDUCK_TOKEN")`
  - `BonneagarLakehouseDestination(uri="ducklake:postgres:host=lakehouse-postgres …")`
- [ ] All 5 new DLT sources accept `destination: Literal["local","motherduck","bonneagar"]`

## WS7b — CocoIndex apps (bump from 14 → 17)

- [ ] `cocoindex_flows/british_isles/ireland/education/university/uog_official_docs_embedding.py`
  - `UoGOfficialDocsApp` (BGE-M3 1024-d)
- [ ] `cocoindex_flows/british_isles/ireland/education/university/nui_federation_embedding.py`
  - `NuiFederationApp`
- [ ] `cocoindex_flows/british_isles/ireland/education/university/uog_students_union_embedding.py`
  - `UoGStudentsUnionApp`
- [ ] `cocoindex_flows/british_isles/university/app_factory.py`
  - `bitertiary_universities_app_factory(config)` — generates one v1 App per nation

## WS7c — Cognee edges

- [ ] `scripts/graph_storage/cognify/rules/uog_official_doc_describes_module.py`
  - edge `UoGOfficialDoc-DESCRIBES-UoGModuleDescriptor`
- [ ] `scripts/graph_storage/cognify/rules/uog_su_covers_service.py`
  - edge `UoGStudentsUnionDocument-COVERS-UoGServiceArea {academic,welfare,equality,class_reps}`
- [ ] `scripts/graph_storage/cognify/rules/nui_member_connects.py`
  - edge `UoGNUIMemberDescriptor-CONNECTED_TO-UoGModuleDescriptor`
- [ ] Wire into the existing cognify runner (`scripts/graph_storage/cognify/rules/__init__.py` or equivalent)

## WS7d — Marimo (3 sibling notebooks, 8 tabs each)

- [ ] `notebooks/12_uog_exam_papers.py` (NEW, supersedes the 3-tab `11_uog_exam_papers.py` from the WS1-WS8 lift)
- [ ] `notebooks/13_nui_federation.py` (NEW)
- [ ] `notebooks/14_uog_students_union.py` (NEW)
- All 3 follow the canonical 8-tab BIEP pattern (Health / Filters / Materials / URL Health / Heatmap / Recent / Lance Search / SQL Console)
- All 3 use `mo.sql(engine=md:cianfhoghlaim)` primary + local DuckDB fallback
- All 3 prefer `ibis.duckdb.connect(uri)` over raw `duckdb.connect()`

## WS8 — Tests + observability + thesis figures

- [ ] `tests/uog_official_docs/` (4 modules)
- [ ] `tests/nui_federation/` (3 modules)
- [ ] `tests/students_union/` (3 modules)
- [ ] `tests/british_isles_tertiary/` (2 modules)
- [ ] `tests/uog_official_docs/test_secrets_university_sso.py`
- [ ] `tests/uog_official_docs/test_ducklake_destinations.py`
- [ ] `scripts/uog_official_docs_stage0.py` — the per-institution one-liner
- [ ] `orchestration/defs/uog_official_docs_figures.py` — generates `figures/thesis/{vlm_exam_ocr_chart.pdf, nui_module_equivalence_heatmap.pdf, students_union_service_coverage.pdf}`
