# Iceberg Medallion Architecture with lakeFS

This example demonstrates the medallion architecture (bronze/silver/gold) pattern using Apache Iceberg tables with lakeFS version control.

## Overview

The medallion architecture organizes data into three layers:

- **Bronze**: Raw ingested data (as-is from source)
- **Silver**: Cleaned and validated data
- **Gold**: Business-level aggregations and features

Combined with lakeFS branching, you can:
- Develop transformations on isolated branches
- Test data quality before promotion
- Roll back any layer independently

## Prerequisites

- Docker and Docker Compose installed
- lakeFS Enterprise (for Iceberg REST Catalog)
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

- **iceberg-books-spark-medallion.ipynb** - Full medallion architecture demo

## What You'll Learn

- Setting up bronze/silver/gold Iceberg tables
- Using lakeFS branches for layer isolation
- Atomic promotion between layers
- Data quality validation at each stage

## Note

This example requires **lakeFS Enterprise** for the Iceberg REST Catalog functionality.

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [lakeFS + Iceberg](https://docs.lakefs.io/integrations/iceberg.html)
