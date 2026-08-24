# 2026-08-24-wave-2-orchestration-vertical-pipelines-v1

## Why

The 2026-08-24 master refactor plan identified Wave 2 as the **vertical
pipeline reorganisation** for the Dagster orchestration layer. Three
structural problems motivate this change:

1. **The 5-layer horizontal model (`1_ingestion/`, `2_materials/`,
   `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/`) no
   longer matches the actual processing needs.** Wave 1 migrated
   `dlt_sources/` into a **domain-first namespace** (`dlt_sources/law/`,
   `dlt_sources/medicine/`, `dlt_sources/education/tertiary/`, etc.), so
   the horizontal layer boundaries don't correspond to anything in the
   data plane. A chemistry-syllabus pipeline has different processing
   steps than a comic-book pipeline; treating them as identical
   "L1 ingestion" is meaningless.

2. **The post-2026-08-23 UoG flat files (`uog_exam`,
   `uog_official_docs`, `uog_personal_archive`,
   `uog_personal_archive_figures`, `uog_students_union`, `nui_federation`,
   `british_isles_tertiary`, `media_intel`) bypass the Component
   architecture entirely.** They were added as `defs/<file>.py` modules
   rather than per-pipeline directories, so they appear in the Dagster
   asset graph but don't follow the CelticIngestionComponent +
   CelticMaterialsComponent + CelticModelLifecycleComponent pattern.
   Wave 2 fixes this regression.

3. **Each pipeline needs its own per-source-kind processing logic.**
   A chemistry syllabus (NCCA documents → BAML extraction → CocoIndex
   embeddings → marimo dashboard) is fundamentally different from a
   comic book (image fetch → VLM via cognee → asset generation). The
   new `pipeline_kind_handlers/` namespace lets each pipeline declare
   which processing strategy applies (syllabus, exam_papers,
   personal_archive, official_docs, comics, crypto, pdf, media).

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Dagster pipeline derivation | BOTH (a) dlt source decorator metadata introspection AND (c) `pipeline.dataset()` schema introspection — per the master plan |
| Pipeline organisation | **Vertical domain pipelines** mirroring `dlt_sources/` (not horizontal layers) |
| UoG tertiary pipelines | `pipelines/education/tertiary/uog/{exam_papers, personal_archive, official_docs, students_union}/` — proper Components |
| Firecrawl integration | **Use firecrawl mcp** to fetch latest Dagster docs and best practices |
| UoG is the FIRST tertiary example | NUI federation, British Isles tertiary, etc. follow the same pattern in subsequent PRs |

## Dependencies

`Blocked by: 2026-08-24-wave-0-cocoindex-module-path-repair-v1` (✅ landed), `2026-08-24-wave-1-dlt-sources-domain-restructure-v1` (✅ landed)
`Unblocks: 2026-08-24-wave-3-cocoindex-v0-stragglers-v1, 2026-08-24-wave-4-ducklake-v1-hardening-v1, 2026-08-24-wave-5-web-consolidation-v1`
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. New `pipeline_factory.py` Component

**File**: `orchestration/components/pipeline_factory.py` (NEW)

The `PipelineFactoryComponent` is a single Dagster Component that auto-derives
a complete 5-stage asset graph from a single dlt source reference:

```yaml
# orchestration/pipelines/education/tertiary/uog/exam_papers/defs.yaml
type: orchestration.components.pipeline_factory.PipelineFactoryComponent
attributes:
  dlt_source: dlt_sources.education.tertiary.uog.exam_papers
  pipeline_kind: exam_papers
  embedding_model: BAAI/bge-large-en-v1.5
  destinations: [ducklake_cianfhoghlaim]
  processing:
    - baml_extraction
    - cocoindex_live_update
    - marimo_dashboard
  schedules:
    - cron: "0 3 * * *"
      timezone: UTC
  sensors:
    - upstream_change
```

The factory uses **BOTH (a) and (c)**:
- (a) **Decorator metadata introspection**: scan `@dlt.source` /
  `@dlt.resource` for `name`, `primary_key`, `write_disposition`,
  `columns`, `schema_contract`
- (c) **`pipeline.dataset()` schema introspection**: after a dry-run,
  read the actual column types, NULL constraints, row counts

It then auto-generates: dlt asset, BAML extraction asset, cocoindex flow
asset, marimo dashboard asset, asset checks. Per the user's choice.

### 2. New `pipeline_kind_handlers/` namespace

**Directory**: `orchestration/components/pipeline_kind_handlers/` (NEW)

Eight handler classes, one per source-kind:

