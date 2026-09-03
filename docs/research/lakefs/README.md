# lakeFS Examples

This directory contains examples demonstrating lakeFS integration for data versioning, lakehouse patterns, and ML/AI workflows.

## Examples Index

### Iceberg / Data Lakehouse

| Example | Description | Complexity |
|---------|-------------|------------|
| [iceberg/spark-basic](./iceberg/spark-basic/) | Basic Spark + lakeFS integration | Low |
| [iceberg/spark-medallion](./iceberg/spark-medallion/) | Medallion architecture (bronze/silver/gold) | Medium |
| [iceberg/trino](./iceberg/trino/) | Trino SQL with Iceberg REST Catalog | Medium |
| [iceberg/write-audit-publish](./iceberg/write-audit-publish/) | WAP pattern for data quality | Medium |
| [delta-lake](./delta-lake/) | Delta Lake versioning | Medium |

### ML / AI

| Example | Description | Complexity |
|---------|-------------|------------|
| [ml/llm-langchain](./ml/llm-langchain/) | AI agents with LangChain + OpenAI | Medium |
| [ml/image-segmentation](./ml/image-segmentation/) | PyTorch + MLflow reproducibility | High |
| [ml/ml-reproducibility](./ml/ml-reproducibility/) | ML experimentation tracking | Medium |

### Workflow Orchestration

| Example | Description | Complexity |
|---------|-------------|------------|
| [dagster-integration](./dagster-integration/) | Dagster + lakeFS workflows | High |
| [lakefs-mount-demo](./lakefs-mount-demo/) | lakeFS mount with Git integration | Medium |

## Prerequisites

- Docker and Docker Compose installed
- For ML examples: adequate disk space (see individual READMEs)
- For LLM examples: OpenAI API key

## Quick Start

1. Navigate to an example directory
2. Run the stack:
   ```bash
   # Full local stack (lakeFS + MinIO + Jupyter)
   docker compose --profile local-lakefs up

   # Or connect to existing lakeFS
   docker compose up
   ```
3. Open Jupyter at http://localhost:8888
4. Open lakeFS UI at http://localhost:8000

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| lakeFS | AKIAIOSFOLKFSSAMPLES | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY |
| MinIO | minioadmin | minioadmin |

## Shared Assets

The `_shared/` directory contains common utilities:
- `assets/lakefs_demo.py` - Helper functions for notebooks
- `images/` - Common images and logos

## Architecture Overview

```
lakeFS provides Git-like version control for data:

Repository (quickstart)
├── main branch (production)
│   ├── tables/
│   ├── models/
│   └── features/
├── dev branch (development)
└── experiment-1 branch (ML experiments)
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [lakeFS GitHub](https://github.com/treeverse/lakeFS)
- [lakeFS Slack](https://lakefs.io/slack)
