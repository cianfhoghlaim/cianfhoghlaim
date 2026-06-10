# Semantic Layer Reference

> Merged from 249 source files in `semantic_layer/` — Boring Semantic Layer (BSL) docs, Cube.js semantic layer, Cube UI Kit, Rill examples. 200+ prompt templates summarized as reference tables.

---

# Part 1: Boring Semantic Layer (BSL) — Ibis-based semantic query layer


## BSL Overview


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/README.md`

# Boring Semantic Layer (BSL)

The Boring Semantic Layer (BSL) is a lightweight semantic layer based on [Ibis](https://ibis-project.org/).

**Key Features:**
- **Lightweight**: `pip install boring-semantic-layer`
- **Ibis-powered**: Built on top of [Ibis](https://ibis-project.org/), supporting any database engine that Ibis integrates with (DuckDB, Snowflake, BigQuery, PostgreSQL, and more)
- **MCP-friendly**: Perfect for connecting LLMs to structured data sources

## Quick Start

```bash
pip install 'boring-semantic-layer[examples]'
```

**1. Define your ibis input table**

```python
import ibis

# Create a simple in-memory table
flights_tbl = ibis.memtable({
    "origin": ["JFK", "LAX", "JFK", "ORD", "LAX"],
    "carrier": ["AA", "UA", "AA", "UA", "AA"]
})
```

**2. Define a semantic table**

```python
from boring_semantic_layer import to_semantic_table
flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(origin=lambda t: t.origin)
    .with_measures(flight_count=lambda t: t.count())
)
```

**3. Query it**

```python
result_df = flights.group_by("origin").aggregate("flight_count").execute()
```

---

## 📚 Documentation

**[→ View the full documentation](https://boringdata.github.io/boring-semantic-layer/)**

---

*This project is a joint effort by [xorq-labs](https://github.com/xorq-labs/xorq) and [boringdata](https://www.boringdata.io/).*

*We welcome feedback and contributions!*

---

*Freely inspired by the awesome [Malloy](https://github.com/malloydata/malloy) project. We loved the vision, just took the Python route.*


## BSL Getting Started


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/getting-started.md`

# Getting Started with BSL

BSL (Boring Semantic Layer) is a lightweight semantic layer built on top of Ibis. It allows you to define your data models once and query them anywhere.

## Installation

```bash
pip install boring-semantic-layer
```

## Quick Start

Let's create your first Semantic Table using synthetic data in Ibis.

```setup_flights
import ibis
from boring_semantic_layer import to_semantic_table

# Create sample flight data
flights_tbl = ibis.memtable({
    "origin": ["NYC", "LAX", "NYC", "SFO", "LAX", "NYC", "SFO", "LAX"],
    "destination": ["LAX", "NYC", "SFO", "NYC", "SFO", "LAX", "LAX", "SFO"],
    "distance": [2789, 2789, 2902, 2902, 347, 2789, 347, 347],
    "duration": [330, 330, 360, 360, 65, 330, 65, 65],
})
```

You can then convert these tables in Semantic Tables that contains dimensios and measures definitions:

```define_semantic_table
# Define semantic table with dimensions and measures
flights_st = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin=lambda t: t.origin,
        destination=lambda t: t.destination,
    )
    .with_measures(
        flight_count=lambda t: t.count(),
        total_distance=lambda t: t.distance.sum(),
        avg_duration=lambda t: t.duration.mean(),
    )
)
```

## Query Your Data

Now let's query the semantic table by grouping flights by origin:

```query_by_origin
# Group flights by origin airport
result = flights_st.group_by("origin").aggregate(
    "flight_count",
    "total_distance",
    "avg_duration"
)
```

<bslquery code-block="query_by_origin"></bslquery>

You can also group by destination:

```query_by_destination
# Group flights by destination airport
result = flights_st.group_by("destination").aggregate(
    "flight_count",
    "total_distance"
)
```

<bslquery code-block="query_by_destination"></bslquery>

## Chat with Your Data

BSL includes a built-in chat interface to query your semantic models using natural language.

### 1. Install the agent extra

```bash
pip install 'boring-semantic-layer[agent]'

# Install your LLM provider
pip install langchain-anthropic  # or langchain-openai, langchain-google-genai
```

### 2. Set your API key

Create a `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...  # or OPENAI_API_KEY, GOOGLE_API_KEY
```

### 3. Start chatting

Try the built-in flights demo model (loads remote data automatically):

```bash
# Interactive mode
bsl chat --sm https://raw.githubusercontent.com/boringdata/boring-semantic-layer/main/examples/flights.yml

# Or pass a question directly
bsl chat --sm https://raw.githubusercontent.com/boringdata/boring-semantic-layer/main/examples/flights.yml \
  "What are the top 5 origins by flight count?"

```

### Create your own YAML model

Here's a minimal example showing how to define your own semantic model:

```yaml
# my_model.yaml - Minimal BSL semantic model

# Database profile - loads remote parquet into in-memory DuckDB
profile:
  type: duckdb
  database: ":memory:"
  tables:
    orders_tbl: "path/to/orders.parquet"

# Semantic model definition
orders:
  table: orders_tbl
  description: "Order data with categories and metrics"

  dimensions:
    category:
      expr: _.category
      description: "Product category"
    region:
      expr: _.region
      description: "Sales region"
    status: _.status

  measures:
    order_count:
      expr: _.count()
      description: "Total number of orders"
    total_sales:
      expr: _.amount.sum()
      description: "Total sales amount"
    avg_order_value:
      expr: _.amount.mean()
      description: "Average order value"
```

Then run:

```bash
bsl chat --sm my_model.yaml
```

See [Query Agent Chat](/examples/query-agent-chat) for full documentation on YAML models with joins and advanced features.

## Next Steps

- [Chat with your data](/examples/query-agent-chat) using natural language
- Define models in [YAML configuration](/examples/yaml-config)
- Configure database connections with [Profiles](/examples/profile)
- Learn how to [Build Semantic Tables](/examples/semantic-table) with dimensions, measures, and joins
- Explore [Query Methods](/examples/query-methods) for retrieving data
- Discover how to [Compose Models](/examples/compose) together


## BSL API Reference


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/reference.md`

# API Reference

Complete API documentation for the Boring Semantic Layer.

## Table Creation & Configuration

Methods for creating and configuring semantic tables.

### to_semantic_table()

```python
to_semantic_table(
    table: ibis.Table,
    name: str,
    description: str = None
) -> SemanticTable
```

Create a semantic table from an Ibis table. This is the primary entry point for building semantic models.

| Parameter | Type | Description |
|-----------|------|-------------|
| `table` | `ibis.Table` | Ibis table to build the model from |
| `name` | `str` | Unique identifier for the semantic table |
| `description` | `str` | Optional description of the semantic table |

**Example:**
```python
import ibis
from boring_semantic_layer import to_semantic_table

flights = ibis.read_parquet("flights.parquet")
flights_st = to_semantic_table(flights, "flights")
```

### with_dimensions()

```python
with_dimensions(
    **dimensions: Callable | Dimension
) -> SemanticTable
```

Define dimensions for grouping and analysis. Dimensions are attributes that categorize data.

**Example:**
```python
flights_st = flights_st.with_dimensions(
    origin=lambda t: t.origin,
    dest=lambda t: t.dest,
    carrier=lambda t: t.carrier
)
```

### with_measures()

```python
with_measures(
    **measures: Callable | Measure
) -> SemanticTable
```

Define aggregations and calculations. Measures are numeric values that can be aggregated.

**Example:**
```python
flights_st = flights_st.with_measures(
    flight_count=lambda t: t.count(),
    avg_delay=lambda t: t.arr_delay.mean(),
    total_distance=lambda t: t.distance.sum()
)
```

### from_yaml()

```python
from_yaml(
    yaml_path: str,
    connection: ibis.Connection = None
) -> dict[str, SemanticTable]
```

Load semantic models from a YAML configuration file. Returns a dictionary of semantic tables.

| Parameter | Type | Description |
|-----------|------|-------------|
| `yaml_path` | `str` | Path to YAML configuration file |
| `connection` | `ibis.Connection` | Optional Ibis connection for database tables |

**Example:**
```python
from boring_semantic_layer.yaml import from_yaml

models = from_yaml("models.yaml")
flights_st = models["flights"]
```

### Dimension Class

```python
Dimension(
    expr: Callable,
    description: str = None
)
```

Self-documenting dimension with description. Use for better API documentation.

**Example:**
```python
from boring_semantic_layer import Dimension

flights_st = flights_st.with_dimensions(
    origin=Dimension(
        expr=lambda t: t.origin,
        description="Airport code where the flight departed from"
    )
)
```

### Measure Class

```python
Measure(
    expr: Callable,
    description: str = None
)
```

Self-documenting measure with description. Use for better API documentation.

**Example:**
```python
from boring_semantic_layer import Measure

flights_st = flights_st.with_measures(
    avg_delay=Measure(
        expr=lambda t: t.arr_delay.mean(),
        description="Average arrival delay in minutes"
    )
)
```

### all()

```python
st.all()
```

Reference the entire dataset within measure definitions. Primarily used for percentage-of-total calculations.

**Example:**
```python
flights_st = to_semantic_table(data, "flights").with_measures(
    flight_count=lambda t: t.count(),
    pct_of_total=lambda t: (
        t.count() / t.all().count() * 100
    )
)
```

## Join Methods

Methods for composing semantic tables through joins.

### join_many()

```python
join_many(
    other: SemanticTable,
    on: Callable,
    name: str = None
) -> SemanticTable
```

One-to-many relationship join (LEFT JOIN). Use when the left table can match multiple rows in the right table.

| Parameter | Type | Description |
|-----------|------|-------------|
| `other` | `SemanticTable` | The semantic table to join with |
| `on` | `Callable` | Lambda function defining the join condition |
| `name` | `str` | Optional name for the joined table reference |

**Example:**
```python
flights_st = flights_st.join_many(
    carriers_st,
    on=lambda l, r: l.carrier == r.code,
    name="carrier_info"
)
```

### join_one()

```python
join_one(
    other: SemanticTable,
    on: Callable,
    name: str = None
) -> SemanticTable
```

One-to-one relationship join (INNER JOIN). Use when each row in the left table matches exactly one row in the right table.

**Example:**
```python
flights_st = flights_st.join_one(
    airports_st,
    on=lambda l, r: l.origin == r.code
)
```

### join_cross()

```python
join_cross(
    other: SemanticTable,
    name: str = None
) -> SemanticTable
```

Cross join (CARTESIAN PRODUCT). Creates all possible combinations of rows from both tables.

### join()

```python
join(
    other: SemanticTable,
    on: Callable,
    how: str = "inner",
    name: str = None
) -> SemanticTable
```

Custom join with flexible join type. Supports 'inner', 'left', 'right', 'outer', and 'cross'.

| Parameter | Type | Description |
|-----------|------|-------------|
| `other` | `SemanticTable` | The semantic table to join with |
| `on` | `Callable` | Lambda function defining the join condition |
| `how` | `str` | Join type: 'inner', 'left', 'right', 'outer', or 'cross' |
| `name` | `str` | Optional name for the joined table reference |

## Query Methods

Methods for querying and transforming semantic tables.

### group_by()

```python
group_by(
    *dimensions: str
) -> QueryBuilder
```

Group data by one or more dimension names. Returns a query builder for chaining with aggregate().

**Example:**
```python
result = flights_st.group_by("origin", "carrier").aggregate("flight_count")
```

### aggregate()

```python
aggregate(
    *measures: str,
    **kwargs
) -> ibis.Table
```

Calculate one or more measures. Can be used standalone or after group_by().

**Examples:**
```python
# Without grouping
total = flights_st.aggregate("flight_count")

# With grouping
by_origin = flights_st.group_by("origin").aggregate("flight_count", "avg_delay")
```

### filter()

```python
filter(
    condition: Callable
) -> SemanticTable
```

Apply conditions to filter data. Use lambda functions with Ibis expressions.

**Example:**
```python
delayed_flights = flights_st.filter(lambda t: t.arr_delay > 0)
```

### order_by()

```python
order_by(
    *columns: str | ibis.Expression
) -> ibis.Table
```

Sort query results. Use `ibis.desc()` for descending order.

**Example:**
```python
result = flights_st.group_by("origin").aggregate("flight_count")
result = result.order_by(ibis.desc("flight_count"))
```

### limit()

```python
limit(
    n: int
) -> ibis.Table
```

Restrict the number of rows returned.

**Example:**
```python
top_10 = result.order_by(ibis.desc("flight_count")).limit(10)
```

### mutate()

```python
mutate(
    **expressions: Callable | ibis.Expression
) -> ibis.Table
```

Add or transform columns in aggregated results. Useful for calculations after aggregation.

**Example:**
```python
result = flights_st.group_by("month").aggregate("revenue")
result = result.mutate(
    growth_rate=lambda t: (t.revenue - t.revenue.lag()) / t.revenue.lag() * 100
)
```

### select()

```python
select(
    *columns: str | ibis.Expression
) -> ibis.Table
```

Select specific columns from the result. Often used in nesting operations.

**Example:**
```python
result.select("origin", "flight_count")
```

## Nesting

Create nested data structures within aggregations.

### nest Parameter

```python
aggregate(
    *measures,
    nest={
        "nested_column": lambda t: t.group_by([...]) | t.select(...)
    }
)
```

Create nested arrays of structs within aggregation results. Useful for hierarchical data or subtotals.

**Example:**
```python
result = flights_st.group_by("carrier").aggregate(
    "total_flights",
    nest={
        "by_month": lambda t: t.group_by("month").aggregate("monthly_flights")
    }
)
```

## Charting

Generate visualizations from query results.

### chart()

```python
chart(
    result: ibis.Table,
    backend: str = "altair",
    spec: dict = None,
    format: str = "interactive"
) -> Chart
```

Create visualizations from query results. Supports Altair (default) and Plotly backends.

| Parameter | Type | Description |
|-----------|------|-------------|
| `result` | `ibis.Table` | Query result table to visualize |
| `backend` | `str` | "altair" or "plotly" |
| `spec` | `dict` | Custom Vega-Lite specification (for Altair) |
| `format` | `str` | "interactive", "json", "png", "svg" |

**Auto-detection:**
BSL automatically selects appropriate chart types:
- Single dimension + measure → Bar chart
- Time dimension + measure → Line chart
- Two dimensions + measure → Heatmap

**Example:**
```python
from boring_semantic_layer.chart import chart

result = flights_st.group_by("month").aggregate("flight_count")
chart(result, backend="altair")
```

## Dimensional Indexing

Create searchable catalogs of dimension values.

### index()

```python
index(
    dimensions: Callable | None = None,
    by: str = None,
    sample: int = None
) -> ibis.Table
```

Create a searchable catalog of unique dimension values with optional weighting and sampling.

| Parameter | Type | Description |
|-----------|------|-------------|
| `dimensions` | `Callable` | None (all dimensions) or lambda returning list of fields |
| `by` | `str` | Measure name for weighting results |
| `sample` | `int` | Number of rows to sample (for large datasets) |

**Examples:**
```python
# Index all dimensions
flights_st.index()

# Index specific dimensions
flights_st.index(lambda t: [t.origin, t.dest])

# Weight by measure
flights_st.index(by="flight_count")

# Sample large dataset
flights_st.index(sample=10000)
```

## Other

### MCP Integration

#### MCPSemanticModel()

```python
MCPSemanticModel(
    models: dict[str, SemanticTable] | str,
    description: str = None
)
```

Create an MCP server to expose semantic models to LLMs like Claude. Accepts either a dictionary of models or a path to a YAML configuration file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `models` | `dict` or `str` | Dictionary of SemanticTable objects or path to YAML config |
| `description` | `str` | Optional description of the semantic model |

**Available MCP Tools:**

| Tool | Description |
|------|-------------|
| `list_models()` | List all available semantic model names |
| `get_model()` | Get detailed model information (dimensions, measures, joins) |
| `get_time_range()` | Get available time range for time-series data |
| `query_model()` | Execute queries against semantic models |

**Example:**
```python
from boring_semantic_layer import MCPSemanticModel

# From dictionary
server = MCPSemanticModel(
    models={"flights": flights_st, "airports": airports_st},
    description="Flight data analysis"
)

# From YAML
server = MCPSemanticModel("config.yaml")
```

### YAML Configuration

#### YAML Structure

```yaml
model_name:
  table: table_reference
  description: "Optional description"

  dimensions:
    dimension_name: expression
    # or with description
    dimension_name:
      expr: expression
      description: "Dimension description"

  measures:
    measure_name: expression
    # or with description
    measure_name:
      expr: expression
      description: "Measure description"

  joins:
    join_name:
      model: model_reference
      on: join_condition
      how: join_type  # left, inner, right, outer, cross
```

#### Expression Syntax

| Expression | Description |
|------------|-------------|
| `_` | Reference to the table |
| `_.column` | Reference a column |
| `_.count()` | Count aggregation |
| `_.column.sum()` | Sum aggregation |
| `_.column.mean()` | Average aggregation |
| `_.column.min()` | Minimum value |
| `_.column.max()` | Maximum value |

**Example:**
```yaml
flights:
  table: flights_data
  description: "Flight operations data"

  dimensions:
    origin: _.origin
    dest: _.dest
    carrier:
      expr: _.carrier
      description: "Airline carrier code"

  measures:
    flight_count: _.count()
    avg_delay:
      expr: _.arr_delay.mean()
      description: "Average arrival delay in minutes"
```

## Next Steps

- Learn about [Semantic Tables](/building/semantic-tables)
- Explore [Query Methods](/querying/methods)
- See [Advanced Patterns](/advanced/percentage-total)


## BSL — Core Concepts


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/semantic-table.md`

# Building a Semantic Table

Define your data model with dimensions and measures using Ibis expressions.

## Overview

A Semantic Table is the core building block of BSL. It transforms a raw Ibis table into a reusable, self-documenting data model by defining:
- **Dimensions**: Attributes to group by (e.g., origin, carrier, year)
- **Measures**: Aggregations and calculations (e.g., flight count, total distance)

## to_semantic_table()

```setup_flights
import ibis
from boring_semantic_layer import to_semantic_table

# 1. Start with an Ibis table
con = ibis.duckdb.connect(":memory:")
flights_data = ibis.memtable({
    "origin": ["JFK", "LAX", "SFO"],
    "dest": ["LAX", "SFO", "JFK"],
    "carrier": ["AA", "UA", "DL"],
    "year": [2023, 2023, 2024],
    "distance": [2475, 337, 382],
    "dep_delay": [10, 5, 0]
})
flights_tbl = con.create_table("flights", flights_data)

# 2. Convert to a Semantic Table
flights_st = to_semantic_table(flights_tbl, name="flights")
```

## with_dimensions()

Dimensions define the attributes you can group by in your queries. They represent the categorical or descriptive aspects of your data that you want to analyze.

You can define dimensions using lambda expressions, unbound syntax (`_.`), or the `Dimension` class with descriptions:

```dimensions_demo
from ibis import _
from boring_semantic_layer import Dimension

flights_st = flights_st.with_dimensions(
    # Lambda expressions - simple and explicit
    origin=lambda t: t.origin,

    # Unbound syntax - cleaner and more concise
    destination=_.dest,
    year=_.year,

    # Dimension - self-documenting and AI-friendly
    carrier=Dimension(
        expr=lambda t: t.carrier,
        description="Airline carrier code"
    )
)

flights_st.dimensions
```
<regularoutput code-block="dimensions_demo"></regularoutput>

## with_measures()

Measures define the aggregations and calculations you can query. They represent the quantitative aspects of your data that you want to analyze (counts, sums, averages, etc.).

You can define measures using lambda expressions, reference other measures for composition, or use the `Measure` class with descriptions:

```measures_demo
from boring_semantic_layer import Measure

flights_st = flights_st.with_measures(
    # Lambda expressions - simple and concise
    total_flights=lambda t: t.count(),
    total_distance=lambda t: t.distance.sum(),
    max_delay=lambda t: t.dep_delay.max(),

    # Reference other measures for composition
    avg_distance_per_flight=lambda t: t.total_distance / t.total_flights,

    # Measure - self-documenting and AI-friendly
    avg_distance=Measure(
        expr=lambda t: t.distance.mean(),
        description="Average flight distance in miles"
    )
)

flights_st.measures
```

<regularoutput code-block="measures_demo"></regularoutput>

### all()

The `all()` function references the entire dataset within measure definitions, enabling percent-of-total and comparison calculations.

**Example:** Calculate market share as a percentage

```measure_all_demo
flights_with_pct = flights_st.with_measures(
        flight_count=lambda t: t.count(),
        market_share=lambda t: t.flight_count / t.all(t.flight_count) * 100  # Percent of total
    )

# Query by carrier
result = (
    flights_with_pct
    .group_by("carrier")
    .aggregate("flight_count", "market_share")
)
```

<bslquery code-block="measure_all_demo"></bslquery>

<note type="info">
`t.all()` is a method available on the table parameter `t` in measure definitions. It references the entire dataset regardless of grouping, making it perfect for calculating percentages, or comparing groups to the total.
</note>

For more examples, see the [Percent of Total pattern](/advanced/percentage-total).

## graph

The `graph` property provides a dependency graph showing how dimensions and measures relate to each other. This is useful for:
- **Understanding dependencies**: See what columns or fields each dimension/measure depends on
- **Impact analysis**: Find what breaks when changing a field
- **Documentation**: Generate visual representations of your data model
- **Validation**: Ensure your model doesn't have circular dependencies

```graph_demo
# Build a semantic table with dependencies
flights_with_deps = flights_st.with_dimensions(
    origin=lambda t: t.origin,
    destination=lambda t: t.dest,
).with_measures(
    flight_count=lambda t: t.count(),
    total_distance=lambda t: t.distance.sum(),
    avg_distance_per_flight=lambda t: t.total_distance / t.flight_count
)

# Access the dependency graph
graph = flights_with_deps.get_graph()
graph
```
<regularoutput code-block="graph_demo"></regularoutput>

### Understanding the Graph Structure

The graph is a dictionary where:
- **Keys**: Dimension or measure names
- **Values**: Metadata containing:
  - `deps`: Dependencies mapped to their types (`'column'`, `'dimension'`, or `'measure'`)
  - `type`: The field type (`'dimension'`, `'measure'`, or `'calc_measure'`)

```graph_structure
# Access the graph - it's a dict-like object
graph = flights_with_deps.get_graph()
graph
```
<regularoutput code-block="graph_structure"></regularoutput>

```python
# Find what a specific field depends on
flights_with_deps.get_graph()['avg_distance_per_flight']['deps']
# Output: {'total_distance': 'measure', 'flight_count': 'measure'}
```

### Graph Traversal

Use `graph_predecessors()` and `graph_successors()` to navigate dependencies:

```graph_traversal
from boring_semantic_layer import graph_predecessors, graph_successors

graph = flights_with_deps.get_graph()

# What does this field depend on? (predecessors)
graph_predecessors(graph, 'avg_distance_per_flight')
# {'total_distance', 'flight_count'}

# What depends on this field? (successors)
graph_successors(graph, 'total_distance')
# {'avg_distance_per_flight'}
```
<regularoutput code-block="graph_traversal"></regularoutput>

### Working with the Dependency Graph

The dependency graph is a dict-like object where each key is a field name and the value is a dict with `"type"` (dimension/measure/calc_measure/column) and `"deps"` (dependencies with their types):

```python
# Access the graph directly as a dict
graph = flights_with_deps.get_graph()

# Iterate over fields and their dependencies
for field, info in graph.items():
    print(f"{field} ({info['type']}): depends on {info['deps']}")
```

## join_one() / join_many() / join_cross()

Join semantic tables together to query across relationships. Joins allow you to combine data from multiple semantic tables and access dimensions and measures across all joined tables.

**What Makes Semantic Joins Different?**

Semantic joins explicitly capture the **relationship type** between tables, rather than just specifying SQL join mechanics:

**SQL Joins:**
```python
# Specifies HOW to join (LEFT/INNER), but not the relationship
flights.join(carriers, condition, how="left")
```

**Semantic Joins:**
```python
# Specifies the relationship: one carrier has many flights
flights.join_many(carriers, lambda f, c: f.carrier == c.code)
```

**What You Get:**
- **Explicit relationships**: `join_many()` documents that this is a one-to-many relationship
- **Table hierarchy information**: The method name describes how tables relate to each other
- **Richer metadata**: Makes the data model structure explicit for documentation and tooling

<note type="info">
After joining, dimensions and measures are prefixed with table names (e.g., `flights.origin`, `carriers.name`) to avoid naming conflicts.
</note>

<note type="warning">
**Joining the same table multiple times?** If you need to join to the same source table via different foreign keys (e.g., pickup and dropoff locations), you must use `.view()` to create distinct table references:

```python
# Create distinct references when joining same table twice
pickup_locs = to_semantic_table(locs_tbl.view(), "pickup_locs")
dropoff_locs = to_semantic_table(locs_tbl.view(), "dropoff_locs")
```

Without `.view()`, you'll encounter an `IbisInputError: Ambiguous field reference` error. 
</note>

Let's get some additional data:

```setup_carriers
import ibis
from boring_semantic_layer import to_semantic_table

con = ibis.duckdb.connect(":memory:")

# Create carriers data
carriers_data = ibis.memtable({
    "code": ["AA", "UA", "DL"],
    "name": ["American Airlines", "United Airlines", "Delta Air Lines"]
})
carriers_tbl = con.create_table("carriers", carriers_data)
```
<collapsedcodeblock code-block="setup_carriers" title="Create carriers Ibis table"></collapsedcodeblock>

And create a carriers semantic table:

```carriers_st
carriers = (
    to_semantic_table(carriers_tbl, name="carriers")
    .with_dimensions(
        code=lambda t: t.code,
        name=lambda t: t.name
    )
    .with_measures(
        carrier_count=lambda t: t.count()
    )
)
```

### join_many() - One-to-Many Relationships

Use `join_many()` when one row in the left table can match multiple rows in the right table (LEFT JOIN).

```join_demo
# Join carriers to flights - one carrier has many flights
flights_with_carriers = flights_st.join_many(
    carriers,
    lambda f, c: f.carrier == c.code
)

# Inspect available dimensions and measures
flights_with_carriers.dimensions
```
<regularoutput code-block="join_demo"></regularoutput>

