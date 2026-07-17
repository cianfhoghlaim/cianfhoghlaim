# 2026-07-12-british-isles-parity-pipeline-v1

## Why

Ireland is the only British Isles nation with a full BIEP-style
end-to-end pipeline (6 priority LC subjects × 2 languages + 7 CocoIndex
v1 Apps + 4 MotherDuck Dives + 1 daily Flight). The other 7 nations
(Scotland, Wales, England, Northern Ireland, Isle of Man, Jersey,
Guernsey) have thin scaffolds — typically 1-2 sources per domain,
no per-subject depth, no CocoIndex v1 embedders, no MotherDuck
Dives.

This change brings the other 7 nations up to Ireland-level parity:

- **Per-subject curriculum depth** (Mathematics / Chemistry / Geography /
  English / History / Computing Science — the 6 subjects that
  actually exist in every British Isles jurisdiction) with bilingual
  or trilingual language partitioning.
- **Per-domain DLT sources** (education, law, medicine, statistics,
  government) where the on-disk scaffold is sparse.
- **CocoIndex v1 embedders** (one per nation) for the L3 layer.
- **MotherDuck Dives + daily Flights** (one per nation).
- **Dagster L1 + L3 defs.yaml** using the canonical
  `CelticIngestionComponent`.

Blocked by
[`2026-07-12-british-isles-endpoint-recovery-v1`](../2026-07-12-british-isles-endpoint-recovery-v1/)
(we cannot scaffold live crawls against the 11 broken endpoints).

## What changes

### 1. Per-nation DLT scaffolding

For each of Scotland, Wales, England, Northern Ireland:

- 6 per-subject DLT sources under `dlt/british_isles/<nation>/education/subjects/<subject>.py`
  (Mathematics / Chemistry / Biology / Physics / English / Computing Science,
  with History for SCO + WAL where it's a separate awarding body subject)
- 1 BAML extraction function per subject
- 1 Dagster L1 defs.yaml per source

For the 3 Crown Dependencies (IoM / Jersey / Guernsey):

- The existing single `channel_islands.py` is split into per-island
  DLT sources: `iom_education.py`, `jersey_education.py`,
  `guernsey_education.py` (keeping the cross-island `channel_islands.py`
  as a re-export for backward compat).
- 1 CocoIndex v1 App + 1 Dagster L3 defs.yaml per Crown Dependency.

### 2. Per-nation CocoIndex v1 Apps

`dlt/british_isles/<nation>/` CocoIndex v1 Apps (one per nation,
per the existing `lc_subjects` + `ie_law` pattern):

- `scotland_education_embedding.py` + Dagster L3 defs.yaml
- `wales_education_embedding.py` + Dagster L3 defs.yaml
- `england_education_embedding.py` + Dagster L3 defs.yaml
- `northern_ireland_education_embedding.py` + Dagster L3 defs.yaml
- `iom_education_embedding.py` + Dagster L3 defs.yaml
- `jersey_education_embedding.py` + Dagster L3 defs.yaml
- `guernsey_education_embedding.py` + Dagster L3 defs.yaml

Every App conforms to the R1–R4 contract (imports
`shared_lifespan` + the canonical ContextKeys).

### 3. Per-nation MotherDuck Dives + daily Flight

- 7 new Dives (one per nation): `sct_curriculum_dive`,
  `wls_curriculum_dive`, `eng_curriculum_dive`, `ni_curriculum_dive`,
  `iom_curriculum_dive`, `jey_curriculum_dive`, `ggy_curriculum_dive`.
- 1 new daily Flight: `british_isles_daily_sync_flight`.

### 4. Per-nation BAML

Per-nation BAML files at `baml/education/<nation>/<domain>.baml`:
- `sct/{education,law,medicine}.baml`
- `wls/{education,law,medicine}.baml`
- `en/{education,law,medicine}.baml`
- `ni/{education,law,medicine}.baml`
- `iom/{education,law}.baml`
- `jey/{education,law}.baml`
- `ggy/{education,law}.baml`

Each file declares `Extract<Nation><Domain>Document(nation, language, text)`
that wraps the existing `ExtractCrossNationSpec` / `ExtractCurriculumSyllabus`
BAML functions with the per-nation output class.

## Dependencies

```yaml
Blocked by: 2026-07-12-british-isles-endpoint-recovery-v1
Blocked by (soft): 2026-07-15-pipeline-architecture-clarity-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-12-british-isles-parity-pipeline-v1 --strict` passes
- 24 per-subject DLT sources exist (4 nations × 6 subjects) + AST-parse
- 7 CocoIndex v1 Apps exist + conform to R1–R4
- 21 BAML files exist + AST-parse
- 7 MotherDuck Dives + 1 daily Flight exist + YAML-parse
- 30+ new Dagster L1 defs.yaml files YAML-parse
- `dg check yaml` passes on the new defs
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`british-isles-education-pipeline`](../british-isles-education-pipeline/spec.md) —
  the flagship BIEP spec
- [`cianfhoghlaim-pipeline`](../cianfhoghlaim-pipeline/spec.md) —
  the parent pipeline
- [`cianfhoghlaim-baml-schemas`](../cianfhoghlaim-baml-schemas/spec.md) —
  the BAML cluster taxonomy
- [`cianfhoghlaim-marimo-dashboards`](../cianfhoghlaim-marimo-dashboards/spec.md) —
  the downstream marimo surface
- `docs/agents/british_isles_endpoint_health_audit.md` —
  the Phase 1 endpoint snapshot
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
