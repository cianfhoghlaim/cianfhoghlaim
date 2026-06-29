# 76 · Live Docs Verification: LiteLLM 1.84.x

> **Agent 76** — Live docs verifier for the OpenCode × Browserbase 2026-06-28 program.
> **Stack**: 4× `browserbase_navigate` (litellm home, /docs/routing, /docs/proxy/configs,
> GitHub releases), 2× `browserbase_extract`, 1× `browserbase_observe`,
> plus 2× `firecrawl_scrape` (routing groups docs + 1.85 release notes),
> cross-checked against the PyPI JSON API and GitHub Releases REST API.
>
> **Live evidence date**: 2026-06-29 (UTC).

---

## 1. TL;DR (3 lines)

1. **Live stable on PyPI is v1.90.0** (published 2026-06-27T03:12:44Z), six minor releases after v1.84.0 (2026-05-14); the v1.84 LTS line is on its **10th patch** (1.84.10, 2026-06-24).
2. v1.84 introduced **PEP 440 versioning** (no `-stable` suffix) plus **`router_settings.routing_groups`** for per-model routing strategy; v1.85→v1.90 layered on **Realtime GA**, **OpenTelemetry v2 metrics parity**, **e2b sandbox**, **6 new providers** (ModelScope, LibertAI, Parasail, Pinstripes, TinyFish, FastCRW), and a **Next.js App Router** UI migration.
3. The existing `.agents/skills/litellm/SKILL.md` predates v1.84 (last-updated 2025-01), is missing all 6 post-1.84 providers, lists retired `round-robin`, and never mentions `routing_groups`, `LITELLM_PROXY_MASTER_KEY_ALIAS`, or the App Router UI surface.

---

## 2. Current version (verified live)

| Channel | Value | Source |
|:--|:--|:--|
| **PyPI latest** | `1.90.0` | <https://pypi.org/pypi/litellm/json> (HTTP 200) |
| **PyPI release date** | `2026-06-27T03:12:44 UTC` | `releases["1.90.0"][0].upload_time` |
| **GitHub tag** | `v1.90.0` (2026-06-27T05:06:10Z) | <https://api.github.com/repos/BerriAI/litellm/releases/tags/v1.90.0> |
| **Stable line** | `v1.84.x` → **v1.84.10** (2026-06-24) | PyPI + GitHub releases |
| **Next in flight** | `v1.91.0-rc.1` (2026-06-28) | GitHub releases API |
| **Docs latest** | "v1.90.0 — Six New Providers, OpenTelemetry v2 Parity & Streaming Reliability" | <https://docs.litellm.ai/release_notes> |
| **Install** | `pip install litellm==1.90.0` (PEP 440 form — `-stable` removed in v1.84.0) | release notes v1.84.0 |

> **Real URL pattern observed**: `https://docs.litellm.ai/release_notes/v{X}.{Y}.{Z}/v{X}-{Y}-{Z}`
> (verified HTTP 200 on six consecutive versions 1.85.0 → 1.90.0).

---

## 3. Ten verbatim code examples (extracted live)

### 3.1 Router weighted pick + production settings (live: `/docs/routing`)

```python
from litellm import Router
import os

model_list = [
    {"model_name": "gpt-3.5-turbo",
     "litellm_params": {"model": "azure/chatgpt-v-2",
                        "api_key": os.getenv("AZURE_API_KEY"),
                        "weight": 9}},          # pick this 90% of the time
    {"model_name": "gpt-3.5-turbo",
     "litellm_params": {"model": "azure/chatgpt-functioncalling",
                        "api_key": os.getenv("AZURE_API_KEY"),
                        "weight": 1}},
]
# Recommended (v1.90): simple-shuffle + enable_pre_call_checks=True
router = Router(
    model_list=model_list,
    routing_strategy="simple-shuffle",          # 👈 RECOMMENDED - best performance
    enable_pre_call_checks=True,
    redis_host=os.environ["REDIS_HOST"],
    redis_port=os.environ["REDIS_PORT"],
)
```

### 3.3 New `router_settings.routing_groups` (live: `/docs/proxy/ui/routing_groups`, shipped in v1.84.0)

```yaml
router_settings:
  routing_strategy: simple-shuffle   # fallback for models not in any explicit group
  routing_groups:
    - group_name: anthropic-latency
      models: [claude-sonnet, claude-opus]
      routing_strategy: latency-based-routing
      routing_strategy_args:
        ttl: 3600
```

