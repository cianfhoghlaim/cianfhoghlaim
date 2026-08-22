# 2026-08-21-litellm-1.91-to-1.97-and-mcp-oauth-2.0-v1

## Summary

Upgrade the LiteLLM gateway from `v1.91.0` → `v1.97.0` and adopt the MCP OAuth 2.0 v2 resolver + MCP DCR (Dynamic Client Registration) endpoints. The Hermes multi-channel gateway, OpenClaw channel fanout, and the BIEP 12-agent fleet benefit from the v1.95.0 Rust-based `/v1/messages` endpoint and the OAuth 2.0 v2 drop (Hermes no longer needs its custom auth code).

## Why

Per the upstream-version audit (`stedding/audit/2026-08-21-upstream-audit.md`), the bunchloch LiteLLM stack is 7 minor versions behind. The audit flagged LiteLLM as "Critical for CVE-2026-42271" — the running v1.91 is past the CVE fix (v1.83.7+) but misses:
- MCP Gateway GA (v1.85)
- OAuth 2.0 v2 (v1.91)
- DCR (v1.95)
- Rust `/v1/messages` (v1.95)
- Tool-result guardrails (v1.97)

The hermes stack at `agents/meaisinfhoghlaim/hermes/` has custom auth code that v1.91's OAuth 2.0 v2 would replace.

## What changes

- `pyproject.toml`: bump `litellm>=1.91,<1.98` → `litellm>=1.97,<1.98`.
- `bonneagar/stacks/litellm/compose.yaml`: bump `ghcr.io/berriai/litellm-database:v1.91.0` → `:v1.97.0`.
- `bonneagar/stacks/litellm/config/config.yaml`: regenerate via `mise run ml:litellm:regenerate` (reads MODEL_REGISTRY).
- `bonneagar/stacks/litellm/pangolin.yaml`: add `/v1/messages` reverse-proxy path.
- `agents/meaisinfhoghlaim/hermes/`: drop the custom OAuth code (v1.91's v2 handles it).
- `agents/meaisinfhoghlaim/agents/`: any @observe-decorated trace that used the `--auth v1` flag switches to `--auth v2`.

### New MODIFIED specs under `openspec/specs/`

| Spec | Change |
|:--|:--|
| `agent-observability` | MODIFIED — LiteLLM v1.97 routing tier adds MCP Gateway GA endpoint + OAuth 2.0 v2 resolver + DCR |

### Migration steps

1. Bump `litellm` pin in `pyproject.toml`.
2. Bump the LiteLLM Docker image in `bonneagar/stacks/litellm/compose.yaml`.
3. Re-run `mise run ml:litellm:regenerate` to refresh `config.yaml` from the centralized MODEL_REGISTRY.
4. Add the `/v1/messages` reverse-proxy path to `bonneagar/stacks/litellm/pangolin.yaml`.
5. (Optional) Migrate `agents/meaisinfhoghlaim/hermes/` to use the v2 OAuth flow.

## Test plan

1. `uv sync` succeeds without pinning conflicts.
2. LiteLLM image pulls + boots.
3. `curl -s http://localhost:4000/v1/models` returns the regenerated model list.
4. The 12-agent fleet connects via `http://litellm.cianfhoghlaim.ie/v1/chat/completions` and emits a trace → visible in Langfuse v4.
5. The MCP Gateway endpoint `/v1/mcp` is reachable + accepts OAuth 2.0 requests.

## Rollback

- Revert `pyproject.toml` + the compose file to v1.91.0.
- `docker compose down && docker compose up -d` restores the v1.91 image (already pinned in GHCR).
