## ADDED Requirements

### Requirement: DocSkills Knowledge Graph
The system SHALL publish a `docs_skills_graph` graph in FalkorDB that captures the tagged, extracted, and consolidated view of `docs/` and `.agents/skills/`.

#### Scenario: Graph schema
- **GIVEN** the `docs_skills_graph` is initialised in FalkorDB
- **WHEN** the `docs_skills_consolidation` CocoIndex v1 App runs
- **THEN** the graph SHALL contain the following node types and primary keys:

| Node type | Primary key | Properties |
|---|---|---|
| `DocSkill` | `path` (sha256) | `category`, `quadrant`, `confidence`, `byte_size`, `last_seen` |
| `Concept` | `value` | (canonical concept name) |
| `ConsolidationGroup` | `group_id` | `canonical_path`, `reason`, `member_count` |

- **AND** the graph SHALL contain the following edges:
  - `TAGGED` from `DocSkill` → `ConsolidationGroup`
  - `CONSOLIDATED_INTO` from `DocSkill` → `DocSkill` (per-member link to the canonical)
  - `RELATES_TO` from `Concept` → `Concept` with the predicate stored as an edge property

#### Scenario: Re-extraction on source change
- **GIVEN** a file in `docs/` whose content has changed
- **WHEN** the App re-runs the `process_file` component
- **THEN** the corresponding `DocSkill` node SHALL be updated in place (path is the stable primary key)
- **AND** any `RELATES_TO` edges that came from the old triple set but no longer appear SHALL be removed
- **AND** new `RELATES_TO` edges SHALL be added

#### Scenario: Read-only consumer
- **GIVEN** the `docs_skills_graph` is populated
- **WHEN** any agent or Dagster asset queries it
- **THEN** the query SHALL be a read-only Cypher query
- **AND** the connection SHALL be reusable across processes
- **AND** the connection SHALL come from the `KG_DB` ContextKey declared in `docs_skills_consolidation.py`
