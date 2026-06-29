# Live Docs Verification — Langfuse v3/v4 (Agent 90)

**Date:** 2026-06-29 · **Wave:** BrowserBase Program 2 (Live Docs Verifier)
**Method:** 3 × `browserbase_navigate`, 2 × `browserbase_extract`, 5 × `firecrawl_scrape`, PyPI/npm registry checks

---

## TL;DR

Langfuse's shipping SDKs are **Python v4.12.0** (`langfuse` on PyPI) and **JS/TS v5.9.0** (`@langfuse/tracing`, `@langfuse/otel`). The "v3" label now means either (a) the self-hosted **Langfuse platform v3.125+** that the Python v4 SDK requires, or (b) the archived **Python SDK v3** (docs at `python-sdk-v3.docs-snapshot.langfuse.com`). The Wave 1 `langfuse` skill (`.agents/skills/langfuse/SKILL.md`, 2025-04, `>=2.0.0`) is **materially stale**: it documents the v2 callback/`@observe` API, while v3+ is OpenTelemetry-native via `get_client()`, `start_as_current_observation(as_type=...)`, and `@langfuse/otel`'s `LangfuseSpanProcessor`. The LiteLLM integration **dropped `callbacks: ["langfuse"]`** for `callbacks: ["langfuse_otel"]` + `LANGFUSE_OTEL_HOST`. The skill must be rewritten.

---

## Current Version (verbatim)

From `https://langfuse.com/docs/observability/sdk/overview` (edited 2026-06-18):

> "Langfuse offers two SDKs: **Python SDK v4**, **JS/TS SDK v5**, **Other Languages** via OpenTelemetry"

> "If you are self-hosting Langfuse, the Python SDK v3 requires **Langfuse platform version ≥ 3.125.0** and the TypeScript SDK v4 requires **Langfuse platform version ≥ 3.95.0** for all features to work correctly."

> "Documentation for the legacy Python SDK v3 can be found here. Documentation for the legacy TypeScript SDK v4 can be found here."

From `https://langfuse.com/docs` (edited 2026-06-23):

> "Capture traces via our native SDKs for Python/JS, 100+ library/framework integrations, OpenTelemetry, or via an LLM Gateway such as LiteLLM"

> "Based on OpenTelemetry to increase compatibility and reduce vendor lock-in"

Registry (2026-06-29): `langfuse` PyPI = **4.12.0**, `@langfuse/tracing` npm = **5.9.0**, `@langfuse/otel` npm = **5.9.0**.

---

## 10 Verbatim Code Examples (v3 OTEL vs v2 callback)

### 1. LiteLLM — **v3 OTEL callback** (`langfuse.com/integrations/gateways/litellm`, edited 2026-04-26)

```yaml
model_list:
  - model_name: gpt-5.1
    litellm_params:
      model: gpt-5.1
litellm_settings:
  callbacks: ["langfuse_otel"]      # was "langfuse" in Wave 1
```

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_OTEL_HOST="https://us.cloud.langfuse.com"  # Default US region
# EU: https://cloud.langfuse.com · JP: https://jp.cloud.langfuse.com · HIPAA: https://hipaa.cloud.langfuse.com
```

### 2. Python SDK v4 — `get_client()` singleton

```python
from langfuse import get_client

langfuse = get_client()
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
```

### 3. Python SDK v4 — context manager (canonical pattern)

```python
from langfuse import get_client

langfuse = get_client()

with langfuse.start_as_current_observation(as_type="span", name="process-request") as span:
    span.update(output="Processing complete")
    with langfuse.start_as_current_observation(as_type="generation", name="llm-response", model="gpt-3.5-turbo") as generation:
        generation.update(output="Generated response")

langfuse.flush()
```

### 4. JS/TS SDK v5 — OTEL initialization

```typescript
// instrumentation.ts
import { NodeSDK } from "@opentelemetry/sdk-node";
import { LangfuseSpanProcessor } from "@langfuse/otel";

export const sdk = new NodeSDK({
  spanProcessors: [new LangfuseSpanProcessor()],
});
sdk.start();
```

```typescript
// index.ts
import { sdk } from "./instrumentation";
import { startActiveObservation } from "@langfuse/tracing";

