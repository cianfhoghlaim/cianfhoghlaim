# BAML Extraction in CocoIndex v1

Use BAML as the structured-extraction LLM in a CocoIndex v1 flow. BAML
provides typed Python objects via `baml_py`; you wrap a BAML function
call in a `@coco.fn(memo=True)` and write the typed result to a target.

## Minimal example

```python
import pathlib
from dataclasses import dataclass
from typing import Annotated, AsyncIterator, Any
import cocoindex as coco
from cocoindex.connectors import localfs, lancedb
from cocoindex.resources.file import FileLike, PatternFilePathMatcher
from baml_client import b  # auto-generated from your baml_src/

# 1. Define the BAML function in baml_src/extract.baml
#
# class ProductInfo {
#   name string
#   price float
#   category string
# }
#
# function ExtractProductInfo(text: string) -> ProductInfo {
#   client "openai/gpt-4o-mini"
#   prompt #"Extract the product info from this text: {{ text }}"#
# }

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDER = coco.ContextKey[Any]("embedder", detect_change=True)
LANCE_DB = coco.ContextKey[Any]("lance_db")

@dataclass
class ProductRecord:
    id: int
    filename: str
    name: str
    price: float
    category: str
    embedding: Annotated[Any, EMBEDDER]

@coco.lifespan
async def lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    from cocoindex.ops.sentence_transformers import SentenceTransformerEmbedder
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    import lancedb
    builder.provide(LANCE_DB, await lancedb.connect_async("./lancedb_data"))
    yield

@coco.fn(memo=True)
async def process_file(file: FileLike, table: lancedb.TableTarget[ProductRecord]) -> None:
    text = await file.read_text()
    info = b.ExtractProductInfo(text)            # typed BAML result
    embedder = await coco.use_context(EMBEDDER)
    embedding = await embedder.embed(info.name)  # 384-d float32
    table.declare_row(row=ProductRecord(
        id=hash(info.name) & 0x7fffffff,
        filename=str(file.file_path.path),
        name=info.name,
        price=info.price,
        category=info.category,
        embedding=embedding,
    ))

@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    target = await lancedb.mount_table_target(
        LANCE_DB, table_name="products",
        table_schema=await lancedb.TableSchema.from_class(ProductRecord, primary_key=["id"]),
    )
    target.declare_vector_index(column="embedding")
    files = localfs.walk_dir(sourcedir, recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.txt"]), live=True)
    await coco.mount_each(process_file, files.items(), target)

app = coco.App(coco.AppConfig(name="ProductExtractor"),
               app_main, sourcedir=pathlib.Path("./data"))
```

## Multimodal BAML (image / pdf / audio)

```python
import baml_py

@coco.fn(memo=True)
async def process_pdf(file: FileLike, target) -> None:
    pdf_bytes = await file.read_bytes()
    pdf = baml_py.Pdf.from_base64(pdf_bytes.decode("latin-1"))  # for some BAML versions
    # OR for image-based BAML:
    # image = baml_py.Image.from_base64("application/pdf", base64_str)
    receipt = b.ExtractReceiptTransactions(receipt_image=image)
    target.declare_row(row=MyRecord(text=receipt.grand_total, …))
```

See the `baml` skill's `references/multimodal-vision.md` for the
full BAML multimodal pattern.

## When to use BAML vs DSPy

| Criterion | BAML | DSPy |
|:--|:--|:--|
| Schema stability | Excellent (BAML files are version-controlled) | Good (signatures evolve) |
| Auto-retry on validation failure | Built-in retry policies (`Constant`, `Exponential`) | Manual via `dspy.Assert` |
| Multimodal (image / pdf / audio) | First-class (`image`, `pdf`, `audio` types) | Limited (`dspy.Image` for vision only) |
| Dynamic schemas (LLM describes the schema) | Native (`TypeBuilder`, `@@dynamic`) | Awkward (signatures are static) |
| Streaming | `baml.stream.<Func>` + `get_final_response` | `dspy.streamify` |
| Optimisation (auto-prompt-tune) | Not built-in | `dspy.BootstrapFewShot`, `dspy.MIPROv2` |

**Rule of thumb**: use BAML unless you need prompt optimisation
or have a DSPy-specific requirement.

## In-repo examples

- `cocoindex/docs_skills_consolidation.py` —
  BAML-driven extraction per file
- `cocoindex/curriculum_extraction.py` —
  BAML curriculum extraction
- The external `docs/cocoindex/patient_intake_extraction_baml/`
  example (now in upstream cocoindex repo) is the canonical
  BAML-multimodal pattern
