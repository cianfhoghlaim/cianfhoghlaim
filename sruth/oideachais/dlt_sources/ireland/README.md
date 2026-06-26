# `oideachais/dlt_sources/ireland/` — Ireland DLT Sources

**Last updated:** 2026-06-16

DLT sources for the Republic of Ireland education system. 18 dlt source files covering Aistear (early childhood) through Tertiary (CAO / QQI-FET / Apprenticeship).

## Coverage matrix

Status: ✅ working · ⚠️ partial · 🟡 planned · ❌ missing

| Cycle | dlt source | BAML extract | Dagster asset | Cognee | CocoIndex |
|:--|:--|:--|:--|:--|:--|
| **Aistear** (early childhood) | `ireland/aistear.py` ✅ | `ExtractAistearFramework` 🟡 (in `baml_src/aistear.baml`, **not invoked from any dlt source**) | (planned via `cross_stage_cognify.py`) | `cross_stage_cognify` ✅ | (none) |
| **Primary** | ❌ **MISSING** — `dlt_sources/ireland/primary.py` does not exist | `ExtractPrimaryFramework`, `ExtractPrimaryLearningOutcomes` ✅ defined in `baml_src/primary.baml` | ❌ | (none) | (none) |
| **Junior Cycle** | ❌ **MISSING** — `dlt_sources/ireland/junior_cycle.py` does not exist | `ExtractJCSpec`, `ExtractCBADescriptor` ✅ defined in `baml_src/junior_cycle.baml` | ❌ | (none) | (none) |
| **Senior Cycle** | `ireland/senior_cycle.py`, `leaving_cert.py` ✅ | (BAML via `curriculum_extraction.baml` ✅) | `ie/education/curriculum_dlt_assets.py` ✅, `leaving_cert/dlt_assets.py` (70+ @dlt_assets) ✅ | `cross_stage_cognify` ✅ | `curriculum_embedding.py` (v0 — broken on cocoindex==1.0.9) |
| **Tertiary** (CAO / QQI-FET / Apprenticeship) | `ireland/tertiary.py` ✅ | 10 classes + (TBD functions) in `baml_src/tertiary.baml` | (planned) | (planned) | (none) |
| **NCCA core curriculum** | `ireland/ncca.py`, `curriculum_source.py` ✅ | `ExtractCurriculumFromDocument` ✅ (in `baml_src/curriculum_extraction.baml`) | `ie/education/curriculum_dlt_assets.py` ✅ | ✅ | `curriculum_embedding.py` (v0 — broken) |
| **SEC examinations** | `ireland/examinations.py` ✅ | (TBD) | `ie/education/exam_materials_assets.py` ✅ | ✅ | (none) |
| **EdcoLearning** (LC audio) | `ireland/edcolearning.py` 🟡 (import-guard) | (TBD) | (planned) | (none) | (none) |
| **OIDE CPD** | `ireland/oide.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Parallel corpus** (EN/GA) | `ireland/parallel_corpus.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **PDF downloads** (NCCA / SEC PDFs to local cache) | `ireland/pdf_downloader.py` ✅ | (none — pure download) | (none) | (none) | (none) |
| **Local documents** (UoG archive) | `ireland/local_documents.py` ✅ | (none — the dlt_sources/leabharlann/university_of_galway.py is the canonical source) | (none) | (none) | (none) |
| **SEC aural transcripts** | `ireland/sec_aural_transcripts.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Subjects** (LC subject inventory) | `subjects/{base,junior_cycle,senior_cycle}.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Curriculum registry** (registry of all sources) | `ireland/curriculum_registry.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **JSON seed** (manual corpus) | `ireland/json_seed.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Content deduplication** | `ireland/content_deduplication.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Agentic discovery** (LLM-driven source discovery) | `ireland/agentic_discovery.py` ✅ | (TBD) | (planned) | (none) | (none) |
| **Source adapters** (canonical adapter interface) | `ireland/source_adapters.py` ✅ | (TBD) | (planned) | (none) | (none) |

## Critical gap: Primary + Junior Cycle BAML-without-dlt

The BAML schemas in `baml_src/primary.baml` and `baml_src/junior_cycle.baml` define rich, type-safe extraction for the Irish primary curriculum and the Junior Cycle curriculum. **No dlt source backs them.** The extraction is unreachable.

This is the single biggest "BAML defined but not invoked" gap in the platform. **It is the top of the `oideachais/REFACTORING.md` backlog (Feature 1) and will be closed by the queued openspec change `primary-secondary-british-isles-dlt-baml`.**

## How dlt sources are registered

`oideachais/dlt_sources/ireland/__init__.py` re-exports the canonical `@dlt.source` factories. `oideachais/dlt_sources/__init__.py` does NOT re-export them directly — the canonical pattern is `from oideachais.dlt_sources.ireland import ncca_source` (or similar).

## How Dagster assets are registered

- `oideachais/dagster_defs/assets/ie/education/curriculum_dlt_assets.py` — 4 cycle assets (early_childhood, primary, junior_cycle, senior_cycle) with `MultiPartitionsDefinition(subject, language)`.
- `oideachais/dagster_defs/assets/ie/education/exam_materials_assets.py` — SEC exam materials.
- `oideachais/dagster_defs/assets/leaving_cert/dlt_assets.py` — 70+ @dlt_assets for the 7 Leaving Cert 2026 priority subjects.
- `oideachais/dagster_defs/assets/ireland/` — older Ireland-specific assets.
- `oideachais/dagster_defs/assets/uk_education_assets.py` — UK + NI + Crown Dependencies assets.
- `oideachais/dagster_defs/assets/multi_nation_curriculum_assets.py` — cross-nation pipeline.

## Source URLs (canonical, used by the dlt sources)

- **NCCA**: curriculumonline.ie, ncca.ie
- **SEC**: examinations.ie
- **OIDE**: oide.ie
- **gov.ie**: gov.ie/en/department-of-education
- **CAO**: cao.ie
- **QQI**: qqi.ie
- **HET (Higher Education Authority)hea.ie

## Related

- `oideachais/dlt_sources/uk/README.md` — UK + Crown Dependencies coverage matrix.
- `oideachais/STATUS.md` § 2 — per-nation × per-cycle coverage matrix.
- `baml_src/README.md` — BAML schema catalogue.
