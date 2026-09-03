---
name: ibis
description: Expert assistance for Ibis portable dataframe library. Use when users need backend-agnostic analytics, pandas migration, SQL generation, or switching between DuckDB, BigQuery, Snowflake, and other backends. KCG-preferred analytics layer over the BIEP `md:cianfhoghlaim` MotherDuck database — `ibis.duckdb.connect("md:cianfhoghlaim")` is the canonical entrypoint for the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) and `gov.ie` circulars.
---

# Ibis - Portable Dataframe Library

**Version:** 9.x | **Last Updated:** 2025-01

## Overview

Ibis provides portable dataframe operations across analytical backends:

- **Backend Agnostic**: Same code, different backends (DuckDB, BigQuery, Snowflake, etc.)
- **Deferred Execution**: Build expressions, execute when needed
- **SQL Generation**: Inspect generated SQL for debugging
- **Pandas Migration**: Similar API, lazy evaluation
- **Type Safety**: Rich type system with inference

**Documentation**: https://ibis-project.org

## When to Use This Skill

Activate when users need:

- "Write analytics code that works on multiple backends"
- "Migrate pandas code to work with databases"
- "Build dataframe queries for BigQuery/Snowflake"
- "Generate SQL from Python expressions"
- "Process data locally then scale to cloud"

## Core Concepts

### 1. Connection and Basic Operations

```python
import ibis
from ibis import _  # Deferred expression

# Connect to backend
con = ibis.duckdb.connect()  # In-memory
con = ibis.duckdb.connect("data.duckdb")  # File

# Read data
t = con.read_parquet("data.parquet")
t = con.read_csv("data.csv")
t = con.table("existing_table")

# In-memory table
t = ibis.memtable({"a": [1, 2, 3], "b": ["x", "y", "z"]})
```

### 2. Basic Query Chain

```python
import ibis
from ibis import _

con = ibis.duckdb.connect()
t = con.read_parquet("sales.parquet")

result = (
    t
    .filter(_.date >= "2024-01-01")
    .mutate(revenue=_.quantity * _.price)
    .group_by("region")
    .aggregate(
        total_revenue=_.revenue.sum(),
        order_count=_.count()
    )
    .order_by(ibis.desc("total_revenue"))
)

# Execute and get pandas DataFrame
df = result.to_pandas()
```

### 3. Filtering

```python
# Single condition
t.filter(_.status == "active")

# Multiple conditions (AND)
t.filter(_.date >= "2024-01-01", _.amount > 100)

# OR conditions
t.filter((_.region == "US") | (_.region == "EU"))

# IN condition
t.filter(_.category.isin(["A", "B", "C"]))

# NULL handling
t.filter(_.value.notnull())
t.filter(_.value.isnull())

# String matching
t.filter(_.name.like("%Smith%"))
t.filter(_.email.contains("@gmail.com"))
```

### 4. Mutate (Add/Modify Columns)

```python
# Add new columns
t.mutate(
    revenue=_.quantity * _.price,
    year=_.date.year(),
    month=_.date.month()
)

# Conditional logic
t.mutate(
    size=ibis.case()
        .when(_.amount < 100, "small")
        .when(_.amount < 1000, "medium")
        .else_("large")
        .end()
)

# Using ifelse
t.mutate(
    is_large=(_.amount > 1000).ifelse("yes", "no")
)
```

### 5. Aggregations

```python
# Basic aggregation
t.aggregate(
    total=_.amount.sum(),
    average=_.amount.mean(),
    count=_.count(),
    unique_customers=_.customer_id.nunique()
)

# Grouped aggregation
t.group_by("region", "category").aggregate(
    total=_.amount.sum(),
    count=_.count()
)

# Conditional aggregation
t.group_by("country").aggregate(
    total=_.sales.sum(),
    us_sales=_.sales.sum(where=_.region == "US"),
    large_deals=_.count(where=_.value > 10000)
)
```

### 6. Joins

