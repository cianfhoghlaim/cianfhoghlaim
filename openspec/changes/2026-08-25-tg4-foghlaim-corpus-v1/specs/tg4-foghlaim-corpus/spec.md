# TG4 + Foghlaim Media Corpus Capability

## Purpose

`tg4-foghlaim-corpus` is a capability of the Cianfhoghlaim platform. It
ingests, classifies, and indexes the on-demand video catalogues of
**TG4.ie** (the Irish-language public broadcaster) and its parallel
**educational portal Foghlaim.tg4.ie** as a multimodal Irish-language
corpus. The corpus is the largest open collection of modern spoken
Gaeilge on the public internet: ~hundreds of broadcast episodes per
season across 8 genres + ~1,500+ classroom-tagged lessons across 3
educational levels and 11+ subjects that map 1:1 onto the BIEP v3
subject taxonomy.

The capability covers three pillars:

1. **Catalogue ingestion** — TG4 player shows + Foghlaim lessons via
   DLT sources that wrap the **Brightcove Playback API** (the public
   video backend, identified by 13-digit `pid` IDs) and the **Nuxt.js
   lesson pages** (which also reference **YouTube** videos for the
   Cúla4 channel).
2. **Multimodal embedding** — a CocoIndex v1 App that joins the
   subtitles (Brightcove `text_tracks` WebVTT, treated as canonical per
   the user decision), audio-derived transcripts (WhisperX, run on a
   5% audit sample + every NCCA-tagged lesson for proof-of-alignment),
   and frame captions (`qwen3-vl-8b` + `molmo2-8b` via the existing
   `MODEL_REGISTRY`) into 4 LanceDB tables.
3. **Educational metadata extraction** — 4 BAML functions that
   surface `biep_subject` joins + speaker diarization + worksheet
   extraction + transcript-quality audit, all routed through the
   existing BIEP BAML infrastructure.

The corresponding source code lives at:

- `dlt_sources/api_sources/tg4_player_shows.py` (NEW — TG4 player
  catalog via Brightcove Playback API)
- `dlt_sources/api_sources/foghlaim_lessons.py` (NEW — Foghlaim
  Nuxt.js lesson scrape via Firecrawl MCP)
- `baml_src/media/tg4_classification.baml` (NEW — 4 BAML fns)
- `cocoindex_flows/media/tg4_foghlaim_embedding.py` (NEW — v1 App,
  R1–R4 conformant)
- `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml`
  (NEW — L3 component)
- `orchestration/defs/2_materials/tg4_foghlaim/tg4_foghlaim_assets.py`
  (NEW — 6 Dagster assets)
- `notebooks/41_tg4_foghlaim_corpus.py` (NEW — 5-tab marimo notebook)
- `motherduck/dives/tg4_corpus_overview.py` (NEW — analytics Dive)

## ADDED Requirements

### Requirement: Tg4PlayerCatalogIngest

The system SHALL provide a DLT source at
`dlt_sources/api_sources/tg4_player_shows.py` that walks the 8 TG4
on-demand genres (`Faisnéis` / `Ceol` / `Drámaíocht` / `Cúrsaí Reatha` /
`Siamsaíocht` / `Spórt` / `Saolchláir` / `Cúla4`) plus the `Bailiúcháin`
box-set route, paginates each (`?page=N` + `?series=<series>`), and for
every episode card extracts the 13-digit `pid` (Brightcove video ID) +
the `pcode` (Cloudinary poster ID) + title + season/episode + duration
+ upload date + genre + series. For every episode, the source SHALL
call the public Brightcove Playback API
(`https://edge.api.brightcove.com/playback/v1/accounts/<TG4_ACCOUNT>/videos/<pid>`)
with `Accept: application/json;pk=<POLICY_KEY>` to fetch the canonical
JSON (HLS manifest URL, MP4 renditions array, captions list of WebVTT
URLs, custom fields, poster). The source SHALL emit one row per episode
into `cianfhoghlaim.tg4.player_shows` (DuckLake). `primary_key =
["pid"]`, `write_disposition = "merge"`. The source SHALL honor
`USE_LOCAL_SCRAPES=true` by falling back to
`stedding/ingest_queue/tg4_player/` cached JSON.

