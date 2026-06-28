# Adding Data Sources

Guide for adding new data sources to the Tuath Celtic Educational MMO data pipeline.

## Overview

Data flows through the following pipeline:
```
Sources → DLT Ingestion → CocoIndex Transform → Vector/Graph Store → RAG Retrieval
```

### Current Data Sources

| Source | Type | Content | Language |
|--------|------|---------|----------|
| NCCA Curriculum | PDF/HTML | Irish curriculum specs | en/ga |
| SEC Exams | PDF | Past exam papers | en/ga |
| WJEC | PDF/HTML | Welsh curriculum | en/cy |
| SQA | PDF/HTML | Scottish qualifications | en/gd |
| Logainm | API | Irish place names | ga |
| Dúchas | API | Irish folklore | ga |
| Celtic Mythology | JSON | Character/story data | multi |

---

## Adding a New Source

### Step 1: Create DLT Source

DLT (Data Load Tool) handles extraction and incremental loading.

```python
# dlt_sources/my_source.py
"""
DLT source for [source name].

Extracts [content type] from [source location].
"""

import dlt
from dlt.sources.helpers import requests
from typing import Iterator
from pydantic import BaseModel


class MyDocument(BaseModel):
    """Schema for extracted documents."""
    id: str
    title: str
    content: str
    language: str
    source_url: str
    published_date: str | None = None
    metadata: dict = {}


@dlt.source(name="my_source")
def my_source(
    api_key: str = dlt.secrets.value,
    base_url: str = "https://api.example.com",
) -> Iterator[dlt.Resource]:
    """
    Extract documents from My Source.

    Args:
        api_key: API authentication key
        base_url: Base URL for the API

    Yields:
        DLT resources for documents
    """

    @dlt.resource(
        name="documents",
        write_disposition="merge",
        primary_key="id",
    )
    def documents() -> Iterator[MyDocument]:
        """Fetch all documents."""

        page = 1
        while True:
            response = requests.get(
                f"{base_url}/documents",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"page": page, "per_page": 100},
            )
            response.raise_for_status()
            data = response.json()

            if not data["items"]:
                break

            for item in data["items"]:
                yield MyDocument(
                    id=item["id"],
                    title=item["title"],
                    content=item["body"],
                    language=item.get("lang", "en"),
                    source_url=item["url"],
                    published_date=item.get("published_at"),
                    metadata={
                        "author": item.get("author"),
                        "category": item.get("category"),
                    },
                )

            page += 1

    yield documents


# Incremental loading for updates
@dlt.source(name="my_source_incremental")
def my_source_incremental(
    api_key: str = dlt.secrets.value,
    base_url: str = "https://api.example.com",
) -> Iterator[dlt.Resource]:
    """Incremental extraction with state tracking."""

    @dlt.resource(
        name="documents",
        write_disposition="merge",
        primary_key="id",
    )
    def documents(
        last_updated: dlt.sources.incremental[str] = dlt.sources.incremental(
            "updated_at",
            initial_value="2020-01-01T00:00:00Z",
        ),
    ) -> Iterator[MyDocument]:
        """Fetch documents updated since last sync."""

        response = requests.get(
            f"{base_url}/documents",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"updated_since": last_updated.last_value},
        )
        response.raise_for_status()

        for item in response.json()["items"]:
            yield MyDocument(
                id=item["id"],
                title=item["title"],
                content=item["body"],
                language=item.get("lang", "en"),
                source_url=item["url"],
                published_date=item.get("published_at"),
                metadata={"updated_at": item["updated_at"]},
            )

    yield documents
```

### Step 2: Configure Secrets

```toml
# .dlt/secrets.toml
[sources.my_source]
api_key = "your-api-key-here"

[destination.duckdb]
credentials = "tuath.duckdb"
```

### Step 3: Create Pipeline Script

```python
# dlt_sources/run_my_source.py
"""
Run the My Source pipeline.
"""

import dlt
from my_source import my_source


def run_pipeline(full_refresh: bool = False):
    """Execute the data pipeline."""

    pipeline = dlt.pipeline(
        pipeline_name="my_source_pipeline",
        destination="duckdb",
        dataset_name="my_source",
        progress="log",
    )

    # Load data
    source = my_source()

    if full_refresh:
        load_info = pipeline.run(source, write_disposition="replace")
    else:
        load_info = pipeline.run(source)

    print(f"Load completed: {load_info}")
    print(f"Loaded {load_info.load_packages[0].jobs['completed_jobs']} items")

    return load_info


if __name__ == "__main__":
    run_pipeline()
```

