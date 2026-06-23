# Stirling PDF — Self-Hosted PDF Manipulation Toolkit

## Overview

Stirling PDF is an open-source, self-hosted web application providing 50+ PDF manipulation tools. It can merge, split, rotate, compress, OCR, convert (to/from Word, Excel, PowerPoint, images), sign, redact, and watermark PDFs through a clean web UI. Built with Spring Boot and LibreOffice, all processing happens locally.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline processes hundreds of PDFs: SEC exam papers, NCCA syllabus documents, marking schemes, and chief examiner reports. These PDFs need preprocessing before entering the extraction pipeline — merging multi-part exam papers, compressing large scanned PDFs, OCR-ing older documents, and converting Word-based teacher resources to PDF. Stirling PDF provides all of these in a single self-hosted tool, eliminating Adobe Acrobat or online PDF converters which would leak educational data to third parties.

## Key Features

- **50+ PDF tools** — Merge, split, rotate, compress, OCR, convert, sign, redact, watermark
- **Office format conversion** — Convert between PDF and Word, Excel, PowerPoint, HTML, images
- **OCR** — Add searchable text layers to scanned PDFs (Tesseract-powered)
- **Compression** — Reduce file size while preserving quality
- **Privacy-first** — All processing happens locally; no data sent to external services

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/stirling-pdf
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. PDF processing is CPU-intensive; allocate sufficient resources for batch operations.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `STIRLING_PDF_PORT` | No | Web UI port | `8080` |
| `DOCKER_ENABLE_SECURITY` | No | Enable login | `true` |
| `SYSTEM_DEFAULTLOCALE` | No | Default locale | `en-IE` |

## Access

- **Web UI**: `https://stirling-pdf.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/Stirling-Tools/Stirling-PDF>
- **Documentation**: <https://docs.stirlingpdf.com>
- **Latest**: Active development (2025) — 50+ tools, UI redesign, improved OCR, ARM64 support

## Screenshot

Stirling PDF's web UI presents a grid of tool cards organised by category: Organise (merge, split, rotate, extract), Convert (to/from Word, Excel, PPT, images), Edit (add text, images, watermarks, redact), Security (encrypt, decrypt, sign), and Optimise (compress, OCR, repair). Each card leads to a drag-and-drop interface for processing files with configuration options.
