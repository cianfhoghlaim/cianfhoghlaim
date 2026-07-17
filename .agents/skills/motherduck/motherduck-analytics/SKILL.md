---
name: motherduck-analytics
description: Run analytics on MotherDuck data. Use when writing DuckDB SQL queries, building Dives (live React + SQL dashboards), composing a dashboard with KPIs + trends + breakdowns, exploring databases / tables / columns, sharing databases zero-copy with team members or organisations, or running query optimisation. Covers the full DuckDB SQL dialect reference (window functions, QUALIFY, macros, CTEs, extensions, hints for performance), the Dive authoring model, the explore API, and the data-share semantics. Triggers: 'SELECT', 'CTE', 'window function', 'QUALIFY', 'CREATE DIVE', 'Dive authoring', 'KPI', 'breakdown', 'data share', 'zero-copy share', 'explore tables'.
---

# MotherDuck — Analytics, Dives & Sharing

Run analytics, build Dives, share data. Absorbs the former
`motherduck-query`, `motherduck-duckdb-sql`, `motherduck-create-dive`,
`motherduck-build-dashboard`, `motherduck-explore`, and
`motherduck-share-data` skills.

## When to use this skill

Use this skill when:

- Writing any DuckDB SQL against a MotherDuck database.
- Building a **Dive** (live React + SQL component) for an
  internal or external consumer.
- Composing a **dashboard** of KPIs + trends + breakdowns on
  top of existing MotherDuck data.
- Exploring a database you haven't seen (find tables, columns,
  sample data).
- Sharing a database zero-copy with another team or org.

For storage pattern and ingestion, use the `motherduck-architecture`
and `motherduck-data-modeling` sister skills.

## DuckDB SQL dialect (the KCG cheatsheet)

DuckDB is a SQL superset. Most ANSI SQL works. The differences
from PostgreSQL matter most:

| Feature | DuckDB | PostgreSQL | KCG use |
|:--|:--|:--|:--|
| `QUALIFY` | ✅ | ❌ (use subquery) | filter window results inline |
| `SELECT * EXCLUDE (col)` | ✅ | ❌ | column-drop without naming the rest |
| `SELECT * REPLACE (col AS alias)` | ✅ | ❌ | rename in place |
| `STRUCT` / `LIST` / `MAP` | ✅ first-class | JSONB workaround | nested data |
| `unnest()` | ✅ | ✅ with `LATERAL` | list-to-rows |
| `PIVOT` / `UNPIVOT` | ✅ | ❌ manual CASE | reshape |
| `SAMPLE 10%` | ✅ | ❌ | cheap sampling |
| `GROUP BY ALL` | ✅ | ❌ | no enumerate |
| `ORDER BY ALL` | ✅ | ❌ | no enumerate |
| `WITH ... AS MATERIALIZED` | ✅ (force materialise CTE) | ❌ | query-planning hint |
| `EXPLAIN ANALYZE` | ✅ | ✅ | performance debug |
| `COPY ... TO ...` | ✅ local + S3 | ✅ local only | export to Parquet |

Always use **window functions + QUALIFY** for ranking queries
instead of subqueries:

```sql
-- Find the top 3 most recent papers per author
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY author_id
                              ORDER BY published_at DESC) AS rn
    FROM papers
) t
WHERE rn <= 3;

-- Same thing with QUALIFY
SELECT *
FROM papers
QUALIFY ROW_NUMBER() OVER (PARTITION BY author_id
                           ORDER BY published_at DESC) <= 3;
```

## Query optimisation (the 3 high-impact rules)

1. **Filter before joining** — DuckDB optimises this, but the
   planner can be conservative. Use CTEs to make the intent
   explicit: `WITH filtered AS (SELECT * FROM x WHERE ...)` then
   join.
2. **Use `EXPLAIN ANALYZE` on any query > 1 second** — look
   for `UNNEST` and `HASH JOIN` rows that balloon the row
   count.
3. **Materialise CTEs that are joined more than once** — add
   `AS MATERIALIZED` to avoid re-computation.

```sql
WITH MATERIALIZED recent_orders AS (
    SELECT * FROM orders WHERE created_at > now() - INTERVAL '7 days'
)
SELECT a.id, COUNT(*) AS order_count
FROM accounts a
JOIN recent_orders o ON o.account_id = a.id
GROUP BY a.id;
```

## Dive authoring (the 3-surface layout)

A Dive is a live React + SQL component. It has 3 surfaces:

1. **KPI surface** — a single big number (revenue today, MAU,
   total users). One query, one result.
2. **Trend surface** — a time-series chart (revenue by day, MAU
   by week). One query, a time column + a metric column.
3. **Breakdown surface** — a categorical chart (revenue by
   persona, MAU by nation). One query, a categorical column + a
   metric column.

A good Dive is 3 surfaces max, each with a 1-line title and a
1-line subtitle. Anything more is a marimo notebook, not a Dive.

```sql
-- Example: revenue KPI
SELECT SUM(amount) AS revenue_today
FROM cianfhoghlaim.curriculum_dlt.ie_education_revenue
WHERE date = CURRENT_DATE;
```

## Dashboard composition (KPI + trend + breakdown)

For a multi-Dive dashboard, use the `motherduck-build-dashboard`
pattern:

```
+---------------------------------------------+
|  KPI: revenue_today = $42,500  (Dive 1)     |
+---------------------------------------------+
|  Trend: revenue by day, last 30 days (D2)   |
|  ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇█▇▆▅▄▃▂▁            |
+---------------------------------------------+
|  Breakdown: revenue by persona (D3)         |
|  aletum     ████████  42%                    |
|  cianfhoghlaim ████  21%                     |
|  carlcashman ██  11%                         |
+---------------------------------------------+
```

The Dives are independent (each has its own query); the dashboard
is a thin React wrapper that lays them out.

## Explore (find what's in a database)

When you don't know the database, use `INFORMATION_SCHEMA` queries:

```sql
-- List all schemas
SELECT schema_name
FROM information_schema.schemata
WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'main')
ORDER BY schema_name;

-- List all tables in a schema
SELECT table_name, table_type
FROM information_schema.tables
WHERE table_schema = 'cianfhoghlaim_curriculum'
ORDER BY table_name;

-- Sample a table
SELECT * FROM cianfhoghlaim_curriculum.ie_education_primary
USING SAMPLE 10 ROWS;
```

The `motherduck-explore` skill's content is captured in this
section.

## Data sharing (zero-copy)

MotherDuck supports zero-copy shares between organisations. The
flow:

```sql
-- Owner side: create the share
CREATE SHARE cianfhoghlaim_curriculum_share
FROM DATABASE cianfhoghlaim_curriculum;

-- Recipient side: list available shares
SELECT * FROM information_schema.shares;

-- Recipient side: attach the share
ATTACH 'md:cianfhoghlaim_curriculum_share' AS shared_curriculum
    (READ_ONLY);
```

Shares are zero-copy (no data movement). The recipient can query
the shared database but cannot modify it. The owner can revoke
at any time with `DROP SHARE`.

## Pair this skill with

- `motherduck-architecture/SKILL.md` — storage pattern
- `motherduck-data-modeling/SKILL.md` — schema design
- `motherduck-connections/SKILL.md` — wiring (Postgres endpoint, MCP)
- `marimo/SKILL.md` — for richer dashboards that need Python
  reactivity (Dives are pure SQL)

## Cross-references

- [DuckDB SQL reference](https://duckdb.org/docs/sql/introduction)
- [MotherDuck Dives docs](https://motherduck.com/docs/dives)
- [MotherDuck shares](https://motherduck.com/docs/sharing)
