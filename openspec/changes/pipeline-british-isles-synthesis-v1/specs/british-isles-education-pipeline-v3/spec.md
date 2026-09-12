# BIEP v3 Ireland LC M1 Per-Subject Pipeline Synthesis

## ADDED Requirements

### Requirement: BIEP v3 Ireland LC M1 per-subject pipeline synthesis

The system SHALL provide a canonical per-subject CocoIndex v1 App
+ BAML fallback + LanceDB target + per-subject pytest for each of
the 6 BIEP v3 Ireland LC subjects:

1. **Mathematics** — `cocoindex_flows/british_isles/ireland/education/lc/mathematics.py`
2. **Chemistry** — `cocoindex_flows/british_isles/ireland/education/lc/chemistry.py`
3. **Geography** — `cocoindex_flows/british_isles/ireland/education/lc/geography.py`
4. **English** — `cocoindex_flows/british_isles/ireland/education/lc/english.py`
5. **Gaeilge** — `cocoindex_flows/british_isles/ireland/education/lc/gaeilge.py` (ga-only)
6. **Computer Science** — `cocoindex_flows/british_isles/ireland/education/lc/computer_science.py`

Each App MUST conform to the BIEP v3 R1-R4 contract:
- **R1** — `from ....._shared._lifespan import shared_lifespan`
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` ContextKeys
- **R3** — `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — At least one `@coco.fn(...)` decorator (2 in fact: `process_*_file` + `*_app_main`)

The 6 Apps MUST be validated by 6 per-subject pytests in
`tests/biep_parity_lc/test_<subject>.py` that exercise the full
load → embed → store → query pipeline against a 3-row per-subject
fixture (HL/OL/FL snippets). The pytests MUST use the
`pure_python_embed` (deterministic numpy substitute for BGE-M3),
the `python_baml_fallback_extract` (regex-based fallback for the
BAML extraction function used when defect #3 blocks `baml_client/`
from regenerating), and the `InMemoryLanceTable` (a list-based
"LanceDB table" substitute).

#### Scenario: All 6 per-subject pipelines pass end-to-end

- **WHEN** the operator runs `uv run pytest tests/biep_parity_lc/ -v`
- **THEN** all 29 tests pass (9 Mathematics + 4 × 5 siblings)
- **AND** each per-subject `run_<subject>_subject(sourcedir=<tmp>)` returns 3 rows
- **AND** each row has a 1024-d `embedding` + non-empty `extracted_topic` + `extracted_level` + `extracted_year`

#### Scenario: What works / What's blocked table

| Subject | CocoIndex App | BAML fallback | Pytest | End-to-end | Blocked by |
|---|---|---|---|---|---|
| Mathematics | ✅ | ✅ | ✅ 9/9 | ✅ | none |
| Chemistry | ✅ | ✅ | ✅ 4/4 | ✅ | none |
| Geography | ✅ | ✅ | ✅ 4/4 | ✅ | none |
| English | ✅ | ✅ | ✅ 4/4 | ✅ | none |
| Gaeilge | ✅ | ✅ (Irish) | ✅ 4/4 | ✅ | none |
| Computer Science | ✅ | ✅ | ✅ 4/4 | ✅ | none |

#### Scenario: Inert-layer status

The 5 inert-layer defects from the kcg-runtime-inert-layers memory
are verified as of the date of this change:

- **#1 (cocoindex shadow)** — FIXED. `cocoindex 1.0.20` resolves to PyPI site-packages.
- **#2 (defs/__init__.py)** — FIXED. `orchestration/defs/__init__.py` exists.
- **#3 (baml_client)** — EVOLVED. `baml_client/` doesn't exist; `baml-cli generate` fails on duplicate class definitions in `baml_src/_shared/templates/`. The per-subject pipelines use the Python BAML fallback (regex-based).
- **#4 (dlt_sources vs dlt)** — MOSTLY FIXED. `import dlt_sources` is a no-op; `dlt.X` API calls work everywhere.
- **#5 (OCR ensemble)** — PARTIALLY FIXED. VLM calls now send real images; hardcoded `confidence_score=0.9` at `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:639` remains.

### Requirement: Next-session defect remediation order

To unblock the next phase of work (BIEP v3 England A-Level +
England GCSE + the rest), the next session MUST attack the
defects in this order:

1. **Defect #3 (BAML client generation)** — consolidate the 18
   domain templates per the 2026-12-XX-mega-3d-baml-quality-v1
   change, then remove the duplicate class definitions across
   `baml_src/_shared/templates/` + `baml_src/processing/`.
2. **Defect #5 (OCR ensemble hardcoded confidence)** — small
   change at `ensembled_extractor.py:639` to compute the confidence
   from the actual RAGAS `biiep_extraction_consensus` vote.

#### Scenario: Defect remediation order is documented

- **WHEN** the next session runs `openspec list` to find the
  British Isles pipeline work
- **THEN** the synthesis change's "Next session: defect remediation
  order" section is the canonical reference
- **AND** it identifies defect #3 as the P0 unblock for BAML → CocoIndex wiring
