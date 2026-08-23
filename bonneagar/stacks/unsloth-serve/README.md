# Unsloth Studio Integration

## Architecture

The Unsloth Studio runs **directly on the host** (bunchloch, the MacBook M4 Max) at
`127.0.0.1:8888`. The Docker stack directory is intentionally minimal — Unsloth is a
**host process**, not a Docker container.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ INTERNET (Pangolin Enterprise Edition on arm1-oci)                      │
│                                                                          │
│   https://unsloth.cianfhoghlaim.ie/v1/chat/completions                  │
│         │                                                                │
│         ▼                                                                │
│   Pangolin private resource target:                                      │
│   http://host.docker.internal:8888                                       │
│         │ (via Newt WireGuard tunnel from bunchloch)                     │
│         ▼                                                                │
└──────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ BUNCHLOCH (MacBook M4 Max)                                               │
│                                                                          │
│   Docker containers (cianfhoghlaim network):                             │
│     • litellm    ─────┐                                                   │
│     • hermes     ─────┤                                                   │
│     • openclaw   ─────┼──► host.docker.internal:8888  ──► Studio      │
│     • openchamber ────┤                                                   │
│     • newt (Pangolin client)                                              │
│     • marimo     ─────┘                                                   │
│                                                                          │
│   Unsloth Studio (host, port 8888):                                     │
│     • /v1/chat/completions (OpenAI-compatible)                          │
│     • /v1/messages         (Anthropic-compatible)                       │
│     • llama-server under the hood                                        │
│     • 1 API key: sk-unsloth-...                                         │
└──────────────────────────────────────────────────────────────────────────┘
```

This is **exactly the same pattern as hermes/openclaw/marimo** — service runs
locally on bunchloch, Pangolin on arm1-oci exposes it via a private resource,
Newt bridges them via WireGuard.

## URLs

| Path | URL |
|:--|:--|
| **Public** (external users) | `https://unsloth.cianfhoghlaim.ie/v1/chat/completions` (via Pangolin) |
| **Public** (Anthropic) | `https://unsloth.cianfhoghlaim.ie/v1/messages` |
| **Internal** (Docker on bunchloch) | `http://host.docker.internal:8888/v1/chat/completions` |
| **Local-only** (host machine) | `http://127.0.0.1:8888/` (Studio UI) |

Both the public URL (via Pangolin + Newt tunnel) and the internal URL (direct
Docker → host) reach the same Studio on bunchloch. Single source of truth.

## Litellm integration

The 22 litellm routes for `local/unsloth/*` point at
`http://host.docker.internal:8888/v1` (internal path). The `vision`/`text`/`coding`
aliases fall through to this backend after the M3 chokepoint (Kimi-K2.6 / GLM-5.1 /
minimax-m3). For public URL fallback, see `local/public-unsloth-qwen3.8-27b` which
points at `https://unsloth.cianfhoghlaim.ie/v1` (the Pangolin path).

## API key storage

The Unsloth API key (`sk-unsloth-...`) lives in two places:

1. **Production**: `infisical://dev-baile/unsloth/api_key` (Infisical vault).
   The Locket sidecar in `bonneagar/stacks/litellm/sidecar.yaml` injects it into
   the litellm container's env block at container start.
2. **Local dev**: Hardcoded in `bonneagar/stacks/litellm/.env` as a fallback
   (when Infisical is offline).

The key only has access to the local Studio (loopback). If compromised, the
attacker can only reach the local Studio which is bound to `127.0.0.1:8888`.

## Verification

Run the 7-step verification protocol:

```bash
# Step 1: Studio health
curl -fs http://localhost:8888/api/auth/status

# Step 2: Studio status (empty models)
curl -fs -H "Authorization: Bearer sk-unsloth-..." http://localhost:8888/api/inference/status

# Step 3: Studio flags (100+ entries)
curl -fs -H "Authorization: Bearer sk-unsloth-..." http://localhost:8888/api/inference/llama-flags | jq '.flags | keys | length'

# Step 4: Studio error path (no model loaded)
curl -fs -X POST -H "Authorization: Bearer sk-unsloth-..." http://localhost:8888/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"unsloth/Qwen3.8-27B-GGUF","messages":[{"role":"user","content":"hi"}]}'

# Step 5: Litellm routes (22 unsloth)
curl -fs -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/models \
  | jq '.data[] | select(.id | startswith("local/unsloth/")) | .id' | wc -l

# Step 6: Litellm passthrough (proves litellm → host.docker.internal:8888 → Studio)
curl -fs -X POST -H "Authorization: Bearer $LITELLM_MASTER_KEY" http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"local/unsloth/qwen3.8-27b","messages":[{"role":"user","content":"hi"}],"max_tokens":5}'

# Step 7: Marimo notebook renders
mise run notebook:unsloth-compare
```

## Source

Per the 2026-08-21-unsloth-v5-architecture-refinement-v1 change (the
follow-up to 2026-08-21-unsloth-v5-integration-v1). The original change tried
to run unsloth in a Docker container; this refinement removes the container
and uses Pangolin + Newt + host.docker.internal instead — consistent with the
rest of the Bonneagar stack.

## Related files

- `bonneagar/stacks/litellm/config/config.yaml` — 22 unsloth routes + 1 public alias
- `bonneagar/stacks/hermes/secrets.env` — `UNSLOTH_BASE_URL` env var
- `bonneagar/stacks/openclaw/config/openclaw.json` — `fallback_chain` block
- `opencode.json` — `unsloth-studio` provider block
- `bonneagar/pangolin/agent-fleet.yaml` — `unsloth` private resource
- `openspec/changes/2026-08-21-unsloth-v5-architecture-refinement-v1/` — follow-up change
- `openspec/changes/archive/2026-08-21-2026-08-21-unsloth-v5-vision-llm-hermes-openclaw-opencode-marimo-integration-v1/` — archived original change