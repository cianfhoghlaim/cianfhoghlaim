---
name: feast
description: Expert assistance for Feast feature store. Use when users need ML feature management, training-serving consistency, point-in-time correct joins, or real-time feature serving.
---

# Feast - Feature Store

**Version:** 0.40.x | **Last Updated:** 2025-01

## Overview

Feast is an open-source feature store for machine learning:

- **Training-Serving Consistency**: Same features for training and inference
- **Point-in-Time Correct**: Historical feature retrieval without data leakage
- **Real-Time Serving**: Low-latency online feature retrieval
- **Feature Registry**: Centralized feature definitions
- **Multiple Backends**: S3, BigQuery, Snowflake, Redis, PostgreSQL

**Documentation**: https://docs.feast.dev

## When to Use This Skill

Activate when users need:

- "Set up a feature store for ML"
- "Get historical features for training"
- "Serve features in real-time"
- "Prevent training-serving skew"
- "Store and retrieve embeddings"

## Core Concepts

### 1. Feature Store Configuration

```yaml
# feature_store.yaml
project: my_project
registry: data/registry.db
provider: local

online_store:
  type: sqlite
  path: data/online.db

offline_store:
  type: file

entity_key_serialization_version: 2
```

### 2. Entity Definition

```python
from feast import Entity

# Define entities (join keys)
customer = Entity(
    name="customer",
    join_keys=["customer_id"],
    description="Customer entity"
)

product = Entity(
    name="product",
    join_keys=["product_id"],
    description="Product entity"
)
```

### 3. Feature View

```python
from feast import FeatureView, Field, FileSource
from feast.types import Float32, Int64, String
from datetime import timedelta

# Data source
customer_source = FileSource(
    name="customer_stats_source",
    path="data/customer_stats.parquet",
    timestamp_field="event_timestamp"
)

# Feature view
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    ttl=timedelta(days=1),
    schema=[
        Field(name="total_purchases", dtype=Int64),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_order", dtype=Int64),
        Field(name="customer_segment", dtype=String),
    ],
    online=True,
    source=customer_source,
    tags={"team": "ml", "domain": "customers"}
)
```

### 4. On-Demand Feature View

```python
from feast import on_demand_feature_view, Field
from feast.types import Float32
import pandas as pd

@on_demand_feature_view(
    sources=[customer_features],
    schema=[
        Field(name="purchase_velocity", dtype=Float32),
    ]
)
def customer_derived_features(inputs: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame()
    df["purchase_velocity"] = (
        inputs["total_purchases"] /
        (inputs["days_since_last_order"] + 1)
    )
    return df
```

### 5. Feature Service

```python
from feast import FeatureService

# Group features for a model
customer_model_v1 = FeatureService(
    name="customer_model_v1",
    features=[
        customer_features[["total_purchases", "avg_order_value"]],
        customer_derived_features,
    ],
    tags={"model": "churn_prediction", "version": "1.0"}
)
```

### 6. Apply and Materialize

```python
from feast import FeatureStore
from datetime import datetime, timedelta

store = FeatureStore(repo_path="feature_repo")

# Apply feature definitions
store.apply([
    customer,
    customer_source,
    customer_features,
    customer_derived_features,
    customer_model_v1,
])

# Materialize to online store
store.materialize_incremental(end_date=datetime.utcnow())

# Or full materialization
store.materialize(
    start_date=datetime.utcnow() - timedelta(days=30),
    end_date=datetime.utcnow()
)
```

### 7. Get Historical Features (Training)

```python
import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

# Entity DataFrame with timestamps (for point-in-time correct joins)
entity_df = pd.DataFrame({
    "customer_id": [1001, 1002, 1003],
    "event_timestamp": pd.to_datetime([
        "2024-01-15 10:00:00",
        "2024-01-16 14:00:00",
        "2024-01-17 09:00:00",
    ])
})

# Get historical features
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_features:total_purchases",
        "customer_features:avg_order_value",
        "customer_derived_features:purchase_velocity",
    ]
).to_df()

# Or use feature service
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=customer_model_v1,
).to_df()
```

