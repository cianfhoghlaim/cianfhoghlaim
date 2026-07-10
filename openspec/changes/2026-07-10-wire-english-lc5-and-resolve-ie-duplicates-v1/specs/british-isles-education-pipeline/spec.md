# `british-isles-education-pipeline` MODIFIED — Wire English into lc5 + duplicate-removal declaration

## ADDED Requirements

### Requirement: All 6 LC subjects have working filesystem DLT source

The system SHALL ingest every PDF (and JPG for the scanned geography exam
page) in `cianfhoghlaim/leaving_certificate/{chemistry,computer_science,english,gaeilge,geography,mathematics}/`
through a single filesystem DLT resource
(`cianfhoghlaim.dlt.filesystem.leaving_cert_source.lc5_documents` with
`LC6_SUBJECTS = ("chemistry", "computer_science", "english", "gaeilge",
"geography", "mathematics")`). English is en-only at the root of its
subject directory (mirrors the gaeilge asymmetry but with `language = "en"`).
The `LC_PDF_KIND_REGISTRY` SHALL contain explicit regex patterns for both
the English exam-paper kind (`LC002ALP\d{3}[EI]V\.pdf`) and the English
spec-constitution kind (`SC-English-Spec-ENG-INT.*\.pdf`).

#### Scenario: English contributes 8 PDFs to the filesystem resource

- **GIVEN** the 8 PDFs in `cianfhoghlaim/leaving_certificate/english/`
      (`LC002ALP100EV.pdf`, `LC002ALP200EV.pdf`, `LC002GLP100EV.pdf`,
      `LC002GLP200EV.pdf`, `SCSEC14_English_Syllabus.pdf`,
      `SCSEC14_English_Syllabus_2026-06-30.pdf`,
      `SC-English-Spec-ENG-INT.pdf`,
      `SC-English-Spec-ENG-INT_2026-06-30.pdf`)
- **WHEN** `from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents; rows = list(lc5_documents())` runs
- **THEN** exactly 8 rows have `subject == "english"` and `language == "en"`
- **AND** the 4 exam papers route through `model_key = "qwen3-vl-8b"`
- **AND** the 4 syllabi / spec constitutions route through `model_key = "gemma-4-26B-A4B"`
- **AND** the total row count is ≥ 80 (the 6 subjects × 2 languages

  minus the english ga-only and gaeilge en-only subjects)

#### Scenario: 36 lc5-group Dagster assets register per subject × asset group

- **GIVEN** `LC6_SUBJECTS` has 6 elements
- **WHEN** the `_make_subject_extraction_asset` factory loop + the 6
      explicit ingestion + 6 explicit cognify `@asset` decorators execute
- **THEN** exactly 36 assets register under the `lc5` group_name subtree
      (6 subjects × 6 asset groups: 1 ingestion + 4 BAML extraction +
      1 cognify)
- **AND** the English asset set is `{lc5_english_ingested,
  lc5_english_syllabus_extracted, lc5_english_papers_extracted,
  lc5_english_marking_extracted, lc5_english_diagrams_extracted,
  lc5_english_cognified}` (6 assets, one per asset group)

#### Scenario: lc6 cross-subject Graphiti fan-out reports 6 subjects

- **WHEN** `lc5_cross_subject_graphiti_stream` materialises
- **THEN** its return payload reports `subjects = len(LC6_SUBJECTS) = 6`
- **AND** the Graphiti episode stream merges all 6 subjects into the
      FalkorDB cross-subject graph (nodes: Subject, Topic,
      LearningOutcome, Question, Year, ModuleKind;
      edges: HAS_TOPIC, ASSESSED_BY, EVOLVED_TO, EN_CORRESPONDS_TO_GA)

### Requirement: No duplicate DLT source files (curriculum_source.py deleted)

The canonical Irish curriculum DLT source SHALL live exclusively at
`cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py`.
The legacy 972-LOC byte-identical duplicate
`cianfhoghlaim/dlt/british_isles/ireland/education/curriculum_source.py`
and the 0-byte stub `exam_source_update.py` SHALL NOT exist. All 11
importers (5 in `dlt/british_isles/ireland/law/` + 5 in
`dlt/british_isles/ireland/education/law/` + the canonical
`curriculum.py`'s own docstring + the `test_curriculum_source_local_cache.py`
test) SHALL import `_crawl_source` from `...education.curriculum` (not
`...education.curriculum_source`).

#### Scenario: The duplicate pair is gone

- **WHEN** a developer runs `ls cianfhoghlaim/dlt/british_isles/ireland/education/ | grep -E "curriculum_source|exam_source_update"`
- **THEN** zero matches SHALL be returned
- **AND** `curriculum.py` (972 LOC) remains the sole canonical surface

#### Scenario: The 11 importers resolve against the kept file

- **GIVEN** `curriculum.py` defines `_crawl_source` at line 57
      (verified via `grep -n "^def _crawl_source" cianfhoghlaim/dlt/british_isles/ireland/education/curriculum.py`)
- **WHEN** any of the 11 importer modules is loaded
- **THEN** the import `from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum import _crawl_source` SHALL succeed
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.curriculum_source" cianfhoghlaim/`
- **AND** zero matches SHALL be returned by
      `grep -rn "from cianfhoghlaim.dlt.british_isles.ireland.education.exam_source_update" cianfhoghlaim/`

## MODIFIED Requirements

*(no prior requirements are modified — the existing "6 Irish LC subjects
end-to-end" Requirement already lists English; this delta only ADDED the
2 filesystem-layer Requirements above)*
