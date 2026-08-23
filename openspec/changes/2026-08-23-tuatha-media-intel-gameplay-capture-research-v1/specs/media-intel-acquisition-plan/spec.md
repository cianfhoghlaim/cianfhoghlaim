# Spec Delta: media-intel-acquisition-plan

## Purpose

`media-intel-acquisition-plan` is the canonical surface for the
5 v1 reference-corpus sources the Cianfhoghlaim platform will
ingest to feed the medium-agnostic `MediaDescriptor` schema
(per the `media-intel-corpus` spec). The plan declares, per
class, the source surface, the acquisition path, the VLM
routing, the BAML function set, the LanceDB + DuckLake
storage, and the licence summary.

The 5 classes are:

- **A — Comics**: the Jonathan Hickman Marvel run
- **B — Prose**: The Wheel of Time (the 0-pixel control)
- **C — Animation**: Avatar: The Last Airbender + The Legend
  of Korra + the Aang-film continuity
- **D — Games**: Hades 1 + 2 + World of Warcraft + Golden Sun
  (GBA via `romm`) + Pokémon (GB via `romm`) (local-capture only)
- **E — Official**: the 6 educational body sources (NCCA + SEC
  + DfE + SQA + WJEC + DESC) + the 3 government sub-buckets
  (UK + Éire + Crown Dependencies — police + defence + army +
  Acts + Treaties) + the 5 departments sub-buckets (UK + Éire +
  Scotia + Wales + Northern Ireland)

The plan is **gathering-only**. The Celtic-MMO design that
consumes the resulting `MediaDescriptor` corpus is a
downstream change gated on this one.

The 9 Celtic-history research topics (Tuatha Dé Danann, Irish
mythology, etc.) were MOVED to
`dlt_sources/media/celtic_history_research/` per the
2026-08-23 refactor. They are gated for the downstream
Celtic-MMO theming change.

## ADDED Requirements

### Requirement: Class A — Comics acquisition plan (Hickman Marvel run)

The system SHALL ingest the following Jonathan Hickman Marvel
publications as the Class A comics source:

1. `Fantastic Four` #570-611 (the "FF 1-23" relaunch)
2. `FF` #1-23
3. `Future Foundation` (the post-`Three` follow-up)
4. `Avengers` (2012)
5. `New Avengers` (2013) → `Infinity` → `Secret Wars` (2015)
6. `House of X` + `Powers of X` (2019)
7. `X-Men` (2019) + Krakoa-era crossovers (Dawn of X
   framing, `Inferno`, `X of Swords`)

Acquisition path: Wikipedia + Marvel wiki transcripts (panel
images are Wikipedia-Commons only — copyrighted panel images
are description-only).

#### Scenario: A panel is described from a Hickman FF issue

- **GIVEN** the source is `dlt_sources/media/comics/hickman_marvel/`
  with `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `ExtractComicDescriptor` BAML function runs
  with `vlm_primary: "qwen3-vl-8b"` (resolved via
  `MODEL_REGISTRY.resolve(family="ocr_vision", role="media_descriptor")`)
- **THEN** the function emits a `MediaDescriptor` record
  with all 7 axes populated
- **AND** the record's `shippable` field SHALL be `False`
- **AND** the record's `licence` field SHALL be
  `"fair-use-description"`
- **AND** the record's `provenance.rights_holder` SHALL
  reference Marvel Comics (the rights holder)

### Requirement: Class B — Prose acquisition plan (Wheel of Time)

The system SHALL ingest the Wheel of Time as the Class B prose
source. The Wheel of Time is the 0-pixel control group: it
proves the medium-agnostic descriptor schema works on a work
with no visual component.

Acquisition path: Wikisource + Wikipedia summary pulls (text
only, no images).

The Wheel of Time is the explicit analogue for the
gender-agnostic channelling contract. The 5 magic-system
axes (`saidar / saidin / Tel'aran'rhiod / One Power / Aes
Sedai`) are surface-cited from the Wikisource text.

#### Scenario: A Wheel of Time passage is described

- **GIVEN** the source is `dlt_sources/media/prose/wheel_of_time/`
  with `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `ExtractProseDescriptor` BAML function runs
  with `vlm_primary: "qwen3.6-27b-mtp"` (the prose-specialist
  per `multimodal-code-and-media-intel`)
- **THEN** the function emits a `MediaDescriptor` record
  with the 7 axes populated
- **AND** the `vfx_vocabulary.particle_class` SHALL be set
  to `ink` (prose-as-medium default)
- **AND** the `visual_grammar.composition` SHALL be a
  paragraph of text rather than a panel coordinate

### Requirement: Class C — Animation acquisition plan (ATLA + Korra + Aang film)

The system SHALL ingest the Avatar animated property
(`Avatar: The Last Airbender` + `The Legend of Korra` + the
Aang-film continuity) as the Class C moving-media source.

