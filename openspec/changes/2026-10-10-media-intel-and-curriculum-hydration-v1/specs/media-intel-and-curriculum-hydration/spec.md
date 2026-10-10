# media-intel-and-curriculum-hydration Specification

## Purpose
`media-intel-and-curriculum-hydration` is the contract for the
cross-media design-pattern catalogue (Hades / Avatar: The Last Airbender
/ X-Men / The Wheel of Time) that supersedes the retro-game-only
catalogue, and for hydrating the Leaving Certificate corpus into the
lakehouse so media descriptors and generated assets are conditioned on
real syllabus rows. Every descriptor is **description-only**
(`provenance.shippable = false`); no copyrighted pixels, panels,
animation frames, or game art are ever stored.

Per the 2026-10-10-media-intel-and-curriculum-hydration-v1 saga change
(Plan 1 + Plan 2 + Plan 2.5 of
openspec/plans/2026-10-10-tuatha-curriculum-media-saga-v1.md).

## ADDED Requirements

### Requirement: Cross-media power descriptor schema

The system MUST provide a `MediaPowerDescriptor` BAML class that
generalises the 7-axis per-medium descriptors across all four media
classes, plus the supporting `PowerUseEvent`, `MediaVisualGrammar`,
`PaletteSignature`, `ComparativeStudyLens`, and `MediaPowerProvenance`
classes, and the enums `PowerSystemKind` (`DivineBoon` | `ElementalBending`
| `MutantGene` | `Channeling` | `Cosmic` | `Other`), `MediaMedium` (`Game`
| `Animation` | `Comic` | `Prose` | `Film`), `ElementalAxis`, and
`PowerScaleTier`. The schema MUST live in
`baml_src/media/media_power_system.baml`.

#### Scenario: Hades boon maps onto the cross-media schema
- **GIVEN** a Hades boon-selection frame (Class D)
- **WHEN** `ExtractMediaPowerDescriptor` runs with `power_system = "DivineBoon"`
- **THEN** the returned `MediaPowerDescriptor.power_event.power_system == "DivineBoon"`
- **AND** `provenance.shippable == false`

#### Scenario: X-Men panel maps onto the cross-media schema
- **GIVEN** a Hickman X-Men panel (Class A)
- **WHEN** `ExtractMediaPowerDescriptor` runs with `power_system = "MutantGene"`
- **THEN** `power_event.power_system == "MutantGene"` and `medium == "Comic"`

### Requirement: Wheel of Time per-chapter schema

The system MUST provide a `WotChapterSchema` BAML class in
`baml_src/media/wheel_of_time.baml` that describes **one chapter** of the
Wheel of Time (not one passage), including `book`, `book_index`,
`chapter_number`, `chapter_title`, `pov_character`, `summary`,
`power_events[]` (each a `WotPowerUseEvent` with a `WotPowerSystem` and,
for channeling, a `WotFlow`), `characters[]` (`WotCharacterMention`), and
`provenance`. The extractor function MUST be `ExtractWotChapterSchema`.

#### Scenario: A chapter with channeling is indexed
- **GIVEN** the text of a chapter in which a character channels
- **WHEN** `ExtractWotChapterSchema` runs for `(book_index = 1, chapter_number = N)`
- **THEN** `power_events[]` contains ≥1 event whose `power_system` is
  `OnePowerSaidar` or `OnePowerSaidin`
- **AND** each such event carries a `flow` value from `WotFlow`

#### Scenario: A chapter with no power use is still indexed
- **GIVEN** a chapter with no power use
- **WHEN** `ExtractWotChapterSchema` runs
- **THEN** `power_events` is empty and the row is still emitted (the
  per-chapter index is complete, not sparse)

### Requirement: Description-only provenance

Every record emitted by any media-intel extractor MUST carry a
`MediaPowerProvenance`/per-medium `Provenance` whose `shippable` field is
the literal `false`, and MUST name a `rights_holder` +
`derivation_class` (`description_only`). The pipelines MUST NOT persist
copyrighted pixels, panels, animation frames, or game art.

#### Scenario: A descriptor is rejected if it claims shippable
- **GIVEN** a media descriptor whose `provenance.shippable != false`
- **WHEN** the CocoIndex embedding flow validates it
- **THEN** the row is dropped and a warning is logged
  (`media_intel_shippable_violation`)

### Requirement: Media library covers four classes

The system MUST provide `agents/adk/tools/media_library.py` with a
`MEDIA_LIBRARY` listing at least one entry per class:
`hades` (Class D, `Game`), `avatar_the_last_airbender` (Class C,
`Animation`), `xmen_hickman` (Class A, `Comic`), `wheel_of_time` (Class
B, `Prose`). Each entry MUST name its `power_system_kind`, its BAML
extraction function, and its model family (resolved via `MODEL_REGISTRY`;
no hardcoded model strings). The retro entries MUST remain, marked
`media_class = "retro"` + `artifact = true`.

