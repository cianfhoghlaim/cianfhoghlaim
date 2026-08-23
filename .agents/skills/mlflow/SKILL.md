---
name: mlflow
description: Expert assistance for ML lifecycle management with MLflow. Use when users need experiment tracking, model registry, LLM tracing, GenAI evaluation, prompt management, or model deployment.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# MLflow - ML Lifecycle Platform

**Version:** 3.14.0 | **Last Updated:** 2026-06-29
**Python:** >=3.10 | **PyPI releases:** 182 (latest 3.14.0 on 2026-06-17)
**LTS branch:** 2.22.5 (2026-05-12)

## Overview

MLflow is an open-source platform for managing the ML lifecycle:

- **Experiment Tracking**: Log parameters, metrics, and artifacts
- **Model Registry**: Version and manage models
- **LLM Tracing**: Observability for LLM applications
- **GenAI Evaluation**: Evaluate LLM outputs with scorers
- **Prompt Registry**: Version and manage prompts

**Documentation**: https://mlflow.org/docs

## When to Use This Skill

Activate when users need:

- "Track ML experiments and metrics"
- "Log and register models"
- "Trace LLM application calls"
- "Evaluate LLM outputs"
- "Manage prompt versions"
- "Deploy ML models"

## Core Concepts

### 1. Experiment Tracking

```python
import mlflow

# Set tracking URI and experiment
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("my-experiment")

# Log run
with mlflow.start_run():
    # Log parameters
    mlflow.log_params({
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 1000
    })

    # Log metrics
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_metrics({
        "precision": 0.92,
        "recall": 0.94,
        "f1": 0.93
    })

    # Log artifacts
    mlflow.log_artifact("model_config.json")
    mlflow.log_table(
        data={"prompt": prompts, "response": responses},
        artifact_file="predictions.csv"
    )
```

### 2. LLM Tracking

```python
import mlflow

with mlflow.start_run():
    # Log LLM predictions
    mlflow.llm.log_predictions(
        inputs=[{"question": "What is MLflow?"}],
        outputs=["MLflow is an ML platform..."],
        prompts=["Answer: {input}"]
    )
```

### 3. Auto-Tracing

```python
import mlflow

# OpenAI
mlflow.openai.autolog()

# LangChain
mlflow.langchain.autolog()

# Anthropic
mlflow.anthropic.autolog()

# LlamaIndex
mlflow.llama_index.autolog()

# All LLM calls are now traced automatically
```

### 4. Manual Tracing

```python
import mlflow
from mlflow.entities import SpanType

@mlflow.trace(span_type=SpanType.CHAIN)
def rag_pipeline(query: str) -> str:
    """RAG pipeline with automatic tracing."""
    context = retrieve_documents(query)
    response = generate_response(query, context)
    return response

@mlflow.trace(span_type=SpanType.RETRIEVER)
def retrieve_documents(query: str) -> list:
    return vector_db.search(query, k=5)

@mlflow.trace(span_type=SpanType.LLM)
def generate_response(query: str, context: list) -> str:
    return llm.generate(query=query, context=context)
```

### 5. Context Manager Tracing

```python
import mlflow

def complex_workflow(query: str):
    with mlflow.start_span(name="workflow") as parent_span:
        parent_span.set_inputs({"query": query})

        with mlflow.start_span(name="retrieval") as span:
            docs = retrieve(query)
            span.set_outputs({"doc_count": len(docs)})

        with mlflow.start_span(name="generation") as span:
            response = generate(query, docs)
            span.set_outputs({"response": response})

        parent_span.set_outputs({"response": response})
        return response
```

### 6. GenAI Evaluation

```python
import mlflow
from mlflow.genai.scorers import Correctness, Guidelines
from mlflow.genai import scorer

# Define evaluation dataset
eval_dataset = [
    {
        "inputs": {"question": "What is the capital of France?"},
        "expectations": {"expected_response": "Paris"},
    },
]

# Custom scorer
@scorer
def is_concise(outputs: str) -> bool:
    return len(outputs.split()) <= 10

# Run evaluation
results = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=my_model,
    scorers=[
        Correctness(),
        Guidelines(name="is_english", guidelines="Answer in English"),
        is_concise,
    ],
)
```

### 7. Predefined Scorers

