# meaisinfhoghlaim v3 — Cron Schedule

> Per the meaisinfhoghlaim v5 umbrella spec. The 4-cadence meaisinfhoghlaim
> scheduling policy in detail.

## Overview

The meaisinfhoghlaim v5 surface implements a **4-cadence scheduling policy**:

1. **Weekly** for the M0 foundation + registry audit + HF watchdog
2. **Nightly** for the RAGAS BIEP ensemble + 4-path OCR ensemble evaluations
3. **Monthly** for the 7 document converter pipeline
4. **Event-driven** (eager) for the HuggingFace watchdog + DriftMonitor

## Weekly cadence (Monday 06:00 UTC)

The weekly cron expression is `0 6 * * 1`. This fires on Monday at
06:00 UTC, which is a low-traffic window. The weekly cron triggers:

- `mise run cic:meaisin:registry-audit` — verifies the 24-model v4 registry
- `mise run cic:meaisin:hf-watchdog` — verifies the HuggingFace watchdog
- `mise run lint:skills` — validates the 53/53 skill metadata

The 3 weekly Dagster assets:

| Asset | Purpose |
|:--|:--|
| `meaisin_registry_audit` | Verifies the 24 OCR/VLM model registry |
| `meaisin_hf_watchdog` | Verifies the HuggingFace watchdog |
| `meaisin_lint_skills` | Validates the 53/53 skill metadata |

## Nightly cadence (00:00 UTC)

The nightly cron expression is `0 0 * * *`. This fires every day at
00:00 UTC. The nightly cron triggers:

- `cic:ocr:test` — the OCR evaluation harness
- `cic:ocr:eval` — the OCR evaluation pipeline
- `cic:ocr:registry-lint` — the OCR registry lint

The 3 nightly Dagster assets:

| Asset | Purpose |
|:--|:--|
| `meaisin_ocr_evaluation` | The OCR evaluation harness |
| `meaisin_ragas_evaluation` | The RAGAS BIEP ensemble evaluation |
| `meaisin_ensemble_audit` | The 4-path OCR ensemble audit |

## Monthly cadence (1st of each month 00:00 UTC)

The monthly cron expression is `0 0 1 * *`. This fires on the 1st of
each month at 00:00 UTC. The monthly cron triggers the 7 document
converter pipeline.

The 7 monthly Dagster assets:

| Asset | Converter |
|:--|:--|
| `meaisin_docling_ingestion` | IBM Docling |
| `meaisin_marker_ingestion` | Marker PDF converter |
| `meaisin_unstructured_ingestion` | Unstructured.io |
| `meaisin_deepseekocr_ingestion` | DeepSeek OCR |
| `meaisin_pymupdf4llm_ingestion` | PyMuPDF4LLM |
| `meaisin_curriculum_document_ingestion` | Custom for cianfhoghlaim |
| `meaisin_pdf_factory_ingestion` | Custom PDF generator |

## Event-driven cadence (eager)

The HuggingFace watchdog + DriftMonitor are event-driven:

- `meaisin_hf_watchdog` — triggers on every new HF model release
- `meaisin_drift_monitor` — triggers on every drift detection

## Per-asset + per-converter + per-model + per-agent cron schedule table

| Component | Cadence | Cron | Mise task |
|:--|:--|:--|:--|
| M0 foundation (registry audit + HF watchdog + lint) | Weekly | `0 6 * * 1` | `meaisin:v3:setup` |
| 24 OCR entries (4-path OCR ensemble evaluations) | Nightly | `0 0 * * *` | `cic:ocr:test` |
| 7 document converters (conversion pipeline) | Monthly | `0 0 1 * *` | `meaisin:converter:test:<name>` |
| 12 agents (per-agent memory + observability) | Event-driven | n/a | `meaisin:agent:test:<name>` |
| RAGAS BIEP ensemble | Nightly | `0 0 * * *` | `cic:ocr:eval` |
| HF watchdog | Weekly | `0 6 * * 1` | `cic:meaisin:hf-watchdog` |
| DriftMonitor | Weekly | `0 6 * * 1` | `cic:meaisin:registry-audit` |

## See also

- `meaisin-v3-systematic-download.md` — the canonical newcomer guide
- `meaisin-v3-quickstart.md` — the "first 30 minutes" guide
- `meaisin-v3-faq.md` — the canonical FAQ
- `meaisin-v3-ocr-vlm-client.md` — how to invoke the 24 OCR/VLM models
- `meaisin-v3-storage-layout.md` — the canonical meaisinfhoghlaim storage layout
- `meaisin-v3-mieaisin-7-packages.md` — the 11 sub-packages overview