#### Scenario: Every class resolves to a BAML function
- **GIVEN** the `MEDIA_LIBRARY`
- **WHEN** `power_descriptor_targets()` is called
- **THEN** each returned target names an extraction function that exists
  in the generated `baml_client`

### Requirement: CocoIndex media-power + per-chapter embedding

The system MUST provide two CocoIndex v1 Apps:
`cocoindex_flows/media/media_power_embedding.py` (mounts
`lance://media.media_power_descriptors`) and
`cocoindex_flows/media/wheel_of_time_embedding.py` (mounts
`lance://media.wheel_of_time_chapters` keyed by
`(book_index, chapter_number)`). Both MUST conform to R1–R4: import
`shared_lifespan` + the shared `EMBEDDER`/`LANCE_DB` from
`.._shared._lifespan`, declare no new `ContextKey[`, declare a module-scope
`app = coco.App(coco.AppConfig(name=...))`, and use at least one
`@coco.fn(`.

#### Scenario: A WoT chapter is searchable by power system
- **GIVEN** a `WotChapterSchema` with a `OnePowerSaidin` event is embedded
- **WHEN** a semantic query "chapters where saidin is channelled" runs
- **THEN** the chapter row is returned from
  `lance://media.wheel_of_time_chapters`

#### Scenario: R2 conformance is machine-checkable
- **GIVEN** the 3 new flow modules
- **WHEN** the conformance scan greps for `ContextKey[`
- **THEN** zero new declarations are found

### Requirement: Leaving Certificate corpus hydration into DuckLake

The system MUST provide `scripts/curriculum_hydrate.py` that reads the
Leaving Certificate corpus (`leaving_certificate/`, including the
per-subject NCCA PDFs and the NCCA policy PDFs) plus the operator's
hand-made examples (`stedding/geog.pdf`, the `PastLC-IrishEnglish`
images) and upserts rows into DuckLake tables
`cianfhoghlaim.lc.geography.topics`,
`cianfhoghlaim.lc.gaeilge.poems_higher`,
`cianfhoghlaim.lc.english.poets_higher`, and
`cianfhoghlaim.education.ie.policies`. Each row MUST carry a
`source_pdf` + `source_page` + `source_url` provenance triple.

#### Scenario: geog.pdf hydrates geography topics
- **GIVEN** an operator has a hand-made `stedding/geog.pdf`
- **WHEN** `python scripts/curriculum_hydrate.py --source stedding/geog.pdf` runs
- **THEN** rows are upserted into `cianfhoghlaim.lc.geography.topics`
- **AND** every row carries `source_pdf = "stedding/geog.pdf"`

#### Scenario: PastLC-IrishEnglish hydrates the poetry tables
- **GIVEN** the `PastLC-IrishEnglish` page images
- **WHEN** `curriculum_hydrate` runs with `--subject english --subject gaeilge`
- **THEN** rows land in `cianfhoghlaim.lc.english.poets_higher` and
  `cianfhoghlaim.lc.gaeilge.poems_higher` with page-level provenance

#### Scenario: NCCA policies hydrate the policy table
- **GIVEN** the NCCA policy PDFs under `leaving_certificate/`
- **WHEN** `curriculum_hydrate` runs with `--policies`
- **THEN** rows land in `cianfhoghlaim.education.ie.policies`

### Requirement: LC Art + English Comparative Study lens

Every `MediaPowerDescriptor` MUST carry a `ComparativeStudyLens` exposing
the LC English Comparative Study axes (`theme_or_issue`,
`cultural_context`, `literary_genre`, `general_vision`) and the LC Art
comparative-study axes (`composition`, `palette_strategy`,
`visual_grammar`). The marimo dashboard MUST render the lens side by side
for cross-work comparison.

#### Scenario: Two works are compared
- **GIVEN** an X-Men descriptor and an Avatar descriptor
- **WHEN** the comparative-study view renders
- **THEN** the four LC English axes + three LC Art axes are shown for
  both works side by side

### Requirement: BAML project builds

The system MUST build its BAML project. `baml-cli generate` MUST exit 0
and inject the new `ExtractMediaPowerDescriptor` + `ExtractWotChapterSchema`
functions into `baml_client/`.

#### Scenario: Generation succeeds
- **GIVEN** a clean checkout
- **WHEN** `./.venv/bin/baml-cli generate --from ./baml_src` runs
- **THEN** it exits 0 and `ExtractWotChapterSchema` appears in
  `baml_client/baml_client/async_client.py`
