## ADDED Requirements

### Requirement: 5 BAML+CocoIndex tutorial notebooks render in marimo

The system SHALL provide 5 marimo tutorial notebooks at
`notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py` covering the
full BAML 0.223.0 + CocoIndex v1 + vision-model stack. The 5
notebooks SHALL be CLI-discoverable via
`uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial` and
SHALL render in `marimo edit` mode without error. Each notebook
SHALL be dual-mode (marimo app + standalone CLI script via PEP 723
inline dependency blocks).

The 5 notebooks are:

1. `01_baml_post_v4_syntax.py` — canonical post-v4 BAML 0.223.0 syntax
2. `02_qpack_8_subject_walkthrough.py` — the 8 `qpack_<subject>.baml`
   files
3. `03_education_pdf_vision_pipeline.py` — the vision+PDF pipeline
   with side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison
4. `04_cocoindex_baml_integration.py` — the 3 real CocoIndex+BAML
   patterns
5. `05_post_v4_duplicate_audit_and_migration.py` — the 42-renames
   commit audit

#### Scenario: 5 tutorial files AST-parse + CLI-discoverable

- **GIVEN** the 5 follow-up tutorials exist at
  `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
- **WHEN** the user runs `uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
- **THEN** all 5 files SHALL be listed
- **AND** each file SHALL AST-parse without error