#### Scenario: Player catalog ingested end-to-end

- **WHEN** a Dagster user clicks "Materialize all" on the
  `tg4_player_catalog` asset
- **THEN** the DLT source scrapes all 8 genres + `Bailiúcháin` + every
  paginated series + every episode card
- **AND** for every episode the Brightcove Playback API call returns
  the canonical JSON
- **AND** exactly one DuckLake row per `pid` lands in
  `cianfhoghlaim.tg4.player_shows`
- **AND** the row contains `pid`, `pcode`, `title`, `title_irish`,
  `title_english`, `season`, `episode`, `duration_s`, `upload_date`,
  `genre`, `series`, `hls_manifest_url`, `mp4_renditions` (JSON
  array), `vtt_caption_urls` (JSON array), `poster_url`,
  `custom_fields` (JSON object), `educational_use` (bool), `age_rating`

#### Scenario: USE_LOCAL_SCRAPES fallback

- **GIVEN** `USE_LOCAL_SCRAPES=true` is set
- **AND** the `stedding/ingest_queue/tg4_player/` directory contains
  pre-scraped JSON snapshots
- **WHEN** the DLT source runs
- **THEN** the source SHALL iterate the cached JSON files in place of
  the live TG4 player pages + Brightcove API calls
- **AND** no network requests are made

#### Scenario: Metadata-only by default

- **GIVEN** `TG4_DOWNLOAD_MEDIA=skip` (the default)
- **WHEN** the DLT source runs
- **THEN** the source SHALL NOT download MP4 files from the Brightcove
  CDN
- **AND** the `mp4_renditions` column SHALL still be populated (URLs
  are public metadata) but no bytes are fetched

### Requirement: FoghlaimLessonsIngest

The system SHALL provide a DLT source at
`dlt_sources/api_sources/foghlaim_lessons.py` that enumerates every
`/ceacht/<lesson-id>` URL on `foghlaim.tg4.ie` via `firecrawl_map` with
a `search:` term that matches `ceacht`, then `firecrawl_scrape`s each
lesson with `formats=[json]` and a `jsonOptions.schema` that surfaces
`level`, `subject`, `keywords`, `worksheet_urls`, `learning_outcomes`,
`duration_s`, `source_suffix` (`FO|BC|MO|YT`), `series`, and
`related_lessons`. The source SHALL detect the upstream video source
type from the `lesson_id`:

- **13-digit Brightcove ID** → reuse the Brightcove Playback API call
  from `tg4_player_shows.py` (with a join key on `pid`)
- **11-character YouTube ID** → shell `yt-dlp --dump-json` (mirroring
  `dlt_sources/api_sources/youtube_videos.py`) to get the canonical
  metadata + captions URL

The source SHALL emit one row per lesson into
`cianfhoghlaim.tg4.foghlaim_lessons`. `primary_key = ["lesson_id"]`,
`write_disposition = "merge"`. The source SHALL add 3 derived columns
via a small BIEP taxonomy table:
`biep_subject` (e.g. `Stair` → BIEP `history`,
`Béaltriail` → BIEP `gaeilge_oral`),
`biep_stage` (`bunscoil | junior_cycle | senior_cycle | adult`),
`has_worksheet` (boolean).

#### Scenario: 1500+ lessons ingested end-to-end

- **WHEN** a Dagster user clicks "Materialize all" on the
  `foghlaim_lessons_catalog` asset
- **THEN** the Firecrawl map call enumerates >=1500 `/ceacht/<id>`
  URLs (the lower bound observed in the 2026-08-25 pilot scrape)
- **AND** every URL is `firecrawl_scrape`d with the lesson schema
- **AND** for every lesson the upstream video source is detected
  (Brightcove vs YouTube) and the appropriate child resource runs
- **AND** exactly one DuckLake row per `lesson_id` lands in
  `cianfhoghlaim.tg4.foghlaim_lessons`
- **AND** the `biep_subject`, `biep_stage`, and `has_worksheet`
  derived columns are populated

#### Scenario: YouTube lesson reuses yt-dlp

- **GIVEN** a lesson `lesson_id = "IZDzeqJ80K0"` (an 11-char YouTube ID)
- **WHEN** the Foghlaim DLT source runs
- **THEN** the source SHALL shell `yt-dlp --dump-json` against
  `https://www.youtube.com/watch?v=IZDzeqJ80K0`
