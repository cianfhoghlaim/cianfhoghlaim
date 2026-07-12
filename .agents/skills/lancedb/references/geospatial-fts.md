# Geospatial + FTS Pattern

LanceDB supports **compound queries** that combine full-text search
(FTS), vector similarity, and geospatial filters in a single
`table.search(...)` call. The canonical example is the
`Geospatial-Recommendation-System` (in the upstream
lancedb/vectordb-recipes repo, deleted with `docs/lance/`).

## Schema

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("name", pa.string()),
    pa.field("description", pa.string()),
    pa.field("lat", pa.float32()),
    pa.field("lon", pa.float32()),
    pa.field("embedding", pa.list_(pa.float32(), 1024)),
])

table = db.create_table("places", schema=schema)
```

## Insert

```python
table.add([{
    "id": 1,
    "name": "Tigh Hughes",
    "description": "Traditional Irish pub with live music",
    "lat": 53.2707,
    "lon": -9.0568,
    "embedding": embed("Traditional Irish pub with live music"),
}, ...])
```

## Compound query (vector + FTS + geo)

```python
results = (table.search("best fish and chips", query_type="hybrid")
          .vector(embed("best fish and chips"))
          .where("distance(lat, lon, 53.2707, -9.0568) < 5")  # 5 km
          .prefilter(False)  # post-filter (geo is non-selective)
          .limit(10)
          .to_pandas())
```

**Key gotcha — prefilter vs postfilter:**

- If the geo filter is **selective** (e.g. < 1% of rows match), use
  `.prefilter(True)` (the default). The filter is applied first,
  then the vector search runs only on the matching rows.
- If the geo filter is **non-selective** (e.g. > 50% of rows match,
  like a wide radius), use `.prefilter(False)`. The vector search
  runs on the full table, then the geo filter is applied.

## Indexing for geo

For datasets with > 1M rows, create a **scalar index** on `lat` and
`lon` to speed up the geo filter:

```python
table.create_scalar_index("lat")
table.create_scalar_index("lon")
```

## KCG example

The `cocoindex/geospatial_indexing.py` CocoIndex v1
App embeds + indexes the Celtic place-name corpora (Gaeltacht
regions, heritage sites, school locations) with geospatial
metadata. The Dagster asset group `orchestration/defs/geospatial_assets.py`
schedules a daily materialisation that updates the geo index.

## Reference

- The `Geospatial-Recommendation-System` example in the upstream
  lancedb/vectordb-recipes repo (deleted with `docs/lance/examples/`)
  is the canonical pattern.
- The LanceDB `distance()` operator docs: <https://lancedb.github.io/lancedb/sql/>
