# Agent 06 — LiteLLM (LLM Gateway)

**Date:** 2026-06-28 23:25 UTC
**Wave:** 1 (25 agents parallel) — Program 2
**Credits used:** ~12 (main docs + routing + configs + JSON mode + Langfuse + providers + MiniMax provider + cleaner-versions + PyPI + releases + 3 search queries)
**Subagent:** infrastructure

## TL;DR

LiteLLM is the **OpenAI-compatible LLM gateway** fronting 100+ LLM providers for every BAML function, opencode subagent, Marimo notebook, and MotherDuck query. The `minimax` alias (Phase 0.4 default, set `2026-06-28`) routes through a 7-tier fallback chain and remains intact. **Two urgent drift items discovered:**

1. **`main-stable` Docker tag is deprecated 2026-06-30** (in 2 days). Our pin `ghcr.io/berriai/litellm:main-stable` in `compose.yaml` must migrate to `:latest` or a pinned `:1.84.0+` version.
2. **LiteLLM now has a native `minimax` provider** for third-party MiniMax Inc. (Chinese AI, `MiniMax-M2`/`M2.1`/`M2.1-lightning` at `api.minimax.io`). Our bare `minimax` model_name does NOT collide today, but future cross-team usage of `minimax/MiniMax-M2.1` will route to MiniMax Inc., not our internal alias — needs docs note.

JSON mode, Langfuse integration, embedding routing, and the `num_retries: 3` fallback pattern all match our current usage. **Langfuse v3 OTEL is now the recommended integration path** — our current v2-callback pattern still works but should be evaluated for upgrade.

## Code

| Source | Path / URL | Purpose |
|:--|:--|:--|
| Local | `infrastructure/stacks/litellm/compose.yaml` | Docker Compose — LiteLLM proxy + Postgres for spend tracking |
| Local | `infrastructure/stacks/litellm/config/config.yaml` (776 lines) | Canonical model registry (100+ models + 7-tier `minimax` alias) |
| Local | `infrastructure/stacks/litellm/sidecar.yaml` | Locket sidecar for `LITELLM_MASTER_KEY` |
| Local | `infrastructure/stacks/litellm/blueprint.yaml` | Pangolin private-resource (`litellm.cianfhoghlaim.ie:4000`) |
| Local | `infrastructure/stacks/litellm/secrets.env` | `infisical://dev-baile/litellm/*` template |
| Local | `infrastructure/stacks/litellm/README.md` | Stack notes (needs `main-stable` migration doc) |
| Local | `infrastructure/dagger/ts_submodules/bonneagar/src/observability.ts:487-509` | Dagger TS — `generateLiteLLMCallbackConfig()` template |
| Local | `infrastructure/stacks/openclaw/skills-curated/litellm/references/litellm-comprehensive-guide.md:3936-3979` | Curated skills reference (latency-based routing, multi-region) |
| Local | `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215` | `minimax_alias_health` Dagster asset check |
| Local | `openspec/changes/litellm-minimax-vendor-derisking/proposal.md:43-57` | Phase 0.4 proposal — 7-tier fallback origin |
| Local | `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md:18-25` | Spec — fallback chain SHALL order |
| Local | `openspec/changes/2026-06-28-browserbase-phase-1a-decisions/specs/oideachais-pipeline/spec.md:1-23` | Phase 1A delta — `minimax` alias canonical |
| Local | `openspec/changes/2026-06-28-browserbase-phase-2-decisions/specs/meaisinfhoghlaim-platform/spec.md:1-22` | Phase 2 delta — LiteLLM canonical |
| Web | https://docs.litellm.ai | Main docs (Docusaurus v3.8.1) — "Call 100+ LLMs" |
| Web | https://docs.litellm.ai/docs/routing | Router — load balancing + fallbacks + Redis cooldown |
| Web | https://docs.litellm.ai/docs/proxy/configs | Config schema: `model_list` / `router_settings` / `litellm_settings` / `general_settings` / `environment_variables` / `credential_list` |
| Web | https://docs.litellm.ai/docs/completion/json_mode | `response_format` + `json_schema` + `enable_json_schema_validation` |
| Web | https://docs.litellm.ai/docs/observability/langfuse_integration | Legacy v2 Langfuse callback (per-request credentials supported) |
| Web | https://docs.litellm.ai/docs/observability/langfuse_otel_integration | NEW v3 Langfuse OTEL integration (recommended) |
| Web | https://docs.litellm.ai/docs/providers | Provider directory (MiniMax, GLM, OpenAI, Anthropic, Bedrock, +100) |
| Web | https://docs.litellm.ai/docs/providers/minimax | **NEW native third-party MiniMax provider (Chinese AI)** |
| Web | https://docs.litellm.ai/blog/cleaner-release-versions | **`main-stable` deprecation, June 30 2026 cutover** |
| Web | https://docs.litellm.ai/blog/security-update-march-2026 | March 2026 supply-chain incident; v1.83.0 clean |
| Web | https://docs.litellm.ai/release_notes/ | v1.82.3 (Mar 16 2026) latest visible stable |

