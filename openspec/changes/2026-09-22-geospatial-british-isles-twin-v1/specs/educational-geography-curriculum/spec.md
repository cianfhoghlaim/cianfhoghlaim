## ADDED Requirements

### Requirement: 4 Syllabuses Bound to Geospatial Layers

The system SHALL provide a canonical mapping from Leaving Certificate
Geography, English A-Level Geography, Scottish CfE Higher Geography, and
Welsh WJEC Geography to the 5 geospatial layers.

#### Scenario: LC Geography Core Unit 1.1 mapping
- **WHEN** the user invokes `curriculum.lookup_geo_layer("LCGEO-1.1-PT")`
- **THEN** the function returns `["geomorphology", "geology"]`

### Requirement: Educational Geography Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/educational_geography_agent.py`
as an ADK agent with 10 tools.

#### Scenario: Agent queries curriculum binding
- **WHEN** the user invokes `educational_geography_agent` with "What geospatial layers cover LC Geography Core Unit 1.1?"
- **THEN** the agent returns the layer list

### Requirement: Cross-Reference Bindings in BIEP v3

The system SHALL materialise the cross-reference bindings in the BIEP v3
`lessonObjective` table as a new column `geo_layers: List[str]`.

#### Scenario: Cross-reference materialises
- **WHEN** the user invokes `mise run biep:v3:infrastructure`
- **THEN** the `lessonObjective` table SHALL have the `geo_layers` column populated

### Requirement: Marimo Curriculum Explorer

The system SHALL provide `notebooks/33_educational_geography.py` as a
curriculum-aware syllabus explorer.

#### Scenario: Explorer renders
- **WHEN** the user invokes `mise run notebook:geography`
- **THEN** the explorer SHALL render with 4 syllabus tabs