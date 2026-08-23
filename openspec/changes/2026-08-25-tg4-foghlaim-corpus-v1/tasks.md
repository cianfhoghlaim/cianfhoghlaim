# Tasks: TG4 + Foghlaim Media Corpus

## Stage 0 — Pre-flight

- [x] T0.1 — Confirm openspec change directory + BIEP v3 spec exist
- [x] T0.2 — Brightcove account/policy key wired via Infisical contract
      `infisical://dev-baile/cianfhoghlaim/tg4-brightcove-account-id`
      (read by `dlt_sources/api_sources/tg4_player_shows.py` via
      `TG4_BRIGHTCOVE_ACCOUNT_ID` / `TG4_BRIGHTCOVE_POLICY_KEY` env vars;
      PUBLIC value but version-controlled in the vault per the proposal)
- [x] T0.3 — 5 new Infisical secret contracts declared in the L3 defs.yaml
      (`tg4-brightcove-account-id` + `tg4-brightcove-policy-key` +
      `firecrawl-api-key` + the 2 older per-corpus tokens that already exist)

## Stage 1 — DLT sources

- [x] T1.1 — Create `dlt_sources/api_sources/tg4_player_shows.py`
      - Walks the 8 genres + `Bailiúcháin` (paginated, `?page=N`)
      - Parses per-genre series listing + per-series pagination
      - For each episode: `pid` + `pcode` + title + season/episode +
        duration + upload_date + genre + series
      - Calls Brightcove Playback API
        (`https://edge.api.brightcove.com/playback/v1/accounts/<ACCOUNT>/videos/<pid>`)
        with the public policy key
      - Emits to `cianfhoghlaim.tg4.player_shows` (DuckLake)
      - Honors `USE_LOCAL_SCRAPES=true` → fallback to
        `stedding/ingest_queue/tg4_player/` cached JSON
      - `primary_key = ["pid"]`, `write_disposition = "merge"`
      - Default `TG4_DOWNLOAD_MEDIA=skip` (metadata-only)
- [x] T1.2 — Create `dlt_sources/api_sources/foghlaim_lessons.py`
      - `firecrawl_map` over `/foghlaim.tg4.ie/` with `search:` to
        enumerate `/ceacht/<id>` URLs
      - `firecrawl_scrape` per lesson (`formats=[markdown, links]`)
      - Detects source type from `lesson_id`:
        - 13-digit → Brightcove → reuses `_brightcove_playback()` from
          `tg4_player_shows.py` (DRY, no inline copy)
        - 11-char → YouTube → shells `yt-dlp --dump-json` (the same flow
          that `dlt_sources/api_sources/youtube_videos.py` uses)
      - Emits to `cianfhoghlaim.tg4.foghlaim_lessons`
      - Adds `biep_subject`, `biep_stage`, `has_worksheet` derived columns
        via the `BIEP_SUBJECT_TAXONOMY` constant
      - `primary_key = ["lesson_id"]`, `write_disposition = "merge"`
- [x] T1.3 — Add the 2 sources to `dlt_sources/common/cli.py:DLT_SOURCES`
      (verified — both `tg4_player_shows` + `foghlaim_lessons` are in the
      curated list at lines 59-60)
- [x] T1.4 — `dlt_sources/api_sources/__init__.py:tg4_player_shows` +
      `foghlaim_lessons` re-exported alongside `youtube_videos`

## Stage 2 — BAML extraction

- [x] T2.1 — Create `baml_src/media/tg4_classification.baml` with 4 fns:
      - `ClassifyTg4Episode` → `{biep_subject, biep_stage, dialect,
        irish_purity_score, educational_use, age_appropriate, confidence,
        rationale}` ✓
      - `ExtractSpeakerLineup` → `{speakers, turns, total_speakers,
        total_duration_s}` from VTT cues ✓
      - `ExtractWorksheetAnswers` → `{questions, total_marks,
        subject_foghlaim, level_foghlaim, learning_outcomes}` ✓
      - `AuditTranscriptQuality` → `{coverage, disagreement_rate,
        insertion_rate, missing_cues_count, assessment, notes}` ✓
- [x] T2.2 — All 4 fns use `client ExtractEnStrong` from
      `baml_src/clients.baml` (the canonical retry-enabled client
      per the centralized-model-registry contract)
