# gcp-gemini-vertex — GCP Vertex AI Gemini 3.5 Flash mirror stack

> **Phase 3** of the Cianfhoghlaim v5 refactor umbrella.
>
> Mirrors the `cloud/terraform/modules/cloudrun_service/` pattern from
> the gemini_hackathon GCP-first IaC refactor (`2026-08-30-gcp-first-iac-refactor-v1`)
> as a Docker Compose stack that runs locally + on bunchloch.
>
> **Opensource counterpart:** `unsloth-studio` Gemma 4 (stays canonical
> for local dev).

## What this stack provides

- **Vertex AI Express** mode for Gemini 3.5 Flash (the Tier 1 Google
  fallback in the v5 model priority change).
- **AI Studio** fallback for when Vertex credentials are missing.
- **Stackdriver AI Agent ADK instrumentation** — the OTLP exporter
  to the unified Telemetry API.
- **Workload Identity Federation** — no JSON keys needed in the
  container; the service account is bound at the GCP project level.

## What this stack does NOT do

- Replace the opensource `unsloth-studio` Gemma 4 path (that stays
  canonical for local dev on bunchloch).
- Replace the BIEP text-extraction chokepoint (which still routes
  through `minimax-m3` via `BIEPV3Extract`).

## Deployment

```bash
# Local dev (via the opensource stack)
docker compose up -d

# GCP deploy (via Komodo)
mise run stack:gcp-gemini-vertex
```

## Files

| File | Purpose |
|---|---|
| `compose.yaml` | Base compose file (Vertex AI client + OTLP exporter) |
| `sidecar.yaml` | Locket shim (infisical provider for secrets) |
| `secrets.env` | Locket template (Google Cloud service-account URI + API key) |
| `pangolin.yaml` | Pangolin labels (private resource — Vertex AI client is internal) |
| `blueprint.yaml` | Pangolin routing blueprint |
| `.env.example` | Non-secret defaults for local development |

## See also

- `openspec/changes/2026-08-31-gcp-mirror-stacks-v1/proposal.md`
- `openspec/changes/2026-08-31-cianfhoghlaim-v5-opencode-model-priority-v1/proposal.md`
- `gemini_hackathon/cloud/terraform/modules/cloudrun_service/`
- `gemini_hackathon/cloud/terraform/cloud_run.tf`