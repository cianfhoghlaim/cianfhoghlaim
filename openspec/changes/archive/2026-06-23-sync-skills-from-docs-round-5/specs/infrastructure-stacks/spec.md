# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Embedding pipeline as a first-class infrastructure concern

The system SHALL treat the embedding pipeline (BGE-M3
inference + batching + HNSW lifecycle) as a first-class
infrastructure concern, with canonical patterns documented in
`.agents/skills/embedding-pipeline/SKILL.md`.

#### Scenario: Embedding pipeline bootstraps a new corpus

- **GIVEN** a new corpus at `stedding/ingest_queue/<corpus>/`
  (e.g. a fresh NCCA PDF dump)
- **WHEN** the `embedding_pipeline_bootstrap` Dagster asset
  runs
- **THEN** the `BatchedEmbeddingService` is invoked with
  `MIN_EMBEDDING_BATCH_SIZE = 100` (the KCG production rule
  for 100× performance)
- **AND** the embeddings are persisted to LanceDB via
  `lancedb.mount_table_target`
- **AND** the HNSW index is dropped and recreated above 50k
  rows

### Requirement: Monorepo infrastructure (bun + uv + turbo)

The system SHALL use a polyglot monorepo (bun + uv + turbo)
managed via the Inner/Outer loop pattern (mise = inner
loop, Dagger = outer loop), documented in
`.agents/skills/monorepo/SKILL.md`.

#### Scenario: New workspace member added

- **GIVEN** a new quadrant (e.g. `meaisínfhoghlaim/`) needs
  to be added to the monorepo
- **WHEN** the developer runs `mise run monorepo:add-member
  meaisínfhoghlaim`
- **THEN** the workspace is updated in `package.json`
  (TypeScript) and `pyproject.toml` (Python)
- **AND** the turbo pipeline is updated in `turbo.json`
- **AND** the mise polyglot toolchain is updated in `mise.toml`
- **AND** `dagger call test` runs the new member's test suite
  hermetically

## REMOVED Requirements

(None.)
