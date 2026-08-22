# Tasks: TG4 + Foghlaim Media Corpus

## Stage 0 — Pre-flight

- [x] T0.1 — Confirm openspec change directory + BIEP v3 spec exist
- [ ] T0.2 — Confirm Brightcove account ID + policy key for TG4 (extract
      from player page `<script>` tags; cache at
      `stedding/ingest_queue/tg4_player/brightcove_account.json`)
- [ ] T0.3 — Confirm 5 new Infisical secret contracts exist (or get
      `bun run scripts/init-vault.ts` to create them)

## Stage 1 — DLT sources

- [ ] T1.1 — Create `dlt_sources/api_sources/tg4_player_shows.py`
      - Walks the 8 genres + `Bailiúcháin` (paginated, `?page=N`)
      - Parses per-genre series listing + per-series pagination
      - For each episode: `pid` + `pcode` + title + season/episode +
        duration + upload_date + genre + series
      - Calls Brightcove Playback API
        (`https://edge.api.brightcove.com/playback/v1/accounts/<ACCOUNT>/videos/<pid>`)
        with the public policy key
      - Emits to `cianfhoghlaim.tg4.player_shows` (DuckLake via
        `get_dlt_destination(mode="production")`)
      - Honors `USE_LOCAL_SCRAPES=true` → fallback to
        `stedding/ingest_queue/tg4_player/` cached JSON
      - `primary_key = ["pid"]`, `write_disposition = "merge"`
      - Default `TG4_DOWNLOAD_MEDIA=skip` (metadata-only)
- [ ] T1.2 — Create `dlt_sources/api_sources/foghlaim_lessons.py`
      - `firecrawl_map` over `/foghlaim.tg4.ie/` with `search:` to
        enumerate `/ceacht/<id>` URLs
      - `firecrawl_scrape` per lesson with `formats=[json]` +
        `jsonOptions.schema` (level, keywords, worksheets, learning
        outcomes, duration, source suffix `FO|BC|MO|YT`, subject tags,
        series, related-lessons)
      - Detects source type from `pid`:
        - 13-digit → Brightcove → reuse Brightcove Playback API call
        - 11-char → YouTube → reuse `dlt_sources/api_sources/youtube_videos.py`'s
          `yt-dlp --dump-json` flow as a child resource
      - Emits to `cianfhoghlaim.tg4.foghlaim_lessons`
      - Adds `biep_subject`, `biep_stage`, `has_worksheet` derived columns
      - `primary_key = ["lesson_id"]`, `write_disposition = "merge"`
- [ ] T1.3 — Add the 2 sources to `dlt_sources/cli.py:list-sources`
- [ ] T1.4 — Run `uv run python -m dlt_sources.cli list-sources` — both
      appear in the curated list

## Stage 2 — BAML extraction

- [ ] T2.1 — Create `baml_src/media/tg4_classification.baml` with 4 fns:
      - `ClassifyTg4Episode` → `{genre, biep_subject, biep_stage,
        age_appropriate, educational_use, dialect,
        irish_purity_score: 0.0–1.0}`
      - `ExtractSpeakerLineup` → `{speakers, turns}` from VTT cues
      - `ExtractWorksheetAnswers` → `{questions, total_marks}` from PNG
      - `AuditTranscriptQuality` → `{coverage, disagreement_rate,
        missing_cues, insertion_rate}` from VTT vs WhisperX
- [ ] T2.2 — Add the 4 fns to the existing BIEP BAML clients
      (`baml_src/clients.baml`)
- [ ] T2.3 — Run `baml-cli test` against the 4 fns — all green
- [ ] T2.4 — Run `mise run baml:test` — pass

## Stage 3 — CocoIndex v1 App

- [ ] T3.1 — Create `cocoindex_flows/media/tg4_foghlaim_embedding.py`
      - R1–R4 conformant (imports `.._shared._lifespan`)
      - Reads `cianfhoghlaim.tg4.player_shows` + `cianfhoghlaim.tg4.foghlaim_lessons`
        from DuckLake
      - Reads MP4/WebM from `stedding/ingest_queue/tg4/`
      - 4 LanceDB tables: `tg4_segments`, `tg4_frame_captions`,
        `tg4_triples`, `tg4_quality_audits`
      - Subtitle canonical (your decision) + audio audit (5% sample)
      - Frame sampling `0.1 fps` (one frame per 10s, same as YouTube KG)
      - `qwen3-vl-8b` caption + `molmo2-8b` diagram pointing via
        `MODEL_REGISTRY` (no literal HuggingFace IDs)
      - All 4 BAML fns called per the cost-ordering in proposal.md
- [ ] T3.2 — Run `mise run cocoindex:conformance` — R1–R4 pass
- [ ] T3.3 — Run `mise run cocoindex:update -- cianfhoghlaim.cocoindex_flows.media.tg4_foghlaim_embedding:Tg4FoghlaimEmbedding`

## Stage 4 — Dagster orchestration

