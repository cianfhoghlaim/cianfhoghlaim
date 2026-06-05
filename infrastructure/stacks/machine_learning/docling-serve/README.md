# Docling Serve — PDF Document Understanding Server

## Overview

Docling Serve is an HTTP API server wrapping IBM's Docling library, which converts PDF documents into structured formats (markdown, JSON, DocTags XML). Unlike traditional OCR, Docling understands document layout — it can identify headings, paragraphs, tables, figures, and equations, preserving the document's logical structure rather than just extracting raw text.

## Why This Matters for Kings' College Galway

Leaving Cert exam papers are heavily structured documents with complex layouts: multi-column question formats, embedded diagrams and graphs, mathematical equations, and bilingual Irish/English sections. Docling processes these papers into structured DocTags XML that preserves the semantic hierarchy — "this is Question 2, part (a), containing a trigonometric equation and a diagram." The structured output feeds into BAML extraction where individual questions and marking scheme components are isolated for the RAGAS evaluation pipeline. Docling's layout understanding is what makes it possible to correctly associate a diagram with its surrounding question text.

## Key Features

- **Layout-aware parsing** — Understands headings, paragraphs, tables, figures, equations
- **DocTags XML output** — Structured document representation for downstream processing
- **Equation recognition** — Preserves mathematical notation structure
- **Multi-column handling** — Correctly reads newspaper-style exam layouts
- **MLX backend** — Runs on Apple Silicon via the mlx-omni stack

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/docling-serve
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on bunchloch (MacBook M4) for MLX acceleration. The server exposes an HTTP API that the Dagster pipeline and LiteLLM gateway call for PDF processing.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DOCLING_PORT` | No | API port | `8100` |
| `DOCLING_MODEL` | No | Model to use | `granite-docling` |
| `MLX_ENABLED` | No | Use MLX acceleration | `true` |

## Access

- **API**: `http://localhost:8100`
- **Auth**: Internal-only (not exposed publicly)

## Upstream

- **Repository**: <https://github.com/DS4SD/docling>
- **Documentation**: <https://ds4sd.github.io/docling/>
- **Latest**: Active development — MLX backend, improved table extraction, equation recognition, multi-language support

## Screenshot

Docling Serve is a headless HTTP API. The `/docs` endpoint provides a Swagger UI for testing PDF conversion interactively. Output is structured JSON/XML showing the document's logical tree: sections, paragraphs (with positions), tables (with cell coordinates), and figures (with bounding boxes and captions).
