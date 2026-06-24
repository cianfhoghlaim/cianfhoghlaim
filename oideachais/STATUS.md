# Oideachais — Pipeline STATUS

**Last updated:** 2026-06-16
**Single source of truth** for: which BAML schemas are wired to dlt sources, which Dagster assets materialise them, which CocoIndex flows embed them, and which Cognee cognify passes enrich them.

> If you change any of: BAML schema files, dlt source files, Dagster assets, CocoIndex flows, or Cognee cognify assets — **update this file in the same commit.**

## Reading guide

1. **[§ 1 BAML × dlt × Dagster × CocoIndex matrix](#1-baml--dlt--dagster--cocoindex-matrix)** — which BAML function backs which dlt source / Dagster asset / CocoIndex flow.
2. **[§ 2 Per-nation × per-cycle coverage matrix](#2-per-nation--per-cycle-coverage-matrix)** — British Isles education coverage (Ireland, England, Scotland, Wales, Northern Ireland, Crown Dependencies).
3. **[§ 3 CocoIndex v0 vs v1 status](#3-cocoindex-v0-vs-v1-status)** — which flows are v1 (working on cocoindex==1.0.9), which are v0 (broken), which are unwired.
4. **[§ 4 Dagster asset catalogue](#4-dagster-asset-catalogue)** — 21 asset modules, 7 groups.
5. **[§ 5 Leabharlann pipeline status](#5-leabharlann-pipeline-status)** — the 6 dlt sources, 7 Dagster assets, 3 v1 CocoIndex Apps, 4 BAML schemas, 6 search handlers.
6. **[§ 6 Open refactor backlog](#6-open-refactor-backlog)** — 5 high-leverage features in `oideachais/REFACTORING.md`.

---

## 1. BAML × dlt × Dagster × CocoIndex matrix

| BAML file | Classes | Extraction functions | dlt source(s) that invoke it | Dagster asset(s) | CocoIndex flow |
|:--|:--|:--|:--|:--|:--|
| `aistear.baml` | `AistearTheme`, `AistearPrinciple`, `AistearLearningGoal`, `Naionra`, `AistearDocument`, `BridgeEdge` (8) | `ExtractAistearFramework` | `oideachais/dlt_sources/ireland/aistear.py` (planned) | (no Dagster asset) | (none) |
| `primary.baml` | `PrimaryStage`, `PrimaryAreaCode`, `CompetencyLink`, `PrimaryLearningOutcome`, `PrimaryStrand`, `PrimaryCurriculumArea` (6) | `ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes` | **MISSING** — `dlt_sources/ireland/primary.py` does not exist | (none) | (none) |
| `junior_cycle.baml` | `JuniorCycleSubject`, `JuniorCycleShortCourse`, `AchievementLevel`, `RubricDescriptor`, `CBATask`, `JCWellbeingStatement`, `JCSubjectSpec`, `L2LPOutcome` (8) | `ExtractJCSpec`, `ExtractCBADescriptor` | **MISSING** — `dlt_sources/ireland/junior_cycle.py` does not exist | (none) | (none) |
| `tertiary.baml` | `NFQLevel`, `EQFLevel`, `HEIType`, `EntryPathway`, `MatriculationRequirement`, `CAOCourse`, `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline` (10) | (TBD) | `oideachais/dlt_sources/ireland/tertiary.py` | (no Dagster asset) | (none) |
| `curriculum_extraction.baml` | `LearningOutcome`, `ExtractedRelationship`, `RelationshipExtractionResult`, `Skill`, `SkillExtractionResult`, `CurriculumSection`, `ExtractedCurriculumDocument`, `EnhancedLearningOutcome`, `CurriculumStrand`, `AssessmentComponent`, `AssessmentInfo`, `CurriculumSpecification` (12) | `ExtractLearningOutcomeRelationships`, `ExtractSkillsFromOutcome`, `ExtractCurriculumFromDocument` | `oideachais/dlt_sources/ireland/curriculum_source.py` | `ireland/education/curriculum_dlt_assets.py` (70+ @dlt_assets) | `oideachais/cocoindex_flows/curriculum_embedding.py` (v0 — broken) |
| `ui_components.baml` | `UIComponentKind`, `UIComponentSuggestion` (2) | `SuggestUIComponents` | (called by `oideachais/dagster_defs/assets/ui_suggestion.py`) | `ui_suggestion_asset` (nightly) | (none — populates LanceDB directly) |
| `author_archive.baml` | `GeminiDomain`, `UoGArtifactKind`, `UoGStage`, `UoGLanguage`, `EquationConfidence`, `CitedUrl`, `GeminiDeepResearchReport`, `UniversityOfGalwayArtifact`, `HandwrittenEquation`, `PaperKind`, `Author`, `ZoteroPaper` (12) | `ExtractGeminiReport`, `ExtractUoGArtifact`, `ExtractHandwrittenEquations`, `ExtractZoteroMetadata` | `oideachais/dlt_sources/author_archive/{gemini_deep_research,university_of_galway,leabharlann_books,zotero,takeout_v1}.py` (5 sources) | `oideachais/dagster_defs/assets/{author_archive,leabharlann}_assets.py` (14 assets) | `oideachais/cocoindex_flows/{author_archive,leabharlann}_embedding.py` (2 flows; 1 v1 + 1 v0) |
| `image_generation.baml` | (image-generation helpers) | (FIBO + Z-Image-Turbo extraction) | (called by `oideachais/dagster_assets/asset_generation_assets.py`) | `asset_generation_assets` | (none — image gen) |

**Summary**: 8 BAML files, 44 classes, ~12 extraction functions. **8 of 12 functions are invoked from at least one dlt source / Dagster asset.** 4 are *defined but never invoked*:

- `ExtractHandwrittenEquations` — defined in `author_archive.baml`, called only in `oideachais/ocr/author_archive_ocr.py:1` (not wired to any Dagster asset).
- `ExtractZoteroMetadata` — defined, called by **no dlt source** (zotero.py yields rows but never calls BAML).
- `ExtractPrimaryFramework` + `ExtractPrimaryLearningOutcomes` — primary.py dlt source does not exist.
- `ExtractJCSpec` + `ExtractCBADescriptor` — junior_cycle.py dlt source does not exist.

See `oideachais/REFACTORING.md` for the 5 backlog features that close these gaps.

---

## 2. Per-nation × per-cycle coverage matrix

Status: ✅ working · ⚠️ partial · 🟡 planned · ❌ missing

### Ireland (Aistear → Tertiary)

| Cycle | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **Aistear** (early childhood) | `ireland/aistear.py` ✅ | `ExtractAistearFramework` 🟡 (in `baml_src/aistear.baml`, not invoked) | (planned via `cross_stage_cognify.py`) | `cross_stage_cognify` ✅ | (none) |
| **Primary** | `ireland/primary.py` ✅ (4 resources: `primary_specifications`, `primary_curriculum_areas`, `primary_strands`, `primary_learning_outcomes`) | `ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes` ✅ invoked | (none yet — see `REFACTORING.md`) | (planned via `cross_stage_cognify.py`) | (none yet) |
| **Junior Cycle** | `ireland/junior_cycle.py` ✅ (3 resources: `jc_specifications`, `jc_short_courses`, `cba_tasks`) | `ExtractJCSpec`, `ExtractCBADescriptor` ✅ invoked | (none yet — see `REFACTORING.md`) | (planned via `cross_stage_cognify.py`) | (none yet) |
| **Senior Cycle** | `ireland/senior_cycle.py`, `leaving_cert.py` ✅ | (TBD — BAML `curriculum_extraction.baml` covers) | `leabharlann/leaving_cert/dlt_assets.py` ✅ | ✅ | `curriculum_embedding.py` (v0 — broken) |
| **Tertiary** (CAO / QQI-FET / Apprenticeship) | `ireland/tertiary.py` ✅ | ✅ defined (`baml_src/tertiary.baml`) | (planned) | (planned) | (none) |
| **SEC examinations** | `ireland/examinations.py` ✅ | (TBD) | `ireland/education/exam_materials_assets.py` ✅ | ✅ | (none) |
| **OIDE CPD** | `ireland/oide.py` ✅ | (TBD) | (none) | (none) | (none) |
| **NCCA** (core) | `ireland/ncca.py` ✅ | ✅ (curriculum_extraction) | `ireland/education/curriculum_dlt_assets.py` ✅ | ✅ | `curriculum_embedding.py` (v0 — broken) |

### England

| Cycle | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **Key Stage 1-2** (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Key Stage 3-4** (secondary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **Key Stage 5** (post-16) | `uk/england/dfe_explore_statistics.py`, `national_curriculum.py`, `ofsted.py`, `school_info.py` ✅ | (none for KS5) | `uk_education_assets.py` (England assets) ✅ | (none) | (none) |

### Scotland

| Cycle | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **CfE Early Level** (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **CfE First/Second Level** (lower secondary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **CfE Third/Fourth Level** (upper secondary) | `uk/scotland/curriculum_for_excellence.py` ✅ | (none) | `uk_education_assets.py` (Scotland assets) ✅ | (none) | (none) |
| **SQA qualifications** (post-16) | `uk/scotland/gov_scot_statistics.py`, `insight_benchmarking.py`, `simd.py` ✅ | (none) | ✅ | (none) | (none) |

### Wales

| Cycle | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **Foundation Phase** (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **KS3-4** (secondary) | `uk/wales/curriculum_for_wales.py` ✅ | (none) | `uk_education_assets.py` (Wales assets) ✅ | (none) | (none) |
| **KS5** (post-16) | `uk/wales/curriculum_for_wales.py` ✅ | (none) | ✅ | (none) | (none) |
| **StatsWales** | `uk/wales/statswales.py` ✅ | (none) | ✅ | (none) | (none) |
| **Estyn** (inspections) | `uk/wales/estyn.py` ✅ | (none) | ✅ | (none) | (none) |

### Northern Ireland

| Cycle | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **Foundation Stage** (primary) | ❌ missing | (none) | (planned) | (none) | (none) |
| **KS3-4** (secondary) | `uk/northern_ireland/ccea_curriculum.py`, `education_ni.py` ✅ | (none) | `uk_education_assets.py` (NI assets) ✅ | (none) | (none) |
| **KS5** (post-16) | `uk/northern_ireland/ccea_curriculum.py` ✅ | (none) | ✅ | (none) | (none) |
| **ETI** (inspections) | `uk/northern_ireland/etini.py` ✅ | (none) | ✅ | (none) | (none) |
| **NISRA** (statistics) | `uk/northern_ireland/nisra.py` ✅ | (none) | ✅ | (none) | (none) |

### Crown Dependencies

| Territory | dlt source | BAML extract | Dagster asset | Cognee cognify | CocoIndex embed |
|:--|:--|:--|:--|:--|:--|
| **Guernsey (GGY)** | `crown_dependencies/channel_islands.py` ✅ | (none) | (planned) | (none) | (none) |
| **Jersey (JEY)** | `crown_dependencies/channel_islands.py` ✅ | (none) | (planned) | (none) | (none) |
| **Isle of Man (IOM)** | `crown_dependencies/isle_of_man.py` ✅ | (none) | (planned) | (none) | (none) |

**Cross-cutting coverage gap**: primary and junior cycle BAML schemas exist for Ireland but lack backing dlt sources; **Feature 1 in `oideachais/REFACTORING.md` closes this gap.**

---

## 3. CocoIndex v0 vs v1 status

The venv has `cocoindex==1.0.9` (v1 API). The v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`, `cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`) is removed. Status of the 11 modules in `oideachais/cocoindex_flows/`:

| Flow | API | Status | Action |
|:--|:--|:--|:--|
| `leabharlann_embedding.py` | v1 | ✅ working | — |
| `author_archive_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `curriculum_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `curriculum_translation.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `curriculum_specification_extraction.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `geospatial_indexing.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `learning_outcome_graph.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `ocr_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `pdf_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `research_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |
| `site_analysis_embedding.py` | v0 | ❌ broken on import | Migrate to v1 (deferred) |

**`oideachais/cocoindex_flows/__init__.py` uses a guarded `try/except` import so the package loads despite the broken v0 modules. The v0 modules are not re-exported; only the v1 `leabharlann_embedding` module is.**

The canonical v1 pattern (in `leabharlann_embedding.py`):

- `@coco.fn` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
- `localfs.walk_dir(sourcedir, recursive=True, path_matcher=PatternFilePathMatcher(...), live=True)`
- `lancedb.mount_table_target(LANCE_DB, table_name=..., table_schema=lancedb.TableSchema.from_class(...))`
- `IdGenerator()` + `await id_gen.next_id(chunk.text)` for stable IDs
- `@coco.fn(memo=True)` for the file-level processor
- `query_once` + `query` async helpers for ad-hoc semantic search

Reference: `docs/cocoindex/AGENTS.md` and the 5 canonical examples (`pdf_embedding/`, `code_embedding_lancedb/`, `paper_metadata/`, `multi_format_indexing/`, `live_updates/`).

---

## 4. Dagster asset catalogue

21 asset modules, ~120 assets total, registered in `oideachais/dagster_defs/definitions.py` (loaded into the unified `dg dev` UI via `dg.toml` → `oideachais` code location).

| Group | Module | Compute kind | Notable assets |
|:--|:--|:--|:--|
| `multi_nation_curriculum` | `multi_nation_curriculum_assets.py` | firecrawl/dlt | `ireland_ncca_curriculum`, `england_*`, `scotland_*`, `wales_*`, `northern_ireland_*`, `unified.outcomes` |
| `uk_education` | `uk_education_assets.py` | dlt | `england_dfe_statistics`, `scotland_*_curriculum`, `wales_curriculum_for_wales`, `northern_ireland_ccea_curriculum` |
| `ireland_seed` | `ie/education/curriculum_dlt_assets.py` | dlt | 70+ @dlt_assets for Ireland primary/JC/SC + extraction (multi-partition subject×language) |
| `pdf_processing` | `pdf_assets.py` | python | `ireland_curriculum_pdf_downloads`, `ireland_curriculum_pdf_extracted_text` |
| `exam_materials` | `ie/education/exam_materials_assets.py` | dlt | SEC exam papers, marking schemes, examiner reports |
| `leaving_cert_2026` | `leaving_cert/dlt_assets.py` | dlt | 7 priority subjects × 10 assets = 70 @dlt_assets |
| `research_ingestion` | `research_assets.py` | dlt/python | `research_bunchloch_raw` (BUNCHLOCH path), `research_pdf_extraction` |
| `author_archive_ingestion` | `author_archive_assets.py` | dlt/ocr/baml/embedding | 7 assets for the UoG / Gemini Deep Research / Google Takeout pipeline |
| `leabharlann_ingestion` | `leabharlann_assets.py` | dlt/baml/embedding | 7 assets for the new leabharlann/ tree: books (gaeilge+aigne), zotero, takeout_v1, BAML metadata, 3 CocoIndex updates |
| `celtic_language` | `celtic_language_assets.py` | dlt | Celtic language corpus ingestion |
| `canuint_alignment` | `canuint_alignment_assets.py` | dlt | Canuint Unicode alignment |
| `duchas` | `duchas_assets.py` | dlt | Dúchas folklore |
| `enriched` | `enriched_assets.py` | python | Cross-domain enrichment |
| `geospatial` | `geospatial_assets.py` | python | H3 spatial indexing |
| `htr_training` | `htr_training_assets.py` | python | Irish HTR model training |
| `ocr_comparison` | `ocr_comparison_assets.py` | python | OCR back-end comparison |
| `search` | `search_assets.py` | python | Unified search indexes |
| `knowledge_graph` | `senior_cycle_kg.py` | cognify | `senior_cycle_knowledge_graph`, `lazy_extract_exam_paper` |
| `cross_stage_cognify` | (in `cognee_integration/cross_stage_cognify.py`) | cognify | `cross_stage_cognify` (8 cross-stage edges: Aistear→Primary→JC→SC→Tertiary) |
| `ui_suggestion` | `ui_suggestion.py` | baml | `ui_suggestion_asset` (nightly BAML + Cognee) |
| `unified_audio` | `unified_audio_dataset_assets.py` | dlt | Unified Celtic audio dataset |

Sensors (`oideachais/dagster_defs/sensors/`): `curriculum_freshness`, `domain_sensors`, `author_archive_directory_sensor` (60 s, UoG + Gemini + Takeout), `leabharlann_directory_sensor` (60 s, leabharlann + zotero + stedding/Takeout + ~/Downloads/takeout-*.zip).

---

## 5. Leabharlann pipeline status

`leabharlann/` is the renamed home of the personal archive tree (was `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/`). 6 sub-dirs:

| Sub-dir | Content | Size | dlt source | Dagster asset | CocoIndex App | LanceDB table | BAML extract |
|:--|:--|:--|:--|:--|:--|:--|:--|
| `ollscoil_na_gaillimhe/` | Renamed UoG archive (assignments, placements, lectures) | 2.2 GB | `author_archive/university_of_galway.py` | `author_archive_university_of_galway_raw` | (none — v0 broken) | (none) | `ExtractUoGArtifact` (in `author_archive.baml`) |
| `gemini_deep_research/` | Renamed Gemini archive (7 domains) | 79 MB | `author_archive/gemini_deep_research.py` | `author_archive_gemini_deep_research_raw` | (none — v0 broken) | (none) | `ExtractGeminiReport` (in `author_archive.baml`) |
| `zotero/` | 117 PDFs in real Zotero storage format (arXiv IDs, `__dup0`) | 294 MB | `author_archive/zotero.py` (new) | `leabharlann_zotero_raw` | `LeabharlannZoteroEmbedding` (v1) | `leabharlann_zotero` | `ExtractZoteroMetadata` (defined, **not invoked**) |
| `gaeilge/` | 40 PDFs (Celtic studies) + 37 PNGs in `previews/` | 621 MB | `author_archive/leabharlann_books.py` (new) | `leabharlann_books_raw` | `LeabharlannBooksEmbedding` (v1) | `leabharlann_books` | (none) |
| `aigne/` | 7 psychology books | 28 MB | (same `leabharlann_books.py` with `subject="aigne"`) | `leabharlann_books_raw` | `LeabharlannBooksEmbedding` (v1) | `leabharlann_books` | (none) |
| `stedding/Takeout/` | Sample googletakeout (64 .docx + 1 .csv) | 98 MB | `author_archive/takeout_v1.py` (new) | `leabharlann_takeout_v1_raw` | `LeabharlannTakeoutEmbedding` (v1) | `leabharlann_takeout` | (none) |
| (planned `google_takeout.py`) | OAuth-driven Drive export | (Phase 2) | `author_archive/google_takeout.py` | (TBD) | (TBD) | (TBD) | (TBD) |

OCR pipeline: `oideachais/ocr/author_archive_ocr.py` — Pylaia (Irish HTR) / TrOCR (English) / PaddleOCR (fallback) / VLM (equations) dispatch with graceful degradation. Backs the `author_archive_handwriting_ocr` asset. **Currently underused: only wired to author-archive, not to leabharlann.**

Search handlers (`oideachais/cocoindex_flows/leabharlann_embedding.py`): 3 async helpers, each filtering by domain-specific column:
- `search_leabharlann_books(query, subject=None, limit=10)` — top-10 chunks from `leabharlann_books`.
- `search_leabharlann_zotero(query, htr_relevant=None, irish_relevant=None, arxiv_id=None, limit=10)` — top-10 chunks from `leabharlann_zotero`.
- `search_leabharlann_takeout(query, account=None, domain=None, limit=10)` — top-10 chunks from `leabharlann_takeout`.

---

## 6. Open refactor backlog

See `oideachais/REFACTORING.md` for the 5 queued features in priority order:

1. **Primary + Junior Cycle British Isles dlt + BAML loop** (closes the BAML-without-dlt gap).
2. **Cognee + FalkorDB cross-archive knowledge graph for the leabharlann + primary/secondary archives**.
3. **LanceDB blob storage via the `lancedb` compose stack + RCLONE FUSE mount** (leabharlann PDFs → blob store).
4. **Leabharlann full-document processing pipeline (sample PDFs → BAML → Cognee → FalkorDB → LanceDB blob → Dagster UI)**.
5. **Comprehensive `oideachais/STATUS.md` + per-area READMEs that demystify the stack** — *this is what Phase 1 of the `data-engineering-documentation-and-refactor-roadmap` change is implementing.*

---

## Cross-references

- `oideachais/REFACTORING.md` — refactor backlog with `Status` per item.
- `oideachais/dlt_sources/uk/README.md` — UK per-nation coverage matrix.
- `oideachais/dlt_sources/ireland/README.md` — Ireland coverage matrix.
- `oideachais/cocoindex_flows/README.md` — v0/v1 split per flow.
- `oideachais/dagster_defs/assets/README.md` — Dagster asset catalogue.
- `baml_src/README.md` — BAML schema catalogue.
- `docs/06-infrastructure/leabharlann-stack-overview.md` — end-to-end stack diagram.
- `openspec/changes/data-engineering-documentation-and-refactor-roadmap/` — this change.

## Archived BAML functions

The following 6 BAML files in `baml_src/_archive/` contain 29 functions
that have no current Python consumer. See
`oideachais/baml_src/_archive/README.md` and
`openspec/changes/archive-celtic-baml-orphans/` for re-activation
instructions.

- `cognates.baml` (5 functions) — meaisinfhoghlaim Celtic cognate agent
- `celtic_linguistics.baml` (3 functions) — meaisinfhoghlaim Celtic-linguistic agent
- `morphology.baml` (4 functions) — meaisinfhoghlaim Celtic morphology agent
- `grammar_patterns.baml` (6 functions) — meaisinfhoghlaim Celtic grammar agent
- `named_entities.baml` (5 functions) — meaisinfhoghlaim Celtic NER agent (or wire into duchas_assets.py)
- `portfolio_extraction.baml` (6 functions) — croilar persona profile extraction

The 5 oideachas.baml functions (`ExtractSyllabus`, `ExtractExamPaper`,
`ExtractMarkingScheme`, `BuildCurriculumGraph`,
`ExtractCelticLanguageContent`) are tracked separately by the
`leaving-cert-2026` openspec change.