After joining, all dimensions and measures from both tables are available. Each is prefixed with its table name to avoid conflicts:


### join_one() - One-to-One Relationships

Use `join_one()` when rows have a unique matching relationship (INNER JOIN).

```python
# Many flights → one carrier (each flight has exactly one carrier)
flights_with_carrier = flights_st.join_one(
    carriers,
    lambda f, c: f.carrier == c.code
)
```

<note type="warning">
**Important Limitation:** Currently, `left_on` and `right_on` must be **COLUMN names**, not dimension names.

If you have a dimension that maps to a different column name, you must use the underlying column name in the join.

**Example:**
```python
# If users table has column 'id' but dimension 'customer_id':
users = to_semantic_table(users_tbl).with_dimensions(
    customer_id=lambda t: t.id  # Dimension renamed
)

# ❌ This will fail with a helpful error:
orders.join_one(users, left_on="customer_id", right_on="customer_id")

# ✓ Use the actual column name:
orders.join_one(users, left_on="customer_id", right_on="id")
```

This is a known limitation tracked in [issue #43](https://github.com/boringdata/boring-semantic-layer/issues/43). If you attempt to use a dimension name that doesn't match a column name, you'll get a helpful error message guiding you to use the correct column name.
</note>

### join_cross() - Cross Join

Use `join_cross()` to create every possible combination of rows from both tables (CARTESIAN PRODUCT).

```python
# Every flight × every carrier combination
all_combinations = flights_st.join_cross(carriers)
```

### join() - Custom Join Conditions

Use `join()` for complex join conditions or specific SQL join types.

```python
# LEFT JOIN with custom condition
flights_with_carriers = flights_st.join(
    carriers,
    lambda f, c: f.carrier == c.code,
    how="left"
)

# INNER JOIN
flights_matched = flights_st.join(
    carriers,
    lambda f, c: f.carrier == c.code,
    how="inner"
)

# Complex conditions
date_range_join = flights_st.join(
    promotions,
    lambda f, p: (f.date >= p.start_date) & (f.date <= p.end_date),
    how="left"
)
```

**Supported join types:** `"inner"`, `"left"`, `"right"`, `"outer"`, `"cross"`

## Next Steps

- Learn about [Composing Models](/examples/compose)
- Explore [YAML Configuration](/examples/yaml-config)
- Start [Querying Semantic Tables](/examples/query-methods)


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/compose.md`

# Composing Models

Build complex data models by combining multiple semantic tables through joins. Model composition allows you to create rich, multi-dimensional views of your data.

## Composition via Joins

Model composition in BSL is achieved through **joins**. When you join semantic tables, the result is a new composed model that contains **all dimensions and measures** from both tables.

<note type="info">
Each join creates a new semantic model with the combined dimensions and measures from all joined tables. This allows you to build progressively richer models.
</note>

## Example: Two-Level Composition

Let's build a composed model step-by-step, showing available dimensions and measures at each level.

### Level 0: Base Models

First, let's set up our base tables:

```setup_ibis_tables
import ibis
from boring_semantic_layer import to_semantic_table

# Create sample data
con = ibis.duckdb.connect(":memory:")

# Flights table
flights_data = ibis.memtable({
    "flight_id": [1, 2, 3],
    "carrier_code": ["AA", "UA", "DL"],
    "aircraft_id": [101, 102, 103],
    "distance": [1000, 1500, 800],
    "passengers": [150, 180, 120]
})
flights_tbl = con.create_table("flights", flights_data)

# Carriers table
carriers_data = ibis.memtable({
    "code": ["AA", "UA", "DL"],
    "name": ["American Airlines", "United Airlines", "Delta Air Lines"],
    "country": ["USA", "USA", "USA"]
})
carriers_tbl = con.create_table("carriers", carriers_data)

# Aircraft table
aircraft_data = ibis.memtable({
    "id": [101, 102, 103],
    "model": ["Boeing 737", "Airbus A320", "Boeing 777"],
    "capacity": [180, 200, 350]
})
aircraft_tbl = con.create_table("aircraft", aircraft_data)
```

<collapsedcodeblock code-block="setup_ibis_tables" title="Define Ibis Tables"></collapsedcodeblock>

```setup_semantic_models
# Create semantic tables
flights_st = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        flight_id=lambda t: t.flight_id,
        carrier_code=lambda t: t.carrier_code,
        aircraft_id=lambda t: t.aircraft_id
    )
    .with_measures(
        flight_count=lambda t: t.count(),
        total_distance=lambda t: t.distance.sum(),
        total_passengers=lambda t: t.passengers.sum()
    )
)

carriers_st = (
    to_semantic_table(carriers_tbl, name="carriers")
    .with_dimensions(
        code=lambda t: t.code,
        name=lambda t: t.name,
        country=lambda t: t.country
    )
    .with_measures(
        carrier_count=lambda t: t.count()
    )
)

aircraft_st = (
    to_semantic_table(aircraft_tbl, name="aircraft")
    .with_dimensions(
        id=lambda t: t.id,
        model=lambda t: t.model
    )
    .with_measures(
        aircraft_count=lambda t: t.count(),
        total_capacity=lambda t: t.capacity.sum()
    )
)
```

<collapsedcodeblock code-block="setup_semantic_models" title="Define Semantic Models"></collapsedcodeblock>

```level0_dimensions
flights_st.dimensions, flights_st.measures
```

<regularoutput code-block="level0_dimensions"></regularoutput>

### Level 1: First Join (Flights + Carriers)

Join carriers to flights to add carrier information:

```level1_join
# Join carriers to flights
flights_with_carriers = flights_st.join_many(
    carriers_st,
    lambda f, c: f.carrier_code == c.code
)

# Inspect dimensions - now includes both flights and carriers
flights_with_carriers.dimensions, flights_with_carriers.measures
```
<regularoutput code-block="level1_join"></regularoutput>

### Level 2: Second Join (+ Aircraft)

Add aircraft information to create a fully composed model:

```level2_join
# Join aircraft to the composed model
full_model = flights_with_carriers.join_many(
    aircraft_st,
    lambda f, a: f.aircraft_id == a.id
)

# Inspect dimensions - now includes flights, carriers, AND aircraft
full_model.dimensions, full_model.measures
```
<regularoutput code-block="level2_join"></regularoutput>

## Query the Composed Model

Now you can query across all joined tables:

```composed_query
# Query using dimensions and measures from all three tables
result = (
    full_model
    .group_by( "aircraft.model")
    .aggregate("flight_count", "total_passengers", "total_capacity")
)
```

<bslquery code-block="composed_query"></bslquery>

## Key Takeaways

- **Composition via Joins**: Use `join_many()`, `join_one()`, or `join()` to compose models
- **Additive**: Each join adds dimensions and measures from the joined table
- **Table Prefixes**: Dimensions/measures are prefixed with table names (`flights.`, `carriers.`, `aircraft.`)
- **No Limit**: Compose as many models as needed for your analysis
- **Incremental**: Build from simple to complex, one join at a time

## Next Steps

- Learn about [YAML Configuration](/building/yaml) for declarative model composition
- Explore [Query Methods](/querying/methods) for querying composed models


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-methods.md`

# Query Methods

## Overview

BSL provides a simple and consistent query API for retrieving data from your semantic tables. Queries are built by chaining methods, then executed or inspected using output methods.

Start with a semantic table and chain methods together. Here's the typical query flow:

```setup_table
import ibis
from ibis import _
from boring_semantic_layer import to_semantic_table

# Create Ibis table
flights_tbl = ibis.memtable({
    "origin": ["NYC", "LAX", "NYC", "SFO", "LAX", "NYC", "SFO", "LAX", "NYC"],
    "carrier": ["AA", "UA", "AA", "UA", "AA", "UA", "AA", "UA", "AA"],
    "distance": [2789, 2789, 2902, 2902, 347, 2789, 347, 347, 2789],
    "duration": [330, 330, 360, 360, 65, 330, 65, 65, 330],
})

# Create semantic table
flights_st = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin=lambda t: t.origin,
        carrier=lambda t: t.carrier,
    )
    .with_measures(
        flight_count=lambda t: t.count(),
        total_distance=lambda t: t.distance.sum(),
        avg_duration=lambda t: t.duration.mean(),
    )
)
```
<collapsedcodeblock code-block="setup_table" title="Setup: Create Ibis Table and Semantic Table"></collapsedcodeblock>


```python
result = (
    flights_st                                   # Start with semantic table
    .filter(_.distance > 1000)                   # 1. Filter (optional)
    .group_by("origin")                          # 2. Group by dimensions
    .aggregate("flight_count", "total_distance") # 3. Aggregate measures
    .mutate(avg=lambda t: t.total_distance / t.flight_count)  # 4. Transform (optional)
    .order_by(ibis.desc("flight_count"))         # 5. Sort (optional)
    .limit(10)                                   # 6. Limit rows (optional)
)
```

Once you've built a query, you can inspect it or execute it:

```simple_demo

# Build a query
result = flights_st.group_by("origin").aggregate("flight_count")

# Option 1: Execute and get data as pandas DataFrame
df = result.execute()

# Option 2: View the generated SQL
print(result.sql())

# Option 3: Generate a visualization (when applicable)
chart = result.chart()

# Option 4: See the semantic query plan
print(result)

result
```
<bslquery code-block="simple_demo"></bslquery>

The output above includes a **Query Plan** tab showing how BSL translates this query into semantic operations. 

You print the query object directly to see the plan:
```python
print(result)
```

This displays operations like `SemanticTableOp`, `SemanticGroupByOp`, and `SemanticAggregateOp`, useful for debugging and understanding query execution.

Let's get now into the details of each query method.

## group_by()

The `group_by()` method groups data by one or more dimensions.

<note type="info">
`group_by()` only accepts string dimension names that were previously defined in `with_dimensions()`. It does not support lambda functions or unbound `_` syntax.
</note>

### Single Dimension

Group by a single dimension:

```query_single_dimension
# Group by one dimension
result = flights_st.group_by("origin").aggregate("flight_count")
```

<bslquery code-block="query_single_dimension"></bslquery>

### Multiple Dimensions

Group by multiple dimensions to create detailed breakdowns:

```query_multiple_dimensions
# Group by multiple dimensions
result = flights_st.group_by("origin", "carrier").aggregate("flight_count")
```

<bslquery code-block="query_multiple_dimensions"></bslquery>

### No Grouping

Calculate overall statistics across all rows using `group_by()` with no arguments:

```query_no_grouping
# Aggregate entire dataset without grouping
result = flights_st.group_by().aggregate("flight_count", "total_distance", "avg_duration")
```

<bslquery code-block="query_no_grouping"></bslquery>

## aggregate()

The `aggregate()` method calculates measures after grouping. You can reference pre-defined measures or compute new ones on-the-fly.

<note type="warning">
**CRITICAL**: `aggregate()` takes **measure names as strings**, not expressions or lambdas directly. Use measure names from `get_model()` output.
```python
# ✅ CORRECT - measure names as strings
model.group_by("category").aggregate("flight_count", "total_revenue")

# ❌ WRONG - no standalone lambdas in aggregate
model.aggregate(total=lambda t: t.sum())  # ERROR!
```
</note>

### Pre-defined Measures

Reference measures by their string names:

```query_predefined_measures
# Use measures defined in with_measures()
result = flights_st.group_by("origin").aggregate("flight_count", "avg_duration")
```

<bslquery code-block="query_predefined_measures"></bslquery>

### On-the-Fly Transformations

Add computed measures directly in `aggregate()` without modifying the semantic table:

```query_onthefly_measures
# Mix predefined and computed measures
result = (
    flights_st
    .group_by("origin")
    .aggregate(
        "flight_count",              # Pre-defined measure
        "avg_duration",               # Pre-defined measure
        total_miles=lambda t: t.distance.sum(),  # Computed on-the-fly
        max_distance=lambda t: t.flight_count + 2  # You can reference other measures as well
    )
)
```

<bslquery code-block="query_onthefly_measures"></bslquery>

<note type="info">
On-the-fly measures let you add context-specific calculations without modifying your semantic table definition. This keeps your base model clean while enabling flexible queries.
</note>

### Referencing Table Columns

You can reference **any column from the underlying table** in `aggregate()`, not just pre-defined measures. This is useful when you need one-off calculations without cluttering your semantic table definition.

```query_table_columns
# Reference table columns directly in aggregate()
result = (
    flights_st
    .group_by("origin")
    .aggregate(
        "flight_count",                           # Pre-defined measure
        total_distance=lambda t: t.distance.sum(),  # Table column 'distance'
        avg_duration=lambda t: t.duration.mean(),   # Table column 'duration'
        distance_in_km=lambda t: (t.distance * 1.60934).sum()  # Transform then aggregate
    )
)
```

<bslquery code-block="query_table_columns"></bslquery>

**Key points:**
- Table columns **must be aggregated** (e.g., `.sum()`, `.mean()`, `.max()`, `.count()`)
- You can transform columns before aggregating (e.g., `(t.distance * 1.60934).sum()`)
- This works for any column in the underlying table, even if not defined as a dimension or measure
- Use this for ad-hoc calculations without modifying your semantic table

<note type="warning">
Table columns cannot be used without an aggregation function. For example, `lambda t: t.distance` will fail. You must use `lambda t: t.distance.sum()` or another aggregation.
</note>

## filter() / order_by() / limit() 

Combine `filter()`, `order_by()`, and `limit()` to refine your query results.

```query_filter_order_limit
from ibis import _

# Filter data, sort, and limit results
result = (
    flights_st
    .filter(lambda t: t.origin.isin(["NYC", "LAX"]))  # Filter origins
    .filter(_.distance > 500)                          # Filter distance using _ syntax
    .group_by("origin")
    .aggregate("flight_count", "avg_duration")        # Aggregate both measures
    .order_by(ibis.desc("flight_count"))              # Sort by flight_count descending
    .limit(5)                                          # Top 5 results
)
```

<bslquery code-block="query_filter_order_limit"></bslquery>

**Key points:**
- **`filter()`**: Use lambda or `_` syntax to apply conditions before aggregation
- **`order_by()`**: Use `ibis.desc()` for descending order, or column name for ascending
- **`limit()`**: Restrict the number of rows returned

### Critical Filter Patterns

**Multiple conditions** - use `ibis.and_()` or `ibis.or_()`:

```python
# Multiple conditions with AND
model.filter(lambda t: ibis.and_(t.amount > 1000, t.year >= 2023))

# Multiple conditions with OR
model.filter(lambda t: ibis.or_(t.status == "active", t.status == "pending"))
```

**IN operator** - MUST use `.isin()` method:

```python
# ✅ CORRECT - use .isin() method
model.filter(lambda t: t.region.isin(["US", "EU", "APAC"]))

# ❌ WRONG - Python's 'in' does NOT work!
model.filter(lambda t: t.region in ["US", "EU"])  # ERROR: truth value of Ibis expression is not defined
```

**Lambda column names** - use column names directly, never prefix with model name:

```python
# ✅ CORRECT - use column name directly
model.filter(lambda t: t.carrier == "AA")

# ❌ WRONG - do NOT prefix with model name
model.filter(lambda t: t.model.carrier == "AA")  # ERROR!
```

**Joined columns** - use exact prefixed name from `get_model()`:

```python
# If get_model() shows "customers.country", use it exactly:
model.filter(lambda t: t.customers.country == "US")

# ❌ WRONG - don't call methods on ID columns
model.filter(lambda t: t.customer_id.country())  # ERROR: no such method!
```

## nest()

The `nest` parameter in `aggregate()` creates nested data structures (arrays of structs) in your query results. This is useful for API responses, hierarchical visualizations, and preserving relationships in aggregated data.

Use `nest` to collect rows as structured arrays within each group:

```query_basic_nest
from ibis import _

# Nest flight details within each origin
result = (
    flights_st
    .group_by("origin")
    .aggregate(
        "flight_count",
        "total_distance",
        # Create nested array of flight details
        nest={"flights": lambda t: t.group_by(["carrier", "distance"])}
    )
)
```

<bslquery code-block="query_basic_nest"></bslquery>

**How it works:**
- The `nest` parameter accepts a dictionary: `{"column_name": lambda t: ...}`
- The lambda specifies which columns to collect using `.group_by()` or `.select()`
- Results in an array of structs column named `flights`

You can also use `.select()` to specify which columns to nest:

```query_nest_select
# Nest specific columns
result = (
    flights_st
    .group_by("carrier")
    .aggregate(
        "flight_count",
        nest={"routes": lambda t: t.select("origin", "distance", "duration")}
    )
)
```

<bslquery code-block="query_nest_select"></bslquery>

After nesting, you can re-group which automatically unnests, then access the nested fields.

**Step 1: Create nested data**

First, create the nested structure. Notice the `flights` column contains arrays of structs:

```query_nest_step1
from ibis import _

# Create nested data structure
result = (
    flights_st
    .group_by("origin")
    .aggregate(
        "flight_count",
        nest={"flights": lambda t: t.group_by(["carrier", "distance"])}
    )
)
```

<bslquery code-block="query_nest_step1"></bslquery>

**Step 2: Re-group to unnest and access fields**

Now re-group on the same dimension, which automatically unnests the array, allowing you to access the nested fields:

```query_nest_step2
from ibis import _

# Re-grouping automatically unnests the 'flights' array
result = (
    result
    .group_by("origin")
    .aggregate(
        total_flights=lambda t: t.flight_count.sum(),
        # Access unnested fields from the flights array
        unique_carriers=lambda t: t.flights.carrier.nunique(),
        avg_distance=lambda t: t.flights.distance.mean()
    )
)
```

<bslquery code-block="query_nest_step2"></bslquery>

**Use cases for nesting:**
- **API responses**: Create JSON-compatible hierarchical structures
- **Hierarchical data**: Preserve parent-child relationships in results
- **Data export**: Generate nested documents for external systems
- **Drill-down analysis**: Keep detailed records available in aggregated views

<note type="info">
For more complex nesting patterns and multi-level hierarchies, see [Nested Subtotals](/advanced/nested-subtotals).
</note>

## mutate()

The `mutate()` method transforms aggregated results by adding new computed columns. This is different from on-the-fly measures in `aggregate()` — `mutate()` works on already-aggregated data.

<note type="warning">
**Key difference:** `.aggregate()` computes from raw data, while `.mutate()` transforms already-aggregated results.
</note>

```query_mutate
from ibis import _

# Add post-aggregation calculations
result = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count", "total_distance")
    .mutate(
        avg_distance_per_flight=lambda t: t.total_distance / t.flight_count,
        flight_category=lambda t: ibis.cases(
            (t.flight_count >= 3, "high"),
            (t.flight_count >= 2, "medium"),
            else_="low"
        )
    )
)
```

<bslquery code-block="query_mutate"></bslquery>

**Use cases for `mutate()`:**
- Calculate ratios from aggregated measures (e.g., `total / count`)
- Create categories based on aggregated values
- Add labels or formatting to results
- Transform aggregated columns using the full power of Ibis

