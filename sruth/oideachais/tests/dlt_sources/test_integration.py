"""
Integration tests for DLT data sources.

Tests the full pipeline flow from source to destination,
ensuring data flows correctly through transformations.

Run with: pytest tests/dlt_sources/test_integration.py -m integration
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


# ===========================================================================
# Firecrawl Source Tests
# ===========================================================================


class TestFirecrawlSource:
    """Tests for the shared Firecrawl utilities."""

    def test_scrape_page_no_api_key(self) -> None:
        """Test scrape_page returns client_unavailable when no API key."""
        from oideachais.dlt_sources.common.firecrawl_source import scrape_page

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}, clear=False):
            result = scrape_page("https://example.com")

        assert result["status"] == "client_unavailable"
        assert result["url"] == "https://example.com"
        assert "scraped_at" in result

    def test_scrape_page_with_mock_client(self) -> None:
        """Test scrape_page with mocked Firecrawl client."""
        from oideachais.dlt_sources.common.firecrawl_source import scrape_page

        mock_result = {
            "markdown": "# Test Content",
            "html": "<h1>Test Content</h1>",
            "links": ["https://example.com/page1"],
            "metadata": {
                "sourceURL": "https://example.com",
                "title": "Test Page",
                "description": "A test page",
                "language": "en",
            },
        }

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test_key"}):
            with patch("oideachais.dlt_sources.common.firecrawl_source.get_firecrawl_client") as mock_get:
                mock_client = MagicMock()
                mock_client.scrape_url.return_value = mock_result
                mock_get.return_value = mock_client

                result = scrape_page("https://example.com")

        assert result["status"] == "success"
        assert result["title"] == "Test Page"
        assert result["markdown"] == "# Test Content"

    def test_crawl_website_no_api_key(self) -> None:
        """Test crawl_website returns client_unavailable when no API key."""
        from oideachais.dlt_sources.common.firecrawl_source import crawl_website

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}, clear=False):
            results = list(crawl_website("https://example.com"))

        assert len(results) == 1
        assert results[0]["status"] == "client_unavailable"

    def test_map_urls_no_api_key(self) -> None:
        """Test map_urls returns empty when no API key."""
        from oideachais.dlt_sources.common.firecrawl_source import map_urls

        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}, clear=False):
            results = list(map_urls("https://example.com"))

        assert results == []


# ===========================================================================
# Crawl Utils Tests
# ===========================================================================


class TestCrawlUtils:
    """Tests for crawl utility functions."""

    def test_url_matcher_include_patterns(self) -> None:
        """Test URL matching with include patterns."""
        from oideachais.dlt_sources.crawl_utils import URLMatcher

        matcher = URLMatcher(
            include_patterns=["https://curriculumonline.ie/Junior-Cycle/*"]
        )

        assert matcher.matches("https://curriculumonline.ie/Junior-Cycle/Mathematics")
        assert not matcher.matches("https://curriculumonline.ie/Senior-Cycle/Irish")

    def test_url_matcher_exclude_patterns(self) -> None:
        """Test URL matching with exclude patterns."""
        from oideachais.dlt_sources.crawl_utils import URLMatcher

        matcher = URLMatcher(
            exclude_patterns=["*.pdf", "*.zip"]
        )

        assert matcher.matches("https://example.com/page.html")
        assert not matcher.matches("https://example.com/document.pdf")
        assert not matcher.matches("https://example.com/archive.zip")

    def test_url_matcher_domain_filtering(self) -> None:
        """Test URL matching with domain filters."""
        from oideachais.dlt_sources.crawl_utils import URLMatcher

        matcher = URLMatcher(
            include_domains=["curriculumonline.ie", "ncca.ie"]
        )

        assert matcher.matches("https://curriculumonline.ie/page")
        assert matcher.matches("https://ncca.ie/resource")
        assert not matcher.matches("https://google.com/search")

    def test_normalize_url(self) -> None:
        """Test URL normalization."""
        from oideachais.dlt_sources.crawl_utils import normalize_url

        # Remove fragment
        assert "anchor" not in normalize_url("https://example.com/page#anchor")

        # Lowercase scheme and host
        assert normalize_url("HTTPS://EXAMPLE.COM/Page") == "https://example.com/Page"

        # Remove trailing slash
        assert normalize_url("https://example.com/page/") == "https://example.com/page"

    def test_extract_links(self) -> None:
        """Test link extraction from HTML."""
        from oideachais.dlt_sources.crawl_utils import extract_links

        html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="https://other.com/page2">Page 2</a>
                <a href="page3">Page 3</a>
            </body>
        </html>
        """

        links = extract_links(html, "https://example.com/current/")

        assert "https://example.com/page1" in links
        assert "https://other.com/page2" in links
        assert "https://example.com/current/page3" in links

    def test_crawl_pattern_matching(self) -> None:
        """Test CrawlPattern URL matching."""
        from oideachais.dlt_sources.crawl_utils import CrawlPattern, ExtractionStrategy

        pattern = CrawlPattern(
            url_pattern="https://curriculumonline.ie/*/specifications/*",
            extraction_strategy=ExtractionStrategy.MARKDOWN,
            exclude_patterns=["*.pdf"],
        )

        assert pattern.matches("https://curriculumonline.ie/Junior-Cycle/specifications/math")
        assert not pattern.matches("https://curriculumonline.ie/Junior-Cycle/specifications/doc.pdf")
        assert not pattern.matches("https://other.ie/Junior-Cycle/specifications/math")


