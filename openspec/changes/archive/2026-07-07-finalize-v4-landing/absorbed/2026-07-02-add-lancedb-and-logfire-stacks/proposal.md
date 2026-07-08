# Change: 2026-07-02-add-lancedb-and-logfire-stacks

## Why

The sibling change `2026-07-02-bunchloch-stack-bootstrap` brought
the 19 foundational workload-host stacks up on `bunchloch`, but
3 active specs were left partially-served:

1. **`agent-observability` §"LLM Observability Tri-Split"** explicitly
   requires **Langfuse + MLflow + Logfire**. Change 1 ships the
   first two; this change ships the third (`logfire`).

2. **`oideachais-pipeline`** + **`oideachais-cocoindex-v1-migration`**
   + **`oideachais-semantic-search`** + **`agent-platform-cluster`**
   all reference the **standalone LanceDB viewer stack** at
   `127.0.0.1:8081` for browsing the `codebase_chunks`,
   `unified_embeddings`, and `leabharlann_books` tables. The
   storage layer is already provided by `lakehouse-lance-namespace`
   in Change 1; this change ships the viewer UI.

3. **`infrastructure-stacks` §"Image Pinning Policy"** requires
   every `image:` line to declare a specific semver tag (no
   `:latest`). At the time of Change 1, 5 stacks still violated
   this rule and emitted WARNINGs from stack-doctor.

This change ships those 3 missing pieces in one bundle because
they all share the same Wave-1/Wave-2 dependency graph and all
touch the `infrastructure-stacks` umbrella spec.

## What changes

### 2 new stack bring-ups (no compose edits)

- `lancedb` (Wave 1) — already GOLD_STANDARD-compliant (all 6
  core files present). Image already pinned
  (`ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3`). The
  optional `rclone/rclone:latest` sidecar in the `s3` profile is
  pinned to `rclone/rclone:v1.74-stable` (Docker Hub's most
  recent stable channel — the upstream GitHub semver is
  `v1.74.3` but Docker Hub only auto-tags `v1.74-stable` /
  `latest` / `beta` / `master`).

- `logfire` (Wave 2b) — already GOLD_STANDARD-compliant (all 6
  core files present). Image already pinned
  (`otel/opentelemetry-collector-contrib:0.104.0`). Per
  `agent-observability` §"Logfire Stack Self-Hosted Compose",
  Pydantic Logfire is SaaS-only (no self-hostable Docker image
  exists); the local service is an OpenTelemetry Collector
  that forwards OTLP traces to `logfire.pydantic.dev`.

### 5 image pins (resolved at first pull, then committed)

| Stack | Was | Now | Source verified |
|:--|:--|:--|:--|
| `cognee` | `cognee/cognee:latest` | `cognee/cognee:1.2.2` | Docker Hub `1.2.2` (released 2026-06-26) |
| `olmocr` | `allenai/olmocr:latest` | `alleninstituteforai/olmocr:0.4.27` | **Registry path was wrong** — `allenai/olmocr` does NOT exist on Docker Hub; the correct upstream namespace is `alleninstituteforai/olmocr`. Latest stable `0.4.27` (released 2026-03-12) |
| `paddleocr` | `paddlecloud/paddleocr:latest` | `paddlecloud/paddleocr:2.6-cpu-latest` | Docker Hub `2.6-cpu-latest` is the latest stable CPU tag (released 2023; no newer stable published). For GPU hosts use `2.6-gpu-cuda10.2-cudnn7-latest` or `2.6-gpu-cuda11.2-cudnn8-latest` |
| `docling-serve` | `ghcr.io/ds4sd/docling-serve:latest` | `ghcr.io/ds4sd/docling-serve:v0.4.0` | GHCR `v0.4.0` (most recent stable; previous was `v0.3.0`) |
| `lancedb` (s3 mounter) | `rclone/rclone:latest` | `rclone/rclone:v1.74-stable` | Docker Hub `v1.74-stable` (matches upstream GitHub `v1.74.3`); rclone does not auto-tag GitHub semvers to Docker Hub |

