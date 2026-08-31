# gcp-cloud-run — GCP mirror stack

> **Phase 3** of the Cianfhoghlaim v5 refactor umbrella.
>
> Mirrors the GCP-first IaC pattern from the gemini_hackathon repo.
>
> **Opensource counterpart:** stays canonical for local dev on bunchloch.

## What this stack provides

See `openspec/changes/2026-08-31-gcp-mirror-stacks-v1/proposal.md`
for the full GCP mirror description.

## Deployment

```bash
docker compose up -d           # Local dev
mise run stack:gcp-cloud-run             # GCP deploy via Komodo
```

## Files

- `compose.yaml` — Base compose file
- `sidecar.yaml` — Locket shim (Infisical provider)
- `secrets.env` — Locket template (Google Cloud service-account URI + API keys)
- `pangolin.yaml` — Pangolin labels (private resource)
- `blueprint.yaml` — Pangolin routing blueprint
- `.env.example` — Non-secret defaults for local dev
