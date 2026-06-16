## ADDED Requirements

The `oideachais-semantic-search` capability is renamed from
`semantic-search` to disambiguate it from any future non-oideachais
semantic-search surfaces. The full Requirements + Scenarios are in the
canonical spec at `openspec/specs/oideachais-semantic-search/spec.md`.

### Requirement: Bilingual + English-only search

The system SHALL support both bilingual (multilingual) and English-only
semantic search via two distinct embedding models.

#### Scenario: Bilingual model selection

- **WHEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-m3` is
  used
- **THEN** the query is embedded with the BGE-M3 multilingual model
  (1024-d)

#### Scenario: English-only model selection

- **WHEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5`
  is used
- **THEN** the query is embedded with the BGE-large-en-v1.5 model
  (1024-d, English-tuned)

### Requirement: Cross-corpus search

The system SHALL support cross-corpus search across the oideachais
leabharlann corpora and the curriculum corpora.

#### Scenario: Cross-corpus query

- **WHEN** a user issues a search via `/search/semantic`
- **THEN** the system returns the top-10 results from BOTH the
  zotero corpus and the leabharlann books corpus