**Canonical `minimax` alias block** (`infrastructure/stacks/litellm/config/config.yaml:714-730`):

```yaml
- model_name: minimax
  litellm_params:
    model: anthropic/minimax-m3
    api_base: https://opencode.ai/zen/go/v1/messages
    api_key: os.environ/OPENCODE_GO_API_KEY
  model_info:
    description: "Alias: minimax → M3 (3-key round-robin), then qwen3.7-max, kimi-k2.6, glm-4.6, then local qwen-math GGUF"
    capabilities: ["general", "agentic", "alias"]
    tier: paid
    fallback_chain:
      - "opencode-go/minimax-m3-slot0"
      - "opencode-go/minimax-m3-slot1"
      - "opencode-go/minimax-m3-slot2"
      - "opencode-go/qwen3.7-max"
      - "opencode-go/kimi-k2.6"
      - "openai/glm-4.6"
      - "local/math/qwen25-math"
```

**`general_settings` (lines 736-765)** — confirms `default_model: minimax` (line 753), `enable_json_schema_validation: true` (line 745), Langfuse config block (lines 760-765), `database_connection_pool_limit: 10` matching the new docs guidance (10-20 recommended).

**`router_settings` (lines 770-776)** — confirms `num_retries: 3`, `timeout: 600`, `enable_caching: false`, `caching_groups: []`, no Redis.

