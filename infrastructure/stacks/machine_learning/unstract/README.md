# Unstract — LLM-Powered Document Processing Platform

## Overview

Unstract is an open-source platform for building document processing pipelines powered by LLMs. It provides a visual workflow builder for document extraction, classification, and transformation — connecting document ingestion (S3, API, email) through LLM processing to structured output (databases, APIs, spreadsheets). Unlike code-only extraction pipelines, Unstract provides a UI for designing and monitoring document workflows.

## Why This Matters for Kings' College Galway

The curriculum extraction pipeline processes a wide variety of documents: syllabus PDFs (from NCCA), exam papers (from SEC), marking schemes, chief examiner reports, and curriculum frameworks (from multiple jurisdictions — Ireland, UK, Wales, Scotland). Each document type has different extraction requirements. Unstract provides a visual workflow builder where non-engineer curriculum researchers can design extraction templates — "for this type of document, extract these fields using this LLM prompt" — without writing Dagster assets or BAML schemas. This bridges the gap between the engineering team (who build the core pipeline) and the education team (who define what to extract).

## Key Features

- **Visual workflow builder** — Drag-and-drop document processing pipelines
- **LLM-powered extraction** — Use any LLM (local or cloud) for document understanding
- **Multi-source ingestion** — S3, API, email, manual upload
- **Structured output** — Export to databases, APIs, CSV, JSON
- **Prompt management** — Version and A/B test extraction prompts

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/unstract
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Connects to the LiteLLM gateway for LLM access and Garage S3 for document storage.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `UNSTRACT_PORT` | No | Web UI port | `8000` |
| `UNSTRACT_API_PORT` | No | API port | `8001` |
| `LLM_ENDPOINT` | Yes | LiteLLM gateway URL | `http://litellm:4000/v1` |
| `S3_ENDPOINT` | Yes | Garage S3 endpoint | — |
| `DB_CONNECTION` | Yes | PostgreSQL connection string | — |

## Access

- **Web UI**: `https://unstract.cianfhoghlaim.ie` (private, Member role)
- **API**: `http://localhost:8001`
- **Auth**: Email/password + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/Zipstack/unstract>
- **Documentation**: <https://docs.unstract.com>
- **Latest**: Active development — LLM prompt versioning, multi-step workflows, API extraction templates, structured output formatting

## Screenshot

Unstract's web UI provides a workflow canvas where users drag document sources, LLM extraction steps, and output destinations into a pipeline. The prompt editor shows the extraction prompt template with document variable placeholders. A test mode lets you run a single document through the pipeline and inspect the structured output at each step.