### Step 4: Create CocoIndex Flow

CocoIndex generates embeddings for vector search.

```python
# cocoindex_flows/my_source_embeddings.py
"""
CocoIndex flow for My Source embeddings.
"""

import cocoindex
from cocoindex import Flow, Table, VectorStore
from cocoindex.transforms import chunking, embedding


@cocoindex.flow(name="my_source_embeddings")
def create_flow(
    source_db: str = "tuath.duckdb",
    vector_db: str = "lancedb://tuath_vectors",
) -> Flow:
    """
    Create embedding flow for My Source documents.

    Args:
        source_db: DuckDB database path
        vector_db: LanceDB connection string

    Returns:
        CocoIndex flow definition
    """

    flow = Flow()

    # Source table
    documents = flow.add_source(
        Table.from_duckdb(
            connection=source_db,
            table="my_source.documents",
            columns=["id", "title", "content", "language", "metadata"],
        )
    )

    # Chunk content
    chunked = documents.pipe(
        chunking.RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " "],
        ),
        input_column="content",
        output_column="chunk",
    )

    # Generate embeddings using BGE-M3 (multilingual)
    embedded = chunked.pipe(
        embedding.SentenceTransformerEmbedding(
            model_name="BAAI/bge-m3",
            batch_size=100,  # CRITICAL: Always batch!
            device="cuda" if torch.cuda.is_available() else "cpu",
        ),
        input_column="chunk",
        output_column="embedding",
    )

    # Write to vector store
    flow.add_sink(
        embedded,
        VectorStore.to_lancedb(
            connection=vector_db,
            table_name="my_source_chunks",
            vector_column="embedding",
            id_column="id",
            metadata_columns=["title", "language", "chunk"],
        ),
    )

    return flow


# Run flow
if __name__ == "__main__":
    flow = create_flow()
    flow.run(batch_size=1000)
```

### Step 5: Create Dagster Asset

Dagster orchestrates the full pipeline.

```python
# dagster_assets/my_source.py
"""
Dagster assets for My Source pipeline.
"""

from dagster import (
    asset,
    AssetExecutionContext,
    DailyPartitionsDefinition,
    OpExecutionContext,
    Output,
    MetadataValue,
)
from datetime import datetime


daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")


@asset(
    group_name="my_source",
    description="Raw documents from My Source API",
    partitions_def=daily_partitions,
)
def my_source_raw(context: AssetExecutionContext) -> Output[dict]:
    """Extract raw documents from My Source."""

    from dlt_sources.my_source import my_source
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="my_source",
        destination="duckdb",
        dataset_name="my_source",
    )

    source = my_source()
    load_info = pipeline.run(source)

    row_count = load_info.load_packages[0].jobs.get("completed_jobs", 0)

    return Output(
        value={"load_info": str(load_info)},
        metadata={
            "row_count": MetadataValue.int(row_count),
            "pipeline": MetadataValue.text("my_source"),
            "timestamp": MetadataValue.text(datetime.now().isoformat()),
        },
    )


@asset(
    group_name="my_source",
    description="Embedded chunks in vector store",
    deps=["my_source_raw"],
)
def my_source_embeddings(context: AssetExecutionContext) -> Output[dict]:
    """Generate embeddings for My Source documents."""

    from cocoindex_flows.my_source_embeddings import create_flow

    flow = create_flow()
    result = flow.run(batch_size=1000)

    return Output(
        value={"chunks_embedded": result.rows_processed},
        metadata={
            "chunks_processed": MetadataValue.int(result.rows_processed),
            "embedding_model": MetadataValue.text("BAAI/bge-m3"),
        },
    )


@asset(
    group_name="my_source",
    description="Knowledge graph nodes and relationships",
    deps=["my_source_raw"],
)
def my_source_graph(context: AssetExecutionContext) -> Output[dict]:
    """Create graph nodes for My Source documents."""

    from tuath.knowledge_graph.falkordb_client import FalkorDBClient

    client = FalkorDBClient()

    # Load documents from DuckDB
    import duckdb
    conn = duckdb.connect("tuath.duckdb")
    docs = conn.execute("SELECT * FROM my_source.documents").fetchall()

    nodes_created = 0
    for doc in docs:
        # Create document node
        client.execute(
            """
            MERGE (d:Document {id: $id})
            SET d.title = $title,
                d.language = $language,
                d.source = 'my_source'
            """,
            {"id": doc[0], "title": doc[1], "language": doc[3]},
        )
        nodes_created += 1

    return Output(
        value={"nodes_created": nodes_created},
        metadata={
            "nodes_created": MetadataValue.int(nodes_created),
            "graph": MetadataValue.text("FalkorDB"),
        },
    )
```

