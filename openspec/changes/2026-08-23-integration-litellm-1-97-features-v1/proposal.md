# 2026-08-23 — Adopt LiteLLM v1.97 features (2 new tasks)

## Why

LiteLLM v1.97 (Aug 2026) introduced:

- **MCP Gateway GA**: pass `mcp_servers` to the router; LiteLLM routes
  MCP requests to the right backend
- **OAuth 2.0 v2**: dynamic client registration + DCR support (replaces
  the v1 static flow)
- **Rust-based /v1/messages endpoint**: 3-5× faster than the Python
  implementation

The previous round (`a9541d53b feat(litellm): upgrade 1.91.0 → 1.97.0`)
did the actual bump + added 2 MCP-related config keys. This change
adds the **task surface** for using these features.

## What changes

### 2 new mise tasks in `mise.toml`

| Task | What it does |
|:--|:--|
| `data:litellm:mcp:gateway` | `litellm --enable_mcp_gateway` — boots the MCP Gateway daemon + shows the routes for all configured MCP servers |
| `data:litellm:oauth:v2` | `litellm --oauth2-v2` — enables OAuth 2.0 v2 (DCR) + shows the dynamic client registration endpoint |

### 1 doc update

`.agents/skills/litellm/SKILL.md`: add a "LiteLLM v1.97+ new features"
section documenting MCP Gateway GA + OAuth 2.0 v2 + the Rust
`/v1/messages` endpoint.

## Dependencies

- **Blocked by:** none
- **Soft-blocked by:** the `a9541d53b feat(litellm): upgrade 1.91.0 → 1.97.0` commit
- **Affected repos:** cianfhoghlaim only

## Acceptance criteria

1. Both new tasks exist in `mise.toml`
2. `data:litellm:mcp:gateway` runs the gateway daemon
3. `data:litellm:oauth:v2` enables OAuth 2.0 v2
4. `.agents/skills/litellm/SKILL.md` includes the new section
5. `openspec validate 2026-08-23-integration-litellm-1-97-features-v1 --strict` exits 0