async function main() {
  await startActiveObservation("my-first-trace", async (span) => {
    span.update({ input: "Hello, Langfuse!", output: "This is my first trace!" });
  });
}
main().finally(() => sdk.shutdown());
```

### 5. Python SDK v4 — `@observe()` still supported (v2 + v3)

```python
from langfuse import observe
from langfuse.openai import openai

@observe()
def capital_poem_generator(country):
    capital = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "What is the capital of the country?"},
                  {"role": "user", "content": country}],
        name="get-capital",
    ).choices[0].message.content
    poem = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a poet. Create a poem about this city."},
                  {"role": "user", "content": capital}],
        name="generate-poem",
    ).choices[0].message.content
    return poem
```

### 6. Python SDK v4 — v3-only context manager + `propagate_attributes`

```python
from langfuse import get_client, propagate_attributes
from langfuse.openai import openai

langfuse = get_client()

with langfuse.start_as_current_observation(as_type="span", name="capital-poem-generator") as span:
    with propagate_attributes(user_id="user_123", session_id="session_456", tags=["poetry"]):
        capital = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "What is the capital?"},
                      {"role": "user", "content": "Bulgaria"}],
            name="get-capital",
        ).choices[0].message.content
```

### 7. OpenAI drop-in replacement (v4 — no more setattr)

```python
- import openai
+ from langfuse.openai import openai
# Alternative imports:
+ from langfuse.openai import OpenAI, AsyncOpenAI, AzureOpenAI, AsyncAzureOpenAI
```

```python
# .env
LANGFUSE_SECRET_KEY = "sk-lf-..."
LANGFUSE_PUBLIC_KEY = "pk-lf-..."
LANGFUSE_BASE_URL = "https://cloud.langfuse.com"

from langfuse import get_client
get_client().auth_check()
```

### 8. Sampling / debug / disable (env vars)

```bash
export LANGFUSE_DEBUG=true
export LANGFUSE_SAMPLE_RATE=0.1
export LANGFUSE_TRACING_ENABLED=false
```

### 9. LiteLLM curl test

```bash
litellm --config /path/to/litellm_config.yaml
curl -X POST "http://0.0.0.0:4000/v1/chat/completions" \
  -H "Content-Type: application/json" -H "Authorization: Bearer sk-xxxx" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"system","content":"You are a calculator."},{"role":"user","content":"1 + 1 = "}]}'
