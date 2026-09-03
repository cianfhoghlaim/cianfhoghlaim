## Deferred — Blocked on CocoIndex factory dedup pattern (centralized-model-schema-registry Phase 7)

This change is **deferred**. The 40 remaining tasks (Phases 1.6 - 4.6 across 4 streams: youtube_kg, package_changelog, codebase_git_history, repo_arch_docs) require the CocoIndex factory dedup pattern that is Phase 7 of the centralized-model-schema-registry change, which was itself explicitly deferred per its tasks.md header note.

The 10 completed Phase 0 + Phase 1.1-1.5 tasks (4 codeolas primitive ports + 1 partial youtube_kg CocoIndex flow) shipped via commits `1afc4201f` (CocoIndex sruth/ cleanup) + `4f676a65b` (V1_APPS dynamic + BIEP v3 clients reconcile) + the parallel-session work.

Per the original plan (`2026-07-14-multimodal-code-and-media-intel-v1` proposal.md Phase 4.5: "End-to-end smoke test: run the App on the cianfhoghlaim repo"), the 4-stream CocoIndex rollout is a substantial feature delivery (4 DLT sources + 4 BAML classes + 4 CocoIndex v1 Apps + 4 L3 Component definitions + 4 asset files + 4 CocoIndex quality gates + 1 smoke test) that should be a dedicated wave once the CocoIndex factory dedup pattern lands.

## Follow-up

When the CocoIndex factory dedup pattern lands (centralized-model-schema-registry-v1 Phase 7 follow-up), reopen this change and complete:
- Stream 1 (YouTube Knowledge Graph): 5 tasks (1.6-1.7, video_kg CocoIndex completion)
- Stream 2 (Package Changelog): 6 tasks (2.1-2.6)
- Stream 3 (Codebase Git History): 6 tasks (3.1-3.6)
- Stream 4 (Repo Arch Docs): 6 tasks (4.1-4.6)
- End-to-end smoke test: 4.5
# 2026-07-14-multimodal-code-and-media-intel-v1

## Why

Closes the 4 surviving gaps from the archived `códeolas` project
(`stedding/dev/cianfhoghlaim copy/sruth/códeolas/`, last commit 2026-06-26) by
shipping **5 new CocoIndex v1 Apps** that fuse YouTube video tutorials,
package changelogs, git history, repo architecture docs, and local media
(game captures + downloaded audio) into one multi-hop-searchable knowledge
graph. Each App is R1+R2+R3+R4 conformant, dispatches through the existing
`ocianfhoghlaim.meaisinfhoghlaim.models.registry.VISION_MODELS` (24
backbones, all already shipped), and is mounted as a new
`CelticModelLifecycleComponent` L3 defs.yaml.

The headline outcome: a single MCP tool call
(`cocoindex-code.multihop_search("How does the cianfhoghlaim Lakehouse
relate to the 3Blue1Brown linear-algebra tutorial?"`) returns a synthesised
answer grounded in **code AST triples + commit-intent triples + package
changelog triples + video frame triples + local-media triples**, all fused
behind one LanceDB-backed `multihop_search` `@coco.fn(memo=True)`.

## What Changes

This change ships 5 new CocoIndex v1 Apps + 4 Phase 0 primitives:

- **NEW**: `multihop_search`, `reranker`, `repo_type_detector`,
  `arch_doc_cache` CocoIndex v1 primitives (Phase 0) ported from the
  archived codeolas `search/multihop.py`, `search/reranker.py`,
  `generators/reposwarm/detector.py`, `generators/reposwarm/cache.py`
- **NEW**: `YoutubeKgEmbedding` App (Phase 1) — yt-dlp + WhisperX +
  Qwen3-VL-8B + Molmo2-8B + 3 BAML fns → 3 LanceDB tables
- **NEW**: `PackageChangelogEmbedding` App (Phase 2) — PyPI/npm/CRAN +
  Firecrawl MCP + Qwen3.6-27B-MTP + 2 BAML fns → 2 LanceDB tables
- **NEW**: `CodebaseGitHistory` App (Phase 3) — local git connector +
  Qwen3.6-27B-MTP + 1 BAML fn + 2 new graph edges (AUTHORED_BY,
  TOUCHED_IN) → 2 LanceDB tables
