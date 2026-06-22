# Embeddings Registry (10+ Providers)

LanceDB's `embedding.get_registry().get("<provider>")` gives you
access to 10+ embedding providers through a uniform interface.
The registry handles auth, batching, and async dispatch.

## Canonical pattern

```python
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

registry = get_registry()

# Pick a provider
model = registry.get("openai").create(name="text-embedding-3-small")

# Bind to a LanceModel
class Document(LanceModel):
    text: str = model.SourceField()  # source field
    vector: Vector(model.ndims()) = model.VectorField()  # auto-embedded

# Create table (embeddings auto-generated on insert)
table = db.create_table("docs", schema=Document)
table.add([{"text": "..."}, {"text": "..."}])  # embeddings are computed automatically
```

## Provider list

| Provider | Registry key | Typical models | Notes |
|:--|:--|:--|:--|
| OpenAI | `openai` | `text-embedding-3-small` (1536-d), `text-embedding-3-large` (3072-d), `text-embedding-ada-002` | Requires `OPENAI_API_KEY` |
| Cohere | `cohere` | `embed-english-v3.0` (1024-d), `embed-multilingual-v3.0` | Requires `COHERE_API_KEY` |
| HuggingFace | `huggingface` | Any sentence-transformers model (e.g. `BAAI/bge-large-en-v1.5`, 1024-d) | Local, no API key |
| Sentence-Transformers | `sentence-transformers` | Same as HuggingFace, but with the `sentence-transformers` library | Local |
| ColBERT | `colbert` | `colbert-ir/colbertv2.0` | Multi-vector; pair with Qdrant MaxSim |
| Gemini | `gemini` | `text-embedding-004` (768-d) | Requires `GOOGLE_API_KEY` |
| Bedrock | `bedrock` | `amazon.titan-embed-text-v1` (1536-d) | Requires AWS creds |
| Ollama | `ollama` | `nomic-embed-text` (768-d), `mxbai-embed-large` | Local; no API key |
| OpenCLIP | `open-clip` | `ViT-B-32`, `ViT-L-14` | Multimodal (image + text) |
| Jina | `jina` | `jina-embeddings-v3` (1024-d) | Multilingual |

## Multilingual pattern (KCG-relevant)

For oideachais (Irish, Welsh, Scottish Gaelic, Breton), use
multilingual models:

```python
# BGE-M3 (100+ languages, 1024-d, multilingual)
model = registry.get("huggingface").create(
    name="BAAI/bge-m3",
    device="cuda",  # or "cpu", "mps"
)

# Or Cohere embed-multilingual-v3.0
model = registry.get("cohere").create(
    name="embed-multilingual-v3.0",
    input_type="search_document",  # or "search_query"
)
```

## Batching

The registry auto-batches. For large inserts, you can tune the batch
size:

```python
model = registry.get("openai").create(
    name="text-embedding-3-small",
    batch_size=128,  # default 32
)
```

## Async embedding

```python
import asyncio

async def embed_all(texts):
    tasks = [model.aembed(text) for text in texts]
    return await asyncio.gather(*tasks)

embeddings = asyncio.run(embed_all(texts))
```

## Custom provider

If a provider isn't in the registry, you can implement your own by
subclassing `lancedb.embeddings.base.TextEmbeddingFunction`:

```python
from lancedb.embeddings.base import TextEmbeddingFunction
from lancedb.embeddings.registry import register

@register("my-provider")
class MyProvider(TextEmbeddingFunction):
    ndims: int = 768
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        # Call your model here
        return my_model.encode(texts).tolist()

# Use it
model = registry.get("my-provider").create()
```

## When NOT to use the registry

- You need fine-grained control over the model (e.g. LoRA, custom
  tokenisation) — call the model directly and pass the embeddings to
  `table.add([{..., "vector": vec}])`
- The model is not a text/image embedder (e.g. you want to store
  custom features) — just write the column manually