Acquisition path: Wikipedia + Avatar wiki concept-art
thumbnails (static concept art only — animation frame
stills are description-only per the `media-intel-corpus`
legal capture boundary).

The 4+1 element vocabulary (air / water / fire / earth /
spirit) is surface-cited from the Wikipedia article. The
bending sub-disciplines (metal / blood / lightning /
healing / sand) are captured via the `power_event` axis.

#### Scenario: An ATLA frame is described

- **GIVEN** the source is
  `dlt_sources/media/animation/atla_korra_aang_film/` with
  `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `ExtractAnimationDescriptor` BAML function
  runs with `vlm_primary: "molmo2-8b"` (the diagram-pointing
  specialist)
- **THEN** the function emits a `MediaDescriptor` record
  with the 7 axes populated
- **AND** the `transferability.palette_token` field SHALL
  reference the per-element palette token (e.g.
  `"air"`, `"water"`, `"fire"`, `"earth"`, `"spirit"`)

### Requirement: Class D — Games acquisition plan (Hades + WoW + Golden Sun + Pokémon)

The system SHALL ingest the following locally-available games
as the Class D games source:

1. **Hades 1** (owned, installed locally on `bunchloch`) —
   boon descriptors only, never captured screenshots
2. **Hades 2** (owned, installed locally on `bunchloch`) —
   boon descriptors only, never captured screenshots
3. **World of Warcraft** (owned, installed locally on
   `bunchloch`) — class/role/zone descriptors, never
   captured frames
4. **Golden Sun** (owned ROM via `romm` + libretro `mgba`
   core) — Djinn/Psynergy class descriptors, screenshots
   stored in `stedding/ingest_queue/retro/gba/golden_sun/`
   per the `retro-game-design-catalogue` spec (NOT
   shippable)
5. **Pokémon** (owned ROM via `romm` + libretro `gambatte`
   core) — type chart interaction matrix is public-domain
   mechanics; no per-game asset reused

Acquisition path: `sunshine` + `moonlight` for Hades/WoW;
`libretro-retroarch` headless capture for Golden Sun/
Pokémon; `ludusavi` for save-state restore; `sam3-server`
for Djinn sprite + boon-orb icon segmentation.

No Firecrawl involvement (Class D is local-capture only).

#### Scenario: A Golden Sun Djinn sprite is described

- **GIVEN** the source is
  `dlt_sources/media/games/hades_wow_golden_sun_pokemon/`
  with `source.yaml:firecrawl_plan: n/a` (local capture)
- **WHEN** the deterministic macro
  `golden_sun_title_to_venus_lighthouse.py` runs the
  libretro netcommand interface to load the ROM + the
  `ludusavi` save state
- **AND** the screenshot capture loop runs for 60 seconds
- **AND** the `sam3-server` API segments the Djinn sprite
  from the central-screen image
- **AND** the `ExtractGameplayDescriptor` BAML function
  runs on the segmented sprite + the session log
- **THEN** the function emits a `MediaDescriptor` record
  with all 7 axes populated
- **AND** the screenshot count in
  `stedding/ingest_queue/retro/gba/golden_sun/` SHALL be
  ≥12

### Requirement: Class E — Official acquisition plan (refactored 2026-08-23)

The system SHALL ingest the following OFFICIAL sources as
the Class E official-document source. The acquisition plan
is split into 3 sub-buckets per the user's brief: the
**educational body** sub-bucket (NCCA + SEC + DfE + SQA +
WJEC + DESC), the **government** sub-bucket (UK + Éire +
Crown Dependencies — police + defence + army + Acts +
Treaties), and the **departments** sub-bucket (UK + Éire +
Scotia + Wales + Northern Ireland).

The 9 Celtic-history research topics (Tuatha Dé Danann,
Irish mythology, etc.) were MOVED to
`dlt_sources/media/celtic_history_research/` per the
2026-08-23 refactor (they are gated for the downstream
Celtic-MMO theming change).

#### Scenario: An NCCA research PDF is described

- **GIVEN** the source is
  `dlt_sources/media/official/ncca_sec_celt_duchas_wikipedia/`
  (the educational body sub-bucket) with
  `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `firecrawl_parse` call ingests a PDF page
  from the NCCA research PDF on certificates + online
  learning
- **AND** the `ExtractOfficialDocumentDescriptor` BAML
  function runs with `vlm_primary: "olmocr-2-7b"` (the OCR
  specialist)
- **THEN** the function emits a `MediaDescriptor` record
  with the 7 axes populated
- **AND** the `provenance.rights_holder` SHALL be
  `"NCCA"` (the issuing body, not "Wikipedia Foundation")
- **AND** the `provenance.licence` SHALL be
  `"fair-use-description"`
- **AND** the `derivation_class` SHALL be `fair_use_quote`

#### Scenario: A UK police / defence / department page is described

