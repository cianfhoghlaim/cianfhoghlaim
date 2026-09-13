## ADDED Requirements

### Requirement: CISP DLT Source

The system SHALL provide a DLT source at `dlt/language/cisp/cisp.py` that
ingests the CISP (Celtic Inscribed Stones Project) data from UCL. The
source SHALL yield ≥1,200 inscribed stone records.

#### Scenario: CISP DLT source loads 1,200+ stones
- **WHEN** the user invokes `mise run dlt:cisp`
- **THEN** the source SHALL ingest ≥1,200 records from the CISP API

### Requirement: Megalithic Portal DLT Source

The system SHALL provide a DLT source at `dlt/language/megalithic_portal/megalithic_portal.py`
that ingests the Megalithic Portal data. The source SHALL yield ≥30,000
megalithic site records.

#### Scenario: Megalithic Portal DLT source loads 30,000+ sites
- **WHEN** the user invokes `mise run dlt:megalithic`
- **THEN** the source SHALL ingest ≥30,000 records

### Requirement: BAML Extractors for CISP Stones + Ogham Inscriptions

The system SHALL provide 2 BAML functions in `baml/celtic/mythology.baml`
(extended from change 1): `ExtractCISPStone`, `ExtractOghamInscription`.

#### Scenario: ExtractCISPStone recognise aicme
- **WHEN** the user invokes `ExtractCISPStone` on the CISP record for stone CW-001 with inscription "B L N F S"
- **THEN** the function returns a `CISPStone` Pydantic model with `aicme="beith"`, `letter_set=["B","L","N","F","S"]`

### Requirement: Convex Tables for Ogham Stones + Anam Particles + Visits

The system SHALL provide 3 new Convex tables: `ogham_stones.ts`,
`anam_particles.ts`, `stone_visits.ts`.

#### Scenario: Convex schema deploys
- **WHEN** the user invokes `mise run convex:dev`
- **THEN** the schema SHALL deploy with all 3 new tables

### Requirement: Ogham Stone Agent

The system SHALL provide `agents/meaisinfhoghlaim/educational/ogham_stone_agent.py`
as an ADK agent with 6 tools. The agent SHALL be registered in `AGENT_REGISTRY`
with `framework="adk"`, `litellm_routing_key="ogham"`.

#### Scenario: Ogham agent queries a stone
- **WHEN** the user invokes `ogham_stone_agent` with "Tell me about the Kilcachrine Ogham stone"
- **THEN** the agent returns a `CISPStone` Pydantic model

#### Scenario: Ogham agent finds nearby stones
- **WHEN** the user invokes `ogham_stone_agent` with "Find Ogham stones near 51.86°N, -10.27°E within 10km"
- **THEN** the agent invokes the spatial grid utility and returns a list of CISP stones within the 10km radius

### Requirement: Spatial Grid Utility

The system SHALL provide `notebooks/_shared/spatial_grid.py` implementing
the Bucket Key Algorithm, Haversine proximity, and 9-bucket Moore
neighborhood query.

#### Scenario: Bucket key for a coordinate
- **WHEN** the user invokes `bucket_key(lat=51.86, lon=-10.27)`
- **THEN** the function returns the unique integer key

#### Scenario: 9-bucket Moore neighborhood query
- **WHEN** the user invokes `find_nearby_stones(stones_table, lat=51.86, lon=-10.27, radius_km=10)`
- **THEN** the function returns ≤9 candidate stones

### Requirement: CocoIndex v1 Embedding for Ogham Stones

The system SHALL provide `cocoindex/biep_parity/ogham_stones_embedding.py`
as a CocoIndex v1 App conforming to R1-R4.

#### Scenario: 1,200+ Ogham stones embedded
- **WHEN** the user invokes `mise run biep:v3:ogham`
- **THEN** the CocoIndex App SHALL successfully materialise ≥1,200 rows