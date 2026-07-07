## ADDED Requirements

### Requirement: HNSW Indexes on LanceDB Tables
Every LanceDB table in the leabharlann full-stack demo SHALL
have an HNSW index built on the `vector` column at
materialisation time. The 3 helper functions in
`oideachais.lancedb.indexing` (`build_hnsw_index`,
`build_ivf_pq_index`, `optimize_index`) SHALL be importable
and SHALL follow the canonical 2026-06 LanceDB 0.15 API.

#### Scenario: The leabharlann_books table is materialised
- **WHEN** the `leabharlann_books_app` v1 CocoIndex App
  materialises
- **THEN** `build_hnsw_index(table, column="vector")` is called
  on the resulting LanceDB table
- **AND** the HNSW index has `ef_construction=100` and `M=16`

### Requirement: Vector Search with HNSW
The oideachais semantic search endpoint SHALL use the HNSW
indexes for `leabharlann_books`, `leabharlann_zotero`, and
`leabharlann_takeout` searches. The 3 search handlers
(`search_leabharlann_books`, `search_leabharlann_zotero`,
`search_leabharlann_takeout`) SHALL use the HNSW-accelerated
query path.

#### Scenario: A user searches the leabharlann_books table
- **WHEN** a user calls `search_leabharlann_books("Celtic
  studies", limit=10)`
- **THEN** the search uses the HNSW index and returns 10
  results in < 100ms

## REMOVED Requirements

### Requirement: No Vector Index
**Reason**: The LanceDB 0.15 default (`index=None`) is
suboptimal for the leabharlann full-stack demo's 117 Zotero
+ 64 Takeout + 40 gaeilge/aigne books + 7 aigne books. The
HNSW index provides 10-100x speedup at the cost of ~10%
recall loss.
**Migration**: All 5 leabharlann tables now have HNSW indexes
built at materialisation time. The HNSW index parameters
(`ef_construction=100, M=16`) are the defaults recommended
by the LanceDB 10B-scale blog.
