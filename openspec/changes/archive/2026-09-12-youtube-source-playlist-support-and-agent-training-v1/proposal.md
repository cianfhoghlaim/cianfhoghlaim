# Change: YouTube source playlist-scoped support + HuggingFace & Google Cloud agent training corpus

## Why

The existing `dlt_sources/api_sources/youtube_videos.py` DLT source
declares playlist support in its watchlist schema docstring
(`{channel_id, playlist_id?, max_videos?, label}` at
`youtube_videos.py:18-19`) but the implementation only honours
`channel_id` — the `_channel_video_urls` helper fetches from the
channel's `/videos` page rather than the supplied `playlist_id`. This
prevents ingestion of YouTube's most valuable unit of curation (the
playlist) and forces the source to scrape all videos on a channel to
find the curated subset.

Two specific playlists became the trigger for this change:

1. **HuggingFace Post-training Agents**
   (`https://www.youtube.com/playlist?list=PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5`)
   — 6 live workshops on agent training + evaluation, including the
   "Agentic Evaluations Workshop" (`UxMZfbWI3LY`, 1:48:46, 32K views)
   that the user explicitly requested.

2. **Google Cloud AI Agent Crash Course**
   (`https://www.youtube.com/playlist?list=PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG`)
   — 11 short tutorials on building + deploying agents with ADK +
   Cloud Run + MCP servers + Vertex AI Agent Engine. Companion to
   the HuggingFace playlist (deployment side vs training side).

The 17 videos together form a paired agent-training corpus that
crosses 2 vendors (open-source + Google Cloud), 2 stacks (transformers/
TRL/Smol-course vs ADK/Cloud Run/MCP), and 2 audience levels
(long-form workshops vs short tutorials). A cross-source BAML join
that finds concepts shared between the 2 playlists is the unique
value this change unlocks beyond mere ingestion.

## What changes

### 1. MODIFIED `dlt_sources/api_sources/youtube_videos.py` — playlist-scoped watchlist support

Three hunks in the existing 382-line file:

- **New helper `_playlist_video_urls(playlist_id, max_videos)`**
  (~25 LoC, mirror of `_channel_video_urls` but targets
  `https://www.youtube.com/playlist?list={playlist_id}`). Returns an
  iterator of video URLs in playlist order via
  `yt-dlp --flat-playlist --playlist-end`.

- **Modified main loop in `youtube_videos_source()`** (~10 LoC):
  when a watchlist entry carries `playlist_id`, dispatch to
  `_playlist_video_urls`; otherwise keep the existing
  `_channel_video_urls` behaviour. Backwards-compatible — the 4
  existing channel-only entries (3Blue1Brown, Khan Academy, TG4
  placeholder, Cúla4 placeholder) work unchanged.

- **Two new fields on `YouTubeVideoRow`** (`playlist_id: str | None`
  + `playlist_index: int | None`): populated when the row came from
  a playlist; null for the 4 existing channel-only rows. Enables the
  per-playlist subtable views.

- **New `apply_migrations()` helper** (~15 LoC): reads
  `dlt_sources/api_sources/youtube_videos_migrations.sql` and
  executes the statements idempotently on the local DuckDB the first
  time the source initialises. Version-gated via a
  `_MIGRATIONS_VERSION` constant.

### 2. NEW `dlt_sources/api_sources/youtube_videos_migrations.sql` — the subtable view layer

Idempotent SQL that creates 3 views on the existing
`cianfhoghlaim.youtube.youtube_videos` parent table:

- `youtube_huggingface_post_training_agents` — projection filtered by
  `playlist_id = 'PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5'`
- `youtube_google_cloud_ai_agent_crash_course` — projection filtered by
  `playlist_id = 'PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG'`
- `youtube_playlist_registry` — per-playlist metadata (video count,
  first/last upload, total + avg duration)

Per the user's explicit "from generic → specific via common subtable
naming" direction, the subtables share the `youtube_<playlist_slug>`
naming pattern; the generic parent has no slug. The CLI names map
1:1 to the subtable names.

### 3. MODIFIED `stedding/youtube_curated.yaml` — 2 new watchlist entries

Two new entries appended to the `channels:` list:

- `UCHlNU7kIZhRgSbhHvFoy72w` (HuggingFace) →
  `PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5` (Post-training Agents)
  with `max_videos: 6` + label `huggingface_post_training_agents`
- `UCJS9pqu9BzkAMNTmzNMNhvg` (Google Cloud Tech) →
  `PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG` (AI Agent Crash Course)
  with `max_videos: 11` + label `google_cloud_ai_agent_crash_course`

Both channel IDs + playlist IDs verified live from
`@HuggingFace/about` + `@googlecloudtech/about` + the playlist
pages themselves on 2026-09-12.

### 4. MODIFIED `dlt_sources/common/cli.py:DLT_SOURCES` — 3 new tuple entries

Adds 3 names to the 22-entry tuple: `"youtube_videos"`,
`"huggingface_post_training_agents"`,
`"google_cloud_ai_agent_crash_course"`. Wires them into the existing
`cianfhoghlaim-dlt list-sources` + `run-pipeline` CLI.

### 5. NEW `baml_src/youtube_knowledge_graph.baml` — cross-source extraction

3 classes + 2 functions for the cross-source agent-training
knowledge graph:

- `class CrossSourceConcept` (concept_name, concept_kind, hf_video_ids[],
  gc_video_ids[], confidence, source_evidence[])
- `class SnippetEvidence` (video_id, timestamp_s, snippet)
- `class CrossSourceComparison` (concept_name, hf_perspective,
  gc_perspective, agreement_pct, differences[])
