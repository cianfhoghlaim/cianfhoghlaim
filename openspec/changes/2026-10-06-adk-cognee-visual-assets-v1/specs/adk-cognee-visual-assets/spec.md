# adk-cognee-visual-assets Specification

## Purpose
`adk-cognee-visual-assets` is the contract that connects the ADK 2
Pillar 3 deep-research pipelines (aistear + primary + JC + SC + tertiary)
to the Cognee knowledge graph. Each pipeline writes its briefing as
a `LearningEpisode` record, extracts NER entities via BAML, and links
those entities to assets via `CITED_IN` edges.

This lets the 8 subject agents answer questions like "show me the
assets related to Julius Caesar" by traversing the Cognee graph
(entities → edges → assets).

Per the 2026-10-06-adk-cognee-visual-assets-v1 saga change (Plan 6 of
`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## ADDED Requirements

### Requirement: Briefing → Cognee LearningEpisode

The system MUST provide a `link_briefing_to_cognee(briefing, subject, language)`
function that writes the Pillar 3 briefing as a Cognee `LearningEpisode`
record. The episode MUST carry:
- `episode_id` (deterministic: sha256(subject + language + briefing headline)[:16])
- `subject` (the NCCA subject)
- `language` (en | ga)
- `headline` (the briefing headline)
- `sections` (the list of section summaries)
- `provenance` (the source pipeline + the model used)

#### Scenario: Pillar 3 aistear brief written to Cognee
- **GIVEN** the aistear_deep_research pipeline produces a briefing on "The 4 Aistear themes support wellbeing"
- **WHEN** `link_briefing_to_cognee(briefing, subject="aistear", language="en")` is called
- **THEN** a `LearningEpisode` row is created in Cognee with `episode_id="a8b7c6..."` + `subject="aistear"` + `headline="The 4 Aistear themes support wellbeing"`
- **AND** the call returns `{"episode_id": "a8b7c6...", "created": true, "stub": false}`

### Requirement: NER entity extraction via BAML

The system MUST provide an `extract_entities(briefing)` BAML function
that returns an `EntityKnowledgeGraph` with the entities + relationships
extracted from the briefing. The entities MUST be classified into one
of: `PERSON`, `PLACE`, `CONCEPT`, `EVENT`, `WORK`, `ORGANIZATION`.

#### Scenario: Entities extracted from a history briefing
- **WHEN** `extract_entities(briefing)` runs on a history briefing about "Julius Caesar was assassinated by Brutus on the Ides of March"
- **THEN** the returned `EntityKnowledgeGraph` includes:
  - 1 `PERSON`: "Julius Caesar"
  - 1 `PERSON`: "Brutus"
  - 1 `EVENT`: "Assassination of Julius Caesar"
  - 1 `DATE`: "Ides of March"
  - 1 `RELATIONSHIP`: "Brutus ASSASSINATED Julius Caesar"

### Requirement: CITED_IN edge linking (entities → assets)

The system MUST provide a `link_entities_to_assets(entities, subject)`
function that creates `CITED_IN` edges in Cognee connecting each entity
to the asset table for the subject. The edge MUST carry:
- `entity_id`
- `entity_name`
- `entity_type`
- `asset_id` (the asset UUID in the Lakehouse table)
- `subject`
- `created_at` (ISO 8601 timestamp)

#### Scenario: Entity linked to asset via CITED_IN edge
- **WHEN** `link_entities_to_assets(entities, subject="history")` runs with the entities from the Julius Caesar briefing
- **THEN** a `CITED_IN` edge is created between each entity + the 4 history assets in `media.image_gen_chunks`
- **AND** the call returns `{"edges_created": 4, "stub": false}`

### Requirement: Marimo visual graph dashboard

The system MUST provide a marimo dashboard at
`notebooks/dashboards/cognee_asset_graph.py` that:
1. Queries Cognee for entities + CITED_IN edges (via the Cognee client)
2. Renders the graph (entity nodes + asset nodes + edges)
3. Lets the operator click an entity to expand the linked assets
4. Shows the Cognee knowledge graph statistics (entity count + edge count + per-entity-type breakdown)

#### Scenario: Marimo dashboard renders the Julius Caesar graph
- **WHEN** the operator opens the dashboard
- **THEN** the graph shows 2 PERSON nodes (Julius Caesar + Brutus) + 1 EVENT node (Assassination) + 4 CITED_IN edges to history assets
- **AND** clicking "Julius Caesar" expands the 4 linked history assets (with their palettes + validation scores)
