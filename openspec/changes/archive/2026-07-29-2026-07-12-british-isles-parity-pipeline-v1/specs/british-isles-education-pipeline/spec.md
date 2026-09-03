## ADDED Requirements

### Requirement: 7 British Isles nations reach Ireland parity

The system MUST extend the BIEP end-to-end pipeline (DLT + BAML +
CocoIndex v1 + Dagster + MotherDuck) to all 8 British Isles nations.
Per-nation parity requires:

- ≥1 per-subject DLT source per nation for the 6 priority subjects
  (Mathematics / Chemistry / Biology / Physics / English / Computing
  Science) — with bilingual or trilingual language partitioning
  matching the nation's official languages
- 1 CocoIndex v1 App per nation (L3 layer) embedding every per-subject
  row into a shared LanceDB table
- 1 MotherDuck Dive per nation surfacing the per-nation curriculum
  coverage matrix
- 1 daily MotherDuck Flight (`british_isles_daily_sync_flight`)
  backfilling the per-nation sources

#### Scenario: Scotland ships 6 per-subject DLT sources

- **WHEN** the British Isles parity change is materialised
- **THEN** the system MUST provide 6 DLT sources under
  `dlt/british_isles/scotland/education/subjects/` (one per subject)
- **AND** each source MUST partition on
  `language ∈ ("en", "gd")` (Scots Gaelic)
- **AND** the `scotland_education` CocoIndex v1 App MUST embed every
  per-subject row into
  `cianfhoghlaim.lc.scotland.<subject>.<level>_<language>`
- **AND** the `sct_curriculum_dive` MotherDuck Dive MUST surface the
  per-subject curriculum coverage matrix

### Requirement: 7 CocoIndex v1 Apps conform to R1–R4

Every per-nation CocoIndex v1 App MUST import
`from cianfhoghlaim.cocoindex._lifespan import shared_lifespan` and
declare the canonical ContextKeys (`EMBEDDER`, `LANCE_DB`). Every
App MUST use `BAAI/bge-m3` (1024-d multilingual embedder) + the
LanceDB HNSW index.

#### Scenario: The Wales CocoIndex v1 App materialises

- **WHEN** the `wales_education` CocoIndex v1 App materialises
- **THEN** it MUST embed every Welsh per-subject row into the shared
  LanceDB table `cianfhoghlaim.lc.wales.<subject>.<level>_<language>`
- **AND** it MUST honour the R1–R4 conformance contract (the
  `cocoindex_v1_conformance` App MUST report `passed=True` for it)

## Cross-references

- [`cross-region-pipeline`](../cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../european-union-official-language-pipeline/spec.md) —
  the EU institutional counterpart (24-language reference)
- [`european-nations-ukraine-pipeline`](../european-nations-ukraine-pipeline/spec.md) —
  the EU nations counterpart
- [`commonwealth-pipeline`](../commonwealth-pipeline/spec.md) —
  the Commonwealth counterpart
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the seed instance of the contract
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- `docs/agents/british_isles_endpoint_health_audit.md` —
  the Phase 1 endpoint snapshot
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
