# Spec delta: `cianfhoghlaim-pipeline`

This delta is part of the openspec change
`2026-08-01-lakehouse-and-reproducible-deploy-v1`. It adds 1
requirement that pins the canonical embedder env-var contract so
operators can swap embedders (e.g. for OCR-HTR experiments) without
rebuilding the dlt pipeline.

## ADDED Requirements

### Requirement: Embedder env-var contract

MUST export 2 embedder env vars via `secrets.env`. Every data-plane
stack (`lakehouse`, `cianfhoghlaim`, `dagster`, `motherduck`, `marimo`)
MUST set the following:

- `CIANFHOGHLAIM_EMBED_MODEL` (default `BAAI/bge-m3`)
- `CIANFHOGHLAIM_EMBED_DIM` (default `1024`)

The canonical CocoIndex v1 App entry point at
`cocoindex/_shared/_lifespan.py` reads these env vars at module
load (lines 99-108) and constructs the shared
`SentenceTransformerEmbedder(EMBED_MODEL)` for the 14 v1 Apps.

The dlt observability helper at
`dlt_sources/common/observability.py` reads these via the embedded
MLflow tracking URI; downstream BAML extractions + LanceDB
vector embeddings read them via the CocoIndex lifespan.

#### Scenario: an operator swaps the embedder for an OCR-HTR experiment

```
# Operator overrides in .env.local:
CIANFHOGHLAIM_EMBED_MODEL=sentence-transformers/all-mpnet-base-v2
CIANFHOGHLAIM_EMBED_DIM=768
# restarts the dagster webserver + dagster daemon
# the next materialisation uses the new embedder
# the old 1024-dim tables are preserved (legacy_embedding_dim=384)
```

#### Scenario: an operator reverts to the canonical embedder

```
# Operator unsets the overrides:
CIANFHOGHLAIM_EMBED_MODEL=           # unset → default
CIANFHOGHLAIM_EMBED_DIM=             # unset → default 1024
# restarts dagster
# materialisations resume using BAAI/bge-m3 (the canonical embedder)
```

## Why this matters

Today the canonical embedder (`BAAI/bge-m3` at 1024-dim) is hardcoded
in `cocoindex/_shared/_lifespan.py` + `orchestration/resources.py`.
Operators who want to swap embedders (for OCR-HTR experiments, for
cross-archive domain adaptation, for benchmarking) have no env knob
and must edit source code + redeploy. This requirement gives them the
canonical env knob + pins the canonical default.

It also gives the dlt observability helper a clean place to read the
embedder dimensions (via the same `CIANFHOGHLAIM_EMBED_DIM` env),
enabling the per-asset MLflow tags to carry the embedder dimension
metadata.