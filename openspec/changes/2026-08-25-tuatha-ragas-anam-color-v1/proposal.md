# Change: tuatha-ragas-anam-color (v1)

## Why

The ANAM particle pipeline is the first KCG pipeline that produces
visual artifacts (color + motion). The quality gate is custom: it needs
to assert that the derived ANAM color falls within a ΔE ≤ 8 of the
source color, so we can detect when the BAML join hallucinates.

The standard RAGAS metrics (`faithfulness`, `answer_relevancy`,
`context_precision`, `context_recall`) are insufficient because they
measure text-based faithfulness, not perceptual color drift.

## What changes

- New RAGAS metric `anam_color_anchor` registered in
  `scripts/ragas_metrics.py`.
- New Dagster asset_check `ragas_anam_color_anchor` in
  `orchestration/defs/2_materials/tuatha_media_intel.py`.
- New helper `delta_e` in `notebooks/tuatha_anam/helpers/__init__.py`.

## Impact

- Affected spec: `openspec/specs/tuatha-ragas/spec.md` (new).
- Affected DAG: the `tuatha_quality` asset group.

## Out of scope

- Generalizing the metric to other visual pipelines (the
  OpenSpec pattern stays specific to ANAM for now).

## Verification

1. The RAGAS metric is registered and visible via
   `scripts/ragas_metrics.py list`.
2. The Dagster asset_check passes on a synthetic anam_particles table.
3. The ΔE computation matches the reference implementation
   (verified via `scripts/ragas_metrics.py test anam_color_anchor`).
