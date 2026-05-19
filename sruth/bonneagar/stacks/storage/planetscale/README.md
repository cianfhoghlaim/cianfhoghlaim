# PlanetScale - Managed PostgreSQL ($5/mo)

Serverless PostgreSQL with automatic scaling, branching, and point-in-time recovery.

## Migration Candidates

| Service | Current State | Migration Priority |
|---------|--------------|-------------------|
| Langfuse | Self-hosted PostgreSQL | High |
| MLflow | Self-hosted PostgreSQL | Medium |
| Cognee | Self-hosted PostgreSQL | Medium |

## Connection

```python
import psycopg2

conn = psycopg2.connect(
    host="eu-west-3.pg.psdb.cloud",
    port=5432,
    database="langfuse",
    user=os.getenv("PLANETSCALE_USERNAME"),
    password=os.getenv("PLANETSCALE_PASSWORD"),
    sslmode="require"
)
```

## Environment Variables

```bash
# Set in secrets.env
export PLANETSCALE_HOST="eu-west-3.pg.psdb.cloud"
export PLANETSCALE_DATABASE="langfuse"
export PLANETSCALE_USERNAME="{{ infisical://taisce-secrets/planetscale/username }}"
export PLANETSCALE_PASSWORD="{{ infisical://taisce-secrets/planetscale/password }}"
```

## Features

- **Branching**: Create isolated database branches for testing
- **Connection pooling**: Built-in connection pooler
- **Auto-scaling**: Scales automatically based on load
- **Point-in-time recovery**: Restore to any point in time

## Migration Steps

### 1. Create PlanetScale Database

```bash
pscale database create langfuse --region eu-west-3
pscale branch create langfuse main
pscale password create langfuse main production
```

### 2. Export from Self-Hosted

```bash
pg_dump -h localhost -U langfuse -d langfuse > langfuse_backup.sql
```

### 3. Import to PlanetScale

```bash
pscale connect langfuse main --port 3309 &
psql -h 127.0.0.1 -p 3309 -d langfuse < langfuse_backup.sql
```

### 4. Update Langfuse Configuration

Update `bonneagar/storage/langfuse/secrets.env`:

```env
# Switch to PlanetScale
DATABASE_URL=postgresql://${PLANETSCALE_USERNAME}:${PLANETSCALE_PASSWORD}@${PLANETSCALE_HOST}:5432/${PLANETSCALE_DATABASE}?sslmode=require
```

## Pricing

- **Free Tier**: 5GB storage, 1 billion reads/month
- **Scaler ($5/mo)**: 10GB storage, unlimited reads
- **Enterprise**: Custom pricing

## Databases

| Database | Service | Storage Estimate |
|----------|---------|-----------------|
| langfuse | LLM observability | 2GB |
| mlflow | Experiment tracking | 1GB |
| cognee | AI memory | 1GB |