For more transformations, see [Ibis Table API reference](https://ibis-project.org/reference/expression-tables.html#ibis.expr.types.relations.Table.mutate).

## Window Functions with .over()

Window functions perform calculations across ordered rows, enabling operations like running totals, moving averages, and ranking. Unlike regular aggregations that reduce many rows to one, window functions preserve row count while adding computed values.

<note type="warning">
**Important:** Window functions can only be applied **after aggregation**, typically within a `.mutate()` call. They cannot be defined directly in measures.
</note>

**Common window functions:**
- **`lag()` / `lead()`**: Access previous/next row values for period-over-period comparisons
- **`cumsum()`**: Calculate running totals
- **`.over(window)`**: Apply functions over sliding windows (e.g., moving averages)
- **`rank()` / `row_number()`**: Assign ranks or sequential numbers to rows

Here's a simple example:

```query_window_example
from ibis import _

# First aggregate to daily level
daily_flights = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count", "total_distance")
    .order_by("origin")
)

# Then apply window function for cumulative distance
window_spec = ibis.window(order_by="origin")

result = daily_flights.mutate(
    cumulative_distance=_.total_distance.cumsum(),
    flight_rank=lambda t: ibis.rank().over(ibis.window(order_by=_.flight_count.desc()))
).limit(10)
```

<bslquery code-block="query_window_example"></bslquery>

**Key points:**
- Window functions are applied **after** `.aggregate()` using `.mutate()`
- Use `.order_by()` to establish row order for window operations
- Combine with `ibis.window()` for advanced sliding window calculations

For comprehensive examples including lag/lead, moving averages, and ranking, see [Window Functions](/advanced/windowing).

## as_table()

After filtering or aggregating data, you may want to perform additional semantic operations. However, intermediate results don't always preserve the semantic table's dimensions and measures.

The Problem: Lost Semantic Information

When you aggregate data, the result loses semantic metadata. The aggregated result is a `SemanticAggregate` expression, which doesn't have `.dimensions` or `.measures` attributes:

```query_as_table_problem
from ibis import _

# Aggregate the data - this returns a SemanticAggregate
agg_result = flights_st.group_by("origin").aggregate("flight_count", "total_distance")

# Show the type/class of the result
result_type = type(agg_result).__name__

# Try to access .dimensions - this will raise an AttributeError
try:
    dimensions = agg_result.dimensions
    result = f"Type: {result_type}\nDimensions: {dimensions}"
except AttributeError as e:
    result = f"Type: {result_type}\nError: {str(e)}"

result
```

<regularoutput code-block="query_as_table_problem"></regularoutput>


After aggregation, you can no longer access the original semantic table's dimensions and measures metadata.

The Solution: Use as_table()

The `as_table()` method converts results back into a `SemanticModel`. However, note that for aggregations, the metadata is intentionally cleared (since columns are now materialized):

```query_as_table_after_aggregate
from ibis import _

# Aggregate the data
agg_result = flights_st.group_by("origin").aggregate("flight_count", "total_distance")

# Convert to SemanticModel using as_table()
agg_table = agg_result.as_table()

# Now .dimensions and .measures attributes exist, but they're empty (metadata was cleared)
result = f"Type: {type(agg_table).__name__}\nDimensions: {agg_table.dimensions}\nMeasures: {agg_table.measures}"
```

<regularoutput code-block="query_as_table_after_aggregate"></regularoutput>

When are metadata preserved ?

For operations like `filter()`, `order_by()`, and `limit()`, `as_table()` **preserves** the original semantic metadata:

```query_as_table_filter_preserved
from ibis import _

# Filter the data
filtered = flights_st.filter(_.distance > 2000)

# Convert back to SemanticModel - metadata is preserved!
filtered_table = filtered.as_table()

# Dimensions and measures are still available (preserved from original semantic table)
result = f"Type: {type(filtered_table).__name__}\nDimensions: {filtered_table.dimensions}\nMeasures: {filtered_table.measures}"
```

<regularoutput code-block="query_as_table_filter_preserved"></regularoutput>

Notice how the dimensions and measures are preserved, unlike the aggregation case above where they were empty.

**Key points:**
- **Operations that preserve metadata**: `filter()`, `order_by()`, `limit()`, `unnest()` — calling `as_table()` restores full semantic capabilities with original dimensions/measures
- **Operations that clear metadata**: `aggregate()`, `mutate()` — calling `as_table()` returns a `SemanticModel` with empty dimensions/measures (columns are materialized)
- Use `as_table()` when you need to continue semantic operations on intermediate results

## Next Steps

- Learn about [Building Semantic Tables](/building/semantic-tables) to define dimensions and measures
- Explore [Composing Models](/building/compose) for multi-table queries
- Try [Advanced Patterns](/advanced/percentage-total) for complex analytics


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/indexing.md`

# Dimensional Indexing

Create a searchable catalog of all unique values across your dimensions for data exploration, autocomplete features, and understanding data distributions. Inspired by [Malloy's index pattern](https://docs.malloydata.dev/documentation/patterns/dim_index).

## Overview

Dimensional indexing allows you to:

- **Catalog all values**: Extract and count all unique values across dimensions
- **Search dimensions**: Build autocomplete and search features
- **Profile data**: Understand cardinality and distributions
- **Weight by measures**: Find values ranked by custom metrics (e.g., highest revenue cities)
- **Index across joins**: Search values from related tables

The `index()` method returns a standardized table with columns:
- `fieldName`: The dimension name
- `fieldValue`: The unique value
- `fieldType`: The data type (string, number, etc.)
- `weight`: Count or custom measure value for ranking

## Setup

Let's create an airports semantic table for our examples:

```setup_airports
import ibis
from boring_semantic_layer import to_semantic_table

# Create synthetic airports data
airports_data = ibis.memtable({
    "code": ["JFK", "LAX", "ORD", "ATL", "DFW", "DEN", "SFO", "LAS", "SEA", "PHX",
             "IAH", "MCO", "EWR", "BOS", "MIA", "SAN", "LGA", "PHL", "DTW", "MSP"],
    "city": ["NEW YORK", "LOS ANGELES", "CHICAGO", "ATLANTA", "DALLAS", "DENVER",
             "SAN FRANCISCO", "LAS VEGAS", "SEATTLE", "PHOENIX", "HOUSTON", "ORLANDO",
             "NEWARK", "BOSTON", "MIAMI", "SAN DIEGO", "NEW YORK", "PHILADELPHIA",
             "DETROIT", "MINNEAPOLIS"],
    "state": ["NY", "CA", "IL", "GA", "TX", "CO", "CA", "NV", "WA", "AZ",
              "TX", "FL", "NJ", "MA", "FL", "CA", "NY", "PA", "MI", "MN"],
    "fac_type": ["AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT",
                 "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT",
                 "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT", "AIRPORT",
                 "AIRPORT", "AIRPORT"],
    "elevation": [13, 128, 672, 1026, 607, 5433, 13, 2181, 433, 1135,
                  97, 96, 18, 19, 8, 17, 21, 36, 645, 841]
})

# Define semantic table
airports = (
    to_semantic_table(airports_data, name="airports")
    .with_dimensions(
        code=lambda t: t.code,
        city=lambda t: t.city,
        state=lambda t: t.state,
        fac_type=lambda t: t.fac_type,
        elevation=lambda t: t.elevation,
    )
    .with_measures(
        airport_count=lambda t: t.count(),
        avg_elevation=lambda t: t.elevation.mean(),
    )
)
```

<collapsedcodeblock code-block="setup_airports" title="Setup: Create Airports Table"></collapsedcodeblock>

## Basic Index: All Dimensions

Index all dimensions to see every unique value with its frequency:

```query_index_all
# Index all dimensions (None means all)
result = airports.index(None).limit(10)
```

<bslquery code-block="query_index_all"></bslquery>

The `weight` column shows the count for each value. Use this to understand which values are most common across your dataset.

## Index Specific Fields

Focus on specific dimensions by selecting them:

```query_index_specific
# Index only state and city
result = (
    airports.index(lambda t: [t.state, t.city])
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_index_specific"></bslquery>

This is useful when you only care about certain dimensions, reducing noise and improving performance.

## Search Pattern: Autocomplete

Build autocomplete features by filtering the index with pattern matching:

```query_autocomplete
# Get city suggestions starting with "SAN"
result = (
    airports.index(lambda t: t.city)
    .filter(lambda t: t.fieldValue.like("SAN%"))
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_autocomplete"></bslquery>

<note type="info">
Use pattern matching with `like()` to implement autocomplete, search suggestions, or fuzzy matching features in your application.
</note>

## Filter by Field Type

Analyze only string or numeric fields:

```query_by_type
# Get only string field values
result = (
    airports.index(None)
    .filter(lambda t: t.fieldType == "string")
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_by_type"></bslquery>

This helps when you want to focus on categorical vs. numeric dimensions separately.

## Custom Weights: Rank by Measure

Instead of counting occurrences, weight values by a custom measure:

```query_custom_weight
# Find states with most airports
result = (
    airports.index(lambda t: t.state, by="airport_count")
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_custom_weight"></bslquery>

<note type="info">
The `by` parameter lets you rank dimension values by any measure. This is powerful for finding "top cities by revenue", "states by average temperature", etc.
</note>

## Sampling for Large Datasets

For very large datasets, use sampling to get quick insights:

```query_sampled
# Sample 100 rows before indexing
result = (
    airports.index(None, sample=100)
    .filter(lambda t: t.fieldType == "string")
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_sampled"></bslquery>

Sampling trades perfect accuracy for speed, which is often acceptable for exploratory analysis.

## Index Across Joins

Index dimensions from joined tables:

```query_index_joins
# Create synthetic flights data
flights_data = ibis.memtable({
    "flight_id": list(range(1, 31)),
    "carrier": ["AA", "UA", "DL", "WN", "B6", "AA", "UA", "DL", "WN", "B6"] * 3,
    "origin": ["JFK", "LAX", "ORD", "ATL", "DFW", "SFO", "SEA", "DEN", "PHX", "BOS"] * 3,
})

flights = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        carrier=lambda t: t.carrier,
        origin=lambda t: t.origin,
    )
    .with_measures(
        flight_count=lambda t: t.count(),
    )
)

# Join flights with airports
flights_with_origin = flights.join_one(airports, lambda f, a: f.origin == a.code)

# Index across the join
result = (
    flights_with_origin.index(["flights.carrier", "airports.state"])
    .order_by(lambda t: t.weight.desc())
    .limit(10)
)
```

<bslquery code-block="query_index_joins"></bslquery>

<note type="warning">
When referencing dimensions from joined tables in the index, use dot notation with table name prefix: `"airports.state"` instead of just `"state"`.
</note>

## Use Cases

**Data Discovery**: Quickly explore what values exist in your dimensions without writing complex group-by queries. Perfect for understanding unfamiliar datasets.

**Autocomplete & Search**: Build type-ahead search features by indexing dimension values and filtering with pattern matching. The weight helps rank suggestions by relevance.

**Data Profiling**: Understand data quality by examining cardinality, common values, and distributions across dimensions. Identify outliers or data entry errors.

**Metric-Weighted Ranking**: Find dimension values that matter most for your metrics - e.g., "cities with highest revenue", "products with most returns", "states with longest delivery times".

**Cross-Table Search**: Index dimensions across joined tables to search related data simultaneously, enabling unified search experiences.

## Key Takeaways

- Use `index(None)` to catalog all dimension values
- Use `index(lambda t: [t.field1, t.field2])` for specific fields or `index(lambda t: t.field)` for a single field
- Filter by `fieldType` to focus on strings or numbers
- Use `by="measure_name"` to weight by custom measures instead of counts
- Add `sample=N` to analyze large datasets quickly
- The index works across joins - use `"table.field"` syntax for joined dimensions
- Perfect for building autocomplete, search, and data profiling features

## Next Steps

- Learn about [Nested Subtotals](/advanced/nested-subtotals) for hierarchical data structures
- Explore [Query Methods](/querying/methods) for more query patterns


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/yaml-config.md`

# YAML Configuration

Define your semantic models using YAML for better organization and maintainability.

## Why YAML?

YAML configuration provides several advantages:
- **Better organization**: Keep your model definitions separate from your code
- **Version control**: Track changes to your data model structure
- **Collaboration**: Non-developers can review and understand the model
- **Reusability**: Share model definitions across different projects

## Expression Syntax

Here's a complete example with dimensions, measures, and joins:

<yamlcontent path="yaml_example.yaml"></yamlcontent>

<note type="warning">
In YAML configuration, **only unbound syntax (`_`) is accepted** for expressions. Lambda expressions are not supported in YAML files.
</note>

## Loading YAML Models

### Option 1: Using Profiles (Recommended)

```yaml
# File-level profile
profile: my_db

flights:
  table: flights_tbl
  dimensions:
    origin: _.origin
```

```python
from boring_semantic_layer import from_yaml

models = from_yaml("flights_model.yml")
```

See [Profile documentation](/building/profile) for setup details.

### Option 2: Passing Tables Manually

Create your ibis tables:

```yaml_setup
import ibis

flights_tbl = ibis.memtable({
    "origin": ["JFK", "LAX", "SFO"],
    "dest": ["LAX", "SFO", "JFK"],
    "carrier": ["AA", "UA", "DL"],
    "year": [2023, 2023, 2024],
    "distance": [2475, 337, 382]
})

carriers_tbl = ibis.memtable({
    "code": ["AA", "UA", "DL"],
    "name": ["American Airlines", "United Airlines", "Delta Air Lines"]
})
```

And pass them to the loaded YAML file defining your Semantic Tables:

```load_yaml_example
from boring_semantic_layer import from_yaml

# Load models from YAML file with explicit tables
models = from_yaml(
    "yaml_example.yaml",
    tables={
        "flights_tbl": flights_tbl,
        "carriers_tbl": carriers_tbl
    }
)

flights_sm = models["flights"]
carriers_sm = models["carriers"]

# Inspect the loaded models
flights_sm.dimensions, flights_sm.measures
```

<regularoutput code-block="load_yaml_example"></regularoutput> 

### Option 3: Loading from a Dictionary (`from_config`)

If you're loading configuration through your own mechanism (e.g., Kedro catalog, external config management), you can use `from_config()` to construct semantic models directly from a Python dictionary:

```python
from boring_semantic_layer import from_config

config = {
    "flights": {
        "table": "flights_tbl",
        "dimensions": {
            "origin": "_.origin",
            "destination": "_.dest",
        },
        "measures": {
            "flight_count": "_.count()",
            "avg_distance": "_.distance.mean()",
        },
    }
}

models = from_config(config, tables={"flights_tbl": flights_tbl})
flights_sm = models["flights"]
```

This is useful for integrations where you don't want to write config to a file just to load it. The `from_config()` function accepts the same `profile` and `profile_path` parameters as `from_yaml()`:

```python
# With a profile
models = from_config(config, profile="my_db")

# With profile in config
config = {
    "profile": "my_db",
    "flights": {
        "table": "flights_tbl",
        ...
    }
}
models = from_config(config)
```

## Querying YAML Models

YAML-defined models work exactly like Python-defined models. You can use the same `group_by()` and `aggregate()` methods to query your data.

```query_yaml_model
# Query the YAML-defined model
result = (
    flights_sm
    .group_by("origin")
    .aggregate("flight_count", "avg_distance")
)
```

<bslquery code-block="query_yaml_model"></bslquery>

## Filters

You can apply a filter to all queries on a model by adding a `filter` field:

```yaml
flights:
  table: flights_tbl
  filter: _.year > 2020  # Applied to all queries
  dimensions:
    origin: _.origin
  measures:
    flight_count: _.count()
```

The filter expression uses the same `_` syntax as dimensions and measures. It's applied automatically when you query the model.

## Next Steps

- See [Building Semantic Tables](/building/semantic-tables) for Python-based definitions
- Learn [Query Methods](/querying/methods) for querying YAML-defined models
- Explore [Composing Models](/building/compose) for joining YAML models


## BSL — Advanced Analytics


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/bucketing.md`

# Bucketing with 'Other'

Limit displayed group-by values while consolidating remaining items into an 'Other' category. This pattern maintains focus on top-performing segments while capturing complete data and handling long-tail distributions.

## Overview

The bucketing with 'Other' pattern allows you to:

- Focus on top N items while grouping the rest as 'Other'
- Use window functions to rank and identify top performers
- Create custom ranges for continuous values (e.g., age groups, price tiers)
- Consolidate low-frequency items into an "Other" category
- Maintain analytical clarity by reducing dimensional cardinality

## Setup

Let's create customer data with ages and purchase amounts:

```setup_raw_data
import ibis
from ibis import _
from boring_semantic_layer import to_semantic_table

# Create customer transaction data
customer_data = ibis.memtable({
    "customer_id": list(range(1, 21)),
    "age": [22, 28, 35, 42, 19, 55, 31, 67, 24, 38, 45, 29, 51, 33, 61, 26, 48, 36, 58, 41],
    "purchase_amount": [45, 120, 250, 180, 35, 520, 95, 850, 65, 310, 190, 78, 420, 145, 680, 88, 275, 165, 590, 225],
    "product_category": ["Electronics", "Clothing", "Electronics", "Home", "Clothing", "Electronics",
                        "Clothing", "Electronics", "Clothing", "Home", "Electronics", "Clothing",
                        "Home", "Clothing", "Electronics", "Clothing", "Home", "Electronics", "Electronics", "Home"]
})
```

<collapsedcodeblock code-block="setup_raw_data" title="Setup: Create Raw Customer Data"></collapsedcodeblock>

Now create a semantic table with dimensions and measures:

```semantic_table_def
from boring_semantic_layer import to_semantic_table

customer_st = (
    to_semantic_table(customer_data, name="customers")
    .with_dimensions(
        customer_id=lambda t: t.customer_id,
        age=lambda t: t.age,
        product_category=lambda t: t.product_category
    )
    .with_measures(
        customer_count=lambda t: t.count(),
        total_revenue=lambda t: t.purchase_amount.sum(),
        avg_purchase=lambda t: t.purchase_amount.mean().round(2)
    )
)
```

<collapsedcodeblock code-block="semantic_table_def" title="Setup: Define Semantic Table"></collapsedcodeblock>

## Top Categories with 'Other'

The most common bucketing pattern: show top N items by a metric, consolidate the rest as 'Other'. This uses a two-stage approach with window functions to rank items.

```query_top_categories
from ibis import _

# Two-stage pipeline: rank then consolidate
result = (
    customer_st
    .group_by("product_category")
    .aggregate("total_revenue", "customer_count")
    .mutate(
        # Rank categories by revenue
        rank=lambda t: ibis.row_number().over(
            ibis.window(order_by=t.total_revenue.desc())
        )
    )
    .mutate(
        # Replace non-top categories with "Other"
        category_display=lambda t: ibis.cases(
            (t.rank <= 2, t.product_category),
            else_="Other"
        ),
        # Keep original revenue for sorting (only for top categories)
        sort_value=lambda t: ibis.cases(
            (t.rank <= 2, t.total_revenue),
            else_=0
        )
    )
    .group_by("category_display")
    .aggregate(
        revenue=lambda t: t.total_revenue.sum(),
        customers=lambda t: t.customer_count.sum(),
        sort_helper=lambda t: t.sort_value.max()
    )
    .mutate(
        avg_per_customer=lambda t: (t.revenue / t.customers).round(2)
    )
    .order_by(_.sort_helper.desc())
)
```

<bslquery code-block="query_top_categories"></bslquery>

<note type="info">
The window function `row_number()` ranks categories by revenue. Non-top items are marked with `is_other`, then consolidated into a single 'Other' category. The `sort_helper` field ensures top categories appear first, sorted by their original revenue, with 'Other' at the end.
</note>

## Age Range Bucketing

Create age buckets using case expressions:

```query_age_buckets
from ibis import _
result = (
    customer_st
    .group_by("customer_id", "age", "product_category")
    .aggregate("total_revenue")
    .mutate(
        age_group=lambda t: ibis.cases(
            (t.age < 25, "18-24"),
            (t.age < 35, "25-34"),
            (t.age < 45, "35-44"),
            (t.age < 55, "45-54"),
            else_="55+"
        )
    )
    .group_by("age_group")
    .aggregate(
        customers=lambda t: t.count(),
        revenue=lambda t: t.total_revenue.sum()
    )
    .order_by(_.age_group)
)
```

<bslquery code-block="query_age_buckets" />

## Purchase Amount Tiers

Categorize purchases into value tiers:

```query_purchase_tiers
from ibis import _
result = (
    customer_st
    .group_by("customer_id")
    .aggregate("total_revenue")
    .mutate(
        tier=lambda t: ibis.cases(
            (t.total_revenue < 100, "Small ($0-99)"),
            (t.total_revenue < 250, "Medium ($100-249)"),
            (t.total_revenue < 500, "Large ($250-499)"),
            else_="Premium ($500+)"
        )
    )
    .group_by("tier")
    .aggregate(
        customer_count=lambda t: t.count(),
        total_value=lambda t: t.total_revenue.sum(),
        avg_value=lambda t: t.total_revenue.mean().round(2)
    )
    .order_by(_.total_value.desc())
)
```

<bslquery code-block="query_purchase_tiers" />

## Threshold-Based 'Other' Category

Instead of ranking, you can consolidate categories based on a threshold (e.g., minimum customer count):

```query_with_other
from ibis import _

result = (
    customer_st
    .group_by("product_category")
    .aggregate("total_revenue", "customer_count")
    .mutate(
        # Mark categories with less than 5 customers as "Other"
        category_grouped=lambda t: ibis.cases(
            (t.customer_count >= 5, t.product_category),
            else_="Other"
        )
    )
    .group_by("category_grouped")
    .aggregate(
        customers=lambda t: t.customer_count.sum(),
        revenue=lambda t: t.total_revenue.sum()
    )
    .mutate(
        avg_per_customer=lambda t: (t.revenue / t.customers).round(2)
    )
    .order_by(_.revenue.desc())
)
```

<bslquery code-block="query_with_other"></bslquery>

<note type="info">
This approach uses a fixed threshold rather than ranking. Categories with fewer than 5 customers are consolidated into 'Other'. This is simpler but less dynamic than the window function approach.
</note>

## Combined Bucketing

Combine age groups and purchase tiers for multi-dimensional segmentation:

```query_combined_buckets
from ibis import _
result = (
    customer_st
    .group_by("customer_id", "age")
    .aggregate("total_revenue")
    .mutate(
        age_group=lambda t: ibis.cases(
            (t.age < 30, "Young (18-29)"),
            (t.age < 50, "Middle (30-49)"),
            else_="Senior (50+)"
        ),
        value_tier=lambda t: ibis.cases(
            (t.total_revenue < 150, "Low Value"),
            (t.total_revenue < 350, "Mid Value"),
            else_="High Value"
        )
    )
    .group_by("age_group", "value_tier")
    .aggregate(
        customers=lambda t: t.count(),
        revenue=lambda t: t.total_revenue.sum()
    )
    .order_by(_.age_group, _.revenue.desc())
)
```

<bslquery code-block="query_combined_buckets" />

## Use Cases

**Focus on Top Performers**: Show top 10 products by revenue, consolidate the rest as 'Other' to highlight key items while maintaining complete totals.

**Long-Tail Distribution Management**: In e-commerce, display top categories while grouping niche categories as 'Other' to simplify reporting and dashboards.

**Threshold-Based Filtering**: Consolidate low-volume customer segments (< 100 customers) into 'Other' to focus on statistically significant groups.

**Age and Value Segmentation**: Create meaningful customer segments by combining age ranges (Young, Middle, Senior) with purchase tiers (Low, Mid, High).

## Key Takeaways

- Use window functions like `row_number()` to rank items for dynamic top-N selection
- Two-stage pattern: rank first, then consolidate and re-aggregate
- `ibis.cases((condition, value), ..., else_=default)` provides flexible bucketing logic
- Threshold-based 'Other' works well when you have a clear cutoff value
- Sort helper fields ensure 'Other' appears at the end of results
- 'Other' category maintains complete data while reducing cardinality

## Next Steps

- Learn about [Sessionized Data](/advanced/sessionized) for time-based grouping
- Explore [Indexing](/advanced/indexing) for baseline comparisons


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/windowing.md`

# Window Functions

Perform calculations across ordered rows using window functions like running totals, moving averages, rank, lag/lead, and more. Window functions operate on query results after aggregation, enabling powerful comparative and analytical operations.

## Overview

Window functions allow you to:

- **Compare rows**: Calculate differences between current and previous rows (lag/lead)
- **Running calculations**: Compute cumulative sums and running averages
- **Ranking**: Assign ranks, row numbers, and percentiles
- **Moving windows**: Calculate metrics over sliding time windows

<note type="info">
Window functions in BSL are applied using Ibis window operations on aggregated results. They execute logically after the aggregation stage.
</note>

## Setup

Create a synthetic sales dataset with daily revenue data:

```setup_data
import ibis
from ibis import _
from datetime import datetime, timedelta
import random

# Create daily sales data spanning 90 days
start_date = datetime(2024, 1, 1)
dates = [start_date + timedelta(days=i) for i in range(90)]

# Generate synthetic revenue with upward trend and weekly patterns
random.seed(42)

revenue_values = []
for i, date in enumerate(dates):
    # Base trend: increasing over time
    base = 1000 + (i * 10)

    # Weekly pattern: weekends have higher sales
    weekday_multiplier = 1.3 if date.weekday() >= 5 else 1.0

    # Random variation
    noise = random.uniform(-100, 100)

    revenue = base * weekday_multiplier + noise
    revenue_values.append(round(revenue, 2))

# Create table
sales_data = ibis.memtable({
    "sale_date": dates,
    "revenue": revenue_values,
    "product_category": ["Electronics" if i % 3 == 0 else "Clothing" if i % 3 == 1 else "Home" for i in range(90)],
})
```

<collapsedcodeblock code-block="setup_data" title="Setup: Create Daily Sales Data"></collapsedcodeblock>

```setup_st
from boring_semantic_layer import to_semantic_table

# Create semantic table with measures
sales_st = to_semantic_table(
    sales_data,
    name="daily_sales"
).with_measures(
    total_revenue=lambda t: t.revenue.sum(),
    avg_revenue=lambda t: t.revenue.mean(),
    sale_count=lambda t: t.count(),
)
```

<collapsedcodeblock code-block="setup_st" title="Setup: Define Semantic Table"></collapsedcodeblock>

## Lag and Lead: Comparing to Previous/Next Rows

Calculate period-over-period changes by comparing current values to previous rows:

```query_lag_lead
from ibis import _

# Aggregate daily revenue
daily_revenue = (
    sales_st
    .group_by("sale_date")
    .aggregate("total_revenue")
    .order_by("sale_date")
)

# Add window functions for lag/lead
result = daily_revenue.mutate(
    prev_day_revenue=_.total_revenue.lag(),
    next_day_revenue=_.total_revenue.lead(),
    day_over_day_change=_.total_revenue - _.total_revenue.lag(),
    pct_change=((_.total_revenue - _.total_revenue.lag()) / _.total_revenue.lag() * 100).round(2)
).limit(10)
```

<bslquery code-block="query_lag_lead"></bslquery>

<note type="info">
`lag()` accesses the previous row's value, while `lead()` accesses the next row's value. The first row's lag and last row's lead will be null.
</note>

## Running Totals: Cumulative Calculations

Compute running sums to track cumulative metrics over time:

```query_running_total
from ibis import _

# Daily revenue with cumulative total
daily_revenue = (
    sales_st
    .group_by("sale_date")
    .aggregate("total_revenue")
    .order_by("sale_date")
)

# Calculate cumulative sum and running average
window_unbounded = ibis.window(rows=(None, 0), order_by="sale_date")

result = daily_revenue.mutate(
    cumulative_revenue=_.total_revenue.cumsum(),
    days_count=lambda t: t.count().over(window_unbounded),
    avg_daily_so_far=lambda t: (t.cumulative_revenue / t.days_count).round(2)
).limit(10)
```

<bslquery code-block="query_running_total"></bslquery>

## Moving Averages: Sliding Window Calculations

Calculate metrics over a rolling window of rows:

```query_moving_average
from ibis import _

# Daily revenue
daily_revenue = (
    sales_st
    .group_by("sale_date")
    .aggregate("total_revenue")
    .order_by("sale_date")
)

# 7-day moving average
window_7d = ibis.window(rows=(-6, 0), order_by="sale_date")

result = daily_revenue.mutate(
    ma_7day=_.total_revenue.mean().over(window_7d).round(2),
    ma_7day_sum=_.total_revenue.sum().over(window_7d).round(2),
).limit(10)
```

<bslquery code-block="query_moving_average"></bslquery>

<note type="info">
The window specification `rows=(-6, 0)` means "6 rows before the current row through the current row" (7 total rows). The moving average smooths out daily volatility.
</note>

## Ranking: Assign Positions

Rank rows based on values:

```query_ranking
from ibis import _

# Aggregate by product category
category_revenue = (
    sales_st
    .group_by("product_category")
    .aggregate("total_revenue", "sale_count")
    .order_by(_.total_revenue.desc())
)

# Add rank columns
result = category_revenue.mutate(
    rank=ibis.rank().over(ibis.window(order_by=_.total_revenue.desc())),
    dense_rank=ibis.dense_rank().over(ibis.window(order_by=_.total_revenue.desc())),
    row_number=ibis.row_number().over(ibis.window(order_by=_.total_revenue.desc())),
)
```

<bslquery code-block="query_ranking"></bslquery>

<note type="info">
`row_number()` assigns unique sequential numbers, `rank()` assigns the same rank to ties (skipping next ranks), and `dense_rank()` assigns the same rank to ties without gaps.
</note>

## Week-over-Week Comparison

Compare metrics across weekly periods:

```query_week_over_week
from ibis import _

# Aggregate by week
weekly_revenue = (
    sales_st
    .mutate(week_start=_.sale_date.truncate("W"))
    .group_by("week_start")
    .aggregate("total_revenue")
    .order_by("week_start")
)

# Calculate week-over-week changes
result = weekly_revenue.mutate(
    prev_week_revenue=_.total_revenue.lag(),
    wow_change=_.total_revenue - _.total_revenue.lag(),
    wow_pct_change=((_.total_revenue - _.total_revenue.lag()) / _.total_revenue.lag() * 100).round(2)
).limit(10)
```

<bslquery code-block="query_week_over_week"></bslquery>

## Percent of Running Total

Calculate each row's contribution to the cumulative total:

```query_pct_running
from ibis import _

# Top 10 days by revenue
top_days = (
    sales_st
    .group_by("sale_date")
    .aggregate("total_revenue")
    .order_by(_.total_revenue.desc())
    .limit(10)
)

# Calculate cumulative percentage
result = top_days.mutate(
    cumulative_revenue=_.total_revenue.cumsum(),
    total_top10=_.total_revenue.sum(),
    pct_of_top10=(_.total_revenue.cumsum() / _.total_revenue.sum() * 100).round(2)
)
```

<bslquery code-block="query_pct_running"></bslquery>

## Moving Window with Filters

Combine window functions with filtering for focused analysis:

```query_window_filter
from ibis import _

# Focus on weekends only
weekend_revenue = (
    sales_st
    .mutate(is_weekend=_.sale_date.day_of_week.index().isin([5, 6]))
    .filter(_.is_weekend)
    .group_by("sale_date")
    .aggregate("total_revenue")
    .order_by("sale_date")
)

# 3-weekend moving average
window_3 = ibis.window(rows=(-2, 0), order_by="sale_date")

result = weekend_revenue.mutate(
    ma_3weekend=_.total_revenue.mean().over(window_3).round(2),
    prev_weekend=_.total_revenue.lag(),
    weekend_change=_.total_revenue - _.total_revenue.lag()
).limit(10)
```

<bslquery code-block="query_window_filter"></bslquery>

## Key Takeaways

- **Window functions operate after aggregation**: They work on query results, not raw data
- **Order matters**: Most window functions require `order_by()` for meaningful results
- **Flexible windows**: Define windows by rows (`rows=(n, m)`) or ranges
- **Common patterns**:
  - `lag()/lead()` for period-over-period comparisons
  - `cumsum()` for running totals
  - `.over(window)` for moving averages
  - `rank()`, `row_number()` for ranking
- **Combine with filters**: Focus window calculations on specific subsets

## Next Steps

- Explore [Percentage of Total](/advanced/percentage-total) for ratio calculations
- Learn about [Nested Subtotals](/advanced/nested-subtotals) for hierarchical aggregations and complex data structures


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/sessionized.md`

# Sessionized Data

Analyze time-series events grouped into sessions based on activity gaps. This pattern identifies and aggregates user or system behavior within discrete time-bounded sessions.

## Overview

The sessionization pattern allows you to:

- Define session boundaries based on inactivity timeouts
- Group sequential events into logical sessions
- Calculate session-level metrics (duration, event count, conversion)
- Handle session spanning across multiple time periods

## Setup

Let's create user activity data with timestamps:

```setup_raw_data
import ibis
from ibis import _
from boring_semantic_layer import to_semantic_table

# Create user activity events with minute offsets instead of timestamps
activity_data = ibis.memtable({
    "user_id": ["user1", "user1", "user1", "user1", "user2", "user2", "user2", "user3", "user3", "user3", "user3", "user3"],
    "minute_offset": [0, 5, 10, 45, 2, 40, 42, 1, 3, 7, 50, 52],  # Minutes from start
    "page_url": ["/home", "/products", "/cart", "/checkout", "/home", "/products", "/cart",
                 "/home", "/about", "/products", "/home", "/contact"],
    "action": ["view", "view", "view", "purchase", "view", "view", "view",
               "view", "view", "view", "view", "view"]
})
```

<collapsedcodeblock code-block="setup_raw_data" title="Setup: Create Raw Activity Data"></collapsedcodeblock>

Now create a semantic table with dimensions and measures:

```semantic_table_def
from boring_semantic_layer import to_semantic_table

activity_st = (
    to_semantic_table(activity_data, name="activity")
    .with_dimensions(
        user_id=lambda t: t.user_id,
        minute_offset=lambda t: t.minute_offset,
        page_url=lambda t: t.page_url,
        action=lambda t: t.action
    )
    .with_measures(
        event_count=lambda t: t.count(),
        unique_users=lambda t: t.user_id.nunique()
    )
)
```

## Identify Session Boundaries

Use window functions to identify session starts based on inactivity gaps:

```query_session_boundaries
from ibis import _

result = (
    activity_st
    .group_by("user_id", "minute_offset", "page_url", "action")
    .aggregate()
    .mutate(
        # Calculate time since previous event for same user
        prev_minute=lambda t: t.minute_offset.lag().over(
            group_by="user_id",
            order_by=t.minute_offset
        ),
        # Calculate minutes since last event
        minutes_since_last=lambda t: t.minute_offset - t.prev_minute,
        # Mark session start (>30 min gap or first event)
        is_session_start=lambda t: (t.minutes_since_last > 30) | t.prev_minute.isnull()
    )
    .order_by(_.user_id, _.minute_offset)
)
```

<bslquery code-block="query_session_boundaries" />

## Assign Session IDs

Create session identifiers by counting session starts:

```query_with_session_ids
from ibis import _

result = (
    activity_st
    .group_by("user_id", "minute_offset", "page_url", "action")
    .aggregate()
    .mutate(
        prev_minute=lambda t: t.minute_offset.lag().over(
            group_by="user_id",
            order_by=t.minute_offset
        ),
        minutes_since_last=lambda t: t.minute_offset - t.prev_minute,
        is_session_start=lambda t: (t.minutes_since_last > 30) | t.prev_minute.isnull(),
        # Cumulative sum of session starts gives session ID
        session_id=lambda t: t.is_session_start.cast("int32").sum().over(
            group_by="user_id",
            order_by=t.minute_offset,
            rows=(None, 0)  # Cumulative sum
        )
    )
    .order_by(_.user_id, _.minute_offset)
)
```

<bslquery code-block="query_with_session_ids" />

## Calculate Session Metrics

Aggregate events by session to get session-level metrics:

```query_session_metrics
from ibis import _

result = (
    activity_st
    .group_by("user_id", "minute_offset", "action")
    .aggregate()
    .mutate(
        prev_minute=lambda t: t.minute_offset.lag().over(
            group_by="user_id",
            order_by=t.minute_offset
        ),
        minutes_since_last=lambda t: t.minute_offset - t.prev_minute,
        is_session_start=lambda t: (t.minutes_since_last > 30) | t.prev_minute.isnull(),
        session_id=lambda t: t.is_session_start.cast("int32").sum().over(
            group_by="user_id",
            order_by=t.minute_offset,
            rows=(None, 0)
        )
    )
    .group_by("user_id", "session_id")
    .aggregate(
        events_in_session=lambda t: t.count(),
        session_start_min=lambda t: t.minute_offset.min(),
        session_end_min=lambda t: t.minute_offset.max(),
        has_purchase=lambda t: (t.action == "purchase").any()
    )
    .mutate(
        session_duration_min=lambda t: (t.session_end_min - t.session_start_min)
    )
    .order_by(_.user_id, _.session_id)
)
```

<bslquery code-block="query_session_metrics" />

## User-Level Session Summary

Summarize sessions per user:

```query_user_summary
from ibis import _

result = (
    activity_st
    .group_by("user_id", "minute_offset", "action")
    .aggregate()
    .mutate(
        prev_minute=lambda t: t.minute_offset.lag().over(
            group_by="user_id",
            order_by=t.minute_offset
        ),
        minutes_since_last=lambda t: t.minute_offset - t.prev_minute,
        is_session_start=lambda t: (t.minutes_since_last > 30) | t.prev_minute.isnull(),
        session_id=lambda t: t.is_session_start.cast("int32").sum().over(
            group_by="user_id",
            order_by=t.minute_offset,
            rows=(None, 0)
        )
    )
    .group_by("user_id", "session_id")
    .aggregate(
        events_in_session=lambda t: t.count(),
        has_purchase=lambda t: (t.action == "purchase").any()
    )
    .group_by("user_id")
    .aggregate(
        total_sessions=lambda t: t.count(),
        total_events=lambda t: t.events_in_session.sum(),
        sessions_with_purchase=lambda t: t.has_purchase.cast("int32").sum(),
        avg_events_per_session=lambda t: t.events_in_session.mean().round(2)
    )
    .mutate(
        conversion_rate=lambda t: (t.sessions_with_purchase / t.total_sessions * 100).round(2)
    )
    .order_by(_.total_events.desc())
)
```

<bslquery code-block="query_user_summary" />

## Use Cases

**Web Analytics**: Group user page views and interactions into sessions, with a session ending after 30 minutes of inactivity. Calculate metrics like session duration, pages per session, and conversion rate.

**IoT Device Monitoring**: Sessionize sensor readings to identify distinct usage periods and calculate metrics like average session length and activity intensity.

**Application Usage Tracking**: Analyze how users interact with applications by grouping activities into sessions, identifying drop-off points, and measuring engagement patterns.

## Key Takeaways

- Use `lag()` window function to find time since previous event
- Compare time gaps to session timeout threshold (e.g., 30 minutes)
- Use cumulative sum of session starts to assign session IDs
- Calculate session metrics like duration, event count, and conversions
- Aggregate sessions to user level for summary statistics

## Next Steps

- Learn about [Indexing](/advanced/indexing) for trend analysis
- Explore [Bucketing](/advanced/bucketing) to categorize session durations


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/nested-subtotals.md`

# Nested Subtotals

Create hierarchical aggregations with subtotals at multiple levels using the `nest` parameter. This pattern enables drill-down analysis where each row contains both summary metrics and nested breakdowns.

## Overview

The nested subtotals pattern allows you to:

- Generate subtotals at each level of a dimensional hierarchy in a single query
- Create nested structures where each parent row contains child breakdowns
- Avoid complex self-joins or ROLLUP queries
- Build hierarchical data suitable for tree views and drill-down UIs

## Setup

Create a sample order items dataset with temporal and categorical dimensions:

```setup_data
import ibis
from ibis import _
from boring_semantic_layer import to_semantic_table

# Create synthetic order items data
order_items_data = ibis.memtable({
    "order_id": [1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010,
                 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020,
                 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030],
    "sale_price": [45.99, 89.50, 120.00, 34.99, 67.80, 99.99, 54.50, 78.99, 150.00, 42.00,
                   55.99, 72.50, 88.80, 110.00, 39.99, 95.00, 62.50, 81.99, 125.00, 48.50,
                   66.99, 92.00, 105.50, 73.99, 58.80, 118.00, 84.50, 69.99, 135.00, 51.50],
    "status": ["shipped", "delivered", "shipped", "processing", "delivered",
               "shipped", "cancelled", "delivered", "shipped", "processing",
               "delivered", "shipped", "delivered", "processing", "shipped",
               "cancelled", "delivered", "shipped", "delivered", "processing",
               "shipped", "delivered", "shipped", "processing", "delivered",
               "shipped", "cancelled", "delivered", "shipped", "processing"],
    "created_year": [2022, 2022, 2022, 2022, 2022, 2022, 2022, 2022, 2022, 2022,
                     2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023,
                     2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024, 2024],
    "created_month": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
                      1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
                      1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
})

# Create semantic table with measures
order_items = to_semantic_table(
    order_items_data,
    name="order_items",
).with_measures(
    order_count=lambda t: t.count(),
    total_sales=lambda t: t.sale_price.sum(),
    avg_price=lambda t: t.sale_price.mean(),
)
```

<collapsedcodeblock code-block="setup_data" title="Setup: Create Order Items Data"></collapsedcodeblock>

## Year with Nested Month Subtotals

Create yearly totals with monthly breakdowns nested inside each year:

```query_year_with_months
from ibis import _

# First aggregate by year and month to get monthly subtotals
monthly_data = (
    order_items
    .group_by("created_year", "created_month")
    .aggregate("order_count", "total_sales")
)

# Then nest months within years
result = (
    monthly_data
    .group_by("created_year")
    .aggregate(
        year_order_count=lambda t: t.order_count.sum(),
        year_total_sales=lambda t: t.total_sales.sum(),
        nest={"by_month": lambda t: t.group_by(["created_month", "order_count", "total_sales"]).order_by("created_month")}
    )
    .order_by("created_year")
)
```

<bslquery code-block="query_year_with_months"></bslquery>

<note type="info">
Each year row contains a `by_month` array with all monthly subtotals for that year. The pattern is: aggregate at the finest level first, then nest at each parent level.
</note>

## Year with Nested Status Subtotals

Alternative breakdown: nest order status within each year:

```query_year_with_status
from ibis import _

# First aggregate by year and status
status_data = (
    order_items
    .group_by("created_year", "status")
    .aggregate("order_count", "total_sales", "avg_price")
)

# Then nest status within years
result = (
    status_data
    .group_by("created_year")
    .aggregate(
        year_order_count=lambda t: t.order_count.sum(),
        year_total_sales=lambda t: t.total_sales.sum(),
        nest={"by_status": lambda t: t.group_by(["status", "order_count", "total_sales", "avg_price"]).order_by(_.total_sales.desc())}
    )
    .order_by("created_year")
)
```

<bslquery code-block="query_year_with_status"></bslquery>

## Multi-Level Nesting: Year > Month > Status

Create three-level hierarchy with nested subtotals:

```query_multi_level
from ibis import _

# First aggregate at the finest level: year, month, status
detailed_data = (
    order_items
    .group_by("created_year", "created_month", "status")
    .aggregate("order_count", "total_sales")
)

# Second level: nest status within month
monthly_with_status = (
    detailed_data
    .group_by("created_year", "created_month")
    .aggregate(
        month_order_count=lambda t: t.order_count.sum(),
        month_total_sales=lambda t: t.total_sales.sum(),
        nest={"by_status": lambda t: t.group_by(["status", "order_count", "total_sales"])}
    )
)

# Top level: nest months within year
result = (
    monthly_with_status
    .group_by("created_year")
    .aggregate(
        year_order_count=lambda t: t.month_order_count.sum(),
        year_total_sales=lambda t: t.month_total_sales.sum(),
        nest={"by_month": lambda t: t.group_by(["created_month", "month_order_count", "month_total_sales", "by_status"]).order_by("created_month")}
    )
    .order_by("created_year")
    .limit(3)
)
```

<bslquery code-block="query_multi_level"></bslquery>

## Use Cases

**Financial Reporting**: Create income statements with nested line items - show total revenue with product categories nested inside, each containing individual products.

**Geographic Hierarchies**: Aggregate sales by region, with nested states, with nested cities, all in a single query result.

**Time-Based Drill-Downs**: Show yearly summaries with monthly breakdowns nested inside, perfect for dashboard drill-down interactions.

**Organizational Analysis**: Display department totals with nested team breakdowns, with nested individual employee details.

## Key Takeaways

- Use the `nest` parameter in `.aggregate()` to create hierarchical subtotals
- Each parent row contains an array column with child-level breakdowns
- Avoid complex SQL ROLLUP or self-join patterns
- Nest multiple levels deep for complex hierarchies
- Perfect for building tree views, expandable tables, and drill-down UIs

## Next Steps

- Learn about [Percentage of Total](/advanced/percentage-total) calculations
- Explore [Bucketing](/advanced/bucketing) for categorizing continuous values


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/percentage-total.md`

# Percentage of Total

Calculate percentages relative to total values across different dimensions. Use this pattern when you need to understand market share, contribution ratios, or what proportion each segment represents of the whole.

## Overview

The percentage of total pattern allows you to:

- Define percentage measures using the `.all()` method
- Calculate individual segment values as percentages of the grand total
- Maintain dimensional breakdowns while computing percentage contributions
- Support multiple aggregation functions (sum, count, average)

## Setup

Let's use the flights dataset with carrier information to demonstrate market share calculations:

```setup_data
import ibis
from ibis import _
from boring_semantic_layer import to_semantic_table

# Create synthetic flights data with carrier information
flights_data = ibis.memtable({
    "flight_id": list(range(1, 51)),
    "carrier": ["AA", "UA", "DL", "WN", "B6"] * 10,
    "nickname": ["American Airlines", "United Airlines", "Delta Air Lines",
                 "Southwest Airlines", "JetBlue Airways"] * 10,
    "origin": ["JFK", "LAX", "ORD", "ATL", "DFW"] * 10,
    "distance": [2475, 1745, 733, 946, 1383, 2475, 1745, 733, 946, 1383,
                 2475, 1745, 733, 946, 1383, 2475, 1745, 733, 946, 1383,
                 2475, 1745, 733, 946, 1383, 2475, 1745, 733, 946, 1383,
                 2475, 1745, 733, 946, 1383, 2475, 1745, 733, 946, 1383,
                 2475, 1745, 733, 946, 1383, 2475, 1745, 733, 946, 1383]
})

# Create semantic table with measures including percentage calculations
flights = (
    to_semantic_table(flights_data, name="flights")
    .with_measures(
        flight_count=lambda t: t.count(),
        total_distance=lambda t: t.distance.sum(),
    )
    .with_measures(
        market_share=lambda t: t.flight_count / t.all(t.flight_count) * 100,
        distance_share=lambda t: t.total_distance / t.all(t.total_distance) * 100,
    )
)
```

<collapsedcodeblock code-block="setup_data" title="Setup: Create Flights and Carriers Data"></collapsedcodeblock>

<note type="info">
The `.all()` method calculates the grand total across all groups, allowing you to define percentage measures directly in the semantic table. This is more elegant than using window functions in post-processing.
</note>

## Market Share by Carrier

Calculate each carrier's percentage of total flights:

```query_market_share
from ibis import _

result = (
    flights.group_by("nickname")
    .aggregate("flight_count", "market_share")
    .order_by(_.market_share.desc())
    .limit(10)
)
```

<bslquery code-block="query_market_share"></bslquery>

## Market Share by Origin and Carrier

Calculate market share broken down by both origin airport and carrier:

```query_market_share_by_origin
from ibis import _

result = (
    flights.group_by("origin", "nickname")
    .aggregate("flight_count", "market_share")
    .order_by(_.market_share.desc())
    .limit(15)
)
```

<bslquery code-block="query_market_share_by_origin"></bslquery>

## Use Cases

**Market Share Analysis**: Calculate each carrier's, product's, or region's share of total volume.

**Traffic Distribution**: Determine what percentage of total website visits or conversions come from each source.

**Resource Allocation**: Understand how resources (budget, time, capacity) are distributed as percentages of the total.

## Key Takeaways

- Define percentage measures using `.all()` to reference the grand total
- The `.all(measure)` method calculates the total across all groups
- Percentage measures work seamlessly across different dimensional breakdowns
- More elegant than post-processing with window functions

## Next Steps

- Learn about [Nested Subtotals](/advanced/nested-subtotals) for hierarchical aggregations
- Explore [Bucketing](/advanced/bucketing) to group continuous values


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/comparison.md`

# BSL vs Malloy vs dbt Semantic Layer

Comprehensive comparison of three semantic layer solutions to help you choose the right tool for your needs.

## Comparison Table

| Aspect | BSL | Malloy | dbt Semantic Layer |
|--------|-----|--------|-------------------|
| **Language Type** | Pure Python API | Custom DSL (programming language) | YAML Configuration |
| **Query Style** | Python fluent API with lambdas | Malloy query language with `->` operator | CLI commands or API calls |
| **Learning Curve** | Python + Ibis expressions | New language (approachable syntax) | YAML + dbt + MetricFlow concepts |
| **Backend Support** | 20+ databases via Ibis | 7 databases (BigQuery, Snowflake, PostgreSQL, MySQL, Trino, Presto, DuckDB) | dbt-supported warehouses |
| **License** | Open Source | MIT (fully open source) | Hybrid (MetricFlow open, full Layer requires paid dbt Cloud) |
| **Cost** | ✅ Free | ✅ Free | ⚠️ Free for local use, paid for cloud APIs & BI integrations |
| **Visualization** | Built-in (Altair/Plotly) | Built-in (basic in VSCode/Composer) | Via BI tool integrations |
| **AI/LLM Support** | ✅ MCP protocol native | Not explicit | ✅ Native (MetricFlow open-sourced for AI) |
| **IDE Support** | Standard Python IDEs | ✅ Excellent VSCode extension | dbt Cloud IDE |
| **Programming Languages** | Python | Python (`malloy-py`), JavaScript/TypeScript | Python (`dbt-metricflow`) |
| **Dimensions** | Lambda functions with Ibis | Native `dimension:` syntax | YAML `dimensions:` definitions |
| **Measures** | Lambda functions with aggregations | Native `measure:` syntax | YAML `measures:` with aggregation types |
| **Joins** | Ibis join system | ✅ Graph-based, automatic safety (prevents fan-out) | Entity-based, dynamic at query time |
| **Nested Queries** | Via Ibis subqueries | ✅ Native, infinite nesting | Limited |
| **Time Operations** | Ibis time functions (`.year()`, `.month()`) | ✅ Built-in syntax (`@2003`, `.year`, `.month`) | Time dimensions with granularity |
| **Window Functions** | ✅ Full Ibis support | ✅ Supported | ✅ Supported |
| **Calculated Fields** | Python expressions with Ibis | Built-in expressions with `pick` statements | SQL expressions in YAML |
| **Metric Types** | Custom via Python | Dimensions + Measures | 5 types: Simple, Ratio, Cumulative, Derived, Conversion |
| **Performance** | Depends on Ibis + backend | ✅ Optimized SQL generation (faster than hand-written) | Depends on warehouse + caching |
| **BI Integrations** | Export to DataFrames for any tool | Export + growing ecosystem | ✅ Extensive (Tableau, Power BI, Looker, Mode, Hex, etc.) |
| **CLI Tools** | Standard Python | `malloy-cli` (run, compile, connections) | `dbt sl` (query, list, validate) |
| **Setup Complexity** | ⚡ Simple (`pip install`) | Medium (npm/VSCode extension) | Complex (requires dbt project) |
| **Community Size** | Growing | Medium (Google-backed) | ✅ Large (dbt ecosystem) |
| **Primary Use Case** | Python-first analytics, AI agents | Complex analytical queries, BigQuery | Enterprise metrics governance |
| **Target Audience** | Data scientists, Python developers | Data analysts, anyone wanting "better SQL" | Analytics engineers, enterprise teams |
| **Enterprise Features** | Basic | Basic | ✅ Governance, validation, centralized metrics |
| **Documentation** | Growing | ✅ Comprehensive | ✅ Extensive |
| **Query Syntax Example** | `.filter(lambda t: t.year > 1900)` | `where: year > 1900` | `--where "year > 1900"` |
| **Join Syntax** | Explicit Ibis joins | `join_one: users with user_id` | Entity relationships in YAML |
| **Inspired By** | Malloy + Ibis portability | Looker (created by Looker founder) | LookML + metrics-as-code |


## Resources

### BSL
- GitHub: [boring-semantic-layer](https://github.com/boringdata/boring-semantic-layer)
- Docs: [boringdata.github.io/boring-semantic-layer](https://boringdata.github.io/boring-semantic-layer/)
- Install: `pip install boring-semantic-layer`

### Malloy
- Website: [malloydata.dev](https://www.malloydata.dev/)
- Docs: [docs.malloydata.dev](https://docs.malloydata.dev/)
- GitHub: [malloydata/malloy](https://github.com/malloydata/malloy)
- Install: `npm install -g @malloydata/malloy-cli` or VSCode extension

### dbt Semantic Layer
- Website: [getdbt.com/product/semantic-layer](https://www.getdbt.com/product/semantic-layer)
- Docs: [docs.getdbt.com](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
- GitHub: [dbt-labs/metricflow](https://github.com/dbt-labs/metricflow)
- Install: `pip install dbt-metricflow`


## BSL — Charting & Visualization


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/charting.md`

# Charting

BSL includes built-in support for generating data visualizations from your semantic queries. Create charts directly from query results with automatic chart type detection or full custom control.

## Installation

To use chart visualization, install with the appropriate backend:

```bash
# For Altair backend (default)
pip install 'boring-semantic-layer[viz-altair]'

# For Plotly backend
pip install 'boring-semantic-layer[viz-plotly]'
```

## Quick Start

Here's a simple example showing how to create a chart:

```setup_chart_data
import ibis
from boring_semantic_layer import to_semantic_table

con = ibis.duckdb.connect(":memory:")
flights_data = ibis.memtable({
    "origin": ["JFK", "LAX", "SFO", "ORD", "DFW", "ATL", "DEN"],
    "flight_count": [150, 135, 89, 112, 98, 145, 78],
    "avg_distance": [2475, 1850, 1200, 950, 1100, 1650, 900]
})
flights_tbl = con.create_table("flights", flights_data)

flights_st = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin=lambda t: t.origin
    )
    .with_measures(
        flight_count=lambda t: t.flight_count.sum(),
        avg_distance=lambda t: t.avg_distance.mean()
    )
)
```

<collapsedcodeblock code-block="setup_chart_data" title="Setup: Create Sample Data"></collapsedcodeblock>

```query_basic_chart
# Query and chart in one fluent chain
result = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count")
    .order_by(ibis.desc("flight_count"))
    .limit(5)
)

result.chart()
```

<altairchart code-block="query_basic_chart"></altairchart>

<note type="info">
The `.chart()` method is available on query results from `.aggregate()`, `.order_by()`, `.limit()`, and `.mutate()` operations.
</note>

## Backend Selection

BSL supports two charting backends with different strengths:

### Altair (Default)

**Best for:** Web-native interactive visualizations, declarative specifications, embedding in notebooks and web apps.

```python
# Use Altair backend (default)
chart = result.chart()
# or explicitly
chart = result.chart(backend="altair")
```

**Features:**
- Built on Vega-Lite grammar
- Declarative JSON specifications
- Great for interactive web visualizations
- Excellent notebook integration

### Plotly

**Best for:** Rich interactive dashboards, 3D visualizations, extensive chart types, business intelligence tools.

```python
# Use Plotly backend
chart = result.chart(backend="plotly")
```

**Features:**
- Extensive chart type library
- Rich interactivity out of the box
- Dashboard integration
- Export to static formats

## Auto-Detection

BSL automatically detects the appropriate chart type based on your query structure:

### Bar Chart (Categorical Data)

Single dimension + measure → Bar chart

```query_bar_chart
result = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count")
    .order_by(ibis.desc("flight_count"))
)

result.chart()
```

<altairchart code-block="query_bar_chart"></altairchart>

**Auto-detected because:** Single categorical dimension (`origin`) with one measure (`flight_count`)

### Time Series (Temporal Data)

Time dimension + measure → Line chart with time-aware formatting

```setup_timeseries
import ibis
from boring_semantic_layer import to_semantic_table

con = ibis.duckdb.connect(":memory:")
timeseries_data = ibis.memtable({
    "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05", "2024-01-06", "2024-01-07"],
    "flight_count": [145, 152, 148, 139, 156, 161, 143]
})
timeseries_tbl = con.create_table("daily_flights", timeseries_data)

daily_flights_st = (
    to_semantic_table(timeseries_tbl, name="daily_flights")
    .with_dimensions(
        date={
            "expr": lambda t: t.date.cast("date"),
            "is_time_dimension": True,
            "smallest_time_grain": "TIME_GRAIN_DAY"
        }
    )
    .with_measures(
        flight_count=lambda t: t.flight_count.sum()
    )
)
```

<collapsedcodeblock code-block="setup_timeseries" title="Setup: Create Time Series Data"></collapsedcodeblock>

```query_timeseries
result = (
    daily_flights_st
    .group_by("date")
    .aggregate("flight_count")
)
result.chart()
```

<altairchart code-block="query_timeseries"></altairchart>

**Auto-detected because:** Dimension marked as `is_time_dimension=True`

### Heatmap (Two Dimensions)

Two categorical dimensions + measure → Heatmap

```setup_heatmap
import ibis
from boring_semantic_layer import to_semantic_table

con = ibis.duckdb.connect(":memory:")
route_data = ibis.memtable({
    "origin": ["JFK", "JFK", "LAX", "LAX", "SFO", "SFO"],
    "dest": ["LAX", "SFO", "JFK", "SFO", "JFK", "LAX"],
    "flight_count": [45, 32, 43, 28, 31, 27]
})
route_tbl = con.create_table("routes", route_data)

routes_st = (
    to_semantic_table(route_tbl, name="routes")
    .with_dimensions(
        origin=lambda t: t.origin,
        dest=lambda t: t.dest
    )
    .with_measures(
        flight_count=lambda t: t.flight_count.sum()
    )
)
```

<collapsedcodeblock code-block="setup_heatmap" title="Setup: Create Route Data"></collapsedcodeblock>

```query_heatmap
result = (
    routes_st
    .group_by("origin", "dest")
    .aggregate("flight_count")
)
result.chart()
```

<altairchart code-block="query_heatmap"></altairchart>

**Auto-detected because:** Two categorical dimensions with one measure

### Multi-Series Charts

Multiple measures → Grouped/overlaid visualization with color encoding

```query_multi_measure
result = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count", "avg_distance")
    .limit(5)
)
result.chart()
```

<altairchart code-block="query_multi_measure"></altairchart>

**Auto-detected because:** Multiple measures trigger automatic color encoding by measure name


## Custom Specifications

Override auto-detection with custom specifications:

### Change Mark Type And Add Styling

Customize the mark type while providing explicit encodings:

```query_custom_mark
import ibis
# Create line chart with custom spec
result = (
    flights_st
    .group_by("origin")
    .aggregate("flight_count")
    .order_by(ibis.desc("flight_count"))
    .limit(5)
)
result.chart(spec={
    "mark": {"type": "line", "color": "#e74c3c"}
})
```

<altairchart code-block="query_custom_mark"></altairchart>

<note type="info">
You don't need to provide full vega spec: the spec object is merged with the BSL's default one.
</note>

## Export Formats

Export charts in various formats for different use cases:

```python
# Interactive chart object (default)
chart = result.chart()

# JSON specification for web embedding
json_spec = result.chart(format="json")

# PNG image (requires altair[all] or plotly)
png_bytes = result.chart(format="png")

# SVG markup (requires altair[all] or plotly)
svg_str = result.chart(format="svg")

# Save to file
with open("my_chart.png", "wb") as f:
    f.write(png_bytes)
```

**Available formats:**
- `"static"` or `"interactive"` - Chart object (default)
- `"json"` - JSON specification
- `"png"` - PNG image bytes
- `"svg"` - SVG markup string

## Next Steps

- Learn about [Query Methods](/querying/methods) to build complex queries
- Explore [YAML Configuration](/building/yaml) for declarative semantic models
- See [Compose Models](/building/compose) for joining semantic tables


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/profile.md`

# Backend Profiles

BSL provides a profile system for managing database connections using configuration files. Profiles let you:

- **Store backend configurations** for different environments (dev, staging, prod)
- **Share connections across systems** using global or local profile files
- **Switch backends easily** without changing your code
- **Secure credentials** with environment variable substitution


## Quick Start

### Python-Based

```python
from boring_semantic_layer import get_connection, to_semantic_table

# Load connection directly by profile name
# Searches for 'my_db' profile in:
#   1. ~/.config/bsl/profiles/my_db.yml
#   2. ./profiles.yml (current directory)
#   3. xorq profiles directory
con = get_connection('my_db')

# Load from a specific file
con = get_connection('my_db', profile_file='config/profiles.yml')

# Use the connection to access tables and create semantic tables
flights_table = con.table('flights')
flights = to_semantic_table(flights_table)
```

## Profile YAML Format

Create a `profiles.yml` file in your project directory:

```yaml
dev_db:
  type: duckdb
  database: dev.db

prod_db:
  type: postgres
  host: ${POSTGRES_HOST}
  database: ${POSTGRES_DB}
  user: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
```

**Notes:**
- The `type` field corresponds to the ibis backend name. Each backend has specific required parameters - see the [Supported Backends](#supported-backends) section below for details.
- Use `${VAR_NAME}` or `$VAR_NAME` syntax for environment variables (see `prod_db` example above for securing credentials). Environment variables are resolved at connection time from the OS environment.

### YAML-Based

**File-level profile** - all tables from one connection (must be defined in a profiles.yml file):

```yaml
# flights_model.yml
profile: my_db

flights:
  table: flights
  dimensions:
    origin: _.origin
  measures:
    flight_count: _.count()
```

**Table-level profiles** - different tables from different connections:

```yaml
# multi_db_model.yml
flights:
  profile: postgres_db
  table: flights
  dimensions:
    origin: _.origin
  measures:
    flight_count: _.count()

carriers:
  profile: duckdb_db
  table: carriers
  dimensions:
    code: _.code
    name: _.name
```

```python
from boring_semantic_layer import from_yaml

# Profiles loaded automatically from YAML
models = from_yaml('multi_db_model.yml')

# Or pass profile as parameter
models = from_yaml('model.yml', profile='my_db')
```

## Profile Resolution Order

`get_connection('my_db')` searches in this order:
1. `~/.config/bsl/profiles/my_db.yml` (BSL-specific profiles)
2. `./profiles.yml` (local project profiles)
3. xorq profiles directory (system-wide xorq profiles)

You can customize the search order:

```python
from boring_semantic_layer import get_connection

# Specify custom search order
con = get_connection('my_db', search_locations=['bsl_dir'])

# Search only local directory
con = get_connection('my_db', search_locations=['local'])

# Custom order
con = get_connection('my_db', search_locations=['local', 'bsl_dir', 'xorq_dir'])
```

`from_yaml()` resolves profiles in priority order (first match wins):

1. **`profile` parameter** - Explicit argument passed to `from_yaml()`:
   ```python
   models = from_yaml('model.yml', profile='my_db')
   ```

2. **`BSL_PROFILE` environment variable** - System-wide default:
   ```bash
   export BSL_PROFILE=my_db
   ```

3. **YAML file-level `profile`** - Default defined inside the YAML file:
   ```yaml
   profile: my_db  # File-level default
   models:
     flights: ...
   ```

4. **Table-level `profile`** - Per-table override (see [YAML-Based](#yaml-based) section)

## Supported Backends

BSL uses xorq backends for all connections, which provide caching and performance optimizations. The `type` field in your profile corresponds to the ibis backend name, and the other fields are passed as connection parameters.

```python
con = get_connection('my_db')  # Uses xorq backend
```

See the [ibis backends documentation](https://ibis-project.org/backends/) for the complete list of supported backends and their required connection parameters.

## Auto-Loading Parquet Files

The `tables` configuration automatically creates database tables from parquet files when loading a profile:

```python
from boring_semantic_layer import get_connection

con = get_connection('test_db')  # Creates 'flights' table
print(con.list_tables())         # ['flights']
```

Supports both string paths and dict config:

```yaml
test_db:
  type: duckdb
  database: ":memory:"
  tables:
    # String format
    flights: "data/flights.parquet"

    # Dict format
    carriers:
      source: "data/carriers.parquet"
```

Ideal for testing, CI/CD, and prototyping. Supports local files, remote URLs, and S3 paths. The `tables` configuration works with any backend that supports `read_parquet()` (DuckDB, Polars, DataFusion, etc.). An error will be raised if the backend doesn't support this feature.

## BSL — Query Agent (Natural Language)


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent.md`

# Query Agent

The Query Agent lets you ask natural-language questions about your semantic tables.

It converts a user prompt into a valid BSL query and returns the resulting table or chart along with a concise summary.

You can expose the Query Agent in three ways, depending on your workflow:

### [MCP Server](/agents/mcp)

Expose your tables to any LLM via the Model Context Protocol.

- **Pros:** All major LLM providers support MCP out-of-the-box
- **Cons:** Requires running an MCP server alongside your project

### [LLM Tool](/agents/tool)

Let the model execute BSL queries directly as a callable tool.

- **Pros:** No additional infrastructure—the LLM executes queries inline
- **Cons:** Requires a sandboxing solution for production use

### [AI Skills (CLI)](/agents/skill)

Add BSL querying to your local coding assistant (Claude Code, Cursor, Codex).

- **Pros:** Fastest setup—run `bsl skill install` and you're ready
- **Cons:** Runs locally only

---

Want to try it out? The [Demo Chat](/agents/chat) provides a built-in CLI interface to explore your semantic models using natural language.


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-chat.md`

# Query Agent: Demo Chat

The BSL CLI includes a built-in chat interface to interact with your semantic models using natural language. It uses LangChain under the hood and supports multiple LLM providers.

<img src="/bsl-chat-demo.png" alt="BSL Chat Demo" width="600" />

## Installation

Install BSL with the agent extra:

```bash
pip install 'boring-semantic-layer[agent]'
```

Then install the LLM provider package for your preferred model:

```bash
# For Claude models
pip install langchain-anthropic

# For GPT models
pip install langchain-openai

# For Gemini models
pip install langchain-google-genai
```

See the LangChain docs for available models: [Anthropic](https://python.langchain.com/docs/integrations/chat/anthropic/) | [OpenAI](https://python.langchain.com/docs/integrations/chat/openai/) | [Google](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)

Set your API key for your preferred LLM provider:

```bash
# For Claude models
export ANTHROPIC_API_KEY=sk-ant-...

# For GPT models
export OPENAI_API_KEY=sk-...

# For Gemini models
export GOOGLE_API_KEY=...
```

## Configuration

You can optionally set the semantic model path in a `.env` file or as environment variables:

```bash
# .env

# Optional: default semantic model path (avoids --sm flag)
BSL_MODEL_PATH=path/to/your/model.yaml

# Optional: default profile name (avoids --profile flag)
BSL_PROFILE=my_profile

# Optional: default profile file path (avoids --profile-file flag)
BSL_PROFILE_FILE=path/to/profiles.yml
```

## Starting the chat

```bash
bsl chat --sm path/to/your/model.yaml
```

You can also pass a prompt directly to skip interactive mode:

```bash
bsl chat --sm path/to/your/model.yaml "What are the top 5 origins by flight count?"
```

## Required flags

| Flag | Description |
|------|-------------|
| `--sm` | Path to your semantic model YAML file |
| `--model` | LLM model to use (OpenAI, Anthropic, or Google) |

## Optional flags

| Flag | Description |
|------|-------------|
| `--chart-backend` | Chart renderer: `plotext` (terminal, default), `altair` (opens in browser), or `plotly` (opens in browser) |
| `--profile` | Profile name to use |
| `--profile-file` | Path to a custom profiles file |



> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-llm-tool.md`

# Query Agent: LLM Tool

LLM tools are Python functions that a language model can call during a conversation. When the model needs data, it invokes a tool, receives the result, and continues reasoning.

The advantage of this approach is that the LLM can directly execute Ibis-style chained queries—unlike MCP, which requires passing JSON payloads through a separate server.

**Benefits:**
- No additional server to run
- Full access to native BSL features without an intermediate DSL

## BSLTools: Framework-Agnostic Tool Layer

`BSLTools` provides tool definitions in OpenAI JSON Schema format (the de facto standard), making it compatible with any LLM provider:

- **OpenAI**: `client.chat.completions.create(tools=bsl.tools)`
- **LangChain**: `llm.bind_tools(bsl.tools)`
- **Anthropic**, **PydanticAI**, **AI SDK**, etc.

### Installation

```bash
pip install boring-semantic-layer[agent]
```

### Usage

```python
import json
from pathlib import Path
from openai import OpenAI
from boring_semantic_layer.agents.tools import BSLTools

# Initialize BSLTools with your semantic model
bsl = BSLTools(
    model_path=Path("flights.yml"),
    profile="dev",                        # Profile name (optional)
    profile_file=Path("profiles.yml"),    # Profile file path (optional)
    chart_backend="plotext",              # plotext, altair, or plotly
)

# Use with OpenAI SDK
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": bsl.system_prompt},
        {"role": "user", "content": "Show top 5 carriers by flight count"},
    ],
    tools=bsl.tools,
)

# Execute tool calls
for tool_call in response.choices[0].message.tool_calls or []:
    result = bsl.execute(
        tool_call.function.name,
        json.loads(tool_call.function.arguments)
    )
    print(result)
```

See [YAML Config](/building/yaml) for the semantic model format and [Backend Profiles](/building/profile) for connection setup.

### What BSLTools Provides

| Attribute | Description |
|-----------|-------------|
| `bsl.tools` | Tool definitions in OpenAI JSON Schema format |
| `bsl.system_prompt` | System prompt teaching the LLM how to write BSL queries |
| `bsl.execute(name, args)` | Execute a tool and return the result |

### Available Tools

The LLM has access to three tools:

#### `list_models`

Lists all available semantic models with their dimensions and measures. Useful when multiple models are loaded and the LLM needs to pick the right one.

#### `query_model`

Executes a BSL query and returns results. The LLM passes an Ibis-style query string:

```python
sm.group_by("origin").aggregate("flight_count")
```

**Parameters:**
- `query` — The BSL query string to execute
- `chart_spec` — Chart specification (backend, format, and visualization options)

#### `get_documentation`

Returns BSL documentation split into topics (query syntax, methods, charting, etc.). The LLM can explore relevant topics on demand to learn how to construct valid queries and charts.

## LangGraph Reference Implementation

For multi-turn conversations with history management, we provide a LangGraph-based agent:

👉 [`langgraph.py`](https://github.com/boringdata/boring-semantic-layer/blob/main/src/boring_semantic_layer/agents/backends/langgraph.py)

This implementation powers the [BSL CLI demo chat](/agents/chat).

### Installation

Install the agent dependencies plus your LLM provider:

```bash
pip install boring-semantic-layer[agent]

# Anthropic (recommended)
pip install langchain-anthropic

# OpenAI
pip install langchain-openai

# Google
pip install langchain-google-genai
```

### Usage

```python
from pathlib import Path
from boring_semantic_layer.agents.backends import LangGraphBackend

agent = LangGraphBackend(
    model_path=Path("flights.yml"),
    llm_model="anthropic:claude-sonnet-4-20250514",  # or "openai:gpt-4o"
    chart_backend="plotext",              # plotext, altair, or plotly
    profile="dev",                        # Profile name (optional)
    profile_file=Path("profiles.yml"),    # Profile file path (optional)
)

tool_output, response = agent.query("What are the top 10 origins by flight count?")
```


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-mcp.md`

# Query Agent: MCP Server

BSL includes built-in support for the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk), allowing you to expose your semantic models to Large Language Models like Claude.

<note type="info">
**Pro tip:** Use [descriptions in dimensions and measures](/building/semantic-tables#adding-descriptions) to make your models more AI-friendly. Descriptions help provide context to LLMs, enabling them to understand what each field represents and when to use them.
</note>

## Installation

To use MCP functionality, install BSL with the `fastmcp` extra:

```bash
pip install 'boring-semantic-layer[fastmcp]'
```

## Setting up an MCP Server

Create an MCP server script that exposes your semantic models:

```python
import ibis
from boring_semantic_layer import to_semantic_table, MCPSemanticModel

# Create synthetic flights data
flights_data = ibis.memtable({
    "flight_id": list(range(1, 101)),
    "origin": ["JFK", "LAX", "ORD", "ATL", "DFW"] * 20,
    "dest": ["LAX", "JFK", "DFW", "ORD", "ATL"] * 20,
    "carrier": ["AA", "UA", "DL", "WN", "B6"] * 20,
    "distance": [2475, 2475, 801, 606, 732] * 20,
})

# Define your semantic table with descriptions
flights = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code where the flight departed from"
        },
        destination={
            "expr": lambda t: t.dest,
            "description": "Destination airport code where the flight arrived"
        },
        carrier={
            "expr": lambda t: t.carrier,
            "description": "Airline carrier code (e.g., AA, UA, DL)"
        },
    )
    .with_measures(
        total_flights={
            "expr": lambda t: t.count(),
            "description": "Total number of flights"
        },
        avg_distance={
            "expr": lambda t: t.distance.mean(),
            "description": "Average flight distance in miles"
        },
    )
)

# Create the MCP server
mcp_server = MCPSemanticModel(
    models={"flights": flights},
    name="Flight Data Server"
)

if __name__ == "__main__":
    mcp_server.run(transport="stdio")
```

Save this as `example_mcp.py` in your project directory.

## Configuring Claude Desktop

To use your MCP server with Claude Desktop, add it to your configuration file.

**Configuration file location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Example configuration:**

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/",
        "run",
        "example_mcp.py"
      ]
    }
  }
}
```

Replace `/path/to/your/project/` with the actual path to your project directory.

<note type="info">
This example uses [uv](https://docs.astral.sh/uv/) to run the MCP server. You can also use `python` directly if you have BSL installed in your environment:

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "python",
      "args": ["/path/to/your/project/example_mcp.py"]
    }
  }
}
```
</note>

After updating the configuration:
1. Restart Claude Desktop
2. Look for the MCP server indicator in the Claude Desktop interface
3. You should see "flight_sm" listed as an available server

## Available MCP Tools

Once configured, Claude will have access to these tools for interacting with your semantic models:

### list_models

List all available semantic model names in the MCP server.

**Example usage in Claude:**
> "What models are available?"

**Returns:** Array of model names (e.g., `["flights", "carriers"]`)

### get_model

Get detailed information about a specific model including its dimensions, measures, and descriptions.

**Parameters:**
- `model_name` (str): Name of the model to inspect

**Example usage in Claude:**
> "Show me the details of the flights model"

**Returns:** Model schema including:
- Model name and description
- List of dimensions with their descriptions
- List of measures with their descriptions
- Available joins (if any)

### get_time_range

Get the available time range for time-series data in a model.

**Parameters:**
- `model_name` (str): Name of the model
- `time_dimension` (str): Name of the time dimension

**Example usage in Claude:**
> "What's the time range available in the flights model?"

**Returns:** Dictionary with `min_time` and `max_time` values

### query_model

Execute queries against a semantic model with dimensions, measures, filters, and optional chart specifications.

**Parameters:**
- `model_name` (str): Name of the model to query
- `dimensions` (list[str]): List of dimension names to group by
- `measures` (list[str]): List of measure names to aggregate
- `filters` (list[str], optional): List of filter expressions (e.g., `["origin == 'JFK'"]`)
- `limit` (int, optional): Maximum number of rows to return
- `order_by` (list[str], optional): List of columns to sort by
- `chart_spec` (dict, optional): Vega-Lite chart specification

**Example usage in Claude:**
> "Show me the top 10 origins by flight count"
> "Create a bar chart of average distance by carrier"

**Returns:**
- When `chart_spec` is provided: `{"records": [...], "chart": {...}}`
- When `chart_spec` is not provided: `{"records": [...]}`

### Example Interactions

Here are some example questions you can ask Claude when the MCP server is configured:

**Data Exploration:**
- "What models are available in the flight data server?"
- "Show me all dimensions and measures in the flights model"
- "What is the time range covered by the flights data?"

**Basic Queries:**
- "How many flights departed from JFK?"
- "Show me the top 5 destinations by flight count"
- "What's the average flight distance for each carrier?"

**Filtered Queries:**
- "Show me flights from California airports (starting with 'S')"
- "What carriers have an average distance over 1000 miles?"
- "List the top 10 busiest routes"

**Visualizations:**
- "Create a bar chart showing flights by origin airport"
- "Make a line chart of flights over time"
- "Show me a heatmap of routes between origins and destinations"

## Best Practices

### 1. Add Descriptions to All Fields

Descriptions are crucial for LLMs to understand your data model:

```python
flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code (3-letter IATA code)"
        }
    )
    .with_measures(
        total_flights={
            "expr": lambda t: t.count(),
            "description": "Total number of flights in the dataset"
        }
    )
)
```

### 2. Use Descriptive Model Names

Choose clear, descriptive names for your models:

```python
# Good
mcp_server = MCPSemanticModel(
    models={"flights": flights, "carriers": carriers},
    name="Aviation Analytics Server"
)

