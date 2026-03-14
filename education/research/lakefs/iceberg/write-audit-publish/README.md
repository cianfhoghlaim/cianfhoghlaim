# Write-Audit-Publish (WAP) Pattern with lakeFS

This example demonstrates the Write-Audit-Publish pattern for data quality assurance using Apache Iceberg branches with lakeFS.

## Overview

The WAP pattern ensures data quality before publishing to production:

1. **Write**: Write new data to an isolated branch
2. **Audit**: Run validation and quality checks
3. **Publish**: Merge to production only if checks pass

This pattern is essential for:
- Preventing bad data from reaching production
- Enabling data quality gates in pipelines
- Supporting rollback when issues are detected

## Prerequisites

- Docker and Docker Compose installed
- ~4GB disk space

## Quick Start

```bash
# Start with local lakeFS stack
docker compose --profile local-lakefs up

# Or connect to existing lakeFS
docker compose up
```

Then open:
- Jupyter: http://localhost:8888
- lakeFS UI: http://localhost:8000

## Notebook

- **wap-iceberg.ipynb** - Write-Audit-Publish workflow demo

## What You'll Learn

- Creating isolated write branches
- Running data quality validations
- Conditional merging based on audit results
- Rolling back failed publishes

## WAP Workflow

```
main (production)
  │
  └── write-branch
        │
        ├── Write new data
        ├── Run quality checks
        │
        └── If pass: Merge to main
            If fail: Delete branch
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Write-Audit-Publish Guide](https://docs.lakefs.io/use_cases/production_data.html)
- [Data Quality with lakeFS](https://docs.lakefs.io/use_cases/data_quality.html)