- `function ExtractCrossSourceConcept(hf_video_descriptions, gc_video_descriptions) -> CrossSourceConcept[]`
- `function CompareCrossSourcePerspectives(hf_video_id, gc_video_id, shared_concept) -> CrossSourceComparison`

Routes through the existing `ExtractEn` LiteLLM client (no new
model entries — uses the existing 24-entry `VISION_MODELS` registry).

### 6. MODIFIED `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` — new LanceDB table

- New `LANCEDB_TABLE_CROSS_SOURCE_CONCEPTS = "cross_source_concepts"`
  (~5 LoC constant)
- New `CrossSourceConceptRecord` dataclass with `concept_name`,
  `concept_kind`, `hf_video_ids[]`, `gc_video_ids[]`, `confidence`,
  `source_evidence[]` fields (~25 LoC)
- New `@coco.fn(memo=True)` wrapper `extract_cross_source_concepts()`
  (~30 LoC) that calls `b.ExtractCrossSourceConcept` over all 17
  videos + persists rows to the new LanceDB table
- New LanceDB mount in `youtube_kg_embedding_app` (~10 LoC)

### 7. NEW `notebooks/case_studies/agent_training_research.py` — 4-tab marimo notebook

Reactive marimo notebook with 4 tabs:

- **HuggingFace playlist timeline** — the 6 videos sorted by upload
  date with the cross-source concept highlights
- **Google Cloud playlist timeline** — the 11 videos sorted by upload
  date with the cross-source concept highlights
- **Cross-source concepts** — the 3 classes from
  `cross_source_concepts` (concept name + hf_video_ids +
  gc_video_ids + confidence); filter by concept_kind
- **Concept deep-dive** — pick 1 concept (e.g. "agent evaluation"),
  see the `CrossSourceComparison` between the 2 best-matching videos
  (one HF, one GC)

Mounts the existing `notebooks/_shared/db.py` against the local
DuckDB at `~/Documents/cianfhoghlaim/case_studies/credential_study.duckdb`
(per the personal-scope decision).

## Why 1 change (not 7)

The 6 sub-tasks (ST-1 through ST-6) are interdependent: ST-1
(plumbing) is required for ST-2/ST-3 (data); ST-5 (cross-source join)
requires ST-2/ST-3; ST-6 (notebook) reads from ST-5. Splitting into
multiple openspec changes would force a sequencing dependency chain
in the same review cycle. One umbrella change + 6 ADDED Requirements
on `multimodal-code-and-media-intel` keeps the audit trail tight.

## Out of scope

- Scraping the entire HuggingFace or Google Cloud channel (only the
  2 specific playlists are in scope)
- New CocoIndex App (extends the existing `youtube_kg_embedding.py`
  only)
- New DLT source file (extends `youtube_videos.py` only)
- New ADK agent (the marimo notebook is the consumer surface)
- MotherDuck hand-off (stays in the local DuckDB per the personal-scope
  decision)
- Bilingual EN + GA processing (both playlists are English-only)
- New openspec spec (modifies the existing
  `multimodal-code-and-media-intel` spec only)

## Dependencies

None — this change is independent of the other 78 pending changes.
It does not block any other change.

## Impact

### Affected specs

- **MODIFIED** `multimodal-code-and-media-intel` — 3 ADDED Requirements:
  1. "playlist-scoped watchlist entries"
  2. "playlist subtable views"
  3. "cross-source concept extraction (HuggingFace ↔ Google Cloud)"

### Affected code/config

- `openspec/changes/2026-09-12-youtube-source-playlist-support-and-agent-training-v1/proposal.md` — NEW
- `openspec/changes/2026-09-12-youtube-source-playlist-support-and-agent-training-v1/tasks.md` — NEW
- `openspec/changes/2026-09-12-youtube-source-playlist-support-and-agent-training-v1/specs/multimodal-code-and-media-intel/spec.md` — NEW (the delta)
- `dlt_sources/api_sources/youtube_videos.py` — MODIFY (~55 LoC net)
- `dlt_sources/api_sources/youtube_videos_migrations.sql` — NEW (~30 LoC)
- `stedding/youtube_curated.yaml` — MODIFY (~50 LoC net addition)
- `dlt_sources/common/cli.py` — MODIFY (3 tuple entries)
- `baml_src/youtube_knowledge_graph.baml` — NEW (~80 LoC)
- `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` — MODIFY (~70 LoC net)
- `notebooks/case_studies/agent_training_research.py` — NEW (~200 LoC)

### Numbers

- Files touched: 9 (5 modified, 4 new)
- LoC net: ~485 (excluding the openspec proposal + tasks.md + spec delta)
- New CocoIndex LanceDB tables: 1 (`cross_source_concepts`)
- New DLT CLI names: 3 (`youtube_videos`,
  `huggingface_post_training_agents`,
  `google_cloud_ai_agent_crash_course`)
- New DuckDB views: 3 (2 subtables + 1 playlist registry)
- New BAML classes: 3
- New BAML functions: 2
- New marimo notebooks: 1

## Cross-references

- `openspec/specs/multimodal-code-and-media-intel/spec.md` — the
  modified spec (5 v1 Apps including `YoutubeKgEmbedding`)
- `dlt_sources/api_sources/youtube_videos.py:18-19` — the watchlist
  schema docstring that already declared `playlist_id?`
- `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py:80` —
  `YOUTUBE_VIDEOS_DUCKLAKE_TABLE = "cianfhoghlaim.youtube.youtube_videos"`
  (the parent table the new views project from)
- `dlt_sources/common/cli.py:DLT_SOURCES` — the existing 22-entry
  CLI tuple (will become 25)
- `baml_src/_shared/` — the canonical BAML client home (the new
  `youtube_knowledge_graph.baml` lives alongside the existing
  `media_intel_*.baml` siblings)
