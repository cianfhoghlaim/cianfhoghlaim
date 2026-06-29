# mlflow

## Purpose for the Cianfhoghlaim project

MLflow is an open-source platform for managing the machine learning lifecycle: experiment tracking, model registry, deployment, and evaluation. It provides a web UI for comparing experiment runs, a model registry for versioning trained models, and SDKs for Python, R, and Java.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the LLM inference + observability surface. LiteLLM is the unified gateway; MLX-Omni is the local Apple Silicon backend; Langfuse + mlflow + logfire provide the observability tier.

## Cross-references

- **Ops**: `bonneagar/stacks/mlflow/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:language-model`
- - **Pangolin**: `https://mlflow.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:language-model`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
