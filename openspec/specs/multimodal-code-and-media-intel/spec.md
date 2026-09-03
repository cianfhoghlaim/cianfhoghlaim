# `multimodal-code-and-media-intel` Specification

## Purpose

`multimodal-code-and-media-intel` is a capability of the Cianfhoghlaim
platform. It fuses 5 new CocoIndex v1 Apps — YouTube tutorial ingest,
package changelog scraping, git history alongside repo code,
RepoSwarm-style `.arch.md` generation, and local media (game captures +
downloaded audio) — behind one multi-hop-searchable knowledge graph that
closes the 4 surviving gaps from the archived `códeolas` project (last
commit 2026-06-26).

The corresponding source code lives at `cianfhoghlaim/cocoindex/` (5
new v1 Apps + 4 Phase 0 primitives) + `cianfhoghlaim/dlt/api_sources/`
(4 new DLT sources) + `cianfhoghlaim/baml_src/processing/_shared/` (4
new BAML files) + `cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/`
(5 new L3 Component defs) + the `cocoindex-code` MCP server (3 new
tools).
## Requirements
### Requirement: The system SHALL provide 5 v1 CocoIndex Apps that fan into a shared multi-hop search layer

The system SHALL provide 5 new CocoIndex v1 Apps, each R1+R2+R3+R4
conformant, mounted as `CelticModelLifecycleComponent` L3 defs under
`cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/`. Each
App SHALL fan into the shared `multihop_search` `@coco.fn(memo=True)`
primitive so that one MCP-level `multihop_search(question, limit=10)`
call can synthesize answers across all 5 Apps + the existing
`codebase_chunks` + `leabharlann_chunks` tables.

The 5 Apps are:

1. `YoutubeKgEmbedding` (Phase 1) — ingests curated YouTube channels
   via yt-dlp + WhisperX + `qwen3-vl-8b` frame captioning +
   `molmo2-8b` diagram pointing + 3 BAML fns (`ExtractVideoKnowledgeTriple`,
   `ExtractConceptChain`, `ExtractFrameSequence`). Mounts 3 LanceDB
   tables: `video_segments`, `video_frame_captions`, `video_triples`.

2. `PackageChangelogEmbedding` (Phase 2) — ingests PyPI + npm + CRAN
   package releases via dlt `rest_api` + Firecrawl MCP + 2 BAML fns
   (`ExtractChangelogEntry`, `ExtractAPIDiff`) routed through
   `qwen3.6-27b-mtp`. Mounts 2 LanceDB tables: `package_changelog_chunks`,
   `package_changelog_diffs`.

3. `CodebaseGitHistory` (Phase 3) — shells `git log` + `git blame` to
   ingest commit messages + blame regions + per-author churn. Extends
   the existing `codebase_graph` App's 7-edge schema with 2 new edges
   (`AUTHORED_BY`, `TOUCHED_IN`). Mounts 2 LanceDB tables:
   `codebase_git_commits`, `codebase_git_blame_regions`.

4. `RepoArchDocs` (Phase 4, the RepoSwarm revival) — reads
   `codebase_index` + `codebase_graph` + `codebase_git_history` tables;
   runs the 4 BAML fns (`ExtractOverview`, `ExtractComponents`,
   `ExtractDataLayer`, `ExtractDependencies`) via
   `qwen3.6-27b-mtp` (primary) / `gemma-4-26B-A4B` (fallback); emits
   a `.arch.md` file per `(repo_path, git_sha)` cached tuple. Mounts
   1 LanceDB table: `repo_arch_docs`.

5. `MediaLocalEmbedding` (Phase 5) — ingests local `.mp4`/`.mkv`/
   `.webm`/`.mp3`/`.wav`/`.m4a`/`.ogg` files from
   `stedding/ingest_queue/media/` via WhisperX + `qwen3-vl-8b` +
   `molmo2-8b` + 2 BAML fns (`ExtractGameplaySequence`,
   `ExtractPlayerCommentary`) + the existing
   `baml_src/processing/_shared/music_genre.baml`. Mounts 3 LanceDB
   tables: `media_segments`, `media_frame_captions`, `media_triples`.

#### Scenario: One MCP call fans across all 5 Apps

- **GIVEN** a developer opens the `cianfhoghlaim-web` TanStack Start UI and
  invokes the `cocoindex-code.multihop_search` MCP tool with the
  question `"How does the cianfhoghlaim Lakehouse stack relate to the
  3Blue1Brown linear-algebra tutorial?"`
- **WHEN** the tool runs with `limit=10, max_iterations=3,
  convergence_threshold=0.05`
- **THEN** the `multihop_search` `@coco.fn(memo=True, as_async)`
  primitive fans out to all 7 tables (5 new + 2 existing)
- **AND** returns `{ answer: string, sources: { table, row_id,
  citation }[] }` with citations spanning at least 2 of the 7 tables
- **AND** if the candidate-set size converges within 3 iterations the
  Langfuse v3 span `multihop.iteration.<n>` records
  `convergence_score=<threshold>`

### Requirement: All 5 Apps MUST dispatch through the canonical OCR/VLM registry

