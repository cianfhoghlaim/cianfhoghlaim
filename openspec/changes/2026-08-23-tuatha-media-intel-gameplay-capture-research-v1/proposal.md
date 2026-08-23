# Change: Tuatha Media-Intel + Gameplay-Capture Research v1

## Why

The Cianfhoghlaim platform has the official-document ingestion
spine for NCCA Ireland (the 41-file
`dlt_sources/british_isles/ireland/education/` tree, the 12
NCCA subject BAML extractions in
`baml_src/british_isles/ireland/education/marking/`, the
per-subject ADK agents in `agents/tuatha/<slug>_agent.py` with 5
tools each, and the per-subject AG-UI event types in
`web/apps/oideachais/src/lib/ag-ui/<stage>/<subject>.ts`).

What is **not** there yet is the **reference-corpus spine** for
the **Celtic-MMO design** that the change proposes to *defer*
but not *build*:

- The Jonathan Hickman Marvel run (FF #570-611 → FF #1-23 →
  Future Foundation → Avengers 2012 → New Avengers 2013 → Infinity
  → Secret Wars 2015 → House of X / Powers of X → X-Men 2019 →
  Krakoa crossovers) — the structural model for the
  "world-as-evolving-system" writing.
- The Wheel of Time — the 0-pixel control group, the
  saidar/saidin/Tel'aran'rhiod/One Power magic-system
  architecture, the explicit analogue for the gender-agnostic
  channelling contract.
- Avatar: The Last Airbender + The Legend of Korra + the Aang-film
  continuity — the 4+1 element world + the motion-vocabulary
  model.
- Hades 1 + Hades 2 (owned) + World of Warcraft (owned) + Golden
  Sun (owned ROM via `romm` + libretro) + Pokémon (owned ROM via
  `libretro`) — the boon-grant / class design / Djinn-Psynergy
  / type-chart design surface.
- The 5 v1 BAML extractor functions in `baml_src/media/` for
  the medium-agnostic `MediaDescriptor` schema.
- The 4 docker stacks the existing `retro-game-design-catalogue`
  + `celtic-asset-generation` specs reference aspirationally
  (`comfyui/`, `libretro-retroarch/`, `sam3-server/`,
  `sam3d-objects-server/`).

This change **gathers the reference corpus** + the 4 docker
stacks + the per-medium BAML extractor pipeline. The Celtic-MMO
**design itself** (which elements, what the boons look like,
which ogham stones map to which portals, the 4+1 element
binding, whether anamcara is NPC-shaped or NFT-shaped, whether
the world overlay uses Tel'aran'rhiod or SpacetimeDB or Convex,
the iOS delivery vehicle, the 2D particle renderer choice) is a
downstream change gated on this corpus.

## What this change does

**The change has 3 layers:**

### Layer 1 — The 5-class source registry (the research spine)

The 5 v1 source classes:

- **A — Comics**: the Jonathan Hickman Marvel run
- **B — Prose**: The Wheel of Time (the 0-pixel control)
- **C — Animation**: Avatar: The Last Airbender + The Legend
  of Korra + the Aang-film continuity
- **D — Games**: Hades 1 + 2 + World of Warcraft + Golden Sun
  (GBA via `romm`) + Pokémon (GB via `romm`) — local-capture only
- **E — Official**: 36 official records across 3 sub-buckets
  (the educational body sub-bucket + the government sub-bucket
  + the departments sub-bucket)

The 5 v2 stubbed sources (Morrison `Batman Incorporated`, Tomasi
`Super Sons`, Johns `Green Lantern`, Valiant `Harbinger`, Gillen
`The Power Fantasy`) are stubbed in the plugin-registry manifest
only. The 9 Celtic-history research topics (Tuatha Dé Danann,
Irish mythology, Celtic mythology, Celtic law, Brehon law, Aran
Islands, Isle of Skye, Isle of Man, Dyfed) are MOVED to
`dlt_sources/media/celtic_history_research/` as 9 stub sources
gated for the downstream Celtic-MMO theming change.

### Layer 2 — The 7-axis medium-agnostic `MediaDescriptor` schema

Per design.md § 1, the descriptor captures:

1. `power_event` (actor, element, source, trigger, tier, cost,
   consequence, counter)
2. `visual_grammar` (composition, panel/shot type, motion
   lines, camera, silhouette, focal hierarchy)
3. `palette` (dominant + accent + emissive hex, per-element
   palette, contrast strategy)
4. `vfx_vocabulary` (particle class, density, trail behaviour,
   dissipation, light interaction)
