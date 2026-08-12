## ADDED Requirements

### Requirement: Purpose-section accuracy note (visibility)

The `celtic-asset-generation` spec's Purpose section SHALL carry an
explicit note that the "4 successive INDEPENDENT asset-generation
pipelines" description (`official_documents/`, `subject_assets/`,
`language_assets/`, `exporters/{babylon,godot,unity,unreal}`) at
`cianfhoghlaim/assets/asset_generation/` does not correspond to code
that exists in the live tree, and that the real, working asset
generation code lives at `tuatha/asset_generation/fibo/` instead. This
SHALL be a visible note, not a silent removal — a full rewrite or
deletion of the aspirational content is out of scope for this change
(see the "FIBO 2D educational diagram generation" requirement below
for what actually runs today).

#### Scenario: A developer reads the spec's Purpose section

- **GIVEN** a developer opens `openspec/specs/celtic-asset-generation/
  spec.md` looking for the real asset-generation code path
- **WHEN** they read the Purpose section
- **THEN** they find an explicit note directing them to
  `tuatha/asset_generation/fibo/` for the real, working pipeline
- **AND** the note does not claim the 4-pipeline / 6-Celtic-language /
  4-game-engine-exporter structure is implemented

### Requirement: FIBO 2D educational diagram generation (as-built)

The system SHALL generate 2D educational diagram assets via the FIBO
pipeline at `tuatha/asset_generation/fibo/` (Dagster assets in
`orchestration/defs/4_asset_generation/`), consisting of: (1)
`fibo_json_configs`, which turns curriculum concepts into FIBO JSON
generation configs; (2) `fibo_configs_from_syllabus_diagrams`, which
turns real diagrams detected by `ExtractSyllabusDiagram` in a subject's
official NCCA syllabus PDF into FIBO JSON configs — the docs-informed
alternative to `fibo_json_configs`' sample-concept fallback; and (3)
`generated_images`, which renders each config via `FiboResource`,
validates it with `ValidationResource` (a VLM-based scorer), and
refines up to `max_refinement_iterations` times before accepting the
result. Diagram content used as generation input SHALL trace back to a
real source PDF page — never a fabricated concept — whenever
`fibo_configs_from_syllabus_diagrams` is the config source.

#### Scenario: Real diagram detected and turned into a FIBO config

- **GIVEN** a subject's English-medium syllabus PDF contains a figure
  the text references (e.g. "Figure 3: Overview of Leaving Certificate
  Chemistry")
- **WHEN** `fibo_configs_from_syllabus_diagrams` runs for that subject
- **THEN** `ExtractSyllabusDiagram` returns ≥1 `SyllabusDiagram` record
  with a `page_number` and `source_pdf`
- **AND** the resulting FIBO config's `_metadata` carries that
  `diagram_id`, `source_pdf`, and `page_number` — traceable back to
  the real PDF page, not fabricated

#### Scenario: Subject with no English-medium syllabus is skipped, not fabricated

- **GIVEN** a subject (e.g. gaeilge) has no English-medium syllabus PDF
  in the corpus
- **WHEN** `fibo_configs_from_syllabus_diagrams` runs for that subject
- **THEN** the asset materialises with `configs_generated = 0`
- **AND** no FIBO config is fabricated from a sample/placeholder concept