# Less clear
mcp_server = MCPSemanticModel(
    models={"f": flights, "c": carriers},
    name="Server"
)
```

### 3. Define Time Dimensions for Time-Series Queries

When exposing models through MCP, you need to explicitly define time dimensions to enable LLMs to query time ranges and perform time-based aggregations. This is specific to MCP—when using BSL's fluent API directly, you can simply use Ibis functions like `.year()` and `.month()`.

To define a time dimension, set `is_time_dimension=True` and specify the `smallest_time_grain`:

```python
from boring_semantic_layer import to_semantic_table

flights = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        arr_time={
            "expr": lambda t: t.arr_time,
            "description": "Arrival time of the flight",
            "is_time_dimension": True,
            "smallest_time_grain": "TIME_GRAIN_SECOND",
        },
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code"
        },
    )
    .with_measures(
        flight_count={
            "expr": lambda t: t.count(),
            "description": "Total number of flights"
        }
    )
)
```

**Available time grains:**
- `TIME_GRAIN_SECOND` - For second-level precision
- `TIME_GRAIN_MINUTE` - For minute-level precision
- `TIME_GRAIN_HOUR` - For hourly data
- `TIME_GRAIN_DAY` - For daily data
- `TIME_GRAIN_WEEK` - For weekly data
- `TIME_GRAIN_MONTH` - For monthly data
- `TIME_GRAIN_QUARTER` - For quarterly data
- `TIME_GRAIN_YEAR` - For yearly data

<note type="info">
If you define multiple time dimensions in your model, the `.query()` method and MCP tools will use the first time dimension that appears in your query's dimensions list.
</note>

**Example time-based queries:**

With time dimensions defined, you can use the `.query()` method with time ranges and grains:

```python
# Query with a specific time range
result = flights.query(
    dimensions=["origin"],
    measures=["flight_count"],
    time_range={"start": "2024-01-01", "end": "2024-12-31"}
)

