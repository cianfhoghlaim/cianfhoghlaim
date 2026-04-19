"""Code Indexing Flow with CocoIndex.

Implements semantic code indexing using CocoIndex with:
- Tree-sitter aware chunking
- SentenceTransformer embeddings
- LanceDB vector storage

Reference: multi_github_code_indexing example from CocoIndex
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from cocoindex.config import CodeIndexingConfig
from cocoindex.embeddings import generate_embedding, EmbeddingFunction

# Check if cocoindex is available
try:
    import cocoindex
    HAS_COCOINDEX = True
except ImportError:
    HAS_COCOINDEX = False


@dataclass
class CodeChunk:
    """Represents a chunk of code with metadata."""
    filename: str
    location: str
    code: str
    start: int
    end: int
    language: str
    embedding: list[float] | None = None


class CodeIndexingFlow:
    """Code indexing flow manager.

    Handles indexing code from local directories or GitHub repositories
    into LanceDB for semantic search.

    This is a simplified implementation that works without the full CocoIndex
    infrastructure, suitable for local development and prototyping.
    """

    def __init__(self, config: CodeIndexingConfig):
        self.config = config
        self._db = None
        self._table = None
        self._embedding_fn = EmbeddingFunction(config.embedding_model)

    @property
    def db(self):
        """Lazy-load LanceDB connection."""
        if self._db is None:
            import lancedb
            os.makedirs(Path(self.config.lancedb_uri).parent, exist_ok=True)
            self._db = lancedb.connect(self.config.lancedb_uri)
        return self._db

    @property
    def table_name(self) -> str:
        return self.config.table_name

    def _get_file_extension(self, filename: str) -> str:
        """Extract file extension."""
        return Path(filename).suffix.lstrip(".")

    def _should_include_file(self, filepath: str) -> bool:
        """Check if file should be included based on patterns."""
        from fnmatch import fnmatch

        # Check exclusion patterns
        for pattern in self.config.excluded_patterns:
            if fnmatch(filepath, pattern):
                return False

        # Check inclusion patterns
        for pattern in self.config.included_patterns:
            if fnmatch(filepath, pattern):
                return True

        return False

    def _split_code(self, content: str, language: str) -> Iterator[dict[str, Any]]:
        """Split code into chunks.

        Uses a simple recursive splitting strategy.
        For production, CocoIndex provides tree-sitter aware splitting.
        """
        chunk_size = self.config.chunk_size
        overlap = self.config.chunk_overlap
        min_size = self.config.min_chunk_size

        if len(content) <= chunk_size:
            yield {
                "text": content,
                "start": 0,
                "end": len(content),
                "location": "0:0",
            }
            return

        # Simple character-based splitting with overlap
        start = 0
        chunk_num = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))

            # Try to find a good break point (newline)
            if end < len(content):
                # Look for newline within last 20% of chunk
                search_start = start + int(chunk_size * 0.8)
                newline_pos = content.rfind("\n", search_start, end)
                if newline_pos > start:
                    end = newline_pos + 1

            chunk_text = content[start:end]

            if len(chunk_text) >= min_size:
                yield {
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "location": f"{chunk_num}:{start}",
                }
                chunk_num += 1

            # Move start with overlap
            start = end - overlap if end < len(content) else end

    def index_directory(self, directory: str | Path) -> int:
        """Index all matching files in a directory.

        Args:
            directory: Path to directory to index

        Returns:
            Number of chunks indexed
        """
        directory = Path(directory)
        chunks = []

        for filepath in directory.rglob("*"):
            if not filepath.is_file():
                continue

            rel_path = str(filepath.relative_to(directory))
            if not self._should_include_file(rel_path):
                continue

            try:
                content = filepath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, IOError):
                continue

            extension = self._get_file_extension(filepath.name)

            for chunk_data in self._split_code(content, extension):
                chunk = {
                    "filename": rel_path,
                    "location": chunk_data["location"],
                    "code": chunk_data["text"],
                    "start": chunk_data["start"],
                    "end": chunk_data["end"],
                    "language": extension,
                }
                chunks.append(chunk)

        if not chunks:
            return 0

        # Generate embeddings in batch
        texts = [c["code"] for c in chunks]
        embeddings = self._embedding_fn(texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding

        # Create or update LanceDB table
        self._create_or_update_table(chunks)

        return len(chunks)

    def _create_or_update_table(self, chunks: list[dict[str, Any]]):
        """Create or update the LanceDB table."""
        import pyarrow as pa

        # Convert to PyArrow table
        data = {
            "filename": [c["filename"] for c in chunks],
            "location": [c["location"] for c in chunks],
            "code": [c["code"] for c in chunks],
            "start": [c["start"] for c in chunks],
            "end": [c["end"] for c in chunks],
            "language": [c["language"] for c in chunks],
            "embedding": [c["embedding"] for c in chunks],
        }

        # Check if table exists
        existing_tables = self.db.table_names()
        if self.table_name in existing_tables:
            table = self.db.open_table(self.table_name)
            table.add(data)
        else:
            self.db.create_table(self.table_name, data)

    def search(
        self,
        query: str,
        limit: int = 10,
        filter_language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for code similar to the query.

        Args:
            query: Search query
            limit: Maximum results to return
            filter_language: Optional language filter

        Returns:
            List of matching code chunks with scores
        """
        query_embedding = self._embedding_fn.embed_query(query)

        table = self.db.open_table(self.table_name)

        # Build search query
        search = table.search(query_embedding).limit(limit)

        if filter_language:
            search = search.where(f"language = '{filter_language}'")

        results = search.to_list()

        return [
            {
                "filename": r["filename"],
                "location": r["location"],
                "code": r["code"],
                "language": r["language"],
                "score": 1.0 - r.get("_distance", 0),  # Convert distance to score
            }
            for r in results
        ]


