# MotherDuck - Cloud DuckDB

Cloud-hosted DuckDB with serverless scaling and collaboration features.

## Connection

```python
import duckdb

# MotherDuck connection (authenticates via browser or token)
con = duckdb.connect('md:oideachas_education')

# With explicit token
con = duckdb.connect('md:oideachas_education?motherduck_token=YOUR_TOKEN')
```

## Environment Variables

```bash
# Set in .env or secrets
export MOTHERDUCK_TOKEN="{{ infisical://taisce-secrets/motherduck/token }}"
```

## Databases

| Database | Pipeline | Purpose |
|----------|----------|---------|
| `oideachas_education` | sruth/oideachais | Curriculum analytics |
| `crypteolas_defi` | sruth/crypteolas | DeFi protocol data |
| `aleyum_market` | sruth/aleyum | Art market analytics |

## Usage with DLT

```python
import dlt

pipeline = dlt.pipeline(
    pipeline_name="curriculum",
    destination=dlt.destinations.motherduck(
        credentials="md:oideachas_education"
    )
)
```

## Usage with Dagster

```python
from dagster import asset, AssetExecutionContext
import duckdb

@asset
def curriculum_metrics(context: AssetExecutionContext):
    con = duckdb.connect('md:oideachas_education')
    return con.execute("SELECT * FROM curriculum.metrics").df()
```

## Iceberg Integration

Query Iceberg tables from R2 storage:

```sql
-- Attach Iceberg catalog via R2
CREATE TABLE curriculum_iceberg AS
  SELECT * FROM iceberg_scan(
    's3://iceberg/curriculum/',
    allow_moved_paths = true
  );
```

## 21-Day Trial Notes

- Trial expires: [Set after activation]
- Includes: 10GB storage, unlimited compute
- Upgrade path: $20/month for 100GB
