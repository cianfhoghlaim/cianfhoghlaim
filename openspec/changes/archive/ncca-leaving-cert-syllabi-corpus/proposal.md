# ncca-leaving-cert-syllabi-corpus — Leaving Certificate Syllabi PDF Corpus

## Why

Cianfhoghlaim's `leaving-cert-2026` change wires the per-subject exam portal for 7 subjects, and `pdf_processing_syllabus` already runs the 6-stage pipeline against NCCA documents in `stedding/ingest_queue/ncca.ie/`. What is missing is a canonical corpus of the **currently-taught Leaving Certificate syllabi for the 8 highest-priority subjects in EN + GA**, landing in the local ingest queue so that any downstream consumer — Croílár teaching portfolios, Túatha in-game NPCs, the oideachais portal, the Leaving Cert agent — can hydrate from the same source of truth.

This corpus is intentionally decoupled from `leaving-cert-2026` because:
1. **Different refresh cadence**: annual (NCCA republication), not exam-year.
2. **Different shape**: a stable cross-subject corpus, not a per-subject exam-portal surface.
3. **Reusability**: the same 23 PDFs feed the leaving-cert portal, the Croílár tutor persona, and the Meaisínfhoghlaim curriculum agent.

## What

A single openspec change that delivers:

1. **A DLT source** at `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculumonline_syllabi.py` that scrapes `curriculumonline.ie/{en|ga-ie}/senior-cycle/senior-cycle-subjects/{slug}/` for the 8 subjects, extracts the syllabus + specification PDF URLs from each page, normalises filenames, and yields a `curriculumonline_syllabi` dlt resource.
2. **An extension to the existing `leaving_cert_syllabus_extraction.baml`** adding the new `ExtractSyllabusStructure(pdf, subject, language) -> SyllabusStructure` function. This new function splits a single combined syllabus PDF into its Higher / Ordinary / Foundation level sections and returns per-level chapter counts, topic counts, page ranges, and learning outcomes. The existing `ExtractLeavingCertSyllabus` is preserved unchanged.
3. **A Dagster asset** `lc_syllabus_download` with `MultiPartitionsDefinition(subject × language)` that runs the DLT source for one (subject, language) pair and writes the PDF bytes to `stedding/ingest_queue/curriculumonline.ie/{subject}/{lang}/{filename}.pdf`. SHA-256 dedup so re-runs are no-ops.
4. **An extension to `pdf_processing_syllabus`** Dagster asset so it also scans the new `curriculumonline.ie/` subtree of `stedding/ingest_queue/`. Existing behaviour for `ncca.ie/` is preserved.
5. **A spec delta** to `oideachais-pipeline` adding 3 new Requirements covering corpus enumeration, syllabus download, and BAML level-section extraction.

## Impact

### Affected specs
- `oideachais-pipeline` — MODIFIED, add 3 Requirements in the leaving-cert section

### Existing assets/services reused
- `pdf_processing_syllabus` Dagster asset — extended scan path
- `stedding/ingest_queue/` — local-first ingest convention
- Subject × language partition pattern — same as `pdf_processing_syllabus`

### Files added
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculumonline_syllabi.py`
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/lc_syllabus_download.py`
- `openspec/changes/ncca-leaving-cert-syllabi-corpus/url-inventory.md` (the verified PDF URL list)
- `stedding/ingest_queue/curriculumonline.ie/.gitkeep`

### Files modified
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing_assets.py` (extend `_get_ingest_queue_path` to scan `curriculumonline.ie/`)
- `cianfhoghlaim/core/baml/_oideachais_src/leaving_cert_syllabus_extraction.baml` (add `ExtractSyllabusStructure` function + 2 new classes)

> **Note on `SUBJECTS_WITH_NCCA`:** we deliberately do **not** extend the `SUBJECTS_WITH_NCCA` list in `subjects/senior_cycle.py` to include `applied-mathematics` and `computer-science`. The NCCA does not have redevelopment pages for these two subjects (verified 2026-06-30), so adding them would cause unnecessary Firecrawl credit spend on 403 responses. The `lc_syllabus_download` asset handles these subjects directly via curriculumonline.ie, bypassing the senior_cycle source entirely.

### Files modified
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/pdf_processing_assets.py` (extend `_get_ingest_queue_path` to scan `curriculumonline.ie/`)
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/subjects/senior_cycle.py` (extend `SUBJECTS_WITH_NCCA`)

### Non-Goals
- No new web scraping tools — reuses Firecrawl via the existing `_crawl_with_firecrawl` helper.
- No Irish-language translations of syllabi that don't exist (Gaeilge is taught in Irish only — no EN version; English GA-equivalent not separately published).
- No HL-vs-OL as separate PDF split — NCCA doesn't publish that way; the BAML function handles logical splitting inside the combined PDF.
- No Cloudflare R2 mirror (deferred to `leaving-cert-2026` Phase 5).
- No Cognee cross-archive edges (separate change).
- No CopilotKit chat agent (separate change).

## Risks
1. **Cloudflare bot challenge on `ncca.ie` and `curriculumonline.ie`** — already hit during this research; Firecrawl proxy handles it. Local cache in `stedding/ingest_queue/` is the mitigation.
2. **Some GA versions may be missing** for Computer Science or English — Phase 0 research confirms only the EN PDF is published for English (the GA-equivalent link points to the same EN file). The asset yields zero rows for these combinations and registers them as `not_available`.
3. **URL stability** — NCCA's `getmedia` GUIDs are stable but the surrounding HTML changes; the DLT source uses link-extraction (not URL templating) so this is resilient.
4. **BAML extraction cost** — running `ExtractSyllabusStructure` over ~17 PDFs ≈ 17 × ~$0.10 = $1.70 one-time.
5. **PDF download size** — each syllabus ≈ 1-3 MB, total ≈ 50 MB.
