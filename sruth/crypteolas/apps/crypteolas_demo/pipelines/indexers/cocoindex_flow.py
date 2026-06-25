"""
CocoIndex flow for crypto documentation processing.

Provides semantic chunking and embedding for:
- Protocol documentation
- Research papers
- API specifications
- Governance proposals

Uses syntax-aware splitting and generates embeddings
for vector search in LanceDB.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Optional

import cocoindex
from cocoindex import FlowBuilder, op
from cocoindex.sources import LocalDirectory, CustomSource


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class CryptoDocument:
    """Crypto documentation document."""

    id: str
    url: str
    title: str
    content: str
    protocol: str
    doc_type: str  # docs, whitepaper, governance, api
    metadata: dict = field(default_factory=dict)
    scraped_at: Optional[datetime] = None


@dataclass
class CryptoChunk:
    """Chunked crypto document for embedding."""

    chunk_id: str
    document_id: str
    content: str
    chunk_index: int
    protocol: str
    doc_type: str
    embedding: Optional[list[float]] = None
    metadata: dict = field(default_factory=dict)


# =============================================================================
# Custom Sources
# =============================================================================


class DuckDBSource(CustomSource):
    """
    CocoIndex source reading from DuckDB.

    Reads scraped documents from Firecrawl pipeline output.
    """

    def __init__(
        self,
        db_path: str,
        table_name: str = "firecrawl_crawl",
        protocol_filter: Optional[str] = None,
    ):
        self.db_path = db_path
        self.table_name = table_name
        self.protocol_filter = protocol_filter

    def read(self) -> Iterator[CryptoDocument]:
        """Read documents from DuckDB."""
        import duckdb

        con = duckdb.connect(self.db_path)

        query = f"""
            SELECT
                url,
                title,
                markdown as content,
                metadata,
                start_url,
                scraped_at
            FROM {self.table_name}
            WHERE markdown IS NOT NULL
        """

        if self.protocol_filter:
            query += f" AND start_url LIKE '%{self.protocol_filter}%'"

        results = con.execute(query).fetchall()

        for row in results:
            url, title, content, metadata, start_url, scraped_at = row

            # Determine protocol from URL
            protocol = _extract_protocol(start_url)
            doc_type = _classify_doc_type(url, content)

            doc_id = hashlib.md5(url.encode()).hexdigest()

            yield CryptoDocument(
                id=doc_id,
                url=url,
                title=title or "",
                content=content,
                protocol=protocol,
                doc_type=doc_type,
                metadata=metadata or {},
                scraped_at=scraped_at,
            )

        con.close()


class R2Source(CustomSource):
    """
    CocoIndex source reading from Cloudflare R2.

    For documents uploaded via Firecrawl pipeline.
    """

    def __init__(
        self,
        bucket: str,
        prefix: str = "crypto-docs",
        credentials: Optional[dict] = None,
    ):
        self.bucket = bucket
        self.prefix = prefix
        self.credentials = credentials

    def read(self) -> Iterator[CryptoDocument]:
        """Read documents from R2."""
        import boto3
        import json
        import os

        creds = self.credentials or {
            "endpoint_url": os.environ.get("R2_ENDPOINT_URL"),
            "aws_access_key_id": os.environ.get("R2_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("R2_SECRET_ACCESS_KEY"),
        }

        s3 = boto3.client("s3", **creds)

        paginator = s3.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]

                if not key.endswith(".json"):
                    continue

                response = s3.get_object(Bucket=self.bucket, Key=key)
                data = json.loads(response["Body"].read())

                url = data.get("url", "")
                content = data.get("markdown", "")

                if not content:
                    continue

                protocol = _extract_protocol(data.get("start_url", url))
                doc_type = _classify_doc_type(url, content)

                yield CryptoDocument(
                    id=hashlib.md5(url.encode()).hexdigest(),
                    url=url,
                    title=data.get("title", ""),
                    content=content,
                    protocol=protocol,
                    doc_type=doc_type,
                    metadata=data.get("metadata", {}),
                    scraped_at=data.get("scraped_at"),
                )


# =============================================================================
# Processing Operators
# =============================================================================


@op.map
def chunk_document(doc: CryptoDocument) -> list[CryptoChunk]:
    """
    Chunk document using semantic splitting.

    Uses markdown-aware splitting for better context preservation.
    """
    from langchain_text_splitters import MarkdownHeaderTextSplitter

    # Define markdown headers to split on
    headers_to_split = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
        ("####", "h4"),
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split,
        strip_headers=False,
    )

    # Split by headers first
    header_splits = splitter.split_text(doc.content)

    # Further split large sections
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = []
    chunk_index = 0

    for split in header_splits:
        # Get section content
        content = split.page_content if hasattr(split, "page_content") else str(split)
        header_meta = split.metadata if hasattr(split, "metadata") else {}

        # Split if too large
        if len(content) > 1000:
            sub_chunks = text_splitter.split_text(content)
        else:
            sub_chunks = [content]

        for sub_content in sub_chunks:
            chunk_id = f"{doc.id}_{chunk_index}"

            chunks.append(
                CryptoChunk(
                    chunk_id=chunk_id,
                    document_id=doc.id,
                    content=sub_content,
                    chunk_index=chunk_index,
                    protocol=doc.protocol,
                    doc_type=doc.doc_type,
                    metadata={
                        **doc.metadata,
                        **header_meta,
                        "url": doc.url,
                        "title": doc.title,
                    },
                )
            )
            chunk_index += 1

    return chunks


@op.map
def embed_chunk(chunk: CryptoChunk) -> CryptoChunk:
    """
    Generate embedding for chunk.

    Uses sentence-transformers for local embedding generation.
    """
    from sentence_transformers import SentenceTransformer

    # Use cached model
    model = _get_embedding_model()

    embedding = model.encode(chunk.content).tolist()
    chunk.embedding = embedding

    return chunk


# Model cache
_embedding_model = None


def _get_embedding_model():
    """Get or create cached embedding model."""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer

        _embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _embedding_model


# =============================================================================
# Flow Definition
# =============================================================================


class CryptoDocumentFlow:
    """
    CocoIndex flow for processing crypto documentation.

    Pipeline:
    1. Read documents from source (DuckDB, R2, or local)
    2. Chunk using markdown-aware splitting
    3. Generate embeddings
    4. Store in LanceDB for vector search
    """

    def __init__(
        self,
        source_type: str = "duckdb",
        source_config: Optional[dict] = None,
        lancedb_uri: str = "data/crypto_vectors",
        table_name: str = "crypto_docs",
    ):
        self.source_type = source_type
        self.source_config = source_config or {}
        self.lancedb_uri = lancedb_uri
        self.table_name = table_name

        self.flow = self._build_flow()

    def _build_flow(self) -> FlowBuilder:
        """Build CocoIndex flow."""
        flow = FlowBuilder("crypto_docs_flow")

        # Configure source
        if self.source_type == "duckdb":
            source = DuckDBSource(
                db_path=self.source_config.get("db_path", "data/crypto_analytics.duckdb"),
                table_name=self.source_config.get("table_name", "firecrawl_crawl"),
            )
        elif self.source_type == "r2":
            source = R2Source(
                bucket=self.source_config.get("bucket", "crypto-docs"),
                prefix=self.source_config.get("prefix", "crypto-docs"),
            )
        elif self.source_type == "local":
            source = LocalDirectory(
                path=self.source_config.get("path", "data/docs"),
                glob_pattern=self.source_config.get("pattern", "**/*.md"),
            )
        else:
            raise ValueError(f"Unknown source type: {self.source_type}")

        # Build pipeline
        flow.source(source)
        flow.map(chunk_document)
        flow.map(embed_chunk)

        # Configure LanceDB sink
        flow.sink(
            "lancedb",
            uri=self.lancedb_uri,
            table=self.table_name,
            schema={
                "chunk_id": "string",
                "document_id": "string",
                "content": "string",
                "chunk_index": "int",
                "protocol": "string",
                "doc_type": "string",
                "embedding": "vector[384]",  # MiniLM dimension
                "metadata": "json",
            },
        )

        return flow

    def run(self) -> dict[str, Any]:
        """Execute the flow."""
        return self.flow.run()

    def run_incremental(self, since: Optional[datetime] = None) -> dict[str, Any]:
        """Run incremental update."""
        return self.flow.run(incremental=True, since=since)


# =============================================================================
# Query Functions
# =============================================================================


def query_crypto_knowledge(
    query: str,
    lancedb_uri: str = "data/crypto_vectors",
    table_name: str = "crypto_docs",
    protocol_filter: Optional[str] = None,
    doc_type_filter: Optional[str] = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Query crypto knowledge base using semantic search.

    Args:
        query: Search query
        lancedb_uri: LanceDB path
        table_name: Table name
        protocol_filter: Filter by protocol
        doc_type_filter: Filter by document type
        limit: Max results

    Returns:
        List of matching chunks with scores
    """
    import lancedb

    db = lancedb.connect(lancedb_uri)
    table = db.open_table(table_name)

    # Generate query embedding
    model = _get_embedding_model()
    query_embedding = model.encode(query).tolist()

    # Build search
    search = table.search(query_embedding).limit(limit)

    # Apply filters
    if protocol_filter:
        search = search.where(f"protocol = '{protocol_filter}'")
    if doc_type_filter:
        search = search.where(f"doc_type = '{doc_type_filter}'")

    results = search.to_pandas()

    return results.to_dict(orient="records")


