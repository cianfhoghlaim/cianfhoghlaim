# Spec Delta: celtic-asset-generation

## ADDED Requirements

### Requirement: `media_descriptors` input alongside `subject_assets` and `language_assets`

The system SHALL extend the 4-pipeline asset generation
surface (`official_documents` / `subject_assets` /
`language_assets` / `exporters`) with a 5th input pipeline
`media_descriptors`.

The `media_descriptors` input SHALL consume the
`media_descriptors` LanceDB table (built by the
`media-intel-corpus` spec) and SHALL feed the descriptors
into the 4 existing exporters:

- `exporters/pixi.py` (NEW) — Pixi.js 2D renderer for the
  Celtic-Elemental MMO client (the primary renderer per
  ADR-0020)
- `exporters/phaser.py` (NEW) — Phaser 3 alternative 2D
  renderer (the fallback)
- `exporters/canvas2d.py` (NEW) — pure Canvas2D +
  tsparticles fallback for low-end iOS devices
- `exporters/{babylon,godot,unity,unreal}.py` (EXISTING) —
  unchanged; the 3D exporters remain but are no longer the
  default output

The Celtic motifs (pale, ogham, gaelic typography) SHALL be
derived from the public-domain ogham-stone records (built by
`2026-09-08-ogham-celtic-stones-pipeline-v1`) + the
Tuatha Dé Danann cycle (built by
`2026-09-01-celtic-mythology-content-system-v1`), NOT from
the rejected Pent-Elemental Cosmology.

#### Scenario: A descriptor is converted to a Pixi.js sprite atlas

- **GIVEN** a `MediaDescriptor` row exists in the
  `media_descriptors` table with
  `medium = "comic"`, `work = "FF #570"`, `palette =
  ["#1a1a1a", "#ff6b35", "#ffd23f"]`, `vfx_vocabulary.
  particle_class = "spark"`
- **WHEN** the `exporters/pixi.py` exporter runs
- **THEN** a Pixi.js sprite atlas is generated with the
  3-colour palette + the spark particle archetype
- **AND** the atlas is written to
  `stedding/asset_out/pixi/ff_570_sprite.json` +
  the PNG companion
- **AND** the descriptor's `shippable_art_path` is
  updated to the asset path
- **AND** the `derivation_class` is updated to
  `"derivative"` (no longer `description_only`)
- **AND** the original FF #570 panel image is NEVER
  included in the asset output (the `shippable: false`
  invariant is preserved)