5. `narrative_beat` (arc position, beat significance)
6. `transferability` (in_game_mechanic, anam_cost,
   palette_token, particle_effect)
7. `provenance` (rights_holder, licence, derivation_class,
   `shippable: false` enforced, shippable_art_path)

BAML-as-source-of-truth per `centralized-schema-registry` with
codegen to Pydantic + Zod + Convex + DuckLake DDL.

### Layer 3 — The 4 docker stacks

The 4 aspirational stacks the existing
`retro-game-design-catalogue` + `celtic-asset-generation` specs
reference:

- `comfyui/` (ComfyUI node-graph image gen, Apache 2.0)
- `libretro-retroarch/` (headless libretro + 6 cores, GPL + BSD)
- `sam3-server/` (Facebook SAM3 image segmentation, Apache 2.0)
- `sam3d-objects-server/` (Facebook SAM-3D-Objects, Apache 2.0)

All 4 land as 6-file GOLD_STANDARD artifacts per
`infrastructure-stacks` spec.

## Out of scope (deferred to the downstream theming change)

- The Celtic-MMO design itself (which elements, what the boons
  look like, which ogham stones map to which portals, the 4+1
  element binding, whether anamcara is NPC-shaped or NFT-shaped,
  whether the world overlay uses Tel'aran'rhiod or SpacetimeDB
  or Convex, the iOS delivery vehicle, the 2D particle renderer
  choice).
- The 5 stubbed source-class plugins (Morrison / Tomasi / Johns
  / Valiant / Gillen) — gated for v2.
- The agentic gameplay capture at scale (Phase 2 macro
  orchestration) — Phase 1 stands up the 4 stacks; Phase 2
  wires the macros.
- The 9 Celtic-history research topics — gated for the
  downstream theming change at `dlt_sources/media/celtic_history_research/`.

## Dependencies

```markdown
## Dependencies

`Blocked by: 2026-09-01-celtic-mythology-content-system-v1` (the parent change that creates `baml/celtic/mythology.baml` + the 6 pantheons + the GeoAI helpers + the Celtic Mythology Agent + the Fibo+ComfyUI enablement).

`Blocked by: 2026-09-08-ogham-celtic-stones-pipeline-v1` (the parent change that creates `ogham_stones` + `anam_particles` Convex tables + the spatial grid utility + the Ogham Stone Agent — the agentic capture is informed by this).

`Blocked by: 2026-09-22-geospatial-british-isles-twin-v1` (the parent change that creates the 5 geospatial DLT sources + the `notebooks/_shared/spatial_grid.py` helper + the `notebooks/37_geospatial_explorer.py` UI).

`Blocked by: 2026-09-29-familiar-dynamic-nft-system-v1` (the parent change that creates the 3 Convex tables + the Anam Progression Agent + the Fibo enablement — the family-system research context).

`Blocked by: 2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1` (the parent change that formalises the renderer + backend rejection + archives the orphaned Rust crates).

`Blocked by (soft): 2026-08-21-biiep-hackathon-agentic-educational-system-v1` (the sibling tangent; this change is the *next* layer of the hackathon direction).

`Blocked by (soft): 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1` (every model string MUST route through `MODEL_REGISTRY`; every BAML function MUST codegen to Pydantic + Zod + Convex + DuckLake DDL).

`Affected repos: cianfhoghlaim`
```

## Impact

Affected specs (2 NEW + 7 MODIFIED + 0 collisions):

| Spec | Action | ADDED / MODIFIED Requirements |
|:--|:--|:--|
| `media-intel-corpus` | **NEW** | 6 ADDED Requirements (the 7-axis descriptor schema + the 5-class registry + the plugin contract + the Firecrawl 3-plan ladder + the legal capture boundary + the cross-medium compare) |
| `media-intel-acquisition-plan` | **NEW** | 5 ADDED Requirements (the 5 v1 source acquisition plans: Class A comics + Class B prose + Class C animation + Class D games + Class E official — with the post-refactor 36 official records + the per-jurisdiction split) |
| `celtic-history-research` | **NEW** | 2 ADDED Requirements (the 9 stub sources + the cross-class drift contract — gates the 9 Celtic-history topics for the downstream theming change) |
| `retro-game-design-catalogue` | MODIFIED | 2 ADDED Requirements (the 4 NEW docker stacks + the deterministic libretro headless capture surface) |
| `celtic-asset-generation` | MODIFIED | 1 ADDED Requirement (the `media_descriptors` input flows from `media-intel-corpus`) |
| `multimodal-code-and-media-intel` | MODIFIED | 1 ADDED Requirement (the `MediaLocalEmbedding` CocoIndex v1 App accepts typed descriptors) |
| `firecrawl-corpus-and-portals` | MODIFIED | 2 ADDED Requirements (the 3-plan ladder + the per-source `firecrawl_plan` declaration) |
| `infrastructure-stacks` | MODIFIED | 4 ADDED Requirements (the 4 NEW 6-file GOLD_STANDARD stacks) |