```python
# Inner join
orders.join(customers, orders.customer_id == customers.id)

# Left join
orders.left_join(customers, orders.customer_id == customers.id)

# Multiple join conditions
orders.join(
    products,
    [orders.product_id == products.id, orders.region == products.region]
)

# Select columns after join
orders.join(customers, orders.customer_id == customers.id).select(
    orders.order_id,
    orders.amount,
    customers.name
)
```

### 7. Window Functions

```python
# Running total
t.group_by("category").order_by("date").mutate(
    running_total=_.amount.sum()
)

# Ranking
t.group_by("category").order_by(ibis.desc("sales")).mutate(
    rank=ibis.row_number()
)

# Lag/Lead
t.group_by("customer_id").order_by("date").mutate(
    prev_amount=_.amount.lag(),
    next_amount=_.amount.lead()
)

# Moving average
t.group_by("product_id").order_by("date").mutate(
    moving_avg=_.amount.mean().over(
        ibis.window(preceding=6, following=0)
    )
)
```

### 8. Selectors

```python
import ibis.selectors as s

# Select columns by type
t.select(s.numeric())
t.select(s.string())
t.select(s.temporal())

# Select by pattern
t.select(s.startswith("user_"))
t.select(s.endswith("_id"))
t.select(s.contains("amount"))

# Apply transformation to multiple columns
t.mutate(s.across(s.numeric(), (_ - _.mean()) / _.std()))

# Exclude columns
t.select(~s.cols("internal_id", "created_at"))
```

### 9. Reusable Transformations

```python
def add_date_parts(table):
    return table.mutate(
        year=_.date.year(),
        month=_.date.month(),
        quarter=_.date.quarter(),
        day_of_week=_.date.day_of_week()
    )

def standardize_numeric(table):
    import ibis.selectors as s
    return table.mutate(
        s.across(s.numeric(), (_ - _.mean()) / _.std())
    )

# Use with pipe
result = t.pipe(add_date_parts).pipe(standardize_numeric)
```

### 10. Backend Switching

```python
import ibis

# Development: DuckDB
con_dev = ibis.duckdb.connect()
t = con_dev.read_parquet("data.parquet")

# Same query works on any backend
query = (
    t
    .filter(_.date >= "2024-01-01")
    .group_by("region")
    .aggregate(total=_.amount.sum())
)

# Execute locally
result_local = query.to_pandas()

# Production: BigQuery
con_prod = ibis.bigquery.connect(project_id="my-project")
t_prod = con_prod.table("dataset.sales")

# Same transformations work
query_prod = (
    t_prod
    .filter(_.date >= "2024-01-01")
    .group_by("region")
    .aggregate(total=_.amount.sum())
)
```

## Connection Reference

```python
# DuckDB
con = ibis.duckdb.connect()  # in-memory
con = ibis.duckdb.connect("file.duckdb")

# PostgreSQL
con = ibis.postgres.connect(
    host="localhost", port=5432,
    database="mydb", user="user", password="pass"
)
# Or connection string
con = ibis.connect("postgresql://user:pass@host:5432/db")

# BigQuery
con = ibis.bigquery.connect(project_id="my-project")

# Snowflake
con = ibis.snowflake.connect(
    user="user", password="pass",
    account="account",
    database="DB", schema="SCHEMA"
)

# SQLite
con = ibis.sqlite.connect("database.db")
```

## SQL Inspection

```python
# View generated SQL
print(ibis.to_sql(query))

# Execute raw SQL
result = con.sql("SELECT * FROM table WHERE value > 100")
```

## Pandas Migration Guide

| pandas | Ibis |
|--------|------|
| `df[df['x'] > 0]` | `t.filter(_.x > 0)` |
| `df['y'] = df['x'] * 2` | `t.mutate(y=_.x * 2)` |
| `df.groupby('a').sum()` | `t.group_by('a').aggregate(_.sum())` |
| `df.merge(other, on='id')` | `t.join(other, 'id')` |
| `df.sort_values('x')` | `t.order_by('x')` |
| `df.head(10)` | `t.limit(10)` |
| Result is eager | Result is lazy (call `.to_pandas()`) |

