# bunchloch-unsloth-studio Specification

## Purpose
The unsloth Studio bring-up on the bunchloch MacBook (M4 Max, 16.8 GB RAM, CPU/MPS only —
no GPU passthrough in Docker Desktop on macOS). Serves the 12 unsloth GGUF + chat + embedding
+ image-gen + voice models from the central MODEL_REGISTRY, exposed via the Pangolin Custom
provider pattern as `unsloth-local` on the AI Gateway.

## ADDED Requirements

### Requirement: unsloth-serve CPU/MPS deployment on bunchloch
The system SHALL run `unsloth/unsloth:latest` (or compatible) on the bunchloch host with:

- **Image**: `unsloth/unsloth:latest` (overridden via `compose.bunchloch.yaml`)
- **Memory cap**: 8 GB
- **CPU cap**: 8 cores
- **GPU offload**: `LLAMA_ARG_NGL=0` (no Metal passthrough in Docker Desktop on macOS;
  llama-swap:cpu is the existing pattern, mirrored here per the unsloth-serve skill)
- **Context size**: `LLAMA_ARG_CTX_SIZE=32768`
- **Ports**:
  - `:8888` — Studio UI (the Web UI)
  - `:8889` — OpenAI + Anthropic compatible inference API

The deployment SHALL be applied via:
```bash
cd bonneagar/stacks/unsloth-serve && docker compose -f compose.yaml -f compose.bunchloch.yaml up -d
```

#### Scenario: Health gate passes
- **WHEN** `curl http://localhost:8889/v1/models` is called
- **THEN** the response is `200 OK` with a `data` array containing ≥ 1 GGUF model
- **AND** the first entry's `id` is `unsloth/gemma-4-26B-A4B-it-GGUF` (the default load)

#### Scenario: Studio UI loads
- **WHEN** the user opens `http://localhost:8888` in a browser
- **THEN** the Studio UI renders within 5 seconds
- **AND** the loaded GGUF model appears in the model dropdown

### Requirement: 12 unsloth models served
The system SHALL make the following 12 models reachable via the OpenAI-compatible `/v1/chat/completions` endpoint on `:8889`:

| Model | Family | Use case |
|:--|:--|:--|
| `unsloth/gemma-4-26B-A4B-it-GGUF` | vision LLM | syllabus OCR + marking-scheme review |
| `unsloth/Qwen3-VL-8B-Instruct-GGUF` | vision LLM | chart + diagram extraction |
| `unsloth/Qwen3-VL-30B-A3B-Instruct-GGUF` | vision LLM | high-recall OCR |
| `unsloth/Qwen3-VL-4B-Instruct-GGUF` | vision LLM | low-latency OCR |
| `unsloth/gemma-4-12b-it-GGUF` | vision LLM | medium-size backup |
| `unsloth/gemma-4-E4B-it-GGUF` | vision LLM | small/fast |
| `unsloth/gemma-4-E2B-it-GGUF` | vision LLM | tiniest |
| `unsloth/InternVL3-8B-GGUF` | vision LLM | alternate-family benchmark |
| `unsloth/GLM-4.6V-Flash-GGUF` | vision LLM | alternate-family benchmark |
| `unsloth/Llama-3.2-11B-Vision-Instruct-unsloth-bnb-4bit` | vision LLM | Meta family |
| `unsloth/gemma-3-4b-it-GGUF` | vision LLM | legacy |
| `unsloth/DeepSeek-OCR-2` | OCR specialist | high-recall text-only OCR |

#### Scenario: All 12 models load on demand
- **WHEN** the user requests a specific model via `POST /v1/chat/completions` with `model: "unsloth/Qwen3-VL-8B-Instruct-GGUF"`
- **THEN** the server loads the GGUF on demand within 30 seconds
- **AND** subsequent requests for the same model return within 2 seconds (cached)

### Requirement: Exposed as a Pangolin private resource + Custom AI Gateway provider
The unsloth-serve stack SHALL be reachable from any device with the Pangolin client
connected, via the private resource `unsloth.cianfhoghlaim.ie` (Studio UI on `:8888`) and
`unsloth-api.cianfhoghlaim.ie` (inference API on `:8889`). The `:8889` endpoint SHALL
also be registered as the Custom provider `unsloth-local` in the Pangolin AI Gateway so
that calls to `https://ai.cianfhoghlaim.ie/v1/chat/completions` with model
`unsloth/<name>` route to this upstream.

#### Scenario: Studio UI reachable over Pangolin.app tunnel
- **GIVEN** the user has Pangolin.app connected
- **WHEN** the user opens `https://unsloth.cianfhoghlaim.ie` in a browser
- **THEN** the Studio UI loads (after Pocket ID OIDC redirect)
- **AND** the user can chat with the loaded GGUF model

#### Scenario: Inference API reachable over Pangolin.app tunnel
- **WHEN** the user runs `curl -H "Authorization: Bearer none" https://unsloth-api.cianfhoghlaim.ie/v1/models`
- **THEN** the response returns the 12-model catalogue

#### Scenario: AI Gateway routes to unsloth-local
- **WHEN** a caller sends `POST https://ai.cianfhoghlaim.ie/v1/chat/completions` with `model: "unsloth/Qwen3-VL-8B-Instruct-GGUF"`
- **THEN** the gateway forwards the call to `unsloth-local`
- **AND** the response streams back from the unsloth-serve container

### Requirement: 6-file GOLD_STANDARD layout
The `bonneagar/stacks/unsloth-serve/` directory SHALL contain the canonical 6 files:

- `compose.yaml` — base compose (CPU/MPS, ports, env)
- `compose.bunchloch.yaml` — bunchloch CPU/MPS override
- `compose.arm1-oci.yaml` — arm1-oci GPU override (existing, preserved)
- `sidecar.yaml` — Locket sidecar (Infisical secret injection)
- `secrets.env` — template with `UNSLOTH_API_KEY`, `UNSLOTH_MODEL_ID`, `UNSLOTH_OTEL_EXPORTER_OTLP_ENDPOINT`
- `blueprint.yaml` — Pangolin blueprint declaring the 2 private resources (Studio UI + API)
- `pangolin.yaml` — Traefik routing rules

This requirement is already satisfied (the layout existed before this change). Verified.

#### Scenario: stack-doctor passes the GOLD_STANDARD check
- **WHEN** `bun run stack-doctor --strict` is run
- **THEN** the `unsloth-serve` stack reports `0` missing files
- **AND** `0` healthcheck failures
- **AND** `0` blueprint validation failures