def get_protocol_context(
    protocol: str,
    lancedb_uri: str = "data/crypto_vectors",
    table_name: str = "crypto_docs",
    limit: int = 50,
) -> str:
    """
    Get full context for a protocol.

    Useful for LLM context injection.

    Args:
        protocol: Protocol name
        lancedb_uri: LanceDB path
        table_name: Table name
        limit: Max chunks

    Returns:
        Concatenated context string
    """
    import lancedb

    db = lancedb.connect(lancedb_uri)
    table = db.open_table(table_name)

    # Get all chunks for protocol
    results = (
        table.search()
        .where(f"protocol = '{protocol}'")
        .limit(limit)
        .to_pandas()
    )

    # Sort by chunk index
    results = results.sort_values(["document_id", "chunk_index"])

    # Concatenate content
    context_parts = []
    current_doc = None

    for _, row in results.iterrows():
        if row["document_id"] != current_doc:
            current_doc = row["document_id"]
            title = row.get("metadata", {}).get("title", "")
            if title:
                context_parts.append(f"\n## {title}\n")

        context_parts.append(row["content"])

    return "\n\n".join(context_parts)


# =============================================================================
# Utilities
# =============================================================================


def _extract_protocol(url: str) -> str:
    """Extract protocol name from URL."""
    url_lower = url.lower()

    protocol_patterns = {
        "ethena": ["ethena", "usde"],
        "aave": ["aave"],
        "pendle": ["pendle"],
        "lido": ["lido"],
        "eigenlayer": ["eigenlayer"],
        "curve": ["curve"],
        "uniswap": ["uniswap"],
        "compound": ["compound"],
        "maker": ["maker", "makerdao"],
    }

    for protocol, patterns in protocol_patterns.items():
        if any(p in url_lower for p in patterns):
            return protocol

    return "unknown"


