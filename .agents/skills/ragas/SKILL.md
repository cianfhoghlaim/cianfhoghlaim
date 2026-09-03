---
name: ragas
description: Expert assistance for RAG evaluation with RAGAS. Use when users need RAG metrics, evaluation frameworks, or measuring retrieval and generation quality.
---

# RAGAS - RAG Evaluation Framework

**Version:** >=0.1.10 | **Last Updated:** 2025-04

## Overview

RAGAS is a framework for evaluating Retrieval-Augmented Generation systems:

- **Trace-Based Metrics**: Evaluate based on execution traces
- **Multiple Metrics**: Faithfulness, answer relevance, context precision
- **LLM-Based Evaluation**: Use LLMs to evaluate RAG outputs
- **Custom Metrics**: Define custom evaluation metrics
- **Dataset Support**: Work with various RAG datasets

**Documentation**: https://docs.ragas.io

## When to Use This Skill

Activate when users need:

- "Evaluate RAG system performance"
- "Measure retrieval quality"
- "Assess answer faithfulness"
- "Compare different RAG implementations"
- "Create custom evaluation metrics"

## Core Concepts

### 1. Basic Setup

```python
pip install ragas
```

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall
)
```

### 2. Preparing Evaluation Data

```python
from datasets import Dataset

evaluation_data = {
    "question": [
        "What is the capital of France?",
        "Who wrote Romeo and Juliet?"
    ],
    "answer": [
        "The capital of France is Paris.",
        "William Shakespeare wrote Romeo and Juliet."
    ],
    "contexts": [
        ["Paris is the capital and most populous city of France."],
        ["Romeo and Juliet is a tragedy by William Shakespeare."]
    ],
    "ground_truths": [
        ["Paris"],
        ["William Shakespeare"]
    ]
}

dataset = Dataset.from_dict(evaluation_data)
```

### 3. Running Evaluation

```python
# Basic evaluation
result = evaluate(
    dataset=dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall
    ]
)

# View results
print(result.to_pandas())

# Get overall scores
print(result)
```

### 4. Trace-Based Evaluation

```python
from ragas import RunConfig
from ragas.integrations.llama_index import LlamaIndexEvaluator

# Evaluate from traces
evaluator = LlamaIndexEvaluator(
    metrics=[faithfulness, answer_relevancy]
)

result = evaluator.evaluate(
    traces=llama_index_traces,
    batch_size=10
)
```

### 5. Custom Metrics

```python
from ragas.metrics import Metric
from typing import Dict, Any

class CustomMetric(Metric):
    name = "custom_metric"
    description = "Custom evaluation metric"

    def score(self, row: Dict[str, Any]) -> float:
        # Custom scoring logic
        answer = row["answer"]
        context = row["contexts"]
        # Your evaluation logic here
        return score_value

# Use custom metric
result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, CustomMetric()]
)
```

## Available Metrics

### Answer Quality Metrics

```python
from ragas.metrics import (
    faithfulness,        # How faithful is answer to context
    answer_relevancy,   # How relevant is answer to question
    answer_correctness,   # How correct is the answer
    answer_similarity    # Semantic similarity to ground truth
)
```

### Retrieval Metrics

```python
from ragas.metrics import (
    context_precision,    # Precision of retrieved contexts
    context_recall,       # Recall of relevant contexts
    context_relevancy,   # Relevance of contexts to question
    context_entity_recall # Entity-based recall
)
```

### Critique Metrics

```python
from ragas.metrics import (
    harmfulness,         # Is the answer harmful?
    coherence,           # Is the answer coherent?
    conciseness          # Is the answer concise?
)
```

## Advanced Features

### Batch Evaluation

```python
from ragas import RunConfig

config = RunConfig(
    batch_size=10,
    max_workers=4,
    timeout=30
)

result = evaluate(
    dataset=dataset,
    metrics=[faithfulness, answer_relevancy],
    run_config=config
)
```

### LLM Configuration

```python
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI

