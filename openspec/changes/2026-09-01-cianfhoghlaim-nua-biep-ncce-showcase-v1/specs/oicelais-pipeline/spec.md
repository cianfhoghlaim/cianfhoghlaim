## ADDED Requirements

### Requirement: BAML MUST support 6 per-subject NCCE learning-graph extractors

The Cianfhoghlaim oicelais-pipeline capability MUST expose 6 per-subject
BAML extractors for the UK NCCE learning-graph showcase (one per
the canonical Phase 1 subject + Computer Science):

1. `ExtractComputerScienceLearningGraph(pdf_text, year_level, source_pdf) -> LearningGraph`
2. `ExtractMathematicsLearningGraph(pdf_text, year_level, source_pdf) -> LearningGraph`
3. `ExtractEnglishLearningGraph(pdf_text, year_level, source_pdf) -> LearningGraph`
4. `ExtractGaeilgeLearningGraph(pdf_text, year_level, source_pdf) -> LearningGraph`
5. `ExtractGeographyLearningGraph(pdf_text, year_level, source_pdf) -> LearningGraph`
6. `ExtractNCCEPedagogyPrinciples(pdf_text, source_pdf) -> PedagogyOverlay`
7. `ExtractCrossJurisdictionEquivalencies(...) -> EquivalencyGraph`

Each extractor MUST consume `pdf_text: string` + `year_level: UKNCCEYearLevel` (Y6-Y11) + `source_pdf: string` and emit a typed response. Phase 4 of the
2026-09-01-cianfhoghlaim-nua-v6-era-v1 plan defines these extractors
in `baml_src/british_isles/uk_ncce/learning_graph.baml` +
`baml_src/british_isles/uk_ncce/equivalencies.baml`.

#### Scenario: A researcher extracts an NCCE learning graph

- **WHEN** a researcher runs `b.ExtractComputerScienceLearningGraph(pdf_text="NCCE Y8 Python: Variables → Functions → Classes", year_level=UKNCCEYearLevel.Y8, source_pdf="/data/.../y8_python.pdf")`
- **THEN** the response SHALL be a `LearningGraph` instance
- **AND** the `cells` array SHALL contain at least 2 × 2 cells (one row × column intersection)
- **AND** each cell SHALL have a `pedagogy_principles` array referencing one of the 12 canonical NCCE principles

### Requirement: Convex schema MUST persist NCCE learning-graph rows + equivalencies + pedagogy overlay

The Cianfhoghlaim oicelais-pipeline capability MUST extend the
canonical Convex schema with an `ncce_learning_graphs` table that
persists:

- `subject: string` — one of `computer_science` / `mathematics` / `english` / `gaeilge` / `geography`
- `year_level: string` — one of `Y6` / `Y7` / `Y8` / `Y9` / `Y10` / `Y11`
- `rows_json: v.array(v.record(v.string(), v.any()))` — the skill rows
- `columns_json: v.array(v.record(v.string(), v.any()))` — the lesson columns
- `cells_json: v.array(v.record(v.string(), v.any()))` — the row × column cells
- `prerequisites_json: v.array(v.record(v.string(), v.any()))` — the LO prerequisite arrows
- `pedagogy_overlay_json: v.optional(v.record(v.string(), v.any()))` — the 12-principle overlay
- `equivalencies_json: v.optional(v.array(v.record(v.string(), v.any())))` — the cross-jurisdiction equivalencies

Indices MUST be created on `subject`, `year_level`, and `(subject, year_level)`.

#### Scenario: A learning graph row is persisted

- **WHEN** a researcher submits a BAML extraction result
- **THEN** a new row is inserted into the `ncce_learning_graphs` table
- **AND** the row is queryable via `by_subject_year(subject, year_level)` index

### Requirement: CocoIndex pipeline MUST preserve row × column grid structure

The Cianfhoghlaim oicelais-pipeline capability MUST expose a
CocoIndex App (`cocoindex_flows/uk_ncce/learning_graphs_app.py`)
that walks the 5 NCCE PDF artefacts at
`data/bi_ep/syllabi_raw/uk_ncce/curriculum/` and writes grid-aware
Markdown output to `data/bi_ep/syllabi_md/uk_ncce/` — preserving
the row × column structure of the learning-graph PDFs as Markdown
tables.

The App MUST delegate to
`cocoindex_flows/_shared/_docling_grid_segmenter.extract_markdown_with_grid()`
when Docling is available, falling back to the canonical pypdfium2
extractor when Docling is not installed.

#### Scenario: A NCCE PDF is converted to grid-aware Markdown

- **WHEN** `python -m cocoindex_flows.uk_ncce.learning_graphs_app` runs
- **THEN** all 5 NCCE artefacts (Y6 Variables + Y7 Scratch + Y8 Python + pedagogy + computing journey) are converted
- **AND** each output Markdown file has at least one Markdown table (the row × column grid)
- **AND** the output preserves the prerequisite arrows from the original PDF