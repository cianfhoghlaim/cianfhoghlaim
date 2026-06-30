# `sruth/oideachais/dagster_defs/assets/` — Dagster Asset Catalogue

**Last updated:** 2026-06-16

21 asset modules, ~120 assets, registered in `sruth/oideachais/dagster_defs/definitions.py` (loaded into the unified `dg dev` UI via `dg.toml` → `oideachais` code location).

## Asset groups

### `multi_nation_curriculum`

`multi_nation_curriculum_assets.py`. 4-nation × 4-cycle cross-pipeline (Ireland, England, Scotland, Wales, NI). Compute kinds: `firecrawl`, `dlt`.

| Asset | Deps | Notes |
|:--|:--|:--|
| `ireland_ncca_curriculum` | none | Crawls NCCA + curriculumonline.ie (en + ga) |
| `england_*_curriculum` | none | National Curriculum + DfE + Ofsted |
| `scotland_*_curriculum` | none | CfE + SQA + SIMD + Insight |
| `wales_*_curriculum` | none | CfW + StatsWales + Estyn |
| `northern_ireland_*_curriculum` | none | CCEA + Education NI + ETI + NISRA |
| `unified.outcomes` | all nation assets | Cross-nation outcome alignment |

### `uk_education`

`uk_education_assets.py`. UK + Crown Dependencies education pipelines. Compute kinds: `dlt`.

Per-nation assets for `england_dfe_statistics`, `scotland_*_curriculum`, `wales_curriculum_for_wales`, `northern_ireland_ccea_curriculum`, etc.

### `ireland_seed` (and `ireland/{curriculum,exam_materials,sec}`)

`ie/education/curriculum_dlt_assets.py`, `ie/education/exam_materials_assets.py`. 70+ `@dlt_assets` for Ireland primary/JC/SC + SEC exam materials. `MultiPartitionsDefinition(subject, language)`.

### `pdf_processing`

`pdf_assets.py`. PDF download + extraction pipeline. Compute kind: `python`.

| Asset | Deps | Notes |
|:--|:--|:--|
| `ireland_curriculum_pdf_downloads` | none | Downloads NCCA + SEC PDFs to `stedding/ingest_queue/` |
| `ireland_curriculum_pdf_extracted_text` | `pdf_downloads` | pymupdf + Marker + Docling extraction |

### `lc_syllabus`

`lc_syllabus_download.py`. The currently-taught Leaving Certificate syllabi corpus (8 subjects × 2 languages). Per the `ncca-leaving-cert-syllabi-corpus` openspec change (2026-06-30). The `pdf_processing` asset above scans both `stedding/ingest_queue/ncca.ie/` and `stedding/ingest_queue/curriculumonline.ie/` so this asset is the producer of the latter.

| Asset | Deps | Notes |
|:--|:--|:--|
| `lc_syllabus_download` | none | `MultiPartitionsDefinition(subject × language)`. Downloads ~17 syllabi + specifications + guidelines PDFs from `curriculumonline.ie/getmedia/...` to `stedding/ingest_queue/curriculumonline.ie/`. SHA-256 dedup, idempotent. |

### `leaving_cert_2026`

`leaving_cert/dlt_assets.py`. 7 priority subjects × 10 assets = 70 @dlt_assets for Leaving Cert 2026. Each subject has syllabus, past_papers, marking_schemes, examiner_reports tables in DuckLake.

### `research_ingestion`

`research_assets.py`. Bunchloch research archive (CT511, GA101, Mata, Oideachas) ingestion. Compute kinds: `dlt`, `python`.

| Asset | Deps | Notes |
|:--|:--|:--|
| `research_bunchloch_raw` | none | `@dlt.source bunchloch_source()` |
| `research_bunchloch_by_subject` | `bunchloch_raw` | Subject-partitioned re-runs |
| `research_pdf_extraction` | `bunchloch_raw` | pymupdf + Marker + Docling + DeepSeek-OCR |

### `author_archive_ingestion`

