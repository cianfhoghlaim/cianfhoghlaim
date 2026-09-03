# Tasks: ncca-leaving-cert-syllabi-corpus

## Phase 0: URL Enumeration (read-only research) — COMPLETED

- [x] Firecrawl-scrape each of the 7 unverified curriculumonline.ie subject pages:
  - `applied-mathematics`, `chemistry`, `geography`, `history` (EN + GA each)
  - `english/ga-ie`, `computer-science` (EN + GA each)
- [x] Record the exact `getmedia` URLs into `openspec/changes/ncca-leaving-cert-syllabi-corpus/url-inventory.md`
- [x] Document any "GA version not available" cases explicitly (English GA equivalent is the EN PDF; Gaeilge has no EN version)

## Phase 1: DLT source

- [ ] Create `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculumonline_syllabi.py`
- [ ] Define `SENIOR_CYCLE_SYLLABI_SUBJECTS = ["mathematics", "applied-mathematics", "chemistry", "geography", "history", "english", "gaeilge", "computer-science"]`
- [ ] Define `curriculumonline_syllabi_source(language: str, subject: str | None = None) -> Iterable`
- [ ] Reuse existing `_crawl_with_firecrawl` helper, no new browser tooling
- [ ] Use `USE_LOCAL_SCRAPES=true` by default; honour the existing 21-second Firecrawl throttle
- [ ] Yield a normalised `curriculumonline_syllabi` dlt resource with `primary_key=["url"]` and columns `{url, subject, language, filename, sha256, page_title, source_page_url, scraped_at}`

## Phase 2: Dagster asset

- [ ] Create `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/lc_syllabus_download.py`
- [ ] Define `MultiPartitionsDefinition(subject=StaticPartitionsDefinition([...]), language=StaticPartitionsDefinition(["en","ga"]))`
- [ ] Drop the `(gaeilge, en)` partition — Gaeilge has no EN syllabus
- [ ] Asset downloads the PDF bytes, computes SHA-256, writes to `stedding/ingest_queue/curriculumonline.ie/{subject}/{lang}/{filename}.pdf`
- [ ] If the file already exists with matching SHA-256, skip the write (idempotent re-runs)
- [ ] MaterializeResult emits `metadata={"url", "filename", "size_bytes", "sha256", "skipped", "http_status"}`

## Phase 3: Extend `pdf_processing_syllabus` to scan curriculumonline.ie too

- [ ] Modify `_get_ingest_queue_path("syllabus")` in `pdf_processing_assets.py` to return a combined iterator over **both** `ncca.ie/` and `curriculumonline.ie/` subtrees
- [ ] Add a `source_domain` column to the inferred metadata (so downstream can distinguish provenance)
- [ ] Preserve existing skip-on-empty behaviour

## Phase 4: BAML extraction (extends existing file)

- [x] Extend `cianfhoghlaim/core/baml/_oideachais_src/leaving_cert_syllabus_extraction.baml`
- [x] Add `class SyllabusLevel { level: "Foundation" | "Ordinary" | "Higher", chapter_count: int, topic_count: int, page_range: str, learning_outcomes: list[str] }`
- [x] Add `class SyllabusStructure { title: str, subject: str, language: str, level_sections: list[SyllabusLevel], subject_overview: str, assessment_overview: str }`
- [x] Add `@function ExtractSyllabusStructure(pdf_text: string, subject: string, language: string) -> SyllabusStructure` using the existing `ExtractEnStrong` client
- [ ] Run `baml-cli generate` to rebuild the client
- [ ] Add 5 unit tests covering: Maths (3 levels), English (2 levels), Gaeilge (3 levels), Geography (2 levels), single-language fallback

## Phase 5: Spec delta + openspec validation

- [x] Add 3 Requirements to the change's spec delta at `openspec/changes/ncca-leaving-cert-syllabi-corpus/specs/oideachais-pipeline/spec.md`
- [x] Each Requirement SHALL/MUST language; each has ≥1 Scenario block (WHEN/THEN/AND)
- [ ] Run `bun run spec:validate ncca-leaving-cert-syllabi-corpus --strict`
- [ ] Run `bun run lint:skills` to ensure no skill regressions

## Phase 6: Dagster auto-discovery + smoke test

- [ ] Register the new asset in the existing `_oideachais_dagster_defs` mount point (`defs.yaml`)
- [ ] Manually materialise the `(mathematics, en)` partition as a smoke test
- [ ] Confirm the file appears at `stedding/ingest_queue/curriculumonline.ie/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf`
- [ ] Confirm the daily `pdf_processing_syllabus` Dagster asset picks it up
- [ ] Run a manual BAML extraction on the resulting PDF and verify the level-sections structure

## Phase 7: Documentation

- [ ] Update `openspec/AGENTS.md` if a new capability spec is added (not required if it's a delta to `oideachais-pipeline`)
- [ ] Add 1-paragraph note to `cianfhoghlaim/README.md` under "Ingest queue layout" mentioning `curriculumonline.ie/`
- [ ] Update `docs/openspec/changelog.md` with the new change