# Query with time grain aggregation
result = flights.query(
    dimensions=["arr_time"],
    measures=["flight_count"],
    time_grain="TIME_GRAIN_MONTH"
)
```

LLMs can then perform similar queries through MCP:
```
> "What's the time range available in the flights data?"
> "Show me flights from January 2024"
> "Give me monthly flight counts for the last year"
```

### 4. Structure Your Data Logically

Organize related dimensions and measures together, and use joins to connect related models:

```python
# Flights model focuses on flight operations
flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(origin=..., destination=..., date=...)
    .with_measures(flight_count=..., avg_delay=...)
)

# Carriers model focuses on airline information
carriers = (
    to_semantic_table(carriers_tbl, name="carriers")
    .with_dimensions(code=..., name=..., country=...)
    .with_measures(carrier_count=...)
)

# Connect them with joins
flights_with_carriers = flights.join_one(
    carriers,
    lambda f, c: f.carrier == c.code
)
```

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. Check the configuration file path is correct
2. Verify JSON syntax in `claude_desktop_config.json`
3. Ensure BSL is installed with MCP support: `pip install 'boring-semantic-layer[fastmcp]'`
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for error messages

### Import Errors

If you see import errors when the server starts:

```bash
# Ensure all dependencies are installed
pip install 'boring-semantic-layer[fastmcp]'

# Or install specific dependencies
pip install fastmcp ibis-framework
```

### Path Issues

Make sure file paths in your configuration are absolute paths, not relative:

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "python",
      "args": ["/Users/username/projects/my-project/example_mcp.py"]
    }
  }
}
```


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-skill.md`

# Query Agent: BSL Skills for AI Coding Assistants

AI coding assistants can help you build and maintain your semantic model, but they don't know about BSL out of the box.

The easiest way to provide this context is to use the `bsl` CLI, which copies pre-built prompts into your agent's config folder.

## Installation

### Claude Code

```bash
bsl skill install claude-code
```

Or manually copy the prompt from [`skills/claude-code/`](https://github.com/boringdata/boring-semantic-layer/tree/main/docs/md/skills/claude-code/) to `.claude/skills/bsl-query-expert/SKILL.md`

### Claude Desktop

1. Open Claude Desktop and click **Skills -> New Skill**.
2. Run `bsl skill show claude-code` and copy the output into the editor.
3. Name it something memorable like "BSL Query Expert" and save.
4. Add optional tags ("data", "analytics") so you can search for it quickly.

### Cursor

```bash
bsl skill install cursor
```

Or manually copy the prompt from [`skills/cursor/`](https://github.com/boringdata/boring-semantic-layer/tree/main/docs/md/skills/cursor) to `.cursorrules` in your project root

### Codex (OpenAI)

```bash
bsl skill install codex
```

Or manually copy the prompt from [`skills/codex/`](https://github.com/boringdata/boring-semantic-layer/tree/main/docs/md/skills/codex) to your Codex system instructions

## CLI Reference

```bash
# List available skills
bsl skill list

# Preview a skill before installing
bsl skill show claude-code

# Install a skill to your project
bsl skill install claude-code
bsl skill install cursor
bsl skill install codex

# Overwrite existing file
bsl skill install cursor --force
```


## BSL — MCP Integration


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/mcp.md`

# Model Context Protocol (MCP) Integration

BSL includes built-in support for the [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk), allowing you to expose your semantic models to Large Language Models like Claude.

<note type="info">
**Pro tip:** Use [descriptions in dimensions and measures](/building/semantic-tables#adding-descriptions) to make your models more AI-friendly. Descriptions help provide context to LLMs, enabling them to understand what each field represents and when to use them.
</note>

## Installation

To use MCP functionality, install BSL with the `fastmcp` extra:

```bash
pip install 'boring-semantic-layer[fastmcp]'
```

## Setting up an MCP Server

Create an MCP server script that exposes your semantic models:

```python
import ibis
from boring_semantic_layer.semantic_api import to_semantic_table
from boring_semantic_layer.api.mcp import MCPSemanticModel

# Create synthetic flights data
flights_data = ibis.memtable({
    "flight_id": list(range(1, 101)),
    "origin": ["JFK", "LAX", "ORD", "ATL", "DFW"] * 20,
    "dest": ["LAX", "JFK", "DFW", "ORD", "ATL"] * 20,
    "carrier": ["AA", "UA", "DL", "WN", "B6"] * 20,
    "distance": [2475, 2475, 801, 606, 732] * 20,
})

# Define your semantic table with descriptions
flights = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code where the flight departed from"
        },
        destination={
            "expr": lambda t: t.dest,
            "description": "Destination airport code where the flight arrived"
        },
        carrier={
            "expr": lambda t: t.carrier,
            "description": "Airline carrier code (e.g., AA, UA, DL)"
        },
    )
    .with_measures(
        total_flights={
            "expr": lambda t: t.count(),
            "description": "Total number of flights"
        },
        avg_distance={
            "expr": lambda t: t.distance.mean(),
            "description": "Average flight distance in miles"
        },
    )
)

# Create the MCP server
mcp_server = MCPSemanticModel(
    models={"flights": flights},
    name="Flight Data Server"
)

if __name__ == "__main__":
    mcp_server.run(transport="stdio")
```

Save this as `example_mcp.py` in your project directory.

## Configuring Claude Desktop

To use your MCP server with Claude Desktop, add it to your configuration file.

**Configuration file location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Example configuration:**

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/",
        "run",
        "example_mcp.py"
      ]
    }
  }
}
```

Replace `/path/to/your/project/` with the actual path to your project directory.

<note type="info">
This example uses [uv](https://docs.astral.sh/uv/) to run the MCP server. You can also use `python` directly if you have BSL installed in your environment:

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "python",
      "args": ["/path/to/your/project/example_mcp.py"]
    }
  }
}
```
</note>

After updating the configuration:
1. Restart Claude Desktop
2. Look for the MCP server indicator in the Claude Desktop interface
3. You should see "flight_sm" listed as an available server

## Available MCP Tools

Once configured, Claude will have access to these tools for interacting with your semantic models:

### list_models

List all available semantic model names in the MCP server.

**Example usage in Claude:**
> "What models are available?"

**Returns:** Array of model names (e.g., `["flights", "carriers"]`)

### get_model

Get detailed information about a specific model including its dimensions, measures, and descriptions.

**Parameters:**
- `model_name` (str): Name of the model to inspect

**Example usage in Claude:**
> "Show me the details of the flights model"

**Returns:** Model schema including:
- Model name and description
- List of dimensions with their descriptions
- List of measures with their descriptions
- Available joins (if any)

### get_time_range

Get the available time range for time-series data in a model.

**Parameters:**
- `model_name` (str): Name of the model
- `time_dimension` (str): Name of the time dimension

