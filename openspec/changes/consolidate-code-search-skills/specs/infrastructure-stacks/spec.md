## MODIFIED Requirements

### Requirement: Single canonical code search skill

The code search capability SHALL be provided by exactly one skill: `ccc`. The canonical implementation uses CocoIndex v1 + BGE-M3 embeddings + LanceDB HNSW + Dagster asset group. Alternative engines (e.g. ChunkHound) MAY be documented as a subsection of `ccc/SKILL.md` but MUST NOT ship as a separate top-level skill.

#### Scenario: Agent uses ccc for code search

- **WHEN** an agent needs to search the codebase, find a function definition, or summarise a directory
- **THEN** the loader matches exactly one skill: `ccc`
- **AND** `chunkhound` is no longer a top-level skill (its content lives in `ccc/SKILL.md` Appendix A)

#### Scenario: ccc documents the ChunkHound alternative

- **WHEN** an agent reads `ccc/SKILL.md`
- **THEN** an "Appendix A: Alternative engines" section exists
- **AND** that section documents when to use ChunkHound over ccc (the multi-hop exploration pattern, the air-gapped / no-cloud use case)
