---
name: sqlmesh
description: Expert assistance for data transformation with SQLMesh. Use when users need data transformation, dbt alternatives, DuckDB integration, or version-controlled SQL transformations.
---

# SQLMesh - Data Transformation Framework

**Version:** >=0.228.1 | **Last Updated:** 2025-04

## Overview

SQLMesh is a modern data transformation framework with DuckDB integration:

- **DuckDB Native**: Built-in DuckDB support for fast local development
- **Virtual Data Environments**: Isolated environments for testing and development
- **Forward-Only Changes**: Non-breaking schema evolution
- **Type Safety**: SQL type checking and validation
- **Incremental Processing**: Efficient incremental model execution

**Documentation**: https://sqlmesh.com/docs

## When to Use This Skill

Activate when users need:

- "Create data transformations with SQL"
- "Build dbt-like pipelines with DuckDB"
- "Implement incremental data processing"
- "Version control SQL transformations"
- "Test data transformations in isolation"

## Core Concepts

### 1. Basic Model Definition

```python
# models/orders.sql
MODEL (
    name db.orders,
    kind FULL,
    cron '@daily',
    grain order_id,
    changes (
        order_date,
        customer_id,
        total_amount
    )
);

SELECT
    o.order_id,
    o.order_date,
    o.customer_id,
    SUM(oi.quantity * oi.price) as total_amount
FROM
    raw_orders o
    JOIN raw_order_items oi ON o.order_id = oi.order_id
GROUP BY
    o.order_id, o.order_date, o.customer_id
```

### 2. Incremental Models

```python
# models/customer_metrics.sql
MODEL (
    name db.customer_metrics,
    kind INCREMENTAL_BY_TIME_RANGE (
        time_column order_date
    ),
    cron '@daily',
    grain customer_id
);

SELECT
    customer_id,
    order_date,
    COUNT(*) as orders_count,
    SUM(total_amount) as total_spent
FROM
    db.orders
WHERE
    order_date >= @start_date
    AND order_date < @end_date
GROUP BY
    customer_id, order_date
```

### 3. DuckDB Integration

```python
# config.py
from sqlmesh.core.config import Config
from sqlmesh.core.engine_adapter.duckdb import DuckDBEngineAdapter

config = Config(
    engine_adapter_type="duckdb",
    engine_adapter=DuckDBEngineAdapter,
    engine_connection={
        "database": "./data/warehouse.duckdb"
    }
)
```

### 4. Virtual Data Environments

```bash
# Create a new environment
sqlmesh plan dev --from prod

# Test changes in isolation
sqlmesh run dev

# Promote to production
sqlmesh promote dev
```

### 5. Model Dependencies

```python
# models/revenue.sql
MODEL (
    name db.revenue,
    kind FULL,
    depends_on (
        db.orders,
        db.customer_metrics
    )
);

SELECT
    DATE_TRUNC('month', order_date) as month,
    COUNT(DISTINCT customer_id) as active_customers,
    SUM(total_amount) as total_revenue
FROM
    db.orders
GROUP BY
    DATE_TRUNC('month', order_date)
```

## Advanced Features

### Forward-Only Changes

SQLMesh automatically handles schema evolution without breaking existing data:

```python
# Adding a new column
MODEL (
    name db.orders,
    kind FULL,
    changes (
        order_date,
        customer_id,
        total_amount,
        discount_amount  -- New column added
    )
);
```

### Macros

```python
# macros/common.sql
MACRO calculate_discount(total_amount, discount_rate) AS (
    total_amount * (1 - discount_rate)
);

# Usage in model
SELECT
    customer_id,
    total_amount,
    calculate_discount(total_amount, 0.1) as discounted_amount
FROM
    db.orders
```

### Tests

```python
# tests/orders_test.sql
MODEL (
    name db.orders_test,
    kind TEST,
    check (
        total_amount >= 0,
        order_date IS NOT NULL,
        customer_id IS NOT NULL
    )
);

SELECT * FROM db.orders
```

## Configuration

### Project Structure

```
project/
├── config/
│   └── config.py          # SQLMesh configuration
├── models/
│   ├── staging/          # Raw data models
│   ├── intermediate/     # Transformed models
│   └── marts/           # Final business logic
├── macros/
│   └── common.sql       # Reusable macros
└── tests/
    └── *_test.sql       # Model tests
```

### DuckDB Setup

```python
# config/config.py
from sqlmesh.core.config import Config

config = Config(
    engine_adapter_type="duckdb",
    engine_connection={
        "database": "./data/warehouse.duckdb"
    },
    default_catalog="main",
    default_schema="analytics",
    time_column_format="%Y-%m-%d"
)
```

## Best Practices

### Model Design

1. **Grain Definition**: Always specify grain for incremental models
2. **Change Tracking**: Use `changes` for schema evolution
3. **Dependencies**: Explicitly declare model dependencies

### Performance

1. **Incremental Processing**: Use incremental models for large datasets
2. **Partitioning**: Partition by time for efficient queries
3. **Materialization**: Choose appropriate model kind (FULL/INCREMENTAL)

### Testing

1. **Unit Tests**: Write tests for business logic
2. **Data Quality**: Add data quality checks
3. **Integration Tests**: Test in virtual environments

## Installation

```bash
pip install "sqlmesh[duckdb]"
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| ELT Pipelines | DuckDB + incremental models |
| Analytics | Materialized views with virtual environments |
| Data Quality | Test models with assertions |
| Schema Evolution | Forward-only changes |

### Related Skills

- [`dagster`](.skills/dagster/SKILL.md) - Orchestration for SQLMesh
- [`dlt`](.skills/dlt/SKILL.md) - Data loading into DuckDB
- [`duckdb`](.skills/duckdb/SKILL.md) - DuckDB database