### Step 6: Register with Dagster

```python
# dagster_assets/__init__.py

from dagster import Definitions, load_assets_from_modules

from . import curriculum, mythology, geospatial, my_source  # Add module

all_assets = load_assets_from_modules([
    curriculum,
    mythology,
    geospatial,
    my_source,  # Register assets
])

defs = Definitions(assets=all_assets)
```

---

## Source Types

### Web Scraping Sources

```python
# dlt_sources/web_source.py
"""Web scraping source using Crawl4AI."""

import dlt
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig


@dlt.source(name="web_source")
def web_source(urls: list[str]) -> Iterator[dlt.Resource]:
    """Scrape content from web pages."""

    @dlt.resource(name="pages", write_disposition="merge", primary_key="url")
    async def pages():
        browser_config = BrowserConfig(headless=True)
        crawler_config = CrawlerRunConfig(
            word_count_threshold=100,
            excluded_tags=["nav", "footer", "aside"],
        )

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for url in urls:
                result = await crawler.arun(url, config=crawler_config)

                if result.success:
                    yield {
                        "url": url,
                        "title": result.metadata.get("title", ""),
                        "content": result.markdown,
                        "language": detect_language(result.markdown),
                    }

    yield pages
```

### PDF Sources

```python
# dlt_sources/pdf_source.py
"""PDF document source using Docling."""

import dlt
from docling.document_converter import DocumentConverter
from pathlib import Path


@dlt.source(name="pdf_source")
def pdf_source(directory: str) -> Iterator[dlt.Resource]:
    """Extract content from PDF documents."""

    converter = DocumentConverter()

    @dlt.resource(name="documents", write_disposition="merge", primary_key="path")
    def documents():
        pdf_dir = Path(directory)

        for pdf_path in pdf_dir.glob("**/*.pdf"):
            try:
                result = converter.convert(str(pdf_path))
                doc = result.document

                yield {
                    "path": str(pdf_path),
                    "title": doc.metadata.get("title", pdf_path.stem),
                    "content": doc.export_to_markdown(),
                    "pages": len(doc.pages),
                    "metadata": doc.metadata,
                }
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")

    yield documents
```

### API Sources

```python
# dlt_sources/rest_api_source.py
"""Generic REST API source."""

import dlt
from dlt.sources.rest_api import rest_api_source, RESTAPIConfig


def create_api_source(
    base_url: str,
    endpoints: list[dict],
    auth_token: str,
) -> dlt.Source:
    """Create a REST API source."""

    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            "auth": {
                "type": "bearer",
                "token": auth_token,
            },
        },
        "resources": [
            {
                "name": ep["name"],
                "endpoint": {
                    "path": ep["path"],
                    "params": ep.get("params", {}),
                    "paginator": {
                        "type": "page_number",
                        "page_param": "page",
                        "total_path": "meta.total_pages",
                    },
                },
            }
            for ep in endpoints
        ],
    }

    return rest_api_source(config)
```

---

## Embedding Strategies

### Multilingual Embeddings

```python
# For Celtic language content, use BGE-M3
embedding.SentenceTransformerEmbedding(
    model_name="BAAI/bge-m3",  # Supports 100+ languages including Celtic
    batch_size=100,
)
```

### Domain-Specific Embeddings

```python
# For Irish-specific content
embedding.SentenceTransformerEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    batch_size=100,
)

# For curriculum/educational content
embedding.SentenceTransformerEmbedding(
    model_name="BAAI/bge-large-en-v1.5",
    batch_size=50,  # Larger model, smaller batches
)
```

### Chunking Strategies

```python
# For structured documents (curriculum)
chunking.RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n\n", "\n", ". "],
)

# For prose/stories (mythology)
chunking.RecursiveCharacterTextSplitter(
    chunk_size=1024,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", "! ", "? "],
)

# For technical content
chunking.RecursiveCharacterTextSplitter(
    chunk_size=256,
    chunk_overlap=25,
    separators=["\n\n", "\n", ". "],
)
```

---

## Graph Integration

### Creating Entity Nodes