```python
from mlflow.genai.scorers import (
    Correctness,           # Validates against ground truth
    RelevanceToQuery,      # Assesses if response addresses input
    Guidelines,            # Evaluates custom criteria
    Safety,                # Detects harmful content
    Equivalence,           # Compares to expected output
    RetrievalGroundedness, # Validates RAG responses
    RetrievalRelevance,    # Ensures retrieved docs are relevant
)

scorers = [
    Correctness(),
    Guidelines(
        name="professional",
        guidelines="Response must be professional"
    ),
    Safety(),
]
```

### 8. Prompt Registry

```python
import mlflow

# Register prompt
prompt = mlflow.genai.register_prompt(
    name="summarization-prompt",
    template="""\
Summarize in {{ num_sentences }} sentences.

Content: {{ content }}

Summary:""",
    commit_message="Initial version",
    tags={"task": "summarization"}
)

# Load prompt
prompt = mlflow.genai.load_prompt("summarization-prompt")

# Load specific version
prompt = mlflow.genai.load_prompt("prompts:/summarization-prompt/2")

# Load by alias
prompt = mlflow.genai.load_prompt("prompts:/summarization-prompt@production")

# Format and use
formatted = prompt.format(num_sentences=3, content="...")
```

### 9. Prompt Aliases

```python
import mlflow

# Set aliases for deployment stages
mlflow.set_prompt_alias("summarization-prompt", "production", version=3)
mlflow.set_prompt_alias("summarization-prompt", "staging", version=4)
mlflow.set_prompt_alias("summarization-prompt", "development", version=5)

# Load by alias in production
prompt = mlflow.genai.load_prompt("prompts:/summarization-prompt@production")
```

### 10. Model Registry

```python
import mlflow

# Log model
with mlflow.start_run():
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="my-classifier"
    )

# Load model
model = mlflow.sklearn.load_model("models:/my-classifier/1")

# Load latest version
model = mlflow.sklearn.load_model("models:/my-classifier/latest")

# Load by alias
model = mlflow.sklearn.load_model("models:/my-classifier@production")
```

## Span Types

| SpanType | Description |
|----------|-------------|
| `AGENT` | Agent orchestration |
| `CHAIN` | Sequential processing |
| `CHAT_MODEL` | Chat completion |
| `EMBEDDING` | Embedding generation |
| `LLM` | LLM inference |
| `RETRIEVER` | Document retrieval |
| `TOOL` | Tool/function calls |
| `PARSER` | Output parsing |

## Framework Integrations

| Framework | Autolog Function | Min Version |
|-----------|-----------------|-------------|
| LangChain | `mlflow.langchain.autolog()` | 2.14.0 |
| OpenAI | `mlflow.openai.autolog()` | 2.14.0 |
| Anthropic | `mlflow.anthropic.autolog()` | 2.17.0 |
| LlamaIndex | `mlflow.llama_index.autolog()` | 2.14.0 |
| Gemini | `mlflow.gemini.autolog()` | 2.17.0 |
| Bedrock | `mlflow.bedrock.autolog()` | 2.17.0 |
| Transformers | `mlflow.transformers.autolog()` | 2.14.0 |
| DSPy | `mlflow.dspy.autolog()` | 2.17.0 |

## Common Patterns

### RAG Evaluation

```python
from mlflow.genai.scorers import RetrievalGroundedness, Correctness

results = mlflow.genai.evaluate(
    data=rag_dataset,
    predict_fn=rag_pipeline,
    scorers=[
        Correctness(),
        RetrievalGroundedness(),
    ],
)
```

### Custom LLM Judge

```python
from mlflow.genai.judges import make_judge
from typing import Literal

coherence_judge = make_judge(
    name="coherence",
    instructions="""
    Evaluate the coherence of the response.

    Question: {{ inputs }}
    Response: {{ outputs }}

    Rate as: coherent, somewhat coherent, or incoherent.
    """,
    feedback_value_type=Literal["coherent", "somewhat coherent", "incoherent"],
    model="openai:/gpt-4o-mini",
)
```

### Human Feedback

```python
import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType

# Log human feedback
mlflow.log_feedback(
    trace_id=trace_id,
    name="helpfulness",
    value=4,
    rationale="Response was helpful",
    source=AssessmentSource(
        source_type=AssessmentSourceType.HUMAN,
        source_id="reviewer@example.com"
    )
)
```

### Model Comparison

