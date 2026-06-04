# Iceberg Examples with lakeFS

This directory contains examples demonstrating Apache Iceberg integration with lakeFS for versioned data lakehouse workflows.

## Examples

| Example | Description | Enterprise Required |
|---------|-------------|---------------------|
| [spark-basic](./spark-basic/) | Basic Spark + lakeFS integration | No |
| [spark-medallion](./spark-medallion/) | Medallion architecture (bronze/silver/gold) with Iceberg | Yes |
| [trino](./trino/) | Trino SQL queries with Iceberg REST Catalog | Yes |
| [write-audit-publish](./write-audit-publish/) | Write-Audit-Publish (WAP) pattern for data quality | No |

## Prerequisites

- Docker and Docker Compose installed
- For Enterprise examples: lakeFS Enterprise license

## Quick Start

Navigate to any example directory and run:

```bash
# For examples without local lakeFS:
docker compose up

# For full local stack:
docker compose --profile local-lakefs up
```

## Architecture

These examples demonstrate how lakeFS provides Git-like version control for Iceberg tables:

- **Branching**: Create isolated branches for development/testing
- **Commits**: Track changes with immutable commits
- **Merging**: Safely promote changes to production
- **Time Travel**: Query data at any point in history

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [lakeFS + Iceberg Guide](https://docs.lakefs.io/integrations/iceberg.html)
