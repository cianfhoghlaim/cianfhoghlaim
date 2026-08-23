# Spec Delta: media-intel-corpus

## Purpose

`media-intel-corpus` is the canonical surface for ingesting 5
classes of external media (comics, prose, moving media, games,
official) into the Cianfhoghlaim platform, distilling a
medium-agnostic `MediaDescriptor` schema from each via the
existing VLM fleet, and feeding the resulting descriptors
into the asset generation + the Celtic-Elemental MMO client.

The capability is the **content spine** for the
Tuatha-Elemental canon: every external source (a Hickman comic
panel, a Wheel-of-Time prose passage, an ATLA animation frame,
a Hades boon, an NCCA syllabus PDF) is reduced to the same 7
descriptor axes and stored in the `media_descriptors` LanceDB
table. The `shippable: false` invariant ensures no copyrighted
asset is ever re-rendered or upscaled; the descriptor
*vocabulary* is the only thing that flows forward to the
shippable asset-generation pipeline.

## ADDED Requirements

### Requirement: 5-class source registry with 5 v1 sources + 5 v2 stubbed sources + 3 v3 future sources

The system SHALL provide a `media_intel_sources` DLT resource
that lists every external source in the registry. The v1
sources SHALL be:

1. **Class A — Comics**: Jonathan Hickman's Marvel run
   (Fantastic Four #570-611 + FF #1-23 + Future Foundation
   + Avengers 2012 + New Avengers 2013 → Infinity → Secret
   Wars 2015 + House of X / Powers of X → X-Men 2019 +
   Krakoa-era crossovers)
2. **Class B — Prose**: The Wheel of Time (the 0-pixel
   control group)
3. **Class C — Moving media**: Avatar: The Last Airbender,
   The Legend of Korra, the Aang-film continuity
4. **Class D — Games**: Hades 1 + Hades 2 + World of Warcraft
   (all locally installed) + Golden Sun (GBA, via `romm`) +
   Pokémon (GB/GBA) + DragonBox (iOS) + Duolingo (iOS) +
   Bejeweled (iOS)
5. **Class E — Official**: NCCA (Ireland) + SEC /
   examinations.ie + DfE (England) + SQA (Scotland) + WJEC
   (Wales) + DESC (Isle of Man) + Met Éireann + Met Office +
   OSi + Ordnance Survey + Wikipedia + CELT (UCC) + Dúchas /
   Gaois

The v2 stubbed sources SHALL be: Grant Morrison `Batman
Incorporated`, Peter J. Tomasi `Super Sons`, Geoff Johns
`Green Lantern`, Valiant `Harbinger`, Kieron Gillen `The
Power Fantasy`.

The v3 future sources SHALL be: Crown Dependencies education,
Cornish / Kernow curriculum, full Alba CfE coverage.

#### Scenario: A new source is added to the registry

- **GIVEN** a new external source is declared in
  `dlt_sources/media/<class>/<work>/source.yaml`
- **WHEN** the `media_intel_sources` DLT resource materialises
- **THEN** a new row is appended with `class`, `work`,
  `firecrawl_plan`, `vlm_primary`, `baml_functions`,
  `lance_table`, `ducklake_schema`, `licence_summary`,
  `legal_notes`
- **AND** the system SHALL refuse to materialise if the
  declared `firecrawl_plan` is unavailable
- **AND** the system SHALL refuse to materialise if the
  declared `vlm_primary` is not a `MODEL_REGISTRY`
  family+role resolution

### Requirement: Medium-agnostic `MediaDescriptor` schema with 7 axes

The system SHALL provide a BAML-typed `MediaDescriptor`
schema at `baml_src/media/media_descriptor.baml` with the
following 7 descriptor axes, each as a typed BAML class:

1. `power_event` (actor, element, source, trigger,
   scale_tier, cost, consequence, counter)
2. `visual_grammar` (composition, panel_or_shot_type,
   motion_lines, camera, silhouette, focal_hierarchy)
