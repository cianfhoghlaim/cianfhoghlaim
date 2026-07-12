# Dots OCR — Lightweight Document OCR Service

## Overview

Dots OCR is a lightweight, containerised OCR service focused on speed and simplicity. It wraps Tesseract and other open-source OCR engines in a clean HTTP API, optimised for batch processing of document images at high throughput.

## Why This Matters for Kings' College Galway

While OLMOCR handles the high-quality MLX-based OCR for scanned exam papers, Dots OCR serves as the fast-throughput alternative for born-digital PDFs and modern exam papers that don't need AI-powered recognition. For the 2015-2024 exam papers (which are digital PDFs with embedded text layers), Dots OCR provides sub-second page processing — much faster than spinning up an MLX model. This two-tier OCR strategy (MLX for scans, Dots for digital) dramatically reduces the processing time for a full curriculum extraction run.

## Key Features

- **High-throughput** — Optimised for batch processing of clean digital documents
- **Tesseract-backed** — Mature, battle-tested OCR engine
- **Simple HTTP API** — Single endpoint: POST image, receive text
- **Lightweight** — Minimal container, low memory footprint

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/dots-ocr
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DOTS_OCR_PORT` | No | API port | `8000` |
| `TESSERACT_LANG` | No | Language codes | `eng+gle` |
| `TESSDATA_PREFIX` | No | Tesseract data path | `/usr/share/tesseract-ocr/5/tessdata` |

## Access

- **API**: `http://localhost:8000`
- **Auth**: Internal-only

## Upstream

- **Repository**: <https://github.com/nicholasgriffintn/dots-ocr>
- **Latest**: Active development — Tesseract 5 support, multi-language configuration, batch processing improvements

## Screenshot

Headless HTTP API. Dots OCR provides a simple POST endpoint accepting image files and returning extracted text. The service is used programmatically by the Dagster pipeline — when `USE_LOCAL_SCRAPES=true` is set, Dots OCR processes locally cached PDFs instead of calling cloud OCR services.
