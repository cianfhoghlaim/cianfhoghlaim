# 2026-07-11-commonwealth-pipeline-v1

## Why

The
[`2026-07-11-european-nations-ukraine-pipeline-v1`](../2026-07-11-european-nations-ukraine-pipeline-v1/)
change ships the EU nations + Ukraine national layer. After the
EU institutional layer + the EU nations + Ukraine layer, the next
region in the global-expansion plan is the **Commonwealth of Nations**
(56 member states, 2.4 billion people, 19 of which recognise the
British monarch as head of state).

The user said:

> after we do the extensive implementation of that we also now want to
> create a plan to do the same for the Commonwealth and for the state
> of California as a subset example of America

This change ships the canonical Commonwealth pipeline (one
`dlt/commonwealth/<iso3>/` subtree per member state) and the
institutional Commonwealth layer (`dlt/commonwealth/official/`).
California (the Americas example) ships in the parallel
`2026-07-11-americas-california-pipeline-v1` change.

The change obeys the canonical
[`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md)
contract (the Phase 0 lockdown).

## Pilot countries

This change ships the 5 priority Commonwealth nations:

| ISO 3166-1 alpha-3 | Country | Notes |
|:--|:--|:--|
| `aus` | Australia | Federal system (6 states + 2 territories); ACARA / NESA / TGA |
| `can` | Canada | Federal + 10 provinces + 3 territories; bilingual EN/FR |
| `nzl` | New Zealand | NZQA + Ministry of Education |
| `ind` | India | NCERT + CBSE + NMC |
| `zaf` | South Africa | DBE + Umalusi + SAHPRA |

The remaining 51 Commonwealth members are deferred to a follow-on
change.

## What changes

### 1. New umbrella spec `commonwealth-pipeline`

Adds `openspec/specs/commonwealth-pipeline/spec.md` as the canonical
spec for the Commonwealth pipeline.

### 2. New DLT sources under `dlt/commonwealth/`

```text
dlt/commonwealth/
├── official/                              # Commonwealth Secretariat + Commonwealth Foundation
│   ├── commonwealth_secretariat.py
│   └── commonwealth_foundation.py
├── aus/
│   ├── education/acara.py
│   ├── law/federal_register_legislation.py
│   ├── medicine/tga.py
│   ├── statistics/abs.py
│   └── government/gov_au.py
├── can/
│   ├── education/cmec.py
│   ├── law/federal_laws.py
│   ├── medicine/health_canada.py
│   ├── statistics/statcan.py
│   └── government/canada_ca.py
├── nzl/
│   ├── education/nzqa.py
│   └── ...
├── ind/
│   └── ...
└── zaf/
    └── ...
```

### 3. New BAML extraction schemas under `baml/commonwealth/`

```text
baml/commonwealth/
├── _shared/
│   └── commonwealth_jurisdiction.baml
├── aus/
│   ├── education.baml
│   ├── law.baml
│   └── medicine.baml
├── can/...
├── nzl/...
└── ...
```

### 4. New CocoIndex v1 App

`cocoindex/commonwealth_education_embedding.py` —
embeds the 5 pilot countries' education rows into the shared LanceDB
table `oideachais.commonwealth.education_chunks`.

### 5. New Dagster L1 + L3 assets

```text
orchestration/defs/1_ingestion/commonwealth/<iso3>/<domain>/defs.yaml
orchestration/defs/3_model_lifecycle/cocoindex_v1/commonwealth_education/defs.yaml
```

### 6. New MotherDuck analytics

- 1 Dive: `commonwealth_curriculum_matrix` — cross-nation coverage
  matrix for the 5 pilot countries
- 1 daily Flight: `commonwealth_daily_sync_flight`

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-european-nations-ukraine-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-11-commonwealth-pipeline-v1 --strict` passes
- `openspec/specs/commonwealth-pipeline/spec.md` exists with at
  least 5 Requirements + 5 Scenarios
- The 25 DLT sources (5 countries × 5 domains) exist + AST-parse
- The 15 BAML files (5 countries × 3 domains) exist + AST-parse
- The 1 CocoIndex v1 App conforms to R1–R4
- `dg check yaml` passes on the new defs.yaml
- `mise run lint:skills` still passes
- Push target: `origin/main`

## Cross-references

- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract
- [`european-union-official-language-pipeline`](../../specs/european-union-official-language-pipeline/spec.md) —
  the EU institutional counterpart
- [`european-nations-ukraine-pipeline`](../../specs/european-nations-ukraine-pipeline/spec.md) —
  the EU nations counterpart
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the seed instance of the contract
- `.agents/skills/dlt/SKILL.md` — DLT conventions
