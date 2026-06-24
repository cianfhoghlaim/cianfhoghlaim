## ADDED Requirements

### Requirement: Graphiti 0.5 Client
The oideachais cognify pipeline SHALL use the real
`graphiti_core` 0.5 client (with the `falkordb_lite` fallback
for local dev) backed by the FalkorDB compose stack. The
hand-rolled `oideachais/graph/temporal.py` implementation
SHALL be deleted.

#### Scenario: The cross_stage_cognify pipeline runs
- **WHEN** the `cross_stage_cognify` Dagster asset materialises
- **THEN** it calls `graphiti_client.add_episode()` to persist
  the 8 cross-stage edges to the FalkorDB graph
- **AND** the edges are queryable via a Cypher query against
  the `falkordb.cianfhoghlaim.ie:6379` endpoint

#### Scenario: A developer runs locally without the FalkorDB stack
- **WHEN** the `falkordb.cianfhoghlaim.ie` compose stack is
  unreachable
- **THEN** the `graphiti_client` falls back to the
  `FalkorDBLite` embedded mode (the `falkordb_lite` Python
  package introduced in 2026-05)

### Requirement: FalkorDB Compose Stack
The oideachais cognify pipeline SHALL use the FalkorDB compose
stack (running at `falkordb.cianfhoghlaim.ie:6379`) for the
production deployment. The `falkordb_lite` embedded mode is
ONLY used for local development when the compose stack is
unreachable.

#### Scenario: A pipeline runs in production
- **WHEN** the `cross_stage_cognify` Dagster asset materialises
  in the production environment
- **THEN** the `graphiti_client` connects to
  `falkordb.cianfhoghlaim.ie:6379` (the canonical FalkorDB
  compose stack)

## REMOVED Requirements

### Requirement: Hand-Rolled Temporal Knowledge Graph
**Reason**: Replaced by the real `graphiti_core` 0.5 client
backed by the FalkorDB compose stack.
**Migration**: Delete `oideachais/graph/temporal.py`. Update
`oideachais/cognee_integration/cross_stage_cognify.py` to use
`oideachais.graph.graphiti_client`.
