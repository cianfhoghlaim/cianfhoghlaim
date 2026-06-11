---
title: 'Pattern: Observability (Datadog, MLflow, Langfuse, Ragas)'
domain: 'patterns'
status: 'stable'
description: '| Constraint | Description | Violation Consequence | |------------|-------------|----------------------| | **Trace all LLM calls** | Every LLM invocation must be traced | No cost visibility, debugging blind | | **Track embeddings** | Log embedding operations | Performance issues'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/OBSERVABILITY.md
ccc_query_hints:
  - pattern: observability (datadog, mlflow,
---

# Pattern: Observability (Datadog, MLflow, Langfuse, Ragas)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **Trace all LLM calls** | Every LLM invocation must be traced | No cost visibility, debugging blind |
| **Track embeddings** | Log embedding operations | Performance issues undetected |
| **Evaluate RAG quality** | Use Ragas metrics | Silent retrieval degradation |
| **Experiment tracking** | Version all model configs | No reproducibility |

---

## Observability Stack

```
Application Layer
        ↓
├── Datadog APM (Request tracing, metrics)
├── Datadog LLMObs (LLM-specific tracing)
├── MLflow (Experiment tracking, model registry)
├── Langfuse (LLM cost tracking, prompt management)
└── Ragas (RAG evaluation metrics)
        ↓
Storage & Visualization
```

---

## Datadog Patterns

### Pattern 1: FastAPI Middleware

**When to use**: All FastAPI applications.

**Implementation**:
```python
from fastapi import FastAPI
from ddtrace import patch_all, tracer
from ddtrace.contrib.fastapi import TraceMiddleware
import os

# Patch all supported libraries
patch_all()

# Configure Datadog
os.environ.setdefault("DD_SERVICE", "cianfhoghlaim-api")
os.environ.setdefault("DD_ENV", "production")
os.environ.setdefault("DD_VERSION", "1.0.0")

app = FastAPI()

# Add tracing middleware
app.add_middleware(
    TraceMiddleware,
    service_name="cianfhoghlaim-api",
)

@app.get("/api/search")
async def search(query: str):
    # Automatic tracing via middleware
    with tracer.trace("search.execute", service="search"):
        results = await execute_search(query)
    return results
```

### Pattern 2: LLM Observability Decorator

**When to use**: All agent and LLM operations.

**Implementation**:
```python
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm, agent, workflow, task
from functools import wraps

# Initialize LLMObs
LLMObs.enable(
    ml_app="cianfhoghlaim",
    api_key=os.getenv("DD_API_KEY"),
    site="datadoghq.eu",  # EU site
    agentless_enabled=True,
)

@llm(model_name="gemini-2.0-flash", model_provider="google")
async def generate_response(prompt: str) -> str:
    """LLM call with automatic tracing."""
    response = await llm_client.generate(prompt)
    return response.text

@agent(agent_name="curriculum_agent")
async def curriculum_search(query: str) -> dict:
    """Agent operation with tracing."""
    # Search
    results = await search_curriculum(query)

    # Generate response
    response = await generate_response(
        f"Answer based on: {results}\n\nQuery: {query}"
    )

    return {"query": query, "response": response, "sources": results}

@workflow(workflow_name="full_pipeline")
async def process_document(doc: dict) -> dict:
    """Multi-step workflow with tracing."""
    # Each step is traced
    extracted = await extract_content(doc)
    embedded = await embed_content(extracted)
    stored = await store_content(embedded)
    return stored
```

### Pattern 3: Custom Agent Tracing Decorator

**When to use**: Google ADK agents.

**Implementation**:
```python
from ddtrace import tracer
from ddtrace.llmobs import LLMObs
from functools import wraps
import time

def trace_adk_agent(agent_name: str):
    """Decorator for tracing Google ADK agent calls."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            # Create span
            with tracer.trace(
                f"agent.{agent_name}",
                service="cianfhoghlaim-agents",
                resource=func.__name__,
            ) as span:
                span.set_tag("agent.name", agent_name)
                span.set_tag("agent.type", "google_adk")

                try:
                    result = await func(*args, **kwargs)

                    # Log success metrics
                    duration = time.time() - start_time
                    span.set_tag("agent.duration_ms", int(duration * 1000))
                    span.set_tag("agent.status", "success")

                    # Log to LLMObs
                    LLMObs.annotate(
                        span=span,
                        input_data=str(kwargs.get("query", args[0] if args else "")),
                        output_data=str(result)[:1000],  # Truncate
                    )

                    return result

                except Exception as e:
                    span.set_tag("agent.status", "error")
                    span.set_tag("agent.error", str(e))
                    raise

        return wrapper
    return decorator

# Usage
@trace_adk_agent("curriculum_agent")
async def search_curriculum(query: str) -> list:
    return await agent.run(query)
```

---

## MLflow Patterns

### Pattern 4: Experiment Tracking

**When to use**: Model training and evaluation.

**Implementation**:
```python
import mlflow
from mlflow.tracking import MlflowClient

# Configure MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
mlflow.set_experiment("curriculum-embedding")

def train_embedding_model(config: dict):
    """Train embedding model with experiment tracking."""
    with mlflow.start_run(run_name=f"embedding-{config['model_name']}"):
        # Log parameters
        mlflow.log_params({
            "model_name": config["model_name"],
            "batch_size": config["batch_size"],
            "learning_rate": config["learning_rate"],
            "epochs": config["epochs"],
        })

        # Training loop
        for epoch in range(config["epochs"]):
            loss = train_epoch(model, data)
            accuracy = evaluate(model, eval_data)

            # Log metrics
            mlflow.log_metrics({
                "train_loss": loss,
                "eval_accuracy": accuracy,
            }, step=epoch)

        # Log model
        mlflow.pytorch.log_model(
            model,
            "model",
            registered_model_name="curriculum-embedder",
        )

        # Log artifacts
        mlflow.log_artifact("config.yaml")
        mlflow.log_artifact("training_data_summary.json")
```

### Pattern 5: Model Registry

**When to use**: Managing model versions.

**Implementation**:
```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

def promote_model(model_name: str, version: int, stage: str):
    """Promote model version to new stage."""
    client.transition_model_version_stage(
        name=model_name,
        version=version,
        stage=stage,  # "Staging", "Production", "Archived"
    )

def load_production_model(model_name: str):
    """Load the production model."""
    model_uri = f"models:/{model_name}/Production"
    return mlflow.pytorch.load_model(model_uri)

# Usage
model = load_production_model("curriculum-embedder")
embeddings = model.encode(texts)
```

---

## Langfuse Patterns

### Pattern 6: LLM Cost Tracking

**When to use**: All LLM API calls.

**Implementation**:
```python
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

# Initialize Langfuse
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
)

@observe(as_type="generation")
async def generate_with_tracking(
    prompt: str,
    model: str = "gpt-4o",
) -> str:
    """Generate with automatic cost tracking."""
    # Langfuse automatically tracks:
    # - Input/output tokens
    # - Latency
    # - Cost (based on model pricing)

    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    # Add metadata
    langfuse_context.update_current_observation(
        metadata={
            "use_case": "curriculum_qa",
            "language": "en",
        }
    )

    return response.choices[0].message.content

@observe()
async def rag_pipeline(query: str) -> dict:
    """Full RAG pipeline with tracing."""
    # Each step is traced as a span
    with langfuse_context.observe(name="retrieval"):
        documents = await retrieve_documents(query)

    with langfuse_context.observe(name="generation"):
        response = await generate_with_tracking(
            f"Context: {documents}\n\nQuery: {query}"
        )

    return {"query": query, "response": response, "sources": documents}
```

### Pattern 7: Prompt Management

**When to use**: Version-controlling prompts.

**Implementation**:
```python
from langfuse import Langfuse

langfuse = Langfuse()

def get_prompt(name: str, version: int | None = None) -> str:
    """Fetch prompt from Langfuse."""
    prompt = langfuse.get_prompt(
        name=name,
        version=version,  # None = latest
        type="text",
    )
    return prompt.compile()

def get_chat_prompt(name: str, variables: dict) -> list:
    """Fetch and compile chat prompt."""
    prompt = langfuse.get_prompt(name=name, type="chat")
    return prompt.compile(**variables)

# Usage
system_prompt = get_prompt("curriculum_qa_system")
messages = get_chat_prompt(
    "curriculum_qa",
    {"context": documents, "query": query}
)
```

---

## Ragas Patterns

### Pattern 8: RAG Evaluation

**When to use**: Measuring retrieval quality.

**Implementation**:
```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from datasets import Dataset

def evaluate_rag(
    questions: list[str],
    answers: list[str],
    contexts: list[list[str]],
    ground_truths: list[str],
) -> dict:
    """Evaluate RAG system with Ragas metrics."""
    # Create dataset
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    }
    dataset = Dataset.from_dict(data)

    # Run evaluation
    result = evaluate(
        dataset,
        metrics=[
            faithfulness,      # Is answer faithful to context?
            answer_relevancy,  # Is answer relevant to question?
            context_precision, # Are retrieved contexts precise?
            context_recall,    # Are all relevant contexts retrieved?
        ],
    )

    return {
        "faithfulness": result["faithfulness"],
        "answer_relevancy": result["answer_relevancy"],
        "context_precision": result["context_precision"],
        "context_recall": result["context_recall"],
    }

# Usage in Dagster
@asset
def rag_quality_metrics(context, rag_test_data):
    """Evaluate RAG quality as Dagster asset."""
    metrics = evaluate_rag(
        questions=rag_test_data["questions"],
        answers=rag_test_data["answers"],
        contexts=rag_test_data["contexts"],
        ground_truths=rag_test_data["ground_truths"],
    )

    # Log to MLflow
    with mlflow.start_run(run_name="rag-eval"):
        mlflow.log_metrics(metrics)

    context.log.info(f"RAG metrics: {metrics}")
    return metrics
```

### Pattern 9: Continuous Evaluation

**When to use**: Automated quality monitoring.

**Implementation**:
```python
from dagster import asset, AssetExecutionContext, AssetCheckResult
import pandas as pd

QUALITY_THRESHOLDS = {
    "faithfulness": 0.8,
    "answer_relevancy": 0.7,
    "context_precision": 0.75,
    "context_recall": 0.7,
}

@asset
def rag_quality_check(context: AssetExecutionContext):
    """Run RAG quality evaluation."""
    # Load test cases
    test_cases = load_test_cases()

    # Generate answers
    answers = []
    contexts = []
    for q in test_cases["questions"]:
        result = await rag_pipeline(q)
        answers.append(result["response"])
        contexts.append(result["sources"])

    # Evaluate
    metrics = evaluate_rag(
        questions=test_cases["questions"],
        answers=answers,
        contexts=contexts,
        ground_truths=test_cases["ground_truths"],
    )

    # Check thresholds
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
    """Ensure faithfulness meets threshold."""
    return AssetCheckResult(
        passed=rag_quality_check["faithfulness"] >= QUALITY_THRESHOLDS["faithfulness"],
        metadata={"faithfulness": rag_quality_check["faithfulness"]},
    )
```

---

## Unified Logging

### Pattern 10: Structured Logging

**When to use**: All application logging.

**Implementation**:
```python
import structlog
import logging

def configure_logging(service_name: str, env: str):
    """Configure structured logging with Datadog integration."""
    # Processors for structured output
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if env == "production":
        # JSON format for Datadog
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty print for development
        processors.append(structlog.dev.ConsoleRenderer())

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
        logger.info(
            "search_completed",
            query=query,
            result_count=len(results),
            latency_ms=elapsed_ms,
        )
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
| **MLflow** | Training | Experiment logging |
| **Langfuse** | LLM calls | Cost tracking |
| **Ragas** | RAG pipeline | Quality metrics |
| **Structlog** | All services | Unified logging |

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

---

## References

- Source: `sruth/oideachais/observability/`
- Skills: `.claude/skills/mlflow/`, `.claude/skills/langfuse/`
- Documentation: https://docs.datadoghq.com, https://mlflow.org, https://langfuse.com
