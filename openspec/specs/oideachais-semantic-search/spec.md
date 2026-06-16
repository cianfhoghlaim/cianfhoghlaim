# Oideachais Semantic Search Capability

## Purpose

`oideachais-semantic-search` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `oideachais/cocoindex_flows/` (8 v0 flows +
the new v1 leabharlann flows) and `oideachais/api/routes/search.py`. See
`docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the
project identity.

## Background

Vector-based curriculum and corpus search via LanceDB HNSW (BAAI/bge-m3 or
BAAI/bge-large-en-v1.5 for English-only, 1024-d) with a FastAPI route at
`/search/*`. The full leabharlann corpus (books, zotero, takeout) is
indexed via the v1 CocoIndex Apps in
`oideachais/cocoindex_flows/leabharlann_embedding.py`.

This spec was renamed from `semantic-search` to disambiguate it from any
future non-oideachais semantic-search surfaces (e.g. a `tuatha` or `croilar`
semantic-search surface would have its own spec).

## Requirements

### Requirement: Bilingual + English-only search

The system SHALL support both bilingual (multilingual) and English-only
semantic search via two distinct embedding models, selected at the
CocoIndex flow level.

#### Scenario: Bilingual model selection

- **GIVEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-m3`
- **WHEN** a query is embedded
- **THEN** the query is embedded with the BGE-M3 multilingual model (1024-d)
- **AND** the result includes the top-10 closest chunks across all corpora

#### Scenario: English-only model selection

- **GIVEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5`
- **WHEN** a query is embedded
- **THEN** the query is embedded with the BGE-large-en-v1.5 model (1024-d, English-tuned)
- **AND** the result includes the top-10 closest chunks across all corpora

### Requirement: Cross-corpus search

The system SHALL support cross-corpus search across the oideachais
leabharlann corpora (books, zotero, takeout) and the curriculum corpora
(NCCA, SEC, examinations).

#### Scenario: Cross-corpus query

- **GIVEN** a search request `q="handwritten text recognition for Irish"`
- **WHEN** the user issues a search via `/search/semantic`
- **THEN** the system returns the top-10 results from BOTH the zotero
  corpus and the leabharlann books corpus
- **AND** the result includes a `corpus` field per hit for routing

### Requirement: Search API

The system SHALL expose a FastAPI route at `/search/semantic` for
semantic search.

#### Scenario: API returns 200

- **GIVEN** a user issues `GET /search/semantic?q=irish+gaelic`
- **WHEN** the request is processed
- **THEN** the route returns HTTP 200 with `{"results": [...], "total": N}`
