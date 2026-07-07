# Infrastructure Stacks — Add lancedb + logfire + Image Pins Delta

> This file is the change-side delta for
> `2026-07-02-add-lancedb-and-logfire-stacks`. It applies on top
> of the canonical `infrastructure-stacks` spec at
> `../../../../specs/infrastructure-stacks/spec.md` and on top
> of the prior `2026-07-02-bunchloch-stack-bootstrap` delta.

## ADDED Requirements

### Requirement: lancedb + logfire stack bring-up

The system SHALL provide a procedure to bring up the 2
observability + vector-viewer stacks in their correct wave
order: `lancedb` in Wave 1 alongside `lakehouse`, and `logfire`
in Wave 2b after `langfuse` and `mlflow` are healthy.

Both stacks SHALL be brought up via
`./scripts/stack.sh <name> up -d` (the dev-mode direct CLI).
No Locket, Infisical, or live secret round-trip SHALL be
required.

#### Scenario: lancedb Wave 1
- **WHEN** an agent runs `./scripts/stack.sh lancedb up -d`
  after `./scripts/stack.sh lakehouse up -d` has completed
- **THEN** the lancedb container SHALL start using the pinned
  image `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`
- **AND** the viewer SHALL be reachable at
  `http://localhost:8081/` (HTTP 200 on `/`)
- **AND** the viewer SHALL be able to discover the
  lakehouse-lance-namespace REST endpoint at
  `rest://lakehouse-lance-namespace:8182` over the
  `lakehouse_lakehouse` external network (operator-driven
  via the viewer UI; not a service-link check)

#### Scenario: logfire Wave 2b
- **WHEN** an agent runs `./scripts/stack.sh logfire up -d`
  after `langfuse` and `mlflow` are both healthy
- **THEN** the OpenTelemetry Collector SHALL start using the
  pinned image `otel/opentelemetry-collector-contrib:0.104.0`
- **AND** the collector SHALL listen on the OTLP gRPC port
  `:4317` AND the OTLP HTTP port `:4318` (verified via
  `nc -zv localhost 4317` and `nc -zv localhost 4318`)
- **AND** if `LOGFIRE_TOKEN` is set, the collector SHALL
  forward OTLP traces to `logfire.pydantic.dev` (the SaaS
  endpoint, per `agent-observability` §"Logfire Stack
  Self-Hosted Compose" — Pydantic Logfire is SaaS-only)
- **AND** the `langfuse` web + worker services SHALL be able
  to add the OTel collector as a secondary OTLP exporter
  (so the unified_tracer fans out to 3 destinations per
  `agent-observability` §"LLM Observability Tri-Split")

### Requirement: Image Pinning Policy applied to 6 stacks

The system SHALL pin the cognee + 4 OCR + lancedb (s3 mounter)
images to their resolved semver tags. The `bun run validate-stacks`
Image Pinning Policy gate SHALL report zero `:latest` WARNINGs
for these 6 stacks.

The 6 pinned images are:

| Stack | Image | Resolved semver | Source |
|:--|:--|:--|:--|
| `cognee` | `cognee/cognee:1.2.2` | Docker Hub stable `1.2.2` (released 2026-06-26) |
| `olmocr` | `alleninstituteforai/olmocr:0.4.27` | Docker Hub stable `0.4.27` (released 2026-03-12); **the previous `allenai/olmocr` path was wrong** — that image does NOT exist on Docker Hub; the correct upstream namespace is `alleninstituteforai/olmocr` |
| `paddleocr` | `paddlecloud/paddleocr:2.6-cpu-latest` | Docker Hub `2.6-cpu-latest` (released 2023; use `2.6-gpu-cuda*-latest` for GPU hosts) |
| `docling-serve` | `ghcr.io/ds4sd/docling-serve:v0.4.0` | GHCR stable `v0.4.0` (most recent stable; previous was `v0.3.0`) |
| `lancedb` (s3 mounter) | `rclone/rclone:v1.74-stable` | Docker Hub `v1.74-stable` channel (matches upstream GitHub `v1.74.3`; rclone does not auto-tag GitHub semvers to Docker Hub) |

#### Scenario: All 6 stacks pinned (5 actually pinned in this change)
- **WHEN** `bun run validate-stacks` runs against the 5 pinned
  stacks (cognee + olmocr + paddleocr + docling-serve + lancedb)
- **THEN** the validator SHALL report zero `:latest` WARNINGs
  for these 5 stacks
- **AND** the `image:` line in each compose.yaml SHALL end with
  a semver tag (not `:latest`)

#### Scenario: dots-ocr remains pinned to `:latest` (deferred)
- **WHEN** `bun run validate-stacks` runs against the `dots-ocr`
  stack
- **THEN** the validator SHALL report a `:latest` WARNING for
  the `dots-ocr/dots-ocr:latest` image line
- **AND** the dots-ocr compose SHALL fail on `docker compose up`
  because no such image exists on Docker Hub; the canonical
  upstream project (`rednote-hilab/dots.ocr`) ships source-only
  and must be built locally
- **AND** the fix is deferred to a separate
  `2026-07-XX-bring-dots-ocr-up-to-spec` change