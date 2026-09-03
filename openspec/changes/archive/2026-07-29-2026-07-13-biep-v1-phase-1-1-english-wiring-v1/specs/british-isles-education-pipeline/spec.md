# `british-isles-education-pipeline` MODIFIED — Phase 1.1 English lc5 wiring verification

## ADDED Requirements

### Requirement: Phase 1.1 English lc5 wiring verified complete (2026-07-13)

The system SHALL satisfy the four static Phase 1.1 verification
gates on the `pick-4-biep-v1` branch as of 2026-07-13. The
Phase 1.1 sub-batch of the BIEP v1 flagship (the 6-subject LC
filesystem wiring for English) was already code-shipped by the
prior openspec change
`2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` (commit
`ba234de61`); this delta captures the verification status, NOT
the implementation. The flagship's Phase 1.1 `[ ]` tick-boxes
remain un-ticked in the archived
`openspec/changes/archive/2026-07-09-2026-07-06-british-isles-education-pipeline-v1/tasks.md`
(the archive is frozen — modification would violate the "Do NOT
touch the 50+ archived openspec changes" hard rule), but the
underlying code state SHALL satisfy the four gates below.

#### Scenario: Gate 1 — `LC6_SUBJECTS` includes `english` as the 3rd element

- **GIVEN** the file
      `dlt/filesystem/leaving_cert_source.py`
- **WHEN** an agent runs `grep -A 7 "^LC6_SUBJECTS" dlt/filesystem/leaving_cert_source.py`
- **THEN** the output SHALL be exactly:
      ```python
      LC6_SUBJECTS: tuple[str, ...] = (
          "chemistry",
          "computer_science",
          "english",
          "gaeilge",
          "geography",
          "mathematics",
      )
      ```
- **AND** `grep -rn "LC5_SUBJECTS" cianfhoghlaim/` SHALL return
      zero matches (the rename is complete — no stale references
      in the source tree)

#### Scenario: Gate 2 — `LC_PDF_KIND_REGISTRY` has 2 English regex patterns

- **GIVEN** the `LC_PDF_KIND_REGISTRY` dict in
      `dlt/filesystem/leaving_cert_source.py`
- **THEN** the dict SHALL contain both of these patterns:
      - `r"^LC002ALP\d{3}[EI]V\.pdf$"` mapped to `qwen3-vl-8b`
        (the LC English ALP/GLP exam-paper kind)
      - `r"^SC-English-Spec-ENG-INT.*\.pdf$"` mapped to
        `gemma-4-26B-A4B` (the English spec-constitution kind)
- **AND** `_scan_subject` SHALL have an
      `elif subject_dir.name == "english"` branch that emits files
      at the root with `language = "en"` (the English LC syllabus
      is monolingual — no `en/` subdir needed, mirrors the gaeilge
      asymmetry)

#### Scenario: Gate 3 — 6 `lc5_english_*` assets exist in `lc5_assets.py`

- **GIVEN** the file
      `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
- **THEN** the asset registry SHALL contain exactly these 6 names:
      - `lc5_english_ingested` (explicit `@asset` decorator, Layer 1)
      - `lc5_english_syllabus_extracted`
      - `lc5_english_papers_extracted`
      - `lc5_english_marking_extracted`
      - `lc5_english_diagrams_extracted`
      - `lc5_english_cognified` (explicit `@asset` decorator, Layer 3)
- **AND** the 4 `*_extracted` assets SHALL be generated at
      module-import time by the factory loop
      `for _subject in LC6_SUBJECTS: for _kind in ("syllabus",
      "papers", "marking", "diagrams"): globals()[f"lc5_{_subject}_{_kind}_extracted"]`
      at lines 199-201 (the loop binds to `LC6_SUBJECTS`, which
      contains `"english"` per Gate 1)

#### Scenario: Gate 4 — `english.yaml` cron asset exists

- **GIVEN** the path
      `orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
- **THEN** the file SHALL exist (≥ 1 KB)
- **AND** its top-level `type` SHALL be
      `cianfhoghlaim.orchestration.components.CelticIngestionComponent`
- **AND** its `attributes` SHALL include:
      - `source_id: cianfhoghlaim.filesystem.leaving_cert.english`
      - `subject: english`
      - `automation_cron: "0 5 * * *"` (UTC, mirrors
        `lc5/defs.yaml`)
      - `state_backed: true`
      - `tags: [biep, lc6, english, ingestion]`

## MODIFIED Requirements

*(no prior requirements are modified — this delta is a pure
verification ADDED Requirement; the existing "6 Irish LC subjects
end-to-end" Requirement + the prior change's
"All 6 LC subjects have working filesystem DLT source" Requirement
remain unchanged)*