- **NEW**: `RepoArchDocs` App (Phase 4, the RepoSwarm revival) — 4 BAML
  fns (Overview / Components / Data Layer / Dependencies) + Mermaid
  diagram + DuckDB-by-git-SHA cache → 1 LanceDB table + `.arch.md` files
- **NEW**: `MediaLocalEmbedding` App (Phase 5) — ffmpeg + WhisperX +
  Qwen3-VL-8B + Molmo2-8B + 2 BAML fns + existing music_genre.baml →
  3 LanceDB tables
- **NEW**: 3 MCP tools on the existing `cocoindex-code` server:
  `multihop_search`, `rerank_query`, `arch_doc_for_repo`
- **NEW**: 5 cognify datasets under `cognify/datasets/`
- **NEW**: 1 marimo mission-control notebook
- **NEW**: 4 DLT sources (`youtube_videos.py`, `package_docs.py`,
  `local_media_files.py`, ...), 5 BAML schema files
  (`video_kg.baml`, `package_changelog.baml`, `git_intent.baml`,
  `repo_arch_summary.baml`, `gameplay_sequence.baml`), 5 L3
  `CelticModelLifecycleComponent` `defs.yaml` + `_assets.py`

## Capabilities

### New Capabilities
- `multimodal-code-and-media-intel`: 5 new CocoIndex v1 Apps +
  multi-hop search + RepoSwarm-style arch doc generation +
  video/package-doc/git-history/local-media knowledge graph fusion
  behind a unified MCP-level `multihop_search` tool

### Modified Capabilities
- `cianfhoghlaim-cocoindex-v1-migration`: the R1+R2+R3+R4 conformance
  registry gets 5 new v1 Apps + 4 new Phase 0 primitives added
- `celtic-asset-generation`: Stream 5 (`media_local_embedding.py`) +
  Stream 1 (`youtube_kg_embedding.py`) become asset-generation
  consumers
- `indexing-and-cognition`: the `cocoindex-code` MCP server gets 3 new
  tools (`multihop_search`, `rerank_query`, `arch_doc_for_repo`) — total
  rises from 9 to 12 tools
- `cianfhoghlaim-pipeline`: register the 4 new DLT sources + 5 new BAML
  schemas
- `cianfhoghlaim-baml-schemas`: register the 5 new BAML files

## Impact