# ===========================================================================
# DLT Pipeline Tests
# ===========================================================================


class TestDLTPipeline:
    """Tests for DLT pipeline execution."""

    def test_firecrawl_source_creation(self) -> None:
        """Test creating a Firecrawl DLT source."""
        from oideachais.dlt_sources.common.firecrawl_source import create_firecrawl_source

        source_factory = create_firecrawl_source(
            source_name="test_source",
            base_url="https://example.com",
            include_paths=["/docs/*"],
            max_pages=10,
        )

        source = source_factory()
        assert source is not None

    def test_dlt_pipeline_run_with_mock(self, dlt_pipeline: Any, temp_dir: Path) -> None:
        """Test DLT pipeline execution with mock data."""
        import dlt

        @dlt.source(name="test_source")
        def test_source():
            @dlt.resource(name="test_data", write_disposition="replace")
            def test_data():
                yield {"id": 1, "name": "Test 1"}
                yield {"id": 2, "name": "Test 2"}

            return test_data

        source = test_source()
        info = dlt_pipeline.run(source)

        assert info is not None
        assert info.has_failed_jobs is False


# ===========================================================================
# Circuit Breaker Tests
# ===========================================================================


class TestCircuitBreaker:
    """Tests for the circuit breaker pattern."""

    def test_circuit_starts_closed(self, circuit_breaker: Any) -> None:
        """Test circuit breaker starts in closed state."""
        assert circuit_breaker.get_state("test_service") == "closed"
        assert not circuit_breaker.is_open("test_service")

    def test_circuit_opens_after_failures(self, circuit_breaker: Any) -> None:
        """Test circuit opens after threshold failures."""
        # failure_threshold=2 in fixture
        circuit_breaker.record_failure("test_service")
        assert circuit_breaker.get_state("test_service") == "closed"

        circuit_breaker.record_failure("test_service")
        assert circuit_breaker.get_state("test_service") == "open"
        assert circuit_breaker.is_open("test_service")

    def test_circuit_recovers_after_timeout(self, circuit_breaker: Any) -> None:
        """Test circuit transitions to half-open after recovery time."""
        import time

        # Open the circuit
        circuit_breaker.record_failure("test_service")
        circuit_breaker.record_failure("test_service")
        assert circuit_breaker.is_open("test_service")

        # Wait for recovery (recovery_time=1 in fixture)
        time.sleep(1.1)

        # Should transition to half-open
        assert not circuit_breaker.is_open("test_service")
        assert circuit_breaker.is_half_open("test_service")

    def test_success_resets_failures(self, circuit_breaker: Any) -> None:
        """Test success resets failure count."""
        circuit_breaker.record_failure("test_service")
        assert circuit_breaker._failures.get("test_service") == 1

        circuit_breaker.record_success("test_service")
        assert circuit_breaker._failures.get("test_service") == 0