3. `palette` (dominant_hex, accent_hex, emissive_hex,
   per_element_palette, contrast_strategy)
4. `vfx_vocabulary` (particle_class, density,
   trail_behavior, dissipation, light_interaction)
5. `narrative_beat` (arc_position, beat_significance)
6. `transferability` (in_game_mechanic, anam_cost,
   palette_token, particle_effect)
7. `provenance` (rights_holder, licence,
   derivation_class, shippable, shippable_art_path)

The schema SHALL codegen to Pydantic v2 + Zod + Convex table
+ DuckLake DDL per the `centralized-schema-registry` spec.

#### Scenario: A Hickman comic panel is processed

- **GIVEN** the `retro_marvel_hickman_ff` DLT source
  materialises an FF #570 panel image
- **WHEN** the `ExtractComicDescriptor` BAML function runs
  with `vlm_primary = qwen3-vl-8b` (resolved via
  `MODEL_REGISTRY.resolve(family="ocr_vision", role="media_descriptor")`)
- **THEN** a `MediaDescriptor` record is written to the
  `media_descriptors` LanceDB table with all 7 axes populated
- **AND** the record's `shippable` field SHALL be `False`
- **AND** the record's `licence` field SHALL be
  `"fair-use-description"`
- **AND** the record's `provenance.rights_holder` SHALL
  reference Marvel Comics (the rights holder)

### Requirement: Source-type plugin contract with declarative `source.yaml`

The system SHALL enforce a `source.yaml` manifest schema at
`dlt_sources/media/<class>/<work>/source.yaml` for every
source. The manifest SHALL declare:

- `id`, `medium`, `work`
- `firecrawl_plan` (one of `plan_a_keyless`,
  `plan_b_paid_basic`, `plan_c_full`)
- `vlm_primary` + `vlm_secondary` (each via
  `MODEL_REGISTRY` family+role)
- `baml_functions` (a list of function names from
  `baml_src/media/<medium>_descriptor.baml`)
- `lance_table` (the target LanceDB table)
- `ducklake_schema` (the target DuckLake schema)
- `licence_summary` (one of `CC-BY-SA-4.0`, `CC0`,
  `OFL-1.1`, `fair-use-description`)
- `shippable_default` (MUST be `false` for v1)
- `legal_notes` (a free-text note)

#### Scenario: A new source is added with config only (no code)

- **GIVEN** a new external work is identified
- **WHEN** the operator adds a `source.yaml` file at
  `dlt_sources/media/<class>/<work>/source.yaml`
- **THEN** the system SHALL auto-generate the DLT source
  stub + the BAML function stub from the manifest
- **AND** the system SHALL refuse the new source if
  `shippable_default: true` and `licence_summary` is not
  in the approved list
- **AND** the system SHALL refuse the new source if any
  field is missing

### Requirement: Firecrawl 3-plan ladder with auto-detect of keyless tier

The system SHALL provide 3 Firecrawl plan configurations
(`firecrawl_plan_a_keyless`, `firecrawl_plan_b_paid_basic`,
`firecrawl_plan_c_full`) and SHALL auto-detect the keyless
tier (no `FIRECRAWL_API_KEY` env var) at process start.

- **Plan A — keyless** SHALL use only
  `firecrawl_search`, `firecrawl_scrape`, `firecrawl_parse`
  (per `agents/meaisinfhoghlaim/firecrawl_mcp/client.py:KEYLESS_TOOLS`).
- **Plan B — paid basic** SHALL additionally enable
  `firecrawl_map`, `firecrawl_crawl`, `firecrawl_batch_scrape`,
  `firecrawl_monitor_create`, `firecrawl_monitor_check`.
- **Plan C — full** SHALL additionally enable
  `firecrawl_agent`, `firecrawl_interact`,
  `firecrawl_research_search_papers`, `firecrawl_research_inspect_paper`,
  `firecrawl_developer_search`, `firecrawl_ask`.

