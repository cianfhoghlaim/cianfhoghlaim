# Delta Lake with lakeFS

This example demonstrates Delta Lake integration with lakeFS for versioned data lake workflows.

## Overview

Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and big data workloads. Combined with lakeFS, you get:

- **Git-like versioning** for Delta tables
- **Branch isolation** for safe experimentation
- **Atomic commits** across multiple tables
- **Time travel** at the repository level

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

- **delta-lake.ipynb** - Demonstrates Delta Lake versioning with lakeFS branching

## What You'll Learn

- Creating Delta tables on lakeFS
- Using branches for isolated development
- Merging changes safely to production
- Rolling back to previous versions

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Delta Lake](https://delta.io/)
- [lakeFS + Delta Lake Guide](https://docs.lakefs.io/integrations/delta.html)