def _classify_doc_type(url: str, content: str) -> str:
    """Classify document type."""
    url_lower = url.lower()
    content_lower = content[:500].lower() if content else ""

    if "api" in url_lower or "reference" in url_lower:
        return "api"
    elif "whitepaper" in url_lower or "whitepaper" in content_lower:
        return "whitepaper"
    elif "governance" in url_lower or "proposal" in url_lower:
        return "governance"
    elif "tutorial" in url_lower or "guide" in url_lower:
        return "tutorial"
    else:
        return "docs"


# =============================================================================
# Pipeline Runner
# =============================================================================


def index_crypto_docs(
    source_type: str = "duckdb",
    source_config: Optional[dict] = None,
    lancedb_uri: str = "data/crypto_vectors",
    incremental: bool = False,
) -> dict[str, Any]:
    """
    Run crypto documentation indexing.

    Args:
        source_type: Source type (duckdb, r2, local)
        source_config: Source configuration
        lancedb_uri: LanceDB storage path
        incremental: Whether to run incremental update

    Returns:
        Flow execution results
    """
    flow = CryptoDocumentFlow(
        source_type=source_type,
        source_config=source_config,
        lancedb_uri=lancedb_uri,
    )

    if incremental:
        return flow.run_incremental()
    else:
        return flow.run()


if __name__ == "__main__":
    # Test indexing from DuckDB
    result = index_crypto_docs(
        source_type="duckdb",
        source_config={
            "db_path": "data/crypto_analytics.duckdb",
            "table_name": "firecrawl_crawl",
        },
    )

    print(f"Indexing result: {result}")

    # Test query
    results = query_crypto_knowledge(
        "How does Ethena generate yield?",
        protocol_filter="ethena",
    )

    for r in results[:3]:
        print(f"\n--- {r.get('protocol')} ---")
        print(r.get("content", "")[:200])
