# Tasks — 2026-07-14-multimodal-code-and-media-intel-v1

## Phase 0 — Port the archived codeolas primitives (~4 h)

Revive the 4 archived codeolas subsystems as CocoIndex v1 native
primitives (`@coco.fn(memo=True)` + `ContextKey`).

- [x] 0.1 Create `cocoindex/multihop_search.py` — port
      `stedding/dev/cianfhoghlaim copy/sruth/códeolas/search/multihop.py`
      as `@coco.fn(memo=True, as_async) async def multihop_search(question,
      limit=10, max_iterations=3, convergence_threshold=0.05)`. Accept a
      list of (table_name, lancedb_query_fn) pairs to fan out over. Emit a
      Langfuse v3 span `multihop.iteration.<n>` with the candidate-set size
      + convergence score on every iteration.

- [x] 0.2 Create `cocoindex/reranker.py` — `RERANKER`
      `ContextKey` wrapping Jina (default) / Cohere / Aliyun via
      LiteLLM; expose `@coco.fn(memo=True) async def query_reranker(query,
      results, top_n)` matching the archived
      `search/reranker.py:rerank_results` signature.

- [x] 0.3 Create `cocoindex/repo_type_detector.py` — port
      `stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/detector.py:RepoTypeDetector`
      as `@coco.fn(memo=True) async def detect_repo_type(repo_path)`. Same
      enum (`FRONTEND | BACKEND | LIBRARY | DATA_PIPELINE | MONOREPO`)
      + same heuristic (markers: `package.json` → FRONTEND; `dagster/`
      dir → DATA_PIPELINE; `pyproject.toml` + `src/<pkg>/` → LIBRARY;
      monorepo markers → MONOREPO; else BACKEND).

- [x] 0.4 Create `cocoindex/arch_doc_cache.py` — port
      `stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/cache.py:ArchDocCache`
      as a `ContextKey` wrapping a DuckDB instance keyed by
      `(repo_path, git_sha, repo_type)`. Use the existing
      `memory_facade/duckdb` stack per the `storage-memory-facade` spec.

- [x] 0.5 Quality gate: `mise run cocoindex:conformance` exits 0 on all 4
      primitives (each is R1+R2+R3+R4 conformant: imports `_lifespan`,
      declares a v1 `coco.App(...)` at module scope even if no LanceDB
      target, satisfies the R3+R4 contract via stub declarations).

## Phase 1 — Stream 1: `youtube_kg_embedding.py` (~6 h)

- [x] 1.1 Create `dlt/api_sources/youtube_videos.py` — DLT
      source that reads `stedding/youtube_curated.yaml` (a list of
      `{channel_id, playlist_id?, max_videos?}` tuples) and emits 1 row per
      video via yt-dlp. Mirror the `soundcloud_downloader.py` pattern:
      `yt-dlp --dump-json` for metadata + `yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/best`
      for the MP4 to `stedding/ingest_queue/youtube/<video_id>.mp4`.

- [x] 1.2 Create `baml/processing/_shared/video_kg.baml`
      — 3 classes (`KnowledgeTriple`, `ConceptChain`, `VisualSequence`)
      + 3 BAML functions (`ExtractVideoKnowledgeTriple`,
      `ExtractConceptChain`, `ExtractFrameSequence`). Routes through the
      existing `qwen3-vl-8b` client for the visual leg and
      `qwen3.6-27b-mtp` for the text leg.

- [x] 1.3 Generate the BAML client: `mise run baml:generate`.

- [x] 1.4 Create `cocoindex/youtube_kg_embedding.py` — the
      v1 App `YoutubeKgEmbedding`. Reads `youtube_videos` DuckLake table;
      for each video, runs WhisperX via `transcript_aligner.py` +
      `ffmpeg -vf fps=1/10` frame sampling + `qwen3-vl-8b` caption +
      `molmo2-8b` for slide diagrams + the 3 BAML fns. Mounts 3 LanceDB
      tables: `video_segments`, `video_frame_captions`, `video_triples`.

- [x] 1.5 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/defs.yaml`
      — L3 `CelticModelLifecycleComponent` mount.

- [ ] 1.6 Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/_assets.py`
      — 3 Dagster assets (all `is_virtual=True`).

- [ ] 1.7 Quality gate: `mise run cocoindex:conformance` exits 0 on the
      new App; `mise run dagster:oideachais` lists `youtube_kg` in the L3
      Component tree.

## Phase 2 — Stream 3: `package_changelog_embedding.py` (~5 h)

