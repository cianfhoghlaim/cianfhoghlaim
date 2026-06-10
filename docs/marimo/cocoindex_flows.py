# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "cocoindex[embeddings,lancedb]>=0.3.9",
#     "polars>=1.0.0",
#     "altair>=5.0.0",
#     "pandas>=2.0.0",
#     "python-dotenv>=1.0.0",
#     "lancedb>=0.24.0",
#     "sentence-transformers>=3.0.0",
# ]
# ///

import marimo

__generated_with = "0.17.7"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # CocoIndex: Semantic Document Indexing

    This notebook demonstrates CocoIndex's capabilities for building semantic search pipelines:

    1. **Flow Definitions** - Declarative data processing pipelines
    2. **Transform Flows** - Reusable embedding and transformation logic
    3. **Source Connectors** - Local files, S3, GitHub, custom APIs
    4. **Target Exports** - LanceDB, PostgreSQL, Neo4j, Qdrant
    5. **Query Handlers** - Semantic search with vector similarity

    > Based on patterns from `/data/examples/cocoindex/`
    """)
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv()
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. CocoIndex Architecture Overview

    CocoIndex uses a **flow-based architecture**:

    ```
    Source → Transform → Collect → Export → Target
    ```

    - **Sources**: Where data comes from (files, APIs, databases)
    - **Transforms**: Processing steps (chunking, embedding, extraction)
    - **Collectors**: Aggregation points for structured output
    - **Targets**: Where indexed data is stored (vector DBs, graph DBs)
    """)
    return


@app.cell
def _():
    import cocoindex
    import cocoindex.targets.lancedb as coco_lancedb
    import datetime
    import math
    return coco_lancedb, cocoindex, datetime, math


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Transform Flow: Reusable Embedding Logic

    Transform flows define reusable operations that can be shared between indexing and querying.
    """)
    return


@app.cell
def _(cocoindex):
    @cocoindex.transform_flow()
    def text_to_embedding(
        text: cocoindex.DataSlice[str],
    ) -> cocoindex.DataSlice[list[float]]:
        """
        Embed text using SentenceTransformer model.

        This transform flow is shared between:
        - Indexing: Converting document chunks to embeddings
        - Querying: Converting search queries to embeddings
        """
        return text.transform(
            cocoindex.functions.SentenceTransformerEmbed(
                model="sentence-transformers/all-MiniLM-L6-v2"
            )
        )
    return (text_to_embedding,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Flow Definition: Document Indexing

    Define a complete flow for indexing markdown documents into LanceDB.
    """)
    return


@app.cell
def _(mo):
    # Configuration inputs
    source_path = mo.ui.text(
        value="./sample_docs",
        label="Source Directory",
        placeholder="Path to markdown files"
    )

    lancedb_uri = mo.ui.text(
        value="./cocoindex_lancedb",
        label="LanceDB URI",
        placeholder="Path for LanceDB storage"
    )

    table_name = mo.ui.text(
        value="DocumentEmbeddings",
        label="Table Name"
    )

    mo.hstack([source_path, lancedb_uri, table_name])
    return lancedb_uri, source_path, table_name


