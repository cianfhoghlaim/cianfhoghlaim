# Change: pipeline-computer_science-v1 (BIEP v3 Ireland LC Computer Science Pipeline)

## Why

The Ireland Leaving Certificate (LC) Computer Science curriculum is the
BIEP v3 M1 milestone cohort 6/12. Currently the BIEP v3
umbrella spec (`british-isles-education-pipeline-v3`) calls for 12
Ireland-LC cohorts in M1 (6 subjects × 2 languages, minus 1 for
Gaeilge which is ga-only), and `pipeline-mathematics-v1` has
shipped the canonical Mathematics pipeline (CocoIndex v1 App + BAML
fallback + LanceDB target + per-subject pytest). This change
sisters the Computer Science pipeline — same template, parameterised for
Computer Science.

## What changes

- **Computer Science CocoIndex v1 App** (NEW module
  `cocoindex_flows/british_isles/ireland/education/lc/computer_science.py`):
  conforms to R1-R4 (imports `shared_lifespan` + `LANCE_DB` +
  `EMBEDDER` from `....._shared._lifespan`; `app = coco.App(...)`
  at module scope; 2 × `@coco.fn(...)` decorators), reads from
  `leaving_certificate/computer_science/<lang>/`, embeds via the canonical
  BAAI/bge-m3 1024-d embedder, writes to `cianhoghlaim.ireland.leaving_cycle.computer_science.{level}_{language}_chunks`.

- **Computer Science per-subject pytest** (NEW file
  `tests/biep_parity_lc/test_computer_science.py`): 4 tests that exercise
  the full load → embed → store → query pipeline against a 3-row
  Computer Science fixture (HL/OL/FL snippets).

- **openspec delta to `british-isles-education-pipeline-v3/spec.md`**:
  the new "Per-subject Computer Science pipeline (BIEP v3 M1 cohort
  6/12)" Requirement.

## Out of scope

- The other 5 LC subjects — they ship in their own sibling
  changes (`pipeline-mathematics-v1` through `pipeline-computer-science-v1`).
- The Dagster asset wiring for Computer Science — tracked separately by
  the British Isles Dagster integration change.
- Live network tests against MotherDuck / LanceDB namespace —
  the pytest uses an in-memory substitute.
- Remediating the kcg-runtime-inert-layers defects (defect #3
  BAML client generation, etc.) — tracked in
  `pipeline-british-isles-synthesis-v1`.
