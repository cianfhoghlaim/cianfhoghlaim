## ADDED Requirements

### Requirement: playlist-scoped watchlist entries

The `dlt_sources/api_sources/youtube_videos.py` DLT source SHALL
honour the `playlist_id?` field on each watchlist entry (declared in
the schema docstring at `youtube_videos.py:18-19` since 2026-07-29 but
not previously consumed by `_channel_video_urls`). When a watchlist
entry carries a `playlist_id`, the source SHALL dispatch to a new
`_playlist_video_urls(playlist_id, max_videos)` helper that targets
`https://www.youtube.com/playlist?list={playlist_id}` via
`yt-dlp --flat-playlist --playlist-end`. The existing
`_channel_video_urls` behaviour SHALL remain the fallback for the 4
pre-existing channel-only watchlist entries (3Blue1Brown, Khan
Academy, TG4 placeholder, Cúla4 placeholder).

The `YouTubeVideoRow` dataclass SHALL gain 2 new nullable fields —
`playlist_id: str | None` + `playlist_index: int | None` — populated
when the row came from a playlist; null for the 4 channel-only rows.
The DuckLake write disposition SHALL remain `merge` + primary key
`video_id` so the new columns auto-evolve without a separate
migration.

#### Scenario: A HuggingFace playlist entry is ingested

- **GIVEN** `stedding/youtube_curated.yaml` carries a new entry with
  `channel_id: UCHlNU7kIZhRgSbhHvFoy72w` +
  `playlist_id: PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5` +
  `max_videos: 6`
- **WHEN** `python -m dlt_sources.api_sources.youtube_videos` runs
- **THEN** 6 rows SHALL land in `cianfhoghlaim.youtube.youtube_videos`
- **AND** every row SHALL have `playlist_id =
  "PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5"`
- **AND** the `playlist_index` field SHALL match the playlist order
  (1 for the first video `UxMZfbWI3LY`, 6 for the last)

### Requirement: playlist subtable views

The system SHALL provide a "generic → specific via common subtable
naming" pattern for YouTube data: 1 generic parent table
(`cianfhoghlaim.youtube.youtube_videos`, existing) + 1 subtable per
playlist, all under the existing `cianfhoghlaim.youtube` DuckLake
schema. The subtable naming pattern SHALL be
`youtube_<playlist_slug>` where `<playlist_slug>` is the lowercase,
snake-cased playlist label from the watchlist YAML. The generic
parent table SHALL have no slug.

Each playlist subtable SHALL be a DuckDB view (not a materialised
copy) that filters the parent by `playlist_id`. The system SHALL
also expose a `youtube_playlist_registry` view that returns 1 row per
playlist with the playlist metadata (video count, first/last upload,
total + avg duration).

The subtable views SHALL be created idempotently by a new
`dlt_sources/api_sources/youtube_videos_migrations.sql` file that
runs on first source initialisation via the `apply_migrations()`
helper. The CLI names `huggingface_post_training_agents` +
`google_cloud_ai_agent_crash_course` SHALL map 1:1 to the 2 subtable
view names (`youtube_huggingface_post_training_agents` +
`youtube_google_cloud_ai_agent_crash_course`).

#### Scenario: The 3 views are created idempotently

- **WHEN** `apply_migrations()` runs on a fresh local DuckDB
- **THEN** `cianfhoghlaim.youtube.youtube_huggingface_post_training_agents`
  SHALL exist as a view containing 6 rows
- **AND** `cianfhoghlaim.youtube.youtube_google_cloud_ai_agent_crash_course`
  SHALL exist as a view containing 11 rows
- **AND** `cianfhoghlaim.youtube.youtube_playlist_registry` SHALL
  exist as a view containing 2 rows (1 per playlist)
- **AND** re-running `apply_migrations()` SHALL NOT error (the
  statements use `IF NOT EXISTS`)

### Requirement: cross-source concept extraction (HuggingFace ↔ Google Cloud)

The `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` CocoIndex
App SHALL expose a new LanceDB table `cross_source_concepts` (sibling
to the existing `video_segments` + `video_frame_captions` +
`video_triples`). One row per concept, with the 6 fields
`concept_name`, `concept_kind`, `hf_video_ids[]`, `gc_video_ids[]`,
`confidence`, `source_evidence[]`. The cross-source extraction SHALL
use 2 new BAML functions defined in
`baml_src/youtube_knowledge_graph.baml`:

- `ExtractCrossSourceConcept(hf_video_descriptions, gc_video_descriptions) -> CrossSourceConcept[]`
- `CompareCrossSourcePerspectives(hf_video_id, gc_video_id, shared_concept) -> CrossSourceComparison`

The 3 new BAML classes SHALL be `CrossSourceConcept`,
`SnippetEvidence`, `CrossSourceComparison`. The 2 functions SHALL
route through the existing `ExtractEn` LiteLLM client (no new model
entries — uses the existing 24-entry `VISION_MODELS` registry).

The extraction SHALL run over the 17 videos from the 2 playlists
(6 HuggingFace + 11 Google Cloud) and SHALL yield ≥3 cross-source
concepts at minimum (e.g. "agent evaluation", "MCP server", "ADK").

#### Scenario: A user queries for shared concepts

- **GIVEN** the `cross_source_concepts` LanceDB table has ≥3 rows
  with both `hf_video_ids` AND `gc_video_ids` populated
- **WHEN** the user opens the
  `notebooks/case_studies/agent_training_research.py` marimo notebook
  Tab 3
- **THEN** ≥3 cross-source concepts SHALL render
- **AND** each concept SHALL show its `confidence` score + the
  specific video_ids from each playlist that mention it

#### Scenario: A concept deep-dive renders the comparison

- **WHEN** the user picks 1 concept (e.g. "agent evaluation") in
  Tab 4 of the marimo notebook
- **THEN** the notebook SHALL call
  `b.CompareCrossSourcePerspectives(hf_video_id, gc_video_id, shared_concept)`
- **AND** render the `CrossSourceComparison` row showing
  `hf_perspective`, `gc_perspective`, `agreement_pct`, `differences[]`
- **AND** each side SHALL cite a specific video_id + timestamp from
  the 2 playlists
