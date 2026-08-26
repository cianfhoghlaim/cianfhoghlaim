# Change: tuatha-lance-tables (v1)

## Why

The capture pipeline writes to 4 Lance tables, all under the
`cianfhoghlaim.tuatha.*` namespace. They follow the BIEP v3 convention
(snake_case schema, 1024-d BAAI/bge-m3 embedder, hybrid BM25 + vector
search with RRF reranking). The tables are the canonical destination
for the British Isles Formative Assessment MMO design surface.

## What changes

- 4 new tables in the Lance Namespace:
  - `cianfhoghlaim.tuatha.hades.boons`
  - `cianfhoghlaim.tuatha.comic.particles`
  - `cianfhoghlaim.tuatha.gba.magic`
  - `cianfhoghlaim.tuatha.anam_particles`

## Impact

- Affected spec: `openspec/specs/tuatha-lance/spec.md` (new).

## Out of scope

- The 24+1 BIEP tables (already shipped separately).
- The Lance Namespace registration tooling (tracked in issue #142).

## Verification

1. `mise run lance:list --prefix cianfhoghlaim.tuatha` shows the 4 tables.
2. A smoke-test insert succeeds for each table.
3. Hybrid search (vector + BM25 + RRF) returns a result for each table.
