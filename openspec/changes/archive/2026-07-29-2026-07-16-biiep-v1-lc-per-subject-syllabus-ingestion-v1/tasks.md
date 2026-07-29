# Tasks — 2026-07-16-biiep-v1-lc-per-subject-syllabus-ingestion-v1

## 1. Audit (DONE)

- [x] 1.1 Audit existing per-subject qpack BAML infrastructure (`qpack_<subject>.baml` × 6)
- [x] 1.2 Audit existing canonical `ncca.py` (the BIEP v1 multi-partition NCCA crawl — already shipped)
- [x] 1.3 Audit `CelticIngestionComponent` (the Dagster defs YAML contract — already shipped)
- [x] 1.4 Audit existing per-subject defs YAMLs (`lc5/english.yaml` pattern)
- [x] 1.5 Audit existing `baml/education/lc_extraction/curriculum_syllabus.baml` (the canonical SyllabusDocument + ExtractCurriculumSyllabus)

## 2. Named destinations factory (DONE)

- [x] 2.1 `dlt/common/named_destinations.py` — the canonical named destination registry (warehouse / lakehouse / local_duckb)

## 3. 6 per-subject NCCA crawl DLT sources (DONE)

- [x] 3.1 `dlt/british_isles/ireland/education/ncca_mathematics.py`
  - `@dlt.resource(name="mathematics_syllabus", write_disposition="merge", primary_key=["url"])`
  - `named_destination("warehouse")`
  - `USE_LOCAL_SCRAPES=true` reads from `stedding/ingest_queue/ncca/mathematics/`
  - `default` BAML client (minimax-m3)
- [x] 3.2 `ncca_chemistry.py` — same pattern, `chemistry` subject
- [x] 3.3 `ncca_geography.py` — same pattern, `geography` subject
- [x] 3.4 `ncca_gaeilge.py` — same pattern, `gaeilge` subject, default `ga`
- [x] 3.5 `ncca_english.py` — same pattern, `english` subject
- [x] 3.6 `ncca_computer_science.py` — same pattern, `computer_science` subject

## 4. 6 qpack BAMLs (EXISTING — verified)

- [x] 4.1 `qpack_mathematics.baml` — verified; has `Math*` prefix per `49e0259a0`
- [x] 4.2 `qpack_chemistry.baml` — verified; has `Chem*` prefix
- [x] 4.3 `qpack_geography.baml` — verified; has `Geog*` prefix
- [x] 4.4 `qpack_gaeilge.baml` — verified; has `Gael*` prefix
- [x] 4.5 `qpack_english.baml` — verified; has `Engl*` prefix
- [x] 4.6 `qpack_computer_science.baml` — verified; has `Comp*` prefix

## 5. 1 unified BAML extractor (DONE)

- [x] 5.1 `baml/education/unified_extraction.baml` — the unified extractor
  - `enum LC6Subject` (6 subjects)
  - `enum LC6Language` (en + ga)
  - `class LCSyllabus` — the unified return type with `subject` discriminator
  - `function ExtractLC6Syllabus(subject, text, language) -> LCSyllabus` (the dispatcher)
  - 6 per-subject thin wrappers (`ExtractMathSyllabus`, `ExtractChemSyllabus`, etc.)
  - Routes to `client Default` (minimax-m3 per `667635dfd`)

## 6. 6 per-subject L1 defs YAMLs (DONE)

- [x] 6.1 `orchestration/defs/1_ingestion/curriculum/lc6/mathematics.yaml`
- [x] 6.2 `orchestration/defs/1_ingestion/curriculum/lc6/chemistry.yaml`
- [x] 6.3 `orchestration/defs/1_ingestion/curriculum/lc6/geography.yaml`
- [x] 6.4 `orchestration/defs/1_ingestion/curriculum/lc6/gaeilge.yaml` (default `ga`)
- [x] 6.5 `orchestration/defs/1_ingestion/curriculum/lc6/english.yaml`
- [x] 6.6 `orchestration/defs/1_ingestion/curriculum/lc6/computer_science.yaml`

  Each is a `CelticIngestionComponent` with:
  - `source_id: filesystem.leaving_cert.<subject>`
  - `automation_cron: "0 4 * * *"` (daily 04:00 UTC)
  - `state_backed: true`, `state_refresh_interval: monthly`
  - partitions: subject × language (2 partitions per subject)

## 7. Openspec change (DONE)

- [x] 7.1 `proposal.md` — explain the 6-subject scope + the 6 DLT sources + 6 qpack BAMLs + unified BAML extractor + 6 defs YAMLs
- [x] 7.2 `tasks.md` — this file
- [x] 7.3 `specs/british-isles-education-pipeline/spec.md` — 1 ADDED Requirement
- [x] 7.4 `openspec validate ... --strict` passes

## 8. Commit + push (DONE)

- [x] 8.1 Commit all 13 new files (6 DLT sources + 6 defs YAMLs + 1 unified BAML + 1 named_destinations + 3 openspec files)
- [x] 8.2 Push to `origin/pick-4-biep-v1` (NOT `main`)