**Example usage in Claude:**
> "What's the time range available in the flights model?"

**Returns:** Dictionary with `min_time` and `max_time` values

### query_model

Execute queries against a semantic model with dimensions, measures, filters, and optional chart specifications.

**Parameters:**
- `model_name` (str): Name of the model to query
- `dimensions` (list[str]): List of dimension names to group by
- `measures` (list[str]): List of measure names to aggregate
- `filters` (list[str], optional): List of filter expressions (e.g., `["origin == 'JFK'"]`)
- `limit` (int, optional): Maximum number of rows to return
- `order_by` (list[str], optional): List of columns to sort by
- `chart_spec` (dict, optional): Vega-Lite chart specification

**Example usage in Claude:**
> "Show me the top 10 origins by flight count"
> "Create a bar chart of average distance by carrier"

**Returns:**
- When `chart_spec` is provided: `{"records": [...], "chart": {...}}`
- When `chart_spec` is not provided: `{"records": [...]}`

### Example Interactions

Here are some example questions you can ask Claude when the MCP server is configured:

**Data Exploration:**
- "What models are available in the flight data server?"
- "Show me all dimensions and measures in the flights model"
- "What is the time range covered by the flights data?"

**Basic Queries:**
- "How many flights departed from JFK?"
- "Show me the top 5 destinations by flight count"
- "What's the average flight distance for each carrier?"

**Filtered Queries:**
- "Show me flights from California airports (starting with 'S')"
- "What carriers have an average distance over 1000 miles?"
- "List the top 10 busiest routes"

**Visualizations:**
- "Create a bar chart showing flights by origin airport"
- "Make a line chart of flights over time"
- "Show me a heatmap of routes between origins and destinations"

## Best Practices

### 1. Add Descriptions to All Fields

Descriptions are crucial for LLMs to understand your data model:

```python
flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code (3-letter IATA code)"
        }
    )
    .with_measures(
        total_flights={
            "expr": lambda t: t.count(),
            "description": "Total number of flights in the dataset"
        }
    )
)
```

### 2. Use Descriptive Model Names

Choose clear, descriptive names for your models:

```python
# Good
mcp_server = MCPSemanticModel(
    models={"flights": flights, "carriers": carriers},
    name="Aviation Analytics Server"
)

# Less clear
mcp_server = MCPSemanticModel(
    models={"f": flights, "c": carriers},
    name="Server"
)
```

### 3. Define Time Dimensions for MCP Time-Series Queries

When exposing models through MCP, you need to explicitly define time dimensions to enable LLMs to query time ranges and perform time-based aggregations. This is specific to MCP—when using BSL's fluent API directly, you can simply use Ibis functions like `.year()` and `.month()`.

To define a time dimension, set `is_time_dimension=True` and specify the `smallest_time_grain`:

```python
from boring_semantic_layer.semantic_api import to_semantic_table

flights = (
    to_semantic_table(flights_data, name="flights")
    .with_dimensions(
        arr_time={
            "expr": lambda t: t.arr_time,
            "description": "Arrival time of the flight",
            "is_time_dimension": True,
            "smallest_time_grain": "TIME_GRAIN_SECOND",
        },
        origin={
            "expr": lambda t: t.origin,
            "description": "Origin airport code"
        },
    )
    .with_measures(
        flight_count={
            "expr": lambda t: t.count(),
            "description": "Total number of flights"
        }
    )
)
```

**Available time grains:**
- `TIME_GRAIN_SECOND` - For second-level precision
- `TIME_GRAIN_MINUTE` - For minute-level precision
- `TIME_GRAIN_HOUR` - For hourly data
- `TIME_GRAIN_DAY` - For daily data
- `TIME_GRAIN_WEEK` - For weekly data
- `TIME_GRAIN_MONTH` - For monthly data
- `TIME_GRAIN_QUARTER` - For quarterly data
- `TIME_GRAIN_YEAR` - For yearly data

<note type="info">
If you define multiple time dimensions in your model, the `.query()` method and MCP tools will use the first time dimension that appears in your query's dimensions list.
</note>

**Example time-based queries:**

With time dimensions defined, you can use the `.query()` method with time ranges and grains:

```python
# Query with a specific time range
result = flights.query(
    dimensions=["origin"],
    measures=["flight_count"],
    time_range={"start": "2024-01-01", "end": "2024-12-31"}
)

# Query with time grain aggregation
result = flights.query(
    dimensions=["arr_time"],
    measures=["flight_count"],
    time_grain="TIME_GRAIN_MONTH"
)
```

LLMs can then perform similar queries through MCP:
```
> "What's the time range available in the flights data?"
> "Show me flights from January 2024"
> "Give me monthly flight counts for the last year"
```

### 4. Structure Your Data Logically

Organize related dimensions and measures together, and use joins to connect related models:

```python
# Flights model focuses on flight operations
flights = (
    to_semantic_table(flights_tbl, name="flights")
    .with_dimensions(origin=..., destination=..., date=...)
    .with_measures(flight_count=..., avg_delay=...)
)

# Carriers model focuses on airline information
carriers = (
    to_semantic_table(carriers_tbl, name="carriers")
    .with_dimensions(code=..., name=..., country=...)
    .with_measures(carrier_count=...)
)

# Connect them with joins
flights_with_carriers = flights.join_one(
    carriers,
    lambda f, c: f.carrier == c.code
)
```

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. Check the configuration file path is correct
2. Verify JSON syntax in `claude_desktop_config.json`
3. Ensure BSL is installed with MCP support: `pip install 'boring-semantic-layer[fastmcp]'`
4. Restart Claude Desktop completely
5. Check Claude Desktop logs for error messages

### Import Errors

If you see import errors when the server starts:

```bash
# Ensure all dependencies are installed
pip install 'boring-semantic-layer[fastmcp]'

# Or install specific dependencies
pip install fastmcp ibis-framework
```

### Path Issues

Make sure file paths in your configuration are absolute paths, not relative:

```json
{
  "mcpServers": {
    "flight_sm": {
      "command": "python",
      "args": ["/Users/username/projects/my-project/example_mcp.py"]
    }
  }
}
```

## Next Steps

- Learn about [YAML Configuration](/building/yaml) for managing multiple models
- Explore [Query Methods](/querying/methods) to understand what queries LLMs can perform
- See [Charting](/querying/charting) for visualization capabilities
- Review the [full API Reference](/reference) for advanced features


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/builder-agent.md`

# Builder Agent

The Builder Agent is focused on authoring and evolving semantic tables: defining dimensions, measures, joins, calculated measures, YAML config, and validation patterns. It uses a different Claude skill than the Query Agent because it needs to reason about modeling APIs rather than issuing queries.

## Claude Code Skill

- File: [`src/boring_semantic_layer/agents/claude-code/bsl-model-building/SKILL.md`](../../src/boring_semantic_layer/agents/claude-code/bsl-model-building/SKILL.md)
- Use it when you want Claude Desktop to help write new semantic tables, add time dimensions, or compose models.
- The skill includes:
  - Python DSL examples showing `SemanticTable(...)`, `.with_dimensions`, `.with_measures`, `.with_calculated_measures`, and `.join()` patterns.
  - YAML equivalents so you can copy the same logic into declarative configs.
  - Gotchas such as "measures must aggregate" and "join keys must be defined dimensions".

**Workflow:** Load the skill in Claude Desktop, paste the schema or YAML snippet you are editing, and ask "Generate a semantic table for flights with avg delay and join to airports". Claude will respond with both Python and YAML patterns that mirror the documentation.

## Codex Skill

Running inside the Codex CLI (the environment this assistant uses) already gives you repo access. Pair that with the Builder skill to automate scaffolding:

1. Open `docs/content/semantic-table.md` or the relevant source file in your editor for context.
2. Ask Codex to "apply the builder skill" when drafting new semantic tables. It will reference `bsl-model-building/SKILL.md` to keep the API usage correct.
3. Use the CLI's `apply_patch` output directly to drop in the generated models or YAML definitions.

This approach keeps all modeling work version-controlled while still benefiting from the same guard rails the Claude skill enforces.

## Cursor (or other AI IDEs)

If you prefer Cursor, VS Code Copilot Chat, or another AI-assisted IDE:

1. Store the builder skill text in a snippet (Cursor: *Settings -> Custom Instructions*).
2. Add quick prompts like "Use the BSL builder skill" so the IDE pastes the instructions before generating code.
3. Point the IDE at your actual data context (DuckDB schema, YAML file) so it can thread the builder guard rails through your request.

Regardless of the host, the Builder Agent should always cite the same modeling patterns. That keeps upstream MCP/Query agents consistent because every semantic table passes through the same validation philosophy.


## BSL Prompt Templates Reference

The BSL query agent uses ~200 prompt template files. Below is a summary catalog.

### LangChain Backend Prompts

| Prompt File | Purpose |
|------------|---------|
| input-query-model.md | LangChain query agent template |
| param-query-model-chart_backend.md | LangChain query agent template |
| param-query-model-chart_format.md | LangChain query agent template |
| param-query-model-chart_spec.md | LangChain query agent template |
| param-query-model-get_chart.md | LangChain query agent template |
| param-query-model-get_records.md | LangChain query agent template |
| param-query-model-limit.md | LangChain query agent template |
| param-query-model-query.md | LangChain query agent template |
| param-query-model-records_displayed_limit.md | LangChain query agent template |
| param-query-model-records_limit.md | LangChain query agent template |
| system-full.md | LangChain query agent template |
| system.md | LangChain query agent template |
| tool-list-models.md | LangChain query agent template |
| tool-query-model.md | LangChain query agent template |

### MCP Backend Prompts

| Prompt File | Purpose |
|------------|---------|
| system.md | MCP query agent template |
| tool-get-model-desc.md | MCP query agent template |
| tool-get-model.md | MCP query agent template |
| tool-get-time-range-desc.md | MCP query agent template |
| tool-get-time-range.md | MCP query agent template |
| tool-list-models-desc.md | MCP query agent template |
| tool-list-models.md | MCP query agent template |
| tool-query-desc.md | MCP query agent template |
| tool-query-param-chart_backend.md | MCP query agent template |
| tool-query-param-chart_format.md | MCP query agent template |
| tool-query-param-chart_spec.md | MCP query agent template |
| tool-query-param-dimensions.md | MCP query agent template |
| tool-query-param-filters.md | MCP query agent template |
| tool-query-param-get_chart.md | MCP query agent template |
| tool-query-param-get_records.md | MCP query agent template |
| tool-query-param-limit.md | MCP query agent template |
| tool-query-param-measures.md | MCP query agent template |
| tool-query-param-order_by.md | MCP query agent template |
| tool-query-param-records_limit.md | MCP query agent template |
| tool-query-param-time_grain.md | MCP query agent template |
| tool-query-param-time_range.md | MCP query agent template |
| tool-query.md | MCP query agent template |

### Chart Prompts

| Prompt File | Purpose |
|------------|---------|
| altair.md | Chart generation template |
| plotext.md | Chart generation template |
| plotly.md | Chart generation template |

### Build Prompts

| Prompt File | Purpose |
|------------|---------|
| system.md | BSL model builder template |


## BSL — AI Skills for Claude Code


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/skills/claude-code/bsl-query-expert/SKILL.md`

---
name: bsl-query-expert
description: Query BSL semantic models with group_by, aggregate, filter, and visualizations. Use for data analysis from existing semantic tables.
---

# BSL Query Expert

Query semantic models using BSL. Be concise.

## Workflow
1. `list_models()` → discover available models
2. `get_model(name)` → get schema (REQUIRED before querying)
3. `get_documentation("query-methods")` → **call before first query** to learn syntax
4. `query_model(query)` → execute, auto-displays results
5. Brief summary (1-2 sentences max)

## Behavior
- Execute queries immediately - don't show code to user
- Never stop after listing models - proceed to query
- Charts/tables auto-display - don't print data inline
- **Reuse context**: Don't re-call tools if info already in context
- **IMPORTANT: If query fails** → call `get_documentation("query-methods")` to learn correct syntax before retrying

## CRITICAL: Field Names
- Use EXACT names from `get_model()` output
- Joined columns: `t.customers.country` (not `t.customer_id.country()`)
- Direct columns: `t.region` (not `t.model.region`)
- **NEVER invent methods** on columns - they don't exist!

## CRITICAL: Never Guess Filter Values
- **WRONG**: `.filter(lambda t: t.region.isin(["US", "EU"]))` without checking actual values first
- Data uses codes/IDs that differ from what you expect (e.g., "California" might be "CA" or "US-CA")
- Always discover values first, then filter with real data

## Multi-Hop Query Pattern
When filtering by names/locations/categories you haven't seen:
```
Step 1 (discover): query_model(query="model.group_by('region').aggregate('count')", records_limit=50, get_chart=false)
Step 2 (filter):   query_model(query="model.filter(lambda t: t.region.isin(['CA','NY'])).group_by('region').aggregate('count')", get_records=false)
```
- Step 1: Get data to LLM (`records_limit=50`), hide chart (`get_chart=false`)
- Step 2: Display to user (`get_records=false`), show chart (default)

## query_model Parameters
- `get_records=true` (default): Return data to LLM, table auto-displays
- `get_records=false`: Display-only, no data returned to LLM
- `records_limit=N`: Max records to LLM (increase for discovery queries)
- `get_chart=true` (default): Show chart; `false` for table-only

## CRITICAL: Exploration vs Final Query
- **Discovery/exploration queries**: Use `get_chart=false` - no chart when exploring data values
- **Final answer query**: Use `get_chart=true` (default) - show chart for user's answer
- Example: Looking up airport codes? → `get_chart=false`. Final flight count? → chart enabled

## Charts
- **Default: Omit chart_spec** - auto-detect handles most cases
- Override only if needed: `chart_spec={"chart_type": "line"}` or `"bar"`
- **CRITICAL**: Charting only works on BSL SemanticQuery results (after group_by + aggregate)
- If you use filter-only queries (returns Ibis Table), set `get_chart=false` - charts will fail on raw tables

## Time Dimensions
- Use `.truncate()` for time columns: `with_dimensions(year=lambda t: t.date.truncate("Y"))`
- Units: `"Y"`, `"Q"`, `"M"`, `"W"`, `"D"`, `"h"`, `"m"`, `"s"`

## CRITICAL: Case Expressions
- Use `ibis.cases()` (PLURAL) - NOT `ibis.case()`
- Syntax: `ibis.cases((condition1, value1), (condition2, value2), else_=default)`
- Example: `ibis.cases((t.value > 100, "high"), (t.value > 50, "medium"), else_="low")`

## Help
`get_documentation(topic)` for:
- **Core**: getting-started, semantic-table, yaml-config, profile, compose, query-methods
- **Advanced**: windowing, bucketing, nested-subtotals, percentage-total, indexing, sessionized, comparison
- **Charts**: charting, charting-altair, charting-plotly, charting-plotext

## Additional Information

**Available documentation:**

- **Getting Started**: Introduction to BSL, installation, and basic usage with semantic tables
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/getting-started.md
- **Semantic Tables**: Building semantic models with dimensions, measures, and expressions
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/semantic-table.md
- **YAML Configuration**: Defining semantic models in YAML files for better organization
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/yaml-config.md
- **Profiles**: Database connection profiles for connecting to data sources
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/profile.md
- **Composing Models**: Joining multiple semantic tables together
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/compose.md
- **Query Methods**: Complete API reference for group_by, aggregate, filter, order_by, limit, mutate
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/query-methods.md
- **Window Functions**: Running totals, moving averages, rankings, lag/lead, and cumulative calculations
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/windowing.md
- **Bucketing with Other**: Create categorical buckets and consolidate long-tail into 'Other' category
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/bucketing.md
- **Nested Subtotals**: Rollup calculations with subtotals at each grouping level
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/nested-subtotals.md
- **Percent of Total**: Calculate percentages using t.all() for market share and distribution analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/percentage-total.md
- **Dimensional Indexing**: Compare values to baselines and calculate indexed metrics
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/indexing.md
- **Charting Overview**: Data visualization basics with automatic chart type detection
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/charting.md
- **Altair Charts**: Interactive web charts with Vega-Lite via Altair backend
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/altair.md
- **Plotly Charts**: Interactive charts with Plotly backend for dashboards
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/plotly.md
- **Terminal Charts**: ASCII charts for terminal/CLI with Plotext backend
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/plotext.md
- **Sessionized Data**: Working with session-based data and user journey analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/sessionized.md
- **Comparison Queries**: Period-over-period comparisons and trend analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/comparison.md
## Query Syntax Reference

Execute BSL queries and visualize results. Returns query results with optional charts.

## Core Pattern
```python
model.group_by(<dimensions>).aggregate(<measures>)  # Both take STRING names only
```
**CRITICAL**: `aggregate()` takes measure **names as strings**, NOT expressions or lambdas!

## Method Order
```
model -> with_dimensions -> filter -> with_measures -> group_by -> aggregate -> order_by -> mutate -> limit
```

## Lambda Column Access
**CRITICAL**: In `with_dimensions` and `with_measures` lambdas, access columns directly - NO model prefix!
```python
# ✅ CORRECT - access columns directly via t
flights.with_dimensions(x=lambda t: ibis.cases((t.carrier == "WN", "Southwest"), else_="Other"))
flights.with_measures(pct=lambda t: t.flight_count / t.all(t.flight_count) * 100)

# ❌ WRONG - model prefix fails in with_dimensions/with_measures
flights.with_dimensions(x=lambda t: t.flights.carrier)  # ERROR: 'Table' has no attribute 'flights'
flights.with_measures(x=lambda t: t.flights.flight_count)  # ERROR!
```
Note: Model prefix (e.g., `t.flights.carrier`) works in `.filter()` but NOT in `with_dimensions`/`with_measures`.

## Filtering
```python
# Simple filter
model.filter(lambda t: t.status == "active").group_by("category").aggregate("count")

# Multiple conditions - use ibis.and_() / ibis.or_()
model.filter(lambda t: ibis.and_(t.amount > 1000, t.year >= 2023))

# IN operator - MUST use .isin() (Python "in" does NOT work!)
model.filter(lambda t: t.region.isin(["US", "EU"]))  # ✅
model.filter(lambda t: t.region in ["US", "EU"])    # ❌ ERROR!

# Post-aggregate filter (SQL HAVING) - filter AFTER aggregate
model.group_by("carrier").aggregate("count").filter(lambda t: t.count > 1000)
```

## Joined Columns
Models with joins expose prefixed columns (e.g., `customers.country`). Use EXACT names from `get_model()`:
```python
# ✅ CORRECT - use prefixed column name
model.filter(lambda t: t.customers.country.isin(["US", "CA"])).group_by("customers.country").aggregate("count")

# ❌ WRONG - columns don't have lookup methods!
model.filter(lambda t: t.customer_id.country())  # ERROR: no 'country' attribute
```
**Key**: Look for prefixed columns in `get_model()` output - don't call methods on ID columns.

## Time Transformations
`group_by()` only accepts strings. Use `.with_dimensions()` first:
```python
model.with_dimensions(year=lambda t: t.created_at.truncate("Y")).group_by("year").aggregate("count")
```
**Truncate units**: `"Y"`, `"Q"`, `"M"`, `"W"`, `"D"`, `"h"`, `"m"`, `"s"`

## Filtering Timestamps - Match Types!
```python
# .year() returns int -> compare with int
model.filter(lambda t: t.created_at.year() >= 2023)

# .truncate() returns timestamp -> compare with ISO string
model.with_dimensions(yr=lambda t: t.created_at.truncate("Y")).filter(lambda t: t.yr >= '2023-01-01')
```

## Percentage of Total
Use `t.all(t.measure)` in `.with_measures()` for grand total:
```python
# Simple percentage by category
sales.with_measures(pct=lambda t: t.revenue / t.all(t.revenue) * 100).group_by("category").aggregate("revenue", "pct")

# Complex: filter + joined column + time dimension + percentage
orders.filter(lambda t: t.customers.country.isin(["US", "CA"])).with_dimensions(
    order_date=lambda t: t.created_at.date()
).with_measures(
    pct=lambda t: t.order_count / t.all(t.order_count) * 100
).group_by("order_date").aggregate("order_count", "pct").order_by("order_date")
```
**More**: `get_documentation(topic="percentage-total")`

## Sorting & Limiting
```python
model.group_by("category").aggregate("revenue").order_by(ibis.desc("revenue")).limit(10)
```
**CRITICAL**: `.limit()` in query limits data **before** calculations. Use `limit` parameter for display-only limiting.

## Window Functions
`.mutate()` for post-aggregation transforms - **MUST** come after `.order_by()`:
```python
model.group_by("week").aggregate("count").order_by("week").mutate(
    rolling_avg=lambda t: t.count.mean().over(ibis.window(rows=(-9, 0), order_by="week"))
)
```
**More**: `get_documentation(topic="windowing")`

## Chart
```python
chart_spec={"chart_type": "bar"}  # or "line", "scatter" - omit for auto-detect
```


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/skills/claude-code/bsl-model-builder/SKILL.md`

---
name: bsl-model-builder
description: Build BSL semantic models with dimensions, measures, joins, and YAML config. Use for creating/modifying data models.
---

# BSL Model Builder

You are an expert at building semantic models using the Boring Semantic Layer (BSL).

## Core Concepts

A **Semantic Table** transforms a raw Ibis table into a reusable data model:
- **Dimensions**: Attributes to group by (categorical data)
- **Measures**: Aggregations and calculations (quantitative data)

## Creating a Semantic Table

```python
from boring_semantic_layer import to_semantic_table

# Start with an Ibis table
flights_st = to_semantic_table(flights_tbl, name="flights")
```

## with_dimensions()

Define groupable attributes using lambda, unbound syntax (`_.`), or `Dimension` class:

```python
from ibis import _
from boring_semantic_layer import Dimension

flights_st = flights_st.with_dimensions(
    # Lambda - explicit
    origin=lambda t: t.origin,

    # Unbound syntax - concise
    destination=_.dest,
    year=_.year,

    # Dimension class - with description (AI-friendly)
    carrier=Dimension(
        expr=lambda t: t.carrier,
        description="Airline carrier code"
    )
)
```

### Time Dimensions

Use `.truncate()` for time-based groupings:

```python
flights_st = flights_st.with_dimensions(
    # Year, Quarter, Month, Week, Day
    arr_year=lambda t: t.arr_time.truncate("Y"),
    arr_month=lambda t: t.arr_time.truncate("M"),
    arr_date=lambda t: t.arr_time.truncate("D"),
)
```

**Truncate units**: `"Y"` (year), `"Q"` (quarter), `"M"` (month), `"W"` (week), `"D"` (day), `"h"`, `"m"`, `"s"`

## with_measures()

Define aggregations using lambda or `Measure` class:

```python
from boring_semantic_layer import Measure

flights_st = flights_st.with_measures(
    # Simple aggregations
    flight_count=lambda t: t.count(),
    total_distance=lambda t: t.distance.sum(),
    avg_delay=lambda t: t.dep_delay.mean(),
    max_delay=lambda t: t.dep_delay.max(),

    # Composed measures (reference other measures)
    avg_distance_per_flight=lambda t: t.total_distance / t.flight_count,

    # Measure class - with description
    avg_distance=Measure(
        expr=lambda t: t.distance.mean(),
        description="Average flight distance in miles"
    )
)
```

### Percent of Total with all()

Use `t.all()` to reference the entire dataset:

```python
flights_st = flights_st.with_measures(
    flight_count=lambda t: t.count(),
    market_share=lambda t: t.flight_count / t.all(t.flight_count) * 100
)
```

## Joins

### join_many() - One-to-Many (LEFT JOIN)

```python
# One carrier has many flights
flights_with_carriers = flights_st.join_many(
    carriers_st,
    lambda f, c: f.carrier == c.code
)
```

### join_one() - One-to-One (INNER JOIN)

```python
# Each flight has exactly one carrier
flights_with_carrier = flights_st.join_one(
    carriers_st,
    lambda f, c: f.carrier == c.code
)
```

### join_cross() - Cartesian Product

```python
all_combinations = flights_st.join_cross(carriers_st)
```

### Custom Joins

```python
flights_st.join(
    carriers_st,
    lambda f, c: f.carrier == c.code,
    how="left"  # "inner", "left", "right", "outer", "cross"
)
```

**After joins**: Fields are prefixed with table names (e.g., `flights.origin`, `carriers.name`)

**Multiple joins to same table**: Use `.view()` to create distinct references:
```python
pickup_locs = to_semantic_table(locs_tbl.view(), "pickup_locs")
dropoff_locs = to_semantic_table(locs_tbl.view(), "dropoff_locs")
```

## YAML Configuration

Define models in YAML for better organization:

```yaml
# flights_model.yaml
profile: my_db  # Optional: use a profile for connections

flights:
  table: flights_tbl
  dimensions:
    origin: _.origin
    destination: _.dest
    carrier: _.carrier
    arr_year: _.arr_time.truncate("Y")
  measures:
    flight_count: _.count()
    total_distance: _.distance.sum()
    avg_distance: _.distance.mean()

carriers:
  table: carriers_tbl
  dimensions:
    code: _.code
    name: _.name
  measures:
    carrier_count: _.count()
```

**YAML uses unbound syntax only** (`_.field`), not lambdas.

### Loading YAML Models

```python
from boring_semantic_layer import from_yaml

# With profile (recommended)
models = from_yaml("flights_model.yaml")

# With explicit tables
models = from_yaml(
    "flights_model.yaml",
    tables={"flights_tbl": flights_tbl, "carriers_tbl": carriers_tbl}
)