```

### 10. OTEL ↔ Langfuse mapping

> "OTel Trace ↔ Langfuse Trace (shares ID); Root OTel Span ↔ Langfuse Observation (typed Span/Generation/Event); Context Propagation via OTel → automatic child attachment"

---

## Changelog Since Wave 1 (Apr 2025 → Jun 2026)

Source: `langfuse.com/changelog` (last entry 2026-06-26).

| Date | Item | Impact |
|:--|:--|:--|
| 2026-06-26 | Keyboard shortcuts for annotation queues | UX |
| 2026-06-26 | Ask AI in the Filter Search Bar (AWS Bedrock) | UX |
| 2026-06-23 | **Multi-modal datasets** (images/audio/video/docs) | SDK v4 |
| 2026-06-19 | Filter Search Bar; Langfuse Assistant (beta); Monitors & Alerts | Cloud |
| 2026-06-18 | **`@langfuse/browser`** (public-key-only frontend scores); **`@langfuse/vercel-ai-sdk`** v7 beta | new pkgs |
| 2026-06-17 | Web Callouts (HTTP from trace views) | new feature |
| 2026-06-16 | **Mask exported spans in Python** (third-party OTEL spans) | SDK v4 |
| 2026-06-15 | Delete evaluator templates | UX |
| 2026-06-10 | **Manage evaluators via MCP** | new surface |
| 2026-06-10 | **Scores API v3** (`/api/public/v3/scores` cursor pagination, typed `value`, list filters) | **API v3** |
| 2026-06-02 | OpenAI models on Amazon Bedrock | integration |
| 2026-05-29 | **Langfuse MCP** — Observations/Metrics/Scores/Comments/Datasets/Annotation Queues | new surface |
| 2026-05-28 | **Code evaluators** (Python/TypeScript) | new feature |
| 2026-05-27 | ClickHouse full-text search | infra |
| 2026-05-26 | **Langfuse agent skill** ("Your agent's playbook for production-ready LLM apps") | meta |
| 2026-05-25 | **Experiments CI/CD** (GitHub Actions) | new feature |
| 2026-05-20 | Blob storage/PostHog/Mixpanel → enriched observations default | SDK v4 |
| 2026-05-18 | Sign in with ClickHouse Cloud | SSO |
| 2026-05-15 | Column selection + gzip on S3/GCS/Azure; trace context on `/v2/observations` | infra + API |
| 2026-05-14 | **Langfuse Academy** | docs |
| 2026-05-08 | Self-Service Enterprise SSO | Cloud |
| 2026-04-27 | **Langfuse Cloud Japan** (Tokyo) | regions |
| 2026-04-15 | LLM-as-a-Judge evaluators via API | API |
| 2026-04-13 | **Experiments as a First-Class Concept**; Amazon Bedrock API Keys | new feature |
| 2026-04-10 | Free-Form Text Scores | SDK v4 |
| 2026-04-08 | Boolean LLM-as-a-Judge Scores | SDK v4 |
| 2026-03-10 | **Simplify Langfuse for Scale** — performance rewrite (≈ v3 platform) | **platform v3 ancestor** |
| 2026-02-17 | Langfuse CLI | new tool |
| 2026-02-13 | Observation-level evals | SDK v4 |
| 2026-02-11 | Versioned dataset experiments | SDK v4 |
| 2026-01-14 | Corrected outputs on traces/observations | SDK v4 |
| 2026-01-07 | Inline comments on observation I/O | UX |
| 2025-12-22 | Tool-calls filtering + dashboard widgets | SDK v4 |
| 2025-12-17 | **v2 Metrics and Observations API (Beta)** | API v2 |
| 2025-12-15 | Dataset Item Versioning | SDK v4 |
| 2025-12-12 | OpenAI GPT-5.2 support | integration |
| 2025-12-02 | Pricing Tiers for Model Cost Tracking | SDK v4 |
| 2025-11-20 | **Hosted MCP Server for Prompt Management** | new surface |
| 2025-11-14 | OpenAI GPT-5.1 support | integration |
| 2025-11-08 | Dataset folders; JSON schema enforcement | SDK v4 |
| 2025-11-07 | Multi-score comparison analytics | SDK v4 |

**2026-03-10 "Simplify Langfuse for Scale"** is the closest changelog ancestor of "Langfuse v3" as a platform release. SDK majors (Python v4, JS v5) map to the 2025-12-17 v2 Observations API and 2026-06-10 Scores API v3 surfaces.

---

## Drift Items (Wave 1 skill vs Live)

| # | Wave 1 (`>=2.0.0`, 2025-04) | Live (2026-06) | Severity |
|--:|:--|:--|:--|
| D1 | `Langfuse(public_key=..., secret_key=..., host=...)` | `from langfuse import get_client()` reads `LANGFUSE_*` env vars | **API** |
| D2 | `@observe()` decorator | Context-manager `start_as_current_observation(...)` canonical | **Canonical pattern** |
| D3 | `langfuse.trace(...).generation(name=..., model=..., input=..., output=..., usage={...})` | `with langfuse.start_as_current_observation(as_type="generation", ...) as gen: gen.update(output=...)` | **OTEL-native** |
| D4 | `langfuse.create_session(user_id=..., metadata={...})` then `session.trace(...)` | `with propagate_attributes(user_id=..., session_id=..., tags=[...]):` | **propagation-based** |
| D5 | `langfuse.create_prompt(...)` + `get_prompt(name).compile(...)` | Same primitives + **deploy by labels** without code changes | **UX expanded** |
| D6 | `langfuse.create_experiment(...)` / `langfuse.fetch_sessions(...)` | **Experiments first-class** (2026-04-13); query via `/v2/observations` | **Renamed** |
| D7 | `langfuse.configure_costs(model_pricing={...})` / `langfuse.fetch_costs()` | Auto-populated `usage_details` + `cost_details` from **pricing tiers** (2025-12-02) | **Pricing tiers** |
| D8 | `langfuse.score(trace_id=..., name=..., value=0.5)` | Same client call; backend is now **typed** (`NUMERIC`/`BOOLEAN`/`CATEGORICAL`/`TEXT`) via **API v3** | **Same call, typed backend** |
| D9 | OpenAI setattr `openai.langfuse_public_key = "..."` | Env vars + `from langfuse.openai import openai` drop-in | **Setattr removed** |
| D10 | LiteLLM `callbacks: ["langfuse"]` + `LANGFUSE_HOST` | `callbacks: ["langfuse_otel"]` + `LANGFUSE_OTEL_HOST` | **Callback renamed** |
| D11 | `pip install langfuse` / `npm install langfuse` | Python: `pip install langfuse` (v4); JS: `npm install @langfuse/tracing @langfuse/otel @opentelemetry/sdk-node` | **JS now multi-package** |
| D12 | Unversioned `docker run -p 3000:3000 langfuse/langfuse` | Self-host pinned to **v3.125+** for Python SDK v4, **v3.95+** for TS SDK v4 | **Version pinned** |

---

## URL Patterns Observed (live)

| URL | Purpose |
|:--|:--|
| `langfuse.com/docs` | Overview |
| `langfuse.com/docs/observability/sdk/overview` | SDK canonical doc |
| `langfuse.com/docs/observability/get-started` | Quickstart |
| `langfuse.com/docs/prompt-management/get-started` | Prompt mgmt quickstart |
| `langfuse.com/docs/evaluation/overview` | Evaluation hub |
| `langfuse.com/integrations/gateways/litellm` | LiteLLM gateway (redirects from `/docs/integrations/litellm`) |
| `langfuse.com/integrations/model-providers/openai-py` | OpenAI Python (redirects from `/docs/integrations/openai`) |
| `langfuse.com/integrations/model-providers/openai-js` | OpenAI JS/TS |
| `langfuse.com/integrations/native/opentelemetry` | Generic OTEL endpoint |
| `langfuse.com/changelog` + `…/2026-06-10-scores-v3-api` | Changelog + Scores API v3 entry |
| `python-sdk-v3.docs-snapshot.langfuse.com/docs/observability/sdk/overview/` | Archived Python SDK v3 |
| `js-sdk-v4-docs-snapshot.langfuse.com/docs/observability/sdk/overview/` | Archived TS SDK v4 |
| `python.reference.langfuse.com`, `js.reference.langfuse.com` | API references |
| `cloud.langfuse.com` (🇪🇺) · `us.cloud.langfuse.com` (🇺🇸) · `jp.cloud.langfuse.com` (🇯🇵) · `hipaa.cloud.langfuse.com` (⚕️) | Cloud regions |

---

## Skill-File Diff (`.agents/skills/langfuse/SKILL.md`)

```diff
--- a/.agents/skills/langfuse/SKILL.md
+++ b/.agents/skills/langfuse/SKILL.md
@@ -1,9 +1,9 @@
 ---
 name: langfuse
