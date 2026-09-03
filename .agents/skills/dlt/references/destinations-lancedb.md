# LanceDB Destination (lancedb_adapter)

The `lancedb_adapter(source, embed=[...])` pattern is the canonical
way to vectorise a dlt source and write it to a LanceDB table. It
automatically embeds the specified columns using a configured model
and writes the vectors + metadata to a Lance table.

## Basic pattern

```python
import dlt
from lancedb import lancedb_adapter

@dlt.resource(name="curriculum_chunks")
def chunks(pdf_path: str):
    text = extract_pdf_text(pdf_path)
    for i, chunk in enumerate(chunk_text(text)):
        yield {"id": f"{pdf_path}:{i}", "text": chunk, "source": pdf_path}

pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
load_info = pipeline.run(
    lancedb_adapter(chunks("ncca.pdf"), embed=["text"]),
)
```

## Configuration

The adapter reads its config from environment variables:

```bash
# .env
DESTINATION__LANCEDB__LANCE_URI=./lancedb_data
DESTINATION__LANCEDB__EMBEDDING_MODEL_PROVIDER=openai
DESTINATION__LANCEDB__EMBEDDING_MODEL=text-embedding-3-small
DESTINATION__LANCEDB__EMBEDDING_MODEL_API_KEY=...
DESTINATION__LANCEDB__VECTOR_COLUMN_NAME=embedding
DESTINATION__LANCEDB__ID_COLUMN_NAME=id
DESTINATION__LANCEDB__METADATA_COLUMN_NAME=metadata
```

Or pass them as kwargs to the adapter:

```python
lancedb_adapter(
    chunks("ncca.pdf"),
    embed=["text"],
    lancedb_uri="./lancedb_data",
    embedding_model_provider="openai",
    embedding_model="text-embedding-3-small",
)
```

## Supported embedding providers

| Provider | `EMBEDDING_MODEL_PROVIDER` | Example `EMBEDDING_MODEL` |
|:--|:--|:--|
| OpenAI | `openai` | `text-embedding-3-small`, `text-embedding-3-large` |
| Cohere | `cohere` | `embed-english-v3.0`, `embed-multilingual-v3.0` |
| HuggingFace | `huggingface` | `sentence-transformers/all-MiniLM-L6-v2` |
| Sentence-Transformers | `sentence-transformers` | `BAAI/bge-large-en-v1.5` |
| Gemini | `gemini` | `text-embedding-004` |
| Ollama | `ollama` | `nomic-embed-text` |

For a full list, see the `lancedb` skill's
`embed-functions-registry.md`.

## Multi-column embedding

You can embed multiple columns into separate vector columns:

```python
lancedb_adapter(
    chunks("ncca.pdf"),
    embed=["text", "summary"],  # 2 separate vector columns
)
```

The resulting table has `text_embedding` and `summary_embedding`
columns, both indexed.

## LanceDB Cloud

To write to LanceDB Cloud instead of local:

```bash
DESTINATION__LANCEDB__LANCE_URI=db://my-database
DESTINATION__LANCEDB__LANCE_API_KEY=...
DESTINATION__LANCEDB__LANCE_REGION=eu-west-1
```

## Vector search after the load

```python
import lancedb
db = lancedb.connect("./lancedb_data")
table = db.open_table("curriculum_chunks")
results = table.search("handwriting recognition for Irish").limit(10).to_pandas()
```

## KCG usage

- `cianfhoghlaim-semantic-search` spec (cross-corpus LanceDB HNSW)
- `cianfhoghlaim-leabharlann` (the books + zotero + takeout corpora
  are indexed in LanceDB via CocoIndex v1 Apps, not directly via
  dlt, but the `lancedb_adapter` is the canonical dlt-side pattern)
- The `cianfhoghlaim-semantic-search` Dagster asset group uses
  `lancedb_adapter` to backfill vectors

## Reference

- The full `dlt_lance.py` reference (600+ lines) was in `docs/dlt/`
  (deleted with the `sync-skills-from-docs` change). The same content
  is in the upstream
  [dlt-hub/verified-sources](https://github.com/dlt-hub/verified-sources)
  repo under `sources/lancedb/`
- The `lancedb` skill's `embed-functions-registry.md` for the
  full provider list
