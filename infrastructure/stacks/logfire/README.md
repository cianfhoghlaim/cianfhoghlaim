# Logfire — Pydantic Observability Platform

## Overview

Logfire is an observability platform by Pydantic (the creators of the Pydantic validation library) that provides structured logging, tracing, and metrics for Python applications. It integrates natively with Pydantic models, FastAPI, and the Python standard library `logging` module — with zero-config structured output.

## Why This Matters for Kings' College Galway

The entire data platform (Dagster, DLT, BAML extraction) is written in Python and heavily uses Pydantic models for data validation (curriculum specs, exam paper structures, image generation configs). Logfire provides Python-native observability that understands Pydantic models — when a validation error occurs in the `CurriculumSpecification` model during extraction, Logfire captures the full model context, the failing field, and the input data that caused the error. This is more actionable than generic stack traces because it shows the Pydantic field path that failed, not just the line number.

## Key Features

- **Pydantic-native** — Automatic tracing of model validation, serialization
- **Structured logging** — Every log is a typed event, not a string
- **SQL querying** — Query logs and traces with standard SQL
- **FastAPI integration** — Automatic request/response tracing
- **Python logging bridge** — Drop-in replacement for `logging.getLogger()`

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/logfire
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves service tokens from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LOGFIRE_TOKEN` | Yes | Logfire service token | — |
| `LOGFIRE_PROJECT` | No | Project name | `kings-college-galway` |

## Access

- **Web UI**: `https://logfire.cianfhoghlaim.ie` (private, Member role)
- **API**: Internal SDK integration
- **Auth**: Service token (machine); Pocket ID SSO (human)

## Upstream

- **Repository**: <https://github.com/pydantic/logfire>
- **Documentation**: <https://docs.pydantic.dev/logfire/>
- **Latest**: Active development (2025) — SQL query support, FastAPI middleware v2, Pydantic v2 native validation tracing

## Screenshot

Logfire's web UI provides a trace explorer with waterfall visualisation (similar to Langfuse but focused on Python execution rather than LLM calls), structured log search with field-level filters, and a SQL query editor for aggregating trace data. Pydantic model validation errors are highlighted with the exact field path that caused the failure.
