# fibo-asset-pipeline Specification

## Purpose
`fibo-asset-pipeline` is the contract for the FIBO 2D diagram generation
pipeline that produces the celtic-art window chrome + 2D sprite atlases
for the 8 NCCA Leaving Certificate subject realms. Each subject has a
canonical prompt template (per the Brown Ajah theming) that references
the relevant Tuatha Dé deity + treasure + game UI inspiration.

The pipeline is a 5-stage flow:
1. `fibo_json_configs` (Dagster asset) — generates FiboConfig records from
   a sample concept + the canonical prompt template
2. `fibo_configs_from_syllabus_diagrams` (Dagster asset) — generates
   FiboConfig records from REAL BAML-extracted SyllabusDiagram records
   (the docs-informed alternative to the sample-concept path)
3. `FiboResource` (Dagster resource) — calls litellm image gen with the
   resolved image_gen model's litellm_alias
4. `ValidationResource` (Dagster resource) — scores the rendered asset
   with a VLM (openai/gpt-4o-mini) against the validation_criteria
5. The asset refinement loop — re-renders up to `max_refinement_iterations`
   times until the validation score ≥ threshold

Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## ADDED Requirements

### Requirement: 8 NCCA subjects + bilingual (EN + GA) coverage

The system MUST provide 8 subject-specific FIBO prompt templates (one
per NCCA Leaving Certificate subject) in
`tuatha/asset_generation/fibo/education_fibo.py`. Each prompt MUST
be bilingual (EN + GA) and MUST reference:

- The canonical Tuatha Dé deity (per the Brown Ajah theming)
- The Celtic-adaptation of the 4 game UIs (Hades / Clair Obscur / WoW / BitCraft)
- The `baml_color` CSS custom property for the subject

#### Scenario: Chemistry prompt renders
- **WHEN** the operator runs `uv run python scripts/fibo_render.py --subject chemistry`
- **THEN** the prompt is `Render a celtic-art window chrome for the Chemistry realm. Use Dian Cecht's healing cauldron + Nuada's silver hand as the central UI motif. Style: Hades shadow-first + material library.`
- **AND** the GA version is `Déan ciorcal ceoil Ceilteach don réimse Ceimice. Úsáid coire leighis Dian Cécht + lámh airgid Nuada mar mhóitíf láir.`

### Requirement: 5-stage pipeline per asset

The system MUST run, for every subject + language pair (16 total: 8 subjects × 2 languages),
the system MUST run the 5-stage pipeline:

1. **BAML extraction** — `get_fibo_prompt(subject, language)` returns the prompt template
2. **FIBO config generation** — `fibo_json_configs` Dagster asset produces a typed `FiboConfig` record
3. **Asset rendering** — `FiboResource.render(prompt, palette_hex)` calls litellm image gen + writes a PNG + a sidecar manifest
4. **Validation** — `ValidationResource.validate(asset_path, criteria)` scores the rendered asset via the VLM (openai/gpt-4o-mini)
5. **Refinement iteration** — if the score is below `score_threshold`, re-render with the validation feedback (up to `max_refinement_iterations`)

#### Scenario: Chemistry asset renders in stub mode (offline)
- **GIVEN** the litellm gateway is unreachable
- **WHEN** the operator runs the chemistry pipeline
- **THEN** the `FiboResource.render()` returns a stub dict with `"stub": True` + a 1x1 placeholder PNG
- **AND** the `ValidationResource.validate()` returns a stub dict with `"stub": True` + `score: 0.0`
- **AND** the pipeline completes in <1s (no waiting for timeout)

### Requirement: Real syllabus diagram extraction (BAML-driven, docs-informed)

The system MUST provide an `ExtractSyllabusDiagram` BAML function in
`baml_src/media/extract_syllabus_diagram.baml` (new file) that takes
`pdf_text` + `pdf_images` and returns typed `SyllabusDiagram` records
from REAL NCCA syllabus PDFs. The extracted diagrams MUST trace back
to the source PDF page (no fabricated concepts). Each diagram MUST carry:

- `diagram_id` (deterministic: sha256(subject + page + caption))
- `source_pdf` (the path to the source PDF)
- `page_number` (the page where the diagram was found)
- `caption` (the figure caption text)
- `subject` (the NCCA subject)

For each extracted diagram, the system MUST produce a `FiboConfig`
record (the docs-informed alternative to `fibo_json_configs`'s
sample-concept path) where the prompt references the diagram caption.

#### Scenario: Chemistry syllabus page 3 has a real diagram
- **GIVEN** the chemistry_2019.pdf has a figure on page 3 ("Figure 3: Overview of Leaving Certificate Chemistry")
- **WHEN** `fibo_configs_from_syllabus_diagrams` materialises
- **THEN** `ExtractSyllabusDiagram` returns ≥1 record with `diagram_id`, `source_pdf="chemistry_2019.pdf"`, `page_number=3`, `caption="Overview of Leaving Certificate Chemistry"`
- **AND** the produced `FiboConfig` carries the `caption` in the prompt

#### Scenario: Subject with no English syllabus is skipped
- **WHEN** `fibo_configs_from_syllabus_diagrams` materialises for a subject with no English-medium PDF in `leaving_certificate/`
- **THEN** no `FiboConfig` is produced for that subject (the asset still runs but produces 0 docs-informed configs)

### Requirement: Dagster asset wiring (3 assets)

The system MUST ship 3 Dagster assets per the `fibo` group:

1. `fibo_json_configs` (depends on no upstream asset) — generates FiboConfig records from sample concepts
2. `generated_images` (depends on `fibo_json_configs`) — renders images + validates up to `max_refinement_iterations`
3. `fibo_configs_from_syllabus_diagrams` (depends on no upstream asset) — generates docs-informed configs from REAL syllabus diagrams

All 3 assets MUST conform to the canonical 5-layer Component architecture
(per `dagster-5-layer-component-architecture` spec) and MUST be visible
in the Dagster UI under the `fibo` asset group.

#### Scenario: Dagster UI shows the 3 assets
- **WHEN** the operator opens Dagster at `http://localhost:3000`
- **THEN** the `fibo` asset group is visible with 3 assets: `fibo_json_configs` + `generated_images` + `fibo_configs_from_syllabus_diagrams`
- **AND** clicking `fibo_json_configs` shows the 16 generated FIBO configs (8 subjects × 2 languages)
