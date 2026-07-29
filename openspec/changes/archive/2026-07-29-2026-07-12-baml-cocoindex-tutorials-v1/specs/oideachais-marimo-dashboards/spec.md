## ADDED Requirements

### Requirement: 5 new BAML+CocoIndex tutorial notebooks render in marimo edit + dual-mode CLI

The system SHALL provide 5 new marimo tutorial notebooks at
`notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
covering the full BAML 0.223.0 + CocoIndex v1 + vision-model stack.
The 5 notebooks SHALL be CLI-discoverable via
`uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial` and
SHALL render in `marimo edit` mode without error. Each notebook SHALL
be dual-mode (marimo app + standalone CLI script via PEP 723 inline
dependency blocks).

The 5 notebooks are:
1. `01_baml_post_v4_syntax.py` — canonical post-v4 BAML 0.223.0 syntax
2. `02_qpack_8_subject_walkthrough.py` — the 8 `qpack_<subject>.baml` files
3. `03_education_pdf_vision_pipeline.py` — the vision+PDF pipeline with
   side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison
4. `04_cocoindex_baml_integration.py` — the 3 real CocoIndex+BAML patterns
5. `05_post_v4_duplicate_audit_and_migration.py` — the 42-renames commit audit

#### Scenario: 5 tutorial files AST-parse + CLI-discoverable

- **GIVEN** the 5 follow-up tutorials exist at
  `notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
- **WHEN** the user runs
  `python -c "import ast; ast.parse(open(f).read())"` for each
- **THEN** all 5 files parse without SyntaxError
- **AND** `uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
  returns exactly 5 entries

#### Scenario: Tutorial 3 has the side-by-side vision comparison cell

- **GIVEN** the `03_education_pdf_vision_pipeline.py` tutorial renders
- **WHEN** the user clicks the side-by-side cell
- **THEN** the cell calls `baml_sync.ExtractSyllabusDiagram` with
  `pointing_model="gemma-4-26B-A4B"` AND
  `pointing_model="qwen3-vl-8b"` on the same PDF
- **AND** the cell emits a marimo `mo.ui.table` showing both outputs
  side-by-side with the `match_confidence` Jaccard similarity