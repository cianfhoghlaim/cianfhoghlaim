"""
CodebaseAnalyzer - Main public API for códeolas.

Provides a unified interface for:
- Code indexing and embedding
- Semantic search and multi-hop research
- Knowledge graph queries
- Documentation generation
"""

import logging
from pathlib import Path
from typing import Any

from sruth.códeolas.core.config import Config, get_config
from sruth.códeolas.core.types import CodeChunk, SearchResult

logger = logging.getLogger(__name__)


class CodebaseAnalyzer:
    """
    Main entry point for code analysis.

    Example:
        >>> analyzer = CodebaseAnalyzer("/path/to/repo")
        >>> await analyzer.index()
        >>> results = await analyzer.search("authentication logic")
        >>> graph = await analyzer.get_code_graph()

    Critical Constraints:
        - Embeddings are batched (minimum 100) for 100x performance
        - HNSW indexes are dropped for bulk inserts >50 rows
        - DuckDB access must be single-threaded
    """

    def __init__(
        self,
        repo_path: str | Path | None = None,
        config: Config | None = None,
    ):
        """
        Initialize the analyzer.

        Args:
            repo_path: Path to repository to analyze (overrides config)
            config: Optional configuration object
        """
        self.config = config or get_config()

        if repo_path:
            self.repo_path = Path(repo_path)
        else:
            self.repo_path = Path(self.config.repo_path)

        self._lance_catalog = None
        self._embedding_service = None
        self._memgraph_client = None
        self._indexed = False

    @property
    def lance_catalog(self):
        """Get LanceDB catalog (lazy initialization)."""
        if self._lance_catalog is None:
            from sruth.códeolas.storage.lance import LanceCatalog, LanceCatalogConfig

            config = LanceCatalogConfig(
                uri=self.config.lancedb_uri,
                table_prefix=self.config.lancedb_table_prefix,
                default_model=self.config.embedding_model,
                default_dimension=self.config.embedding_dimension,
                hnsw_num_partitions=self.config.hnsw_num_partitions,
                hnsw_num_sub_vectors=self.config.hnsw_num_sub_vectors,
                hnsw_drop_threshold=self.config.hnsw_drop_threshold,
                min_batch_size=self.config.min_batch_size,
                max_batch_size=self.config.max_batch_size,
            )
            self._lance_catalog = LanceCatalog(config)

        return self._lance_catalog

    @property
    def embedding_service(self):
        """Get embedding service (lazy initialization)."""
        if self._embedding_service is None:
            from sruth.códeolas.core.embeddings import EmbeddingService

            self._embedding_service = EmbeddingService(
                model_name=self.config.embedding_model,
            )

        return self._embedding_service

    # =========================================================================
    # Indexing
    # =========================================================================

    async def index(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Index the repository.

        Args:
            include_patterns: Glob patterns for files to include
            exclude_patterns: Glob patterns for files to exclude
            force: Force re-index even if already indexed

        Returns:
            Statistics about the indexing operation
        """
        import glob

        include_patterns = include_patterns or self.config.include_patterns
        exclude_patterns = exclude_patterns or self.config.exclude_patterns

        logger.info(f"Indexing repository: {self.repo_path}")

        # Collect files
        files: set[Path] = set()
        for pattern in include_patterns:
            matched = glob.glob(str(self.repo_path / pattern), recursive=True)
            files.update(Path(f) for f in matched if Path(f).is_file())

        # Apply exclusions
        for pattern in exclude_patterns:
            excluded = glob.glob(str(self.repo_path / pattern), recursive=True)
            files -= set(Path(f) for f in excluded)

        logger.info(f"Found {len(files)} files to index")

        # Chunk files
        from sruth.códeolas.core.chunking import chunk_code_file

        all_chunks: list[CodeChunk] = []
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                chunks = chunk_code_file(content, str(file_path))
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Failed to process {file_path}: {e}")

        logger.info(f"Created {len(all_chunks)} chunks")

        # Generate embeddings
        if all_chunks:
            texts = [chunk.text for chunk in all_chunks]
            embeddings = self.embedding_service.embed_batch(texts)

            # Store in LanceDB
            from sruth.códeolas.storage.lance import CodeChunk as StorageChunk

            storage_chunks = []
            for chunk, embedding in zip(all_chunks, embeddings):
                storage_chunks.append(
                    StorageChunk(
                        id=f"{chunk.file_path}:{chunk.start_line}:{chunk.name or 'chunk'}",
                        file_path=chunk.file_path,
                        language=chunk.language,
                        chunk_type=chunk.chunk_type.value,
                        name=chunk.name,
                        start_line=chunk.start_line,
                        end_line=chunk.end_line,
                        text=chunk.text,
                        vector=embedding,
                    )
                )

            self.lance_catalog.add_code_chunks(storage_chunks)

        self._indexed = True

        return {
            "files_indexed": len(files),
            "chunks_created": len(all_chunks),
            "repo_path": str(self.repo_path),
        }

    # =========================================================================
    # Search
    # =========================================================================

    async def search(
        self,
        query: str,
        limit: int | None = None,
        language: str | None = None,
        chunk_type: str | None = None,
        rerank: bool = True,
    ) -> list[SearchResult]:
        """
        Semantic search for code.

        Args:
            query: Natural language query
            limit: Maximum results to return
            language: Filter by programming language
            chunk_type: Filter by chunk type (function, class, etc.)
            rerank: Whether to rerank results

        Returns:
            List of SearchResult objects
        """
        limit = limit or self.config.default_search_limit

        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)

        # Search LanceDB
        results = self.lance_catalog.search_code(
            query_vector=query_embedding,
            limit=limit * 2 if rerank else limit,  # Get more for reranking
            language=language,
            chunk_type=chunk_type,
        )

        # Convert to SearchResult objects
        search_results = []
        for result in results:
            chunk = CodeChunk(
                text=result.get("text", ""),
                chunk_type=result.get("chunk_type", "other"),
                name=result.get("name"),
                file_path=result.get("file_path", ""),
                language=result.get("language", ""),
                start_line=result.get("start_line", 0),
                end_line=result.get("end_line", 0),
            )
            search_results.append(
                SearchResult(
                    chunk=chunk,
                    score=1.0 - result.get("_distance", 0),
                    distance=result.get("_distance"),
                )
            )

        # Optionally rerank
        if rerank and self.config.rerank_provider != "none":
            search_results = await self._rerank_results(query, search_results, limit)

        return search_results[:limit]

    async def _rerank_results(
        self,
        query: str,
        results: list[SearchResult],
        top_n: int,
    ) -> list[SearchResult]:
        """Rerank search results using external API."""
        try:
            from sruth.códeolas.search.reranker import rerank_results

            return await rerank_results(
                query=query,
                results=results,
                provider=self.config.rerank_provider,
                api_key=self.config.rerank_api_key,
                model=self.config.rerank_model,
                top_n=top_n,
            )
        except Exception as e:
            logger.warning(f"Reranking failed, using original order: {e}")
            return results

    async def search_regex(
        self,
        pattern: str,
        limit: int | None = None,
        language: str | None = None,
    ) -> list[dict]:
        """
        Pattern-based code search.

        Args:
            pattern: Regex pattern to search for
            limit: Maximum results
            language: Filter by language

        Returns:
            List of matching results with file paths and line numbers
        """
        import re

        limit = limit or self.config.default_search_limit
        results = []

        # Search through indexed chunks
        table = self.lance_catalog.get_table("code_chunks")
        if table is None:
            return []

        # Get all chunks (or filtered by language)
        search = table.search()
        if language:
            search = search.where(f"language = '{language}'")

        df = search.to_pandas()

        regex = re.compile(pattern, re.MULTILINE)
        for _, row in df.iterrows():
            matches = regex.findall(row["text"])
            if matches:
                results.append(
                    {
                        "file_path": row["file_path"],
                        "start_line": row["start_line"],
                        "end_line": row["end_line"],
                        "matches": matches,
                        "text": row["text"][:500],  # Preview
                    }
                )
                if len(results) >= limit:
                    break

        return results

    async def deep_research(
        self,
        question: str,
        max_sources: int = 15,
        max_iterations: int | None = None,
    ) -> dict[str, Any]:
        """
        Multi-hop semantic search for complex questions.

        Iteratively searches and refines until convergence or max iterations.

        Args:
            question: Research question
            max_sources: Maximum sources to include
            max_iterations: Maximum search iterations

        Returns:
            Research results with sources and synthesis
        """
        from sruth.códeolas.search.multihop import multihop_search

        max_iterations = max_iterations or self.config.multihop_max_iterations

        return await multihop_search(
            analyzer=self,
            question=question,
            max_sources=max_sources,
            max_iterations=max_iterations,
            convergence_threshold=self.config.multihop_convergence_threshold,
        )

    # =========================================================================
    # Graph Operations
    # =========================================================================

    async def get_code_graph(self) -> dict[str, Any]:
        """
        Get the code knowledge graph.

        Returns:
            Dictionary with nodes and edges
        """
        # Placeholder for graph operations
        return {
            "nodes": [],
            "edges": [],
            "stats": {},
        }

    async def find_callers(self, function_name: str) -> list[dict]:
        """Find all callers of a function."""
        if self._memgraph_client is None:
            return []
        return self._memgraph_client.find_callers(function_name)

    async def get_dependencies(self, file_path: str) -> list[dict]:
        """Get dependencies of a file."""
        if self._memgraph_client is None:
            return []
        return self._memgraph_client.find_dependencies(file_path)

    # =========================================================================
    # Documentation Generation
    # =========================================================================

    async def generate_arch_doc(self, output_path: str | None = None) -> str:
        """
        Generate .arch.md architecture documentation.

        Args:
            output_path: Optional path to write the document

        Returns:
            Generated markdown content
        """
        from sruth.códeolas.generators.arch import ArchGenerator

        generator = ArchGenerator(self.repo_path)
        content = await generator.generate()

        if output_path:
            Path(output_path).write_text(content)

        return content

    async def generate_changelog(
        self,
        from_tag: str | None = None,
        to_tag: str | None = None,
    ) -> str:
        """
        Generate changelog from git history.

        Args:
            from_tag: Starting tag/commit
            to_tag: Ending tag/commit (default: HEAD)

        Returns:
            Generated changelog markdown
        """
        from sruth.códeolas.generators.changelog import ChangelogGenerator

        generator = ChangelogGenerator(self.repo_path)
        return await generator.generate(from_tag=from_tag, to_tag=to_tag)

    async def check_doc_drift(self) -> list[dict]:
        """
        Check for documentation drift (docs out of sync with code).

        Returns:
            List of detected drift issues
        """
        # Placeholder for doc drift detection
        return []

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> dict[str, Any]:
        """Get indexing statistics."""
        lance_stats = self.lance_catalog.get_stats()

        return {
            "repo_path": str(self.repo_path),
            "indexed": self._indexed,
            "lance": lance_stats,
        }