| Handler | Use case |
|:--|:--|
| `syllabus_handler.py` | NCCA / SEC / CCEA / SQA / WJEC syllabuses (chemistry_syllabus → experiments → artifacts) |
| `exam_papers_handler.py` | UoG exam papers + Leaving Cert + GCSE (VLM extraction) |
| `personal_archive_handler.py` | Personal notes + assignments + transcripts |
| `official_docs_handler.py` | University module pages + student union + official sites |
| `comics_handler.py` | Comics (VLM via cognee) |
| `crypto_handler.py` | Chain indexer for crypteolas sources |
| `pdf_handler.py` | OCR + BAML extraction |
| `media_handler.py` | Codec probe + thumbnail + embeddings |

Each handler implements a `process_pipeline(defs, ctx)` method that the
`PipelineFactoryComponent` calls to specialise the generated asset graph.

### 3. New `orchestration/pipelines/` namespace

**Directory**: `orchestration/pipelines/` (NEW — vertical domain pipelines)

Mirrors the Wave 1 `dlt_sources/` domain-first layout:

```
orchestration/pipelines/
├── law/                          # mirrors dlt_sources/law/
│   ├── ireland/
│   │   ├── defs.yaml             # CelticIngestionComponent + MaterialsComponent + ModelLifecycleComponent
│   │   └── ...
│   ├── england/
│   ├── nigeria/
│   └── european_nations/<country>/
├── medicine/
│   ├── ireland/
│   ├── nigeria/
│   └── ...
├── education/                    # secondary (K-12 / Leaving Cert / GCSE)
│   ├── ireland/
│   ├── england/{aqa,edexcel,ocr}/
│   ├── nigeria/
│   ├── canada/
│   ├── united_states/
│   └── tertiary/                 # NEW: 3rd-level / university
│       ├── uog/                  # 1st example: University of Galway
│       │   ├── exam_papers/
│       │   │   └── defs.yaml     # PipelineFactoryComponent
│       │   ├── personal_archive/
│       │   ├── official_docs/
│       │   └── students_union/
│       ├── nui_federation/
│       └── british_isles/
├── lexicographic/
├── cultural_heritage/
├── local_archive/
├── media_text/
├── media_comics/
├── media_games/
├── media_personal/
├── crypteolas_chain/
├── crypteolas_docs/
├── crypteolas_defi/
├── raw_files/
├── cv/
├── artwork/
├── labels/
└── ...
```

### 4. UoG flat-file conversion

The 8 post-2026-08-23 UoG flat files at `orchestration/defs/{uog_exam,uog_official_docs,uog_personal_archive,uog_personal_archive_figures,uog_students_union,nui_federation,british_isles_tertiary,media_intel}.py`
SHALL be converted into proper Components under
`orchestration/pipelines/education/tertiary/{uog,nui_federation,british_isles}/<subdir>/defs.yaml`.

### 5. `definitions.py` update

`orchestration/definitions.py` SHALL be updated to also walk
`orchestration/pipelines/` (in addition to `orchestration/defs/`) so
the new vertical pipelines are auto-loaded.

### 6. Firecrawl-driven docs lookup

The `PipelineFactoryComponent` SHALL include a firecrawl mcp call to
fetch the latest Dagster 1.13+ Components docs at scaffold time,
ensuring the generated YAML uses the current `dg scaffold defs`
patterns.

## Out of scope

- Web apps consolidation (Wave 5)
- Frontend modernisation (Wave 6)
- DuckLake v1.0 hardening (Wave 4)
- CocoIndex v0→v1 API migration (Wave 3 — addresses the 18 remaining
  v0 files)
- Migrating every existing `defs/1_ingestion/` /
  `defs/2_materials/` / `defs/3_model_lifecycle/` file into the new
  vertical layout. **The first PR of Wave 2 only converts the UoG flat
  files + establishes the framework.** Subsequent PRs convert the rest.

## Verification

After Wave 2 lands:

1. `dg list components` lists the new `PipelineFactoryComponent`
2. `dg list defs` includes the new UoG pipelines under
   `pipelines/education/tertiary/uog/{exam_papers,personal_archive,official_docs,students_union}/`
3. `mise run sync:dagster` passes (no `cocoindex_v1_module_import_failed`)
4. `uv run python -c "from orchestration.components.pipeline_factory import PipelineFactoryComponent"` succeeds
5. `uv run python -c "from orchestration.components.pipeline_kind_handlers.exam_papers_handler import ExamPapersHandler"` succeeds

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0: `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/` (✅ landed commit `f0344b787`)
- Wave 1: `openspec/changes/2026-08-24-wave-1-dlt-sources-domain-restructure-v1/` (✅ landed commit `adeecc126`)
- Existing Components: `orchestration/components/layer{1..5}_*.py`
