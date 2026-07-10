## MODIFIED Requirements

### Requirement: 5-notebook BAML+CocoIndex tutorial track

The system SHALL provide 5 marimo tutorial notebooks at `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` (a new directory following the existing 01-12 numbering scheme) covering the full BAML 0.223.0 + CocoIndex v1 + vision-model stack. The 5 notebooks SHALL be:

1. `01_baml_post_v4_syntax.py` — canonical post-v4 BAML 0.223.0 syntax (`generator` block + `field Type` whitespace + `enum` / `class` / `function` + `@description` + `image` + `@stream.*` + `?` optionality)
2. `02_qpack_8_subject_walkthrough.py` — the 8 `qpack_<subject>.baml` files, demonstrating the `paragraph → LO[] → FormativeItem → Score → Validate` pattern across all 8 LC subjects (40+ BAML calls)
3. `03_education_pdf_vision_pipeline.py` — the vision+PDF extraction pipeline (`ExtractCurriculumSyllabus` → `ExtractExamPaperLayout` → `ExtractSyllabusDiagram` → `ExtractMarkingSchemeGuideline`) with a **side-by-side** `gemma-4-26B-A4B` vs `qwen3-vl-8b` comparison cell on the same PDFs
4. `04_cocoindex_baml_integration.py` — the 3 real CocoIndex+BAML integration patterns (`upstream_api_surface`, `upstream_blog_monitor`, `docs_skills_consolidation`) including the lazy-import pattern, the `coco.use_context(BAML_CLIENT_*)` provider, and the fallback-stub for when BAML isn't generated
5. `05_post_v4_duplicate_audit_and_migration.py` — the interactive (marimo-reactive) audit of the duplicates from the 42-renames commit (`49e0259a0`), with each duplicate row becoming a cell block + the user picking which one to keep + a `baml-rename-XX.patch` diff emission + the residual `baml-cli generate --mode check` 50-error report

#### Scenario: 5 tutorial files present and CLI-discoverable

- **GIVEN** the 5 follow-up tutorials exist at `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/{01..05}_*.py`
- **WHEN** the user runs `uv run cianfhoghlaim-marimo list 13_baml_cocoindex_tutorial`
- **THEN** the CLI returns exactly 5 entries
- **AND** `uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax` opens marimo edit without error
- **AND** all 5 files AST-parse under `python -c "import ast; ast.parse(open(f).read())"`

#### Scenario: side-by-side vision model comparison in tutorial 3

- **GIVEN** the `03_education_pdf_vision_pipeline.py` tutorial renders
- **WHEN** the user clicks the side-by-side cell
- **THEN** the cell calls `baml_sync.ExtractSyllabusDiagram(pdf=..., pointing_model="gemma-4-26B-A4B")` AND `baml_sync.ExtractSyllabusDiagram(pdf=..., pointing_model="qwen3-vl-8b")` on the same PDF
- **AND** the cell emits a marimo `mo.ui.table` showing both outputs side-by-side
- **AND** the cell notes the practical difference between the two local vision models (gemma-4-26B-A4B favours structure, qwen3-vl-8b favours OCR fidelity)

## ADDED Requirements

### Requirement: 5 Gaeilge (Irish-language) counterpart tutorials

The system SHALL provide 5 Gaeilge (Irish-language) counterpart tutorial notebooks at `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/*_ga.py` that demonstrate the bilingual EN+GA extraction path through the same BAML 0.223.0 + CocoIndex v1 + vision-model stack as the 5 English tutorials. The 5 _ga notebooks SHALL be:

