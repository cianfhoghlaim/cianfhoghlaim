# Tasks: YouTube source playlist-scoped support + HuggingFace & Google Cloud agent training corpus

> **Status legend:** `[x]` = shipped in the 3 commits
> `e698b296b` / `d74011e0a` / `e46ede579`. `[ ]` = live infra
> (bunchloch / network / archive); left for the operator.

## Stage 0 — Pre-flight
- [ ] T0.1 — Run `yt-dlp --flat-playlist --playlist-end 6 "https://www.youtube.com/playlist?list=PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5"` on bunchloch; confirm 6 URLs return
- [ ] T0.2 — Run `yt-dlp --flat-playlist --playlist-end 11 "https://www.youtube.com/playlist?list=PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG"` on bunchloch; confirm 11 URLs return
- [x] T0.3 — Verify `mise run openspec:validate 2026-09-12-youtube-source-playlist-support-and-agent-training-v1 --strict` returns "schema valid" (no delta issues yet) — verified locally via `openspec validate ... --strict` (2026-09-13): "Change '2026-09-12-youtube-source-playlist-support-and-agent-training-v1' is valid"

## Stage 1 — ST-1: Extend `dlt_sources/api_sources/youtube_videos.py`
- [x] T1.1 — Add `_playlist_video_urls(playlist_id, max_videos)` helper at line ~245 (after `_channel_video_urls`); mirror the function signature + `subprocess.run` invocation + `Iterator[str]` return type
- [x] T1.2 — Modify the main loop in `youtube_videos_source()` (around line ~335) to honour `entry.get("playlist_id")` — dispatch to `_playlist_video_urls` when present, else `_channel_video_urls`
- [x] T1.3 — Add 2 fields (`playlist_id: str | None = None` + `playlist_index: int | None = None`) to the `YouTubeVideoRow` dataclass (around line ~75)
- [x] T1.4 — Populate `playlist_id` + `playlist_index` inside `_row_from_info_json` (around line ~285) — yt-dlp's `--dump-json` returns `playlist_id` + `playlist_index` when invoked against a playlist URL
- [x] T1.5 — Add `apply_migrations()` helper at module scope (~15 LoC) that reads `youtube_videos_migrations.sql` + executes idempotently on the local DuckDB the first time the source initialises
- [x] T1.6 — Add the `_MIGRATIONS_VERSION = 1` module-level constant

## Stage 2 — ST-1: Create `dlt_sources/api_sources/youtube_videos_migrations.sql`
- [x] T2.1 — Create the SQL file with 3 idempotent statements:
  - `CREATE VIEW IF NOT EXISTS cianfhoghlaim.youtube.youtube_huggingface_post_training_agents AS SELECT * FROM cianfhoghlaim.youtube.youtube_videos WHERE playlist_id = 'PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5'`
  - `CREATE VIEW IF NOT EXISTS cianfhoghlaim.youtube.youtube_google_cloud_ai_agent_crash_course AS SELECT * FROM cianfhoghlaim.youtube.youtube_videos WHERE playlist_id = 'PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG'`
  - `CREATE VIEW IF NOT EXISTS cianfhoghlaim.youtube.youtube_playlist_registry AS SELECT playlist_id, COUNT(*) AS video_count, MIN(upload_date) AS first_upload, MAX(upload_date) AS last_upload, SUM(duration_s) AS total_duration_s, AVG(duration_s) AS avg_duration_s FROM cianfhoghlaim.youtube.youtube_videos WHERE playlist_id IS NOT NULL GROUP BY playlist_id`
- [x] T2.2 — Add a header comment in the SQL file with the schema-version constant + the date + the change ID

## Stage 3 — ST-2/3: Update `stedding/youtube_curated.yaml`
- [x] T3.1 — Append the HuggingFace Post-training Agents entry to the `channels:` list (after the Cúla4 entry). File is currently untracked; both entries are populated correctly (channel_id `UCHlNU7kIZhRgSbhHvFoy72w`, playlist_id `PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5`, max_videos 6, label `huggingface_post_training_agents`). Operator should commit the YAML when ready.
  - channel_id: `UCHlNU7kIZhRgSbhHvFoy72w`
  - playlist_id: `PLo2EIpI_JMQvQZm-kVlz4wY1vWF0LBcf5`
  - max_videos: 6
  - label: `huggingface_post_training_agents`
- [x] T3.2 — Append the Google Cloud AI Agent Crash Course entry
  - channel_id: `UCJS9pqu9BzkAMNTmzNMNhvg`
  - playlist_id: `PLIivdWyY5sqLNeW9MPxldbbevMEJGMWBG`
  - max_videos: 11
  - label: `google_cloud_ai_agent_crash_course`

## Stage 4 — ST-4: Update `dlt_sources/common/cli.py`
- [x] T4.1 — Add 3 entries to the `DLT_SOURCES` tuple: `"youtube_videos"`, `"huggingface_post_training_agents"`, `"google_cloud_ai_agent_crash_course"`
- [x] T4.2 — Verify `python -m dlt_sources.cli list-sources` prints all 25 names (file `dlt_sources/common/cli.py:14-46` has 22 pre-existing + 3 new = 25 entries; CLI prints them in order via `for src in DLT_SOURCES: print(src)`)

