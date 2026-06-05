# PaddleOCR — Multi-Language OCR with Layout Analysis

## Overview

PaddleOCR is Baidu's open-source OCR toolkit supporting 80+ languages with built-in text detection, text recognition, table structure recognition, and layout analysis. It provides both a Python SDK and a serving API, and includes pre-trained models for document OCR, scene text, and handwriting.

## Why This Matters for Kings' College Galway

PaddleOCR's multi-language support (including Irish Gaelic `gle` through its Latin script model) and its table structure recognition are particularly valuable for exam paper processing. Leaving Cert papers frequently contain data tables (statistics questions), mark-allocation tables in marking schemes, and multi-column question/answer layouts. PaddleOCR's table recognition extracts these as structured data (CSV/JSON) rather than flat text, preserving the table semantics for downstream analysis. Its layout analysis complements Docling by handling edge cases where Docling's document model doesn't capture the exact table structure.

## Key Features

- **80+ languages** — Including Latin-script languages (Irish Gaelic supported)
- **Table recognition** — Extracts tables as structured CSV/JSON
- **Layout analysis** — Detects text regions, titles, figures, tables
- **Pre-trained models** — No training required; download and use
- **Serving API** — REST and gRPC endpoints for production deployment

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/paddleocr
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Models are downloaded on first run and cached in a Docker volume.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PADDLEOCR_PORT` | No | Serving API port | `8866` |
| `PADDLEOCR_LANG` | No | Language codes | `latin` |
| `PADDLEOCR_DET_MODEL_DIR` | No | Detection model path | `/models/det` |
| `PADDLEOCR_REC_MODEL_DIR` | No | Recognition model path | `/models/rec` |

## Access

- **REST API**: `http://localhost:8866`
- **gRPC API**: `http://localhost:8867`
- **Auth**: Internal-only

## Upstream

- **Repository**: <https://github.com/PaddlePaddle/PaddleOCR>
- **Documentation**: <https://paddlepaddle.github.io/PaddleOCR/>
- **Latest**: v2.9.x (2025) — table recognition improvements, serving API enhancements, 20+ new languages, layout analysis model upgrades

## Screenshot

Headless HTTP/gRPC API. PaddleOCR's serving endpoint accepts images and returns JSON with detected text regions, recognised text, confidence scores, and (for tables) structured CSV output with cell coordinates. The output is consumed by the Dagster pipeline's `pdf_assets` group for downstream BAML extraction.
