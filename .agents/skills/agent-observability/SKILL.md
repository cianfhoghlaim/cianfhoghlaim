---
name: agent-observability
description: Unified agent observability stack — Datadog APM + LLMObs (`@llm`, `@agent`, `@workflow`, `@task`), MLflow experiment tracking + model registry, Langfuse cost + prompt management, Ragas evaluation as a Dagster asset_check, structlog. Use when wiring traces, costs, RAG quality, and experiments across the KCG agent layer.
---

# Agent Observability

## When to use this skill

Use when you need to:

- "Trace every LLM call with input + output + token count"
- "Track experiment runs (RAGAS scores, hyperparams) in MLflow"
- "Monitor cost per agent invocation (USD) in Langfuse"
- "Add a RAGAS quality gate to a Dagster asset (asset_check)"
- "Wire Datadog APM + LLMObs for full-stack tracing"
- "Set up structured JSON logging in production"

## Overview

The KCG agent observability stack is **5 layers**, all wired
together. Each layer covers a different concern:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Traces (Datadog APM + LLMObs)                     │
│  → FastAPI TraceMiddleware, ddtrace.llmobs.decorators      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Experiments (MLflow)                              │
│  → Run tracking, model registry, artifact logging            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Cost + prompt management (Langfuse)               │
│  → Per-invocation cost, prompt versioning, eval              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: RAG quality (Ragas)                                │
│  → faithfulness, answer-relevancy, ctx precision/recall     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Structured logging (structlog)                    │
│  → JSON for prod, console for dev                            │
└─────────────────────────────────────────────────────────────┘
```

## 1. Datadog APM + LLMObs

```python
import ddtrace
from ddtrace.llmobs.decorators import agent, llm, workflow, task


@workflow(name="kcg_curriculum_search")
def curriculum_search(query: str) -> list[dict]:
    """Top-level workflow — emitted as a Datadog workflow span."""
    results = vector_search(query)
    ranked = rerank_with_bge_m3(results)
    return format_response(ranked)


@agent(name="bge_m3_embedder")
def bge_m3_embed(text: str) -> list[float]:
    return embed_bge_m3(text)


@llm(name="gpt4o_mini", model_provider="openai", model_name="gpt-4o-mini")
def llm_call(prompt: str) -> str:
    return openai_client.chat(prompt)


@task(name="vector_search")
def vector_search(query: str) -> list[dict]:
    return lance_search(query, top_k=10)
```

**FastAPI integration**:

```python
from ddtrace.contrib.fastapi import TraceMiddleware
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(TraceMiddleware, service="kcg-api")
```

`@llm` automatically captures:
- model name + provider
- input + output
- token counts (prompt + completion)
- cost (USD)
- latency

## 2. MLflow experiment tracking + model registry

```python
import mlflow

mlflow.set_tracking_uri("https://mlflow.cianfhoghlaim.ie")
mlflow.set_experiment("kcg-rag-pipeline")


@mlflow.trace
def run_rag_experiment(query: str) -> dict:
    """Each invocation is a trace; param + metric logs go to MLflow."""
    mlflow.log_param("embedding_model", "BAAI/bge-m3")
    mlflow.log_param("reranker", "bge-reranker-v2-m3")
    mlflow.log_metric("faithfulness", 0.94)
    mlflow.log_metric("answer_relevancy", 0.89)
    return {"results": [...]}
```

**Model registry**:

```python
mlflow.register_model(
    "runs:/abc123/model",
    "kcg-bge-m3-v3",
)
```

## 3. Langfuse cost + prompt management

```python
from langfuse.decorators import observe, langfuse_context


@observe(as_type="generation")
def llm_call(prompt: str) -> str:
    response = openai_client.chat(prompt)
    # Langfuse automatically tracks cost + token usage
    langfuse_context.update_current_observation(
        model="gpt-4o-mini",
        usage_details={"input": 150, "output": 75},
    )
    return response
```

**Prompt versioning**:

```python
from langfuse import Langfuse

langfuse = Langfuse()
prompt = langfuse.get_prompt("kcg_system_prompt", label="production")
response = openai_client.chat(prompt.compile(variables={"query": query}))
```

## 4. Ragas evaluation (Dagster asset_check)

```python
from dagster import asset_check, AssetCheckResult, AssetCheckSeverity
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy


@asset_check(asset=rag_asset, blocking=True)
def rag_quality_check(context, rag_asset):
    """Run Ragas on the latest 100 samples; gate on faithfulness."""
    samples = load_eval_samples(limit=100)
    scores = evaluate(samples, metrics=[faithfulness, answer_relevancy])
    f = scores["faithfulness"]
    r = scores["answer_relevancy"]
    return AssetCheckResult(
        passed=f >= 0.8 and r >= 0.7,
        severity=AssetCheckSeverity.ERROR if (f < 0.8 or r < 0.7) else AssetCheckSeverity.WARN,
        metadata={
            "faithfulness": f,
            "answer_relevancy": r,
            "n_samples": len(samples),
        },
    )
```

**KCG thresholds**: faithfulness ≥ 0.8, answer-relevancy ≥ 0.7.

## 5. Structured logging with structlog

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),  # JSON for prod
    ],
)

log = structlog.get_logger()
log.info("rag_query", query=query, n_results=10, latency_ms=42)
```

Output:

```json
{"event": "rag_query", "level": "info", "timestamp": "2026-04-15T12:34:56Z", "query": "...", "n_results": 10, "latency_ms": 42}
```

## Observability checklist

For every new agent in the KCG stack, ensure:

- [ ] Every LLM call is wrapped in `@llm` (Datadog LLMObs) or
  `@observe` (Langfuse)
- [ ] Every agent is wrapped in `@agent` for cost tracking
- [ ] Every workflow is wrapped in `@workflow` for end-to-end
  tracing
- [ ] Every task is wrapped in `@task` for step-level timing
- [ ] RAGAS quality gate (asset_check) for any RAG asset
- [ ] MLflow experiment for any model retraining
- [ ] structlog JSON logging in production

## KCG integration

- `oideachais/observability/` — the integration module
  (Datadog + MLflow + Langfuse + Ragas)
- `meaisinfhoghlaim/evaluation/` — the Ragas evaluation harness
- `meaisinfhoghlaim/evaluation/canonical_eval_set.json` —
  100 samples × 4 metrics
- Dagster assets: `oideachais/dagster_defs/assets/quality_assets.py`
  (the Ragas asset_check group)

## Related skills

- `.agents/skills/langfuse/SKILL.md` — LLM tracing +
  cost + prompt management
- `.agents/skills/mlflow/SKILL.md` — experiment tracking +
  model registry
- `.agents/skills/ragas/SKILL.md` — RAG evaluation
- `.agents/skills/dagster/SKILL.md` — Dagster asset_check
  integration
- `.agents/skills/datadog/SKILL.md` — Datadog APM (upstream
  reference)