- **cianfhoghlaim/**: 27 new files (5 v1 Apps + 4 Phase 0 primitives +
  4 DLT sources + 5 BAML files + 5 L3 Component defs.yaml + 5 _assets.py
  + 3 MCP tools + 5 cognify datasets + 1 marimo notebook — some in shared
  dirs)
- **bonneagar/**: no changes
- **leabharlann/**: no changes
- **opencode.json**: 3 new MCP tool grants to all sruth-subagents
- **agent time**: Phase 0–5 each take 4–8 hours of agent time; total
  ~30 hours across 6 phases

## Motivation

The original `códeolas` (archived 2026-06-26) shipped a `CodebaseAnalyzer`
public API for indexing code repos with Tree-sitter chunking + BGE-M3
embeddings + LanceDB storage. After the 2026-06-28 v4 consolidation
(`2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`), the code-indexing
piece was correctly migrated to `cocoindex/codebase_indexing.py`
(the canonical v1 `CodebaseIndex` App), but **4 surviving subsystems never
made it across**:

1. **Video + audio KG pipeline** — the round-8 merge map
   (`openspec/changes/archive/2026-06-23-sync-skills-from-docs-round-8/MERGE_MAP.md`
   line 102) referenced a 482-line "Multimodal Video Knowledge Graph
   Pipeline" doc (yt-dlp + WhisperX + Qwen3-Omni → KG) that was assigned
   to `celtic-asset-generation/references/multimodal-video-kg.md`; that
   skill folder did not survive v4 and the reference doc itself was lost.
   The `croilar-portfolio` openspec proposal mentioned `youtube_ingestion`
   as a would-be music-pipeline asset but never shipped.
2. **RepoSwarm-style `.arch.md` generation** — the archive had
   `RepoSwarmGenerator` with `RepoTypeDetector` (FRONTEND | BACKEND |
   DATA_PIPELINE) + 4 LLM-generated sections (Overview / Components /
   Data Layer / Dependencies) + DuckDB-by-git-SHA cache. This was lost in
   the v4 cleanup. `openspec/specs/indexing-and-cognition/spec.md` line 60
   still references a `codebase_architecture_docs` Dagster asset (a
   CocoIndex v1 stub-named surface), but the asset itself does not exist.
3. **Git history alongside repo code** — `codebase_indexing.py` indexes
   file snapshots; nothing indexes commit messages + blame regions +
   author churn or fuses them with the existing 7-edge AST graph.
4. **Local media + game-capture stream** — `retro-game-design-catalogue`
   covers the headless-emulator path (libretro + SAM3 + Molmo2-8B), and
   `apple_photos_*` covers photos; **no player-capture / live-recording
   stream exists**. Croilar portfolio's `music__*` assets only handle
   metadata + R2 staging, no audio content analysis.

The user explicitly asked: *"there was a different sruth of our project
called codeolas that at one point was going to be able to gather important
youtube videos process them alongside package docs and github repo code
and git analysis to help understanding for agentic context"*. This change
ships the 4 surviving gaps + 1 adjacent gap (package changelogs) as one
unified openspec change.

## What changes

### Phase 0 — Port the archived codeolas primitives (~6 files, ~4 h)

Revive the 4 archived codeolas subsystems as **CocoIndex v1 native
primitives** (no `@cocoindex.flow_def`, no `LanceCatalog`, no
`MemgraphClient` — every primitive is wrapped as `@coco.fn(memo=True)` or a
`ContextKey`):

| Archived codeolas file | New v1 primitive |
|:--|:--|
| `search/multihop.py:multihop_search(analyzer, question, max_sources=15, max_iterations=3, convergence_threshold=0.05)` | `cocoindex/multihop_search.py` — `@coco.fn(memo=True, as_async) async def multihop_search(question, limit=10, max_iterations=3, convergence_threshold=0.05)` over the 5 new LanceDB tables + the existing `codebase_chunks` + `leabharlann_chunks`. Convergence log line emitted to Langfuse v3 |
| `search/reranker.py:rerank_results(query, results, provider, api_key, model, top_n)` | `cocoindex/reranker.py` — `RERANKER` `ContextKey` wrapping Jina (default) / Cohere / Aliyun; `query_reranker(query, results, top_n)` `@coco.fn(memo=True)` |
| `generators/reposwarm/detector.py:RepoTypeDetector.detect()` | `cocoindex/repo_type_detector.py` — `@coco.fn(memo=True) async def detect_repo_type(repo_path)` returning one of `FRONTEND \| BACKEND \| LIBRARY \| DATA_PIPELINE \| MONOREPO` |
| `generators/reposwarm/cache.py:ArchDocCache(cache_config).get(repo_path, git_sha)` | `cocoindex/arch_doc_cache.py` — DuckDB-by-git-SHA cache (`memory_facade/duckdb` stack) keyed by `(repo_path, git_sha, repo_type)`; `(cached, doc)` tuple API |

### Phase 1 — Stream 1: `youtube_kg_embedding.py` (~5 files, ~6 h)

| File | Purpose |
|:--|:--|
| `dlt/api_sources/youtube_videos.py` | DLT source: takes `stedding/youtube_curated.yaml` (curated channel / playlist URLs) → for each video: `yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best --write-info-json --write-auto-sub` → MP4 to `stedding/ingest_queue/youtube/<video_id>.mp4`; metadata row emitted |
| `baml/processing/_shared/video_kg.baml` | `class KnowledgeTriple { subject string; verb string; object string; triple_kind: Concept \| Definition \| Example \| Formula \| VisualSequence; confidence float }`; `class ConceptChain { triples KnowledgeTriple[]; chain_summary string; prerequisites string[] }`; 3 BAML fns: `ExtractVideoKnowledgeTriple(video_id, transcript: str, frame_captions: list[str]) -> KnowledgeTriple[]`, `ExtractConceptChain(triples: KnowledgeTriple[], video_id) -> ConceptChain`, `ExtractFrameSequence(video_id, frame_paths: list[str], fps_sampled: float) -> VisualSequence` |
| `cocoindex/youtube_kg_embedding.py` | CocoIndex v1 App `YoutubeKgEmbedding` — reads `youtube_videos` DuckLake table → for each video: `WhisperXAligner` for audio transcript (reuses `meaisinfhoghlaim/process/transcript_aligner.py`); frame samples every 10 s via `ffmpeg -vf fps=1/10`; `qwen3-vl-8b` captions each frame (256-token frame absorption, 119 langs incl. Irish); `molmo2-8b` for diagram-pointing on slides where formula/figure detected; BAML `ExtractVideoKnowledgeTriple` + `ExtractConceptChain` + `ExtractFrameSequence`; mounts 3 LanceDB tables: `video_segments` (per-clip metadata + audio transcript) + `video_frame_captions` (per-frame caption + bbox) + `video_triples` (typed knowledge triples) |
| `orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/defs.yaml` | L3 `CelticModelLifecycleComponent` mount, `app_name=YoutubeKgEmbedding`, `module=cianfhoghlaim.cocoindex.youtube_kg_embedding`, `hnsw_index=true`, `conformance_required=true` |
| `orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/_assets.py` | 3 Dagster assets: `youtube_video_segments`, `youtube_video_frame_captions`, `youtube_video_triples` (all `is_virtual=True`, mirror the L1 upstream) |

**Reuses existing**: `soundcloud_downloader.py:yt-dlp` invocation pattern; `transcript_aligner.py:WhisperXAligner`; `_lifespan.py:EMBEDDER` (BGE-M3); `qwen3-vl-8b` + `molmo2-8b` from `VISION_MODELS`.

### Phase 2 — Stream 3: `package_changelog_embedding.py` (~5 files, ~5 h)

| File | Purpose |
|:--|:--|
| `dlt/api_sources/package_docs.py` | DLT source: per-package (from `stedding/package_watchlist.yaml` — list of `{ecosystem, name, homepage, docs_url}` tuples): PyPI `GET /pypi/<pkg>/json` for release metadata + `GET /pypi/<pkg>/<version>/json` for each release; Firecrawl MCP scrape of `docs_url` for changelog page; emits 2 resource rows per release |
| `baml/processing/_shared/package_changelog.baml` | `class ChangelogEntry { package string; from_version string; to_version string; summary string; action_verb: ADDED \| REMOVED \| DEPRECATED \| FIXED \| CHANGED; breaking bool; semver_kind: major \| minor \| patch }`; `class APIDiff { symbol string; signature_before string?; signature_after string?; diff_kind: ADDED \| REMOVED \| CHANGED \| RENAMED; docs_url string? }`; 2 BAML fns: `ExtractChangelogEntry(changelog_md: str, package, from_v, to_v) -> ChangelogEntry[]` + `ExtractAPIDiff(api_docs_md: str, package, version) -> APIDiff[]` (both via `qwen3.6-27b-mtp`) |
| `cocoindex/package_changelog_embedding.py` | CocoIndex v1 App `PackageChangelogEmbedding` — mounts 2 LanceDB tables: `package_changelog_chunks` (changelog entry rows, BGE-M3 1024-d) + `package_changelog_diffs` (typed `APIDiff` rows, BGE-M3 1024-d) |
| `.../cocoindex_v1/package_changelog/defs.yaml` | L3 Component mount |
| `.../cocoindex_v1/package_changelog/_assets.py` | 2 Dagster assets |

**Reuses existing**: `upstream_blog_monitor.py:Firecrawl` invocation; `_lifespan.py:EMBEDDER`; `qwen3.6-27b-mtp` from `VISION_MODELS`.

### Phase 3 — Stream 4: `codebase_git_history.py` (~4 files, ~6 h)

| File | Purpose |
|:--|:--|
| `cocoindex/codebase_git_history.py` | CocoIndex v1 App `CodebaseGitHistory` — local-git source connector (custom `@coco.fn` that shells `git log --pretty=format:'%H|%ae|%at|%s'` + `git blame --line-porcelain`); embeds per-commit (subject + diff stats + LLM-classified intent) + per-blame-region (region text + author + commit SHA chain); mounts 2 LanceDB tables: `codebase_git_commits` + `codebase_git_blame_regions`. Extends the existing `codebase_graph` App's 7-edge schema with **2 new edges**: `AUTHORED_BY` (function|file → author email) + `TOUCHED_IN` (file → commit SHA) |
| `baml/processing/_shared/git_intent.baml` | `class CommitIntent { sha string; author_email string; intent_kind: feat \| fix \| refactor \| docs \| test \| chore \| perf \| revert; risk_level: low \| medium \| high; touches_files: string[]; summary string }`; 1 BAML fn: `ExtractCommitIntent(commit_subject: str, diff: str, files_touched: list[str]) -> CommitIntent` (via `qwen3.6-27b-mtp`, the 8 intent kinds mirror the AGENTS.md repo conventions) |
| `.../cocoindex_v1/codebase_git_history/defs.yaml` | L3 Component mount |
| `.../cocoindex_v1/codebase_git_history/_assets.py` | 2 Dagster assets: `codebase_git_history_chunks` + `codebase_git_blame_regions` |

**Reuses existing**: `codebase_indexing.py` (file snapshot index, joined by `(file_path, commit_sha)`); `codebase_graph.py` (7-edge AST graph); `_lifespan.py:EMBEDDER`; `agents_md.py` (8 intent categories).

### Phase 4 — Stream 5: `repo_arch_docs.py` (the RepoSwarm revival — ~4 files, ~8 h)

**This is the surviving gem from the archive**: 4-section LLM-generated `.arch.md` per `(repo_path, git_sha)` cached tuple.

| File | Purpose |
|:--|:--|
| `baml/processing/_shared/repo_arch_summary.baml` | 4 BAML fns (via `qwen3.6-27b-mtp` primary, `gemma-4-26B-A4B` fallback): `ExtractOverview(repo_path, repo_type, repo_structure, languages, deps) -> Markdown`; `ExtractComponents(repo_path, repo_type, repo_structure) -> Markdown`; `ExtractDataLayer(repo_path, repo_structure) -> Markdown`; `ExtractDependencies(repo_path, repo_structure, detected_deps) -> Markdown`. Each returns a `## <section>` markdown string. Ported verbatim from `stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/generator.py:_generate_*_section` |
| `cocoindex/repo_arch_docs.py` | CocoIndex v1 App `RepoArchDocs` — reads existing `codebase_index` + `codebase_graph` + `codebase_git_history` LanceDB tables + `git rev-parse HEAD`; calls `detect_repo_type()` (Phase 0 primitive); checks `arch_doc_cache.get(repo_path, git_sha)`; if cache miss, runs the 4 BAML fns in parallel via `asyncio.gather` + generates a Mermaid `graph TD` from the tree (port of `_generate_mermaid_diagram`); writes `repo_arch_docs` LanceDB table (1 row per `(repo_path, git_sha, repo_type)`); emits `.arch.md` file at `cianfhoghlaim/repo_arch_docs/<repo_path_safe>_<git_sha>.md` |
| `.../cocoindex_v1/repo_arch_docs/defs.yaml` | L3 Component mount, `hnsw_index=true` |
| `.../cocoindex_v1/repo_arch_docs/_assets.py` | 1 Dagster asset: `codebase_architecture_docs` (the stub-named one already referenced in `openspec/specs/indexing-and-cognition/spec.md`) |

**Reuses existing**: Phase 0's `arch_doc_cache`, `detect_repo_type`; existing `codebase_indexing.py` + `codebase_graph.py` + `codebase_git_history.py` (this phase); `_lifespan.py:EMBEDDER`.

### Phase 5 — Stream 2: `media_local_embedding.py` (~4 files, ~6 h)

| File | Purpose |
|:--|:--|
| `dlt/api_sources/local_media_files.py` | DLT source: walks `stedding/ingest_queue/media/**/*.{mp4,mkv,webm,mp3,wav,m4a,ogg}`; `ffprobe` for codec + duration + per-stream metadata; mime sniffing via `python-magic`; emits 1 row per file with `(file_path, media_kind: video\|audio, duration_s, codec, sha256)` |
| `baml/processing/_shared/gameplay_sequence.baml` | `class GameplaySegment { video_id string; t_start_s float; t_end_s float; scene_type: title \| menu \| gameplay \| boss \| minigame \| end \| cutscene; subject_matter: string; key_objects: string[]; player_action: string? }` (reuses `retro-game-design-catalogue` spec's `scene_type` enum); `class PlayerCommentary { transcript_segment string; speaker: player \| npc \| narrator; intent: explain \| react \| question \| command; irish_used bool }`; 2 BAML fns: `ExtractGameplaySequence(video_id, frame_captions, audio_transcript) -> GameplaySegment[]` (via `qwen3-vl-8b` + WhisperX) + `ExtractPlayerCommentary(transcript: str, video_id) -> PlayerCommentary[]` |
| `cocoindex/media_local_embedding.py` | CocoIndex v1 App `MediaLocalEmbedding` — reads `local_media_files` DuckLake table → for each video: `ffmpeg -vf fps=1/10` frame sample + WhisperX transcript + Qwen3-VL-8B caption + Molmo2-8B diagram pointing + BAML `ExtractGameplaySequence` + `ExtractPlayerCommentary`; for each audio-only file: WhisperX transcript + BAML `ExtractPlayerCommentary` + existing `baml_src/processing/_shared/music_genre.baml`; mounts 3 LanceDB tables: `media_segments` (per-clip metadata + audio transcript) + `media_frame_captions` (per-frame caption + bbox) + `media_triples` (typed gameplay / commentary / genre triples) |
| `.../cocoindex_v1/media_local/defs.yaml` + `_assets.py` | L3 Component mount + 2 Dagster assets: `media_segments` + `media_triples` |

**Reuses existing**: `retro-game-design-catalogue` spec's `scene_type` enum + `ExtractGameDesignPattern` schema (extended, not replaced); `apple_photos_chunks.py` (CocoIndex v1 ingestion pattern); `canuint_*` (WhisperX path); `_shared/music_genre.baml`; `_lifespan.py:EMBEDDER`; `qwen3-vl-8b` + `molmo2-8b` from `VISION_MODELS`.

### Phase 6 — Cross-cutting agent surface (~6 files, ~4 h)

| File | Purpose |
|:--|:--|
| `mcp/cocoindex-code/src/tools/multihop_search.ts` (or `.py`) | New MCP tool: `multihop_search(question: string, limit?: number = 10, max_iterations?: number = 3, convergence_threshold?: number = 0.05) -> { answer: string; sources: { table, row_id, citation }[] }`. Fans out to all 5 new LanceDB tables + the existing `codebase_chunks` + `leabharlann_chunks` |
| `mcp/cocoindex-code/src/tools/rerank_query.ts` (or `.py`) | New MCP tool: `rerank_query(query: string, results: SearchResult[], top_n?: number = 10) -> SearchResult[]`. Wraps the `RERANKER` ContextKey |
| `mcp/cocoindex-code/src/tools/arch_doc_for_repo.ts` (or `.py`) | New MCP tool: `arch_doc_for_repo(repo_path: string, git_sha?: string) -> { doc_markdown: string; mermaid: string; cached: bool }`. Calls `repo_arch_docs` + `arch_doc_cache` |
| `cognify/datasets/multimedia_kg.py` (new) + 4 sibling files (`package_changelog.py`, `codebase_git_history.py`, `media_local.py`, `repo_arch_docs.py`) | Cognify dataset registration per `cianfhoghlaim-cognify-knowledge-graph` spec (the existing `cianfhoghlaim_cognify_*` pattern) |
| `notebooks/multimodal_code_and_media_intel.py` (new) | marimo mission-control dashboard over the 5 new LanceDB tables + the `multihop_search` answer panel |
| `openspec/specs/multimodal-code-and-media-intel/spec.md` (canonical) | New spec (see spec delta below) |

## Files changed (summary)

- **27 new Python / TypeScript / BAML / YAML files** (5 v1 Apps + 5 L3 Component defs.yaml + 5 L3 Component _assets.py + 4 DLT sources + 4 BAML schema files + 3 MCP tools + 1 marimo notebook + 5 cognify dataset registrations = 32, but some share directories)
- **0 modified existing files** (this change is additive; downstream MODIFIED deltas touch 5 existing specs in the delta below)

## Spec deltas

### ADDED Requirements (`specs/multimodal-code-and-media-intel/spec.md`)

3 new Requirements with ≥1 Scenario each (R1 + R2 + R3). See the spec delta
file for the full text.

### MODIFIED Requirements (5 cross-referenced specs)

- `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md` — add the 5
  new v1 Apps to the conformance registry (per the R1+R2+R3+R4 contract)
- `openspec/specs/celtic-asset-generation/spec.md` — reference Stream 5
  (`media_local_embedding.py`) + Stream 1 (`youtube_kg_embedding.py`) as
  asset-generation consumers
- `openspec/specs/indexing-and-cognition/spec.md` — add 3 new MCP tools
  to the `cocoindex-code` server (brings it from 9 → 12 tools)
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — register the 4 new DLT
  sources + 4 new BAML schemas
- `openspec/specs/cianfhoghlaim-baml-schemas/spec.md` — register the 4 new
  BAML files (`video_kg.baml`, `package_changelog.baml`,
  `git_intent.baml`, `repo_arch_summary.baml`, `gameplay_sequence.baml`)

## Dependencies

Blocked by: none — the change ships fully within `cianfhoghlaim/`. All
required primitives exist (the OCR/VLM `VISION_MODELS` registry,
`_lifespan.py` shared embedder, 32 L3 `CelticModelLifecycleComponent`
defs, `retro-game-design-catalogue` scene_type enum, `transcript_aligner.py`
WhisperX, `apple_photos_chunks.py` v1 App template,
`soundcloud_downloader.py` yt-dlp wrapper, `croilar-data-engineering`
stream-registry pattern, `cianfhoghlaim-cognify-knowledge-graph` dataset
pattern).

Affected repos: **cianfhoghlaim only**. No `bonneagar` (IaC) or
`leabharlann` (corpus) work required.

## Risks

- **Token cost**: 24-backbone `VISION_MODELS` registry has the audio-free
  WhisperX path; the `molmo2-8b` + `qwen3-vl-8b` frame captioning path
  is ~3 s/frame on M4 Max 48 GB. A 90-second 3Blue1Brown video at 1 fps =
  90 frame captions × 3 s = 4.5 min wall time per video. Mitigated by
  scene-change detection (`ffmpeg select=gt(scene\,0.1)`) before captioning.
- **WhisperX dependency on the `meaisinfhoghlaim/process/transcript_aligner.py`
  aligner**: the aligner assumes audio is a single-speaker / single-stream;
  video tutorials may have multiple speakers. Out of scope; documented in
  the change.
- **`retro-game-design-catalogue` scene_type reuse**: the retro spec
  declares the enum inline. Phase 5 imports it via Python import rather
  than duplicating, but the cross-spec coupling is documented in the
  `codebase_architecture_docs` asset key.
- **Git history for submodules**: the `codebase_git_history` App shells
  `git log`; submodules are walked recursively via `--git-dir` per submodule.
  Edge case documented.

## Quality gates

- `openspec validate --strict` MUST pass before commit
- `mise run lint` MUST pass
- `mise run py:typecheck` MUST pass
- `mise run turbo typecheck` MUST pass
- `mise run cocoindex:conformance` MUST report 0 R1/R2/R3/R4 violations
  on the 5 new v1 Apps + the 4 Phase 0 primitives
- `mise run dagster:oideachais` MUST load the 5 new L3 Component
  defs.yaml without errors

## Cross-references

- `openspec/changes/archive/consolidate-external-libs-into-tuatha/proposal.md`
  (the 2026-06 codeolas cleanup that left the 4 surviving gaps)
- `openspec/changes/archive/2026-06-23-sync-skills-from-docs-round-8/MERGE_MAP.md`
  line 102 (the lost "Multimodal Video KG Pipeline" reference doc)
- `openspec/changes/archive/croilar-portfolio/proposal.md` (the
  youtube_ingestion asset that never shipped)
- `openspec/specs/indexing-and-cognition/spec.md` (the existing
  `cocoindex-code` MCP server + `codebase_architecture_docs` stub asset)
- `openspec/specs/retro-game-design-catalogue/spec.md` (the canonical
  game-capture spec; Stream 2 is the player-content sibling)
- `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md` (the R1+R2+R3+R4
  conformance contract)
- `openspec/specs/celtic-asset-generation/spec.md` (the 5-stage
  Celtic-asset pipeline that consumers feed into)
- `openspec/specs/cianfhoghlaim-baml-schemas/spec.md` (BAML registration spec)
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` (DLT orchestration)
- `openspec/specs/cianfhoghlaim-cognify-knowledge-graph/spec.md` (cognify
  dataset pattern)
- `.agents/skills/cocoindex/SKILL.md` (R1+R2+R3+R4 + `_lifespan.py`)
- `.agents/skills/baml/references/multimodal-vision.md` (BAML multimodal primitives)
- `.agents/skills/dlt/SKILL.md` (DLT conventions)
- `stedding/dev/cianfhoghlaim copy/sruth/códeolas/` (the archived source
  of truth for Phase 0 primitives)