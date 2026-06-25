## MODIFIED Requirements

### Requirement: Orphan BAML functions SHALL be archived
The oideachais quadrant SHALL NOT have orphan BAML functions
(defined but with no Python consumer) in `sruth/oideachais/baml_src/`.
Any BAML function that has no current consumer MUST either be
wired to a working consumer (per the
`wire-baml-with-known-consumers` pattern) or moved to
`sruth/oideachais/baml_src/_archive/`.

#### Scenario: A BAML function is added but the consumer is not yet built
- **WHEN** a contributor adds a new BAML function whose intended
  consumer (e.g. a meaisinfhoghlaim agent) does not yet exist
- **THEN** they MUST either:
  - Wait for the consumer to be built first, OR
  - Place the function in `baml_src/_archive/<descriptive_name>.baml`
    with the ARCHIVED header, AND
  - Update `sruth/oideachais/REFACTORING.md` with the re-activation plan

#### Scenario: An archived BAML function is re-activated
- **WHEN** a contributor implements the deferred consumer
  (e.g. `sruth/meaisinfhoghlaim/agents/celtic_linguistics.py`)
- **THEN** they MUST:
  - Move the archived .baml file back to `baml_src/` (git mv)
  - Remove the ARCHIVED header
  - Add `# PLANNED — wired to <consumer_module>` marker
  - Update `sruth/oideachais/STATUS.md` to mark the function as wired
  - Delete the entry from `sruth/oideachais/REFACTORING.md`
