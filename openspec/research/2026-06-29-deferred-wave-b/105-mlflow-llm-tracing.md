# 105 - MLflow LLM Tracing (deferred site)

**Status:** Researched 2026-06-29 via firecrawl MCP
**Canonical source:** https://mlflow.org/docs/latest/genai/tracing/
**Cianfhoghlaim footprint:** MLflow used in 2 of the 12 meaisinfhoghlaim
agents (per the agent-13-dragonfly.md) and 1 langfuse+mlflow+RAGAS
stack (per .agents/skills/agent-observability/SKILL.md).

## TL;DR

MLflow Tracing is the **fully OpenTelemetry-compatible** LLM
observability solution for cianfhoghlaim agents. The 3 features we
use most:

1. **One-line auto tracing** — `mlflow.openai.autolog()` enables
   OpenTelemetry trace capture for all OpenAI calls
2. **Manual tracing with `@mlflow.trace`** — for custom function
   instrumentation
3. **Production Tracing SDK** — `mlflow-tracing` package is 95%
   smaller than full `mlflow`, optimized for production

**The 6 use cases** (per the canonical docs):
- Build & Debug
- Human Feedback
- Evaluation
- Production Monitoring
- Dataset Collection
- Framework-agnostic (works with OpenAI, LangChain, LlamaIndex, DSPy, Pydantic AI)

## Code

The cianfhoghlaim pattern (per the agent-13-dragonfly.md):

```python
import mlflow

# 1. One-line autolog for OpenAI
mlflow.openai.autolog()

# 2. Manual tracing for BAML callables
@mlflow.trace
async def classify_email_thread(thread_id: str):
    result = await b.ClassifyEmailThread(thread_id)
    return result

# 3. Production SDK for lightweight prod
# requirements-prod.txt: mlflow-tracing==3.14.0
```

## Env

- `MLFLOW_TRACKING_URI` — set in `.infisical.env` to the
  canonical MLflow server (per .agents/skills/agent-observability/SKILL.md)
- `MLFLOW_EXPERIMENT_NAME` — defaults to `cianfhoghlaim`

## ccc anchors

- `mlflow` skill at `.agents/skills/mlflow/SKILL.md` (v3.14+ patterns)
- `agent-observability` skill at `.agents/skills/agent-observability/SKILL.md`
  (Langfuse + MLflow + RAGAS stack)
- `dagster` skill (Dagster asset checks can call MLflow API)

## Anti-patterns

- **Sending trace data to SaaS** — MLflow is open-source and 100% free;
  host it on our own infrastructure
- **Using full `mlflow` package in production** — use `mlflow-tracing`
  instead (95% smaller footprint)
- **Synchronous trace logging** in hot paths — use async logging to
  avoid performance impact
- **Mixing MLflow v2 callback + Langfuse v3 OTEL** — MLflow is
  OTEL-native, so use OTEL collector + MLflow receiver (don't use
  the deprecated v2 callback)

## Decision matrix

| Use MLflow Tracing when | Use Langfuse when | Use Logfire when |
|:--|:--|:--|
| GenAI semantic conventions | Multi-tenant SaaS observability | Pydantic-native apps |
| OpenTelemetry compatibility | Prompt management + A/B testing | Structured logging |
| Free self-hosted | LLM cost tracking | Dev-time debug |
| Framework-agnostic | 100+ LLMs/agents | Python-only |

The cianfhoghlaim stack uses **both** MLflow + Langfuse in parallel
(via the OTEL collector fan-out) per the agent-observability skill.
