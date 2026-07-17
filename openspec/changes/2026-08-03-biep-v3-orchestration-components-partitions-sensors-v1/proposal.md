# 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1

## Why

The BIEP v3 batch shipped 5 generic jurisdiction pipelines (Ireland /
England / SCT+WLS+NI / Crown Dependencies) covering ~1,560 cohorts.
The Dagster orchestration surface needs to be wired to these pipelines
but several components are missing:

- 4 Component classes (`BIEPSubjectComponent`,
  `JuniorCycleSubjectComponent`, `EnglandBoardSubjectComponent`,
  `EnglandCrossBoardComparatorComponent`) referenced by the 5
  `defs.yaml` files but never implemented
- 5 registry-change sensors (NCCA / SQA / WJEC / CCEA / JCQ) that
  should fire when the official sources update the spec
- The 2-axis `scope × year` partition (per the Phase 1 spec delta)
- The `EnsembledExtractor.extract()` wiring into the 4 generic asset
  modules (the `+0` placeholder in the BAML call stubs)

This is the B3 change. It lives in the **cianfhoghlaim repo** (Dagster
orchestration).

## What changes

### 1. Create the 4 missing Component classes

- `orchestration/components/biep_subject_component.py` (new) — the
  canonical BIEP v3 component
- `orchestration/components/junior_cycle_subject_component.py` (new)
- `orchestration/components/england_board_subject_component.py` (new)
- `orchestration/components/england_cross_board_comparator_component.py`
  (new)

### 2. Create the 5 registry-change sensors

- `orchestration/sensors/ncca_registry_sensor.py` (new) — Ireland NCCA
- `orchestration/sensors/sqa_registry_sensor.py` (new) — Scotland SQA
- `orchestration/sensors/wjec_registry_sensor.py` (new) — Wales WJEC
- `orchestration/sensors/ccea_registry_sensor.py` (new) — NI CCEA
- `orchestration/sensors/jcq_registry_sensor.py` (new) — England (AQA + OCR + Edexcel)

### 3. Implement the 2-axis `scope × year` partition

- `orchestration/partitions_v2.py` — add the canonical
  `scope` × `year` partition where `scope` encodes
  `<jurisdiction>__<stage>__<subject>__<board>__<qualification_level>__<language>`

### 4. Wire `EnsembledExtractor.extract()` into the 4 generic asset modules

Replace the `+0` placeholder in the 4 `generic_*.py` files with a
real `EnsembledExtractor.extract()` call.

## Dependencies

```yaml
Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Blocked by (soft): 2026-08-02-biep-v3-motherduck-flights-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `dg list sensors | grep -E "(ncca|sqa|wjec|ccea|jcq)_registry"` returns 5 sensors
- `dg list assets | grep -E "(ireland_|england_|sct_wls_ni_|crown_dependencies_)"` returns 16 assets
- `dg check yaml` passes
- `openspec validate 2026-08-03-biep-v3-orchestration-components-partitions-sensors-v1 --strict` passes

## Cross-references

- `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` (the canonical 4-path ensemble)
- `dlt/british_isles/_cross/registry_api.py` (the registry)
- `orchestration/defs/2_materials/{ireland,england,sct_wls_ni,crown_dependencies}_education/generic_*.py` (consumers)
- `.agents/skills/dagster/SKILL.md` — the 5-layer component convention