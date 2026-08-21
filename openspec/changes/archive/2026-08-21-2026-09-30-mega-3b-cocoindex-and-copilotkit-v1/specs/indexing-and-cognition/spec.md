## ADDED Requirements

### Requirement: cocoindex_query_api integration helper

The system SHALL provide `cocoindex_flows/_shared/cocoindex_query_api.py`
that exposes every CocoIndex App as a `search(query, top_k=5) ->
List[Chunk]` Python closure.

The helper wraps `lancedb.Table.search` with the canonical
`BAAI/bge-m3` embedder.

#### Scenario: Every CocoIndex App exposes a search closure

- **GIVEN** the 47 BIEP CocoIndex Apps + the 4 infrastructure CocoIndex
  Apps + the 40 european_nations Apps
- **WHEN** the operator runs
  `python -c "from cocoindex_flows._shared.cocoindex_query_api import get_search; print(get_search('ireland_lc_mathematics_embedding'))"`
- **THEN** the helper returns a callable that runs the canonical
  LanceDB query against the BIEP v3 table

### Requirement: CocoIndex entity resolution (CO.9)

The system SHALL use CocoIndex's `ops.entity_resolution` module
(LlmPairResolver + ResolvedEntities) for the cross-jurisdiction
CocoIndex Apps.

#### Scenario: LlmPairResolver dedupes cross-jurisdiction NCCA LO codes

- **GIVEN** the cross-jurisdiction BIEP CocoIndex Apps
- **WHEN** the App encounters the same LO code across 2 jurisdictions
  (e.g., `LC-CHEM-LO-001` and `AL-CHEM-LO-001`)
- **THEN** the `LlmPairResolver` deduplicates them into a canonical
  LO code (e.g., `CIANFHOGHLAIM-CHEMISTRY-LO-001`)