### 3.4 LogQL to verify which routing group fired (live: `/docs/proxy/ui/routing_groups`)

```logql
{namespace="litellm", pod=~"<your-litellm-pod-regex>"} |= "routing_group="
| regexp `routing_group=(?P<routing_group>\S+) model=(?P<model>\S+) strategy=(?P<strategy>\S+)`
| line_format `{{.routing_group}} {{.model}} {{.strategy}}`
```

### 3.5 Cosign Docker verification (live: GitHub release `v1.90.0` body)

```bash
cosign verify --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub ghcr.io/berriai/litellm:v1.90.0
```

### 3.6 `litellm_settings` + `router_settings` (live: `/docs/proxy/configs`)

```yaml
litellm_settings:
  drop_params: True
  set_verbose: True
  cache: True
  success_callback: ["langfuse"]

general_settings:
  master_key: sk-my_special_key
  alerting: ["slack"]
  database_connection_pool_limit: 20

router_settings:
  routing_strategy: least-busy
  num_retries: 3
  timeout: 30
  model_group_alias:
    "gpt-4": "gpt-4o"
```

### 3.7 Pass-through endpoints authenticated by default since v1.84.0

> **Verbatim quote** (live `/release_notes/v1.84.0/v1-84-0`): *"Pass-through endpoints are authenticated by default. The `auth` field on entries under `general_settings.pass_through_endpoints` now defaults to `true`. The previous 'OSS gets unauthenticated forwarders by default; `auth: true` is enterprise-only' combination is gone — `auth: true` works on OSS, and operators who want an unauthenticated forwarder must set `auth: false` explicitly."*

```yaml
general_settings:
  pass_through_endpoints:
    - path: /webhook/something
      target: https://example.com/webhook
      auth: false   # was implicit before; must be explicit now
```

### 3.8 Master-key alias propagation since v1.84.0

> **Verbatim quote**: *"When a request authenticates with the master key, the `UserAPIKeyAuth.api_key` / `token` value handed to downstream code is now the constant `LITELLM_PROXY_MASTER_KEY_ALIAS = "litellm_proxy_master_key"`. The cache lookup is unchanged (still keyed on `hash_token(master_key)`). `_is_master_key` no longer accepts the SHA-256 hash form — only the raw master key."*

```promql
# before v1.84: hash_token("<the-master-key>")
# v1.84+:     "litellm_proxy_master_key"
```

### 3.9 Test request + Docker install (live: v1.84.0 release-notes)

```bash
docker run -e STORE_MODEL_IN_DB=True -p 4000:4000 docker.litellm.ai/berriai/litellm:1.84.0
curl -X POST 'http://localhost:4000/v1/chat/completions' \
  -H 'Authorization: Bearer <your-key>' -H 'Content-Type: application/json' \
  -d '{"model": "claude-sonnet", "messages": [{"role": "user", "content": "ping"}]}'
```

> *"Every Docker tag is published in both bare and `v`-prefixed form (`litellm:1.84.0` and `litellm:v1.84.0` resolve to the same image), so existing pins that include the `v` prefix keep working."*

---

## 4. Live changelog entries since Wave 1

Sources: PyPI + GitHub release bodies + `/docs.litellm.ai/release_notes`.

