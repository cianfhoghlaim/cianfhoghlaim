# Change: TG4 + Foghlaim Media Corpus (BIEP v3 media streaming enrichment)

## Why

TG4 (`tg4.ie`) is Ireland's Irish-language public broadcaster. Its
on-demand player and the parallel educational portal `foghlaim.tg4.ie`
together host **the largest open corpus of modern spoken Irish
(Gaeilge) on the public internet**:

- **Player**: 8 genres × N seasons of news (`Nuacht TG4`, ~36 episodes
  per season), drama (`Ros na Rún`), music, sport, factual, lifestyle,
  children's (`Cúla4`), and box-sets (`Bailiúcháin`). Backed by
  **Brightcove Video Cloud** (13-digit `pid`) + **Cloudinary** posters
  + **Video.js** player, with public WebVTT captions on the Brightcove
  `text_tracks` endpoint.
- **Foghlaim**: ~1,500+ classroom-tagged lessons across 3 educational
  levels (Bunscoil / Sraith Shóisearach & GCSE / Ardteist, AS/A2 &
  Adult Learners) and 11+ subjects that map 1:1 onto BIEP v3 subjects.
  Built with **Nuxt.js** (the `<div id="__nuxt">` SSR marker). Lessons
  ship at `/ceacht/<id>` with two source flavours: **Brightcove IDs**
  (13-digit) and **YouTube IDs** (11-char). Each lesson has keywords
  (`Eochairfhocail`), worksheets (`Bileoga Oibre agus Freagraí`),
  support material, and learning outcomes (`Spriocanna Foghlama`).

Today we have **zero** coverage. `grep -rE 'tg4|foghlaim|cúla4|nuacht'`
across `dlt_sources/`, `agents/`, `orchestration/`, and `baml_src/`
returns only the `audiobookshelf` stack README that *mentions* TG4
audio as a future use case. No DLT sources, no CocoIndex flows, no
BAML extraction schemas, no Dagster assets. Greenfield.

A HuggingFace Hub search for `TG4 Irish television`, `Irish television
TG4 Nuacht`, `Irish language video subtitles`, and
`TG4 Nuacht Cula4 Cine4 Irish television broadcast` returns **zero
matches in any combination** — first-mover position for the dataset.

The good news: ~85% of the surface area we need **already exists** in the
monorepo:

| Existing asset | Path | Reuse for |
|:--|:--|:--|
| yt-dlp DLT source (382 lines) | `dlt_sources/api_sources/youtube_videos.py` | Foghlaim's YouTube-sourced lessons |
| YouTube KG v1 App (576 lines) | `cocoindex_flows/knowledge_graph/youtube_kg_embedding.py` | WhisperX audio leg + frame captioning + BAML triples template |
| Media Local v1 App | `cocoindex_flows/media/` | The local-MP4 cousin (`MediaLocalEmbedding`) |
| Irish transcript aligner | `meaisinfhoghlaim/process/transcript_aligner.py` | WhisperX + MFA + CTC + DTW Irish audio alignment |
| Irish dialect classifier | `meaisinfhoghlaim/process/dialect_classifier.py` | Connacht/Munster/Ulster tagging per segment |
| L3 component def | `orchestration/defs/3_model_lifecycle/cocoindex_v1/youtube_kg/defs.yaml` | Drop-in template |
| Pinchflat stack | `bonneagar/stacks/pinchflat/` | Already in the IaC mesh (README mentions Irish-medium channels) |
| Audiobookshelf stack | `bonneagar/stacks/audiobookshelf/` | Already in the IaC mesh (README mentions TG4 audio) |
| Lakehouse stack | `bonneagar/stacks/lakehouse/` | Garage S3 + Lakekeeper Iceberg + Postgres |
| BAML grammar patterns | `baml_src/celtic/grammar_patterns.baml` | Reusable for Irish-mutation-aware transcript cleanup |
| Gaeilge + Gaois CocoIndex Apps | `cocoindex_flows/celtic/` | Reference for Irish-only embedding flows |
| BIEP v3 umbrella | `openspec/specs/british-isles-education-pipeline-v3/spec.md` | The destination spec to MODIFY |

## What changes

- **TG4 + Foghlaim Media Corpus** (NEW capability
  `tg4-foghlaim-corpus`): 2 DLT sources (TG4 player catalog +
  Foghlaim lessons) + 1 CocoIndex v1 App + 4 LanceDB tables + 4 BAML
  functions + 6 Dagster assets + 1 marimo notebook + 1 MotherDuck Dive.