### 0 new spec definitions

The 2 new stacks are covered by the existing
`infrastructure-stacks` umbrella spec (already has the
GOLD_STANDARD + Image Pinning + 3-tier host convergence rules)
and `agent-observability` (already has the Logfire
Self-Hosted Compose rule + the Tri-Split rule).

The change adds **2 ADDED Requirements** to
`infrastructure-stacks` and **1 ADDED Requirement** to
`agent-observability`.

## Impact

- **Affected specs:** `infrastructure-stacks` (shared),
  `agent-observability` (shared)
- **Affected code:** 5 `compose.yaml` files (single-line image
  pin edits with `# pinned 2026-07-02 (was :latest; <reason>)`
  comment) + 4 new openspec change files
- **Affected hosts:** `bunchloch` only (the workload host)
- **Risk:** medium — the olmocr registry-path fix is a structural
  change (not just a tag bump); if the upstream
  `alleninstituteforai/olmocr` image is incompatible with the
  stack's compose assumptions (env vars, healthcheck endpoint,
  port), Wave 2b bring-up will fail and the operator must roll
  back via `./scripts/stack.sh olmocr down`
- **Audit gates:** `bun run validate-stacks` (zero `:latest`
  WARNINGs for the 6 affected stacks post-pin) + `mise run
  lint:skills` (regression) + `openspec validate --strict`
  (change gate)

## Non-goals

- **Not fixing `dots-ocr`.** The compose file at
  `bonneagar/stacks/dots-ocr/compose.yaml` line 4 references
  `dots-ocr/dots-ocr:latest` — **no such image exists on Docker
  Hub**. The canonical upstream project is
  [`rednote-hilab/dots.ocr`](https://github.com/rednote-hilab/dots.ocr)
  which ships **source-only** (with a `docker/Dockerfile` you
  build locally) and is **NOT** published to any container
  registry. Fixing this requires a structural rewrite of the
  dots-ocr stack (clone the repo, build the image locally,
  reference it as `image: dots-ocr:local` with `build:` context
  + `pull_policy: never`). Deferred to a separate
  `2026-07-XX-bring-dots-ocr-up-to-spec` change. The dots-ocr
  service WILL fail on `docker compose up` until that change
  lands; this is documented as a known issue.
- **Not addressing any of the other `:latest` images** in the
  86-stack catalogue (the `agent-observability` spec's
  `compose.litellm` Prometheus removal is already done; the
  remaining unpinned images in other stacks are tracked under
  the in-flight v5-drift change's image pinning milestone).
- **Not bringing the 2 new stacks up on `arm1-oci`.** They are
  workload-tier per the 3-tier host convergence model and belong
  on `bunchloch` (the MacBook M4 Max). The `lancedb` viewer is
  resource-light (~1 GB RAM, 1 CPU) and the `logfire` OTel
  collector is even lighter (~200 MB RAM, 0.5 CPU).
- **Not producing Locket/Infisical integration** for the 2 new
  stacks; both use their existing `secrets.env` defaults.
- **Not migrating the Logfire SaaS token.** The `logfire`
  compose uses an env-driven `LOGFIRE_TOKEN`; this change does
  not add or rotate any Infisical entries. A follow-up change
  could add a `infisical://dev-baile/logfire/token` reference
  once the operator generates a Logfire SaaS project token.

## Spec delta

- `infrastructure-stacks/spec.md` — 2 ADDED Requirements
- `agent-observability/spec.md` — 1 ADDED Requirement

See `specs/<capability>/spec.md` for the full delta.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Build dots-ocr image locally from upstream Dockerfile | `2026-07-XX-bring-dots-ocr-up-to-spec` (deferred) |
| Bring browser stack to GOLD_STANDARD | `2026-07-XX-bring-browser-stack-to-gold-standard` (deferred) |
| Add Infisical `logfire/token` entry | `2026-07-XX-wire-logfire-saas-token` (deferred) |
| Pin remaining `:latest` images in the 86-stack catalogue | consumed by the v5-drift change's image pinning milestone |