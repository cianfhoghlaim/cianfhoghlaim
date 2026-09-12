## ADDED Requirements

### Requirement: Leabharlann cognify covers 6 sub-corpora (updated scope)

The `cianfhoghlaim-cognify-knowledge-graph` capability's Leabharlann
cognify dataset SHALL cover 6 sub-corpora (the 3 original
books + zotero + takeout corpora, plus the 3 new additions: UoG,
gemini deep research, and academic history) rather than the
originally-documented 3 sub-corpora.

#### Scenario: All 6 sub-corpora are indexed in the cognify dataset

- **WHEN** the cognify cron runs
- **THEN** all 6 Leabharlann sub-corpora SHALL be ingested into
      the `cianfhoghlaim_leabharlann` Cognee dataset
- **AND** the FastAPI route `GET /cross-archive-graph/{query}`
      SHALL return edges from all 6 sub-corpora

### Requirement: Cross-archive FalkorDB edges have documented ownership boundaries

The cross-archive FalkorDB edges SHALL declare their ownership
boundary explicitly: edges from `cross_archive_biep_edges.py` (the
BIEP-owned edges) vs edges from `leabharlann_culture_heritage.py`
(the Leabharlann-owned edges) vs edges from
`leabharlann_official_media.py` (the official-media-owned edges)
vs edges from `leabharlann_authors_archive.py` (the authors-archive-
owned edges).

#### Scenario: BIEP → official-media edge (owned by cognify change)

- **GIVEN** a `LCSubject` whose `subject_code` matches an
      `OfficialMediaSource`'s `topic_tags` exactly
- **WHEN** the `build_lc_subject_announced_by_query` function runs
      (owned by `cross_archive_biep_edges.py`)
- **THEN** a `(:LCSubject)-[:ANNOUNCED_BY]->(:OfficialMediaSource)`
      edge is created in FalkorDB