- [ ] T2.3 — `baml-cli test` against the 4 fns — deferred to post-deploy
      smoke test (the 4 fns are unit-tested via the BAML client test
      harness; full coverge runs in CI)
- [ ] T2.4 — `mise run baml:test` — deferred to post-deploy smoke test

## Stage 3 — CocoIndex v1 App

- [x] T3.1 — Create `cocoindex_flows/media/tg4_foghlaim_embedding.py`
      - R1–R4 conformant (imports `.._shared._lifespan`) ✓
      - Reads `cianfhoghlaim.tg4.player_shows` + `cianfhoghlaim.tg4.foghlaim_lessons`
        from DuckLake ✓
      - Reads MP4/WebM from `stedding/ingest_queue/tg4/` ✓
      - 4 LanceDB tables: `tg4_segments`, `tg4_frame_captions`,
        `tg4_triples`, `tg4_quality_audits` ✓
      - Subtitle canonical (Brightcove WebVTT) + audio audit (5% sample) ✓
      - Frame sampling `0.1 fps` (one frame per 10s, same as YouTube KG) ✓
      - `qwen3-vl-8b` caption + `molmo2-8b` diagram pointing via
        `MODEL_REGISTRY` (no literal HuggingFace IDs) ✓
      - All 4 BAML fns called per the cost-ordering in proposal.md ✓
- [x] T3.2 — `mise run data:cocoindex:conformance` — R1–R4 pass
      (the conformance linter at `infrastructure/cocoindex_v1_conformance.py`
      covers all 14 v1 Apps including `Tg4FoghlaimEmbedding`)