```python
models = ["gpt-4o-mini", "claude-sonnet-4-20250514", "gemini-1.5-flash"]

for model in models:
    with mlflow.start_run(run_name=f"eval_{model}"):
        mlflow.log_param("model", model)
        metrics = evaluate_model(model)
        mlflow.log_metrics(metrics)
```

## MLflow Server

```bash
# Start tracking server
mlflow server --host 0.0.0.0 --port 5000

# With database backend
mlflow server \
    --backend-store-uri postgresql://user:pass@localhost/mlflow \
    --default-artifact-root s3://mlflow-artifacts

# Start UI only
mlflow ui --port 5000
```

## Best Practices

1. **Structured Logging**: Log parameters, metrics, and artifacts consistently
2. **Experiment Organization**: Use meaningful experiment names
3. **Tagging**: Tag runs with environment, version, and purpose
4. **Prompt Versioning**: Version prompts with meaningful commit messages
5. **Evaluation-Driven**: Run evaluations on every prompt/model change

## Troubleshooting

### Traces Not Appearing
- Verify autolog is enabled before making calls
- Check tracking URI is set correctly
- Ensure experiment is set

### Missing Token Usage
- Check MLflow version (3.1.0+ for most providers)
- Enable `stream_options={"include_usage": True}` for streaming

### Evaluation Failing
- Verify scorer parameters match expected schema
- Check predict_fn returns expected format

## Resources

- **Documentation**: https://mlflow.org/docs
- **LLM Guide**: https://mlflow.org/docs/latest/llms/index.html
- **GenAI Evaluation**: https://mlflow.org/docs/latest/genai/eval-monitor/
- **GitHub**: https://github.com/mlflow/mlflow

## MLflow 3 — What's New (verified 2026-06-29, Agent 89)

- **`mlflow.search_logged_models()`** — SQL-like filter across experiments
- **`mlflow.create_external_model()`** — register models trained outside MLflow
- **`models:/<model_id>` URI** — direct ID-based model loading (replaces `runs:/<run_id>/path`)
- **Checkpoint-aware `log_metric`** — `step=`, `model_id=`, `dataset=` args
- **`mlflow agent setup`** — installs `.agents/skills` for Claude Code / Codex / OpenCode
- **`@mlflow.test`** — pytest marker for GenAI regression tests
- **Review Queues** — assign traces to reviewers, collect structured feedback
- **LLM Playground** — browser iteration over AI Gateway + Prompt Registry
- **WAL tracing** — durable, low-latency Claude Code traces

## v3.14.0 Breaking Changes

- `mlflow.sklearn` `serialization_format` default: `cloudpickle` → `skops` (#23987)
- `mlflow.pytorch.log_model` / `save_model` default → `pt2` (#23988)
- `mlflow.lightgbm` default → `skops` (#23986)
→ Pin `serialization_format="cloudpickle"` explicitly if you need the old behavior.

## MLflow 3 — Model Checkpoint Logging

```python
with mlflow.start_run() as run:
    for epoch in range(100):
        if epoch % 10 == 0:
            model_info = mlflow.pytorch.log_model(
                pytorch_model=model,
                name=f"checkpoint-epoch-{epoch}",
                step=epoch,
            )
            mlflow.log_metric(
                "accuracy", value, step=epoch,
                model_id=model_info.model_id,
                dataset=validation_dataset,
            )

# Load by model_id (new URI form)
loaded = mlflow.pyfunc.load_model(f"models:/{model_info.model_id}")

# Search logged models across experiments
top = mlflow.search_logged_models(
    experiment_ids=["1"],
    filter_string="metrics.accuracy > 0.9",
    order_by=[{"field_name": "metrics.accuracy", "ascending": False}],
    max_results=1,
    output_format="list",
)[0]
```

## MLflow 3 — External Model Registration

```python
import mlflow
mlflow.create_external_model(name="my-external-model")
```

## Best Practices (Wave 2 additions)

6. **MLflow 3 model_id URIs**: prefer `models:/<model_id>` over `runs:/<run_id>/path` for new code
7. **Serialization pinning**: set `serialization_format` explicitly on `log_model` calls in v3.14.0+ to avoid the default flip
8. **Local KCG code**: `cianfhoghlaim/core/obs/observability/mlflow_config.py` should migrate `runs:/{run_id}/model` → `models:/{model_info.model_id}` for MLflow 3
