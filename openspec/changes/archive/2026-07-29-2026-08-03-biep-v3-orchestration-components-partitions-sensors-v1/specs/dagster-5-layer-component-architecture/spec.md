## MODIFIED Requirements

### Requirement: 4 Component classes + 5 registry sensors + 2-axis partition

The system SHALL provide the 4 missing Dagster Component classes
(`BIEPSubjectComponent`, `JuniorCycleSubjectComponent`,
`EnglandBoardSubjectComponent`,
`EnglandCrossBoardComparatorComponent`), the 5 registry-change
sensors (NCCA / SQA / WJEC / CCEA / JCQ), the 2-axis `scope × year`
partition, AND the `EnsembledExtractor.extract()` wiring into the 4
generic asset modules.

#### Scenario: 4 Component classes + 5 sensors registered

- **WHEN** `dg list components` runs
- **THEN** the 4 missing Component classes SHALL appear
- **AND** `dg list sensors | grep registry` returns 5 entries
- **AND** `dg check yaml` passes

#### Scenario: 2-axis scope × year partition

- **WHEN** a Dagster materialisation runs for any BIEP v3 asset
- **THEN** the partition keys SHALL be
  `(scope=<jurisdiction>__<stage>__<subject>__<board>__<qualification_level>__<language>, year=<YYYY>)`

#### Scenario: EnsembledExtractor.extract() wired into the 4 generic asset modules

- **WHEN** the `*_extractions` Dagster asset materialises for any
  jurisdiction
- **THEN** the asset SHALL call `EnsembledExtractor.extract(pdf_path=..., baml_function=..., jurisdiction=...)`
- **AND** the per-path DuckLake rows SHALL land in
  `cianfhoghlaim.education.british_isles.<jurisdiction>.<scope>.<subject>.{baml_canonical,unstract_json,qwen3_vl,gemma4,voted_canonical}`