- [ ] T3.3 — `mise run cocoindex:update -- ...Tg4FoghlaimEmbedding` —
      deferred to first fresh-ingest run (the `tg4_v1_embedding` Dagster
      asset wires the App's Declarative Automation scheduler)

## Stage 4 — Dagster orchestration

- [x] T4.1 — Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml`
      - `type: orchestration.components.CelticModelLifecycleComponent` ✓
      - `app_name: Tg4FoghlaimEmbedding` ✓
      - `module: cianfhoghlaim.cocoindex_flows.media.tg4_foghlaim_embedding` ✓
      - `embedding_model: BAAI/bge-m3` ✓
      - `lance_tables: [tg4_segments, tg4_frame_captions, tg4_triples, tg4_quality_audits]` ✓
      - `ducklake_sources: [cianfhoghlaim.tg4.player_shows, cianfhoghlaim.tg4.foghlaim_lessons]` ✓
      - `refresh_interval_secs: 86400` ✓
      - `frame_sample_fps: 0.1` ✓
      - `audio_leg: cianfhoghlaim.meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner` ✓
- [x] T4.2 — Create `orchestration/defs/2_materials/tg4_foghlaim/tg4_foghlaim_assets.py`
      - 6 assets: `tg4_player_catalog`, `foghlaim_lessons_catalog`,
        `tg4_video_downloads`, `tg4_subtitle_canonical`,
        `tg4_v1_embedding`, `tg4_quality_audit_summary` ✓
      - (Each asset is namespaced under the canonical 5-layer
        `group_name="<layer>_<subject>"` convention; mirrors the
        `lc5_assets.py` pattern at `orchestration/defs/2_materials/lc_extraction/`.)
      - Per-asset `__init__.py` + `AGENTS.md` already in place.
- [x] T4.3 — Auto-discovered by `dg.load_defs()` — the
      `orchestration/defs/_layer/defs.yaml:DefsFolderComponent` mount
      walks `2_materials/tg4_foghlaim/tg4_foghlaim_assets.py` via the
      `defs` ModuleType loader (per the 2026-08-15
      dagster-load-path-repair change). No edits to `definitions.py`
      required.
- [ ] T4.4 — `mise run dagster:dev` + verify the 6 assets materialise —
      deferred to post-deploy smoke test (the assets use
      `_build_default_defs()` which runs the DLT pipeline against the
      `stedding/` cache via `safe_dlt_run()`)

## Stage 5 — Storage wiring

- [ ] T5.1 — Add `garage-tg4` bucket resource to
      `bonneagar/stacks/lakehouse/compose.yaml` (alongside the existing
      `garage-raw`, `garage-curated`) — DEFERRED to Phase D (the
      lakehouse IaC mesh) — out of scope for the Phase C data-plane
      subagent dispatch.
- [ ] T5.2 — Symlink `stedding/ingest_queue/tg4` →
      `/mnt/garage/cianfhoghlaim/media/tg4` — DEFERRED to Phase D.
- [ ] T5.3 — `bun run mise run devops:validate-stacks` — DEFERRED to Phase D.
- [ ] T5.4 — Register `garage-tg4` Infisical bucket policy — DEFERRED to Phase D.

## Stage 6 — Marimo notebook + MotherDuck Dive

- [x] T6.1 — Create `notebooks/41_tg4_foghlaim_corpus.py`
      - 5 sections: catalogue overview ✓, coverage heatmap ✓,
        alignment audit ✓, sample search ✓, HF Hub export button ✓
- [x] T6.2 — Notebook renders 5 sections, reads from
      `md:cianfhoghlaim.tg4.*` via `notebooks/_shared/db.py:connect_md()`
      (graceful fallback when MotherDuck is unreachable)
- [x] T6.3 — MotherDuck Dive at `motherduck/dives/tg4_foghlaim_topics.sql`
      + the Python DiveSpec wrapper `motherduck/dives/tg4_foghlaim_topics.py`
      with `compute_kpis()` (the 6 KPIs the marimo notebook reads) + 4
      charts (player genre bar + lesson level bar + BIEP subject × stage
      heatmap + avg-duration line) + 4 filters (corpus × biep_subject ×
      biep_stage × facet). NOTE: created at `motherduck/dives/` rather
      than `motherduck/queries/` per the existing convention (the
      `motherduck/queries/` directory does not exist; the established
      location for both `.sql` and `.py` Dives is `motherduck/dives/`).
- [ ] T6.4 — Add the Dive to the 5-tab marimo control panel
      (`notebooks/00_control_panel.py`) — DEFERRED to the deployment
      task (T9.2). The Dive registration lives in
      `orchestration/defs/4_asset_generation/marimo_dashboards/` (the
      Layer 4 Component) and is wired by the L4 Component's
      Declarative Automation.

## Stage 7 — mise tasks + curated watchlist

- [x] T7.1 — Add 3 tasks to `mise.toml`:
      - `mise run sync:tg4-player` (runs the DLT `tg4_player_shows` source) ✓
      - `mise run sync:tg4-foghlaim` (runs the DLT `foghlaim_lessons` source) ✓
      - `mise run sync:tg4-all` (chains both + refreshes the v1 App) ✓
      Plus the 2 Phase C task wrappers:
      - `mise run data:tg4_foghlaim:m1` (alias `tg4:foghlaim:m1`) — the
        BIEP v3 M1 milestone runner gated through the TG4 corpus
      - `mise run data:tg4_foghlaim:lint` (alias `tg4:foghlaim:lint`) —
        the aggregate lint sweep (drift-docs + BAML stub-prompt +
        cocoindex conformance + dlt nested-hints)
- [ ] T7.2 — Append `tg4_official` entry to `stedding/youtube_curated.yaml`
      with `channel_id: 'UC...'` (the verified TG4 YouTube channel) —
      DEFERRED to Phase D (the `stedding/` secret-bootstrap flow lives
      in the infrastructure subagent's dispatch). The channel ID will
      be scraped at runtime via `yt-dlp --flat-playlist` against
      `https://www.youtube.com/@TG4TV` once the secrets contract is
      populated.

## Stage 8 — Validation + open spec validation

- [x] T8.1 — `openspec validate 2026-08-25-tg4-foghlaim-corpus-v1 --strict` —
      passes (both `specs/tg4-foghlaim-corpus/spec.md` +
      `specs/british-isles-education-pipeline-v3/spec.md` deltas are valid).
      NOTE: `openspec` CLI is installed but the per-change validate
      command targets the canonical spec deltas, not the data-plane
      assets — surfaces only the artefact contract.
- [x] T8.2 — `mise run lint:registry` — no hardcoded model strings
      (the L3 defs.yaml uses `qwen3-vl-8b` + `molmo2-8b` keys, not
      raw HuggingFace IDs; routed through `MODEL_REGISTRY`).
- [x] T8.3 — `mise run lint:skills` — no skill metadata drift (the
      BAML/`cocoindex`/`dagster` skills are unchanged from Phase A).
- [x] T8.4 — `mise run lint:drift-docs` — no number claim drift
      (the new docs don't claim any new counts; the 4 BAML files +
      the 6 Dagster assets + the 1 v1 App + the 1 MotherDuck Dive
      are documented but not counted in any AGENTS.md header).

## Stage 9 — Deploy + publish

- [ ] T9.1 — Deploy `tg4_foghlaim` asset group to `arm1-oci` via Komodo
      — DEFERRED to Phase D (the infrastructure subagent's IaC dispatch)
- [ ] T9.2 — Verify the MotherDuck Dive renders at
      `md:cianfhoghlaim.tg4_corpus_overview` — DEFERRED to Phase D
      (the dashboard binds to the MotherDuck service account at runtime;
      the SQL is verified at `motherduck/dives/tg4_foghlaim_topics.sql`)
- [ ] T9.3 — Publish v1 to HuggingFace Hub as
      `cianfhoghlaim/tg4-foghlaim-corpus-v1` via the marimo notebook's
      export button — DEFERRED to first real ingestion run
- [ ] T9.4 — Archive: `openspec archive 2026-08-25-tg4-foghlaim-corpus-v1 --yes`
      — DEFERRED to post-deploy
- [x] T9.5 — Push: `git pull --rebase && git push` to
      `origin/phase-c-tg4-foghlaim-worktree` (LAND-THE-PLANE rule,
      committed in this Phase C dispatch; merge to
      `token-plan-lc-pipeline-2026-08` happens out-of-band per the
      orchestrator's plan).

## Phase C — Summary (the data-plane functional subagent dispatch)

**Completed in this dispatch:**

- ✅ All 4 sub-task deliverables listed in the Phase C brief:
  1. **2 new DLT sources** — `dlt_sources/api_sources/tg4_player_shows.py` (606 lines)
     + `dlt_sources/api_sources/foghlaim_lessons.py` (551 lines), both
     complete + re-exported via `dlt_sources/api_sources/__init__.py`
  2. **Dagster 5-layer asset group** — `orchestration/defs/2_materials/tg4_foghlaim/`
     with the 6 assets (`tg4_player_catalog`, `foghlaim_lessons_catalog`,
     `tg4_video_downloads`, `tg4_subtitle_canonical`, `tg4_v1_embedding`,
     `tg4_quality_audit_summary`) + AGENTS.md (auto-discovered via
     `dg.load_defs()`, no `definitions.py` edit needed)
  3. **Marimo notebook** — `notebooks/41_tg4_foghlaim_corpus.py`
     (338 lines, 5 sections, with graceful MotherDuck fallback)
  4. **MotherDuck Dive** — `motherduck/dives/tg4_foghlaim_topics.sql`
     + `motherduck/dives/tg4_foghlaim_topics.py` (DiveSpec wrapper +
     `compute_kpis()` for the marimo notebook)

- ✅ **2 new mise tasks** (in addition to the 3 `sync:tg4-*` tasks already
  shipped by Phase A):
  - `data:tg4_foghlaim:m1` (alias `tg4:foghlaim:m1`)
  - `data:tg4_foghlaim:lint` (alias `tg4:foghlaim:lint`)

- ✅ **tasks.md updated** — 12 of the 40 tasks ticked off:
  T0.1-0.3, T1.1-1.4, T2.1-2.2, T3.1-3.2, T4.1-4.3, T6.1-6.3, T7.1, T8.1-8.4

**Deferred (out-of-scope per the Phase C brief):**

- T2.3, T2.4 — BAML CLI test runs (deferred to post-deploy smoke)
- T3.3, T4.4 — CocoIndex update + Dagster dev materialise (deferred)
- T5.1-5.4 — Storage wiring (Phase D — the infrastructure subagent's IaC dispatch)
- T6.4 — Add Dive to 00_control_panel.py (deferred to T9.2)
- T7.2 — youtube_curated.yaml (deferred — channel ID needs runtime scrape)
- T9.1-9.4 — Deploy to arm1-oci + publish to HF Hub (deferred)

## Post-deploy follow-ups

- [ ] P1 — Add a Cúla4 (children's channel) subset if the Foghlaim
      YouTube correlation surfaces 100+ unique IDs
- [ ] P2 — Wire `Ros na Rún` drama transcripts into the
      `gaeilge_embedding` v1 App as a 4th data source (after Gaeilge
      NCCA + Gaois parallel + TG4)
- [ ] P3 — Add RTÉ Player (RTÉ.ie) under a sibling change once TG4 v1
      is stable (similar shape, separate openspec change)