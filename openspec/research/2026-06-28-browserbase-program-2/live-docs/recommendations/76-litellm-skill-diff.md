# 76 — Litellm Skill Diff Recommendations

> Companion to `openspec/research/2026-06-28-browserbase-program-2/live-docs/76-live-litellm-184.md`.
> Apply each `Edit` / `MultiEdit` to `.agents/skills/litellm/SKILL.md` (root of the skill folder).

## Hunk 1 — Header + frontmatter

```diff
---- name: litellm
-description: Expert assistance for unified LLM access with LiteLLM. Use when users need multi-provider LLM integration, model fallbacks, load balancing, cost tracking, or a unified API for OpenAI, Anthropic, Google, and other providers.
+name: litellm
+description: Expert assistance for unified LLM access with LiteLLM v1.84–1.90. Use when users need multi-provider LLM integration, per-model routing groups, weighted/rate-limited load balancing, PEP 440 versioning, cosign-verified Docker images, OpenAI Realtime GA, OpenTelemetry v2 metrics, MCP gateway, vector stores, workflows, or a unified proxy for OpenAI / Anthropic / Azure AI / Bedrock / DeepSeek / xAI / Gemini / ModelScope / LibertAI / Parasail / Pinstripes / TinyFish / FastCRW.
----

 # LiteLLM - Unified LLM Interface

-**Version:** 1.x | **Last Updated:** 2025-01
+**Version:** 1.90.x | **Last Updated:** 2026-06-29
+**Live evidence**: PyPI `litellm==1.90.0` published 2026-06-27; docs latest = "Six New Providers, OpenTelemetry v2 Parity & Streaming Reliability".
```

## Hunk 2 — Insert Section 0 ("Versioning & cosign verification") after the Overview block

```yaml
### 0. Versioning & cosign verification (v1.84.0+)

Starting with v1.84.0 LiteLLM follows PEP 440. The `-stable` suffix is gone.
Both `litellm:1.90.0` and `litellm:v1.90.0` resolve to the same image.
All Docker images are cosign-signed with the key from commit `0112e53`:

```bash
cosign verify --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub ghcr.io/berriai/litellm:v1.90.0
```
```

## Hunk 3 — Replace "Load Balancing" routing-strategy enumeration

```diff
 router = Router(
     model_list=[...],
-    routing_strategy="least-busy"  # or "round-robin", "latency-based-routing"
+    routing_strategy="simple-shuffle",   # 👈 RECOMMENDED in v1.90
+    enable_pre_call_checks=True,
 )
-
-# Available strategies:
-# - "round-robin"   ← removed in v1.85
-# - "least-busy"
-# - "usage-based-routing"  ← replaced by "usage-based-routing-v2"
-# - "latency-based-routing"
+# Available strategies (v1.90):
+# - simple-shuffle (default - best raw performance)
+# - least-busy
+# - usage-based-routing-v2 (async, Redis-backed)
+# - latency-based-routing
+# - cost-based-routing via custom routing strategy
```

## Hunk 4 — Insert "Section 7b. Per-model routing groups (v1.84.0+)" right before "### 8. Cost Tracking"

```yaml
### 7b. Per-model routing groups (v1.84.0+)

```yaml
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
```

## Hunk 5 — Update `general_settings.master_key` and remove `user_settings`

```diff
 general_settings:
   master_key: sk-your-master-key
+  # v1.84.0+: master-key requests propagate the alias
+  # "litellm_proxy_master_key" downstream; _is_master_key rejects hash form.
   database_url: postgresql://user:pass@localhost/litellm
+  alerting: ["slack"]                  # requires SLACK_WEBHOOK_URL

 litellm_settings:
   max_budget: 100  # $100 max
   budget_duration: 1d  # per day
-user_settings:
-  - user_id: team-a
-    max_budget: 100
-    budget_duration: 1d
-  - user_id: team-b
-    max_budget: 200
-    budget_duration: 1d
+# Budgets now live on per-member rows; max_budget=NULL falls through to
+# team-level enforcement (v1.84.0 onwards). `user_settings` is removed.
+  num_retries: 3         # coordinated with v1.84+ budget reservation
```

## Hunk 6 — Update "Docker Deployment" section

```diff
 services:
   litellm:
-    image: ghcr.io/berriai/litellm:main-latest
+    # All images are cosign-signed with key from commit 0112e53; both
+    # `litellm:1.84.0` and `litellm:v1.84.0` resolve to the same image.
+    image: ghcr.io/berriai/litellm:v1.90.0
     ports:
       - "4000:4000"
```

## Hunk 7 — Append "Recent additions (post 2025-01)" at end of file

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
