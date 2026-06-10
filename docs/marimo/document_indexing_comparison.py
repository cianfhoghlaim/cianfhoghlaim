# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "cognee>=0.1.0",
#     "cocoindex[embeddings,lancedb]>=0.3.9",
#     "chunkhound>=0.1.0",
#     "lancedb>=0.24.0",
#     "polars>=1.0.0",
#     "altair>=5.0.0",
#     "pandas>=2.0.0",
#     "python-dotenv>=1.0.0",
#     "sentence-transformers>=3.0.0",
#     "neo4j>=5.0.0",
# ]
# ///

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Document Indexing Comparison: Cognee vs CocoIndex vs ChunkHound

        This notebook provides a comprehensive comparison of three document indexing and knowledge graph systems:

        | Feature | **Cognee** | **CocoIndex** | **ChunkHound** |
        |---------|-----------|---------------|----------------|
        | **Primary Focus** | AI Memory & Knowledge Graphs | Semantic Document Indexing | Code Search & Exploration |
        | **Architecture** | ECL Pipeline (Extract→Cognify→Load) | Flow-based Declarative | cAST + Hybrid Search |
        | **Chunking** | Automatic | Configurable Recursive | AST-aware (tree-sitter) |
        | **Vector DB** | LanceDB, Qdrant, PGVector | LanceDB, PostgreSQL, Qdrant | DuckDB, LanceDB |
        | **Graph DB** | KuzuDB, Neo4j, Memgraph | Neo4j | N/A |
        | **Search Types** | Multi-type (6 modes) | Vector + Query Handlers | Hybrid (Semantic + Regex) |
        | **Best For** | Conversational AI, Agent Memory | Document Search, RAG | Code Understanding |

        > Based on research from `/research/data/cognee/`, `/research/data/cocoindex/`, `/research/data/chunkhound/`
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv()
    return mo, os, Path, load_dotenv


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 1. Architecture Comparison

        ### Cognee: ECL Pipeline
        ```
        Raw Data → Extract → Cognify → Load
                     ↓          ↓         ↓
                   Parse    Build KG   Store
        ```

        ### CocoIndex: Flow-Based
        ```
        Source → Transform → Collect → Export → Target
                    ↓           ↓
                 Chunk       Aggregate
                 Embed
        ```

        ### ChunkHound: cAST + Search
        ```
        Code → tree-sitter → AST Chunks → Embed → Index
                                ↓           ↓
                           Boundaries   DuckDB/Lance
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 2. Cognee: AI Memory System

        Cognee transforms raw data into persistent, dynamic memory using knowledge graphs.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ### Core Pattern: ECL (Extract → Cognify → Load)

        ```python
        import cognee

        # Configure storage backends
        cognee.config.set_llm_config({
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
        })
        cognee.config.set_vector_db_config({
            "vector_db_provider": "lancedb",
            "vector_db_url": "./cognee_vectors"
        })
        cognee.config.set_graph_db_config({
            "graph_db_provider": "memgraph",
            "graph_db_url": "bolt://localhost:7687"
        })

        # ECL Pipeline
        async def build_knowledge_base():
            # 1. EXTRACT: Add raw content
            await cognee.add(
                "path/to/documents/",
                dataset_name="my_knowledge"
            )

            # Also supports:
            # await cognee.add(url, dataset_name="web_content")
            # await cognee.add(text_content, dataset_name="text_data")
            # await cognee.add(pdf_bytes, dataset_name="pdf_docs")

            # 2. COGNIFY: Build knowledge graph
            await cognee.cognify()

            # 3. LOAD/SEARCH: Query the knowledge
            results = await cognee.search(
                query_text="What are the main concepts?",
                query_type=SearchType.GRAPH_COMPLETION
            )

            return results
        ```

        ### Six Search Types

        ```python
        from cognee.api.v1.search import SearchType

        # 1. CHUNKS - Raw text chunk retrieval
        results = await cognee.search(query, query_type=SearchType.CHUNKS)

        # 2. INSIGHTS - Extracted insights from processing
        results = await cognee.search(query, query_type=SearchType.INSIGHTS)

        # 3. GRAPH_COMPLETION - Knowledge graph traversal
        results = await cognee.search(query, query_type=SearchType.GRAPH_COMPLETION)

        # 4. CODE - Code-specific search
        results = await cognee.search(query, query_type=SearchType.CODE)

        # 5. CYPHER - Direct graph queries
        results = await cognee.search(
            "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 10",
            query_type=SearchType.CYPHER
        )

        # 6. SUMMARIES - Document summaries
        results = await cognee.search(query, query_type=SearchType.SUMMARIES)
        ```

        ### Three Knowledge Layers

        1. **Raw Nodes**: Original document chunks
        2. **Extracted Entities**: Named entities, concepts
        3. **Relationship Mappings**: Connections between entities
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 3. CocoIndex: Declarative Document Indexing

        CocoIndex provides a flow-based architecture for building semantic search pipelines.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ### Core Pattern: Flow Definition

        ```python
        import cocoindex
        import cocoindex.targets.lancedb as coco_lancedb
        import datetime

        # Reusable transform for embeddings
        @cocoindex.transform_flow()
        def text_to_embedding(text: cocoindex.DataSlice[str]) -> cocoindex.DataSlice[list[float]]:
            return text.transform(
                cocoindex.functions.SentenceTransformerEmbed(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
            )

        # Flow definition
        @cocoindex.flow_def(name="DocumentSearch")
        def document_search_flow(flow_builder, data_scope):
            # 1. SOURCE: Load documents
            data_scope["documents"] = flow_builder.add_source(
                cocoindex.sources.LocalFile(path="./docs"),
                refresh_interval=datetime.timedelta(seconds=30),
            )

            # 2. COLLECT: Create output collector
            doc_embeddings = data_scope.add_collector()

            # 3. TRANSFORM: Process documents
            with data_scope["documents"].row() as doc:
                # Recursive chunking
                doc["chunks"] = doc["content"].transform(
                    cocoindex.functions.SplitRecursively(),
                    language="markdown",
                    chunk_size=500,
                    chunk_overlap=100,
                )

                with doc["chunks"].row() as chunk:
                    # Generate embeddings
                    chunk["embedding"] = text_to_embedding(chunk["text"])

                    # Collect results
                    doc_embeddings.collect(
                        id=cocoindex.GeneratedField.UUID,
                        filename=doc["filename"],
                        text=chunk["text"],
                        embedding=chunk["embedding"],
                    )

            # 4. EXPORT: Store in LanceDB
            doc_embeddings.export(
                "embeddings",
                coco_lancedb.LanceDB(db_uri="./lancedb", table_name="docs"),
                primary_key_fields=["id"],
            )

        # Query handler
        @document_search_flow.query_handler()
        async def search(query: str) -> cocoindex.QueryOutput:
            db = await coco_lancedb.connect_async("./lancedb")
            table = await db.open_table("docs")

            # Reuse same embedding transform
            query_embedding = await text_to_embedding.eval_async(query)

            results = await table.search(query_embedding).limit(10).to_list()
            return cocoindex.QueryOutput(results=[...])
        ```

        ### Multi-Target Export (Vector + Graph)

        ```python
        # Export to LanceDB for vector search
        embeddings.export(
            "vector_index",
            coco_lancedb.LanceDB(db_uri="./lancedb", table_name="docs"),
            primary_key_fields=["id"],
        )

        # Export to Neo4j for graph queries
        entity_relationships.export(
            "graph_relationships",
            cocoindex.targets.Neo4j(
                connection=neo4j_conn,
                mapping=cocoindex.targets.Relationships(
                    rel_type="RELATES_TO",
                    source=cocoindex.targets.NodeFromFields(label="Entity", ...),
                    target=cocoindex.targets.NodeFromFields(label="Entity", ...),
                ),
            ),
            primary_key_fields=["id"],
        )
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 4. ChunkHound: Code-Aware Search

        ChunkHound uses Carnegie Mellon's cAST algorithm for structure-aware code chunking.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ### Core Pattern: cAST Chunking

        ```python
        # cAST Algorithm (Chunking via Abstract Syntax Trees)
        # Uses tree-sitter for 29+ language support

        # Key characteristics:
        # - Max chunk size: 1200 characters
        # - Respects syntax boundaries (functions, classes, blocks)
        # - Preserves semantic context

        # Example: Python function gets chunked as a unit
        '''
        def calculate_metrics(data: dict) -> dict:
            """Calculate various metrics from data."""
            total = sum(data.values())
            avg = total / len(data)
            return {"total": total, "avg": avg}
        '''
        # → Single chunk (within 1200 char limit)

        # Large function → Multiple chunks at logical boundaries
        ```

        ### Hybrid Search Pattern

        ```python
        from chunkhound import ChunkHound

        # Initialize with DuckDB backend
        hound = ChunkHound(
            index_path="./chunkhound_index",
            vector_store="duckdb",  # or "lancedb"
            embedding_model="text-embedding-3-small"
        )

        # Index a codebase
        hound.index_directory(
            path="./my_project",
            languages=["python", "typescript", "rust"],
            exclude_patterns=["**/node_modules/**", "**/.git/**"]
        )

        # 1. SEMANTIC SEARCH - Natural language queries
        results = hound.search(
            "function that handles user authentication",
            search_type="semantic",
            top_k=10
        )

        # 2. REGEX SEARCH - Exact pattern matching (zero API cost)
        results = hound.search(
            r"def\s+authenticate\w*\(",
            search_type="regex"
        )

        # 3. HYBRID SEARCH - Combined approach
        results = hound.search(
            "authentication logic",
            search_type="hybrid",
            semantic_weight=0.7,
            regex_pattern=r"auth|login|session"
        )
        ```

        ### Multi-Hop Exploration

        ```python
        # BFS traversal for architectural understanding
        exploration = hound.explore(
            start_query="main entry point",
            max_hops=4,
            relationship_types=["imports", "calls", "inherits"]
        )

        # Returns connected code elements
        for hop, nodes in exploration.items():
            print(f"Hop {hop}: {len(nodes)} related elements")
            for node in nodes:
                print(f"  - {node.file}:{node.line} - {node.type}")
        ```

        ### MCP Integration

        ChunkHound integrates with Claude Desktop and VS Code via MCP:

        ```json
        // claude_desktop_config.json
        {
            "mcpServers": {
                "chunkhound": {
                    "command": "chunkhound",
                    "args": ["mcp", "--index", "/path/to/index"],
                    "env": {
                        "OPENAI_API_KEY": "..."
                    }
                }
            }
        }
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 5. Feature Comparison Matrix
        """
    )
    return


@app.cell
def _(mo):
    import pandas as pd

    comparison_data = {
        "Feature": [
            "Primary Use Case",
            "Chunking Strategy",
            "Vector Storage",
            "Graph Storage",
            "Search Types",
            "LLM Integration",
            "Incremental Updates",
            "Multi-language Support",
            "MCP Integration",
            "S3/R2 Support",
            "Query Complexity",
            "Setup Complexity",
        ],
        "Cognee": [
            "AI Agent Memory",
            "Automatic",
            "LanceDB, Qdrant, PGVector, Weaviate",
            "KuzuDB, Neo4j, Memgraph, Neptune",
            "6 types (chunks, insights, graph, code, cypher, summaries)",
            "Built-in (extraction, cognify)",
            "Automatic on cognify()",
            "Natural language only",
            "No",
            "Yes (via vector DB)",
            "High (multi-hop, graph queries)",
            "Low (simple API)",
        ],
        "CocoIndex": [
            "Document Search/RAG",
            "Configurable Recursive",
            "LanceDB, PostgreSQL, Qdrant",
            "Neo4j",
            "Custom query handlers",
            "Optional (ExtractByLlm)",
            "FlowLiveUpdater",
            "Markdown, code (via tree-sitter)",
            "No (but FastAPI export)",
            "Yes (AmazonS3 source)",
            "Medium (flow-based)",
            "Medium (flow definitions)",
        ],
        "ChunkHound": [
            "Code Exploration",
            "cAST (syntax-aware)",
            "DuckDB, LanceDB",
            "N/A",
            "Semantic, Regex, Hybrid",
            "Optional (embeddings only)",
            "Manual reindex",
            "29+ programming languages",
            "Yes (Claude, VS Code, Cursor)",
            "No",
            "Low (search-focused)",
            "Low (CLI-based)",
        ],
    }

    df = pd.DataFrame(comparison_data)
    mo.ui.table(df, selection=None)
    return pd, comparison_data, df


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 6. When to Use Each Tool

        ### Use **Cognee** when you need:
        - 🧠 Persistent memory for AI agents across conversations
        - 🔗 Knowledge graph construction with entity relationships
        - 🔍 Multi-type search (chunks, insights, graph completion)
        - 💬 Conversational AI with context retention
        - 📊 Automatic knowledge extraction from documents

        ### Use **CocoIndex** when you need:
        - 📄 Document indexing for RAG applications
        - 🔄 Continuous index updates with source changes
        - 🎯 Custom query handlers for specific search patterns
        - 🗃️ Multi-target export (vector + graph)
        - ⚙️ Declarative, flow-based pipeline definitions

        ### Use **ChunkHound** when you need:
        - 💻 Code search and exploration
        - 🌳 Syntax-aware chunking for 29+ languages
        - 🔎 Hybrid search (semantic + exact regex)
        - 🗺️ Multi-hop code navigation
        - 🤖 MCP integration with AI assistants
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 7. Integration Example: Combined Pipeline

        A comprehensive document indexing pipeline might use multiple tools:
        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
        ```python
        # Combined Pipeline: URL → Crawl → Index → Search

        import asyncio
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        import cognee
        import cocoindex

        async def build_knowledge_pipeline(urls: list[str]):
            '''
            Pipeline combining Crawl4AI + Cognee + CocoIndex:

            1. Crawl4AI: Fetch and extract content from URLs
            2. Cognee: Build knowledge graph for entity relationships
            3. CocoIndex: Create searchable document index
            '''

            # Step 1: Crawl URLs with Crawl4AI
            async with AsyncWebCrawler() as crawler:
                crawl_results = []
                for url in urls:
                    result = await crawler.arun(url=url)
                    if result.success:
                        crawl_results.append({
                            "url": url,
                            "content": result.markdown,
                            "links": result.links
                        })

            # Step 2: Build Knowledge Graph with Cognee
            for doc in crawl_results:
                await cognee.add(
                    doc["content"],
                    dataset_name="web_knowledge",
                    metadata={"url": doc["url"]}
                )

            await cognee.cognify()  # Build graph relationships

            # Step 3: Index for Search with CocoIndex
            # (Assuming CocoIndex flow is defined separately)
            # cocoindex.update("document_search_flow")

            # Search across both systems
            async def hybrid_search(query: str):
                # Graph-based search via Cognee
                graph_results = await cognee.search(
                    query,
                    query_type=SearchType.GRAPH_COMPLETION
                )

                # Vector search via CocoIndex
                vector_results = await semantic_search(query)

                return {
                    "graph": graph_results,
                    "vector": vector_results.results
                }

            return hybrid_search


        # Usage
        urls = [
            "https://docs.anthropic.com/en/docs/",
            "https://python.langchain.com/docs/",
        ]

        search_fn = asyncio.run(build_knowledge_pipeline(urls))
        results = asyncio.run(search_fn("How to use function calling?"))
        ```
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 8. Performance Characteristics
        """
    )
    return


@app.cell
def _(mo, pd):
    perf_data = {
        "Metric": [
            "Index Time (1000 docs)",
            "Query Latency (p50)",
            "Query Latency (p99)",
            "Memory Usage",
            "Storage Efficiency",
            "Incremental Update",
        ],
        "Cognee": [
            "~5-10 min (with cognify)",
            "~100-500ms",
            "~1-2s",
            "High (graph + vectors)",
            "Medium",
            "Full recognify",
        ],
        "CocoIndex": [
            "~2-5 min",
            "~10-50ms",
            "~100-200ms",
            "Medium (vectors only)",
            "High (columnar)",
            "Incremental",
        ],
        "ChunkHound": [
            "~1-3 min",
            "~5-10ms",
            "~50-100ms",
            "Low (DuckDB)",
            "High",
            "Manual reindex",
        ],
    }

    perf_df = pd.DataFrame(perf_data)
    mo.ui.table(perf_df, selection=None)
    return perf_data, perf_df


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## 9. Visualization: Feature Radar Chart
        """
    )
    return


@app.cell
def _(mo, pd):
    import altair as alt
    import numpy as np

    # Feature scores (1-5 scale)
    radar_data = pd.DataFrame({
        "Feature": ["Search Speed", "Graph Queries", "Code Support", "RAG Quality", "Setup Ease", "Incremental Updates"] * 3,
        "Score": [
            # Cognee
            3, 5, 2, 4, 5, 3,
            # CocoIndex
            4, 4, 3, 5, 3, 5,
            # ChunkHound
            5, 1, 5, 3, 4, 2,
        ],
        "Tool": ["Cognee"] * 6 + ["CocoIndex"] * 6 + ["ChunkHound"] * 6
    })

    # Create grouped bar chart (radar alternative for Altair)
    chart = alt.Chart(radar_data).mark_bar().encode(
        x=alt.X('Feature:N', title='Feature', sort=None),
        y=alt.Y('Score:Q', title='Score (1-5)', scale=alt.Scale(domain=[0, 5])),
        color=alt.Color('Tool:N', legend=alt.Legend(title="Tool")),
        xOffset='Tool:N',
        tooltip=['Tool', 'Feature', 'Score']
    ).properties(
        title='Document Indexing Tools: Feature Comparison',
        width=600,
        height=400
    )

    chart
    return alt, np, radar_data, chart


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Summary

        | Scenario | Recommended Tool |
        |----------|-----------------|
        | Building AI agent with persistent memory | **Cognee** |
        | RAG application with document search | **CocoIndex** |
        | Code exploration and understanding | **ChunkHound** |
        | Knowledge graph construction | **Cognee** |
        | Incremental document updates | **CocoIndex** |
        | Hybrid search (semantic + exact) | **ChunkHound** |
        | Multi-modal content (images, PDFs) | **CocoIndex** (with custom ops) |
        | Quick prototyping | **Cognee** (simple API) |
        | Production RAG pipeline | **CocoIndex** (flow-based) |
        | MCP/AI assistant integration | **ChunkHound** |

        All three tools can be combined for comprehensive document intelligence:
        - **Crawl4AI** → Content acquisition
        - **Cognee** → Knowledge graph & entity extraction
        - **CocoIndex** → Document indexing & vector search
        - **ChunkHound** → Code understanding
        """
    )
    return


if __name__ == "__main__":
    app.run()