- [ ] 2.1 Create `dlt/api_sources/package_docs.py` — DLT
      source reading `stedding/package_watchlist.yaml` (list of
      `{ecosystem: pypi|npm|cran, name, homepage, docs_url}` tuples). Uses
      dlt `rest_api` for PyPI JSON + `requests` + the Firecrawl MCP
      client (per the `upstream_blog_monitor.py` pattern) for docs
      scraping.

- [ ] 2.2 Create `baml/processing/_shared/package_changelog.baml`
      — 2 classes (`ChangelogEntry`, `APIDiff`) + 2 BAML fns
      (`ExtractChangelogEntry`, `ExtractAPIDiff`) routed through
      `qwen3.6-27b-mtp`.

- [ ] 2.3 Generate the BAML client.

- [ ] 2.4 Create `cocoindex/package_changelog_embedding.py`
      — v1 App `PackageChangelogEmbedding` mounting 2 LanceDB tables:
      `package_changelog_chunks` + `package_changelog_diffs`.

- [ ] 2.5 Create the L3 Component `defs.yaml` + `_assets.py` (2 Dagster
      assets).

- [ ] 2.6 Quality gate: same as Phase 1.

## Phase 3 — Stream 4: `codebase_git_history.py` (~6 h)

- [ ] 3.1 Create `cocoindex/codebase_git_history.py` —
      v1 App `CodebaseGitHistory`. Custom `@coco.fn` local-git source
      connector that shells `git log --pretty=format:'%H|%ae|%at|%s'`,
      `git blame --line-porcelain`, `git diff --stat` for diff stats.
      Embeds per-commit (subject + diff stats + LLM-classified intent) +
      per-blame-region (region text + author + commit SHA chain).
      Extends the existing `codebase_graph` App's 7-edge schema with **2
      new edges**: `AUTHORED_BY` + `TOUCHED_IN`. Mounts 2 LanceDB tables:
      `codebase_git_commits` + `codebase_git_blame_regions`.

- [ ] 3.2 Create `baml/processing/_shared/git_intent.baml`
      — 1 class (`CommitIntent`) + 1 BAML fn (`ExtractCommitIntent`).

- [ ] 3.3 Generate the BAML client.

- [ ] 3.4 Create the L3 Component `defs.yaml` + `_assets.py` (2 Dagster
      assets: `codebase_git_history_chunks` + `codebase_git_blame_regions`).

- [ ] 3.5 Update `cocoindex/codebase_graph.py` to declare
      the 2 new edge types in the row dataclass (no breaking change to
      existing 7 edges).

- [ ] 3.6 Quality gate: same as Phase 1.

## Phase 4 — Stream 5: `repo_arch_docs.py` (the RepoSwarm revival — ~8 h)

**This is the surviving gem from the archive.**

- [ ] 4.1 Create `baml/processing/_shared/repo_arch_summary.baml`
      — 4 BAML fns (`ExtractOverview`, `ExtractComponents`,
      `ExtractDataLayer`, `ExtractDependencies`). Prompts ported verbatim
      from
      `stedding/dev/cianfhoghlaim copy/sruth/códeolas/generators/reposwarm/generator.py`
      `_generate_overview_section` / `_generate_components_section` /
      `_generate_data_section` / `_generate_dependencies_section`. Routes
      through `qwen3.6-27b-mtp` primary, `gemma-4-26B-A4B` fallback.

- [ ] 4.2 Generate the BAML client.

- [ ] 4.3 Create `cocoindex/repo_arch_docs.py` — v1 App
      `RepoArchDocs`. Reads `codebase_index` + `codebase_graph` +
      `codebase_git_history` tables; calls Phase 0's `detect_repo_type()`
      + `arch_doc_cache.get(repo_path, git_sha)`; on cache miss, runs the
      4 BAML fns via `asyncio.gather`; generates a Mermaid `graph TD`
      diagram (port of `_generate_mermaid_diagram`); writes 1 row to
      `repo_arch_docs` LanceDB table per `(repo_path, git_sha, repo_type)`
      and emits a `.arch.md` file at
      `cianfhoghlaim/repo_arch_docs/<repo_path_safe>_<git_sha>.md`.

- [ ] 4.4 Create the L3 Component `defs.yaml` + `_assets.py` (1 Dagster
      asset: `codebase_architecture_docs` — the stub-named one already
      referenced in `openspec/specs/indexing-and-cognition/spec.md`).

- [ ] 4.5 End-to-end smoke test: run the App on the cianfhoghlaim repo
      with the current `HEAD` SHA; assert a row is written to
      `repo_arch_docs` + a `.arch.md` file is emitted at
      `cianfhoghlaim/repo_arch_docs/cianfhoghlaim_<sha>.md`. Inspect the
      `.arch.md` for the 4 sections + the Mermaid diagram.

