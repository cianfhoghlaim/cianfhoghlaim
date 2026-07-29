# Spec delta: `agent-platform-cluster`

This delta is part of the openspec change
`2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1`. It adds 2
requirements that wire the cross-agent context handoff protocol and
the OCR / VLM routing layer into the 8-stack agent platform cluster.

## ADDED Requirements

### Requirement: Cross-agent context envelope protocol

The system MUST provide a typed context-envelope protocol that any of
the 3 agent surfaces (openclaw + openchamber + hermes) MUST use to hand
context to any other agent surface. The protocol MUST be backed by the
Pydantic v2 model `agents/contracts/context-envelope.py`
(`ContextEnvelope`).

The system MUST provide 3 handler modules — one per surface —
`agents/contracts/openclaw_handler.py`,
`agents/contracts/openchamber_handler.py`,
`agents/contracts/hermes_handler.py`. Each handler MUST implement a
function `receive_envelope(envelope: ContextEnvelope) -> dict[str, Any]`
that unpacks the envelope into the surface's local context.

The protocol MUST be the canonical cross-surface handoff mechanism. No
surface MUST hand context to another via raw HTTP `POST` of an
untyped JSON body.

#### Scenario: openclaw routes a webhook event into hermes

```
# On openclaw (channel fanout):
envelope = ContextEnvelope(
    sender="openclaw",
    recipient="hermes",
    agent_run_id="run_abc123",
    parent_trace_id="trace_def456",
    context_payload={"event": "telegram_message", "from": "@alice",
                     "text": "what's the BIEP v3 status?"},
    mtls_subject="openclaw-telegram-bridge",
)
result = hermes_handler.receive_envelope(envelope)
assert result["status"] == "received"
# hermes now has a RunScope tied to parent_trace_id="trace_def456"
# so any downstream LLM call is correlated to the openclaw webhook
```

#### Scenario: hermes returns a result envelope back to openchamber

```
envelope = ContextEnvelope(
    sender="hermes",
    recipient="openchamber",
    agent_run_id="run_abc123",
    parent_trace_id="trace_def456",
    context_payload={"response": "5 jurisdictions live, 3 deferred",
                     "evidence": ["dagster://asset/biiep_v3_jurisdiction_status"]},
    expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
)
result = openchamber_handler.receive_envelope(envelope)
# openchamber IDE/CLI session now shows the result inline + traces to langfuse
```

### Requirement: OCR / VLM routing layer

The system MUST provide a single OCR / VLM routing layer at
`bonneagar/stacks/ocr-router/` that maps a `requested capability` to
the best-fit backend. The router MUST consult this dispatch matrix:

| Capability | Backend | URL |
|:--|:--|:--|
| `forms` (handwritten + printed forms) | paddleocr | `http://paddleocr:8000/v1` |
| `layout` (dense + sparse layout, tables, sections) | mlx-omni | `http://mlx-omni:10240/v1` |
| `tables+latex` (math, table extraction) | olmocr | `http://olmocr:8003/v1` |
| `doctags` (IBM DocTags format) | docling-serve | `http://docling-serve:5001/v1` |
| `gaelic` / `english` vision (gemma-4 + qwen3-vl) | llama-swap | `http://llama-swap:8080/v1` |
| `tesseract-fallback` (legacy) | dots-ocr | `http://dots-ocr:8001/v1` |

The system MUST keep the router as a separate stack (NOT embed the
routing logic in litellm) so that:

1. litellm's role stays "OpenAI-compatible API gateway"; the OCR router
   is the "OCR / VLM capability gateway".
2. The router is the only place that knows the backend ↔ capability
   mapping, so a new backend (e.g. paddleocr-vl-2) can be added without
   touching litellm.
3. The router exposes the OCR_WEBHOOK_URL convention (see BIEP v3 spec
   delta Requirement "OCR completion webhook").

#### Scenario: a Dagster asset asks for table extraction

```
$ curl -X POST http://ocr-router.cianfhoghlaim.ie/ocr \
    -H "Authorization: Bearer $OCR_ROUTER_API_KEY" \
    -d '{"capability": "tables+latex", "image_url": "s3://lakehouse/lc_chem_2024.pdf"}'
{
  "result_url": "s3://lakehouse/ocr/tables_latex_lc_chem_2024.json",
  "backend_used": "olmocr",
  "model": "olmocr-2-7b-1025",
  "duration_ms": 4128,
  "webhook_delivered": true
}
```

#### Scenario: capability `forms` routes to paddleocr

```
$ curl -X POST http://ocr-router.cianfhoghlaim.ie/ocr \
    -d '{"capability": "forms"}'
[ocr-router] → paddleocr:8000/v1/ocr  (capability match: forms)
[ocr-router] response received in 217ms
{"backend_used": "paddleocr", "model": "pp-ocrv4-multilingual", ...}
```

## Why this matters

Two of the 3 surfaces (openclaw + openchamber) currently have **no
protocol for cross-surface handoff**. The 6 OCR / VLM backends are
individually reachable but the routing decision lives in operator
config files (the `litellm/config.yaml.full.bak`) that are
syntactically broken. This delta ships the handoff protocol +
routing layer that the agent + OCR story needs.