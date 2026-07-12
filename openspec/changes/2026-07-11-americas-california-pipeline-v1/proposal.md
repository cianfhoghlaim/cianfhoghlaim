# 2026-07-11-americas-california-pipeline-v1

## Why

The
[`2026-07-11-commonwealth-pipeline-v1`](../2026-07-11-commonwealth-pipeline-v1/)
change ships the Commonwealth of Nations pipeline (5 pilot countries
+ Commonwealth Secretariat + Commonwealth Foundation). The user said:

> for the state of California as a subset example of America and the
> other example countries before adding others much later of countries
> in America of Brazil and Mexico and Venezuela

This change ships the Americas regional pipeline with California as
the US sub-state example. The pilot non-US countries are Brazil, Mexico,
and Venezuela (the user-named countries). All other American
countries are deferred to a much later change.

The change obeys the canonical
[`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md)
contract.

## Pilot geography

This change ships:

| Jurisdiction | Notes |
|:--|:--|
| `us_ca` | California — US sub-state example |
| `bra` | Brazil — Federative Republic of Brazil |
| `mex` | Mexico — United Mexican States |
| `ven` | Venezuela — Bolivarian Republic of Venezuela |
| `official/` | OAS + PAHO + IDB + CELAC (institutional layer) |

The 35+ remaining American countries are deferred to a much later
change.

## What changes

### 1. New umbrella spec `americas-california-pipeline`

Adds `openspec/specs/americas-california-pipeline/spec.md` as the
canonical spec for the Americas regional pipeline.

### 2. New DLT sources under `dlt/americas/`

```text
dlt/americas/
├── official/                                 # OAS + PAHO + IDB + CELAC
│   ├── oas.py
│   ├── paho.py
│   ├── idb.py
│   └── celac.py
├── us/us_ca/
│   ├── education/cde.py
│   ├── law/ca_leginfo.py
│   ├── medicine/cdph.py
│   ├── statistics/data_ca_gov.py
│   └── government/ca_gov.py
├── bra/
│   ├── education/mec.py
│   ├── law/planalto.py
│   ├── medicine/anvisa.py
│   ├── statistics/ibge.py
│   └── government/planalto_gov.py
├── mex/
│   ├── education/sep.py
│   ├── law/dof.py
│   ├── medicine/ssa.py
│   ├── statistics/inegi.py
│   └── government/gob_mx.py
└── ven/
    ├── education/mppeuct.py
    ├── law/tsj.py
    ├── medicine/mpps.py
    ├── statistics/ine.py
    └── government/gov_ve.py
```

### 3. New BAML extraction schemas under `baml/americas/`

```text
baml/americas/
├── _shared/
│   └── jurisdiction.baml
├── us_ca/
│   ├── education.baml
│   ├── law.baml
│   └── medicine.baml
├── bra/...
├── mex/...
└── ven/...
```

### 4. New CocoIndex v1 App

`cianfhoghlaim/cocoindex/americas_california_education_embedding.py`
embeds every Americas education row into the shared LanceDB table
`oideachais.americas.education_chunks`.

### 5. New Dagster L1 + L3 assets

```text
orchestration/defs/1_ingestion/americas/us/us_ca/<domain>/defs.yaml
orchestration/defs/1_ingestion/americas/bra/<domain>/defs.yaml
orchestration/defs/1_ingestion/americas/mex/<domain>/defs.yaml
orchestration/defs/1_ingestion/americas/ven/<domain>/defs.yaml
orchestration/defs/3_model_lifecycle/cocoindex_v1/americas_california_education/defs.yaml
```

### 6. New MotherDuck analytics

- 1 Dive: `americas_state_standards_crosswalk` — California state
  standards cross-referenced against Common Core + NGSS
- 1 daily Flight: `americas_daily_sync_flight`

## Dependencies

```yaml
Blocked by: 2026-07-11-global-region-source-contract-v1
Blocked by (soft):
  - 2026-07-11-commonwealth-pipeline-v1

Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-11-americas-california-pipeline-v1 --strict` passes
- `openspec/specs/americas-california-pipeline/spec.md` exists with at
  least 5 Requirements + 5 Scenarios
- The 25 per-nation DLT sources (5 jurisdictions × 5 domains) exist
- The 4 institutional DLT sources exist
- The 15 BAML files exist
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
- [`commonwealth-pipeline`](../../specs/commonwealth-pipeline/spec.md) —
  the Commonwealth counterpart
- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the seed instance
- `.agents/skills/dlt/SKILL.md` — DLT conventions