Every `firecrawl_*` call SHALL be logged to
`cianfhoghlaim.firecrawl_meta.scrapes` per the
`firecrawl-corpus-and-portals` spec invariant #1.

#### Scenario: A source declares Plan A and the key is absent

- **GIVEN** `source.yaml:firecrawl_plan = "plan_a_keyless"`
- **AND** the `FIRECRAWL_API_KEY` env var is empty
- **WHEN** the DLT source materialises
- **THEN** only `firecrawl_search` + `firecrawl_scrape` +
  `firecrawl_parse` are used
- **AND** any attempt to use a Plan B or Plan C tool SHALL
  raise a `FirecrawlPlanUnavailable` error
- **AND** the `stedding/ingest_queue/USE_LOCAL_SCRAPES` cache
  is consulted as a substitution for `firecrawl_map` and
  `firecrawl_crawl`

#### Scenario: Plan B is gated by the budget asset

- **GIVEN** `source.yaml:firecrawl_plan = "plan_b_paid_basic"`
- **AND** the `firecrawl_budget_asset` (per
  `firecrawl-corpus-and-portals` invariant #6) reports the
  daily budget is exhausted
- **WHEN** the DLT source attempts a `firecrawl_crawl` call
- **THEN** the call SHALL be refused with a
  `FirecrawlBudgetExceeded` error
- **AND** the source SHALL fall back to Plan A

### Requirement: Legal capture boundary with auto-allowed + audit-required classes

The system SHALL enforce a legal capture boundary:

- **Auto-allowed (v1)**: Hades 1 + Hades 2 + World of Warcraft
  (locally installed); Golden Sun + Pokémon (owned ROMs via
  `romm`); DragonBox + Duolingo + Bejeweled (owned iOS).
- **Audit-required (v2)**: every other ROM, every other
  Game Boy Advance / NES / SNES / Genesis / PS1 title; every
  iOS game not auto-allowed; every Steam / Epic / GOG title
  beyond Hades + WoW.
- **Never captured**: copyrighted comic panel images (only
  the textual descriptor); animation frame stills from
  Netflix / Paramount / Disney (only the textual descriptor);
  game screenshots beyond the libretro headless output (those
  go to `stedding/ingest_queue/retro/` per the
  `retro-game-design-catalogue` spec, NEVER to the shippable
  asset output).

The system SHALL refuse any DLT source materialisation that
violates the boundary.

#### Scenario: A new PS1 title is added to romm

- **GIVEN** a new PS1 ROM is added to the `romm` library
- **WHEN** the `retro_library_watcher` Dagster sensor (per
  `retro-game-design-catalogue` spec) detects the new ROM
- **THEN** the ROM SHALL be added to the audit-required class
- **AND** the DLT source SHALL refuse materialisation until
  the operator runs the `legal_audit.sh` script and grants
  explicit per-title permission

### Requirement: Cross-medium comparison CocoIndex v1 App

The system SHALL provide a `cross_medium_compare` CocoIndex v1
App at `cocoindex_flows/media_intel/cross_medium_compare.py`
that mounts a `media_descriptors_cross_medium_lance` table
with the multihop search surface.

The App SHALL index a sample of descriptors from each of the
5 v1 source classes and SHALL surface the *consistent visual
grammar* across classes (e.g. "which element's visual language
is most consistent across ATLA + WoT prose + Hickman?").

#### Scenario: An agent asks a cross-medium question

- **GIVEN** the `media_descriptors` table has at least 100
  rows from each of the 5 v1 source classes
- **WHEN** an agent calls
  `multihop_search("What visual grammar is shared between
  Wheel of Time's saidin and ATLA's fire-bending?")`
- **THEN** the App SHALL return at least 3 descriptor rows
  (one from WoT prose, one from ATLA, one from Hickman)
  with a similarity score > 0.7
- **AND** the response SHALL be logged to Langfuse with the
  `media_intel.cross_medium` trace tag
