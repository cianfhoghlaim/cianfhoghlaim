"""Integration tests for códeolas CodebaseAnalyzer."""

import pytest

from codeolas import CodebaseAnalyzer


@pytest.mark.integration
class TestIndexing:
    """Tests for codebase indexing."""

    async def test_index_codebase(self, analyzer):
        """Test indexing the códeolas package itself."""
        stats = await analyzer.index()

        assert stats["files_indexed"] > 0, "Should index at least one file"
        assert stats["chunks_created"] > 0, "Should create at least one chunk"
        assert "repo_path" in stats

    async def test_index_with_patterns(self, analyzer):
        """Test indexing with custom patterns."""
        stats = await analyzer.index(
            include_patterns=["**/*.py"],
            exclude_patterns=["**/test_*.py", "**/__pycache__/**"],
        )

        assert stats["files_indexed"] > 0

    async def test_index_force_reindex(self, analyzer):
        """Test force re-indexing."""
        # First index
        stats1 = await analyzer.index()

        # Force re-index
        stats2 = await analyzer.index(force=True)

        assert stats1["chunks_created"] == stats2["chunks_created"]


@pytest.mark.integration
class TestSearch:
    """Tests for semantic search."""

    async def test_search_semantic(self, indexed_analyzer):
        """Test semantic search on indexed codebase."""
        results = await indexed_analyzer.search("code chunking algorithm")

        assert len(results) > 0, "Should return search results"

    async def test_search_with_limit(self, indexed_analyzer):
        """Test search with result limit."""
        results = await indexed_analyzer.search("function", limit=5)

        assert len(results) <= 5

    async def test_search_with_language_filter(self, indexed_analyzer):
        """Test search filtered by language."""
        results = await indexed_analyzer.search("class", language="python", limit=10)

        for result in results:
            assert result.chunk.language == "python"

    async def test_search_with_chunk_type_filter(self, indexed_analyzer):
        """Test search filtered by chunk type."""
        results = await indexed_analyzer.search("analyzer", chunk_type="class", limit=10)

        for result in results:
            assert result.chunk.chunk_type == "class"

    async def test_search_returns_scores(self, indexed_analyzer):
        """Test that search results have scores."""
        results = await indexed_analyzer.search("embedding", limit=5)

        for result in results:
            assert result.score is not None
            assert 0 <= result.score <= 1


@pytest.mark.integration
class TestRegexSearch:
    """Tests for regex pattern search."""

    async def test_search_regex_function_pattern(self, indexed_analyzer):
        """Test regex search for function definitions."""
        results = await indexed_analyzer.search_regex(r"def\s+\w+\s*\(")

        assert len(results) > 0, "Should find function definitions"

    async def test_search_regex_class_pattern(self, indexed_analyzer):
        """Test regex search for class definitions."""
        results = await indexed_analyzer.search_regex(r"class\s+\w+")

        assert len(results) > 0, "Should find class definitions"

    async def test_search_regex_with_language_filter(self, indexed_analyzer):
        """Test regex search with language filter."""
        results = await indexed_analyzer.search_regex(
            r"async\s+def",
            language="python",
            limit=10,
        )

        for result in results:
            assert "async def" in result["text"] or "async def" in str(result.get("matches", []))


@pytest.mark.integration
class TestStats:
    """Tests for analyzer statistics."""

    async def test_get_stats_before_index(self, analyzer):
        """Test getting stats before indexing."""
        stats = analyzer.get_stats()

        assert "repo_path" in stats
        assert stats["indexed"] is False

    async def test_get_stats_after_index(self, indexed_analyzer):
        """Test getting stats after indexing."""
        stats = indexed_analyzer.get_stats()

        assert stats["indexed"] is True
        assert "lance" in stats
