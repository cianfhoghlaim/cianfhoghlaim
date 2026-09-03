# Spec delta: `british-isles-education-pipeline-v3`

This delta is part of the openspec change
`2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1`. It adds 2
requirements that wire the OCR completion webhook convention + Dagster
sensor into the BIEP v3 ingestion pipeline.

## ADDED Requirements

### Requirement: OCR completion webhook convention

The system MUST provide a single OCR_WEBHOOK_URL env convention that
the OCR router (at `bonneagar/stacks/ocr-router/`) MUST honour when
emitting OCR completion events. The webhook payload MUST be a JSON
envelope:

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

The system MUST emit the webhook as a `POST` to `OCR_WEBHOOK_URL` with
HTTP Basic auth using the `OCR_WEBHOOK_TOKEN` env var. If
`OCR_WEBHOOK_URL` is empty, the router MUST skip the emission (graceful
degradation, matching the SaaS-only Logfire pattern).

The webhook MUST be idempotent: re-delivery of the same `document_id`
MUST be a no-op (the Dagster sensor filters by document_id + a
`created_at` window).

#### Scenario: Dagster sensor consumes the OCR completion event

```
# At OCR_WEBHOOK_URL=http://dagster-webhook:8080/webhooks/ocr_completion
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -H "Authorization: Basic $OCR_WEBHOOK_AUTH" \
    -d '{"document_id": "doc-abc", "capability": "tables+latex",
         "backend_used": "olmocr", "model": "olmocr-2-7b-1025",
         "result_url": "s3://lakehouse/ocr/abc.json",
         "duration_ms": 4128, "trace_id": "trace-def",
         "completed_at": "2026-07-31T12:34:56Z"}'
[webhook] 202 Accepted
[dagster-sensor] sensor_trigger(ocr_completion, document_id="doc-abc")
[asset]    ocr_extraction/lc_chem_2024_materialized (downstream triggers)
```

#### Scenario: re-delivery is a no-op

```
# Same document_id delivered twice within the 1-minute dedup window:
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -d '{"document_id": "doc-abc", ...}'
[webhook] 202 Accepted  (first delivery)
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -d '{"document_id": "doc-abc", ...}'
[webhook] 202 Accepted  (re-delivery — sensor filters out as duplicate)
```

### Requirement: Dagster ocr_completion_sensor

The system MUST provide a Dagster sensor
`orchestration/sensors/ocr_completion_sensor.py` that:

1. Polls the OCR_WEBHOOK_URL endpoint on a 30-second tick
2. Filters duplicates by `(document_id, completed_at)` tuple (in-memory
   dedup with a 1-minute rolling window)
3. Materialises a per-document `ocr_extraction/<document_id>` asset on
   receipt of a new event
4. Triggers the downstream `biiep_v3_<jurisdiction>_materialize` asset
   chain (per the existing BIEP v3 ingestion DAG)
5. Emits an OpenTelemetry span tagged with
   `dagster.sensor=ocr_completion, dagster.document_id=<doc-abc>` so
   the trace correlates to the OCR router's span (via shared trace_id)

The sensor MUST fail gracefully if `OCR_WEBHOOK_URL` is unset (returns
a SKIPPED state, not an ERROR).

#### Scenario: the sensor is healthy and emits a new run

```
$ dagster sensor list
ocr_completion_sensor    ACTIVE  last_tick=14s ago  last_run="2026-07-31T12:34:56Z"

# New event arrives:
[dagster-sensor] tick: 1 new event (document_id=doc-abc)
[dagster-sensor] → ocr_extraction/doc-abc  (asset materialised)
[dagster-sensor] → biiep_v3_ireland_lc5_materialize  (downstream triggered)
[langfuse] trace=trace-def → span "dagster.sensor=ocr_completion, document_id=doc-abc"
```

#### Scenario: OCR_WEBHOOK_URL unset → sensor SKIPPED

```
$ OCR_WEBHOOK_URL= dagster sensor list
ocr_completion_sensor    ACTIVE  last_tick=14s ago  state=SKIPPED  reason=OCR_WEBHOOK_URL unset
```

## Why this matters

BIEP v3 ingests 1,146 active items across 8 jurisdictions + 2 scanner
domains. OCR is the chokepoint for the forms-heavy Northern Ireland +
Wales (Welsh-medium) corpora. Today every OCR backend is synchronous
`POST → result` — no convention for downstream pipeline state. This
delta ships the webhook + sensor that closes the loop.