`author_archive_assets.py`. 7 assets for the UoG / Gemini Deep Research / Google Takeout pipeline. Compute kinds: `dlt`, `ocr`, `baml`, `embedding`. (Currently mostly stubs; the v0 `author_archive_embedding.py` flow is broken — see `sruth/oideachais/REFACTORING.md` #6.)

### `leabharlann_ingestion`

`leabharlann_assets.py`. 7 assets for the new `leabharlann/` tree: books (`gaeilge`+`aigne`), zotero, takeout_v1, BAML metadata, 3 CocoIndex updates. Compute kinds: `dlt`, `baml`, `embedding`.

| Asset | Deps | Partition |
|:--|:--|:--|
| `leabharlann_books_raw` | none | `leabharlann_books_subjects` (DynamicPartitions) |
| `leabharlann_zotero_raw` | none | `leabharlann_zotero_batches` (StaticPartitions × 5) |
| `leabharlann_takeout_v1_raw` | none | `leabharlann_takeout_accounts` (DynamicPartitions) |
| `leabharlann_paper_metadata` | `leabharlann_zotero_raw` | none |
| `leabharlann_cocoindex_books_update` | `leabharlann_books_raw`, `leabharlann_paper_metadata` | none |
| `leabharlann_cocoindex_zotero_update` | `leabharlann_zotero_raw`, `leabharlann_paper_metadata` | none |
| `leabharlann_cocoindex_takeout_update` | `leabharlann_takeout_v1_raw` | none |

The 3 CocoIndex-update assets invoke `subprocess.run(["cocoindex", "update", "oideachais.cocoindex_flows.leabharlann_embedding:..."])`. See `sruth/oideachais/REFACTORING.md` #16, #17, #18, #20 for known issues with this approach.

### `celtic_language`

`celtic_language_assets.py`. Celtic language corpus ingestion (Irish, Scottish Gaelic, Welsh, Manx, Cornish, Breton).

### `canuint_alignment`

`canuint_alignment_assets.py`. Canuint Unicode alignment.

### `duchas`

`duchas_assets.py`. Dúchas folklore corpus (school collections, 1937-1939).

### `enriched`

`enriched_assets.py`. Cross-domain enrichment (no partitions).

### `geospatial`

`geospatial_assets.py`. H3 spatial indexing pipeline.

### `htr_training`

`htr_training_assets.py`. Irish HTR model training (Pylaia, VLM fine-tuning).

### `ocr_comparison`

`ocr_comparison_assets.py`. OCR back-end comparison (PaddleOCR, Docling, Unstract, Dots.OCR).

### `search`

`search_assets.py`. Unified search indexes (cross-table).

### `knowledge_graph`

`senior_cycle_kg.py`. Senior Cycle knowledge graph (exam papers + marking schemes).

| Asset | Notes |
|:--|:--|
| `senior_cycle_knowledge_graph` | Senior Cycle knowledge graph |
| `lazy_extract_exam_paper` | On-demand exam paper BAML extraction |

### `cross_stage_cognify`

(Declared in `cognee_integration/cross_stage_cognify.py`, not in `assets/`.) `cross_stage_cognify` asset. 8 cross-stage edges: Aistear → Primary → JC → SC → Tertiary.

### `ui_suggestion`

`ui_suggestion.py`. Nightly UI component suggestions (BAML + Cognee). 1 asset + 1 schedule.

### `unified_audio`

`unified_audio_dataset_assets.py`. Unified Celtic audio dataset (ASR + TTS training data).

## Sensors

`sruth/oideachais/dagster_defs/sensors/`:

- `curriculum_freshness` — Unified curriculum freshness sensor.
- `domain_sensors` — Curriculum sitemap, exam papers (legacy).
- `author_archive_directory_sensor` — 60 s poll of the UoG / Gemini / Takeout trees.
- `leabharlann_directory_sensor` — 60 s poll of the leabharlann + zotero + stedding/Takeout + `~/Downloads/takeout-*.zip`.

## How assets are registered

`sruth/oideachais/dagster_defs/definitions.py` imports each asset module's list and concatenates them into `combined_assets`. The unified `dg dev` UI shows them all under the `oideachais` code location.

```python
# sruth/oideachais/dagster_defs/definitions.py
from .assets.leabharlann_assets import LEABHARLANN_ASSETS
from .assets.author_archive_assets import AUTHOR_ARCHIVE_ASSETS
# ...

combined_assets = [
    *all_assets,
    *curriculum_dlt_assets,
    *LEABHARLANN_ASSETS,
    *AUTHOR_ARCHIVE_ASSETS,
    *LEAVING_CERT_ASSETS,
    # ...
]

defs = dg.Definitions(
    assets=combined_assets,
    asset_checks=all_asset_checks,
    jobs=all_jobs,
    sensors=all_sensors,
    schedules=all_schedules,
    resources=all_resources,
)
```

## Related

- `sruth/oideachais/STATUS.md` § 4 — asset catalogue.
- `sruth/oideachais/dagster_defs/definitions.py` — the canonical asset registry.
