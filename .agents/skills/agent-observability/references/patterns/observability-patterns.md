---
domain: standards
title: Observability Patterns
description: Comprehensive observability patterns for the Cianfhoghlaim platform — Datadog APM, Datadog LLMObs, MLflow experiment tracking, Langfuse LLM cost tracking, Ragas RAG evaluation, and structured logging with structlog.
updated: 2026-06-06
merged_from:
  - docs/context/01-patterns/OBSERVABILITY.md
ccc_query_hints:
  - observability monitoring patterns
  - datadog llmobs tracing
  - mlflow experiment tracking model registry
  - langfuse cost tracking prompt management
  - ragas rag evaluation metrics
---

# Observability Patterns

## Table of Contents

1. [Observability Stack](#observability-stack)
2. [Datadog Patterns](#datadog-patterns)
3. [MLflow Patterns](#mlflow-patterns)
4. [Langfuse Patterns](#langfuse-patterns)
5. [Ragas Patterns](#ragas-patterns)
6. [Structured Logging](#structured-logging)
7. [Integration Points](#integration-points)
8. [Observability Checklist](#observability-checklist)

---

## Observability Stack

```
Application Layer
        |
├── Datadog APM (Request tracing, metrics)
├── Datadog LLMObs (LLM-specific tracing)
├── MLflow (Experiment tracking, model registry)
├── Langfuse (LLM cost tracking, prompt management)
└── Ragas (RAG evaluation metrics)
        |
Storage & Visualization
```

### Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **Trace all LLM calls** | Every LLM invocation must be traced | No cost visibility, debugging blind |
| **Track embeddings** | Log embedding operations | Performance issues undetected |
| **Evaluate RAG quality** | Use Ragas metrics | Silent retrieval degradation |
| **Experiment tracking** | Version all model configs | No reproducibility |

---

## Datadog Patterns

### Pattern 1: FastAPI Middleware

```python
from fastapi import FastAPI
from ddtrace import patch_all, tracer
from ddtrace.contrib.fastapi import TraceMiddleware

patch_all()

os.environ.setdefault("DD_SERVICE", "cianfhoghlaim-api")
os.environ.setdefault("DD_ENV", "production")
os.environ.setdefault("DD_VERSION", "1.0.0")

app = FastAPI()
app.add_middleware(TraceMiddleware, service_name="cianfhoghlaim-api")

@app.get("/api/search")
async def search(query: str):
    with tracer.trace("search.execute", service="search"):
        results = await execute_search(query)
    return results
```

### Pattern 2: LLM Observability Decorator

```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm, agent, workflow

LLMObs.enable(
    ml_app="cianfhoghlaim",
    api_key=os.getenv("DD_API_KEY"),
    site="datadoghq.eu",
    agentless_enabled=True,
)

@llm(model_name="gemini-2.0-flash", model_provider="google")
async def generate_response(prompt: str) -> str:
    response = await llm_client.generate(prompt)
    return response.text

@agent(agent_name="curriculum_agent")
async def curriculum_search(query: str) -> dict:
    results = await search_curriculum(query)
    response = await generate_response(
        f"Answer based on: {results}\n\nQuery: {query}"
    )
    return {"query": query, "response": response, "sources": results}

@workflow(workflow_name="full_pipeline")
async def process_document(doc: dict) -> dict:
    extracted = await extract_content(doc)
    embedded = await embed_content(extracted)
    stored = await store_content(embedded)
    return stored
```

### Pattern 3: Custom Agent Tracing Decorator

```python
def trace_adk_agent(agent_name: str):
    """Decorator for tracing Google ADK agent calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            with tracer.trace(
                f"agent.{agent_name}",
                service="cianfhoghlaim-agents",
                resource=func.__name__,
            ) as span:
                span.set_tag("agent.name", agent_name)
                span.set_tag("agent.type", "google_adk")
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    span.set_tag("agent.duration_ms", int(duration * 1000))
                    span.set_tag("agent.status", "success")
                    LLMObs.annotate(
                        span=span,
                        input_data=str(kwargs.get("query", args[0] if args else "")),
                        output_data=str(result)[:1000],
                    )
                    return result
                except Exception as e:
                    span.set_tag("agent.status", "error")
                    span.set_tag("agent.error", str(e))
                    raise
        return wrapper
    return decorator
```

---

## MLflow Patterns

### Pattern 4: Experiment Tracking

```python
import mlflow

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("curriculum-embedding")

def train_embedding_model(config: dict):
    with mlflow.start_run(run_name=f"embedding-{config['model_name']}"):
        mlflow.log_params({
            "model_name": config["model_name"],
            "batch_size": config["batch_size"],
            "learning_rate": config["learning_rate"],
            "epochs": config["epochs"],
        })
        for epoch in range(config["epochs"]):
            loss = train_epoch(model, data)
            accuracy = evaluate(model, eval_data)
            mlflow.log_metrics({"train_loss": loss, "eval_accuracy": accuracy}, step=epoch)

        mlflow.pytorch.log_model(model, "model", registered_model_name="curriculum-embedder")
        mlflow.log_artifact("config.yaml")
        mlflow.log_artifact("training_data_summary.json")
```

### Pattern 5: Model Registry

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

def promote_model(model_name: str, version: int, stage: str):
    """Promote model to new stage (Staging, Production, Archived)."""
    client.transition_model_version_stage(name=model_name, version=version, stage=stage)

def load_production_model(model_name: str):
    """Load the production model."""
    model_uri = f"models:/{model_name}/Production"
    return mlflow.pytorch.load_model(model_uri)

model = load_production_model("curriculum-embedder")
embeddings = model.encode(texts)
```

---

## Langfuse Patterns

### Pattern 6: LLM Cost Tracking

```python
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

@observe(as_type="generation")
async def generate_with_tracking(prompt: str, model: str = "gpt-4o") -> str:
    """Generate with automatic cost tracking."""
    # Langfuse automatically tracks: input/output tokens, latency, cost
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    langfuse_context.update_current_observation(
        metadata={"use_case": "curriculum_qa", "language": "en"}
    )
    return response.choices[0].message.content

@observe()
async def rag_pipeline(query: str) -> dict:
    with langfuse_context.observe(name="retrieval"):
        documents = await retrieve_documents(query)
    with langfuse_context.observe(name="generation"):
        response = await generate_with_tracking(
            f"Context: {documents}\n\nQuery: {query}"
        )
    return {"query": query, "response": response, "sources": documents}
```

### Pattern 7: Prompt Management

```python
langfuse = Langfuse()

def get_prompt(name: str, version: int | None = None) -> str:
    """Fetch prompt from Langfuse (latest if version=None)."""
    prompt = langfuse.get_prompt(name=name, version=version, type="text")
    return prompt.compile()

def get_chat_prompt(name: str, variables: dict) -> list:
    prompt = langfuse.get_prompt(name=name, type="chat")
    return prompt.compile(**variables)

# Usage
system_prompt = get_prompt("curriculum_qa_system")
messages = get_chat_prompt("curriculum_qa", {"context": documents, "query": query})
```

---

## Ragas Patterns

### Pattern 8: RAG Evaluation

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

def evaluate_rag(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    dataset = Dataset.from_dict({
        "question": questions, "answer": answers,
        "contexts": contexts, "ground_truth": ground_truths,
    })
    result = evaluate(dataset, metrics=[
        faithfulness,      # Is answer faithful to context?
        answer_relevancy,  # Is answer relevant to question?
        context_precision, # Are retrieved contexts precise?
        context_recall,    # Are all relevant contexts retrieved?
    ])
    return {
        "faithfulness": result["faithfulness"],
        "answer_relevancy": result["answer_relevancy"],
        "context_precision": result["context_precision"],
        "context_recall": result["context_recall"],
    }
```

### Pattern 9: Continuous Evaluation (Dagster Asset)

```python
QUALITY_THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.7,
    "context_precision": 0.75,
    "context_recall": 0.7,
}

@asset
def rag_quality_check(context: AssetExecutionContext):
    test_cases = load_test_cases()
    answers, contexts = [], []
    for q in test_cases["questions"]:
        result = await rag_pipeline(q)
        answers.append(result["response"])
        contexts.append(result["sources"])

    metrics = evaluate_rag(
        questions=test_cases["questions"],
        answers=answers, contexts=contexts,
        ground_truths=test_cases["ground_truths"],
    )

    failures = []
    for metric, threshold in QUALITY_THRESHOLDS.items():
        if metrics[metric] < threshold:
            failures.append(f"{metric}: {metrics[metric]:.2f} < {threshold}")

    if failures:
        context.log.warning(f"Quality check failed: {failures}")
    else:
        context.log.info("Quality check passed")

    return metrics

@asset_check(asset=rag_quality_check)
def check_faithfulness(rag_quality_check):
    return AssetCheckResult(
        passed=rag_quality_check["faithfulness"] >= QUALITY_THRESHOLDS["faithfulness"],
        metadata={"faithfulness": rag_quality_check["faithfulness"]},
    )
```

### Pattern 10: Evaluation in Dagster with MLflow

```python
@asset
def rag_quality_metrics(context, rag_test_data):
    metrics = evaluate_rag(
        questions=rag_test_data["questions"],
        answers=rag_test_data["answers"],
        contexts=rag_test_data["contexts"],
        ground_truths=rag_test_data["ground_truths"],
    )
    # Log to MLflow for tracking over time
    with mlflow.start_run(run_name="rag-eval"):
        mlflow.log_metrics(metrics)
    context.log.info(f"RAG metrics: {metrics}")
    return metrics
```

---

## Structured Logging

### Pattern 11: Structlog Configuration

```python
import structlog
import logging

def configure_logging(service_name: str, env: str):
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    if env == "production":
        processors.append(structlog.processors.JSONRenderer())  # JSON for Datadog
    else:
        processors.append(structlog.dev.ConsoleRenderer())  # Pretty print for dev

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger(service=service_name, env=env)

# Usage
logger = configure_logging("cianfhoghlaim-api", "production")

@app.get("/api/search")
async def search(query: str):
    logger.info("search_started", query=query)
    try:
        results = await execute_search(query)
        logger.info("search_completed", query=query, result_count=len(results),
                     latency_ms=elapsed_ms)
        return results
    except Exception as e:
        logger.error("search_failed", query=query, error=str(e))
        raise
```

---

## Integration Points

| Component | Connects To | Pattern |
|-----------|-------------|---------|
| **Datadog** | FastAPI | Middleware tracing |
| **Datadog LLMObs** | Agents | @llm, @agent decorators |
| **MLflow** | Training | Experiment logging, model registry |
| **Langfuse** | LLM calls | Cost tracking, prompt management |
| **Ragas** | RAG pipeline | Quality metrics |
| **Structlog** | All services | Unified logging to Datadog |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| No LLM cost tracking | Integrate Langfuse for all LLM calls |
| Missing trace context | Use context propagation headers |
| No RAG evaluation | Run Ragas metrics regularly |
| Logs without structure | Use structlog with JSON output |
| No experiment tracking | Log all training runs to MLflow |
| Silent agent failures | Add error tracing to all agents |

---

## Observability Checklist

- [ ] Datadog agent deployed and configured
- [ ] FastAPI middleware enabled
- [ ] LLMObs decorators on all LLM calls
- [ ] MLflow tracking for training
- [ ] Langfuse for cost monitoring
- [ ] Ragas evaluation in CI/CD
- [ ] Structured logging configured
- [ ] Dashboards created for key metrics
- [ ] Alerts configured for quality thresholds
