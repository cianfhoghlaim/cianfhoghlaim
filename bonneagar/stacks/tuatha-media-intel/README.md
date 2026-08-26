# tuatha-media-intel

The British Isles Formative Assessment MMO — capture → VLM → ANAM pipeline.

Captures frames from games you play (Phase 1, manual; Phase 2 stubbed for
Hermes Agent control), extracts typed BAML records via local VLMs
(Qwen3-VL via llama-swap), and indexes them in LanceDB multimodal fat
tables. The cross-source join produces the ANAM particle corpus that
feeds the 2D TanStack Start client + the Celtic deity mapping in
`tuatha/subjects/character.py`.

## Components

| Container | Image | Purpose |
|:--|:--|:--|
| `cocoindex-runner` | `cianhoghlaim/cocoindex-runner:1.0.14` | Runs the 4 v1 CocoIndex flows |
| `baml-codegen` | `cianhoghlaim/baml-codegen:0.200.0` | Regenerates `baml_client/` from `.baml` sources every 5min |
| `ragas-evaluator` | `cianhoghlaim/ragas-evaluator:0.2.10` | Nightly quality check on `anam_particles_v1` |
| `mlflow-sidecar` | `cianhoghlaim/locket-sidecar:0.7.0` | Proxies metrics to central MLflow |
| `locket` | (host) | Hydrates secrets from Infisical at runtime |

## Quick start

```bash
mise run stack:tuatha-media-intel:up
mise run stack:tuatha-media-intel:logs
```

Or directly:

```bash
cd bonneagar/stacks/tuatha-media-intel/
cp .env.example .env  # then either fill values or rely on Locket
docker compose --env-file .env up -d
```

## Verification

```bash
# Confirm the 6-file GOLD_STANDARD passes
mise run cic:stack-doctor | grep tuatha-media-intel

# Confirm the CocoIndex flows registered
docker exec tuatha-media-intel-cocoindex-runner-1 \
  cocoindex list | grep tuatha

# Confirm the RAGAS asset_check wired
mise run dagster:check ragas_anam_color_anchor
```

## See also

- `tuatha_media_intel.baml` — the BAML source of truth for the 3 typed classes
- `cocoindex_flows/tuatha_media_intel/ingestors/` — the 4 v1 Apps
- `orchestration/defs/2_materials/tuatha_media_intel.py` — the Dagster assets
- `notebooks/tuatha_anam_dashboard.py` — the marimo design surface (4 tabs)
- `tuatha_media_intel/capture/tuatha-capture/` — the Swift capture daemon
- `tuatha_media_intel/capture/python/` — the Python capture shims

## Shippable invariant

The full-resolution captures (game frames, comic pages, GBA dumps) never
leave the Pangolin-private `cianfhoghlaim-tuatha-raw` bucket (7-day TTL).
The Lance fat tables carry only `thumb_blob` (≤1024px) + BAML-extracted
description + embedding. Per the tuatha skill `shippable: false` invariant:
no copyrighted material ever enters the repo.