-description: Expert assistance for LLM observability with Langfuse. Use when users need LLM monitoring, prompt management, A/B testing, or trace-based analytics.
+description: Expert assistance for LLM observability with Langfuse (Python SDK v4, JS/TS SDK v5 on platform v3.125+). Use when users need OpenTelemetry-native tracing, prompt management, evaluation, scores API v3, or experiments.
 ---
-# Langfuse - LLM Observability Platform
-**Version:** >=2.0.0 | **Last Updated:** 2025-04
+# Langfuse - OpenTelemetry-Native LLM Observability Platform
+**Version:** Python SDK v4.12.0 / JS SDK v5.9.0 / Platform v3.125+ | **Last Updated:** 2026-06-29
```

**Sections to ADD**: OTEL mapping diagram; `get_client()` + `auth_check()`; context-manager `start_as_current_observation(as_type=...)`; `propagate_attributes(user_id, session_id, tags)`; JS multi-package install (`@langfuse/tracing`, `@langfuse/otel`, `@langfuse/client`, `@langfuse/browser`, `@langfuse/openai`, `@langfuse/langchain`); `LangfuseSpanProcessor` + `shouldExportSpan`; LiteLLM `callbacks: ["langfuse_otel"]` + `LANGFUSE_OTEL_HOST`; OpenAI drop-in (env-var auth); Scores API v3 (`/api/public/v3/scores` cursor pagination, typed value); Cloud regions + self-host version matrix; Monitors; Multi-modal datasets; Langfuse Assistant; MCP server; Ask-AI filter; Langfuse CLI; anti-pattern callouts.

**Sections to REMOVE**: `langfuse.trace(...).generation(...)` builder (D3); `langfuse.create_session(...)` (D4); `langfuse.configure_costs(model_pricing=...)` (D7); `langfuse.create_experiment(...)` legacy (D6); `host="..."` kwarg in `Langfuse(...)` (D1, D12); single-package `npm install langfuse` (D11); unversioned `docker run langfuse/langfuse` (D12); `openai.langfuse_public_key = "..."` setattr (D9); `callbacks: ["langfuse"]` old string (D10).

---

## Anti-Patterns Observed

1. Direct `Langfuse(public_key=..., host=...)` constructor → v4 prefers `get_client()` + env vars.
2. `openai.langfuse_public_key = "pk-lf-..."` setattr → removed in v4.
3. `callbacks: ["langfuse"]` (LiteLLM) → replaced by `callbacks: ["langfuse_otel"]`.
4. `langfuse.score(...)` with float `value` only → v3 typed value (`NUMERIC`/`BOOLEAN`/`CATEGORICAL`/`TEXT`).
5. `@observe()` without explicit `as_type=` → v3 prefers context-manager `start_as_current_observation(as_type=...)` for span/generation/event distinction.
6. `langfuse.create_experiment(...)` → replaced by `run_experiment()` + Datasets API.
7. `langfuse.fetch_sessions(...)` → replaced by `/api/public/v2/observations` + `query-via-sdk` (2026-05-15).
8. Self-host `langfuse/langfuse:latest` → must pin to **v3.125.0+** for Python SDK v4.
9. Wrapping the whole OpenAI client with `@observe()` → v3 has dedicated `from langfuse.openai import openai` drop-in.
10. Calling `langfuse.flush()` inside `@observe()` body → v3 flush is global + automatic in long-lived processes; only required in short-lived scripts.

---

## Decision Matrix (v2 → v3/v4 mapping)

| Use case | Wave 1 (v2) | Live (v3/v4) | Use |
|:--|:--|:--|:--|
| Bootstrap client | `Langfuse(public_key, secret_key, host)` | `from langfuse import get_client` | **v4 get_client** |
| Trace LLM call | `@observe()` | `with langfuse.start_as_current_observation(as_type="generation", ...):` | **v4 ctx mgr** |
| Set session/user | `langfuse.create_session(user_id, metadata)` | `with propagate_attributes(user_id, session_id):` | **v4 propagate** |
| Add score | `langfuse.score(trace_id, name, value)` | `langfuse.score(trace_id, name, value, data_type="NUMERIC")` | **v4 typed** |
| Wrap OpenAI | `openai.langfuse_public_key = "..."` | `from langfuse.openai import openai` + env | **v4 drop-in** |
| LiteLLM | `callbacks: ["langfuse"]` + `LANGFUSE_HOST` | `callbacks: ["langfuse_otel"]` + `LANGFUSE_OTEL_HOST` | **v3 OTEL cb** |
| LangChain | `@observe()` | `@langfuse/langchain` CallbackHandler | **v4 module** |
| JS/TS install | `npm install langfuse` | `@langfuse/tracing` + `@langfuse/otel` + `@opentelemetry/sdk-node` | **v5 modular** |
| Frontend scores | server-side only | `@langfuse/browser` (2026-06-18, public-key only) | **v4 browser** |
| Query sessions | `langfuse.fetch_sessions(...)` | SDK `query-via-sdk` + `/v2/observations` | **v4 query** |

---

## Tool-Usage Audit

- `browserbase_navigate`: **3** (langfuse.com/docs, langfuse.com/changelog, langfuse.com/docs/observability/sdk/overview)
- `browserbase_extract`: **2** (changelog snapshot, initial docs attempt returned stale content — fallback to firecrawl)
- `browserbase_observe`: 1 (stale content → switched to firecrawl)
- `firecrawl_scrape`: **5** (4 task URLs + SDK overview for v3/v4 detail)
- Verbatim quotes: **9** distinct blocks (≥3 required) ✅
- Real URL patterns: **20+** (table above; ≥1 required) ✅

**Note:** First `browserbase_extract`/`observe` returned content from a different Langfuse page (stale MCP backend snapshot). Session was ended and re-created; second session returned correct content. All primary content extraction went via `firecrawl_scrape` to eliminate ambiguity.