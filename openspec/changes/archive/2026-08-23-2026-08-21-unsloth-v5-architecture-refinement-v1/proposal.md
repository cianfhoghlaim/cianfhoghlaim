# Unsloth v5 Architecture Refinement — direct host + Pangolin private resource

## Why

The original `2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` change introduced a separate `unsloth-serve` Docker container. That container **could not start in practice** — the upstream `unsloth` Python CLI requires a `~/.unsloth/` host setup that doesn't exist inside a Docker container, and the upstream `unsloth/unsloth` Docker image is x86_64-only (bunchloch is arm64 / M4 Max).

This follow-up change **removes the container entirely** and instead wires the Unsloth Studio (which is installed and running on the bunchloch host) into the existing Bonneagar topology. The pattern matches how hermes, openclaw, and marimo already work — service runs on the host (or in a container), Pangolin exposes it via a private resource, Newt bridges the gap.

## What changes

### Removed

- `bonneagar/stacks/unsloth-serve/` — entire stack directory (8 files: compose.yaml + 2 compose overrides + 2 Dockerfiles + caddyfile + secrets.env + blueprint.yaml). The container was dead (restart loop with exit code1) and the architecture is anti-pattern (two copies of llama-server competing for the same GPU).
- `bonneagar/komodo/stacks/unsloth-serve-bunchloch.toml` — Komodo stack TOML (host entry)
- `bonneagar/komodo/stacks/unsloth-serve-arm1-oci.toml` — Komodo stack TOML (arm1-oci entry)
- `bonneagar/komodo/procedures/deploy-unsloth-serve-bunchloch.toml` — Komodo procedure
- `bonneagar/komodo/procedures/deploy-unsloth-serve-arm1-oci.toml` — Komodo procedure
- `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch}.toml` — references to the above files removed

### Added

- `bonneagar/stacks/unsloth/` — **Pangolin-only** stack directory. No Docker compose, no deployment. Just the Traefik routing rules + blueprint for the Pangolin private resource.
  - `pangolin.yaml` — Traefik HTTP routers + services that route `unsloth.cianfhoghlaim.ie` and `unsloth-api.cianfhoghlaim.ie` → `http://bunchloch:8888` (the Unsloth Studio on the host, reached via the Newt WireGuard tunnel)
  - `blueprint.yaml` — Generated from `pangolin.yaml` for use with the Pangolin Blueprint API
  - `README.md` — Documents the new architecture
- `bonneagar/pangolin/private-resources.blueprint.yaml` — Appended 2 new resources (`unsloth`, `unsloth-api`)

### Updated

- `bonneagar/stacks/litellm/config/config.yaml`:
  - 20 new unsloth routes (across all 7 model families) all pointing at `http://host.docker.internal:8888/v1`
  - 1 public-URL alias block pointing at `https://unsloth.cianfhoghlaim.ie/v1` (for external agents + arm1-oci deployments)
  - The existing `local/vision/unsloth/*` routes continue to use `http://transformers:5000/v1` (the M3 chokepoint transformers backend; unchanged)
  - The `vision` alias flipped to `local/unsloth/qwen3-vl-8b-instruct` as the primary
- `bonneagar/stacks/hermes/secrets.env`:
  - `UNSLOTH_API_KEY=sk-unsloth-dev-local-only-replace-in-prod` (was `infisical://dev-baile/unsloth/api_key` which requires Locket)
  - `UNSLOTH_BASE_URL=http://host.docker.internal:8888/v1` (was `http://unsloth:8889/v1`)
  - Added `UNSLOTH_PUBLIC_URL=https://unsloth.cianfhoghlaim.ie/v1` for production
- `bonneagar/stacks/hermes/compose.yaml`:
  - `UNSLOTH_BASE_URL` reads from env var (default: `http://host.docker.internal:8888/v1`)
- `bonneagar/stacks/openclaw/config/openclaw.json`:
  - `fallback_chain` block: `baseUrl: http://host.docker.internal:8888` (was `http://unsloth:8889`)
  - Notes updated to reference the new architecture
- `opencode.json`:
  - `unsloth-studio` provider: `baseURL: http://host.docker.internal:8888/v1/` (was `http://unsloth:8889/v1/`)
  - Description updated

## URLs (final)

| Audience | URL |
|:--|:--|
| External (internet) | `https://unsloth.cianfhoghlaim.ie/v1/...` (via Pangolin) |
| External (API only) | `https://unsloth-api.cianfhoghlaim.ie/v1/...` (via Pangolin) |
| Internal (Docker on bunchloch) | `http://host.docker.internal:8888/v1/...` (direct host) |
| Local (host) | `http://127.0.0.1:8888/` (Studio UI) |

## Verification (7-step protocol, all 7 steps must pass live)

1. `curl -fs http://localhost:8888/api/auth/status` → 200 + `{"initialized":true,...}`
2. `curl -fs -H "Authorization: Bearer sk-..." http://localhost:8888/api/inference/status` → 200 + empty model fields
3. `curl -fs -H "Authorization: Bearer sk-..." http://localhost:8888/api/inference/llama-flags | jq '.flags | keys | length'` → 100+
4. `curl -fs -X POST -H "Authorization: Bearer sk-..." http://localhost:8888/v1/chat/completions -d '{...}'` → 400 "No model loaded"
5. `curl -fs -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/models | jq '.data[] | select(.id | startswith("local/unsloth/")) | .id' | wc -l` → 18 (or 19 with `public/unsloth/*`)
6. `curl -fs -X POST -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/chat/completions -d '{"model":"local/unsloth/qwen3.8-27b",...}'` → 400 (proves litellm → host.docker.internal:8888 → Studio path works)
7. `mise run notebook:unsloth-compare` + 4 backends + 1 PDF → renders side-by-side

## Dependencies

`Blocked by: none` (no prior changes required — the Unsloth Studio is already installed on the host)

`Blocked by (soft): 2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1` (already archived — this change replaces its stack-with-container architecture with the direct-host pattern)

`Affected repos: cianfhoghlaim` (single-repo; Pangolin + Infisical are separate projects on arm1-oci)

## Cost

- **Compute:** 0 — Unsloth Studio runs on the existing bunchloch M4 Max
- **API tokens:** Saves up to ~80% of M3 plan spend during heavy agent sessions (same as the original change)
- **Storage:** 0 — GGUF models continue to live in `~/.unsloth/.cache/` on the host
- **Infisical:** No new secrets required (UNSLOTH_API_KEY hardcoded in dev `.env`; Locket-mounted in prod once Infisical is online)