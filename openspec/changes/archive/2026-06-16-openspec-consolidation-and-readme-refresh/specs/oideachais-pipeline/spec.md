## MODIFIED Requirements

### Requirement: Curriculum Ingestion

The system SHALL ingest curriculum documents from multiple Irish and
UK sources with caching fallback.

#### Scenario: Integrates with the 4 quadrants

- **WHEN** a developer reads the `oideachais-pipeline` spec
- **THEN** the spec references the 7 oideachais-* openspec specs
  (oideachais-pipeline, oideachais-leabharlann, oideachais-baml-schemas,
  oideachais-cognify-knowledge-graph, oideachais-semantic-search,
  oideachais-marimo-dashboards, ireland-primary-jc-dlt-baml) AND
  the 3 meaisinfhoghlaim-* specs (meaisinfhoghlaim-platform,
  meaisinfhoghlaim-agent-frameworks, meaisinfhoghlaim-ocr-htr) AND
  the 1 tuatha-platform spec AND the 3 croilar-* specs
  (croilar-portfolio, croilar-data-engineering, croilar-cv-extraction)
- **AND** the 4 quadrant AGENTS.md files (sruth/oideachais/AGENTS.md,
  sruth/meaisinfhoghlaim/AGENTS.md, sruth/tuatha/AGENTS.md, sruth/croilar/AGENTS.md)
  are linked from the spec's Cross-references section

#### Scenario: References the right AGENTS.md / README / STATUS

- **GIVEN** the openspec change `openspec-consolidation-and-readme-refresh`
  is archived
- **WHEN** a developer navigates to the pipeline
- **THEN** the canonical `sruth/oideachais/AGENTS.md`,
  `sruth/oideachais/STATUS.md`, `sruth/oideachais/REFACTORING.md`, and the 4
  quadrant READMEs are linked from the spec
