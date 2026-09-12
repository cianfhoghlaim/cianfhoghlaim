# Change: pipeline-mathematics-v1 (BIEP v3 Ireland LC Mathematics Pipeline)

## Why

The Ireland Leaving Certificate (LC) Mathematics curriculum is the
flagship LC subject — the highest-volume content surface (2 levels
× 2 languages × ~50 syllabus topics = ~200 cohorts per the BIEP v3
spec), and the most-frequently-queried across the British Isles
Education Pipeline.

Currently the BIEP v3 umbrella spec (`british-isles-education-pipeline-v3`)
calls for 12 Ireland-LC cohorts in M1 (6 subjects × 2 languages,
minus 1 for Gaeilge which is ga-only), but the per-subject wiring
is only partially in place:

- `cocoindex_flows/subjects/lc_subject_embedding.py` provides the
  *parameterised* CocoIndex v1 App (one app, six subjects) — but
  it doesn't pin subject-specific BAML extraction (the
  `ExtractLCSyllabusMathematics` function) and doesn't have a
  per-subject pytest.
- `cocoindex_flows/biep_parity/ireland_lc_factory.py` builds the
  11 cohort Apps (6 subjects × 2 langs, minus 1) via the BIEP v3
  factory pattern, but it tries to `from baml_client.baml_client
  import b` which fails (per the kcg-runtime-inert-layers memory,
  defect #3 — `baml-cli generate --from baml_src` fails on duplicate
  class definitions in `baml_src/_shared/templates/`).
- No openspec change documents the per-subject wiring at all —
  the BIEP v3 spec only refers to the umbrella.

This change builds the canonical per-subject Mathematics pipeline:
CocoIndex v1 App + BAML fallback + LanceDB target + per-subject
pytest, with the 5 other LC subjects following in sibling changes
(`pipeline-chemistry-v1`, `pipeline-geography-v1`, etc.).

## What changes

- **Mathematics CocoIndex v1 App** (NEW module
  `cocoindex_flows/british_isles/ireland/education/lc/mathematics.py`):
  conforms to R1-R4 (imports `shared_lifespan` + `LANCE_DB` +
  `EMBEDDER` from `....._shared._lifespan`; `app = coco.App(...)`
  at module scope; 2 × `@coco.fn(...)` decorators), reads from
  `leaving_certificate/mathematics/<lang>/`, embeds via the
  canonical BAAI/bge-m3 1024-d embedder, writes to
  `cianhoghlaim.ireland.leaving_cycle.mathematics.<level>_<lang>_chunks`.

- **Per-subject shared scaffolding** (NEW module
  `cocoindex_flows/british_isles/ireland/education/lc/_shared.py`):
  the canonical 6-row `LCSubjectSpec` table (Mathematics →
  Computer Science, dependency order), the `pure_python_embed`
  helper (deterministic numpy substitute for BGE-M3 used by the
  pytests), the `python_baml_fallback_extract` helper (regex-based
  fallback for the BAML extraction function used when defect #3
  blocks `baml_client/` from regenerating), the `chunk_text`
  splitter (2000-char / 200-overlap), and the `build_subject_fixture`
  fixture builder (3 rows of mock LC content per subject).

- **Mathematics per-subject pytest** (NEW file
  `tests/biep_parity_lc/test_mathematics.py`): 9 tests that
  exercise the full load → embed → store → query pipeline against
  a 3-row fixture (HL/OL/FL snippets).

- **Per-subject pytest suite** (NEW package `tests/biep_parity_lc/`):
  `conftest.py` provides the `InMemoryLanceTable` substitute +
  brute-force cosine similarity query + per-subject fixture
  helpers; the 5 sibling subject pytests follow in
  `pipeline-chemistry-v1` through `pipeline-computer-science-v1`.

- **openspec delta to `british-isles-education-pipeline-v3/spec.md`**:
  the new "Per-subject Mathematics pipeline (BIEP v3 M1 cohort
  1 of 12)" Requirement + the "BAML fallback for per-subject
  pipelines" Scenario.

## Out of scope

- The other 5 LC subjects (Chemistry, Geography, English, Gaeilge,
  Computer Science) — they ship in sibling changes
  (`pipeline-chemistry-v1` … `pipeline-computer-science-v1`).
- The Dagster asset wiring for Mathematics — that lands in the
  `orchestration/defs/2_materials/` integration, tracked
  separately by the British Isles Dagster integration change.
- Live network tests against MotherDuck / LanceDB namespace /
  Gemma-4 / Qwen3-VL — the pytest uses an in-memory substitute.
- Remediating the kcg-runtime-inert-layers defects (defect #3
  BAML client generation, etc.) — those are tracked in the
  `pipeline-british-isles-synthesis-v1` change.