@app.cell
def _(
    coco_lancedb,
    cocoindex,
    datetime,
    lancedb_uri,
    source_path,
    table_name,
    text_to_embedding,
):
    # Define the flow (not executed yet)
    LANCEDB_URI = lancedb_uri.value
    LANCEDB_TABLE = table_name.value

    @cocoindex.flow_def(name="DocumentIndexing")
    def document_indexing_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope
    ) -> None:
        """
        Flow that indexes markdown documents into LanceDB with embeddings.

        Steps:
        1. Load markdown files from source directory
        2. Split into chunks using recursive chunking
        3. Generate embeddings for each chunk
        4. Export to LanceDB with vector index
        """
        # 1. Add source - reads markdown files with refresh interval
        data_scope["documents"] = flow_builder.add_source(
            cocoindex.sources.LocalFile(
                path=source_path.value,
                included_patterns=["*.md", "*.mdx", "*.txt"],
            ),
            refresh_interval=datetime.timedelta(seconds=30),
        )

        # 2. Create collector for output
        doc_embeddings = data_scope.add_collector()

        # 3. Process each document
        with data_scope["documents"].row() as doc:
            # Split document into chunks
            doc["chunks"] = doc["content"].transform(
                cocoindex.functions.SplitRecursively(),
                language="markdown",
                chunk_size=500,
                chunk_overlap=100,
            )

            # Process each chunk
            with doc["chunks"].row() as chunk:
                # Generate embedding using shared transform flow
                chunk["embedding"] = text_to_embedding(chunk["text"])

                # Collect results
                doc_embeddings.collect(
                    id=cocoindex.GeneratedField.UUID,
                    filename=doc["filename"],
                    location=chunk["location"],
                    text=chunk["text"],
                    text_embedding=chunk["embedding"],
                )

        # 4. Export to LanceDB
        doc_embeddings.export(
            "doc_embeddings",
            coco_lancedb.LanceDB(db_uri=LANCEDB_URI, table_name=LANCEDB_TABLE),
            primary_key_fields=["id"],
        )
    return LANCEDB_TABLE, LANCEDB_URI, document_indexing_flow


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Query Handler: Semantic Search

    Define a query handler that uses the same embedding transform for search queries.
    """)
    return


@app.cell
def _(
    LANCEDB_TABLE,
    LANCEDB_URI,
    coco_lancedb,
    cocoindex,
    document_indexing_flow,
    math,
    text_to_embedding,
):
    @document_indexing_flow.query_handler(
        result_fields=cocoindex.QueryHandlerResultFields(
            embedding=["embedding"],
            score="score",
        ),
    )
    async def semantic_search(query: str) -> cocoindex.QueryOutput:
        """
        Perform semantic search on indexed documents.

        Args:
            query: Natural language search query

        Returns:
            QueryOutput with ranked results and embeddings
        """
        # Connect to LanceDB
        db = await coco_lancedb.connect_async(LANCEDB_URI)
        table = await db.open_table(LANCEDB_TABLE)

        # Get embedding for query using shared transform flow
        query_embedding = await text_to_embedding.eval_async(query)

        # Vector search
        search = await table.search(
            query_embedding,
            vector_column_name="text_embedding"
        )
        results = await search.limit(10).to_list()

        return cocoindex.QueryOutput(
            results=[
                {
                    "filename": r["filename"],
                    "text": r["text"],
                    "embedding": r["text_embedding"],
                    "score": math.sqrt(r["_distance"]),  # L2 distance
                }
                for r in results
            ],
            query_info=cocoindex.QueryInfo(
                embedding=query_embedding,
                similarity_metric=cocoindex.VectorSimilarityMetric.L2_DISTANCE,
            ),
        )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Knowledge Graph Flow (Neo4j)

    CocoIndex can extract entities and relationships for knowledge graphs.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    import dataclasses
    import cocoindex

    @dataclasses.dataclass
    class DocumentSummary:
        '''Document summary extracted by LLM.'''
        title: str
        summary: str

    @dataclasses.dataclass
    class Relationship:
        '''Entity relationship (subject-predicate-object).'''
        subject: str
        predicate: str
        object: str

    @cocoindex.flow_def(name="DocsToKnowledgeGraph")
    def knowledge_graph_flow(
        flow_builder: cocoindex.FlowBuilder,
        data_scope: cocoindex.DataScope
    ) -> None:
        '''Extract knowledge graph from documents.'''

        # Load documents
        data_scope["documents"] = flow_builder.add_source(
            cocoindex.sources.LocalFile(
                path="./docs",
                included_patterns=["*.md", "*.mdx"],
            )
        )

        # Collectors for different node types
        document_nodes = data_scope.add_collector()
        entity_relationships = data_scope.add_collector()
        entity_mentions = data_scope.add_collector()

        with data_scope["documents"].row() as doc:
            # Extract summary via LLM
            doc["summary"] = doc["content"].transform(
                cocoindex.functions.ExtractByLlm(
                    llm_spec=cocoindex.LlmSpec(
                        api_type=cocoindex.LlmApiType.OPENAI,
                        model="gpt-4o-mini",
                    ),
                    output_type=DocumentSummary,
                    instruction="Summarize this document.",
                )
            )

            document_nodes.collect(
                filename=doc["filename"],
                title=doc["summary"]["title"],
                summary=doc["summary"]["summary"],
            )

            # Extract relationships via LLM
            doc["relationships"] = doc["content"].transform(
                cocoindex.functions.ExtractByLlm(
                    llm_spec=cocoindex.LlmSpec(
                        api_type=cocoindex.LlmApiType.OPENAI,
                        model="gpt-4o-mini",
                    ),
                    output_type=list[Relationship],
                    instruction="Extract entity relationships.",
                )
            )

            with doc["relationships"].row() as rel:
                entity_relationships.collect(
                    id=cocoindex.GeneratedField.UUID,
                    subject=rel["subject"],
                    predicate=rel["predicate"],
                    object=rel["object"],
                )

        # Export to Neo4j
        neo4j_conn = cocoindex.add_auth_entry(
            "Neo4jConnection",
            cocoindex.targets.Neo4jConnection(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="password",
            ),
        )

        document_nodes.export(
            "document_nodes",
            cocoindex.targets.Neo4j(
                connection=neo4j_conn,
                mapping=cocoindex.targets.Nodes(label="Document")
            ),
            primary_key_fields=["filename"],
        )

        entity_relationships.export(
            "relationships",
            cocoindex.targets.Neo4j(
                connection=neo4j_conn,
                mapping=cocoindex.targets.Relationships(
                    rel_type="RELATES_TO",
                    source=cocoindex.targets.NodeFromFields(
                        label="Entity",
                        fields=[cocoindex.targets.TargetFieldMapping(
                            source="subject", target="value"
                        )],
                    ),
                    target=cocoindex.targets.NodeFromFields(
                        label="Entity",
                        fields=[cocoindex.targets.TargetFieldMapping(
                            source="object", target="value"
                        )],
                    ),
                ),
            ),
            primary_key_fields=["id"],
        )
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Custom Source Connector

    Create custom sources for APIs like Hacker News.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    from typing import NamedTuple, AsyncIterator
    from cocoindex.op import SourceSpec, source_connector
    from cocoindex.sources import PartialSourceRow, PartialSourceRowData
    import aiohttp

    class HackerNewsThreadKey(NamedTuple):
        '''Row key for HN source.'''
        thread_id: str

    @dataclasses.dataclass
    class HackerNewsThread:
        '''Thread data from HN API.'''
        author: str | None
        text: str
        url: str | None
        created_at: datetime | None
        comments: list[dict]

    class HackerNewsSource(SourceSpec):
        '''Source spec for HackerNews API.'''
        tag: str | None = None
        max_results: int = 200

    @source_connector(
        spec_cls=HackerNewsSource,
        key_type=HackerNewsThreadKey,
        value_type=HackerNewsThread,
    )
    class HackerNewsConnector:
        '''Custom source connector for HN.'''

        @staticmethod
        async def create(spec: HackerNewsSource) -> "HackerNewsConnector":
            return HackerNewsConnector(spec, aiohttp.ClientSession())

        async def list(self) -> AsyncIterator[PartialSourceRow]:
            '''List threads from search API.'''
            url = "https://hn.algolia.com/api/v1/search_by_date"
            params = {"hitsPerPage": self._spec.max_results}
            if self._spec.tag:
                params["tags"] = self._spec.tag

            async with self._session.get(url, params=params) as response:
                data = await response.json()
                for hit in data.get("hits", []):
                    if thread_id := hit.get("objectID"):
                        yield PartialSourceRow(
                            key=HackerNewsThreadKey(thread_id=thread_id),
                            data=PartialSourceRowData(ordinal=hit.get("created_at_i", 0)),
                        )

        async def get_value(
            self, key: HackerNewsThreadKey
        ) -> PartialSourceRowData[HackerNewsThread]:
            '''Fetch full thread data.'''
            url = f"https://hn.algolia.com/api/v1/items/{key.thread_id}"
            async with self._session.get(url) as response:
                data = await response.json()
                return PartialSourceRowData(
                    value=self._parse_thread(data)
                )

    # Usage in flow
    @cocoindex.flow_def(name="HackerNewsIndex")
    def hn_flow(flow_builder, data_scope):
        data_scope["threads"] = flow_builder.add_source(
            HackerNewsSource(tag="story", max_results=100),
            refresh_interval=timedelta(minutes=5),
        )
        # ... process threads
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Custom Operations

    Define custom processing operations with caching and GPU support.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    import cocoindex
    from PIL import Image
    import io

    @cocoindex.op.function(cache=True, behavior_version=1, gpu=True)
    def image_to_embedding(img_bytes: bytes) -> list[float]:
        '''
        Generate CLIP embedding from image bytes.

        Args:
            img_bytes: Raw image bytes

        Returns:
            CLIP embedding vector

        Decorators:
            cache=True: Cache results for identical inputs
            behavior_version=1: Increment when logic changes
            gpu=True: Enable GPU acceleration
        '''
        from transformers import CLIPProcessor, CLIPModel
        import torch

        model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            features = model.get_image_features(**inputs)

        return features[0].tolist()

    @cocoindex.op.function()
    def extract_pdf_pages(content: bytes) -> list[dict]:
        '''Extract text and images from PDF pages.'''
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(content))
        pages = []

        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            pages.append({
                "page_number": i + 1,
                "text": text,
            })

        return pages
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Live Updater Pattern

    Keep index in sync with source changes using FlowLiveUpdater.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```python
    import cocoindex
    from psycopg_pool import ConnectionPool

    def main():
        # Initialize CocoIndex
        cocoindex.init()

        # Setup flow
        document_indexing_flow.setup()

        # Start live updater - watches for changes
        with cocoindex.FlowLiveUpdater(
            document_indexing_flow,
            cocoindex.FlowLiveUpdaterOptions(print_stats=True)
        ) as updater:
            # Interactive query loop while index updates
            while True:
                query = input("Search (or 'quit'): ")
                if query.lower() == 'quit':
                    break

                # Search runs against live-updating index
                results = semantic_search(query)
                for r in results.results:
                    print(f"[{r['score']:.3f}] {r['filename']}: {r['text'][:100]}...")

    if __name__ == "__main__":
        main()
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. CLI Commands

    CocoIndex provides a CLI for common operations.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ```bash
    # Install CocoIndex
    pip install 'cocoindex[embeddings,lancedb]'

    # Update/build the index
    cocoindex update main

    # Live mode - watch for changes
    cocoindex update -L main

    # Start interactive server with CocoInsight UI
    cocoindex server -ci main

    # Show flow status
    cocoindex status main

    # Drop and recreate index
    cocoindex drop main
    cocoindex update main
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Key Patterns Summary

    ### Flow Definition
    ```python
    @cocoindex.flow_def(name="MyFlow")
    def my_flow(flow_builder, data_scope):
        # Add source
        data_scope["items"] = flow_builder.add_source(
            cocoindex.sources.LocalFile(path="./data")
        )

        # Create collector
        output = data_scope.add_collector()

        # Process rows
        with data_scope["items"].row() as item:
            item["embedding"] = text_to_embedding(item["content"])
            output.collect(id=..., text=..., embedding=...)

        # Export
        output.export("output", target_spec, primary_key_fields=["id"])
    ```

    ### Transform Flow (Reusable)
    ```python
    @cocoindex.transform_flow()
    def my_transform(data: DataSlice[str]) -> DataSlice[list[float]]:
        return data.transform(cocoindex.functions.SomeFunction())

    # Use in indexing
    chunk["embedding"] = my_transform(chunk["text"])

    # Use in querying
    query_embedding = await my_transform.eval_async(query)
    ```

    ### Query Handler
    ```python
    @my_flow.query_handler(
        result_fields=QueryHandlerResultFields(embedding=["emb"], score="score")
    )
    async def search(query: str) -> QueryOutput:
        embedding = await transform.eval_async(query)
        results = await db.search(embedding).to_list()
        return QueryOutput(results=results, query_info=...)
    ```

    ### Custom Operations
    ```python
    @cocoindex.op.function(cache=True, gpu=True, behavior_version=1)
    def my_operation(input: InputType) -> OutputType:
        # Processing logic
        return output
    ```
    """)
    return


if __name__ == "__main__":
    app.run()
