# ML/AI Examples with lakeFS

This directory contains examples demonstrating machine learning and AI workflows with lakeFS for data versioning and reproducibility.

## Examples

| Example | Description | Requirements |
|---------|-------------|--------------|
| [llm-langchain](./llm-langchain/) | AI agents with LangChain + OpenAI | OpenAI API key |
| [image-segmentation](./image-segmentation/) | PyTorch + MLflow ML reproducibility | ~10GB disk |
| [ml-reproducibility](./ml-reproducibility/) | ML experimentation tracking | ~4GB disk |

## Why lakeFS for ML?

- **Data Versioning**: Track exact datasets used for each training run
- **Reproducibility**: Recreate any experiment by checking out the corresponding data version
- **Feature Store**: Version feature tables alongside model artifacts
- **A/B Testing**: Use branches to test different data preprocessing strategies
- **Lineage**: Track which data produced which model

## Quick Start

Navigate to any example directory and run:

```bash
docker compose --profile local-lakefs up
```

## Architecture

```
lakeFS Repository
├── main branch (production data)
├── experiment-1 branch (training data v1)
├── experiment-2 branch (training data v2)
└── feature-engineering branch (new features)
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [ML Reproducibility Guide](https://docs.lakefs.io/use_cases/ml.html)
- [lakeFS + MLflow](https://docs.lakefs.io/integrations/mlflow.html)