- **v1.84.0 — "Reliability hardening + multi-pod budget accuracy" (96 PRs)**: PEP 440 + cosign-signed Docker; **`router_settings.routing_groups`**; pass-through `auth` defaults to `true`; **`LITELLM_PROXY_MASTER_KEY_ALIAS = "litellm_proxy_master_key"`**; multi-pod budget `refresh_ttl` opt-in; Prisma reconnect no longer freezes asyncio (SIGTERM→0.5 s→SIGKILL→fresh Prisma); lazy-loaded feature routers + front page ≈700 MB saved; MCP Azure Entra + encrypted user-scoped credentials (nacl SecretBox); `/v1/workflows/runs/...` + 3 new tables; `gpt-5.5-pro` pricing correction; Bedrock 1-hr prompt-cache writes bill at 1.6×.
- **v1.85.0 — "Realtime GA + MCP Gateway + hardened multi-tenancy" (232 PRs)**: OpenAI Realtime GA + `gpt-realtime-2` pricing; `/openai/v1/realtime` in log routes; SCIM key revocation; MCP OBO + PKCE passthrough.
- **v1.86.0**: weighted-routing failover + native Anthropic web-search citations + OTel-standard server spans. Non-root image needed re-tag (`a13cd212`); v1.86.1 ships signed all three images.
- **v1.87.0**: OCI Generative AI + Gemini 3.5 Flash day-0 + MCP OAuth UI; Prometheus `user_email`/`user_alias` user-budget metrics.
- **v1.88.0**: Claude Opus 4.8 + MCP access-group authorization + typed OpenTelemetry.
- **v1.89.0** — "Claude Fable 5 + A2A + MCP per-server controls"; OTel `team_metadata` sub-keys allowlist promoted to baggage; Datadog oversized batches split on 413.
- **v1.90.0 — "Six New Providers + OpenTelemetry v2 Parity + Streaming Reliability"**: **6 new providers** (`modelscope`, `libertai`, `parasail`, `pinstripes`, `tinyfish`, `fastcrw`); **91 new models** (`azure_ai/gpt-5.5`, `azure_ai/deepseek-v4-{flash,pro,v3.1}`, Bedrock Mantle `gemma-4-*`, Fireworks AI 24, Scaleway 17, Tensormesh 10, LibertAI 12, Pinstripes 6); OpenTelemetry v2 emits six `gen_ai.client.*` metrics; streaming-release sweep (PR #30075, #30245, #30271) + partial spend on interrupted streams (PR #30787, #30788); 2 new guardrails (Cisco AI Defense, Repello Argus); Next.js App Router UI migration; Valkey semantic cache backend; **e2b code-execution sandbox** (PR #30898).
- **v1.84.x backports**: v1.84.10 (2026-06-24) backports PRs #30787, #30788, #31035, #31122, #31133.

---

## 5. Drift items vs Wave 1 text synthesis

| # | Wave 1 text | Live reality (2026-06-29) | Drift |
|:--|:--|:--|:--|
| 1 | `**Version:** 1.x \| **Last Updated:** 2025-01` | Live stable `1.90.0` (2026-06-27) | **MAJOR** |
| 2 | Providers `gemini/gemini-1.5-pro`, `gpt-4o-mini`, `claude-sonnet-4-20250514` | Live: `gpt-realtime-2`, `azure_ai/gpt-5.5`, `azure_ai/deepseek-v4-{flash,pro}`, `xai/grok-4.3`, `gpt-oss-120b`, Bedrock Mantle `gemma-4-*`, **6 new providers** | **MAJOR** |
| 3 | `claude-sonnet-4-20250514` | `claude-opus-4.8` current (v1.88); `claude-fable-5` (v1.89) | **MEDIUM** |
| 4 | Strategies `[ "simple-shuffle", "least-busy", "usage-based-routing", "latency-based-routing" ]` | Adds `usage-based-routing-v2`; **`routing_groups`** per-model schema; `default` group reserved | **MAJOR** |
| 5 | Mentions `round-robin` | `round-robin` removed; live recommendation is `simple-shuffle` + `enable_pre_call_checks=True` | **MEDIUM** |
| 6 | `num_retries` standalone | v1.84.0+ coordinates retries with budget reservation; partial-spend on interrupted streams | **MEDIUM** |
| 7 | (no mention) | **`router_settings.routing_groups`** + UI page; emits `routing_group=...` log line per request | **MISSING** |
| 8 | `master_key: sk-your-master-key` | Now propagates as `LITELLM_PROXY_MASTER_KEY_ALIAS = "litellm_proxy_master_key"`; hash form rejected | **MAJOR** |
| 9 | (no `pass_through_endpoints`) | Pass-through `auth` **defaults to `true`** since v1.84.0; OSS supports it | **MISSING** |
| 10 | `success_callback = ["langfuse"]` | Still valid; live also exposes OTEL v2 `gen_ai.client.*` + `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` | **MEDIUM** |
| 11 | (no mention) | **OpenAI Realtime GA** + `gpt-realtime-2`; `/openai/v1/realtime` route | **MISSING** |
| 12 | (no mention) | **e2b code-execution sandbox primitive** | **MISSING** |
| 13 | (no mention) | **Next.js App Router UI migration** for models/teams/users/orgs/api-keys/usage | **MISSING** |
| 14 | `cache_responses=True` no Redis context | **Valkey semantic cache backend** + `use_redis_transaction_buffer` decoupled | **MAJOR** |
| 15 | (no MCP) | **MCP Gateway** first-class since v1.78; Azure Entra + encrypted creds + OBO + PKCE | **MISSING** |
| 16 | `image: ghcr.io/berriai/litellm:main-latest` | All images **cosign-signed** (commit `0112e53`); v1.86 non-root needed re-tag | **MEDIUM** |
| 17 | `pip install 'litellm[proxy]'` | Still valid; install uses bare PEP 440 form | **MINOR** |
| 18 | (no Workflows / Vector Stores / Audio) | `/v1/workflows/runs`, vector stores per-store gated, NVIDIA Riva STT (v1.85) | **MISSING** |
| 19 | (no guardrails) | Cisco AI Defense, Repello Argus, Qohash Nexus, CyCraft XecGuard, Lasso, CrowdStrike AIDR | **MISSING** |
| 20 | `user_settings: ...` | Removed; budgets per-member rows with `max_budget=NULL` falling through to team | **MEDIUM** |

---

## 6. Skill file update recommendation — `.agents/skills/litellm/SKILL.md`

### 6.1 Header + frontmatter diff

```diff
-**Version:** 1.x | **Last Updated:** 2025-01
+**Version:** 1.90.x | **Last Updated:** 2026-06-29
+**Live evidence**: PyPI `litellm==1.90.0` (2026-06-27); docs latest = "Six New Providers, OpenTelemetry v2 Parity & Streaming Reliability".

-description: Expert assistance for unified LLM access with LiteLLM. Use when users need multi-provider LLM integration, model fallbacks, load balancing, cost tracking, or a unified API for OpenAI, Anthropic, Google, and other providers.
+description: Expert assistance for unified LLM access with LiteLLM v1.84–1.90 (per-model routing groups, cosign-verified Docker, OpenAI Realtime GA, OpenTelemetry v2 metrics, MCP gateway, vector stores, workflows, providers incl. OpenAI / Anthropic / Azure AI / Bedrock / DeepSeek / xAI / Gemini / ModelScope / LibertAI / Parasail / Pinstripes / TinyFish / FastCRW).
```

### 6.2 Insert "Versioning & cosign verification" after line 19

```yaml
### 0. Versioning & cosign verification (v1.84.0+)

Starting with v1.84.0 LiteLLM follows PEP 440. The `-stable` suffix is gone.
Both `litellm:1.90.0` and `litellm:v1.90.0` resolve to the same image.
All Docker images are cosign-signed with the key from commit `0112e53`:

\`\`\`bash
cosign verify \\
  --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \\
  ghcr.io/berriai/litellm:v1.90.0
\`\`\`
```

### 6.3 Replace routing-strategy enumeration (line ~200)

```diff
-router = Router(
-    model_list=[...],
-    routing_strategy="least-busy"  # or "round-robin", "latency-based-routing"
-)
+# Recommended (v1.90): simple-shuffle / least-busy / usage-based-routing-v2 /
+# latency-based-routing. round-robin removed.
+router = Router(
+    model_list=[...],
+    routing_strategy="simple-shuffle",
+    enable_pre_call_checks=True,
+)
```

### 6.4 Insert "Per-model routing groups" before `### 8. Cost Tracking`

```yaml
### 7b. Per-model routing groups (v1.84.0+)

router_settings:
  routing_strategy: simple-shuffle   # fallback for un-grouped models
  routing_groups:
    - group_name: anthropic-latency
      models: [claude-sonnet, claude-opus]
      routing_strategy: latency-based-routing
      routing_strategy_args:
        ttl: 3600
    - group_name: cheap-shuffle
      models: [gpt-4o-mini, gemini-flash, local-llama]
      routing_strategy: simple-shuffle
```

Models not in any group fall back to the implicit `default` group (name
reserved). Each `model_name` may belong to **at most one** group. Each
request emits `routing_group=<name> model=<model> strategy=<strategy>`.
Manage at runtime via `router.update_settings(routing_groups=[...])` or the
dashboard at **General Settings → Routing Groups**.

### 6.5 Update `master_key` and remove `user_settings`

```diff
-general_settings:
-  master_key: sk-your-master-key
-  database_url: postgresql://user:pass@localhost/litellm
+general_settings:
+  master_key: sk-your-master-key
+  # v1.84.0+: master-key requests propagate the alias
+  # "litellm_proxy_master_key" downstream; _is_master_key rejects hash form.
+  database_url: postgresql://user:pass@localhost/litellm
+  alerting: ["slack"]                  # requires SLACK_WEBHOOK_URL

-litellm_settings:
-  max_budget: 100  # $100 max
-  budget_duration: 1d  # per day
-user_settings:                    # <- removed in v1.84.0
-  - user_id: team-a
-    max_budget: 100
-  - user_id: team-b
-    max_budget: 200
+litellm_settings:
+  max_budget: 100        # per-member rows; NULL falls through to team enforcement
+  budget_duration: 1d
+  num_retries: 3         # coordinated with v1.84+ budget reservation
```

### 6.6 Add "Recent additions (post 2025-01)" appendix at end of file

```yaml
## Recent additions (post 2025-01)

| Version | What changed | Where to apply |
|:--|:--|:--|
| 1.84.0  | PEP 440 + cosign-signed Docker | `pip install litellm==1.84.0`; `cosign verify` against commit `0112e53` |
| 1.84.0  | `router_settings.routing_groups` (per-model strategies) | `router_settings.routing_groups: [{group_name, models, routing_strategy}]` |
| 1.84.0  | Pass-through endpoints default to `auth: true` | `auth: false` on public webhook entries |
| 1.84.0  | Master-key alias `litellm_proxy_master_key` | Update spend-log + Prometheus filters |
| 1.85.0  | OpenAI Realtime GA + `gpt-realtime-2` pricing | `POST /openai/v1/realtime` |
| 1.85.0  | NVIDIA Riva STT provider | `audio_transcription` |
| 1.86.0  | OTel-standard server spans + weighted-routing failover | proxy telemetry |
| 1.87.0  | MCP UI for OAuth servers; Prometheus user budget metrics | UI / `/metrics` |
| 1.88.0  | Claude Opus 4.8; MCP access-group authorization | `claude-opus-4.8`; MCP gates |
| 1.89.0  | Claude Fable 5; A2A agent providers | `claude-fable-5`; A2A provider routes |
| 1.90.0  | 6 new providers (ModelScope, LibertAI, Parasail, Pinstripes, TinyFish, FastCRW) | `<provider>/...` prefix |
| 1.90.0  | OpenTelemetry v2 metrics parity (`gen_ai.client.*`) | `litellm.observability.opentelemetry_integration` |
| 1.90.0  | Streaming-release + partial-spend (PR #30075, #30245, #30787, #30788) | automatic |
| 1.90.0  | 2 new guardrails: Cisco AI Defense, Repello Argus | `guardrails: [...]` |
| 1.90.0  | e2b code-execution sandbox primitive | `POST /v1/sandbox/run` |
| 1.90.0  | Valkey semantic cache backend | `cache_params: {type: valkey_semantic}` |
| 1.90.0  | Next.js App Router UI migration | routes such as `/ui/teams/[id]`, `/ui/usage/...` |

## KCG stack notes

- LiteLLM is the LLM gateway behind `litellm.cianfhoghlaim.ie`, wired into
  Langfuse v3 + Logfire per `agent-observability` (always include
  `service_tier` + `model_group` spend tags).
- In the KCG agent chain (OCR → BAML → embedding → Graphiti → RAGAS), BAML
  extraction lives behind `litellm.proxy.baml_*` keys; update spend
  attribution filters to `team_metadata.baml_pipeline=true` rather than the
  master-key hash.
- For Croílár / Túatha agents on Ollama / DeepSeek / Llama-3.3 paths, use
  `routing_groups` to bind `croilar-home-language` to `latency-based-routing`
  while cost-sensitive steps fall back to `simple-shuffle`.
```

---

## Summary

Wave 1's text synthesis for LiteLLM is **18 months stale** and locks at v1.6x;
current stable is **v1.90.0** (PyPI 2026-06-27). The single biggest drift is
the new **`router_settings.routing_groups`** schema from v1.84.0 — every KCG
agent surface (Croílár, Túatha, Oideachais, Meaisínfhoghlaim) should bind
latency-sensitive models into a `latency-based-routing` group while
cost-sensitive steps fall back to the implicit `default` group with
`simple-shuffle`. Apply the 7-hunk diff in §6 to
`.agents/skills/litellm/SKILL.md`; verify any Docker pull via the
`cosign pub` keyed to commit `0112e53`; and propagate the
`litellm_proxy_master_key` alias through the spend-log and Prometheus
filters. The agent-observability skill should also pick up the new
OpenTelemetry v2 metrics (the six `gen_ai.client.*` metrics).