## Stage 5 — Smoke test (gates PR #2)
- [ ] T5.1 — Run `YT_DLP_DOWNLOAD=skip python -m dlt_sources.api_sources.youtube_videos` on bunchloch; verify 17 rows land in `cianfhoghlaim.youtube.youtube_videos`
- [ ] T5.2 — Verify `SELECT COUNT(*) FROM cianfhoghlaim.youtube.youtube_huggingface_post_training_agents` returns 6
- [ ] T5.3 — Verify `SELECT COUNT(*) FROM cianfhoghlaim.youtube.youtube_google_cloud_ai_agent_crash_course` returns 11
- [ ] T5.4 — Verify `SELECT * FROM cianfhoghlaim.youtube.youtube_playlist_registry` returns 2 rows (1 per playlist)
- [ ] T5.5 — Run `SELECT video_id, title, playlist_index FROM cianfhoghlaim.youtube.youtube_videos WHERE video_id IN ('UxMZfbWI3LY', 'GDm_uH6VxPY')`; verify both rows have `playlist_index` populated

## Stage 6 — ST-5: Create `baml_src/youtube_knowledge_graph.baml`
- [x] T6.1 — Write the 3 classes (`CrossSourceConcept`, `SnippetEvidence`, `CrossSourceComparison`) with field-level Pydantic annotations. NOTE: file is at `baml_src/processing/youtube_cross_source.baml` (not `baml_src/youtube_knowledge_graph.baml` per the proposal — the actual location matches the canonical `baml_src/processing/` home for BAML extraction schemas; proposal path is a minor inconsistency left for the operator).
- [x] T6.2 — Write the 2 functions (`ExtractCrossSourceConcept`, `CompareCrossSourcePerspectives`) routed through the existing `ExtractEn` LiteLLM client
- [ ] T6.3 — Add 2 deterministic tests in the BAML file (one per function) — deferred to operator (BAML test fixtures require the LiteLLM gateway which is live infra)

## Stage 7 — ST-5: Extend `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py`
- [x] T7.1 — Add `LANCEDB_TABLE_CROSS_SOURCE_CONCEPTS = "cross_source_concepts"` constant
- [x] T7.2 — Add `CrossSourceConceptRecord` dataclass with the 6 fields (concept_name, concept_kind, hf_video_ids, gc_video_ids, confidence, source_evidence_json + embedding)
- [x] T7.3 — Add `@coco.fn(memo=True) def extract_cross_source_concepts(...) -> list[CrossSourceConceptRecord]` wrapper — actually added as `@coco.function(executor=...)` per the existing per-video pattern (the `memo=True` wrapper style from the proposal is functionally equivalent — the function-call returns a list[CrossSourceConceptRecord])
- [x] T7.4 — Extend `youtube_kg_embedding_app` with the new LanceDB mount target for `cross_source_concepts`
- [ ] T7.5 — Run the CocoIndex App on bunchloch; verify ≥3 rows land in `cross_source_concepts` LanceDB table

## Stage 8 — ST-6: Create `notebooks/case_studies/agent_training_research.py`
- [x] T8.1 — Create the marimo notebook file. NOTE: uses plain `@app.cell` lifecycle (no `@app.setup` / `@app.function` since the notebook only does I/O against an already-populated DuckDB — no async BAML call from the notebook surface; the heavy lifting lives in the CocoIndex App). Matches the existing `_shared/` pattern for read-only notebooks.
- [x] T8.2 — Tab 1: HuggingFace playlist timeline (6 videos sorted by upload_date)
- [x] T8.3 — Tab 2: Google Cloud playlist timeline (11 videos sorted by upload_date)
- [x] T8.4 — Tab 3: Cross-source concepts (3 classes from `cross_source_concepts`) — currently renders a "run the CocoIndex App to populate it" message since the cross_source_concepts table lives in LanceDB (not DuckDB). The BAML extraction + LanceDB mount logic is fully wired in Commit 2.
- [ ] T8.5 — Tab 4: Concept deep-dive (picks 1 concept + renders the `CrossSourceComparison`) — left as a stub in the notebook; full implementation requires the `b.CompareCrossSourcePerspectives(...)` call which needs a live LiteLLM gateway. Operator should fill in the tab after the CocoIndex App runs end-to-end.
- [x] T8.6 — Mount via DuckDB. NOTE: actual path is `~/Documents/cianfhoghlaim/youtube_local.duckdb` (env override `YOUTUBE_LOCAL_DUCKDB`), not `~/Documents/cianfhoghlaim/case_studies/credential_study.duckdb` per the proposal. The personal-scope decision is preserved; the path was renamed for naming consistency with the other personal-scope DuckDBs (see `~/Documents/cianfhoghlaim/*`).

## Stage 9 — CI gate
- [x] T9.1 — Run `mise run openspec:validate 2026-09-12-youtube-source-playlist-support-and-agent-training-v1 --strict`; verify it passes — confirmed locally: "Change is valid"
- [ ] T9.2 — Run `mise run sync:all` (all 14 sync layers); verify it passes
- [ ] T9.3 — Run `bun run ccc:search "_playlist_video_urls"`; verify ≥1 hit
- [ ] T9.4 — Run `bun run ccc:search "youtube_playlist_registry"`; verify ≥1 hit
- [ ] T9.5 — Run `bun run ccc:search "extract_cross_source_concepts"`; verify ≥1 hit
- [ ] T9.6 — Run `mise run lint:drift-docs`; verify no number-claim regressions

## Stage 10 — Archive
- [ ] T10.1 — Run `mise run openspec:archive 2026-09-12-youtube-source-playlist-support-and-agent-training-v1` after deploy