# Configure custom LLM for evaluation
llm = LangchainLLMWrapper(
    ChatOpenAI(model="gpt-4o", temperature=0)
)

result = evaluate(
    dataset=dataset,
    metrics=[faithfulness],
    llm=llm
)
```

### Result Analysis

```python
# Get detailed results
df = result.to_pandas()

# Filter by score threshold
high_quality = df[df["faithfulness"] > 0.8]

# Calculate statistics
print(df.describe())

# Export results
df.to_csv("evaluation_results.csv")
```

## Best Practices

### Dataset Preparation

1. **Ground Truths**: Include accurate ground truth answers
2. **Context Quality**: Ensure retrieved contexts are relevant
3. **Diversity**: Include diverse question types

### Metric Selection

1. **Use Case**: Select metrics based on your use case
2. **Trade-offs**: Balance between different metrics
3. **Baseline**: Establish baseline scores for comparison

### Evaluation

1. **Regular Testing**: Evaluate regularly during development
2. **A/B Testing**: Compare different RAG implementations
3. **Continuous Improvement**: Use results to improve system

## Configuration

### Environment Variables

```bash
# For OpenAI-based metrics
OPENAI_API_KEY=sk-...

# For custom LLM endpoints
RAGAS_LLM_ENDPOINT=https://your-llm-endpoint
```

### Custom Configuration

```python
from ragas import EvaluationConfig

config = EvaluationConfig(
    metrics=[faithfulness, answer_relevancy],
    llm=your_llm,
    embeddings=your_embeddings,
    run_config=RunConfig(batch_size=10)
)
```

## Installation

```bash
pip install ragas
# With optional dependencies
pip install "ragas[llm]"
pip install "ragas[embeddings]"
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| RAG Development | Evaluate during development |
| Production Monitoring | Regular evaluation of production system |
| A/B Testing | Compare different retrieval strategies |
| Quality Assurance | Set quality thresholds for deployment |

### Related Skills

- [`langfuse`](.skills/langfuse/SKILL.md) - LLM observability and tracing
- [`lancedb`](.skills/lancedb/SKILL.md) - Vector database for RAG
- [`cognee`](.skills/cognee/SKILL.md) - Knowledge graph for RAG

## KCG integration

The Cianfhoghlaim curriculum pipeline uses RAGAS in two
critical places:

1. **Quality gate** — every study asset is scored by RAGAS
   before publication. The faithfulness ≥ 0.8 gate is the
   canonical publication bar.
2. **DPO preference signal** — high-RAGAS-score extractions
   become "chosen" examples; hallucinated prerequisites become
   "rejected" examples. The faithfulness ≥ 0.8 gate is then
   encoded directly into the model's preferences via
   `DPOTrainer` (see `.agents/skills/trl/SKILL.md`).

RAGAS scores are wired into MLflow and Langfuse via the
Dagster asset `orchestration/defs/meaisinfhoghlaim/ragas_eval.py`,
which runs daily on a 100-sample held-out test set.

The canonical RAGAS eval set lives in
`agents/meaisinfhoghlaim/evaluation/canonical_eval_set.json`
(100 samples × 4 metrics = 400 scores per run).

## RAGAS-as-DPO preference-signal example

```python
from ragas import evaluate
from trl import DPOConfig, DPOTrainer


def build_preference_dataset(baml_outputs: list[BAMLOutput]) -> list[dict]:
    """RAGAS ≥ 0.8 → chosen; RAGAS < 0.5 → rejected."""
    preferences = []
    for out in baml_outputs:
        ragas_scores = evaluate(
            dataset=out.to_ragas_dataset(),
            metrics=[faithfulness, answer_relevancy],
        )
        if ragas_scores["faithfulness"] >= 0.8 and ragas_scores.get("_rejected"):
            preferences.append({
                "prompt": out.prompt,
                "chosen": out.extraction,
                "rejected": ragas_scores["_rejected"],
            })
    return preferences


# The DPOTrainer is invoked from a Dagster asset
# (see `.agents/skills/trl/SKILL.md`)
```