- [ ] T4.1 — Create `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml`
      - `type: orchestration.components.CelticModelLifecycleComponent`
      - `app_name: Tg4FoghlaimEmbedding`
      - `module: cianfhoghlaim.cocoindex_flows.media.tg4_foghlaim_embedding`
      - `embedding_model: BAAI/bge-m3`
      - `lance_tables: [tg4_segments, tg4_frame_captions, tg4_triples, tg4_quality_audits]`
      - `ducklake_source: cianfhoghlaim.tg4.player_shows`
      - `refresh_interval_secs: 86400`
      - `frame_sample_fps: 0.1`
      - `audio_leg: cianfhoghlaim.meaisinfhoghlaim.process.transcript_aligner.WhisperXAligner`
- [ ] T4.2 — Create `orchestration/defs/2_materials/tg4_foghlaim/tg4_foghlaim_assets.py`
      - 6 assets: `tg4_player_catalog`, `foghlaim_lessons_catalog`,
        `tg4_video_downloads`, `tg4_subtitle_canonical`,
        `tg4_v1_embedding`, `tg4_quality_audit_summary`
- [ ] T4.3 — Add the new asset group to `orchestration/definitions.py`
- [ ] T4.4 — Run `mise run dagster:dev` and verify the 6 assets
      materialise against `stedding/` cache

## Stage 5 — Storage wiring

- [ ] T5.1 — Add `garage-tg4` bucket resource to
      `bonneagar/stacks/lakehouse/compose.yaml` (alongside the existing
      `garage-raw`, `garage-curated`)
- [ ] T5.2 — Add `stedding/ingest_queue/tg4 → /mnt/garage/cianfhoghlaim/media/tg4`
      symlink to `mise.toml` `[env]` block
- [ ] T5.3 — Run `bun run mise run devops:validate-stacks` — pass
- [ ] T5.4 — Register the `garage-tg4` Infisical bucket policy via
      `bun run scripts/init-vault.ts`

## Stage 6 — Marimo notebook + MotherDuck Dive

- [ ] T6.1 — Create `notebooks/41_tg4_foghlaim_corpus.py`
      - 5 sections: catalogue overview, coverage heatmap, alignment
        audit, sample search, HF Hub export button
- [ ] T6.2 — Run `mise run notebook:control-panel` (or directly
      `marimo edit notebooks/41_tg4_foghlaim_corpus.py`) — all 5
      sections render with real rows
- [ ] T6.3 — Create `motherduck/dives/tg4_corpus_overview.py` —
      the Dive for `tg4_player_shows` + `tg4_quality_audits`
- [ ] T6.4 — Add the Dive to the 5-tab marimo control panel
      (`notebooks/00_control_panel.py`)

## Stage 7 — mise tasks + curated watchlist

- [ ] T7.1 — Add 3 tasks to `mise.toml`:
      - `mise run sync:tg4-player` (runs the DLT `tg4_player_shows` source)
      - `mise run sync:tg4-foghlaim` (runs the DLT `foghlaim_lessons` source)
      - `mise run sync:tg4-all` (chains both + refreshes the v1 App)
- [ ] T7.2 — Append `tg4_official` entry to `stedding/youtube_curated.yaml`
      with `channel_id: 'UC...'` (the verified TG4 YouTube channel)

## Stage 8 — Validation + open spec validation

- [ ] T8.1 — Run `openspec validate 2026-08-25-tg4-foghlaim-corpus-v1 --strict`
- [ ] T8.2 — Run `mise run lint:registry` — no hardcoded model strings
- [ ] T8.3 — Run `mise run lint:skills` — no skill metadata drift
- [ ] T8.4 — Run `mise run lint:drift-docs` — no number claim drift

## Stage 9 — Deploy + publish

- [ ] T9.1 — Deploy `tg4_foghlaim` asset group to `arm1-oci` via Komodo
- [ ] T9.2 — Verify the MotherDuck Dive renders at
      `md:cianfhoghlaim.tg4_corpus_overview`
- [ ] T9.3 — Publish v1 to HuggingFace Hub as
      `cianfhoghlaim/tg4-foghlaim-corpus-v1` via the marimo notebook's
      export button
- [ ] T9.4 — Archive: `openspec archive 2026-08-25-tg4-foghlaim-corpus-v1 --yes`
- [ ] T9.5 — Push: `git pull --rebase && git push` (LAND-THE-PLANE rule)

## Post-deploy follow-ups

- [ ] P1 — Add a Cúla4 (children's channel) subset if the Foghlaim
      YouTube correlation surfaces 100+ unique IDs
- [ ] P2 — Wire `Ros na Rún` drama transcripts into the
      `gaeilge_embedding` v1 App as a 4th data source (after Gaeilge
      NCCA + Gaois parallel + TG4)
- [ ] P3 — Add RTÉ Player (RTÉ.ie) under a sibling change once TG4 v1
      is stable (similar shape, separate openspec change)