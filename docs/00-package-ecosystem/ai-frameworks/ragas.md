# RAGAS — RAG Evaluation Framework

## Overview

RAGAS (Retrieval Augmented Generation Assessment) is an open-source framework for evaluating RAG pipelines. It provides metrics for faithfulness, answer relevance, context precision, and context recall — measuring how well a RAG system retrieves relevant documents and generates accurate answers. Built by Exploding Gradients.

## Why This Matters for Kings' College Galway

Every piece of AI-generated educational content in this platform is evaluated by RAGAS before publication. When the BAML extraction pipeline produces a study asset or a learning outcome explanation, RAGAS scores it for faithfulness (does it accurately reflect the source syllabus?), answer relevance (does it actually answer the educational question?), and context precision (did the retrieval step find the right curriculum documents?). Only content scoring ≥0.8 on faithfulness surfaces in the student-facing web app — this is the quality gate that ensures AI-generated educational materials are academically reliable.

## Key Features

- **Faithfulness** — Measures if generated content is grounded in retrieved context
- **Answer relevance** — Checks if the response is actually relevant to the question
- **Context precision** — Evaluates if retrieved documents are relevant
- **Context recall** — Measures if all relevant documents were retrieved
- **Langfuse integration** — Scores are traced alongside LLM calls

## Installation

```bash
uv add ragas
```

## Integration with Our Stack

RAGAS evaluation runs as a Dagster asset after each extraction run. Scores are stored in MLflow as experiment metrics and linked to Langfuse traces for per-extraction observability. The `study_assets_published` asset only proceeds if RAGAS faithfulness ≥ 0.8.

## Upstream

- **Repository**: <https://github.com/explodinggradients/ragas>
- **Documentation**: <https://docs.ragas.io>
- **Latest**: v0.2.x (2025) — trace-based metrics, faithfulness improvements, multi-turn evaluation

## Screenshot

RAGAS is a programmatic library. Evaluation results appear as DataFrames with per-metric scores. The Langfuse UI shows RAGAS scores per trace in the evaluation tab. The MLflow UI shows experiment run comparisons with RAGAS metrics plotted as parallel coordinates and scatter plots.
