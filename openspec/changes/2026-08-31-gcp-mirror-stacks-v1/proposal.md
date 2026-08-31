# Change: GCP Mirror Stacks v1 — 6 New bonneagar/stacks/gcp-*

> **Status:** AUTHORED, ready for execution.
>
> **Phase 3 of 6** in the v5 refactor umbrella.
>
> **Anchor:** the gemini_hackathon GCP-first IaC refactor
> (`openspec/changes/2026-08-30-gcp-first-iac-refactor-v1/`) +
> the Stackdriver AI Agent ADK instrumentation pattern.
>
> **Scope:** 6 new stacks at `bonneagar/stacks/gcp-*/` — each follows
> the 6-file GOLD_STANDARD pattern (compose.yaml + sidecar.yaml +
> secrets.env + pangolin.yaml + blueprint.yaml + .env.example).
> The opensource stack (pangolin + komodo + bunchloch) stays canonical
> for local dev. GCP becomes an opt-in alternate target via
> `deployment-choice.yaml`.

## Why

The `gemini_hackathon` repo implemented a GCP-native Cloud Run +
Terraform + Cloud Build + Google Secret Manager + Workload Identity
Federation substrate over 2026-08-30 — replacing the Komodo +
Pangolin + Locket + Infisical IaC mesh (the previous self-hosted
free-tier stack).

For cianfhoghlaim, the opensource stack (pangolin + komodo +
bunchloch + lakehouse + garage + infisical + locket) stays canonical
because it:

1. Runs on bunchloch (the Mac Studio M4 Max) + arm1-oci (the Oracle
   Cloud free-tier ARM instance) — no GCP billing required.
2. Provides zero-trust access via Pangolin + Olm (the WireGuard
   mesh) — already deployed.
3. Hosts the 89 existing Docker Compose stacks that cianfhoghlaim
   + its 5 sister repos depend on.

But the gemini_hackathon lessons are valuable:

1. The Google API stack (Vertex AI Gemini 3.5 + AI Studio + Cloud
   Run + Secret Manager + Workload Identity Federation) is a
   well-documented GCP-first pattern that sister repos can opt
   into.
2. The Stackdriver AI Agent ADK instrumentation (the OTLP exporter
   to the unified Telemetry API) is the canonical ADK 2 observability
   surface.
3. The Document AI OCR ensemble path is a high-quality GCP-native
   document processor.
4. The Lakehouse Lance namespace + BigLake Iceberg REST pattern is
   the prod path for the BIEP warehouse.

This change mirrors these as opt-in GCP stacks — without removing
the opensource substrate.

## What changes

### §1 — 6 new stacks at `bonneagar/stacks/gcp-*/`

Each stack gets the 6-file GOLD_STANDARD pattern. Each is enabled
in `deployment-choice.yaml` as `false` by default (opt-in).

| Stack | Path | Mirrors gemini_hackathon | Opensource counterpart |
|---|---|---|---|
| `gcp-gemini-vertex` | `bonneagar/stacks/gcp-gemini-vertex/` | `cloud/terraform/modules/cloudrun_service/` (Vertex AI Express mode for Gemini 3.5 Flash) | `unsloth-studio` Gemma 4 fallback |
| `gcp-gemma-unsloth` | `bonneagar/stacks/gcp-gemma-unsloth/` | the Unsloth Studio tier on GCE (host.docker.internal:8888 replacement) | `unsloth-studio` (host process) |
| `gcp-bigquery-mirror` | `bonneagar/stacks/gcp-bigquery-mirror/` | `cloud/terraform/modules/bigquery_dataset/` + BigLake Iceberg REST | `motherduck` + `lakehouse` (Postgres + LanceDB + Lakekeeper) |
| `gcp-gcs-bucket` | `bonneagar/stacks/gcp-gcs-bucket/` | `cloud/terraform/modules/gcs_bucket/` | `garage` (S3-compatible already deployed) |
| `gcp-secret-manager` | `bonneagar/stacks/gcp-secret-manager/` | `cloud/terraform/modules/cloudrun_secret_mount/` + GSM catalogue | `infra/stacks/locket-shim/` + `infra/stacks/infisical/` |
| `gcp-cloud-run` | `bonneagar/stacks/gcp-cloud-run/` | `cloud/terraform/modules/cloudrun_service/` | `komodo` orchestrator daemon |

### §2 — `deployment-choice.yaml` enables the 6 new stacks as `false`

```yaml
enabled_stacks:
  gcp-gemini-vertex: false
  gcp-gemma-unsloth: false
  gcp-bigquery-mirror: false
  gcp-gcs-bucket: false
  gcp-secret-manager: false
  gcp-cloud-run: false
```

### §3 — `mise.toml` adds `stack:gcp-*` tasks

```toml
[tasks."stack:gcp-gemini-vertex"]
description = "Deploy the GCP Gemini Vertex mirror stack (opt-in)"
depends = ["sync"]
run = "komodo deploy --stack=gcp-gemini-vertex"
```

(etc. for the other 5)

### §4 — `openspec/specs/infrastructure-stacks/spec.md` delta

- `GCP_MIRROR_STACKS` ADDED Requirement — the 6 new stacks MUST
  follow the 6-file GOLD_STANDARD pattern + be enabled via
  `deployment-choice.yaml`.
- 6 new Scenarios — one per stack, verifying the 6 files exist +
  pangolin labels + GCP service-account wiring.

## Impact

- 6 new directories at `bonneagar/stacks/gcp-*/` (36 new files total
  — 6 files × 6 stacks).
- 1 update to `deployment-choice.yaml` (6 new keys).
- 1 update to `mise.toml` (6 new `stack:gcp-*` tasks).
- 1 update to `openspec/specs/infrastructure-stacks/spec.md` (1 new
  ADDED Requirement + 6 new Scenarios).
- 0 breaking changes — the 6 stacks are opt-in.

## Dependencies

- `openspec/specs/infrastructure-stacks/spec.md` (already exists).
- The opensource stacks remain canonical (pangolin + komodo + bunchloch).
- The `gemini_hackathon/cloud/terraform/` modules (referenced as the
  GCP pattern but not vendored — this change documents the pattern,
  not the Terraform code itself).

## Out of scope

- Terraform code generation (the 6 stacks document the
  `cloud_run.tf` + `gcs_bucket.tf` + `secret_manager.tf` patterns but
  don't ship Terraform modules; that's a follow-on change).
- Komodo replacement (the opensource Komodo orchestrator daemon stays).
- Pangolin removal (Pangolin stays — it provides zero-trust access).

## Quality gates (must pass before archive)

```bash
mise run openspec:validate 2026-08-31-gcp-mirror-stacks-v1 --strict
mise run lint:skills               # 66 skills pass
mise run sync:all                  # 14 sync layers green
mise run stacks:audit              # 105 + 6 stacks validated
```

---

*Last updated by build subagent at 2026-08-31.*