**LiteLLM docs canonical fallback syntax** (https://docs.litellm.ai/docs/proxy/configs#load-balancing, section "Load Balancing"):

```yaml
litellm_settings:
  num_retries: 3
  request_timeout: 10
  fallbacks: [{"zephyr-beta": ["gpt-4o"]}]
  context_window_fallbacks: [{"zephyr-beta": ["gpt-3.5-turbo-16k"]}, {"gpt-4o": ["gpt-3.5-turbo-16k"]}]
  allowed_fails: 3  # cooldown model if it fails > 1 call in a minute
router_settings:
  routing_strategy: simple-shuffle  # default
  num_retries: 2
  timeout: 30
  redis_host: <redis host>  # for multi-instance
```

> **Drift:** We currently use `model_info.fallback_chain` (a custom convention at line 723) instead of the canonical `litellm_settings.fallbacks` array. Our custom field is documented in the spec but not enforced by LiteLLM — verify whether `minimax` alias actually triggers fallback today, or whether the fallback silently doesn't fire.

**JSON mode for BAML** (https://docs.litellm.ai/docs/completion/json_mode):

```python
# Proxy / SDK unified response_format:
response_format={
  "type": "json_schema",
  "json_schema": {"name": "...", "schema": {...}, "strict": True}
}

# Client-side validation for non-Gemini-2.0 / non-OpenAI / non-Anthropic:
litellm.enable_json_schema_validation = True
# Confirmed in our config.yaml line 745
```

`get_supported_openai_params(model="...", custom_llm_provider="...")` → check before relying on `response_format`. `supports_response_schema(model="...", custom_llm_provider="...")` → check before relying on `json_schema`. Supported providers: OpenAI, Azure, xAI (Grok-2+), Google AI Studio Gemini, Vertex AI (Gemini + Anthropic), Bedrock, Anthropic API, Groq, Ollama, Databricks. **Gemini 2.0+ uses native `responseJsonSchema` (better Pydantic compat)**; Gemini 1.5 uses OpenAPI `responseSchema` (no `additionalProperties: false`).

**Langfuse v2 callback pattern** (current usage at config.yaml:760-765; canonical example https://docs.litellm.ai/docs/observability/langfuse_integration):

```yaml
# Option A — env-var + module callback (our current pattern)
general_settings:
  langfuse:
    langfuse_enabled: true
    langfuse_host: os.environ/LANGFUSE_HOST
    langfuse_public_key: os.environ/LANGFUSE_PUBLIC_KEY
    langfuse_secret_key: os.environ/LANGFUSE_SECRET_KEY

# Option B — module-level callback (alternative)
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["langfuse"]
```

> **Recommended path:** Docs now say "For Langfuse v3, we recommend using the [Langfuse OTEL](https://docs.litellm.ai/docs/observability/langfuse_otel_integration) integration." Per-request credentials supported via `langfuse_public_key=`, `langfuse_secret_key=`, `langfuse_host=` kwargs. `litellm.turn_off_message_logging=True` for PII redaction. Pin `langfuse==2.59.7` (SDK) for current Langfuse v2 compat.

**Embedding routing** (https://docs.litellm.ai/docs/proxy/configs#embedding-models):

```yaml
model_list:
  - model_name: text-embedding-ada-002
    litellm_params:
      model: text-embedding-ada-002
      api_key: os.environ/OPENAI_API_KEY_1
  - model_name: text-embedding-ada-002
    litellm_params:
      model: text-embedding-ada-002
      api_key: os.environ/OPENAI_API_KEY_2  # LB between two keys
```

Multiple deployments with the same `model_name` auto-load-balance. Supported: Sagemaker, Bedrock, HuggingFace (inference endpoints + free API), Azure OpenAI, OpenAI, Xinference, any OpenAI-compatible. **Note: Our `embedding-*` aliases (lines 657) use this pattern but route only to single backends each — consider adding LB tiers.**

**Credential management — NEW pattern** (https://docs.litellm.ai/docs/proxy/configs#centralized-credential-management):

```yaml
model_list:
  - model_name: gpt-4o
    litellm_params:
      model: azure/gpt-4o
      litellm_credential_name: default_azure_credential  # NEW: cross-model credential ref
credential_list:
  - credential_name: default_azure_credential
    credential_values:
      api_key: os.environ/AZURE_API_KEY
      api_base: os.environ/AZURE_API_BASE
      api_version: "2023-05-15"
    credential_info:
      description: "Production credentials for EU region"
      custom_llm_provider: "azure"
```

> **Refactor opportunity:** We currently duplicate `api_key: os.environ/OPENCODE_GO_API_KEY_0/1/2` across the 3 minimax-m3 slots (config.yaml:381-410). With `credential_list` + `litellm_credential_name`, we could define each key once and reference — but the slot rotation semantics (which slot burns first) may differ. Verify before refactor.

## Env

| Env var | Value | Source | Notes |
|:--|:--|:--|:--|
| `LITELLM_MASTER_KEY` | `infisical://dev-baile/litellm/master_key` | Locket | Our config — ✓ matches canonical |
| `LITELLM_DATABASE_URL` | `infisical://dev-baile/litellm/database_url` | Locket | Postgres for spend tracking |
| `LITELLM_SALT_KEY` | `infisical://dev-baile/litellm/salt_key` | Locket | New — for DB-encrypted virtual keys |
| `OPENCODE_GO_API_KEY_0/1/2` | `infisical://dev-baile/opencode_go/api_key_0/1/2` | Locket | 3-key round-robin for `minimax-m3-slot{0,1,2}` |
| `OPENCODE_GO_API_KEY` | `infisical://dev-baile/opencode_go/api_key` | Locket | Canonical for `opencode-go/*` direct |
| `Qwen_API_KEY` | `infisical://dev-baile/qwen/api_key` | Locket | Dashscope |
| `GLM_API_KEY` | `infisical://dev-baile/glm/api_key` | Locket | Z.ai direct (chain tier 6) |
| `LITELLM_BASE_URL` | `http://litellm:4000/v1` | docker network | BAML / opencode / marimo |
| `LANGFUSE_HOST` | `https://langfuse.cianfhoghlaim.ie` | Locket | Used by general_settings.langfuse |
| `LANGFUSE_PUBLIC_KEY` | `infisical://dev-baile/langfuse/public_key` | Locket | Required for callback to fire |
| `LANGFUSE_SECRET_KEY` | `infisical://dev-baile/langfuse/secret_key` | Locket | Required for callback to fire |

> **NEW docs env var (not yet in our config):** `LITELLM_LICENSE` (Enterprise features), `LITELLM_CONFIG_BUCKET_*` (read config from S3/GCS instead of file), `NO_DOCS` / `NO_REDOC` (disable Swagger UI), `LITELLM_ENVIRONMENT` (production/staging/development gating via `model_info.supported_environments`).

## CCC anchors

| Anchor | File | Notes |
|:--|:--|:--|
| `minimax` alias | `infrastructure/stacks/litellm/config/config.yaml:714-730` | 7-tier `fallback_chain` (custom field) |
| `default_model: minimax` | `infrastructure/stacks/litellm/config/config.yaml:753` | Phase 0.4 commit |
| `enable_json_schema_validation: true` | `infrastructure/stacks/litellm/config/config.yaml:745` | BAML strict mode |
| `num_retries: 3` | `infrastructure/stacks/litellm/config/config.yaml:771` | Fallback trigger |
| `enable_caching: false` | `infrastructure/stacks/litellm/config/config.yaml:775` | Curriculum is dynamic |
| `database_connection_pool_limit: 10` | `infrastructure/stacks/litellm/config/config.yaml:740` | Matches new docs recommendation 10-20 |
| `langfuse:` block | `infrastructure/stacks/litellm/config/config.yaml:760-765` | v2-callback pattern |
| Opencode-go providers | `infrastructure/stacks/litellm/config/config.yaml:289-410` | 9 routes via `opencode.ai/zen/go/v1/{messages,chat/completions}` |
| 3-key round-robin | `infrastructure/stacks/litellm/config/config.yaml:381-410` | `opencode-go/minimax-m3-slot{0,1,2}` |
| Local MLX/GGUF | `infrastructure/stacks/litellm/config/config.yaml:34-200` | llama-swap (:8080) + mlx-omni (:10240) |
| Health asset | `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215` | `minimax_alias_health` check |

**CCC search terms that hit:**

- `"litellm model_list minimax default_model fallback_chain"` → 8 hits including the spec at `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md:18-25`
- `"litellm config general_settings langfuse num_retries"` → 6 hits including the comprehensive curated guide at `infrastructure/stacks/openclaw/skills-curated/litellm/references/litellm-comprehensive-guide.md:3936-3979`

## Drift log

| Date | Event | Source |
|:--|:--|:--|
| 2025-09 | Initial LiteLLM deploy (single model, no fallback) | Phase 0 log |
| 2025-11 | Added `deepseek/deepseek-chat` as default | Phase 0 log |
| 2026-02 | Added local GGUF fallback (llama-swap → qwen2.5-math) | Phase 0 log |
| 2026-03-30 | **LiteLLM security update** — v1.83.0 clean after suspected supply chain incident | https://docs.litellm.ai/blog/security-update-march-2026 |
| 2026-04-28 | **`main-stable` Docker tag deprecated** (cutover 2026-06-30) | https://docs.litellm.ai/blog/cleaner-release-versions |
| 2026-04 | Added `minimax` alias (Phase 0.4) | openspec/changes/litellm-minimax-vendor-derisking |
| 2026-05 | Cleaner versioning: stable = `1.84.0+` (no `-stable` suffix), MINOR bumps weekly, PATCH reserved for hotfixes | https://docs.litellm.ai/blog/cleaner-release-versions |
| 2026-06 | Added 3-key round-robin for `opencode-go/minimax-m3-slot{0,1,2}` | config.yaml:381-410 |
| 2026-06-28 | Phase 0.4 commit: `default_model: minimax` set in `general_settings` | config.yaml:753 |
| 2026-06-28 | **DRIFT:** Native LiteLLM `minimax` provider added for MiniMax Inc. — potential cross-team confusion | https://docs.litellm.ai/docs/providers/minimax |
| 2026-06-28 | **DRIFT:** Langfuse OTEL recommended for v3 (we still use v2-callback) | https://docs.litellm.ai/docs/observability/langfuse_integration |

## Anti-patterns

1. **Don't pin `main-stable`** — deprecated 2026-06-30 (2 days from today). Use `:latest` (rolling) or pin a specific `:1.84.0+` version for reproducibility.
2. **Don't hardcode API keys in `config.yaml`** — use `os.environ/<VAR>` interpolation (we do this ✓ — `os.environ/OPENCODE_GO_API_KEY`, etc.).
3. **Don't put LiteLLM master key in plain config** — we use env-var ✓.
4. **Don't skip `num_retries: 3`** — required for the `minimax` 7-tier fallback to fire (we set ✓).
5. **Don't use `temperature=0` blindly** — some providers ignore it (we don't set temperature globally ✓).
6. **Don't bypass the `minimax` alias** — direct model access skips the fallback chain (Phase 1A spec enforces ✓).
7. **Don't disable `enable_json_schema_validation`** — BAML strict schema enforcement depends on it (we enable ✓ — config.yaml:745).
8. **Don't write `minimax/MiniMax-M2.1`** expecting our internal alias — that string now routes to **third-party MiniMax Inc.** (Chinese AI at `api.minimax.io`). Use bare `minimax` for our alias, or rename to avoid future confusion.
9. **Don't rely on `model_info.fallback_chain`** as a custom field — the canonical pattern is `litellm_settings.fallbacks: [{"primary": ["fallback1"]}]`. Verify our custom field actually triggers fallback or migrate to the canonical form.
10. **Don't ignore the March 2026 security advisory** — confirm our deployed `litellm` is ≥ v1.83.0.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Default model | `minimax` (alias) | 7-tier fallback for vendor-de-risking ✓ confirmed |
| Fallback chain syntax | `model_info.fallback_chain` (custom) — **needs validation** | Our convention; docs canonical is `litellm_settings.fallbacks` |
| JSON mode | `enable_json_schema_validation: true` | Matches BAML strict schema enforcement |
| Langfuse integration | v2 callback (current) | Works ✓ — consider OTEL upgrade for v3 |
| Embedding routing | Single deployment per alias | Could add LB tiers (Azure + OpenAI split) |
| Spend tracking | LiteLLM Postgres DB | Real-time dashboard ✓ |
| Caching | Disabled (`enable_caching: false`) | Curriculum is dynamic per request ✓ |
| Version pin (URGENT) | `ghcr.io/berriai/litellm:main-stable` — **needs migration to `:latest` or `:1.84.0+` by 2026-06-30** | Docs mandate cutover |
| Security baseline | ≥ v1.83.0 (post supply-chain incident) | March 2026 advisory |
| Provider count | 100+ (was 70+) | docs.litellm.ai header updated |

## §8 Refactor opportunities

### 8.1 URGENT (within 48h) — `main-stable` Docker tag deprecation

**File:** `infrastructure/stacks/litellm/compose.yaml` — change `ghcr.io/berriai/litellm:main-stable` to either:

- **Rolling stable (recommended for dev):** `ghcr.io/berriai/litellm:latest`
- **Reproducible pin (recommended for prod):** `ghcr.io/berriai/litellm:1.84.0`

Verify our currently-deployed image is ≥ v1.83.0 (clean post supply-chain incident) by checking the running container's banner.

**Cross-spec impact:** the `infrastructure-stacks` spec mentions `main-stable` — needs update too. Search: `grep -rn "main-stable" infrastructure/stacks/litellm/ openspec/specs/`.

### 8.2 HIGH — Native `minimax` provider namespace collision

**Issue:** LiteLLM now ships a native `minimax` provider for MiniMax Inc. (Chinese AI company; models `MiniMax-M2`, `MiniMax-M2.1`, `MiniMax-M2.1-lightning` at `api.minimax.io`). Our bare `minimax` model_name does not collide (it's not `minimax/<model>`), but cross-team confusion is likely.

**Mitigation options:**

1. **Rename our alias** from `minimax` → `kanon` (Irish for "canon/standard") or `briathar` (Irish for "verb/utterance") or keep as-is and add a doc note.
2. **Add a `model_info.comment` field** that warns about the namespace overlap.
3. **Document the disambiguation** in `infrastructure/stacks/litellm/README.md` so cross-team contributors know `minimax` (bare) = our alias, `minimax/MiniMax-*` = third-party MiniMax Inc.

**Cross-spec impact:** all openspec deltas that say `model="minimax"` or reference `litellm/minimax` need a footnote.

### 8.3 MEDIUM — Fallback chain syntax migration

**Issue:** We use a custom `model_info.fallback_chain: [...]` list at config.yaml:723-730. LiteLLM's canonical syntax is `litellm_settings.fallbacks: [{"minimax": ["opencode-go/minimax-m3-slot1", ...]}]`. Our spec at `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md:18-25` enforces the order — but if LiteLLM doesn't recognize the custom field, the `minimax` alias may not actually fall back today.

**Action:** Add `litellm_settings.fallbacks` block and verify `num_retries: 3` actually cycles. Write a Dagster asset check that simulates a 429 from `opencode-go/minimax-m3-slot0` and confirms the next slot answered.

### 8.4 MEDIUM — Langfuse v3 OTEL migration

**Issue:** Docs now recommend Langfuse v3 OTEL integration. Our config uses the v2 callback (lines 760-765). The v2 path still works but is on a deprecation trajectory.

**Action:** Open a `openspec/changes/litellm-langfuse-otel/` change to migrate from `general_settings.langfuse` callback block to `litellm_settings.callbacks` + OTEL exporter. Compare trace fidelity.

### 8.5 LOW — Credential centralization

**Issue:** We duplicate `api_key: os.environ/OPENCODE_GO_API_KEY_0/1/2` across 3 minimax-m3 slot entries (config.yaml:381-410). The new `credential_list` pattern lets us define each credential once and reference via `litellm_credential_name`.

**Action:** Refactor slot entries to use `litellm_credential_name: opencode_go_key_0/1/2`. Verify slot rotation semantics are preserved (3-key round-robin should still rotate).

### 8.6 LOW — DB pool limit audit

**Issue:** We set `database_connection_pool_limit: 10`. Docs guidance: `MAX_DB_CONNECTIONS ÷ (instances × workers_per_instance) = 12.5` for a single-instance 8-worker setup. We don't run `--num_workers > 1`, so 10 is fine today.

**Action:** Document the formula in `infrastructure/stacks/litellm/README.md` so future operators don't blindly copy the value.

### 8.7 LOW — Embedding LB tiers

**Issue:** Our `embedding-*` aliases (config.yaml:657 area) each point to a single backend. The docs canonical pattern allows LB across multiple backends (e.g. OpenAI primary + Azure secondary).

**Action:** For high-throughput embeddings (BGE-M3 leabharlann corpus), add a second deployment under the same `model_name` for LB. Track spend per backend via the dashboard.

### 8.8 LOW — `model_info.supported_environments` per-stack gating

**Issue:** The new docs support `model_info.supported_environments: ["production", "staging", "development"]` for environment-aware model exposure. We don't currently set this — the dev `litellm` instance exposes all models.

**Action:** Tag paid providers (e.g. `openai/glm-4.6`, `opencode-go/qwen3.7-max`) with `supported_environments: ["production"]` so dev stays on cheaper routes.

## Files to read next

- `infrastructure/stacks/litellm/config/config.yaml` (776 lines — full read needed for refactor 8.3)
- `infrastructure/stacks/litellm/compose.yaml` (needs `main-stable` → `:latest`/`:1.84.0`)
- `infrastructure/stacks/litellm/README.md` (add MiniMax namespace note)
- `openspec/changes/litellm-minimax-vendor-derisking/specs/llm-gateway/spec.md` (verify fallback syntax)
- `openspec/changes/litellm-minimax-vendor-derisking/proposal.md:43-57` (origin of 7-tier chain)
- `openspec/changes/litellm-langfuse-otel/` (NEW change to author for 8.4)
- `openspec/changes/litellm-main-stable-cutover/` (NEW change to author for 8.1)
- `docs.litellm.ai/blog/cleaner-release-versions` (migrate by 2026-06-30)
- `docs.litellm.ai/blog/security-update-march-2026` (verify ≥ v1.83.0)
- `docs.litellm.ai/docs/providers/minimax` (the third-party collision note for 8.2)
- `docs.litellm.ai/docs/observability/langfuse_otel_integration` (for 8.4)
- `infrastructure/stacks/openclaw/skills-curated/litellm/references/litellm-comprehensive-guide.md` (curated skills reference, 4300+ lines)
- `infrastructure/dagger/ts_submodules/bonneagar/src/observability.ts:487-509` (Dagger TS callback template)
- `cianfhoghlaim/assets/_oideachais_dagster_defs/assets/llm_gateway_assets.py:200-215` (existing `minimax_alias_health` check)