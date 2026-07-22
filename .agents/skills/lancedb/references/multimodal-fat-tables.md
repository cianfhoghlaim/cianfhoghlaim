# Multimodal "Fat Table" Pattern

LanceDB supports storing BLOBs (images, audio, PDFs) alongside
vectors and metadata in the same row — the "fat table" pattern. This
is the recommended approach for small-to-medium BLOBs (< 1 MB).

## Schema

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("filename", pa.string()),
    # BLOB: image / audio / PDF bytes
    pa.field("image_blob", pa.large_list(pa.uint8())),
    # Vector: CLIP / OpenCLIP embedding
    pa.field("image_embedding", pa.list_(pa.float32(), 768)),
    # Metadata
    pa.field("description", pa.string()),
    pa.field("tags", pa.list_(pa.string())),
    # Optional: pre-computed text embedding for hybrid search
    pa.field("text_embedding", pa.list_(pa.float32(), 1024)),
])

table = db.create_table("multimodal", schema=schema)
```

## Insert

```python
import clip
import io
from PIL import Image

def embed_image(image_bytes: bytes) -> list[float]:
    image = Image.open(io.BytesIO(image_bytes))
    return clip.encode(image).tolist()

# Single insert
table.add([{
    "id": 1,
    "filename": "recipe.png",
    "image_blob": open("recipe.png", "rb").read(),
    "image_embedding": embed_image(open("recipe.png", "rb").read()),
    "description": "Beef stew with root vegetables",
    "tags": ["main", "irish"],
}])

# Batch insert
rows = []
for path in image_paths:
    with open(path, "rb") as f:
        data = f.read()
    rows.append({
        "id": hash(path) & 0x7fffffff,
        "filename": path,
        "image_blob": data,
        "image_embedding": embed_image(data),
        "description": caption(path),  # from a vision LLM
    })
table.add(rows)
```

## Range-read on BLOB

LanceDB supports range-reads on `large_list` columns, so you can
fetch only the BLOB for the top-K results:

```python
results = table.search(query_vec).limit(10).to_pandas()
for r in results.itertuples():
    # The image_blob is already a list of bytes (pyarrow large_list)
    image = Image.open(io.BytesIO(bytes(r.image_blob)))
    image.show()
```

If you only need the embedding + metadata (not the BLOB), use
`select(["id", "filename", "image_embedding", "description"])`:

```python
results = (table.search(query_vec)
          .select(["id", "filename", "description", "image_embedding"])
          .limit(10)
          .to_pandas())
```

## Fat table vs pointer strategy

| | Fat table | Pointer strategy |
|:--|:--|:--|
| **BLOB size** | < 1 MB recommended | Any size |
| **Storage** | Lance (one copy) | S3/R2 (BLOB) + Lance (URL) |
| **Read pattern** | Single query | Two queries (metadata + BLOB fetch) |
| **Best for** | Small images, audio clips, page previews | Full videos, large PDFs, raw datasets |
| **Cons** | Slower for very large BLOBs | Extra round-trip for BLOB fetch |

**Rule of thumb**: if the BLOB is < 1 MB, use the fat table. If
> 1 MB, use the pointer strategy.

## Hybrid multimodal search

```python
# Vector search on the image embedding
results = (table.search(query_vec)
          .select(["id", "filename", "image_embedding", "text_embedding", "description"])
          .limit(20)
          .to_pandas())

# Re-rank with the text embedding (hybrid)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
scores = reranker.predict([(query, r.description) for r in results.itertuples()])
results["rerank_score"] = scores
results = results.sort_values("rerank_score", ascending=False).head(10)
```

## KCG example

The `cocoindex/leabharlann_embedding.py` CocoIndex
v1 App embeds the books corpus as text + image (BGE-large-en-v1.5
for text; the multimodal pattern is delegated to a separate
`cocoindex/image_embedding.py` flow if/when
the leabharlann includes cover images).

The external `multimodal-recipe-agent` and `multimodal-search`
examples in the upstream lancedb/vectordb-recipes repo (deleted
with the docs) are the canonical multimodal fat-table patterns.