flights_sm = models["flights"]
```

## Best Practices

1. **Add descriptions** to dimensions/measures for AI-friendly models
2. **Use meaningful names** that reflect business concepts
3. **Define composed measures** to avoid repetition
4. **Use YAML** for production models (version control, collaboration)
5. **Use profiles** for database connections (see Profile docs)

## Common Patterns

### Derived Dimensions

```python
flights_st = flights_st.with_dimensions(
    # Extract from timestamp
    arr_year=lambda t: t.arr_time.truncate("Y"),
    arr_month=lambda t: t.arr_time.truncate("M"),

    # Categorize numeric values (use ibis.cases - PLURAL, not ibis.case)
    distance_bucket=lambda t: ibis.cases(
        (t.distance < 500, "Short"),
        (t.distance < 1500, "Medium"),
        else_="Long"
    )
)
```

### Ratio Measures

```python
flights_st = flights_st.with_measures(
    total_flights=lambda t: t.count(),
    delayed_flights=lambda t: (t.dep_delay > 0).sum(),
    delay_rate=lambda t: t.delayed_flights / t.total_flights * 100
)
```

## Additional Information

**Available documentation:**

- **Getting Started**: Introduction to BSL, installation, and basic usage with semantic tables
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/getting-started.md
- **Semantic Tables**: Building semantic models with dimensions, measures, and expressions
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/semantic-table.md
- **YAML Configuration**: Defining semantic models in YAML files for better organization
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/yaml-config.md
- **Profiles**: Database connection profiles for connecting to data sources
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/profile.md
- **Composing Models**: Joining multiple semantic tables together
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/compose.md
- **Query Methods**: Complete API reference for group_by, aggregate, filter, order_by, limit, mutate
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/query-methods.md
- **Window Functions**: Running totals, moving averages, rankings, lag/lead, and cumulative calculations
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/windowing.md
- **Bucketing with Other**: Create categorical buckets and consolidate long-tail into 'Other' category
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/bucketing.md
- **Nested Subtotals**: Rollup calculations with subtotals at each grouping level
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/nested-subtotals.md
- **Percent of Total**: Calculate percentages using t.all() for market share and distribution analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/percentage-total.md
- **Dimensional Indexing**: Compare values to baselines and calculate indexed metrics
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/indexing.md
- **Charting Overview**: Data visualization basics with automatic chart type detection
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/charting.md
- **Altair Charts**: Interactive web charts with Vega-Lite via Altair backend
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/altair.md
- **Plotly Charts**: Interactive charts with Plotly backend for dashboards
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/plotly.md
- **Terminal Charts**: ASCII charts for terminal/CLI with Plotext backend
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/prompts/chart/plotext.md
- **Sessionized Data**: Working with session-based data and user journey analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/sessionized.md
- **Comparison Queries**: Period-over-period comparisons and trend analysis
  - URL: https://github.com/boringdata/boring-semantic-layer/blob/main/docs/md/doc/comparison.md

## BSL — Examples


> Source: `docs/data_engineering/semantic_layer/boring-semantic-layer/examples/README.md`

# Boring Semantic Layer - Examples

This directory contains focused examples demonstrating the core features of the Boring Semantic Layer using the new Ibis Relation-based fluent API.

## Quick Start

Run the examples in order to learn the key features:

```bash
# Example 1: Basic semantic tables and queries
python examples/01_basic_flights.py

# Example 2: Market share and percent of total
python examples/02_percent_of_total.py

# Example 3: Window functions (rolling averages, rankings)
python examples/03_window_functions.py

# Example 4: Joins and foreign sums/averages
python examples/04_joins.py

# Example 5: Bucketing with 'Other' (Top N with rollup)
python examples/05_bucketing_with_other.py
```

## Examples Overview

### 01_basic_flights.py - Getting Started

Learn the fundamentals of the Boring Semantic Layer:
- Creating semantic tables with dimensions and measures
- Using the fluent API for queries (`.group_by()` → `.aggregate()`)
- Mixing semantic measures with ad-hoc aggregations
- Post-aggregation calculations with `.mutate()`
- Both lambda and Ibis deferred expression syntax (`_.col`)

**Key Concepts**: dimensions, measures, fluent API, method chaining

### 02_percent_of_total.py - Market Share Analysis

Master the `t.all()` functionality for percentage calculations:
- Computing market share: `measure / t.all(measure)`
- Contribution analysis and relative metrics
- Comparing group-level vs grand total percentages
- Using window functions vs t.all() for different aggregation levels

**Key Concepts**: t.all(), percent of total, market share, contribution analysis

### 03_window_functions.py - Advanced Analytics

Explore powerful window functions for time-series and comparative analysis:
- Rolling/moving averages with configurable windows
- Running totals (cumulative sums)
- Rankings within groups
- Lead/lag for day-over-day changes
- Statistical measures (min, max, stddev) over windows

**Key Concepts**: ibis.window(), rolling averages, rankings, cumulative sums

### 04_joins.py - Foreign Sums and Averages

Understand how joins work correctly with aggregations (Malloy-style "foreign sums"):
- Joining semantic tables with proper relationships
- Automatic prefixing of measures with table names
- Computing aggregations at different levels of the join tree
- Three-way joins (flights → aircraft → models)
- Cross-team composability example

**Key Concepts**: join_one(), foreign sums, join tree aggregations, composability

### 05_bucketing_with_other.py - Bucketing with 'Other' (Top N Analysis)

Master the "bucketing with OTHER" pattern for clean reports and visualizations:
- Show top N items individually, group rest as 'OTHER'
- Use `ibis.rank()` with window functions for rankings
- Use `ibis.cases()` for bucketing logic
- Drop to ibis level with `.to_untagged()` for second aggregation
- Top N per group (e.g., top 3 states per facility type)
- Dynamic thresholds (e.g., states covering 80% of total)
- Pie-chart-ready aggregations with limited slices

**Key Concepts**: window functions, rankings, case expressions, multi-level aggregation, Malloy bucketing pattern

## Additional Resources

### Tests

For more advanced examples and patterns, see the test suite:
- `src/boring_semantic_layer/api/tests/test_real_world_scenarios.py`
- `src/boring_semantic_layer/api/tests/malloy_equivalence/`

## Data Sources

All examples use simple in-memory data created with pandas DataFrames and loaded
into DuckDB. The examples are self-contained and don't require external data files.

The flights data is inspired by real aviation datasets and demonstrates realistic
analytical patterns.

## Common Patterns

### Basic Query Pattern

```python
from boring_semantic_layer.api import to_semantic_table
import ibis
from ibis import _

# Create semantic table
flights = (
    to_semantic_table(raw_table, name="flights")
    .with_dimensions(
        origin=lambda t: t.origin,
        carrier=lambda t: t.carrier,
    )
    .with_measures(
        flight_count=lambda t: t.count(),
        avg_distance=lambda t: t.distance.mean(),
    )
)

# Query it
result = (
    flights
    .group_by("origin")
    .aggregate("flight_count", "avg_distance")
    .order_by(_.flight_count.desc())
    .execute()
)
```

### Percent of Total Pattern

```python
result = (
    flights
    .group_by("carrier")
    .aggregate("flight_count")
    .mutate(
        market_share=lambda t: t.flight_count / t.all(t.flight_count)
    )
    .execute()
)
```

### Join Pattern

```python
flights_with_aircraft = flights.join_one(
    aircraft,
    lambda f, a: f.tail_num == a.tail_num
)

# Measures are prefixed: flights__flight_count, aircraft__aircraft_count
```

### Window Function Pattern

```python
rolling_window = ibis.window(order_by="date", preceding=6, following=0)

result = (
    flights
    .group_by("date")
    .aggregate("daily_flights")
    .mutate(
        rolling_7d_avg=lambda t: t.daily_flights.mean().over(rolling_window)
    )
    .execute()
)
```

## Syntax Notes

### Lambda vs Deferred Syntax

Both syntaxes work throughout the API:

```python
# Lambda syntax
.with_measures(total=lambda t: t.amount.sum())
.mutate(pct=lambda t: t.value / t.all(t.value))

# Deferred syntax (using _)
from ibis import _

.with_measures(total=_.amount.sum())
.mutate(pct=_.value / _.all(_.value))
```

### Dot Notation vs Bracket Notation

Both work everywhere, use whichever you prefer:

```python
# Dot notation (cleaner)
.mutate(pct=lambda t: t.total_sales / t.all(t.total_sales))

# Bracket notation (explicit)
.mutate(pct=lambda t: t["total_sales"] / t.all(t["total_sales"]))
```

**Recommendation**: Use dot notation for cleaner code, unless you have column names with
special characters or spaces.

## Contributing

To add new examples:
1. Follow the naming convention: `NN_descriptive_name.py`
2. Include clear docstrings explaining the example
3. Use print statements with section headers for readability
4. Include "Key Takeaways" at the end
5. Reference the next example in sequence

## Questions?

See the main README or check the test suite for more complex examples.


# Part 2: Cube.js — Headless BI & Semantic Layer


## Cube.js Overview


> Source: `docs/data_engineering/semantic_layer/cube/README.md`

![]()
<p align="center">
  <a href="https://cube.dev?ref=github-readme"><img src="https://raw.githubusercontent.com/cube-js/cube/master/docs/content/cube-logo-with-bg.png" alt="Cube — Semantic Layer for Data Applications" width="300px"></a>
</p>
<br/>

[Website](https://cube.dev?ref=github-readme) • [Getting Started](https://cube.dev/docs/getting-started?ref=github-readme) • [Docs](https://cube.dev/docs?ref=github-readme) • [Examples](https://cube.dev/docs/examples?ref=github-readme) • [Blog](https://cube.dev/blog?ref=github-readme) • [Slack](https://slack.cube.dev?ref=github-readme) • [X](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube/workflows/Build/badge.svg)](https://github.com/cube-js/cube/actions?query=workflow%3ABuild+branch%3Amaster)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js?ref=badge_shield)

__Cube Core is an open-source semantic layer and LookML alternative.__ It can be used by data professionals to access data from modern data stores, organize it into consistent definitions, and deliver it to every application. Cube Core is headless and comes with multiple APIs for embedded analytics and BI: REST, GraphQL and SQL. If you are looking for a fully integrated platform, similar to Looker, check out our commercial product - [Cube](https://cube.dev).

<img
  src="https://ucarecdn.com/8d945f29-e9eb-4e7f-9e9e-29ae7074e195/"
  style="border: none"
  width="100%"
/>

<p align="center">
  <i>Learn more about connecting Cube to <a href="https://cube.dev/docs/config/databases?ref=github-readme" target="_blank">data sources</a> and <a href="https://cube.dev/docs/config/downstream?ref=github-readme" target="_blank">analytics & visualization tools</a>.</i>
</p>

Cube was designed to work with all SQL-enabled data sources, including cloud data warehouses like Snowflake or Google BigQuery, query engines like Presto or Amazon Athena, and application databases like Postgres. Cube has a built-in relational caching engine to provide sub-second latency and high concurrency for API requests.

For more details, see the [introduction](https://cube.dev/docs/cubejs-introduction?ref=github-readme) page in our documentation.

## Why Cube?

As data infrastructure evolved from traditional relational databases to cloud data platforms, OLAP capabilities that once lived in specialized servers like SQL Server Analysis Services and Oracle Essbase were left behind. Today's organizations face several challenges:

1. __Analytics Modeling and Multidimensionality.__ Modern cloud data platforms excel at processing large volumes of data but lack native support for multidimensional analysis and modeling. Cube brings OLAP-style analytics to these platforms, enabling consistent metric definitions and multidimensional analysis.

2. __Performance Optimization.__ While cloud data warehouses have improved query performance through column-oriented storage and distributed processing, they still struggle with complex analytical workloads. Cube provides intelligent caching and pre-aggregation strategies that dramatically improve query response times.

3. __Access Control and Governance.__ Securing and governing access to data across all consuming applications remains critical. Cube offers robust access control to ensure consistent security across your entire data ecosystem.

4. __API Flexibility.__ Legacy OLAP tools were limited in how they exposed data. Cube provides modern REST, GraphQL, and SQL APIs along with support for traditional MDX and DAX interfaces, making it a truly universal semantic layer.

Cube is the missing OLAP engine for the cloud data platform era that provides the necessary infrastructure and features to implement efficient data modeling, access control, and performance optimizations without duplicating analytics modeling, data, or security permissions across different tools.

![](https://raw.githubusercontent.com/cube-js/cube.js/master/docs/content/old-was-vs-cubejs-way.png)

## Getting Started 🚀

### Cube Cloud

[Cube Cloud](https://cube.dev/cloud?ref=github-readme) is the fastest way to get started with Cube. It provides managed infrastructure as well as an instant and free access for development projects and proofs of concept.

<a href="https://cubecloud.dev/auth/signup?ref=github-readme"><img src="https://cubedev-blog-images.s3.us-east-2.amazonaws.com/f1f1eac0-0b44-4c47-936e-33b5c06eedf0.png" alt="Get started now" width="200px"></a>

For a step-by-step guide on Cube Cloud, [see the docs](https://cube.dev/docs/getting-started/cloud/overview?ref=github-readme).

### Docker

Alternatively, you can get started with Cube locally or self-host it with [Docker](https://www.docker.com/).

Once Docker is installed, in a new folder for your project, run the following command:

```bash
docker run -p 4000:4000 \
  -p 15432:15432 \
  -v ${PWD}:/cube/conf \
  -e CUBEJS_DEV_MODE=true \
  cubejs/cube