Affected code/config (planned, executed in this change):

- `baml_src/media/` — 5 BAML files (comic / prose / animation /
  gameplay / official_document extractors)
- `dlt_sources/media/comics/hickman_marvel/` — 1 source.yaml + 1
  scrape.py (Class A)
- `dlt_sources/media/prose/wheel_of_time/` — 1 source.yaml + 1
  scrape.py (Class B)
- `dlt_sources/media/animation/atla_korra_aang_film/` — 1
  source.yaml + 1 scrape.py (Class C)
- `dlt_sources/media/games/hades_wow_golden_sun_pokemon/` — 1
  source.yaml + 1 capture.py (Class D)
- `dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/` —
  1 source.yaml + 1 scrape.py (Class E educational body
  sub-bucket — the 2 NCCA research PDFs + the 12 NCCA LC
  syllabus PDFs, en + ga parity)
- `dlt_sources/media/official/government/uk/` — 1 source.yaml + 1
  scrape.py (Class E UK government sub-bucket — police +
  defence + army + Acts + Treaties = 18 records)
- `dlt_sources/media/official/government/ie/` — 1 source.yaml +
  1 scrape.py (Class E Éire government sub-bucket — Garda +
  Defence + Oireachtas + Acts + Treaties = 15 records)
- `dlt_sources/media/official/government/crown_dependencies/` —
  1 source.yaml + 1 scrape.py (Class E Crown Dependencies
  sub-bucket — IoM + Jersey + Guernsey = 8 records)
- `dlt_sources/media/official/departments/{uk,ie,sct,wls,ni}/`
  — 5 source.yaml + 5 scrape.py (Class E departments
  sub-buckets = 18 records)
- `dlt_sources/media/celtic_history_research/{9 topics}/` — 9
  source.yaml + 9 no-op scrape.py (the 9 stub sources — gated
  for the downstream theming change)
- `agents/meaisinfhoghlaim/media_intel/` — `__init__.py` +
  `media_descriptor_agent.py` + `records.py` (the 10-tool ADK
  agent per the `academic_history_agent.py` shape)
- `agents/agent_registry.py` (MOD — 1 new entry:
  `media_descriptor_agent`, bumping the fleet from 13 → 14)
- `cocoindex_flows/media_intel/` — 2 Apps (`media_descriptors` +
  `cross_medium_compare`)
- `orchestration/defs/media_intel.py` — 23 assets (5 L1 media-
  class + 8 L1 official sub-bucket + 5 L2 BAML + 2 L3 CocoIndex
  + 2 L4 marimo + 1 L5 ADK agent) + 1 asset check
- `notebooks/media_intel_explorer_{per_medium,cross_medium}.py`
  — 2 marimo notebooks
- `bonneagar/stacks/{comfyui,libretro-retroarch,sam3-server,
  sam3d-objects-server}/` — 24 stack files (4 × 6-file
  GOLD_STANDARD)
- `mise.toml` (MOD — `data:media-intel:*` namespace: 9 new
  tasks — `educational-bodies` + `uk-government` + `ie-government` +
  `crown-deps-government` + `uk-departments` + `ie-departments` +
  `sct-departments` + `wls-departments` + `ni-departments`)
- `deployment-choice.yaml` (MOD — `media_intel_corpus` dataset
  enablement + 4 stack enablements + `media_intel_coverage`
  monitoring)

## Cross-references

- [`../../specs/media-intel-corpus/spec.md`](../../specs/media-intel-corpus/spec.md)
  — the canonical 7-axis MediaDescriptor schema
- [`../../specs/media-intel-acquisition-plan/spec.md`](../../specs/media-intel-acquisition-plan/spec.md)
  — the 5-class source acquisition plan (with the post-refactor
  36 official records)
- [`../../specs/celtic-history-research/spec.md`](../../specs/celtic-history-research/spec.md)
  — the 9 Celtic-history stub sources (gated for the downstream
  theming change)
- [`../../specs/retro-game-design-catalogue/spec.md`](../../specs/retro-game-design-catalogue/spec.md)
  — the existing libretro + BAML `ExtractGameDesignPattern`
  surface (extended; the 4 NEW stacks land as part of the
  6-file GOLD_STANDARD pattern)