# ===========================================================================
# LanceDB Client Tests
# ===========================================================================


class TestLanceDBClient:
    """Tests for the LanceDB Cloud client."""

    @pytest.fixture
    def lancedb_client(self, temp_dir: Path) -> Any:
        """Create a test LanceDB client with local storage."""
        from oideachais.storage.lancedb_cloud import (
            LanceDBCloudClient,
            LanceDBCloudConfig,
            LanceDBEnvironment,
        )

        config = LanceDBCloudConfig(
            local_path=str(temp_dir / "lancedb"),
            api_key="",  # Force local mode
        )
        client = LanceDBCloudClient(
            config=config,
            environment=LanceDBEnvironment.LOCAL,
        )
        return client

    @pytest.mark.asyncio
    async def test_create_table(self, lancedb_client: Any) -> None:
        """Test table creation."""
        import pyarrow as pa

        schema = pa.schema([
            ("id", pa.string()),
            ("vector", pa.list_(pa.float32(), 3)),
        ])

        table = await lancedb_client.create_table("test_table", schema=schema, mode="overwrite")
        assert table is not None

        tables = await lancedb_client.list_tables()
        assert "test_table" in tables

    @pytest.mark.asyncio
    async def test_add_and_search_embeddings(self, lancedb_client: Any) -> None:
        """Test adding and searching embeddings."""
        from oideachais.storage.lancedb_cloud import EmbeddingBatch

        # Create batch with 3 embeddings
        batch = EmbeddingBatch(
            vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]],
            metadata=[{"doc": "a"}, {"doc": "b"}, {"doc": "c"}],
            ids=["1", "2", "3"],
        )

        # Add embeddings
        count = await lancedb_client.add_embeddings("test_embeddings", batch)
        assert count == 3

        # Search
        results = await lancedb_client.search(
            "test_embeddings",
            query_vector=[0.1, 0.2, 0.3],
            limit=2,
        )
        assert len(results) <= 2

    def test_circuit_breaker_status(self, lancedb_client: Any) -> None:
        """Test circuit breaker status reporting."""
        status = lancedb_client.get_circuit_breaker_status()

        assert status["service"] == "lancedb"
        assert status["state"] == "closed"
        assert status["failures"] == 0

    def test_reset_circuit_breaker(self, lancedb_client: Any) -> None:
        """Test circuit breaker reset."""
        # Record some failures
        lancedb_client._circuit_breaker.record_failure("lancedb")

        status = lancedb_client.get_circuit_breaker_status()
        assert status["failures"] == 1

        # Reset
        lancedb_client.reset_circuit_breaker()

        status = lancedb_client.get_circuit_breaker_status()
        assert status["failures"] == 0


# ===========================================================================
# Local Documents Source Tests
# ===========================================================================


class TestLocalDocumentsSource:
    """Tests for local document processing."""

    def test_file_hash_computation(self, temp_dir: Path) -> None:
        """Test file hash computation for change detection."""
        from oideachais.dlt_sources.ireland.local_documents import _compute_file_hash

        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")

        hash1 = _compute_file_hash(test_file)
        assert len(hash1) == 64  # SHA-256 hex

        # Same content = same hash
        hash2 = _compute_file_hash(test_file)
        assert hash1 == hash2

        # Different content = different hash
        test_file.write_text("different content")
        hash3 = _compute_file_hash(test_file)
        assert hash1 != hash3
