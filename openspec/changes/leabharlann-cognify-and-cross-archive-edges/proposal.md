# Leabharlann cognify + cross-archive edges (Cognee + FalkorDB)

## Why

After the leabharlann dlt sources (books / zotero / takeout) materialise
their BAML-extracted rows, the structured data is sitting in DuckLake
but **not connected to a knowledge graph**. The 3rd-party `oideachais/graph/`
module re-implements Graphiti in pure Python without connecting to the
`graphiti` compose stack on `arm1-oci`; the `cross_stage_cognify.py`
cognify is wired only for the 5-stage curriculum (Aistear → Tertiary).

This change adds a dedicated `leabharlann_cognify` asset group that:

  1. Cognifies the books / zotero / takeout corpora into Cognee datasets.
  2. Populates FalkorDB with **cross-archive edges**:
     - `GeminiReport -[:CITES]-> ZoteroPaper` (when an arxiv_id matches)
     - `UoGArtifact -[:TEACHES]-> ZoteroPaper` (when a module title matches a paper title)
     - `TakeoutDocument -[:CITES]-> GeminiReport` (when a takeout doc cites a Gemini report's URL)
  3. Exposes a new `oideachais/api/cross_archive_graph.py` FastAPI route
     `GET /cross-archive-graph/{query}` that runs a FalkorDB query and
     returns JSON for the web frontend.

## Impact

| Layer | Files | Description |
|:--|:--|:--|
| Dagster assets | `oideachais/dagster_defs/assets/leabharlann_cognify_assets.py` (new, 4 assets) | `cognify_leabharlann_books`, `cognify_leabharlann_zotero`, `cognify_leabharlann_takeout`, `cross_archive_edges` |
| Dagster registration | `oideachais/dagster_defs/definitions.py` (modified, +1 try/except + 1 line) | adds `LEABHARLANN_COGNIFY_ASSETS` to the asset list |
| Cognee adapter | `oideachais/cognee_integration/leabharlann_cognify.py` (new) | dedicated cognify adapter for leabharlann data classes (UoGArtifact, ZoteroPaper, GeminiReport) |
| FalkorDB client | `oideachais/api/cross_archive_graph.py` (new) | FastAPI route `GET /cross-archive-graph/{query}` for the web frontend |
| Cross-archive edge rules | `oideachais/cognify_rules/leabharlann_cross_archive.py` (new) | 3 edge rules: arxiv_id match, module_title match, URL match |

## Backlog

Phase 2 (not in this change): wire `cognee cognify` with
`graph_database_provider=falkordb` so the cognify step also populates
FalkorDB (currently we do the cognify via Cognee then the edge
population as a separate pass via the `cross_archive_edges` asset).
