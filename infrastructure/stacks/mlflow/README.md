# MLflow — ML Experiment Tracking and Model Registry

## Overview

MLflow is an open-source platform for managing the machine learning lifecycle: experiment tracking, model registry, deployment, and evaluation. It provides a web UI for comparing experiment runs, a model registry for versioning trained models, and SDKs for Python, R, and Java.

## Why This Matters for Kings' College Galway

MLflow tracks every machine learning experiment in the platform: the ColPali fine-tuning runs on exam paper images, the BGE-M3 embedding quality experiments, the RAGAS evaluation scores for curriculum extraction, and the llama-swap model performance benchmarks. The model registry versions the GGUF models produced by the Dagster `model_conversion` job, so the infrastructure can roll back to a previous model version if a new conversion produces degraded output. MLflow's integration with Langfuse means every LLM trace can be linked back to a specific model version in the registry.

## Key Features

- **Experiment tracking** — Log parameters, metrics, artifacts per run
- **Model registry** — Version, stage, and deploy models with lineage tracking
- **LLM evaluation** — Built-in evaluation for RAG, question answering, and text generation
- **Artifact storage** — Store models, datasets, and visualisations alongside metadata
- **Python SDK** — `mlflow.log_metric()`, `mlflow.log_model()`, `mlflow.register_model()`

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/mlflow
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves PostgreSQL credentials and S3 access keys from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MLFLOW_PORT` | No | Tracking server port | `5000` |
| `MLFLOW_BACKEND_STORE_URI` | Yes | PostgreSQL connection string for metadata | — |
| `MLFLOW_ARTIFACT_ROOT` | Yes | S3 path for artifact storage | `s3://mlflow` |
| `AWS_ACCESS_KEY_ID` | Yes | S3 access key (Garage) | — |
| `AWS_SECRET_ACCESS_KEY` | Yes | S3 secret key (Garage) | — |

## Access

- **Web UI**: `https://mlflow.cianfhoghlaim.ie` (private, Member role)
- **Tracking API**: `http://localhost:5000`
- **Auth**: Email/password (basic auth proxy) + Pocket ID SSO

## Upstream

- **Repository**: <https://github.com/mlflow/mlflow>
- **Documentation**: <https://mlflow.org/docs>
- **Latest**: v2.20.x (2025) — LLM evaluation, prompt engineering UI, model signing, GenAI tracing

## Screenshot

MLflow's web UI shows: an experiment list with run count and best metrics, a run comparison view (parallel coordinates, scatter plots, contour plots), a model registry with version history and stage transitions (Staging → Production → Archived), and an artifact browser for viewing logged files and plots.