All model calls SHALL route through the
`ocianfhoghlaim.meaisinfhoghlaim.models.registry.VISION_MODELS`
24-entry registry (Unsloth-first fallback chain: `unsloth_id` → `mlx_id`
→ `upstream_id`). No App SHALL introduce a new HuggingFace dependency
or a new ML client. No App SHALL call a cloud API directly (the v4
spec explicitly dropped `OPENAI` and `ANTHROPIC` from the canonical
backend list).

#### Scenario: An M4 Max 48 GB deployment uses Unsloth GGUF

- **GIVEN** the `bunchloch` MacBook M4 Max deployment runs the
  `YoutubeKgEmbedding` App
- **WHEN** the App calls `qwen3-vl-8b` for frame captioning
- **THEN** the registry returns the `unsloth_id` first
  (`unsloth/Qwen3-VL-8B-Instruct-GGUF`) and falls back to the
  `mlx_id` (`mlx-community/Qwen3-VL-8B-Instruct-4bit`) if Unsloth is
  unavailable
- **AND** no App-level code mentions a HuggingFace ID literally

### Requirement: Audio transcription SHALL route through the existing WhisperX aligner

All audio-bearing Apps MUST reuse the existing
`meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner` for
transcription, and SHALL NOT introduce a new ASR backend.

#### Scenario: A YouTube video's audio is transcribed

- **GIVEN** a curated 3Blue1Brown video `video_id = "spUNpyF58BY"`
  (Strang's "Essence of Linear Algebra" episode 1) is downloaded to
  `stedding/ingest_queue/youtube/spUNpyF58BY.mp4`
- **WHEN** the `YoutubeKgEmbedding` App processes it
- **THEN** the App extracts the audio stream via `ffmpeg -vn -c:a copy`
  to a temp `.m4a`
- **AND** the temp `.m4a` is passed to `WhisperXAligner.align()` per
  the `transcript_aligner.py` API
- **AND** the resulting per-segment transcript + word-level timestamps
  are stored as 1 row in `video_segments` (one row per 30-second
  segment)

### Requirement: The 5 new cognify datasets SHALL register alongside the existing 7

The system SHALL register 5 new cognify datasets — `multimedia_kg`,
`package_changelog`, `codebase_git_history`, `media_local`,
`repo_arch_docs` — under `cianfhoghlaim/cognify/datasets/` following
the existing `cianfhoghlaim_cognify_*` pattern. Each dataset SHALL be
cognified on the same daily schedule as the existing 7 cognify clusters
(per the `cianfhoghlaim-cognify-knowledge-graph` spec).

#### Scenario: A new video is cognified

- **GIVEN** the `video_triples` LanceDB table has ≥10 new rows from a
  3Blue1Brown episode materialization
- **WHEN** the `cognify_multimedia_kg` Dagster asset materialises on
  the daily cron
- **THEN** the BAML-extracted triples are loaded into the Cognee
  knowledge graph alongside the existing `cianfhoghlaim_cognify_*` clusters
- **AND** a Graphiti episode is appended with the `source_kind =
  "youtube_kg"` marker for bi-temporal tracking

### Requirement: Multimodal rollout is deferred until CocoIndex factory dedup pattern lands

The system SHALL defer the multimodal CocoIndex rollout (4 streams:
youtube_kg, package_changelog, codebase_git_history, repo_arch_docs)
until the CocoIndex factory dedup pattern (centralized-model-schema-registry
Phase 7) lands. The 10 tasks already shipped (Phase 0 codeolas primitives +
Phase 1.1-1.5 partial youtube_kg) remain in place; the 40 remaining tasks
are tracked under this deferred requirement.

#### Scenario: operator checks the multimodal deferral state

- **WHEN** the operator runs `openspec list` and finds
  `multimodal-code-and-media-intel` archived
- **THEN** the canonical spec at `openspec/specs/multimodal-code-and-media-intel/spec.md`
  SHALL show this deferral requirement
- **AND** the 4 base requirements (5 v1 Apps + OCR/VLM registry + WhisperX + 7+5 cognify)
  SHALL remain in the canonical spec

## Cross-references

- `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md` — the R1+R2+R3+R4
  conformance contract that all 5 new Apps satisfy
- `openspec/specs/celtic-asset-generation/spec.md` — the 5-stage Celtic-asset
  pipeline that Stream 5 (`media_local_embedding.py`) + Stream 1
  (`youtube_kg_embedding.py`) feed into as asset-generation consumers
- `openspec/specs/indexing-and-cognition/spec.md` — the existing
  `cocoindex-code` MCP server (the surface for the 3 new MCP tools)
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — DLT orchestration registration
- `openspec/specs/cianfhoghlaim-baml-schemas/spec.md` — BAML schema registration
- `openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` — cognify
  dataset pattern (the existing `cianfhoghlaim_cognify_*` siblings)
- `openspec/specs/retro-game-design-catalogue/spec.md` — the canonical
  game-capture spec; Stream 5 is the player-content sibling
- `.agents/skills/cocoindex/SKILL.md` — R1+R2+R3+R4 + `_lifespan.py`
- `.agents/skills/baml/references/multimodal-vision.md` — BAML multimodal
  primitives
- `stedding/dev/cianfhoghlaim copy/sruth/códeolas/` — the archived source of
  truth for Phase 0 primitives (`multihop_search`, `reranker`,
  `RepoTypeDetector`, `ArchDocCache`)