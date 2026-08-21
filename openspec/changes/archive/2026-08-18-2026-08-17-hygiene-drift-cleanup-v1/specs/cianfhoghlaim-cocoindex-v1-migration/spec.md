# cocoindex-v1-migration

## ADDED Requirements

### Requirement: CocoIndex v1.x pin and `deps=` memoization discipline

The system SHALL pin CocoIndex to **`>=1.0.20,<2.0.0`** (current
stable as of 2026-08-11 per `https://github.com/cocoindex-io/cocoindex/releases`).

The previous pin (`>=1.0.14,<1.0.8,!=1.0.8`) was set when v1.0.14
was the latest; v1.0.15-v1.0.20 have shipped since (BigQuery/Snowflake/
Valkey target connectors, LiveMap, rate limiting, batched target
writes, zvec FTS fields, preserve target invalidation in v1.0.20).

Additionally, every `@coco.fn(memo=True)` decorator SHALL declare
its module-level prompt strings + model names via the `deps=`
parameter (introduced in v1.0.x per
`cocoindex-io/cocoindex#1836`).

#### Scenario: A `@coco.fn(memo=True)` site has a module-level prompt constant

- **GIVEN** `cocoindex_flows/european_nations_cross/education_embedding.py:30`
  declares `IRISH_LC_PROMPT_V1 = "..."` and uses it at line 87 inside
  `@coco.fn(memo=True)`
- **WHEN** `IRISH_LC_PROMPT_V1` changes
- **THEN** CocoIndex MUST invalidate the dependent memos (because
  `deps=(IRISH_LC_PROMPT_V1,)` is declared on the `@coco.fn` decorator)
- **AND** the next pipeline run MUST re-execute the function

#### Scenario: A `@coco.fn` site has no module-level deps

- **GIVEN** a `@coco.fn(memo=True)` that uses inline string literals
  only (no module-level constants)
- **WHEN** the function body changes
- **THEN** CocoIndex MUST invalidate the dependent memos (the
  source-code change is the only invalidation signal)

#### Scenario: A `@coco.fn` site uses `deps=` for prompt strings

- **GIVEN** a `@coco.fn(memo=True, deps=(BGE_M3_MODEL,))` declaration
  where `BGE_M3_MODEL` is a module-level constant
- **WHEN** `BGE_M3_MODEL` changes from `"BAAI/bge-m3"` to
  `"BAAI/bge-large-en-v1.5"`
- **THEN** CocoIndex MUST invalidate the dependent memos
- **AND** the marimo audit notebook MUST show the new model ID in
  the per-call provenance

#### Scenario: Pin upgrade from v1.0.14 to v1.0.20

- **WHEN** `mise.toml` (via the `bun run cocoindex update --pip` task)
  refreshes the CocoIndex venv
- **THEN** all 196 CocoIndex files in `cocoindex/**/*.py` MUST
  AST-parse cleanly under v1.0.20
- **AND** the canonical `cocoindex_flows/european_nations/_factory.py`
  factory pattern MUST continue to work (tested by
  `mise run cic:cocoindex:v1-conformance`)
- **AND** no breaking change introduced by v1.0.15-v1.0.20 affects
  our factory pattern (the v1.0 changelog confirms new
  connectors/features are purely additive)