```

Then, open http://localhost:4000 in your browser to continue setup.

For a step-by-step guide on Docker, [see the docs](https://cube.dev/docs/getting-started-docker?ref=github-readme).

## Resources

- [Documentation](https://cube.dev/docs?ref=github-readme)
- [Getting Started](https://cube.dev/docs/getting-started?ref=github-readme)
- [Examples & Tutorials](https://cube.dev/docs/examples?ref=github-readme)
- [Architecture](https://cube.dev/docs/product/introduction#four-layers-of-semantic-layer)

## Contributing

There are many ways you can contribute to Cube! Here are a few possibilities:

* Star this repo and follow us on [X](https://twitter.com/the_cube_dev).
* Add Cube to your stack on [Stackshare](https://stackshare.io/cube-js).
* Upvote issues with 👍 reaction so we know what's the demand for particular issue to prioritize it within road map.
* Create issues every time you feel something is missing or goes wrong.
* Ask questions on [Stack Overflow with cube.js tag](https://stackoverflow.com/questions/tagged/cube.js) if others can have these questions as well.
* Provide pull requests for all open issues and especially for those with [help wanted](https://github.com/cube-js/cube/issues?q=is%3Aissue+is%3Aopen+label%3A"help+wanted") and [good first issue](https://github.com/cube-js/cube/issues?q=is%3Aissue+is%3Aopen+label%3A"good+first+issue") labels.

All sort of contributions are **welcome and extremely helpful** 🙌 Please refer to [the contribution guide](https://github.com/cube-js/cube/blob/master/CONTRIBUTING.md) for more information.

## License

Cube Client is [MIT licensed](./packages/cubejs-client-core/LICENSE).

Cube Backend is [Apache 2.0 licensed](./packages/cubejs-server/LICENSE).


[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js?ref=badge_large)


## Cube.js — Contributing


> Source: `docs/data_engineering/semantic_layer/cube/CONTRIBUTING.md`

# Contributing to Cube

Thanks for taking the time for contribution to Cube!
We're very welcoming community and while it's very much appreciated if you follow these guidelines it's not a requirement.

## Code of Conduct
This project and everyone participating in it is governed by the [Cube Code of Conduct](./CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code. Please report unacceptable behavior to conduct@cube.dev.

## Contributing Code Changes

Please review the following sections before proposing code changes. 

### License

- Cube Client is [MIT licensed](./packages/cubejs-client-core/LICENSE).
- Cube Backend is [Apache 2.0 licensed](./packages/cubejs-server/LICENSE).

### Developer Certificate of Origin (DCO)

By contributing to Cube Dev, Inc., You accept and agree to the terms and conditions in the [Developer Certificate of Origin](https://github.com/cube-js/cube/blob/master/DCO.md) for Your present and future Contributions submitted to Cube Dev, Inc. Your contribution includes any submissions to the [Cube repository](https://github.com/cube-js) when you click on such buttons as `Propose changes` or `Create pull request`. Except for the licenses granted herein, You reserve all right, title, and interest in and to Your Contributions.

## Step-by-step guide to contributing

1. Find [issues](https://github.com/cube-js/cube/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc) where we need help. Search for issues with either [`good first issue`](https://github.com/cube-js/cube/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc+label%3A%22good+first+issue%22+) and/or [`help wanted`](https://github.com/cube-js/cube/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc+label%3A%22help+wanted%22) labels.
2. Follow the directions in the [Getting Started guide](https://cube.dev/docs/getting-started) to get Cube up and running (incl. the [Developer Playground](https://cube.dev/docs/dev-tools/dev-playground)). 
3. Clone the [Cube repo](https://github.com/cube-js/cube).
4. Submit your Pull Request. 
5. Testing: Please include test(s) for your code contribution. Depending on a change it can be tested by unit, integration or E2E test. See some of the test examples for [drivers](https://github.com/cube-js/cube/pull/1333/commits/56dadccd62ac4eaceafe650d2853406f5d3d9d43) and [backend](https://github.com/cube-js/cube/tree/master/packages/cubejs-backend-shared/test). There're separate packages for [E2E testing](https://github.com/cube-js/cube/tree/master/packages/cubejs-testing/) and [E2E driver testing](https://github.com/cube-js/cube/tree/master/packages/cubejs-testing-drivers/). **Tests are required for most of the contributions.**
6. Documentation: When new features are added or there are changes to existing features that require updates to documentation, we encourage you to add/update any missing documentation in the [`/docs` folder](https://github.com/cube-js/cube/tree/master/docs). To update an existing documentation page, you can simply click on the `Edit this page` button on the top right corner of the documentation page. 
7. Relevant team(s) will be pinged automatically for a review based on information in the `CODEOWNERS` file. 

## Development Workflow

### Prerequisites

Cube works with Node.js 20+ and uses Yarn as a package manager.

### Cube Docker

Cube offers two different types of Docker image:

- Stable (building from published release on npm)
- Dev (building from source files, needed to test unpublished changes)

For more information, take a look at [Docker Development Guide](./packages/cubejs-docker/DEVELOPMENT.md).

#### Stable Docker Release

1. After cloning Cube repository run `yarn install` in `packages/cubejs-docker` to install dependencies.
2. Copy `yarn.lock` file from the project root to the `packages/cubejs-docker` folder and use `docker build -t cubejs/cube:latest -f latest.Dockerfile` in `packages/cubejs-docker` to build stable docker image manually.

#### Development

1. After cloning Cube repository run `yarn install` to install dependencies.
2. Use `docker build -t cubejs/cube:dev -f dev.Dockerfile ../../` in `packages/cubejs-docker` to build stable development image.

### Cube Client

1. After cloning Cube repository run `yarn install` in root directory.
2. Use `yarn link` to add these packages to link registry.
3. Perform required code changes.
4. Use `yarn build` in the repository root to build CommonJS and UMD modules.
5. Use `yarn link @cubejs-client/core` and/or `yarn link @cubejs-client/react` in your project to test changes applied.
6. Use `yarn test` where available to test your changes.
7. Ensure that any CommonJS and UMD modules are included as part of your commit.

To get set up quickly, you can perform 1) and 2) with one line from the `cube` clone root folder:

```
$ cd packages/cubejs-client-core && yarn && yarn link && cd ../.. && cd packages/cubejs-client-react && yarn && yarn link && cd ../..
```

### Cube Server

#### Prerequisites

If you are going to develop a JDBC driver, you need to [install Java with JDK][link-java-guide].

[link-java-guide]:
https://github.com/cube-js/cube/blob/master/packages/cubejs-jdbc-driver/README.md#java-installation

#### Development

Cube.is written in a mixture of JavaScript, TypeScript, and Rust. TypeScript and Rust are preferred for new code.

> Attention: Cube uses TypeScript configured in incremental mode, which uses cache to speed up compilation,  
> but in some cases, you can run into a problem with a not recompiled file. To fix it, we recommend running `$ yarn clean` and `$ yarn tsc`.

1. Clone the Cube repository, `git clone https://github.com/cube-js/cube`. 
2. Run `yarn install` in the root directory.
3. Run `yarn build` in the root directory to build the frontend dependent packages. 
4. Run `yarn build` in `packages/cubejs-playground` to build the frontend.
5. Run `yarn tsc:watch` to start the TypeScript compiler in watch mode.
6. Run `yarn link` in `packages/cubejs-<pkg>` for the drivers and dependent packages you intend to modify. 
7. Run `yarn install` in `packages/cubejs-<pkg>` to install dependencies for drivers and dependent packages.
8. Run `yarn link @cubejs-backend/<pkg>` in `packages/cubejs-server-core` to link drivers and dependent packages.
9. Run `yarn link` in `packages/cubejs-server-core`.
10. Create or choose an existing project for testing. You can generate a new one with 
    [cubejs-cli](https://cube.dev/docs/reference/cli) tool.
11. Run `yarn link @cubejs-backend/server-core` in your project directory. 
12. Run `yarn dev` to start your testing project and verify changes.

Instead of running all of the above commands manually you can use the `dev-env.sh` script:

1. Clone the Cube repository, `git clone https://github.com/cube-js/cube`.
2. Navigate to your working projects directory and run `/path/to/cube/repo//dev-env.sh setup`. The script will
   ask you some questions and run all the required commands. In case you decide to create a new testing project,
   it will be created in the current directory (that is why you probably don't want to run this script within 
   cube repo directory).

### Debugging with WebStorm

1. Follow all the steps from the previous section. Make sure that the `yarn tsc:watch` daemon is running in the background.
2. Open the Cube project in WebStorm.
3. Create a new configuration, using `./node_modules/.bin/cubejs-server` for Node Parameters and the directory of your test project for Working directory.
4. Run/Debug dev Cube servers using the new configuration.

## Contributing Database Drivers

To enhance the adoption of community-contributed drivers, we decided to split the database driver contribution process into multiple stages.

1. Each driver which is planned to be contributed to the main Cube repository should be published first as an npm package. Please see [Publishing Driver npm package](#publishing-driver-npm-package) on how to do that.
2. This NPM package should be contributed to the list of [Third-party community drivers](https://cube.dev/docs/config/databases#third-party-community-drivers).
3. Please make sure each npm package has a README with instructions on how to install it to the official docker image and how to connect it to the database.
4. Posting a backlink to an open-source repository would be a good idea here so people can provide feedback on it by posting issues.
5. Before creating PR for the main repository, please make sure it's tested with the standard Cube E2E testing suite. An example of an E2E testing suite can be found here: https://github.com/cube-js/cube/blob/master/packages/cubejs-testing/test/driver-postgres.test.ts
6. If you're creating PR for the main repo, please be prepared to become a maintainer for this driver and dedicate some time to it. There're no specific time requirements. As a rule of thumb, you should expect to spend time on a weekly basis.
7. Due to limited resources Core team will review and merge driver PRs based on popularity and development activity. Preference is given to drivers that are used by a significant number of users.

### Implementing a Driver

1. Copy existing driver package structure and name it in `@cubejs-backend/<db-name>-driver` format.
`@cubejs-backend/mysql-driver` is a very good candidate for copying this structure.
2. Please do not copy *CHANGELOG.md*.
3. Name driver class and adjust package.json, README.md accordingly.
4. As a rule of thumb please use only pure JS libraries as a dependencies where possible.
It increases driver adoption rate a lot.
5. Typically, you need to implement only `query()` and `testConnection()` methods of driver.
The rest will be done by `BaseDriver` class.
6. If db requires connection pooling prefer use `generic-pool` implementation with settings similar to other db packages.
7. Make sure your driver has `release()` method in case DB expects graceful shutdowns for connections.
8. Please use yarn to add any dependencies and run `$ yarn` within the package before committing to ensure right `yarn.lock` is in place.
9. Add this driver dependency to [cubejs-server-core/core/DriverDependencies.js](https://github.com/cube-js/cube/blob/master/packages/cubejs-server-core/core/DriverDependencies.js#L1).

### Implementing a JDBC Driver

It is recommended to implement native, non-JDBC drivers for databases. Even though implementing
a JDBC driver might seem like a quick solution, its reliance on external libraries makes it
harder to maintain. Also, such drivers often lack support for important features, such as export buckets and various authentication methods.

### Implementing SQL Dialect

1. Find the most similar `BaseQuery` implementation in `@cubejs-backend/schema-compiler/adapter`.
2. Copy it, adjust SQL generation accordingly and put it in driver package. Driver package will obtain `@cubejs-backend/schema-compiler` dependency from that point.
3. Add `static dialectClass()` method to your driver class which returns `BaseQuery` implementation for the database. For example:
```javascript
const { BaseDriver } = require('@cubejs-backend/query-orchestrator');
const FooQuery = require('./FooQuery');

class FooDriver extends BaseDriver {
  // ...
  static dialectClass() {
    return FooQuery;
  }
}
```
If driver class contains `static dialectClass()` method it'll be used to lookup corresponding SQL dialect. Otherwise, it will use the default dialect for the database type.

### Publishing Driver npm Package

Cube looks up `cubejs-{dbType}-driver` package among installed modules to fullfil driver dependency if there's no corresponding default driver for the specified database type.
For example one can publish `cubejs-foo-driver` npm package to fullfil driver dependency for the `foo` database type.

## Other Packages

### Testing Schema Compiler

In order to run tests in `cubejs-schema-compiler` package you need to have running [Docker](https://docs.docker.com/install/) on your machine.
When it's up and running just use `yarn test` in `packages/cubejs-schema-compiler` to execute tests.

### Client Packages

If you want to make changes to the Cube.js client packages and test them locally in your project you can do it the following way:
1. Make the desired changes and run `yarn build` in the root directory (you can also use `yarn watch`)
2. Go to the `~/some-path/cube.js/packages/cubejs-client-core` directory and run `yarn link`. (You'll see the messages _Registered **"@cubejs-client/core"**_)
3. Now you can link it in your project (e.g. _/my-project/dashboard-app_). You can do so running `yarn link "@cubejs-client/core"`

If you want to make changes to the `@cubejs-client/react` package you'll need a few extra steps
1. Go to your project's **node_modules** directory and find the react package (e.g. _/my-project/dashboard-app/node_modules/react_ and run `yarn link`
2. Go to the `~/some-path/cube.js/packages/cubejs-client-react` directory and run `yarn link react`

Now your project will be using the local packages.

**NOTE:** You might need to restart your project after linking the packages.

### Rust Packages

Please use `cargo test` to test packages and `cargo fmt` to format code before commit.

## Style guides

We're passionate about what code can do rather how it's formatted.
But in order to make code and docs maintainable following style guides will be enforced.
Following these guidelines is not a requirement, but you can save some time for maintainers if you apply those to your contribution beforehand.

### Code

1. Run `yarn lint` in package before committing your changes.
If package doesn't have lint script, please add it and run.
There's one root `.eslintrc.js` file for all packages except client ones.
Client packages has it's own `.eslintrc.js` files.
2. Run `yarn test` before committing if package has tests.
3. Please use [conventional commits name](https://www.conventionalcommits.org/) for your PR.
It'll be used to build change logs.
All PRs are merged using the squash strategy. PR title usually would be used as a name for commit. So please make sure it has a sensible name.  
4. For the scope part of commit name please use package name if it's within one package or don't use it if change spans multiple packages. For example `feat(server-core):` or `fix(cubestore):`.
5. Commit messages that are getting merged should contain mostly "Why" those changes are made as opposed to "What" changes are done. "Why" can be a feature, reference to issue or reasons to fix something like a chore.
6. Do not reformat code you aren't really changing unless it's absolutely necessary (e.g. fixing linter). Such changes make it really hard to use git blame feature when we need to find a commit where line change of interest was introduced. Please do not include files that contain only reformatting changes in the commit.


## Cube.js — CubeSQL & Rust Components


> Source: `docs/data_engineering/semantic_layer/cube/rust/cubestore/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) •
[Examples](#examples) • [Blog](https://cube.dev/blog) •
[Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Rust/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ARust+branch%3Amaster)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fcube-js%2Fcube.js?ref=badge_shield)

# Cube Store

Cube.js pre-aggregation storage layer.

## Motivation

Over the past year, we've accumulated feedback around various use-cases with
pre-aggregations and how to store them. We've learned that there are a set of
problems where relational databases as a storage layer has significant
performance and functionality issues.

These problems include:

- Performance issues with high cardinality rollups (1B and more)
- Lack of HyperLogLog support
- Degraded performance for big `UNION ALL` queries
- Poor `JOIN` performance across rolled up tables
- Table/schema name length issues across different database types
- SQL type differences between source and external database

Over time, we realized that if we try to fix these issues with existing database
engines, we'd end up modifying these databases' codebases in one way or another.

We decided to take another approach and write our own materialized OLAP cache
store, designed solely to store and serve rollup tables at scale.

## Approach

To optimize performance as much as possible, we went with a native approach and
are using Rust to develop Cube Store, utilizing a set of technologies like
RocksDB, Apache Parquet, and Arrow that have proven effectiveness in solving
data access problems.

Cube Store is fully open-sourced and released under the Apache 2.0 license.

## Plans

We intend to start distributing Cube Store with Cube.js, and eventually make
Cube Store the default pre-aggregation storage layer for Cube.js. Support for
MySQL and Postgres as external databases will continue, but at a lower priority.

We'll also update all documentation regarding pre-aggregations and include usage
and deployment instructions for Cube Store.

## Supported architectures and platforms

> If your platform/architecture is not supported, you can launch Cube Store
> using Docker.

|          | `linux-gnu` | `linux-musl` | `darwin` | `win32` |
| -------- | :---------: | :----------: | :------: | :-----: |
| `x86`    |     N/A     |     N/A      |   N/A    |   N/A   |
| `x86_64` |     ✅      |      ✅      |    ✅    |   ✅    |
| `arm64`  |     ✅      |              |  ✅[1]   |         |

[1] It can be launched using Rosetta 2 via the `x86_64-apple` binary.

## Usage

### With Cube.js

Starting with `v0.26.48`, Cube.js ships with Cube Store enabled when `CUBEJS_DEV_MODE=true`.
You don't need to set up any `CUBEJS_EXT_DB_*` environment variables or
`externalDriverFactory` inside your `cube.js` configuration file.

For versions prior to `v0.26.48`, you should upgrade your project to the latest
version and install the Cube Store driver:

```bash
yarn add @cubejs-backend/cubestore-driver
```

After starting up, Cube.js will print a message:

`🔥 Cube Store (0.26.64) is assigned to 3030 port.`

### With Docker

Start Cube Store in a Docker container and bind port `3030` to `127.0.0.1`:

```bash
docker run -d -p 3030:3030 cubejs/cubestore:edge
```

Configure Cube.js to use the above connection for an external database via the
`.env` file:

```dotenv
CUBEJS_EXT_DB_TYPE=cubestore
CUBEJS_EXT_DB_HOST=127.0.0.1
```

### With Docker Compose

Create a `docker-compose.yml` file with the following content:

```yml
version: '2.2'
services:
  cubestore:
    image: cubejs/cubestore:edge

  cube:
    image: cubejs/cube:latest
    ports:
      - 4000:4000  # Cube.js API and Developer Playground
      - 3000:3000  # Dashboard app, if created
    env_file: .env
    depends_on:
      - cubestore
    links:
      - cubestore
    volumes:
      - ./schema:/cube/conf/schema
```

Configure Cube.js to use the above connection for an external database via the
`.env` file:

```dotenv
CUBEJS_EXT_DB_TYPE=cubestore
CUBEJS_EXT_DB_HOST=cubestore
```

## Build

```bash
docker build -t cubejs/cubestore:latest .
docker run --rm cubejs/cubestore:latest
```

## Development

Debian prerequisites (incomplete): `apt-get install lld libssl-dev pkg-config cmake`

When changing Datafusion or Arrow:

Check out https://github.com/cube-js/arrow-rs/tree/cube and
https://github.com/cube-js/arrow-datafusion/tree/cube and add the
following to the current directory's `Cargo.toml`.  (But remember to
exclude this from your PR!)

```

[patch.'https://github.com/cube-js/arrow-rs']
parquet = { path = "../../../arrow-rs/parquet" }
arrow = { path = "../../../arrow-rs/arrow" }

[patch.'https://github.com/cube-js/arrow-datafusion']
datafusion = { path = "../../../arrow-datafusion/datafusion" }
```

Of course, you can use absolute paths or adjust the paths to your
chosen checkout location.

It is possible that uncommenting the arrow-datafusion
`.cargo/config.toml` path line works for you too, but it might not, if
you are making changes in arrow-rs.

## License

Cube Store is [Apache 2.0 licensed](./cubestore/LICENSE).


## Cube.js — Key Packages


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js Server

Standalone Cube.js Express server.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js Server is [Apache 2.0 licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-schema-compiler/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js Schema Compiler

Cube.js Schema acts as an ORM for analytics and allows to model everything from simple counts to cohort retention and funnel analysis.
Cube.js Schema Compiler provides an API to generate analytic SQL queries based on Cube.js Schema.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js Schema Compiler is [Apache 2.0 licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js Query Orchestrator

Multi-stage querying engine.
Receives array of pre-aggregation SQL queries and one query that fetches data to execute it in exact order ensuring up-to-date data structure and freshness.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js CLI is [Apache 2.0 licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-dbt-schema-extension/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js dbt Schema Extension

Schema extension to work with [dbt](https://getdbt.com) projects.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js dbt Schema Extension is [Apache 2.0 licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-duckdb-driver/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js DuckDB Database Driver

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js DuckDB driver is [Apache 2.0 licensed](./LICENSE).


## Cube.js — Client SDKs


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-core/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-backend%2Fserver.svg)](https://badge.fury.io/js/%40cubejs-backend%2Fserver)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js Client Core

Cube.js Client core set of methods to access Cube.js API Gateway.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js Client Core is [MIT licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-react/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-client%2Freact.svg)](https://badge.fury.io/js/%40cubejs-client%2Freact)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js React

Cube.js React is a set of helper React components to simplify Cube.js query rendering.

[Learn more](https://github.com/cube-js/cube.js#getting-started)

### License

Cube.js React is [MIT licensed](./LICENSE).


> Source: `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-vue3/README.md`

<p align="center"><a href="https://cube.dev"><img src="https://i.imgur.com/zYHXm4o.png" alt="Cube.js" width="300px"></a></p>

[Website](https://cube.dev) • [Docs](https://cube.dev/docs) • [Blog](https://cube.dev/blog) • [Slack](https://slack.cube.dev) • [Twitter](https://twitter.com/the_cube_dev)

[![npm version](https://badge.fury.io/js/%40cubejs-client%2Fvue.svg)](https://badge.fury.io/js/%40cubejs-client%2Fvue)
[![GitHub Actions](https://github.com/cube-js/cube.js/workflows/Build/badge.svg)](https://github.com/cube-js/cube.js/actions?query=workflow%3ABuild+branch%3Amaster)

# Cube.js Vue

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn run serve
```

### Compiles and minifies for production
```
yarn run build
```

### Run your tests
```
yarn run test
```

### Lints and fixes files
```
yarn run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

### License

Cube.js Vue is [MIT licensed](./LICENSE).


# Part 3: Cube UI Kit


## Cube UI Kit


> Source: `docs/data_engineering/semantic_layer/cube-ui-kit/README.md`

# UI Kit for Cube Dev Projects

Based on React Aria and `tasty` styling library.

## Available Scripts

### pnpm start

Runs the test page in the development mode.
Open http://localhost:8080 to view it in the browser.

The page will reload if you make edits.
You will also see any lint errors in the console.

### pnpm storybook

Run storybook with all the components of UI Kit.

Deployed version of the Storybook from the `main` branch is here: https://cube-uikit-storybook.netlify.app/ 

### pnpm build

Builds a static copy of UIKit to the `dist/` folder.
Your app is ready to be deployed!

### pnpm test

Not yet implemented

## License

This project is licensed under the MIT License - see the LICENSE file for details.


# Part 4: Rill — Dashboard Semantic Layer


## Rill Examples


> Source: `docs/data_engineering/semantic_layer/rill-examples/README.md`

# Rill Examples

This repository contains a collection of examples for the Rill application. Make sure you have installed Rill before you get started.

# Install Rill 
```
curl https://rill.sh | sh
```

# Start Rill

To run an example:

```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-openrtb-prog-ads
rill start
```

Rill will build your project from data sources to dashboard and then launch in a new browser window.


> Source: `docs/data_engineering/semantic_layer/rill-examples/rill-sec-formd/README.md`

# SEC Form D Offerings

This is a demo project designed to illustrate how Rill can be used to understand US securities reports using publicly available data. This framework allows organizations to bid on advertising inventory in real time.The SEC provides data from Notices of Exempt Offerings of Securities filed with the Commission by issuers relying on Section 4(a)(5) of Securities Act. 

Start `rill start` fromt this directory to jump into this example.

Rill will build your project from data sources to dashboard and then launch in a new browser window.


> Source: `docs/data_engineering/semantic_layer/rill-examples/rill-github-analytics/README.md`

# GitHub Analytics with Rill

Analyze commit activity for any GitHub repository with interactive dashboards. This project provides automation scripts to extract Git history and generate Rill analytics in just a few commands.

**[See live demo →](https://ui.rilldata.com/demo/rill-github-analytics)** | **[Read the full guide →](https://docs.rilldata.com/guides/github-analytics)**

## Overview

This project uses:

- **[PyDriller](https://pydriller.readthedocs.io/)** to extract commit data from Git repositories
- **Automation scripts** (`download_commits.py`, `generate_project.py`) to scrape Git history and generate Rill project files
- **Cloud storage** (GCS) or local files for data
- **Rill** for fast, interactive analytics dashboards

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-github-analytics
poetry install

# 2. Generate Rill files
python generate_project.py your-org/your-repo --gcs --bucket gs://your-bucket/github-analytics

# 3. Download and upload data
python download_commits.py your-org/your-repo --gcs --bucket gs://your-bucket/github-analytics

# 4. Deploy
rill deploy
```

## Automation Scripts

This project includes two scripts to streamline setup:

### `generate_project.py`

Generates all Rill files (sources, models, metrics, dashboards) for a repository:

```bash
python generate_project.py owner/repo --gcs --bucket gs://bucket/path
python generate_project.py owner/repo --local  # For local testing
```

### `download_commits.py`

Extracts commit history and saves to cloud storage:

```bash
python download_commits.py owner/repo --gcs --bucket gs://bucket/path
python download_commits.py owner/repo --local  # For local testing
```

Both scripts require explicit storage flags (`--gcs` or `--local`).

## Project Structure

Generated files for each repository:

- `sources/{repo}_commits_source.yaml` – Data source for commits
- `sources/{repo}_modified_files.yaml` – Data source for file changes
- `models/{repo}_commits_model.sql` – SQL transformations
- `metrics/{repo}_commits_metrics.yaml` – Metrics definitions
- `dashboards/{repo}_commits_explore.yaml` – Explore dashboard

## Authentication

**For private repositories:** Set `GITHUB_TOKEN` environment variable with a [fine-grained personal access token](https://github.com/settings/tokens?type=beta).

**For GCS:** Set `GOOGLE_APPLICATION_CREDENTIALS` to your service account key path. See [GCS credentials guide](https://docs.rilldata.com/deploy/credentials/gcs).

## Learn More

- **[Full Tutorial](https://docs.rilldata.com/guides/github-analytics)** – Step-by-step guide with prerequisites and examples
- **[Rill Documentation](https://docs.rilldata.com)** – Learn more about Rill
- **[Discord Community](https://discord.gg/DJ5qcsxE2m)** – Get help and share your dashboards


> Source: `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads/README.md`

# OpenRTB Programmatic Advertising

This is a demo project designed to illustrate using Rill to analyze programmatic bid logs using the canonical open RTB framework. 

If you have added the full Rill Example project, run `rill start` from this directory to get started.

To run this example specifically:

```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-openrtb-prog-ads
rill start
```

Rill will build your project from data sources to dashboard and then launch in a new browser window.

## Overview
This dataset contains a week of sampled programmatic bid stream data in two data sources - Auctions and Bids. 

Advertisers, DSPs, SSPs, and Publishers will all recognize the familiar metrics (auctions, bids, wins, bid price, bid floor) and dimensions (domain, device details, app/site, etc). Rill’s was born out of a long history with programmatic data via Metamarkets and is well-suited for this type of analysis. More details on OpenRTB via the IAB: https://iabtechlab.com/standards/openrtb/.

## Data Model
In these datasets, you’ll see:

Auction Data:
  - Illustrative Bid Requests sent to advertisers for programmatic bidding 

Bid Data: 
  - Illustrative Bid Responses to those requests including bid prices, winning bids, and advertiser information

## Dashboard Details

For Buyers:
  - Manage all campaigns across multiple supply sources
  - View inventory and audience availability to avoid missing key opportunities and to optimize spend

For Sellers:
  - See both direct and indirect channels across your digital assets
  - Quickly slice and dice inventory to find trends and discover revenue opportunities

For Marketplaces/Technology Providers:
  - Troubleshoot campaigns and quickly identify ad server issues
  - Instantly view top-line revenue, volume, eCPM, and other key metrics without pulling complex reports

## Extra Dashboard

An additional dashboard is created with row policies enabled for specific emails. This is used in our embed examples found, [here](https://rill-embedding-example.netlify.app/).

> Source: `docs/data_engineering/semantic_layer/rill-examples/rill-embed/README.md`

# Rill Embeds

This is a demo project clones from our rill-openrtb project to present our dashboard embedding capabilities. 

```
git clone https://github.com/rilldata/rill-examples.git
cd rill-examples/rill-embeds
rill start
```

Rill will build your project from data sources to dashboard and then launch in a new browser window.



## KCG Summary


> Source: `docs/data_engineering/semantic_layer/KCG_SUMMARY.md`

# Semantic Layer — KCG Summary

## What It Is
This directory aggregates three major semantic layer projects: **Boring Semantic Layer** (BSL) — a lightweight Ibis-based semantic layer with MCP and LangChain integration for LLM-to-SQL querying; **Cube.js** (Cube.dev) — a full-featured semantic layer framework with 40+ database drivers, REST/GraphQL APIs, and a Rust-based SQL compiler; and **Rill** — example dashboards demonstrating Rill Developer patterns for ClickHouse, openRTB, and embedding use cases.

## Why This Matters for Kings' College Galway
BSL's Ibis-based approach aligns directly with the oideachais platform's Ibis analytics layer, providing MCP-friendly query patterns for connecting LLMs (like OpenCode agents) to structured education data. Cube.js's multi-driver architecture and semantic table patterns inform how to expose curriculum datasets across DuckDB, MotherDuck, and PostgreSQL. The BSL query agent (LangChain + MCP + Claude Code skills) provides a working reference for building AI-assisted educational data exploration tools.

## Key Patterns Preserved
200+ .md files remain, including:
- `boring-semantic-layer/README.md` — BSL overview and quick start
- `boring-semantic-layer/docs/md/doc/*.md` (22 files) — Full BSL documentation: query agents, semantic tables, MCP integration, charting, bucketing, sessionized data
- `boring-semantic-layer/docs/md/prompts/query/mcp/*.md` (17 files) — MCP tool parameter docs and system prompts
- `boring-semantic-layer/docs/md/prompts/query/langchain/*.md` (12 files) — LangChain agent prompt engineering patterns
- `boring-semantic-layer/docs/md/skills/claude-code/` — SKILL.md files for BSL model builder and query expert
- `cube/README.md`, `cube/CLAUDE.md`, `cube/CONTRIBUTING.md` — Cube.js architecture and agent instructions
- `cube/packages/*/` (60+ README/CHANGELOG.md) — Per-driver docs for DuckDB, Postgres, BigQuery, Snowflake, ClickHouse, Druid, etc.
- `cube/rust/cubesql/*.md` — Rust SQL compiler and CubeStore internals
- `cube-ui-kit/README.md`, `CONTRIBUTING.md`, `CHANGELOG.md` — React UI kit for semantic layers
- `rill-examples/*/README.md` (14 files) — Rill dashboard examples

## Source Files
Full source removed (2026-06-06). Available at:
- BSL: https://github.com/boringdata/boring-semantic-layer
- Cube.js: https://github.com/cube-js/cube
- Cube UI Kit: https://github.com/cube-js/cube-ui-kit

## What Was Removed
TypeScript/JavaScript source, Rust source, Python packages, Docker files, JSON/YAML configs, Cargo/Rust build files, CSS/HTML, test fixtures, images, nix/CI configs


## Original Sources

### boring-semantic-layer/ docs (included)
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/bucketing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/builder-agent.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/charting.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/comparison.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/compose.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/example.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/getting-started.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/indexing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/mcp.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/nested-subtotals.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/percentage-total.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/profile.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-chat.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-llm-tool.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-mcp.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-skill.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-methods.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/reference.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/semantic-table.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/sessionized.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/windowing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/yaml-config.md`

### boring-semantic-layer/ prompts (summarized — not inlined)
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/build/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/altair.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/plotext.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/plotly.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/input-query-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_backend.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_format.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_spec.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-get_chart.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-get_records.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-query.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-records_displayed_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-records_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/system-full.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/tool-list-models.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/tool-query-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-model-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-time-range-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-time-range.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-list-models-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-list-models.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_backend.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_format.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_spec.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-dimensions.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-filters.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-get_chart.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-get_records.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-measures.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-order_by.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-records_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-time_grain.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-time_range.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query.md`

### cube/ (included)
- `docs/data_engineering/semantic_layer/cube/CONTRIBUTING.md`
- `docs/data_engineering/semantic_layer/cube/docs/README.md`
- `docs/data_engineering/semantic_layer/cube/examples/README.md`
- `docs/data_engineering/semantic_layer/cube/examples/recipes/joining-multiple-databases-data/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-api-gateway/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-athena-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-cloud/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-maven/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/python/cube/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/python/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-shared/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-base-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-bigquery-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cli/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-clickhouse-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-core/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-dx/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ngx/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-react/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-vue3/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ws-transport/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-crate-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cubestore-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-databricks-jdbc-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dbt-schema-extension/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-docker/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dremio-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-druid-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-duckdb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-elasticsearch-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-firebolt-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-hive-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-jdbc-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-ksql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-materialize-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mongobi-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mssql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-aurora-serverless-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-oracle-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-pinot-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/charts-gen/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/apps/react-typescript-antd-table/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/apps/react-typescript-chartjs-area+bar+doughnut+line+pie/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-postgres-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-prestodb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-questdb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-redshift-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-schema-compiler/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server-core/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/command/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-snowflake-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-sqlite-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-templates/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing-shared/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-trino-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-vertica-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/cubeclient/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/cubesql/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/pg-srv/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cross/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubedatasketches/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubehll/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubestore/testing-fixtures/cachestore-migration/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubezetasketch/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/README.md`

### cube-ui-kit/ (included)
- `docs/data_engineering/semantic_layer/cube-ui-kit/.changeset/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/src/components/fields/README.md`

### rill-examples/ (included)
- `docs/data_engineering/semantic_layer/rill-examples/clickhouse-s3-postgres/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/connector-clickhouse/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/my-rill-tutorial/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-app-engagement/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-cost-monitoring/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-embed/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-github-analytics/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-kaggle-elec-consumption/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads-canvas/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads-clickhouse/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-partner-filtered-dashboards/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-row-access-policies/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-sec-formd/README.md`

### Full file list (249 files)

- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/bucketing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/builder-agent.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/charting.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/comparison.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/compose.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/example.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/getting-started.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/indexing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/mcp.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/nested-subtotals.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/percentage-total.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/profile.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-chat.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-llm-tool.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-mcp.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent-skill.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-agent.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/query-methods.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/reference.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/semantic-table.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/sessionized.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/windowing.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/doc/yaml-config.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/build/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/altair.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/plotext.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/chart/plotly.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/input-query-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_backend.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_format.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-chart_spec.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-get_chart.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-get_records.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-query.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-records_displayed_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/param-query-model-records_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/system-full.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/tool-list-models.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/langchain/tool-query-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/system.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-model-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-model.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-time-range-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-get-time-range.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-list-models-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-list-models.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-desc.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_backend.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_format.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-chart_spec.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-dimensions.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-filters.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-get_chart.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-get_records.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-measures.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-order_by.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-records_limit.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-time_grain.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query-param-time_range.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/prompts/query/mcp/tool-query.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/skills/claude-code/bsl-model-builder/SKILL.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/docs/md/skills/claude-code/bsl-query-expert/SKILL.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/examples/README.md`
- `docs/data_engineering/semantic_layer/boring-semantic-layer/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/.changeset/fresh-pumas-knock.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/.changeset/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/.github/PUBLISHING.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/.github/PULL_REQUEST_TEMPLATE.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/.junie/guidelines.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/CONTRIBUTING.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/src/components/fields/README.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/src/components/form/Claude.md`
- `docs/data_engineering/semantic_layer/cube-ui-kit/src/tasty/parser/parser.md`
- `docs/data_engineering/semantic_layer/cube/.github/ISSUE_TEMPLATE/bug_report.md`
- `docs/data_engineering/semantic_layer/cube/.github/ISSUE_TEMPLATE/feature_request.md`
- `docs/data_engineering/semantic_layer/cube/.github/ISSUE_TEMPLATE/question.md`
- `docs/data_engineering/semantic_layer/cube/.github/ISSUE_TEMPLATE/sql_api_query_issue.md`
- `docs/data_engineering/semantic_layer/cube/.github/pull_request_template.md`
- `docs/data_engineering/semantic_layer/cube/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/CODE_OF_CONDUCT.md`
- `docs/data_engineering/semantic_layer/cube/CONTRIBUTING.md`
- `docs/data_engineering/semantic_layer/cube/DCO.md`
- `docs/data_engineering/semantic_layer/cube/DEPRECATION.md`
- `docs/data_engineering/semantic_layer/cube/docs/.claude/commands/move-page.md`
- `docs/data_engineering/semantic_layer/cube/docs/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/docs/README.md`
- `docs/data_engineering/semantic_layer/cube/examples/README.md`
- `docs/data_engineering/semantic_layer/cube/examples/recipes/joining-multiple-databases-data/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-api-gateway/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-api-gateway/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-athena-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-athena-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-cloud/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-cloud/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-maven/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-maven/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/python/cube/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/python/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-native/TECH.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-shared/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-shared/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-backend-shared/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-base-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-base-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-bigquery-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-bigquery-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cli/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cli/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-clickhouse-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-clickhouse-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-core/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-core/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-dx/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-dx/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ngx/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ngx/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-react/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-react/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-vue3/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-vue3/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ws-transport/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-client-ws-transport/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-crate-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-crate-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cubestore-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-cubestore-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-databricks-jdbc-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-databricks-jdbc-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dbt-schema-extension/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dbt-schema-extension/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-docker/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-docker/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-docker/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dremio-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-dremio-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-druid-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-druid-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-duckdb-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-duckdb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-elasticsearch-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-elasticsearch-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-firebolt-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-firebolt-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-hive-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-hive-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-jdbc-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-jdbc-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-ksql-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-ksql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-linter/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-materialize-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-materialize-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mongobi-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mongobi-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mssql-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mssql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-aurora-serverless-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-aurora-serverless-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-mysql-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-oracle-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-oracle-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-pinot-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-pinot-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/charts-gen/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/apps/react-typescript-antd-table/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/apps/react-typescript-chartjs-area+bar+doughnut+line+pie/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-playground/vizard/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-postgres-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-postgres-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-prestodb-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-prestodb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-query-orchestrator/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-questdb-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-questdb-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-redshift-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-redshift-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-schema-compiler/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-schema-compiler/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server-core/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server-core/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/command/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-server/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-snowflake-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-snowflake-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-sqlite-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-sqlite-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-templates/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-templates/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing-drivers/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing-shared/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing-shared/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-testing/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-trino-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-trino-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-vertica-driver/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/packages/cubejs-vertica-driver/README.md`
- `docs/data_engineering/semantic_layer/cube/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubeorchestrator/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubeshared/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/cubeclient/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/cubeclient/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/cubesql/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/DEVELOPMENT.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubesql/pg-srv/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/CHANGELOG.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/CLAUDE.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cross/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubedatasketches/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubehll/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubestore/testing-fixtures/cachestore-migration/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/cubezetasketch/README.md`
- `docs/data_engineering/semantic_layer/cube/rust/cubestore/README.md`
- `docs/data_engineering/semantic_layer/cube/SECURITY.md`
- `docs/data_engineering/semantic_layer/KCG_SUMMARY.md`
- `docs/data_engineering/semantic_layer/rill-examples/clickhouse-s3-postgres/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/connector-clickhouse/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/my-rill-tutorial/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-app-engagement/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-cost-monitoring/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-embed/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-github-analytics/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-kaggle-elec-consumption/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads-canvas/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads-clickhouse/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-openrtb-prog-ads/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-partner-filtered-dashboards/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-row-access-policies/README.md`
- `docs/data_engineering/semantic_layer/rill-examples/rill-sec-formd/README.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
