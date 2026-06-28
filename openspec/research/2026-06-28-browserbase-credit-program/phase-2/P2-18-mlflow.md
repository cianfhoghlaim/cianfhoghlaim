# P2-18 — mlflow (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

MLflow is the **model registry + experiment tracking** for the 6 OCR/HTR models (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) plus the 11 OCR vision models (Gemma 4 + Qwen3.6 + GLM-4.6V families). Every training run + every inference result is tracked.

The canonical Cianfhoghlaim pattern: MLflow tracks **all model artifacts** (checkpoints, ONNX exports, GGUF quantizations), while Langfuse tracks **inference traces**. They're complementary, not redundant.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/mlflow/compose.yaml` | MLflow server + Postgres backend store + Garage S3 artifact store |
| `stacks/mlflow/blueprint.yaml` | Pangolin private-resource (`mlflow.cianfhoghlaim.ie:5000`) |
| `oideachais/ocr/models/registry.py` | OCR model registry (11 vision + 6 classical) |
| `oideachais/ocr/evaluation/compare.py` | Evaluation harness (~220 evals) |
| `cognify/rules/mlflow_register_model.py` | Dagster asset for model registration |
| `cognify/rules/mlflow_promote_to_prod.py` | Dagster asset for staging→prod promotion |
| `oideachais/ocr/evaluation/metrics.py` | OCR-specific metrics (CER, WER, GAELIC-specific) |

**Canonical model registration** (`oideachais/ocr/models/registry.py`):

```python
import mlflow

def register_ocr_model(
    model_name: str,
    checkpoint_path: str,
    metrics: dict[str, float],
    params: dict,
) -> str:
    """Register an OCR model to MLflow with version + stage transition."""
    with mlflow.start_run(run_name=f"ocr-{model_name}") as run:
        # 1. Log params
        mlflow.log_params(params)
        # 2. Log metrics (CER, WER, GAELIC-specific)
        mlflow.log_metrics(metrics)
        # 3. Log model artifact (ONNX or GGUF)
        mlflow.log_artifact(checkpoint_path)
        # 4. Register model version
        model_uri = f"runs:/{run.info.run_id}/model"
        registered = mlflow.register_model(model_uri=model_uri, name=model_name)
        # 5. Transition to staging
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=model_name, version=registered.version, stage="Staging",
        )
    return registered.version
```

**Evaluation run** (`oideachais/ocr/evaluation/compare.py`):

```python
def eval_model_on_irish_syllabus(model_name: str) -> dict:
    """Run ~220 evals across Ireland syllabus + 6 leabharlann subdirs."""
    with mlflow.start_run(run_name=f"eval-{model_name}") as run:
        results = {}
        for subdir in LEABHARLANN_SUBDIRS:
            cer = compute_cer(model_name, subdir)
            wer = compute_wer(model_name, subdir)
            results[f"cer_{subdir}"] = cer
            results[f"wer_{subdir}"] = wer
        mlflow.log_metrics(results)
    return results
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `MLFLOW_TRACKING_URI` | `https://mlflow.cianfhoghlaim.ie` | Locket |
| `MLFLOW_S3_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |
| `MLFLOW_BACKEND_STORE_URI` | `postgres://mlflow-postgres:5432/mlflow` | compose env |
| `MLFLOW_ARTIFACT_ROOT` | `s3://mlflow-artifacts/` | compose env |
| `MLFLOW_REGISTRY_URI` | (same as tracking) | derived |

## CCC anchors

`stacks/mlflow/` · `oideachais/ocr/models/registry.py` · `oideachais/ocr/evaluation/compare.py` · `cognify/rules/mlflow_register_model.py`

Search terms: `"mlflow.register_model"`, `"mlflow.log_metrics"`, `"transition_model_version_stage"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-Q4 | Initial MLflow deploy (for OCR model tracking) |
| 2026-01 | Migrated from MLflow Cloud to self-hosted |
| 2026-03 | Wired 11 OCR vision models to MLflow registry |
| 2026-04 | Built evaluation harness (`oideachais/ocr/evaluation/compare.py`) |
| 2026-05 | Added staging→prod promotion DAG (cognify/rules/mlflow_promote_to_prod.py) |
| 2026-06-28 | v4 consolidation: no path rename (OCR models stay in `oideachais/ocr/`) |

## Anti-patterns

1. Don't store model artifacts in Postgres — use S3 (Garage)
2. Don't use `mlflow.sklearn.log_model` for non-sklearn models — use `mlflow.pyfunc.log_model` (custom)
3. Don't transition to Production directly — always go through Staging first
4. Don't skip the `run_name` — without it, runs are anonymous in the UI
5. Don't store large datasets in MLflow — use a separate DVC or lakehouse table
6. Don't use SQLite as the backend store — it's single-writer, breaks in HA deploys
7. Don't skip the `artifact_path` — it determines where in S3 the model lands

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Backend store | Postgres (PlanetScale) | HA + managed |
| Artifact store | Garage S3 | Already deployed; S3-compatible |
| UI access | Pangolin + Pocket ID SSO | Single auth source |
| Model registry | MLflow's built-in | Standard + integrations |
| Experiment tracking | MLflow's built-in (not wandb/tensorboard) | One tool, fewer deps |
| OCR metrics | CER + WER + GAELIC-specific (custom) | Multilingual support |
| Staging→Prod | Dagster asset (manual approval) | Human-in-the-loop |
| Retention | Permanent for registered models | Model registry is the source of truth |

## Files to read next

`stacks/mlflow/compose.yaml` · `oideachais/ocr/models/registry.py` · `oideachais/ocr/evaluation/compare.py` · `.agents/skills/mlflow/SKILL.md`
