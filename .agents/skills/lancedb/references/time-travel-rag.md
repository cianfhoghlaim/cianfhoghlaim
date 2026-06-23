# Time-Travel RAG in LanceDB

LanceDB supports **time-travel**: every `add()`, `update()`, `delete()`,
and `restore()` operation creates a new immutable version. You can
check out any historical version for read-only queries, or restore a
previous version (which creates a new version with the old data).

## Key APIs

```python
# Current version
current = table.version          # e.g. 7

# Checkout a historical version (read-only)
historical = table.checkout(4)   # version 4
results = historical.search(query_vec).limit(10).to_pandas()

# List all versions
versions = table.list_versions()  # list[Version]

# Restore a previous version (creates a new version with old data)
table.restore(4)  # now table.version == 8, with the data from version 4

# Compare two versions
diff = table.diff_versions(v1=4, v2=7)  # added, removed, updated rows
```

## Use cases

1. **A/B test embedding models** — index the same data twice (once
   with model A, once with model B), then search both tables and
   compare scores
2. **Model rollback** — if a new model under-performs, `restore()` the
   previous version (no need to re-embed)
3. **Knowledge-base audits** — answer "what did the index look like
   on 2026-04-01?" via `checkout(<version-on-that-date>)`
4. **Reproducible experiments** — every search result can be linked to
   the exact version that produced it

## Canonical example

```python
# Index the corpus with model A
table_a = db.create_table("books_v1", schema=BookSchema, mode="overwrite")
table_a.add([embed_with_model_a(text) for text in texts])

# Re-index with model B (creates a new version on the same table)
table_b = db.create_table("books_v2", schema=BookSchema, mode="overwrite")
table_b.add([embed_with_model_b(text) for text in texts])

# A/B test: query both, compare
query = embed("handwritten text recognition")
results_a = table_a.search(query).limit(10).to_pandas()
results_b = table_b.search(query).limit(10).to_pandas()
```

## RAG application pattern

```python
class VersionedRAG:
    def __init__(self, db, table_name):
        self.table = db.open_table(table_name)

    def search(self, query_vec, version=None, top_k=10):
        if version is None:
            tbl = self.table
        else:
            tbl = self.table.checkout(version)
        return tbl.search(query_vec).limit(top_k).to_pandas()

    def rollback(self, version):
        """Roll back the index to a previous version."""
        self.table.restore(version)

    def history(self):
        """Return a list of (version, timestamp) tuples."""
        return [(v.version, v.timestamp) for v in self.table.list_versions()]
```

## Performance notes

- `checkout()` is O(1) — the historical data is already on disk
- `restore()` is O(rows-in-old-version) — the data is re-materialised
- For very large indexes (> 100M rows), consider creating a separate
  Lance table per version rather than relying on `restore()`
