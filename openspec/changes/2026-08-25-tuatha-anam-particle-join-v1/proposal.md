# Change: tuatha-anam-particle-join (v1)

## Why

The cross-source ANAM particle joiner is the deliverable that actually
feeds the British Isles Formative Assessment MMO design surface. Without
it, the 3 source pipelines produce columns of data but the Celtic
deity ↔ ANAM particle mapping stays unused.

## What changes

- New `cocoindex_flows/tuatha_media_intel/ingestors/anam_particles.py`
  CocoIndex v1 App (already shipped in the
  `2026-08-25-tuatha-media-intel-pipeline-v1` change; this is the
  formal spec).
- New `baml_src/tuatha_media_intel.baml` `MapToAnamParticle` function
  (already shipped; this is the formal spec).
- New `baml_src/tuatha_media_intel.baml` `AnamParticle` class
  (already shipped; this is the formal spec).
- New Lance table `cianfhoghlaim.tuatha.anam_particles`.

## Impact

- Affected specs: `openspec/specs/tuatha-anam-particles/spec.md` (new).
- Affected Dagster assets: `anam_particles_v1`.
- Affected CocoIndex flows: `tuatha_anam_particles` (R1–R4 compliant).

## Out of scope

- Image generation (the 2D particle asset generation is downstream;
  this change only produces the metadata + color + motion).
- The Celtic MMO game client (gated on this corpus being populated).

## Verification

1. `cocoindex update tuatha_anam_particles` succeeds end-to-end.
2. The Lance table `cianfhoghlaim.tuatha.anam_particles` has rows.
3. The `notebooks/tuatha_anam_dashboard.py` Join tab shows the rows.
4. The RAGAS `ragas_anam_color_anchor` asset_check passes.
