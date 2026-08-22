# 2026-08-22-litellm-1.91-to-1.97-image-bump-v1

## Summary

Implementation sibling of the archived `2026-08-21-2026-08-21-litellm-1.91-to-1.97-and-mcp-oauth-2.0-v1/` proposal. Bumps the LiteLLM gateway from `v1.91.0` to `v1.97.0` + adopts the v1.95.0 Rust `/v1/messages` endpoint + the v1.85.0 MCP Gateway GA + the v1.91.0 OAuth 2.0 v2 resolver.

## Why

- The audit (`stedding/audit/2026-08-21-upstream-audit.md`) flagged LiteLLM as Priority 2. The local image is 7 minor versions behind.
- LiteLLM 1.85+ shipped the MCP Gateway GA (replaces our hand-rolled MCP support in hermes/openclaw).
- LiteLLM 1.95+ shipped the Rust `/v1/messages` endpoint (5x faster than the Python one — relevant for the 12-agent fleet's high-throughput agent loops).
- LiteLLM 1.91+ shipped OAuth 2.0 v2 resolver + DCR (Hermes can drop its custom auth code).
- LiteLLM 1.97+ shipped tool-result guardrails (output-side safety filters).
- The umbrella change (`2026-08-21-upstream-version-alignment-and-pin-resolution-v1`) already authorised this bump.

## What changes

- `pyproject.toml`: `litellm>=1.97,<1.98`.
- `bonnegar/stacks/litellm/compose.yaml`: `ghcr.io/berriai/litellm-database:v1.91.0` → `:v1.97.0`.
- `bonnegar/stacks/litellm/pangolin.yaml`: expose `/v1/messages` (Rust v1.95.0 endpoint).
- `bonnegar/stacks/litellm/config/config.yaml`: regenerate via `mise run ml:litellm:regenerate` (the canonical model-registry → litellm-config sync).

## Test plan

1. `uv sync` resolves cleanly with `litellm>=1.97,<1.98`.
2. `docker compose -f bonnegar/stacks/litellm/compose.yaml -f bonnegar/stacks/litellm/sidecar.yaml --env-file .env pull` downloads the v1.97.0 image.
3. Restart litellm.
4. `curl http://localhost:4000/v1/models` returns the regenerated model list.
5. `curl http://localhost:4000/v1/messages -X POST` (or via langfuse) successfully routes through the Rust endpoint.
6. The 12-agent fleet still connects + emits traces successfully.

## Rollback

- Revert `pyproject.toml` to `litellm>=1.91,<1.98`.
- Revert the compose image tag to `v1.91.0`.
- Revert the pangolin path addition.
- `uv sync` re-resolves.
- `docker compose down && docker compose up -d` (the v1.91.0 image is still pinned in GHCR).