- **BIEP v3 media streaming enrichment** (MODIFIED capability
  `british-isles-education-pipeline-v3`): 2 ADDED Requirements that
  join TG4 player shows + Foghlaim lessons into the existing 6 LC
  subjects + 18 JC subjects via a `biep_subject` taxonomy.

## Out of scope

- A Jellyfin / Peertube / Audiobookshelf re-streaming stack (Garage
  S3 + Lakehouse is sufficient — users browse via the marimo notebook).
- RTÉ Player / RTÉ archive (similar shape but separate change).
- Live broadcasts (`feach-beo/baile/`) — only the on-demand catalogue
  is in scope.
- A real-time WhisperX pipeline (we re-use the existing
  `WhisperXAligner` on a 5% audit sample + every NCCA-tagged lesson).

## Dependencies

`Blocked by: none`

`Blocked by (soft): 2026-07-14-multimodal-code-and-media-intel-v1` — the
YouTube KG v1 App is the architectural template; already archived, so
this is informational only.

`Affected repos: cianfhoghlaim`

## Impact

- Affected specs:
  - NEW: `tg4-foghlaim-corpus` (5 ADDED Requirements)
  - MODIFIED: `british-isles-education-pipeline-v3` (2 ADDED Requirements)
- Affected code/config:
  - `dlt_sources/api_sources/tg4_player_shows.py` (NEW)
  - `dlt_sources/api_sources/foghlaim_lessons.py` (NEW)
  - `baml_src/media/tg4_classification.baml` (NEW)
  - `cocoindex_flows/media/tg4_foghlaim_embedding.py` (NEW)
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml` (NEW)
  - `orchestration/defs/2_materials/tg4_foghlaim/tg4_foghlaim_assets.py` (NEW)
  - `notebooks/41_tg4_foghlaim_corpus.py` (NEW)
  - `bonneagar/stacks/lakehouse/compose.yaml` (1 `garage-tg4` bucket resource added)
  - `mise.toml` (1 `sync:tg4-*` task family + `stedding` symlink entry)
  - `stedding/youtube_curated.yaml` (extended with a `tg4_official` channel entry)
- Affected observability:
  - Dagster asset group `tg4_foghlaim` (6 assets)
  - Dagster sensor `tg4_player_new_episode_sensor` (re-fires on new
    Brightcove `pid` discovery)
  - MotherDuck Dive `tg4_corpus_overview`
  - Langfuse span prefix `tg4_foghlaim.*` (mirrors the BAML fn names)
- Affected secret contract:
  - NEW Infisical secret: `infisical://dev-baile/cianfhoghlaim/tg4-brightcove-account-id`
    (the public Brightcove account ID + policy key, both public — stored
    in Infisical for version control + audit, not for secrecy)

## Risks & open questions

1. **Brightcove policy key rotation** — TG4's policy key is public but
   can rotate. The DLT source caches the key + auto-refreshes on 401.
2. **TG4 T&Cs** — broadcast content is copyrighted; the DLT source is
   **metadata-only by default** (the VTT + frame captions + BAML
   triples). MP4 download is gated behind the `TG4_DOWNLOAD_MEDIA=full`
   env var (opt-in for personal/educational use).
3. **Foghlaim source duality** — the Brightcove half mirrors the
   player catalog; the YouTube half duplicates content on Cúla4's
   YouTube channel. The two-source approach is intentional — Foghlaim
   lessons get the richer worksheet metadata.
4. **Asset group naming** — `tg4_foghlaim` matches the spec name +
   archive-folder convention.
5. **HF dataset license** — derived dataset (transcripts + frame
   captions + BAML triples, no MP4s) is **CC-BY-SA-4.0** with a clear
   `README.md` notice that the MP4 video files are not redistributed.
6. **BAML function cost ordering** — `ClassifyTg4Episode` (cheap) →
   `ExtractSpeakerLineup` (medium) → `ExtractWorksheetAnswers` (VLM,
   expensive) → `AuditTranscriptQuality` (audio re-decode, most
   expensive). All4 on every NCCA-tagged lesson; rest skip
   `AuditTranscriptQuality` (5% sample) and `ExtractWorksheetAnswers`
   (only when `has_worksheet=true`).