- **AND** the resulting JSON metadata lands in the `youtube_metadata`
  JSON column on the lesson row
- **AND** the row SHALL NOT have a `brightcove_video` JSON column
  populated

#### Scenario: Brightcove lesson reuses Playback API

- **GIVEN** a lesson `lesson_id = "6395898596112"` (a 13-digit
  Brightcove ID)
- **WHEN** the Foghlaim DLT source runs
- **THEN** the source SHALL call the Brightcove Playback API as in
  T1.1's scenario
- **AND** the resulting canonical JSON lands in the `brightcove_video`
  JSON column on the lesson row
- **AND** the row SHALL NOT have a `youtube_metadata` JSON column
  populated

### Requirement: Tg4MultimodalEmbedding

The system SHALL provide a CocoIndex v1 App at
`cocoindex_flows/media/tg4_foghlaim_embedding.py` that mounts 4
LanceDB tables (`tg4_segments`, `tg4_frame_captions`, `tg4_triples`,
`tg4_quality_audits`) and ingests every row of
`cianfhoghlaim.tg4.player_shows` + `cianfhoghlaim.tg4.foghlaim_lessons`
plus the locally-available media files at
`stedding/ingest_queue/tg4/<pid>.{mp4,vtt,info.json}`. The App SHALL be
R1–R4 conformant (import `.._shared._lifespan`, declare the App at
module scope, mount LanceDB targets, declare at least one
`@coco.fn`). The App SHALL:

1. **Subtitle canonical** — read `<pid>.vtt` (the Brightcove
   `text_tracks` WebVTT) and split into 30-second `VideoSegmentRecord`
   rows, embedded via the shared `EMBEDDER` (`BAAI/bge-m3`).
2. **Audio audit** (5% sample + every NCCA-tagged lesson) — shell
   `yt-dlp` or `ffmpeg` to extract the audio, run
   `meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner` to
   get the audio-derived transcript + word-level timestamps, store
   alongside the canonical VTT in `tg4_segments.audio_audit_*` columns.
3. **Frame sampling** — sample at `0.1 fps` (one frame per 10s) via
   ffmpeg, route captions through `qwen3-vl-8b` + diagram pointing
   through `molmo2-8b` via the `MODEL_REGISTRY` (NEVER literal
   HuggingFace IDs per `meaisinfhoghlaim.AGENTS.md` DO NOT).
4. **BAML classification** — call `ClassifyTg4Episode` once per
   episode, `ExtractSpeakerLineup` once per VTT, `ExtractWorksheetAnswers`
   only when `has_worksheet=true`, and `AuditTranscriptQuality` only on
   the 5% sample + NCCA-tagged lessons (per the cost-ordering
   documented in the proposal).

#### Scenario: 4 LanceDB tables populated

- **WHEN** the v1 App materialises against a freshly-loaded
  `stedding/ingest_queue/tg4/` cache
- **THEN** `tg4_segments` SHALL contain one row per 30-second window
  per episode, embedded via `BAAI/bge-m3` (1024-d)
- **AND** `tg4_frame_captions` SHALL contain one row per sampled frame
  with `caption`, `has_diagram`, `has_formula`, `has_text`,
  `diagram_points`
- **AND** `tg4_triples` SHALL contain the 4 BAML fn outputs joined by
  `(pid, segment_idx)` + `(pid, frame_idx)`
- **AND** `tg4_quality_audits` SHALL contain one row per 5%-sampled
  episode with `coverage`, `disagreement_rate`, `insertion_rate`, and
  `missing_cues_count`

#### Scenario: Subtitle canonical, audio audit

- **GIVEN** an episode with a Brightcove VTT (canonical) AND a
  WhisperX transcript (audit)
- **WHEN** the App materialises
- **THEN** the `tg4_segments.transcript` column SHALL be the VTT cue
  text
- **AND** the `tg4_segments.audio_audit_transcript` column SHALL be
  the WhisperX output
- **AND** the `tg4_quality_audits` row SHALL have
  `coverage = len(intersection(vtt_cues, whisperx_segments)) /
  len(vtt_cues)`

#### Scenario: No literal HuggingFace IDs in the App

