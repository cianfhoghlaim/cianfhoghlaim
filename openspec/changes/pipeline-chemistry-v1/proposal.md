# Change: pipeline-chemistry-v1 (BIEP v3 Ireland LC Chemistry Pipeline)

## Why

The Ireland Leaving Certificate (LC) Chemistry curriculum is the
BIEP v3 M1 milestone cohort 2/12. Currently the BIEP v3
umbrella spec (`british-isles-education-pipeline-v3`) calls for 12
Ireland-LC cohorts in M1 (6 subjects × 2 languages, minus 1 for
Gaeilge which is ga-only), and `pipeline-mathematics-v1` has
shipped the canonical Mathematics pipeline (CocoIndex v1 App + BAML
fallback + LanceDB target + per-subject pytest). This change
sisters the Chemistry pipeline — same template, parameterised for
Chemistry.

## What changes

- **Chemistry CocoIndex v1 App** (NEW module
  `cocoindex_flows/british_isles/ireland/education/lc/chemistry.py`):
  conforms to R1-R4 (imports `shared_lifespan` + `LANCE_DB` +
  `EMBEDDER` from `....._shared._lifespan`; `app = coco.App(...)`
  at module scope; 2 × `@coco.fn(...)` decorators), reads from
  `leaving_certificate/chemistry/<lang>/`, embeds via the canonical
  BAAI/bge-m3 1024-d embedder, writes to `cianhoghlaim.ireland.leaving_cycle.chemistry.{level}_{language}_chunks`.

- **Chemistry per-subject pytest** (NEW file
  `tests/biep_parity_lc/test_chemistry.py`): 4 tests that exercise
  the full load → embed → store → query pipeline against a 3-row
  Chemistry fixture (HL/OL/FL snippets).

- **openspec delta to `british-isles-education-pipeline-v3/spec.md`**:
  the new "Per-subject Chemistry pipeline (BIEP v3 M1 cohort
  2/12)" Requirement.

## Out of scope

- The other 5 LC subjects — they ship in their own sibling
  changes (`pipeline-mathematics-v1` through `pipeline-computer-science-v1`).
- The Dagster asset wiring for Chemistry — tracked separately by
  the British Isles Dagster integration change.
- Live network tests against MotherDuck / LanceDB namespace —
  the pytest uses an in-memory substitute.
- Remediating the kcg-runtime-inert-layers defects (defect #3
  BAML client generation, etc.) — tracked in
  `pipeline-british-isles-synthesis-v1`.
