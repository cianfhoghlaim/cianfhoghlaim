## ADDED Requirements

### Requirement: 5-notebook BAML+CocoIndex tutorial track (deferred to follow-up)

The system SHALL provide 5 marimo tutorial notebooks at `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` (a new directory following the existing 01-12 numbering scheme) teaching BAML 0.223.0 syntax + CocoIndex v1 integration + the side-by-side vision pipeline.

#### Scenario: tutorial track directory + spec pointer created

- **GIVEN** the `01_overview_setup.py` notebook in `cianfhoghlaim/notebooks/01_overview_setup.py` already has Steps 0-4
- **WHEN** this change lands
- **THEN** a new directory `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` is reserved (currently empty)
- **AND** a "Step 0.5: the BAML+CocoIndex tutorial track" pointer is appended to `cianfhoghlaim/notebooks/01_overview_setup.py`'s table of contents (in this change)
- **AND** the 5 tutorial files (`01_baml_post_v4_syntax.py`, `02_qpack_8_subject_walkthrough.py`, `03_education_pdf_vision_pipeline.py`, `04_cocoindex_baml_integration.py`, `05_post_v4_duplicate_audit_and_migration.py`) are filled in under the `2026-07-12-baml-cocoindex-tutorials-v1` follow-up change

#### Scenario: `Step 0.5` pointer is a non-breaking no-op

- **GIVEN** the Step 0.5 line in `01_overview_setup.py`
- **WHEN** a student or agent runs `marimo edit cianfhoghlaim/notebooks/01_overview_setup.py`
- **THEN** the notebook renders with the original 4 steps intact
- **AND** the new Step 0.5 is a single Markdown cell that links to the (future) `notebooks/13_baml_cocoindex_tutorial/` directory
- **AND** it does not depend on any of the 5 follow-up tutorials existing yet

### Requirement: `01_overview_setup.py` Step 0.5 pointer

The system SHALL append a "Step 0.5: the BAML+CocoIndex tutorial track" Markdown cell to `cianfhoghlaim/notebooks/01_overview_setup.py`'s table of contents between Step 0 (env setup) and Step 1 (vision models).

#### Scenario: `01_overview_setup.py` does not currently exist

- **GIVEN** a directory listing of `cianfhoghlaim/notebooks/` shows no `01_overview_setup.py` at the top level (verified 2026-07-11)
- **AND** the env-setup + drift-detect + openspec-list tutorials live at `cianfhoghlaim/notebooks/01_dev_env/{01..06}_*.py` instead
- **WHEN** this change lands
- **THEN** the Step 0.5 pointer is **deferred to the tutorials follow-up** (`2026-07-12-baml-cocoindex-tutorials-v1`)
- **AND** the placeholder for now is the reserved directory `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` + its `README.md` (which links to the follow-up change)
- **AND** when the overview notebook is created (or an existing `01_*` env-setup notebook is promoted), the Step 0.5 cell references this README.md
