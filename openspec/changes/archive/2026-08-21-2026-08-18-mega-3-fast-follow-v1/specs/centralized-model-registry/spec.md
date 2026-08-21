## ADDED Requirements

### Requirement: cocoindex_query_api integration helper

The system SHALL provide a `cocoindex_query_api` integration helper at
`cocoindex_flows/_shared/cocoindex_query_api.py` that exposes every
CocoIndex App as a `search(query, top_k=5) -> List[Chunk]` Python
closure. The closure wraps `lancedb.Table.search` with the canonical
`BAAI/bge-m3` embedder.

The helper replaces the 47 ad-hoc `lancedb.connect(CIANFHOGHLAIM_LANCEDB_URL)`
calls scattered across notebooks, agents, and web apps.

#### Scenario: Every CocoIndex App exposes a search closure

- **GIVEN** the 47 BIEP CocoIndex Apps + the 4 infrastructure CocoIndex Apps (upstream_blog_monitor, upstream_api_surface, docs_skills_consolidation, codebase_indexing)
- **WHEN** the operator runs `python -c "from cocoindex_flows._shared.cocoindex_query_api import get_search; print(get_search('ireland_lc_mathematics_embedding'))"`
- **THEN** the helper returns a callable that runs the canonical
  LanceDB query against the BIEP v3 table
  `cianhoghlaim.education.ireland.lc.mathematics.chunks`

#### Scenario: All 47 ad-hoc lancedb.connect calls are replaced

- **WHEN** `mise run lint:cocoindex-query-api-coverage` runs
- **THEN** all 47 ad-hoc `lancedb.connect(...)` calls MUST be replaced
  with `from cocoindex_flows._shared.cocoindex_query_api import get_search`
- **AND** the lint returns `OK: 47/47 connect calls replaced`