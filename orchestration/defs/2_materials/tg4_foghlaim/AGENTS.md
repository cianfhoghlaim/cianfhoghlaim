# `orchestration/defs/2_materials/tg4_foghlaim/` — TG4 + Foghlaim Dagster Assets

> The 6 Dagster assets that materialise the multimodal Irish-language
> media corpus. Added by the `2026-08-25-tg4-foghlaim-corpus-v1` change.

## Routing

Load this AGENTS.md when:

- You need to add / modify a TG4 or Foghlaim asset
- You need to extend the asset group (e.g. add a `tg4_speaker_segments` asset)
- You need to re-run the daily TG4 player catalog refresh

## Quick start

```bash
# Run the 2 DLT sources
uv run python -m dlt_sources.cli run-pipeline tg4_player_shows
uv run python -m dlt_sources.cli run-pipeline foghlaim_lessons

# Materialise all 6 assets via Dagster
mise run sync:tg4-all

# Launch the Dagster UI + materialise manually
mise run dagster:dev
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `tg4_foghlaim_assets.py` | The 6 Dagster assets (2 ingestion + 1 download + 1 subtitle + 1 embedding + 1 audit) |
| `dlt_sources/api_sources/tg4_player_shows.py` | The TG4 player catalog DLT source |
| `dlt_sources/api_sources/foghlaim_lessons.py` | The Foghlaim lessons DLT source |
| `baml_src/media/tg4_classification.baml` | The 4 BAML fns |
| `cocoindex_flows/media/tg4_foghlaim_embedding.py` | The v1 App |
| `orchestration/defs/3_model_lifecycle/cocoindex_v1/tg4_foghlaim/defs.yaml` | The L3 Component |

## The 6 assets

| Asset | Layer | Purpose |
|:--|:--|:--|
| `tg4_player_catalog` | 1 (Ingestion) | DLT → `cianfhoghlaim.tg4.player_shows` |
| `foghlaim_lessons_catalog` | 1 (Ingestion) | DLT → `cianfhoghlaim.tg4.foghlaim_lessons` |
| `tg4_video_downloads` | 2 (Materials) | S3 download (gated behind `TG4_DOWNLOAD_MEDIA=full`) |
| `tg4_subtitle_canonical` | 2 (Materials) | VTT fetch from Brightcove `text_tracks` |
| `tg4_v1_embedding` | 3 (Model Lifecycle) | Materialises the 4 LanceDB tables |
| `tg4_quality_audit_summary` | 4 (Asset Generation) | MotherDuck Dive summary |

## Adjacent specs

- [`tg4-foghlaim-corpus`](../../../../openspec/specs/tg4-foghlaim-corpus/spec.md)
  — the parent capability spec
- [`dagster-5-layer-component-architecture`](../../../../openspec/specs/dagster-5-layer-component-architecture/spec.md)
  — the 5-layer model this directory implements

## DO NOT

- **Never** run `tg4_video_downloads` without `TG4_DOWNLOAD_MEDIA=full`.
  The default `skip` respects TG4's T&Cs.
- **Never** hardcode a Brightcove account ID — route via Infisical
  (`infisical://dev-baile/cianfhoghlaim/tg4-brightcove-account-id`).
- **Never** import raw `duckdb.connect()` in BIEP v3 paths — use
  `ibis.duckdb.connect("md:cianfhoghlaim")`.

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`dagster`](../../../.agents/skills/dagster/SKILL.md) | Dagster 1.13+ Declarative Automation |
| [`dlt`](../../../.agents/skills/dlt/SKILL.md) | DLT source canonical pattern |
| [`cocoindex`](../../../.agents/skills/cocoindex/SKILL.md) | R1–R4 conformance + LanceDB targets |
| [`centralized-registry`](../../../.agents/skills/centralized-registry/SKILL.md) | The MODEL_REGISTRY contract |

<!-- generated: 2026-08-25; do not hand-edit -->