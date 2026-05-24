"""Tests for multi-hop research functionality."""

import pytest


@pytest.mark.integration
class TestDeepResearch:
    """Tests for deep_research multi-hop search."""

    async def test_deep_research_basic(self, indexed_analyzer):
        """Test basic deep research query."""
        result = await indexed_analyzer.deep_research(
            "How does the embedding service handle batching?",
            max_sources=5,
            max_iterations=2,
        )

        assert "sources" in result or "results" in result
        assert isinstance(result, dict)

    async def test_deep_research_code_question(self, indexed_analyzer):
        """Test deep research on code-specific question."""
        result = await indexed_analyzer.deep_research(
            "What classes are defined in the codebase?",
            max_sources=10,
            max_iterations=2,
        )

        assert isinstance(result, dict)

    async def test_deep_research_max_sources_limit(self, indexed_analyzer):
        """Test that max_sources is respected."""
        result = await indexed_analyzer.deep_research(
            "Find all functions",
            max_sources=3,
            max_iterations=1,
        )

        if "sources" in result:
            assert len(result["sources"]) <= 3

    async def test_deep_research_convergence(self, indexed_analyzer):
        """Test that research can converge before max iterations."""
        result = await indexed_analyzer.deep_research(
            "What is CodebaseAnalyzer?",
            max_sources=5,
            max_iterations=5,
        )

        # Should return a result regardless of convergence
        assert isinstance(result, dict)


@pytest.mark.integration
class TestResearchQuestions:
    """Tests for specific research questions on códeolas."""

    RESEARCH_QUESTIONS = [
        "How does the cAST algorithm split code into chunks?",
        "What relationship types are defined for the knowledge graph?",
        "How is LanceDB used for vector storage?",
        "What search methods are available?",
    ]

    @pytest.mark.parametrize("question", RESEARCH_QUESTIONS)
    async def test_research_question(self, indexed_analyzer, question):
        """Test research on predefined questions."""
        result = await indexed_analyzer.deep_research(
            question,
            max_sources=5,
            max_iterations=2,
        )

        assert isinstance(result, dict)
        # Should not be empty
        assert len(result) > 0


@pytest.mark.slow
@pytest.mark.integration
class TestResearchOnFullRepo:
    """Tests for research on the full cianfhoghlaim repository."""

    async def test_research_cross_package(self, cianfhoghlaim_path, tmp_path):
        """Test research that spans multiple packages."""
        import os

        os.environ["LANCEDB_URI"] = str(tmp_path / "lancedb")

        from codeolas import CodebaseAnalyzer

        # Index a subset of the repo (just códeolas for speed)
        analyzer = CodebaseAnalyzer(cianfhoghlaim_path / "sruth" / "códeolas")
        await analyzer.index(
            include_patterns=["**/*.py"],
            exclude_patterns=["**/test_*.py", "**/__pycache__/**"],
        )

        result = await analyzer.deep_research(
            "How does the package structure organize code?",
            max_sources=10,
        )

        assert isinstance(result, dict)
