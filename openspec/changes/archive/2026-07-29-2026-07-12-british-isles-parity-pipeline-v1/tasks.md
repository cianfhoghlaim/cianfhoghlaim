# Tasks: 2026-07-12-british-isles-parity-pipeline-v1

## 1. Per-subject DLT sources (4 nations × 6 subjects = 24)

For each of Scotland, Wales, England, Northern Ireland:

- [ ] 1.x Create
  `dlt/british_isles/<nation>/education/subjects/<subject>.py`
  with the canonical `@dlt.resource(name="<subject>_syllabus",
  write_disposition="merge", primary_key=["url", "language"])`
  pattern + `USE_LOCAL_SCRAPES` honour + per-nation language set

## 2. Per-nation CocoIndex v1 Apps + L3 defs

- [ ] 2.1 Scotland: `dlt/british_isles/scotland/education/embedding.py`
  + `orchestration/defs/3_model_lifecycle/cocoindex_v1/scotland_education/defs.yaml`
- [ ] 2.2 Wales: same pattern
- [ ] 2.3 England: same pattern
- [ ] 2.4 Northern Ireland: same pattern
- [ ] 2.5 IoM: `crown/isle_of_man/education/embedding.py` + L3 defs
- [ ] 2.6 Jersey: `crown/jersey/education/embedding.py` + L3 defs
- [ ] 2.7 Guernsey: `crown/guernsey/education/embedding.py` + L3 defs

Each App uses `BAAI/bge-m3` (1024-d, multilingual) + LanceDB HNSW
+ imports `from cianfhoghlaim.cocoindex._lifespan import shared_lifespan`
(R1–R4 conformance).

## 3. Per-nation BAML extraction schemas

For each of Scotland, Wales, England, Northern Ireland, IoM, Jersey,
Guernsey:

- [ ] 3.x Create
  `baml/education/<nation>/<domain>.baml` with
  `Extract<Nation><Domain>Document(nation, language, text)` that
  wraps the existing `ExtractCrossNationSpec` /
  `ExtractCurriculumSyllabus` BAML functions.

## 4. MotherDuck Dives + daily Flight

For each of Scotland, Wales, England, Northern Ireland, IoM, Jersey,
Guernsey:

- [ ] 4.x Create
  `motherduck/dives/<nation>_curriculum_dive.py`
  + register in
  `motherduck/flights/config.yaml` (the per-nation daily
  Flight).

## 5. Dagster L1 defs (per-subject partitions)

For each of Scotland, Wales, England, Northern Ireland × 6 subjects:

- [ ] 5.x Create
  `orchestration/defs/1_ingestion/british_isles/<nation>/education/subjects/<subject>/defs.yaml`

## 6. Crown Dependency per-island DLT split

- [ ] 6.1 Split
  `dlt/british_isles/isle_of_man/education/channel_islands.py` into
  per-island sources
- [ ] 6.2 Split
  `dlt/british_isles/jersey/education/channel_islands.py` into
  per-island sources
- [ ] 6.3 Split
  `dlt/british_isles/guernsey/education/channel_islands.py` into
  per-island sources

## 7. Spec deltas

- [ ] 7.1 ADDED Requirements on `british-isles-education-pipeline/spec.md`
  for the per-nation parity layer
- [ ] 7.2 MODIFIED delta on `cross-region-pipeline/spec.md` adding a
  cross-reference to the new per-nation instances
- [ ] 7.3 MODIFIED delta on `cianfhoghlaim-pipeline/spec.md` adding a
  cross-reference

## 8. Validate

- [ ] 8.1 `openspec validate 2026-07-12-british-isles-parity-pipeline-v1 --strict` passes
- [ ] 8.2 All 24 per-subject DLT sources AST-parse
- [ ] 8.3 All 21 BAML files AST-parse
- [ ] 8.4 All new Dagster L1 defs.yaml files YAML-parse
- [ ] 8.5 `dg check yaml` passes
- [ ] 8.6 `mise run lint:skills` still passes (53/53)

## 9. Commit + push

- [ ] 9.1 Single commit with message
  `feat(biep): parity for Scotland/Wales/England/NI/Crown — per-subject DLT + 7 CocoIndex v1 Apps + 7 Dives + daily Flight`
- [ ] 9.2 `git push origin main`