## Best Practices

1. **Use Deferred Expressions**: Build query chains with `_`
2. **Filter Early**: Apply filters before aggregations
3. **Use Selectors**: For bulk column operations
4. **Check SQL**: Use `ibis.to_sql()` to debug
5. **Develop with DuckDB**: Fast local testing
6. **Execute at End**: Call `.to_pandas()` only when needed

## Troubleshooting

### Wrong Package Installed
```bash
# Wrong: pip install ibis
# Right: pip install ibis-framework
pip install 'ibis-framework[duckdb]'
```

### Expression Not Executing
```python
# Ibis uses lazy evaluation
# This just builds the expression
result = t.filter(_.x > 0)

# This executes it
df = result.to_pandas()
```

### Column Name Issues
```python
# Check column names
print(t.columns)

# Access columns with special characters
t["column-with-dash"]
```

## Resources

- **Documentation**: https://ibis-project.org
- **API Reference**: https://ibis-project.org/reference/
- **Backends**: https://ibis-project.org/backends/
- **GitHub**: https://github.com/ibis-project/ibis

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) uses
Ibis as the **portable analytics layer** on top of the
`md:cianfhoghlaim` MotherDuck database. The canonical connection
is `ibis.duckdb.connect("md:cianfhoghlaim")` (where the
`MOTHERDUCK_TOKEN` env var comes from Infisical via the Locket
sidecar). The same Ibis expressions run against any of the 24
BIEP per-subject tables — making the marimo notebooks
backend-portable:

```python
import ibis
from ibis import _

# Canonical KCG entrypoint: MotherDuck + DuckLake via Ibis
con = ibis.duckdb.connect("md:cianfhoghlaim")

# 6 LC subjects × 2 languages × 2 levels — 24 partitions
SUBJECTS = [
    "mathematics", "chemistry", "geography",
    "gaeilge", "english", "computer_science",
]

# Read the BAML-extracted curriculum_syllabus table
syllabus = con.table("cianfhoghlaim.leaving_cert.curriculum_syllabus")

# Cross-subject topic-coverage query
topic_coverage = (
    syllabus
    .filter(_.subject.isin(SUBJECTS))
    .group_by(["subject", "level", "language"])
    .aggregate(
        n_modules=_.module_id.nunique(),
        avg_hours=_.hours.mean(),
        n_outcomes=_.learning_outcomes.count(),
    )
    .order_by([_.subject, _.level, _.language])
)

# Execute (lazy → DataFrame)
df = topic_coverage.to_pandas()
print(df.head(10))
```

**British-Isles Education pipeline use case:**

- **6 LC subjects × 2 languages × 2 levels** — the BIEP
  schema is `cianfhoghlaim.leaving_cert.curriculum_syllabus`
  partitioned by `(subject, level, language)`. The same Ibis
  expression runs against all 24 partitions.
- **`gov.ie` circulars** — join the curriculum tables against
  `cianfhoghlaim.education.ie.gov_circulars_archive` to cross-
  reference syllabus changes with Department-of-Education
  policy updates.
- **Cross-linguistic join** — pair the `en` and `ga` partitions
  of the same subject on `module_id` to verify the
  BAML `ExtractCrossLinguisticConcept` output:
  ```python
  en = syllabus.filter(_.language == "en", _.subject == "mathematics")
  ga = syllabus.filter(_.language == "ga", _.subject == "mathematics")
  bilingual = en.join(ga, en.module_id == ga.module_id)
  ```
- **Portable across 4 Dives** — the same `topic_coverage`
  expression runs against `lc_syllabus_topics`,
  `lc_exam_difficulty`, `lc_marking_complexity`,
  `gov_circulars_archive` (the 4 MotherDuck Dives).

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  sources that populate the BIEP tables
- [`.agents/skills/duckdb/SKILL.md`](../duckdb/SKILL.md) — the
  DuckDB-native federated SQL layer
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/ducklake/SKILL.md`](../ducklake/SKILL.md) —
  the DuckLake sink
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject notebooks that consume Ibis queries
