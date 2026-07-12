# Lance vs Iceberg: When to Use Which

Lance and Iceberg are both **table formats** for analytical data on
object storage. They overlap in some areas (columnar Parquet/Arrow
files, ACID transactions, time-travel) but differ in key dimensions.

## Quick comparison

| Dimension | Lance | Iceberg |
|:--|:--|:--|
| **Primary use case** | Vector + full-text + multimodal search | General analytical tables |
| **File format** | Lance (custom, extends Apache Arrow) | Parquet |
| **Table format** | Lance (fragments + manifest) | Iceberg (metadata + manifest list + manifest files) |
| **Vector search** | First-class (HNSW, IVF_PQ) | Not native (use Lance as a sidecar) |
| **FTS / hybrid search** | First-class (FTS index + RRF) | Not native |
| **Multimodal (BLOBs)** | First-class (fat-table pattern) | Not the focus |
| **ACID transactions** | MVCC + version snapshots | Snapshot isolation |
| **Time-travel** | `table.checkout(version)` | `AS OF TIMESTAMP` / `AS OF VERSION` |
| **Schema evolution** | Add columns, rename | Add/drop/rename/reorder columns |
| **Partition evolution** | Limited | First-class (partition spec can change) |
| **Catalog** | Lance Namespace (Lance-specific) | REST (Lakekeeper, Polaris, Nessie, Glue, Hive) |
| **Engine support** | Python, TS, Rust, C++ | Spark, Trino, Flink, DuckDB, PyIceberg, Dremio, Athena |
| **Index types** | HNSW, IVF_PQ, scalar BTREE | Zone maps, bloom filters, sorted files |
| **Performance (vector search)** | Fast (HNSW, sub-millisecond) | Not applicable |
| **Performance (OLAP scans)** | Fast (Arrow + DataFusion) | Fast (Parquet + native readers) |
| **Open source** | Yes (Apache 2.0) | Yes (Apache 2.0) |

## When to use Lance

- You're building a **vector search / RAG / semantic search** application
- You need **full-text search** or **hybrid search**
- You have **multimodal data** (text + image + audio in one table)
- You need **HNSW or IVF_PQ** indexing
- You're optimising for **sub-millisecond vector search latency**
- Your downstream consumer is Python/TS/Rust (Lance-native SDKs)

## When to use Iceberg

- You're building a **general OLAP data lake** (Spark, Trino, Flink, DuckDB)
- You need **multi-engine access** (Spark reads, Trino serves, DuckDB queries)
- You need **partition evolution** (change the partition spec without rewriting data)
- You're integrating with **dbt, Apache Hudi, Delta Lake**-style tooling
- Your downstream consumer is BI / SQL / data-warehouse tooling

## When to use BOTH (the companion-table pattern)

If you need:
- **Lance for vector + FTS** (the write/search hot path)
- **Iceberg for governance** (ACID, time-travel, multi-engine access)

Then use the **companion-table pattern**: `lance.namespace.connect("iceberg", ...)` to
register the Lance table as an Iceberg table. Both engines read the
same underlying data; the Iceberg side provides the governance layer
to PyIceberg / DuckDB / Spark consumers.

See [`references/lance-namespace-and-iceberg.md`](references/lance-namespace-and-iceberg.md).

## KCG usage

- **Lance** is the primary sink for the leabharlann + curriculum
  semantic-search indexes (`cocoindex/leabharlann_embedding.py`)
- **Iceberg** is the catalog layer for the DuckLake sink
  (`storage/ducklake_client.py` — DuckLake uses Iceberg
  metadata internally)
- The two are **complementary**, not competing. The KCG pattern is
  **Lance for the vector search hot path** + **DuckLake (which is
  Iceberg-compatible) for the analytical tables**.

## Reference

- The 100+ line `lance-vs-iceberg` comparison in
  `docs/lance/lancedb-reference.md:2351-2458` (deleted with the docs)
  is the source material for this reference.
- The Iceberg spec: <https://iceberg.apache.org/spec/>
- The Lance spec: <https://lancedb.github.io/lance/>