1. `01_baml_post_v4_syntax_ga.py` — bilingual EN+GA syntax additions (`enum GaeilgeLanguage`, `class BilingualText`, `function ExtractBilingualText`, `function ExtractStrandGaStatement`) plus a `bilingual(en, ga)` rendering helper
2. `02_qpack_8_subject_walkthrough_ga.py` — the 6 GA-LC-subject qpack variants (gaeilge + mathematics + history + geography + chemistry + applied_mathematics) with the `Extract<Subject>GaStatement` functions
3. `03_education_pdf_vision_pipeline_ga.py` — the side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b` vision model comparison on Gaeilge NCCA PDFs (handling the síneadh fada + dual-column Irish+English layout)
4. `04_cocoindex_baml_integration_ga.py` — the 3 CocoIndex+BAML integration patterns applied to GA content (the bilingual `ExtractBilingualText` calls + the `language: "ga"` discriminator)
5. `05_post_v4_duplicate_audit_and_migration_ga.py` — the bilingual audit of the 10 BAML additions (4 in `_shared/content_types.baml` + 6 GA-qpack variants), confirming 0 new duplicates and 0 new residual errors

The system SHALL also extend `cianfhoghlaim/baml/education/_shared/content_types.baml` with the `enum GaeilgeLanguage` discriminant and the `function ExtractBilingualText(content) -> BilingualText` + `function ExtractStrandGaStatement(paragraph) -> string[]` extraction primitives, and SHALL extend each of the 6 GA-LC-subject qpack files (`qpack_gaeilge.baml`, `qpack_mathematics.baml`, `qpack_history.baml`, `qpack_geography.baml`, `qpack_chemistry.baml`, `qpack_applied_mathematics.baml`) with an `Extract<Subject>GaStatement(paragraph) -> string[]` function that uses `client default` and the `[EN-only]` fallback marker for LOs the NCCA did not translate.

#### Scenario: 5 _ga companion files present and AST-parse cleanly

- **GIVEN** the 5 _ga counterpart tutorials exist at `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/{01..05}_*_ga.py`
- **WHEN** the user runs `for nb in <the 5 _ga paths>; do python3 -c "import ast; ast.parse(open('$nb').read())"; done`
- **THEN** all 5 files AST-parse without error
- **AND** the `baml/education/_shared/content_types.baml` file contains the `enum GaeilgeLanguage { GA EN }` declaration + the `function ExtractBilingualText` + the `function ExtractStrandGaStatement`
- **AND** each of the 6 GA-LC-subject qpack files contains the `Extract<Subject>GaStatement` function

#### Scenario: GA side-by-side vision comparison in tutorial 3 _ga

- **GIVEN** the `03_education_pdf_vision_pipeline_ga.py` tutorial renders
- **WHEN** the user clicks the side-by-side cell
- **THEN** the cell runs the same Gaeilge NCCA PDF diagram page through both vision models (`gemma-4-26B-A4B` and `qwen3-vl-8b`)
- **AND** the cell notes the GA-specific challenges (síneadh fada fidelity + dual-column Irish+English layout)
- **AND** the cell emits a marimo `mo.ui.table` with the side-by-side comparison + a `match_confidence` Jaccard similarity score

#### Scenario: bilingual extraction primitives in `_shared/content_types.baml`

- **WHEN** the user runs `grep -n "GaeilgeLanguage\|ExtractBilingualText\|ExtractStrandGaStatement" cianfhoghlaim/baml/education/_shared/content_types.baml`
- **THEN** the output shows exactly 4 matches: 1 for `GaeilgeLanguage` enum + 1 for `ExtractBilingualText` function + 1 for `ExtractStrandGaStatement` function + 1 for the comment header
- **AND** the `GaeilgeLanguage` enum values are unquoted (BAML enum syntax requires unquoted all-caps values, NOT quoted string values)

#### Scenario: 6 GA-qpack variants expose `Extract<Subject>GaStatement`

- **WHEN** the user runs `grep -l "ExtractGaelGaStatement\|ExtractMathGaStatement\|ExtractHistGaStatement\|ExtractGeogGaStatement\|ExtractChemGaStatement\|ExtractAppmGaStatement" cianfhoghlaim/baml/education/subjects/*.baml`
- **THEN** exactly 6 files match (one per GA-LC-subject qpack)
- **AND** each qpack file's `Extract<Subject>GaStatement` function uses `client default` (NOT `client ExtractEn`)
- **AND** each qpack file's `Extract<Subject>GaStatement` function signature is `(paragraph: string) -> string[]` (matching the EN `Extract<Subject>LOStatement` shape)

#### Scenario: README.md is updated with the 5 _ga companion entries

- **WHEN** the user reads `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/README.md`
- **THEN** the README lists both the 5 English tutorials AND the 5 _ga Gaeilge counterparts
- **AND** the README cross-references `openspec/changes/2026-07-13-baml-cocoindex-tutorials-ga-v1/`