def build_code_indexing_flow(config: CodeIndexingConfig) -> CodeIndexingFlow:
    """Build a code indexing flow from configuration.

    Args:
        config: Code indexing configuration

    Returns:
        CodeIndexingFlow instance
    """
    return CodeIndexingFlow(config)


def run_code_indexing(
    directory: str | Path,
    config: CodeIndexingConfig | None = None,
    **kwargs,
) -> int:
    """Run code indexing on a directory.

    Args:
        directory: Path to directory to index
        config: Optional configuration (will create default if not provided)
        **kwargs: Additional configuration options

    Returns:
        Number of chunks indexed
    """
    if config is None:
        config = CodeIndexingConfig(
            repo_owner=kwargs.get("repo_owner", "local"),
            repo_name=kwargs.get("repo_name", Path(directory).name),
            **{k: v for k, v in kwargs.items() if k not in ["repo_owner", "repo_name"]},
        )

    flow = build_code_indexing_flow(config)
    return flow.index_directory(directory)


# CocoIndex native flow definition (requires cocoindex package)
if HAS_COCOINDEX:
    import cocoindex

    @cocoindex.transform_flow()
    def code_to_embedding_transform(
        text: cocoindex.DataSlice[str],
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> cocoindex.DataSlice[list[float]]:
        """CocoIndex transform for embedding generation."""
        return text.transform(
            cocoindex.functions.SentenceTransformerEmbed(model=model_name)
        )

    def build_cocoindex_flow(config: CodeIndexingConfig):
        """Build a native CocoIndex flow.

        This requires the full CocoIndex infrastructure including:
        - PostgreSQL for metadata
        - GitHub App for authenticated access
        - LanceDB for vector storage
        """
        @cocoindex.flow_def(name=config.flow_name)
        def code_indexing_flow(
            flow_builder: cocoindex.FlowBuilder,
            data_scope: cocoindex.DataScope,
        ):
            # Add GitHub source
            data_scope["files"] = flow_builder.add_source(
                cocoindex.sources.LocalFile(
                    path=f"./{config.repo_owner}/{config.repo_name}",
                    included_patterns=config.included_patterns,
                    excluded_patterns=config.excluded_patterns,
                )
            )

            # Create collector for embeddings
            code_embeddings = data_scope.add_collector()

            # Process files
            with data_scope["files"].row() as file:
                # Extract extension
                file["extension"] = file["filename"].transform(
                    lambda f: Path(f).suffix.lstrip(".")
                )

                # Split into chunks
                file["chunks"] = file["content"].transform(
                    cocoindex.functions.SplitRecursively(),
                    language=file["extension"],
                    chunk_size=config.chunk_size,
                    min_chunk_size=config.min_chunk_size,
                    chunk_overlap=config.chunk_overlap,
                )

                # Process chunks
                with file["chunks"].row() as chunk:
                    chunk["embedding"] = chunk["text"].call(code_to_embedding_transform)

                    code_embeddings.collect(
                        filename=file["filename"],
                        location=chunk["location"],
                        code=chunk["text"],
                        embedding=chunk["embedding"],
                        start=chunk["start"],
                        end=chunk["end"],
                        language=file["extension"],
                    )

            # Export to LanceDB
            code_embeddings.export(
                config.table_name,
                cocoindex.targets.LanceDB(
                    db_uri=config.lancedb_uri,
                    table_name=config.table_name,
                ),
                primary_key_fields=["filename", "location"],
                vector_indexes=[
                    cocoindex.VectorIndexDef(
                        field_name="embedding",
                        metric=cocoindex.VectorSimilarityMetric.COSINE_SIMILARITY,
                    )
                ],
            )

        return code_indexing_flow
