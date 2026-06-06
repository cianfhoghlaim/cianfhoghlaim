# lakeFS — KCG Summary

## What It Is
lakeFS is a Git-like version control system for data lakes, providing branch/commit/merge semantics over S3-compatible object stores. This directory contains the full lakeFS-samples repository with 3,100+ files demonstrating Iceberg table versioning, Delta Lake integration, Spark medallion architecture, Trino SQL querying, write-audit-publish (WAP) patterns, and ML reproducibility workflows with PyTorch and LangChain.

## Why This Matters for Kings' College Galway
lakeFS-style data versioning directly supports the curriculum data platform's need for reproducible data pipelines. The WAP and branching patterns documented here are directly applicable to DLT ingestion of Leaving Cert examination data, ensuring data quality gates before promotion to production. The Iceberg catalog examples inform our DuckLake/MotherDuck lakehouse architecture, and the ML reproducibility workflows map to model versioning needs for our educational AI models.

## Key Patterns Preserved
37 .md files remain, including:
- `README.md` — Overview of all lakeFS examples and architecture
- `lakeFS-samples/README.md` — Sample project index with 20+ standalone examples
- `dagster-integration/README.md` — Dagster + lakeFS orchestration patterns
- `iceberg/spark-medallion/README.md` — Bronze/silver/gold medallion architecture
- `iceberg/write-audit-publish/README.md` — WAP quality gate pattern
- `ml/llm-langchain/README.md` — AI agents with LangChain + OpenAI + lakeFS
- `ml/image-segmentation/README.md` — PyTorch + MLflow reproducibility
- `ml/README.md` — ML experimentation patterns
- `delta-lake/README.md` — Delta Lake versioning
- 19 standalone example READMEs covering Airflow, Databricks CI/CD, Kafka, Flink, Trino, Spark, Prefect, Red Hat OpenShift AI, Labelbox, ParadeDB

## Source Files
Full source removed (2026-06-06). Available at https://github.com/treeverse/lakeFS-samples

## What Was Removed
Python notebooks (.ipynb), Docker configurations, JSON/YAML config files, Python scripts, JAR/Scala files, images/logos, shell scripts, Terraform, CSV/Parquet data
