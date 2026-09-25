---
name: pangolin-ai-gateway
description: The identity-aware AI Gateway contract from Pangolin (the 2026-Q3 feature). Covers the public + private resource distinction, the overlapping-FQDN pattern, Custom provider registration for non-Anthropic/non-OpenAI upstreams (e.g. unsloth-serve, invokeai, comfyui), per-role + global budget caps, and session-log forwarding to Langfuse/MLflow. Use when the user asks about "the AI gateway", "ai.cianfhoghlaim.ie", "self-hosted LLM proxy", "model routing with budgets", or any task involving forwarding Claude Code / Codex / OpenCode / Gemini CLI calls through one Pangolin-hosted URL.
---

# Pangolin AI Gateway

**Version**: 2026-Q3 launch | **Upstream**: https://pangolin.net/ai-gateway
**Companion skill**: `pangolin-cli` (for the CLI that writes provider entries into
opencode.json / auth.json). The `pangolin` skill covers the older SASE / ZTNA surface.

Pangolin's AI Gateway is an identity-aware LLM proxy. It speaks each upstream
provider's native API format (OpenAI Chat Completions, Anthropic Messages, Gemini
`generateContent`, Vertex, Bedrock, Microsoft Foundry, OpenRouter, Vercel, **Custom**),
attaches them to a Pangolin **resource** of type `AI Gateway`, and exposes the
result on a normal FQDN like `ai.cianfhoghlaim.ie`. The gateway then sits in front
of:

- **Cloud upstreams** (Anthropic, OpenAI, Gemini, Bedrock, etc.)
- **Self-hosted upstreams** (unsloth-serve, invokeai, comfyui, llama-swap, MLX)
- **Tunneled private endpoints** (any local service reachable over a Pangolin site
  tunnel)

## 1. The 2 resource types: public vs private

| | **Public AI Gateway** | **Private AI Gateway** |
|:--|:--|:--|
| **Reachability** | Public FQDN, reachable from anywhere | Only via Pangolin client tunnel |
| **Auth** | Virtual API key on every call (`Bearer vk_<key>`) | Client identity (proved by the active Pangolin.app / CLI tunnel). Key field set to literal `none` |
| **Who can call** | Roles + identities in the Pangolin UI | Users, roles, or machines granted on the resource |
| **When to use** | CI agents, automation, web apps, public-facing agents | Operators + their own dev tools, anything that needs zero API-key handling |

### The overlapping-FQDN pattern

Pangolin lets you create 2 resources on the **same FQDN** (e.g. both public + private
on `ai.cianfhoghlaim.ie`). The gateway picks the right one based on whether the call
arrived over the Pangolin tunnel (private path, no key check) or from the public
internet (public path, virtual key check). This is the recommended pattern for
the cianfhoghlaim dev environment because:

- One URL for humans (`https://ai.cianfhoghlaim.ie`) — no API key required
- Same URL for CI — same workflow, just add a virtual key
- One access policy (per FQDN), per-resource budgets, shared session logs

## 2. Custom providers (the path for self-hosted upstreams)

A **Custom** provider can speak any API format. Per the Pangolin docs, set
`capability = openai` for an OpenAI-compatible upstream:

```yaml
# Custom provider registration (Pangolin UI form data)
name: unsloth-serve-bunchloch
kind: custom
url: http://192.168.148.5:8889/v1       # docker network IP, not localhost
capability: openai                       # it speaks OpenAI Chat Completions
```

Once registered, attach the provider to 1+ AI Gateway resources. The same Custom
provider can attach to many resources (e.g. the unsloth-serve provider attaches to
both the private and the public resource on `ai.cianfhoghlaim.ie`).

### Programmatic provisioning

Per `scripts/pangolin/provision_ai_gateway.py` — a single Python script that:
1. Mints the Custom provider via `POST /api/v1/org/{org}/ai-providers`
2. Mints the 2 overlapping AI Gateway resources via `POST /api/v1/org/{org}/resources`
3. Sets the per-role + global budgets

```bash
# Mint a fresh API key at https://pangolin.cianfhoghlaim.ie → Settings → API Keys
PANGOLIN_API_KEY=<fresh> uv run python scripts/pangolin/provision_ai_gateway.py

# Dry-run (prints what would be done without making changes)
PANGOLIN_API_KEY=dummy uv run python scripts/pangolin/provision_ai_gateway.py --dry-run
```

## 3. Budgets (per-role + global)

Pangolin's budgets cap **estimated USD spend** OR **token usage** at 4 scopes:

- **Provider** (e.g. don't exceed $20/day on OpenAI)
- **Model** (e.g. don't exceed $5/day on gpt-4o)
- **Resource** (e.g. don't exceed $50/day on `ai-public`)
- **Role** (e.g. CI-Agent role is capped at $5/day)
- **Key** (per-virtual-API-key caps)

Recommended dev-mode budgets on `ai-public`:

```yaml
- scope: role
  role: CI-Agent
  limit_usd_per_day: 5.0
- scope: global
  limit_usd_per_day: 50.0
```

The `ai-private` resource should NOT have budgets (operators are trusted).

## 4. Session log + usage analytics

Every call is logged with: timestamp, caller identity, model, prompt_tokens,
completion_tokens, estimated_cost_usd, latency_ms, role, resource. Forward these
to:

- **Langfuse** (`:3001`) for trace-level prompt/response inspection
- **MLflow** (`:5050`) for token/cost aggregation per model

## 5. Wire-up per AI client

### OpenCode

```bash
pangolin configure opencode --resource ai.cianfhoghlaim.ie
# Writes ~/.config/opencode/opencode.json + auth.json
```

The repo's `opencode.json` already has a `pangolin-ai-gateway` provider configured
manually with `baseURL: https://ai.cianfhoghlaim.ie/v1` and `apiKey: "none"`.

### Claude Code, Codex, Gemini CLI

Per https://docs.pangolin.net/manage/ai/configure-ai-clients/ — the gateway exposes
the native API format for each provider (Anthropic Messages, OpenAI Chat, Gemini
`generateContent`). Point the client at the gateway URL with `Authorization: Bearer vk_<key>`.

### Curl (sanity check)

```bash
# Private resource (over Pangolin.app tunnel)
curl -s -H "Authorization: Bearer none" https://ai.cianfhoghlaim.ie/v1/models | jq .

# Public resource (with virtual API key)
curl -s -H "Authorization: Bearer vk_abc123" https://ai.cianfhoghlaim.ie/v1/models | jq .
```

## 6. When to use this skill

Activate when the user asks about:
- "set up the AI gateway for our self-hosted LLMs"
- "expose unsloth-serve / invokeai / comfyui via Pangolin"
- "give me one URL for both Claude Code and CI"
- "cap spend on the CI agent"
- "route Anthropic + OpenAI + Gemini through one Pangolin FQDN"
- "what's the difference between public and private AI Gateway?"

## Reference

- Upstream product page: https://pangolin.net/ai-gateway
- Upstream docs: https://docs.pangolin.net/manage/ai/overview
- Per-client setup: https://docs.pangolin.net/manage/ai/configure-ai-clients/
- Provisioning script: `scripts/pangolin/provision_ai_gateway.py`
- Companion skill: `pangolin-cli` (for the CLI that wires coding agents to the gateway)
