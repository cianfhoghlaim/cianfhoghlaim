# P2-14 — litellm (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

LiteLLM is the **OpenAI-compatible LLM gateway** that fronts 70+ models for every BAML function, opencode subagent, Marimo notebook, and MotherDuck query. The `minimax` alias (Phase 0.4 default) routes through a 7-tier fallback chain — opencode-go/minimax-m3-slot{0,1,2} → qwen3.7-max → kimi-k2.6 → glm-4.6 → local/math/qwen25-math.

The canonical Cianfhoghlaim pattern: every BAML client + opencode subagent uses `litellm/minimax` (the alias), not a direct provider model.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/litellm/compose.yaml` | LiteLLM proxy + Postgres (DB for spend tracking) |
| `stacks/litellm/config/config.yaml` | **The 770-line config: 70+ models + 7-tier `minimax` alias** |
| `stacks/litellm/sidecar.yaml` | Locket sidecar for `LITELLM_MASTER_KEY` |
| `stacks/litellm/blueprint.yaml` | Pangolin private-resource (`litellm.cianfhoghlaim.ie:4000`) |
| `oideachais/baml_src/clients.baml` | BAML clients pointing at `LITELLM_BASE_URL/minimax` |
| `opencode.json` (provider.litellm) | opencode `litellm` provider (per spec) |
| `cognify/rules/llm_gateway_health.py` | Dagster asset check for `/health/liveliness` |

**Canonical model_list entry** (from `stacks/litellm/config/config.yaml` line ~362):

```yaml
- model_name: opencode-go/minimax-m3
  litellm_params:
    model: anthropic/minimax-m3
    api_base: https://opencode.ai/zen/go/v1/messages
    api_key: os.environ/OPENCODE_GO_API_KEY
  model_info:
    description: "MiniMax M3 (OpenCode Go) — current opencode model"
```

**The `minimax` alias** (line ~755):

```yaml
- model_name: minimax
  litellm_params:
    model: openai/minimax
    api_base: http://localhost:4000/v1  # recursive! litellm refers to itself
    api_key: not-needed
    routes:
      - name: "minimax-fallback"
        targets:
          - "opencode-go/minimax-m3-slot0"
          - "opencode-go/minimax-m3-slot1"
          - "opencode-go/minimax-m3-slot2"
          - "opencode-go/qwen3.7-max"
          - "opencode-go/kimi-k2.6"
          - "openai/glm-4.6"
          - "local/math/qwen25-math"
    model_info:
      capabilities: ["general", "agentic", "alias"]
      tier: paid
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `LITELLM_MASTER_KEY` | `infisical://dev-baile/litellm/master_key` | Locket |
| `LITELLM_DATABASE_URL` | `infisical://dev-baile/litellm/database_url` | Locket |
| `LITELLM_SALT_KEY` | `infisical://dev-baile/litellm/salt_key` | Locket |
| `OPENCODE_GO_API_KEY_0/1/2` | `infisical://dev-baile/opencode_go/api_key_0/1/2` | Locket |
| `OPENCODE_GO_API_KEY` (canonical) | `infisical://dev-baile/opencode_go/api_key` | Locket |
| `Qwen_API_KEY` | `infisical://dev-baile/qwen/api_key` | Locket |
| `GLM_API_KEY` | `infisical://dev-baile/glm/api_key` | Locket |
| `LITELLM_BASE_URL` | `http://litellm:4000/v1` | docker network |

## CCC anchors

`stacks/litellm/` · `stacks/litellm/config/config.yaml` · `oideachais/baml_src/clients.baml` · `cognify/rules/llm_gateway_health.py` · `opencode.json`

Search terms: `"minimax:"`, `"model_name: opencode-go/minimax-m3"`, `"fallback_chain"`, `"num_retries: 3"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-09 | Initial LiteLLM deploy (single model, no fallback) |
| 2025-11 | Added `deepseek/deepseek-chat` as default (works around Gemini 403) |
| 2026-02 | Added local GGUF fallback (llama-swap → qwen2.5-math) |
| 2026-04 | Added `minimax` alias (Phase 0.4 of BrowserBase research prep) |
| 2026-06 | Added 3-key round-robin for opencode-go/minimax-m3-slot{0,1,2} (5-hour cap rotation) |
| 2026-06-28 | Phase 0.4 commit: `default_model: minimax` set in general_settings |

## Anti-patterns

1. Don't call providers directly — always via `LITELLM_BASE_URL`
2. Don't hardcode API keys in `config.yaml` — use `os.environ/<VAR>` interpolation
3. Don't put LiteLLM master key in the gateway config (plain text) — use env
4. Don't skip `num_retries: 3` — that's what enables the fallback chain
5. Don't use `temperature=0` for all models — some providers ignore it (waste of cycles)
6. Don't bypass the alias (`minimax`) — direct model access skips the fallback chain
7. Don't disable `enable_json_schema_validation` — BAML strict schema enforcement depends on it

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Default model | `minimax` (alias) | 7-tier fallback for vendor-de-risking |
| Fallback chain | 3 MiniMax slots → 2 opencode-go alternatives → 1 GLM → 1 local GGUF | 5-hour cap rotation + offline safety |
| Provider | LiteLLM proxy (not direct) | Single point of model rotation |
| Auth | Master key in env, per-model keys | Per-provider least privilege |
| Observability | Langfuse auto-instrumentation | Trace every request |
| Spend tracking | LiteLLM Postgres DB | Real-time spend dashboard |
| Caching | Disabled (curriculum is dynamic) | Avoid stale responses |
| Version pin | `ghcr.io/berriai/litellm:main-stable` | Latest with auto-rebuilds |

## Files to read next

`stacks/litellm/config/config.yaml` (770 lines!) · `oideachais/baml_src/clients.baml` · `cognify/rules/llm_gateway_health.py` · `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md` · `.agents/skills/litellm/SKILL.md`