- [ ] 4.6 Quality gate: same as Phase 1.

## Phase 5 — Stream 2: `media_local_embedding.py` (~6 h)

- [ ] 5.1 Create `dlt/api_sources/local_media_files.py` —
      DLT source walking `stedding/ingest_queue/media/**/*.{mp4,mkv,webm,mp3,wav,m4a,ogg}`.
      `ffprobe` for codec + duration + per-stream metadata; `python-magic`
      mime sniffing. Emits 1 row per file with `(file_path, media_kind:
      video|audio, duration_s, codec, sha256)`.

- [ ] 5.2 Create `baml/processing/_shared/gameplay_sequence.baml`
      — 2 classes (`GameplaySegment`, `PlayerCommentary`) + 2 BAML fns
      (`ExtractGameplaySequence`, `ExtractPlayerCommentary`). Reuses the
      `scene_type` enum from `openspec/specs/retro-game-design-catalogue/spec.md`
      line 70 (`"title" | "menu" | "gameplay" | "boss" | "minigame" |
      "end"` + extended `"cutscene"`).

- [ ] 5.3 Generate the BAML client.

- [ ] 5.4 Create `cocoindex/media_local_embedding.py` —
      v1 App `MediaLocalEmbedding`. Reads `local_media_files` DuckLake
      table; for each video runs `ffmpeg -vf fps=1/10` + WhisperX +
      `qwen3-vl-8b` + `molmo2-8b` + the 2 BAML fns; for each audio-only
      file runs WhisperX + `ExtractPlayerCommentary` + existing
      `baml_src/processing/_shared/music_genre.baml`. Mounts 3 LanceDB
      tables: `media_segments` + `media_frame_captions` + `media_triples`.

- [ ] 5.5 Create the L3 Component `defs.yaml` + `_assets.py` (2 Dagster
      assets).

- [ ] 5.6 Quality gate: same as Phase 1.

## Phase 6 — Cross-cutting agent surface (~4 h)

- [ ] 6.1 Add the `multihop_search` MCP tool to
      `mcp/cocoindex-code/src/tools/multihop_search.{ts,py}`. Fans out
      over the 5 new LanceDB tables + the existing `codebase_chunks` +
      `leabharlann_chunks`. Returns `{ answer: string; sources:
      { table, row_id, citation }[] }`.

- [ ] 6.2 Add the `rerank_query` MCP tool — wraps the `RERANKER`
      ContextKey.

- [ ] 6.3 Add the `arch_doc_for_repo` MCP tool — calls `repo_arch_docs`
      + `arch_doc_cache`. Returns `{ doc_markdown: string; mermaid:
      string; cached: bool }`.

- [ ] 6.4 Register the 5 new cognify datasets:
      `multimedia_kg`, `package_changelog`, `codebase_git_history`,
      `media_local`, `repo_arch_docs`. One file per dataset under
      `cognify/datasets/`, following the existing
      `cianfhoghlaim_cognify_*` pattern.

- [ ] 6.5 Create `notebooks/multimodal_code_and_media_intel.py`
      — marimo mission-control dashboard over the 5 new LanceDB tables +
      the `multihop_search` answer panel.

- [ ] 6.6 Update `openspec/AGENTS.md` priority-specs table to add the
      new `multimodal-code-and-media-intel` spec to the list (5 → 6
      priority specs, but cianfhoghlaim-quadrant priority is unchanged).

- [ ] 6.7 Update `opencode.json` to grant the 5 sruth-subagents (build,
      plan, oideachais, meaisinfhoghlaim, tuatha, infrastructure,
      croilar, dev-env-demo) access to the 3 new MCP tools (skill_filter
      gets 3 new skill names).

- [ ] 6.8 Run `openspec validate --strict` — MUST pass green.

- [ ] 6.9 Run the full quality gate suite:
      ```bash
      mise run lint
      mise run py:typecheck
      mise run turbo typecheck
      mise run cocoindex:conformance
      ```
      All 4 MUST exit 0.

- [ ] 6.10 Commit + push.

## Post-archive

- [ ] A.1 `openspec archive 2026-07-14-multimodal-code-and-media-intel-v1 --yes`
- [ ] A.2 Run `mise run sync_agent_docs.sh` (per the AGENTS.md
      "Self-Documenting Telemetry" rule)
- [ ] A.3 Verify `openspec list --specs` shows the new
      `multimodal-code-and-media-intel` spec in the list
- [ ] A.4 Open a follow-up issue if any Phase has remaining tasks (per the
      AGENTS.md "Landing the Plane" rule)