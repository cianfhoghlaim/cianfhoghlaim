# OCR Router — OCR / VLM Capability Gateway

## Overview

OCR Router is the single FastAPI service that maps a `requested
capability` to the best-fit OCR / VLM backend. It replaces the
operator-decision model (where the BIEP v3 pipeline had to choose
backend per-document manually) with an explicit router.

The router exposes a single endpoint:

```
POST /ocr
{
  "capability": "tables+latex",
  "image_url": "s3://lakehouse/lc_chem_2024.pdf"
}
→ { result_url, backend_used, model, duration_ms, webhook_delivered }
```

## Why This Matters for Kings' College Galway

BIEP v3 ingests 1,146 active items across 8 jurisdictions + 2
scanner domains. OCR is the chokepoint for the forms-heavy
Northern Ireland (CCEA) + Wales (WJEC, Welsh-medium) corpora. Without
this router, every pipeline operator must manually pick a backend per
document, and the BIEP v3 sensors cannot react to OCR completion
events. The router ships:

- **A single decision point** (one place to add a new backend)
- **An OCR completion webhook** (`OCR_WEBHOOK_URL`) that triggers the
  Dagster `ocr_completion_sensor` (downstream BIEP v3 materialisation)
- **A unified observability surface** (every backend + the router
  emit OTLP traces via the logfire collector — fans out to BOTH
  logfire cloud AND langfuse per Change 1 of the
  env-contract-and-observability-fanout trilogy)

## Key Features

- **Capability dispatch** — single decision table; backends plug in
  without changing litellm
- **Webhook emit** — every completion POSTs to `OCR_WEBHOOK_URL`
  (idempotent; document_id + created_at dedup window in the sensor)
- **Timeout-bounded** — `OCR_ROUTER_TIMEOUT_MS` per request (default
  30s)
- **Observability-coherent** — emits OTLP to logfire-otel:4317 (the
  same collector used by graphiti/cognee/mlflow/agent-os)

## Dispatch Matrix

| Capability | Backend | URL | Use case |
|:--|:--|:--|:--|
| `forms` | paddleocr | `http://paddleocr:8000/v1` | Handwritten + printed forms (CCEA / WJEC) |
| `layout` | mlx-omni | `http://mlx-omni:10240/v1` | Dense + sparse layout, sections |
| `tables+latex` | olmocr | `http://olmocr:8003/v1` | Math + table extraction |
| `doctags` | docling-serve | `http://docling-serve:5001/v1` | IBM DocTags format |
| `gaelic` | llama-swap | `http://llama-swap:8080/v1` | Modern Irish (Gemma 4 26B-A4B) |
| `english` | llama-swap | `http://llama-swap:8080/v1` | English vision (Qwen 3-VL 8B) |
| `tesseract-fallback` | dots-ocr | `http://dots-ocr:8001/v1` | Legacy Tesseract OCR |

## Deployment

### Docker Compose (Local)

```bash
cd bonneagar/stacks/ocr-router
cp .env.example .env.local  # edit values as needed
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Production (via Komodo)

Deployed via Komodo on `bunchloch` (MacBook M4). The router MUST
come up after the 6 OCR / VLM backends (paddleocr, dots-ocr, olmocr,
docling-serve, mlx-omni, llama-swap) so the in-network DNS names
resolve.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OCR_ROUTER_PORT` | No | Router port (host binding) | `8090` |
| `OCR_ROUTER_TIMEOUT_MS` | No | Per-request timeout | `30000` |
| `OCR_ROUTER_API_KEY` | Yes (prod) | Clients send `Authorization: Bearer $OCR_ROUTER_API_KEY` | — |
| `OCR_WEBHOOK_URL` | No | POST on completion; empty = graceful skip | — |
| `OCR_WEBHOOK_TOKEN` | No | HTTP Basic auth on webhook | — |
| `OCR_PADDLEOCR_URL` | No | paddleocr endpoint | `http://paddleocr:8000/v1` |
| `OCR_MLX_OMNI_URL` | No | mlx-omni endpoint | `http://mlx-omni:10240/v1` |
| `OCR_OLMOCR_URL` | No | olmocr endpoint | `http://olmocr:8003/v1` |
| `OCR_DOCLING_SERVE_URL` | No | docling-serve endpoint | `http://docling-serve:5001/v1` |
| `OCR_LLAMA_SWAP_URL` | No | llama-swap endpoint | `http://llama-swap:8080/v1` |
| `OCR_DOTS_OCR_URL` | No | dots-ocr endpoint | `http://dots-ocr:8001/v1` |

## Access

- **Operator debugging**: `https://ocr-router.cianfhoghlaim.ie` (Pocket ID passkey)
- **In-network**: `http://ocr-router:8090/ocr` (BIEP v3 Dagster pipelines)

## Webhook Payload

Per spec delta on `british-isles-education-pipeline-v3`:

```json
{
  "document_id": "<uuid>",
  "capability": "<forms|layout|tables+latex|doctags|gaelic|english>",
  "backend_used": "<paddleocr|mlx-omni|olmocr|docling-serve|llama-swap|dots-ocr>",
  "model": "<model name>",
  "result_url": "<s3://lakehouse/ocr/...>",
  "duration_ms": <int>,
  "trace_id": "<opentelemetry trace id>",
  "completed_at": "<iso-8601 utc>"
}
```

## Cross-references

- `openspec/changes/2026-07-31-.../specs/agent-platform-cluster/spec.md` — the OCR routing requirement
- `openspec/changes/2026-07-31-.../specs/british-isles-education-pipeline-v3/spec.md` — the webhook + sensor requirement
- `.agents/skills/agent-observability/SKILL.md` — the observability contract
- `docs/observability/env-var-contract.md` — the canonical 17-var observability reference

## Upstream

- **FastAPI**: <https://fastapi.tiangolo.com>
- **Pydantic v2**: <https://docs.pydantic.dev/latest/>
- **OpenTelemetry**: <https://opentelemetry.io>