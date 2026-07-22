# Multimodal Image Search in CocoIndex v1

The canonical pattern for image + text search using CLIP-style
embeddings. Two flavours: single-vector (CLIP) and multi-vector
(ColPali).

## Single-vector (CLIP + Qdrant)

```python
import cocoindex as coco
from cocoindex.connectors import localfs, qdrant
from cocoindex.resources.file import FileLike, PatternFilePathMatcher

# Assumes you've wrapped CLIP in a ContextKey + SentenceTransformerEmbedder
# (or a custom @coco.fn that calls CLIP).

@coco.fn(memo=True)
async def process_image(file: FileLike, target) -> None:
    image_bytes = await file.read_bytes()
    # Embed via CLIP
    embedding = await clip_embed(image_bytes)
    target.declare_row(row=ImageRecord(
        id=hash(file.file_path.path) & 0x7fffffff,
        filename=str(file.file_path.path),
        embedding=embedding,
    ))
```

## Multi-vector (ColPali + Qdrant MaxSim)

ColPali produces a multi-vector representation (one vector per
image patch), which is better for document / page retrieval. CocoIndex
v1 supports this via the `MultiVector` schema in Qdrant:

```python
# In a @dataclass row:
@dataclass
class DocPage:
    id: int
    image_id: str
    patch_vectors: list[list[float]]  # N patches × D dims
```

Qdrant's MaxSim scoring picks the best patch match per document.

## KCG examples

- `cocoindex/leabharlann_embedding.py` — text-only
  (BGE-large-en-v1.5) for the leabharlann books corpus
- The external `docs/cocoindex/image_search/` example (now in
  upstream cocoindex repo) is the canonical CLIP + Qdrant + FastAPI
  pattern
- The external `docs/cocoindex/image_search_colpali/` example is
  the canonical ColPali + Qdrant MaxSim pattern