- [`../../specs/celtic-asset-generation/spec.md`](../../specs/celtic-asset-generation/spec.md)
  — the 4-pipeline Celtic asset generation (extended with the
  `media_descriptors` input flowing from `media-intel-corpus`)
- [`../../specs/multimodal-code-and-media-intel/spec.md`](../../specs/multimodal-code-and-media-intel/spec.md)
  — the 5 CocoIndex v1 Apps + `MediaLocalEmbedding` (extended
  to accept typed descriptors as the primary input)
- [`../../specs/firecrawl-corpus-and-portals/spec.md`](../../specs/firecrawl-corpus-and-portals/spec.md)
  — the 6 Firecrawl invariants (extended with the 3-plan
  ladder + the per-source `firecrawl_plan` declaration)
- [`../../specs/infrastructure-stacks/spec.md`](../../specs/infrastructure-stacks/spec.md)
  — the 6-file GOLD_STANDARD pattern (extended with the 4
  NEW stacks)
- [`../../specs/centralized-model-registry/spec.md`](../../specs/centralized-model-registry/spec.md)
  — the 24-entry VISION_MODELS + the 7-family MODEL_REGISTRY
- [`../../specs/centralized-schema-registry/spec.md`](../../specs/centralized-schema-registry/spec.md)
  — the BAML-as-source-of-truth contract
- [`../../specs/dagster-5-layer-component-architecture/spec.md`](../../specs/dagster-5-layer-component-architecture/spec.md)
  — the L1 Ingestion / L2 Materials / L3 Model Lifecycle / L4
  Asset Generation / L5 Agent Operations pattern
- [`../../specs/agentic-frontend-frameworks/spec.md`](../../specs/agentic-frontend-frameworks/spec.md)
  — the existing 4 canonical web surfaces (consumed as-is)
- [`../2026-09-01-celtic-mythology-content-system-v1/`](./2026-09-01-celtic-mythology-content-system-v1/)
  — the parent change (must archive first)
- [`../2026-09-08-ogham-celtic-stones-pipeline-v1/`](./2026-09-08-ogham-celtic-stones-pipeline-v1/)
  — the parent change (must archive first)
- [`../2026-09-22-geospatial-british-isles-twin-v1/`](./2026-09-22-geospatial-british-isles-twin-v1/)
  — the parent change (must archive first)
- [`../2026-09-29-familiar-dynamic-nft-system-v1/`](./2026-09-29-familiar-dynamic-nft-system-v1/)
  — the parent change (must archive first)
- [`../2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1/`](./2026-10-06-spacetimedb-babylonjs-adr-clean-break-v1/)
  — the parent change (must archive first)
- [`../2026-08-21-biiep-hackathon-agentic-educational-system-v1/`](./2026-08-21-biiep-hackathon-agentic-educational-system-v1/)
  — the sibling tangent (this change is the *next* layer)
- [`../2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`](../2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/)
  — the soft-blocker (every model + schema must route through it)
- [`../../AGENTS.md`](../../AGENTS.md) — the platform root
- [`../../../AGENTS.md`](../../../AGENTS.md) — the monorepo root

## The 2026-08-23 refactor (mid-flight)

The change was refactored mid-execution to address a drift: the
prior draft of Class E committed 12 Wikipedia pages (Tuatha Dé
Danann, Irish mythology, etc.) as official sources. The user's
brief corrected this:

- The 9 Celtic-history Wikipedia pages were MOVED to
  `dlt_sources/media/celtic_history_research/` as 9 stub sources
  (gated for the downstream theming change)
- The 3 educational body Wikipedia pages (NCCA + SEC + DfE + SQA
  + WJEC + DESC) were kept in the educational body sub-bucket
  (they're real official sources, not Wikipedia)
- The Class E official surface was REPLACED with 3 government
  sub-buckets (UK + Éire + Crown Dependencies — police + defence
  + army + Acts + Treaties) + 5 departments sub-buckets (UK + Éire
  + Scotland + Wales + Northern Ireland) = 36 official records

The 9 Wikipedia pages that were the original drift are now
correctly stubbed for the future theming change. The official
government / police / defence / army / Acts / Treaties surface
is now the canonical Class E.

Every new `rights_holder` field is the actual issuing body
(e.g., "An Garda Síochána", "Metropolitan Police Service",
"Ministry of Defence", "Crown copyright"), not "Wikipedia
Foundation". Every per-source `licence` is declared correctly
(CC-BY-SA-4.0 for the 9 Celtic-history stubs + OGL-3.0 for UK
gov + PSI for Éire gov + Crown copyright for the Acts).