- **GIVEN** the source is
  `dlt_sources/media/official/government/uk/` with
  `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `firecrawl_scrape` call ingests an HTML
  page from the Met Police + MoD + British Army + Home
  Office + FCDO + MoJ + DoH surfaces (and the 7 UK Acts +
  Treaties)
- **AND** the `ExtractOfficialDocumentDescriptor` BAML
  function runs with `vlm_primary: "olmocr-2-7b"`
- **THEN** the function emits a `MediaDescriptor` record
  per source
- **AND** the `provenance.licence` SHALL be `"OGL-3.0"`
  (Open Government Licence v3.0) for departmental pages
- **AND** the `provenance.licence` SHALL be `"OGL-3.0"`
  (Crown copyright) for the Acts + Treaties
- **AND** the `provenance.rights_holder` SHALL be the
  specific issuing body (e.g., "Metropolitan Police
  Service", "Ministry of Defence", "Crown copyright")

#### Scenario: An Éire Garda / Defence / Oireachtas / Act page is described

- **GIVEN** the source is
  `dlt_sources/media/official/government/ie/` with
  `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `firecrawl_scrape` call ingests an HTML
  page from the Garda + Defence + DoD + DoJ + DFA +
  Oireachtas + Office of the President + 6 Acts +
  Treaties surfaces
- **AND** the `ExtractOfficialDocumentDescriptor` BAML
  function runs with `vlm_primary: "olmocr-2-7b"`
- **THEN** the function emits a `MediaDescriptor` record
  per source
- **AND** the `provenance.licence` SHALL be `"PSI"`
  (Public Sector Information Licence) for departmental
  pages + the Oireachtas + Office of the President
- **AND** the `provenance.licence` SHALL be `"OGL-3.0"`
  (Crown copyright) for the 6 Acts + Treaties

#### Scenario: A Crown Dependency (IoM / Jersey / Guernsey) page is described

- **GIVEN** the source is
  `dlt_sources/media/official/government/crown_dependencies/`
  with `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `firecrawl_scrape` call ingests an HTML
  page from the IoM Government + IoM Constabulary + Tynwald
  + States of Jersey + States of Guernsey
- **AND** the `ExtractOfficialDocumentDescriptor` BAML
  function runs with `vlm_primary: "olmocr-2-7b"`
- **THEN** the function emits a `MediaDescriptor` record
  per source
- **AND** the `provenance.licence` SHALL be `"OGL-3.0"`
- **AND** the `provenance.rights_holder` SHALL be the
  specific Crown Dependency body

#### Scenario: A UK / Éire / Scotland / Wales / Northern Ireland department page is described

- **GIVEN** the source is
  `dlt_sources/media/official/departments/{uk,ie,sct,wls,ni}/`
  with `source.yaml:firecrawl_plan: plan_a_keyless`
- **WHEN** the `firecrawl_scrape` call ingests an HTML
  page from the 17 departmental surfaces (5 UK + 3 Éire +
  3 Scotland + 3 Wales + 3 Northern Ireland)
- **AND** the `ExtractOfficialDocumentDescriptor` BAML
  function runs with `vlm_primary: "olmocr-2-7b"`
- **THEN** the function emits a `MediaDescriptor` record
  per source
- **AND** the `provenance.licence` SHALL be `"OGL-3.0"`
  (or `"PSI"` for Éire) per the per-source licence
  whitelist

### Requirement: Cross-class acquisition guard

The system SHALL enforce the following cross-class invariants
on every acquisition:

- Every source declares its Firecrawl plan
  (`plan_a_keyless` / `plan_b_paid_basic` / `plan_c_full`)
  in its `source.yaml`. Class D uses `n/a` (local-capture
  only). The 9 Celtic-history stub sources use `n/a` (gated).
- Every source declares its VLM routing through
  `MODEL_REGISTRY` family+role (no hardcoded model
  strings).
- Every source declares its BAML function set (a list of
  functions from `baml_src/media/<medium>_descriptor.baml`).
  The 9 Celtic-history stub sources declare `baml_functions:
  []`.
- Every source declares its LanceDB target table
  (`media_descriptors`).
- Every source declares its DuckLake schema
  (`cianfhoghlaim.media`).
- Every source declares its licence summary and
  `legal_notes`.
- The system refuses to materialise any source where
  `shippable_default: true` and `licence_summary` is not
  in the approved list (`CC-BY-SA-4.0`, `CC0`, `OFL-1.1`,
  `fair-use-description`, `OGL-3.0`, `PSI`).

#### Scenario: A new source is added to the registry

- **GIVEN** a new external work is identified
- **WHEN** the operator adds a `source.yaml` file at
  `dlt_sources/media/<class>/<work>/source.yaml`
- **THEN** the system SHALL auto-generate the DLT source
  stub from the manifest
- **AND** the system SHALL refuse the new source if
  `shippable_default: true` and `licence_summary` is not
  in the approved list
- **AND** the system SHALL refuse the new source if any
  field is missing
