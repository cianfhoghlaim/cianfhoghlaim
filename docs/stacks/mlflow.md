# mlflow

## Purpose for the Cianfhoghlaim project

MLflow is the **ML experiment tracking and model registry** for the
platform. After the `centralise-data-plane` rewrite (2026-07-30),
its backend store lives on the shared lakehouse-postgres
`mlflow` database and its artifact store lives on the shared
lakehouse-garage `mlflow-artifacts` bucket. The 12-agent fleet
logs all training-time experiments to MLflow (the
`retro_asset_generation_2d` and `retro_asset_generation_3d`
experiments per the `retro-educational-game-asset-pipeline-v1`
openspec change plus the 10+ existing runs in
`meaisinfhoghlaim/training/`).

## Why it stays in komodo/pangolin/infisical GitOps

MLflow is consumed by litellm's `MLFLOW_TRACKING_URI` env var
(per the litellm compose.yaml). The komodo
`deploy-mlflow-bunchloch` procedure ensures MLflow waits for the
lakehouse stack to be healthy first. The custom
`Dockerfile.mlflow` (added 2026-07-30) bakes `psycopg2-binary +
boto3` into the upstream image, eliminating the ~30s pip install
on first cold start.

## Centralised Data Plane Contract

| Resource | Docker DNS | Auth |
|:--|:--|:--|
| Postgres (db=mlflow) | `lakehouse-postgres:5432` | `POSTGRES_USER` + `POSTGRES_PASSWORD` (from lakehouse/*) |
| S3 (artifacts) | `lakehouse-garage:3900` (bucket=`mlflow-artifacts`) | `GARAGE_ACCESS_KEY_ID` + `GARAGE_SECRET_ACCESS_KEY` (from lakehouse-garage/*) |

The `mlflow-artifacts` bucket is auto-created by
`lakehouse/garage-init` on first lakehouse deploy.

## Cross-references

- **Ops**: `bonneagar/stacks/mlflow/` (the 6-file GOLD_STANDARD + custom `Dockerfile.mlflow`)
- **Code**: `meaisinfhoghlaim/training/` + `meaisinfhoghlaim/evaluation/`
- **Komodo procedure**: `deploy-mlflow-bunchloch.toml` (3-stage: lakehouse → mlflow → 4 health checks). The arm1-oci variant is at `mlflow.toml`.
- **Pangolin**: `https://mlflow.cianfhoghlaim.ie/health` (Member role)

## Tags

- `host:bunchloch` (primary) / `host:arm1-oci` (production)
- `tier:observability`
- `project:cianfhoghlaim`
- `group:observability` (depends on `foundation`)