```python
# knowledge_graph/my_source_graph.py
"""Create graph nodes for My Source."""

from tuath.knowledge_graph.falkordb_client import FalkorDBClient


async def create_graph_nodes(documents: list[dict]) -> int:
    """Create document nodes in knowledge graph."""

    client = FalkorDBClient()
    nodes_created = 0

    for doc in documents:
        # Create document node
        await client.execute(
            """
            MERGE (d:Document {id: $id})
            SET d.title = $title,
                d.content_preview = $preview,
                d.language = $language,
                d.source = $source,
                d.created_at = datetime()
            """,
            {
                "id": doc["id"],
                "title": doc["title"],
                "preview": doc["content"][:500],
                "language": doc["language"],
                "source": "my_source",
            },
        )
        nodes_created += 1

        # Extract and create entity relationships
        entities = extract_entities(doc["content"])
        for entity in entities:
            await client.execute(
                """
                MERGE (e:Entity {name: $name, type: $type})
                WITH e
                MATCH (d:Document {id: $doc_id})
                MERGE (d)-[:MENTIONS]->(e)
                """,
                {
                    "name": entity["name"],
                    "type": entity["type"],
                    "doc_id": doc["id"],
                },
            )

    return nodes_created
```

### Linking to Existing Entities

```python
async def link_to_mythology(documents: list[dict]) -> int:
    """Link documents to mythology entities."""

    client = FalkorDBClient()
    links_created = 0

    for doc in documents:
        # Find mentioned mythology characters
        characters = extract_character_mentions(doc["content"])

        for char_name in characters:
            result = await client.execute(
                """
                MATCH (d:Document {id: $doc_id})
                MATCH (c:MythologyEntity {name: $char_name})
                MERGE (d)-[:REFERENCES]->(c)
                RETURN c.name
                """,
                {"doc_id": doc["id"], "char_name": char_name},
            )

            if result:
                links_created += 1

    return links_created
```

---

## Testing Pipelines

### DLT Source Tests

```python
# tests/test_my_source.py
import pytest
from dlt_sources.my_source import my_source


def test_source_schema():
    """Verify source produces expected schema."""
    source = my_source()
    resources = list(source.resources.keys())

    assert "documents" in resources


def test_source_extraction(mock_api):
    """Test document extraction."""
    source = my_source()
    docs = list(source.resources["documents"])

    assert len(docs) > 0
    assert all("id" in d for d in docs)
    assert all("content" in d for d in docs)
```

### CocoIndex Flow Tests

```python
# tests/test_embeddings.py
import pytest
from cocoindex_flows.my_source_embeddings import create_flow


def test_flow_creation():
    """Verify flow creates successfully."""
    flow = create_flow()

    assert flow is not None
    assert len(flow.sources) == 1
    assert len(flow.sinks) == 1


def test_embedding_generation(sample_documents):
    """Test embedding generation."""
    flow = create_flow()
    result = flow.run(documents=sample_documents, batch_size=10)

    assert result.rows_processed == len(sample_documents)
```

### Dagster Asset Tests

```python
# tests/test_dagster_assets.py
from dagster import build_asset_context
from dagster_assets.my_source import my_source_raw


def test_asset_execution():
    """Test Dagster asset runs successfully."""
    context = build_asset_context()
    result = my_source_raw(context)

    assert result is not None
    assert "load_info" in result.value
```

---

## Monitoring

### Pipeline Metrics

```python
# dagster_assets/my_source.py
from dagster import MetadataValue, Output
import time


@asset(group_name="my_source")
def my_source_raw(context: AssetExecutionContext) -> Output[dict]:
    """Extract with monitoring."""

    start_time = time.time()

    # ... extraction logic ...

    duration = time.time() - start_time

    return Output(
        value={"rows": row_count},
        metadata={
            "row_count": MetadataValue.int(row_count),
            "duration_seconds": MetadataValue.float(duration),
            "rows_per_second": MetadataValue.float(row_count / duration),
            "timestamp": MetadataValue.text(datetime.now().isoformat()),
        },
    )
```

### Alerting on Failures

```python
from dagster import failure_hook, HookContext


@failure_hook
def notify_on_failure(context: HookContext):
    """Send alert on pipeline failure."""

    # Log error
    context.log.error(f"Asset {context.op.name} failed!")

    # Send notification (Slack, email, etc.)
    send_slack_alert(
        channel="#data-alerts",
        message=f"Pipeline failure: {context.op.name}",
        error=str(context.op_exception),
    )
```

---

## Related Documentation

- [Architecture](../ARCHITECTURE.md) - System overview
- [Performance Tuning](./PERFORMANCE_TUNING.md) - Embedding optimization
- [Celtic Languages](./CELTIC_LANGUAGES.md) - Language-specific processing