### 8. Get Online Features (Inference)

```python
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

# Single entity
features = store.get_online_features(
    features=[
        "customer_features:total_purchases",
        "customer_features:avg_order_value",
    ],
    entity_rows=[{"customer_id": 1001}]
).to_dict()

# Batch entities (recommended)
features = store.get_online_features(
    features=customer_model_v1,
    entity_rows=[
        {"customer_id": 1001},
        {"customer_id": 1002},
        {"customer_id": 1003},
    ]
).to_dict()
```

### 9. Push Features (Real-Time)

```python
from feast import FeatureStore, PushSource
from feast.data_format import JsonFormat

# Define push source
push_source = PushSource(
    name="customer_activity_push",
    batch_source=customer_source,
)

# Push feature view
realtime_features = FeatureView(
    name="customer_realtime",
    entities=[customer],
    ttl=timedelta(hours=1),
    schema=[
        Field(name="recent_page_views", dtype=Int64),
        Field(name="cart_value", dtype=Float32),
    ],
    source=push_source,
    online=True,
)

# Push data
store.push(
    "customer_activity_push",
    pd.DataFrame({
        "customer_id": [1001],
        "recent_page_views": [15],
        "cart_value": [149.99],
        "event_timestamp": [datetime.utcnow()],
    })
)
```

### 10. Production Configuration

```yaml
# feature_store.yaml (AWS Production)
project: my_project

registry:
  registry_type: sql
  path: postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}/feast

provider: aws

online_store:
  type: dynamodb
  region: us-west-2

offline_store:
  type: redshift
  cluster_id: my-cluster
  region: us-west-2
  database: features
  user: feast
  s3_staging_location: s3://bucket/feast-staging/
```

## Integration Patterns

### FastAPI
```python
from fastapi import FastAPI
from feast import FeatureStore

app = FastAPI()
store = FeatureStore(repo_path="feature_repo")

@app.post("/predict")
async def predict(customer_ids: list[int]):
    features = store.get_online_features(
        features=["customer_features:total_purchases"],
        entity_rows=[{"customer_id": id} for id in customer_ids]
    ).to_dict()

    # Use features for prediction
    return {"features": features}
```

### Airflow Materialization
```python
from airflow.operators.python import PythonOperator

def materialize(**context):
    from feast import FeatureStore
    store = FeatureStore(repo_path="/path/to/repo")
    store.materialize(
        start_date=context["data_interval_start"],
        end_date=context["data_interval_end"]
    )

materialize_task = PythonOperator(
    task_id="materialize",
    python_callable=materialize,
)
```

## Online Store Selection

| Store | Latency | Use Case |
|-------|---------|----------|
| SQLite | ~10ms | Development |
| Redis | <1ms | Production |
| DynamoDB | <5ms | Serverless |
| PostgreSQL | ~5ms | Flexibility |
| Cassandra | <5ms | High write volume |

## Best Practices

1. **Use Feature Services**: Version features with models
2. **Set TTL**: Prevent stale features
3. **Incremental Materialization**: Use `materialize_incremental`
4. **Batch Online Requests**: Fetch multiple entities at once
5. **SQL Registry**: Use SQL registry in production
6. **Point-in-Time Joins**: Always include timestamps
7. **Monitor Freshness**: Track materialization lag

## Troubleshooting

### Training-Serving Skew
1. Use feature services for consistency
2. Verify timestamp handling
3. Compare training vs serving values

### Stale Features
1. Check materialization schedule
2. Verify TTL configuration
3. Monitor materialization lag

### Slow Serving
1. Use Redis instead of SQLite
2. Batch entity requests
3. Reduce feature service size

### Registry Conflicts
1. Use SQL registry
2. Configure cache TTL
3. Avoid concurrent applies

## Resources

- **Documentation**: https://docs.feast.dev
- **Tutorials**: https://docs.feast.dev/getting-started/quickstart
- **GitHub**: https://github.com/feast-dev/feast
- **Slack**: https://slack.feast.dev
