# LanceDB Cloud

LanceDB Cloud is the managed, serverless LanceDB offering. It runs
in 4 regions and includes auto-compaction + auto-reindexing.

## Regions

- `us-east-1` (Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland) — **the KCG region**, closest to Galway
- `ap-south-1` (Mumbai)

## Connection

```python
import lancedb
import os

db = lancedb.connect(
    "db://my-database",
    api_key=os.environ["LANCEDB_API_KEY"],
    region="eu-west-1",
)
```

Or via env vars:

```bash
# .env
LANCEDB_URI=db://my-database
LANCEDB_API_KEY=...
LANCEDB_REGION=eu-west-1
```

```python
db = lancedb.connect(
    os.environ["LANCEDB_URI"],
    api_key=os.environ["LANCEDB_API_KEY"],
    region=os.environ["LANCEDB_REGION"],
)
```

## Features

| Feature | Description |
|:--|:--|
| **Auto-compaction** | Runs every 5 minutes; no manual `compact()` needed |
| **Auto-reindexing** | Re-creates HNSW index on every 1k writes |
| **Multi-region** | Pick the region closest to your data |
| **Serverless** | No instance management; pay per query + storage |
| **Backups** | Daily snapshots, point-in-time recovery |
| **Encryption at rest** | AES-256 |
| **Private endpoints** | Available on Enterprise plan |

## Pricing model

- **Storage**: per GB per month (varies by region)
- **Queries**: per 1k vector queries
- **Writes**: per 1k rows inserted
- **Free tier**: 100 GB storage, 10M queries/month

For KCG production, use LanceDB Cloud in `eu-west-1` for the
leabharlann + curriculum indexes.

## Local → Cloud migration

```python
# 1. Local LanceDB
local_db = lancedb.connect("./lancedb_data")
table = local_db.open_table("my_table")
print(f"{table.count_rows()} rows")

# 2. Cloud LanceDB
cloud_db = lancedb.connect("db://my-database", api_key=..., region="eu-west-1")
cloud_table = cloud_db.create_table("my_table", schema=table.schema, mode="overwrite")

# 3. Bulk copy
batch = []
for batch_start in range(0, table.count_rows(), 1000):
    df = table.to_pandas().iloc[batch_start:batch_start+1000]
    batch.append(df)
cloud_table.add(batch)
```

## Cloudflare R2 + LanceDB Cloud

For a self-hosted R2 backend (the KCG production target), use the
rclone-sidecar Compose pattern (see
`references/hosting-lancedb-docker-compose.md` for the docker-compose
example). The pattern:

1. Run an rclone container mounted as a FUSE filesystem at `/data/lance`
2. Run the LanceDB-using service with `/data/lance` mounted
3. rclone syncs the local `/data/lance` to R2 every N minutes
