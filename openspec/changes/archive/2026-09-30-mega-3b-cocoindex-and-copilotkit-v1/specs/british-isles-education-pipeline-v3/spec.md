## ADDED Requirements

### Requirement: 4 stage CocoIndex factories cover all 4 stages

The system SHALL provide 4 stage CocoIndex factories that cover the
canonical 4-stage plane (Leaving Cycle + Junior Cycle + A-Level + GCSE).

The 4 factories generate Apps as follows:
- `ireland_lc_factory` — 14 LC subjects × EN + GA = 11 Apps
  (6 subjects × 2 langs minus 1 for Gaeilge)
- `ireland_jc_factory` — 8 JC subjects × EN + GA = 16 Apps
  (the 8 NCCA Junior Cycle subjects at full scope per Q4)
- `england_alevel_factory` — 15 A-Level subjects × 3 boards = 45 Apps
- `england_gcse_factory` — 9 GCSE subjects × 3 boards = 27 Apps

Total: 11 + 16 + 45 + 27 = **99 CocoIndex Apps**

#### Scenario: Each stage factory generates the right App count

- **WHEN** `mise run cocoindex:list` runs
- **THEN** the output is:
 - 11 apps for `ireland_lc_factory`
 - 16 apps for `ireland_jc_factory`
 - 45 apps for `england_alevel_factory`
 - 27 apps for `england_gcse_factory`

### Requirement: european_nations factory v2 collapses 40 country files

The system SHALL provide a single `cocoindex/european_nations/_factory.py`
that generates 40 CocoIndex Apps (one per European nation).

The factory consumes the `NATION_CONFIG` table (the canonical 40-row
country table) and generates Apps with the canonical
`BAAI/bge-m3` 1024-d embedder.

#### Scenario: european_nations factory generates 40 Apps

- **WHEN** `mise run cocoindex:update -- european_nations` runs
- **THEN** the system creates 40 CocoIndex Apps (one per country)
- **AND** the 40 hand-written `cocoindex/european_nations/<country>/education_embedding.py`
  files are deleted

### Requirement: CocoIndex → BAML wiring for the BIEP v3 lineage viewer

The system SHALL ensure that every CocoIndex App emits lineage
metadata (per the R28 lineage spec) that includes the BAML function
name + the extraction confidence.

#### Scenario: Each CocoIndex App emits lineage metadata

- **GIVEN** a CocoIndex App that calls `b.ExtractCurriculumSyllabus(...)`
- **WHEN** the App materialises (via Dagster asset or `mise run cocoindex:update`)
- **THEN** the lineage metadata includes:
 - `extraction_function: "ExtractCurriculumSyllabus"`
 - `extraction_client: "BIEPV3Extract"`
 - `extracted_at: ISO 8601 UTC timestamp`
 - `confidence: float (0.0-1.0)`

### Requirement: CocoIndex live mode (FF.5 from fast-follow)

The system SHALL use CocoIndex live mode (`live=True` in
`localfs.walk_dir`) for the 4 stage factories so that changes to the
canonical BIEP source directories (e.g.,
`dlt/british_isles/ireland/education/`) trigger re-extraction in
real-time.

#### Scenario: Live mode re-extracts on source change

- **GIVEN** the `ireland_lc_factory` is running with `live=True`
- **WHEN** the operator updates a file in
  `dlt/british_isles/ireland/education/lc_extraction/`
- **THEN** the CocoIndex App re-extracts the file within 30 seconds
- **AND** the lineage metadata reflects the new `extracted_at` timestamp