- **WHEN** `mise run lint:registry` runs against the new App
- **THEN** the audit SHALL report zero hardcoded model strings
- **AND** every backbone call SHALL route through
  `meaisinfhoghlaim.models.registry.MODEL_REGISTRY.filter(family="vision")`

### Requirement: SubtitleAudioAlignmentAudit

The system SHALL provide a BAML function `AuditTranscriptQuality` at
`baml_src/media/tg4_classification.baml` that takes (a) the canonical
Brightcove VTT transcript cues + (c) the audio-derived WhisperX
segments and produces `{coverage: float, disagreement_rate: float,
missing_cues: int[], insertion_rate: float}`. The function SHALL be
called only on the 5% sample + every NCCA-tagged lesson (per the
cost-ordering in the proposal). The output SHALL be persisted to the
`tg4_quality_audits` LanceDB table + surfaced in the marimo notebook's
"Subtitle–audio alignment" section.

#### Scenario: Audit row produced for a Nuacht TG4 episode

- **GIVEN** a `Nuacht TG4` episode with VTT cues covering 100% of the
  audio + WhisperX transcription
- **WHEN** the BAML `AuditTranscriptQuality` runs
- **THEN** `coverage` SHALL be `>= 0.95`
- **AND** `disagreement_rate` SHALL be `<= 0.10`
- **AND** the row lands in `tg4_quality_audits` + is queryable via the
  marimo notebook

#### Scenario: Audit skipped on non-NCCA episodes

- **GIVEN** a non-NCCA episode (e.g. a `Béalbhinn` music interview)
- **WHEN** the v1 App materialises
- **THEN** `AuditTranscriptQuality` SHALL NOT be called for this episode
- **AND** no `tg4_quality_audits` row SHALL be produced
- **AND** `tg4_segments.audio_audit_*` columns SHALL be NULL

### Requirement: Tg4CorpusMotherDuckDive

The system SHALL provide a MotherDuck Dive at
`motherduck/dives/tg4_corpus_overview.py` that joins
`cianfhoghlaim.tg4.player_shows` + `cianfhoghlaim.tg4.foghlaim_lessons`
+ `tg4_quality_audits` for analytics: total episode count per genre,
total lesson count per `biep_stage`, total lesson count per
`biep_subject`, dialect distribution per series, alignment coverage
distribution, top-20 keywords across all lessons. The Dive SHALL be
added as a tab in `notebooks/00_control_panel.py` (the 5-tab marimo
control panel) and surfaced in `notebooks/41_tg4_foghlaim_corpus.py`
section 1 (catalogue overview).

#### Scenario: Dive renders 6 KPIs

- **WHEN** a user opens the Dive at
  `md:cianfhoghlaim.tg4_corpus_overview`
- **THEN** the Dive SHALL display 6 KPIs (total shows, total lessons,
  total NCCA-tagged lessons, median alignment coverage, total dialect
  distribution, top subject)
- **AND** a date-range filter SHALL scope all 6 KPIs

#### Scenario: Marimo notebook section 1 renders real data

- **GIVEN** the Dive has been materialised
- **WHEN** `marimo edit notebooks/41_tg4_foghlaim_corpus.py` opens
- **THEN** section 1 (catalogue overview) SHALL render against the
  Dive via `mo.sql(engine=md:cianfhoghlaim)`
- **AND** section 3 (subtitle–audio alignment) SHALL render against the
  `tg4_quality_audits` table

## Cross-references

- [`british-isles-education-pipeline-v3`](../british-isles-education-pipeline-v3/spec.md)
  — the destination spec for the 2 ADDED Requirements that join TG4 +
  Foghlaim into the BIEP v3 subject taxonomy
- [`multimodal-code-and-media-intel`](../multimodal-code-and-media-intel/spec.md)
  — the sibling capability (Phase 1 = YouTube KG, Phase 5 = local
  media); TG4 sits alongside these as a 3rd pillar
- [`celtic-language-pipeline`](../celtic-language-pipeline/spec.md) —
  the downstream consumer (transcript segments feed dialect
  classifier + BAML grammar patterns)
- [`official-media-pipeline`](../official-media-pipeline/spec.md) —
  the structural twin (Instagram-export → DLT → BAML → resolver)