"""
Unified Test Configuration for Sruth Pipelines.

Provides shared fixtures for:
- DuckDB (SerialDatabaseExecutor enforced)
- LanceDB (MVCC-safe vector operations)
- MCP server mocks
- Dagster test resources
"""

from __future__ import annotations

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Environment setup for tests
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DUCKDB_SINGLE_THREAD", "1")


# ============================================================================
# Async Event Loop
# ============================================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Temporary Directories
# ============================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_duckdb_path(temp_dir: Path) -> Path:
    """Provide a temporary DuckDB path."""
    return temp_dir / "test.duckdb"


@pytest.fixture
def temp_lancedb_path(temp_dir: Path) -> Path:
    """Provide a temporary LanceDB path."""
    path = temp_dir / "lancedb"
    path.mkdir(exist_ok=True)
    return path


# ============================================================================
# DuckDB Fixtures (Single-Threaded)
# ============================================================================


@pytest.fixture
def duckdb_connection(temp_duckdb_path: Path):
    """
    Create a DuckDB connection wrapped in SerialDatabaseExecutor.

    CRITICAL: DuckDB requires single-threaded access to prevent segfaults.
    """
    import duckdb

    # Use the shared serial executor pattern
    try:
        from sruth.shared.storage.serial_executor import run_serial

        def create_conn():
            conn = duckdb.connect(str(temp_duckdb_path))
            conn.execute("INSTALL spatial; LOAD spatial;")
            return conn

        conn = run_serial(create_conn)
    except ImportError:
        # Fallback for isolated tests
        conn = duckdb.connect(str(temp_duckdb_path))

    yield conn
    conn.close()


@pytest.fixture
def duckdb_with_schema(duckdb_connection):
    """DuckDB connection with common test schema."""
    duckdb_connection.execute("""
        CREATE TABLE IF NOT EXISTS test_curriculum (
            id VARCHAR PRIMARY KEY,
            nation VARCHAR,
            subject VARCHAR,
            level VARCHAR,
            content TEXT,
            embedding FLOAT[1024]
        )
    """)
    duckdb_connection.execute("""
        CREATE TABLE IF NOT EXISTS test_outcomes (
            id VARCHAR PRIMARY KEY,
            curriculum_id VARCHAR,
            outcome_text TEXT,
            strand VARCHAR
        )
    """)
    return duckdb_connection


# ============================================================================
# LanceDB Fixtures (MVCC-Safe)
# ============================================================================


@pytest.fixture
def lancedb_connection(temp_lancedb_path: Path):
    """Create a LanceDB connection with MVCC support."""
    import lancedb

    db = lancedb.connect(str(temp_lancedb_path))
    yield db


@pytest.fixture
def lancedb_with_table(lancedb_connection):
    """LanceDB connection with test table."""
    import numpy as np

    # Create test table with embeddings
    data = [
        {
            "id": f"test_{i}",
            "text": f"Test content {i}",
            "vector": np.random.rand(1024).tolist(),
            "nation": "ireland" if i % 2 == 0 else "scotland",
        }
        for i in range(10)
    ]

    table = lancedb_connection.create_table("test_embeddings", data, mode="overwrite")
    return lancedb_connection, table


# ============================================================================
# MCP Server Mocks
# ============================================================================


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server for testing tool calls."""
    server = MagicMock()
    server.list_tools = AsyncMock(return_value=[
        {"name": "search", "description": "Search content"},
        {"name": "query", "description": "Query database"},
    ])
    server.call_tool = AsyncMock(return_value={"result": "success"})
    return server


@pytest.fixture
def mock_chunkhound_mcp():
    """Mock ChunkHound MCP server."""
    mock = MagicMock()
    mock.search_semantic = AsyncMock(return_value=[
        {"file": "test.py", "chunk": "def test():", "score": 0.95},
    ])
    mock.code_research = AsyncMock(return_value={
        "answer": "Test answer",
        "sources": ["test.py:10"],
    })
    return mock


@pytest.fixture
def mock_firecrawl_mcp():
    """Mock Firecrawl MCP server."""
    mock = MagicMock()
    mock.scrape = AsyncMock(return_value={
        "markdown": "# Test Content",
        "metadata": {"title": "Test Page"},
    })
    mock.search = AsyncMock(return_value=[
        {"url": "https://example.com", "title": "Example"},
    ])
    return mock


@pytest.fixture
def mock_dagster_mcp():
    """Mock Dagster MCP server."""
    mock = MagicMock()
    mock.materialize_asset = AsyncMock(return_value={
        "run_id": "test-run-123",
        "status": "started",
    })
    mock.get_job_status = AsyncMock(return_value={
        "run_id": "test-run-123",
        "status": "success",
    })
    return mock


@pytest.fixture
def mock_memgraph_mcp():
    """Mock Memgraph MCP server."""
    mock = MagicMock()
    mock.cypher_query = AsyncMock(return_value=[
        {"n": {"name": "Test Node", "type": "curriculum"}},
    ])
    return mock


@pytest.fixture
def mock_qdrant_mcp():
    """Mock Qdrant MCP server."""
    mock = MagicMock()
    mock.search = AsyncMock(return_value=[
        {"id": "vec_1", "score": 0.92, "payload": {"text": "Test"}},
    ])
    mock.upsert = AsyncMock(return_value={"status": "ok", "count": 1})
    return mock


# ============================================================================
# Combined MCP Gateway Mock
# ============================================================================


@pytest.fixture
def mock_mcp_gateway(
    mock_chunkhound_mcp,
    mock_firecrawl_mcp,
    mock_dagster_mcp,
    mock_memgraph_mcp,
    mock_qdrant_mcp,
):
    """Combined mock for all MCP servers."""
    gateway = MagicMock()
    gateway.chunkhound = mock_chunkhound_mcp
    gateway.firecrawl = mock_firecrawl_mcp
    gateway.dagster = mock_dagster_mcp
    gateway.memgraph = mock_memgraph_mcp
    gateway.qdrant = mock_qdrant_mcp

    async def route(domain: str, tool: str, args: dict):
        server = getattr(gateway, domain.replace("-", "_"), None)
        if server:
            tool_fn = getattr(server, tool, None)
            if tool_fn:
                return await tool_fn(**args)
        raise ValueError(f"Unknown domain/tool: {domain}/{tool}")

    gateway.route = route
    return gateway


# ============================================================================
# Dagster Test Resources
# ============================================================================


@pytest.fixture
def dagster_test_context():
    """Create a Dagster test context for asset testing."""
    try:
        from dagster import build_op_context
        return build_op_context()
    except ImportError:
        return MagicMock()


@pytest.fixture
def dlt_test_pipeline():
    """Create a DLT test pipeline context."""
    try:
        import dlt_sources
        return dlt.pipeline(
            pipeline_name="test_pipeline",
            destination="duckdb",
            dataset_name="test_dataset",
        )
    except ImportError:
        return MagicMock()


# ============================================================================
# HTTP Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for API testing."""
    import httpx

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok"}
    mock_response.text = '{"status": "ok"}'

    mock_client = MagicMock(spec=httpx.AsyncClient)
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.post = AsyncMock(return_value=mock_response)

    return mock_client


# ============================================================================
# Embedding Batch Fixtures
# ============================================================================


@pytest.fixture
def embedding_batch_validator():
    """
    Validator to ensure embedding batches meet minimum size.

    CRITICAL: Batches must be >= 100 for performance.
    """
    def validate(texts: list[str], min_batch_size: int = 100):
        if len(texts) < min_batch_size:
            import warnings
            warnings.warn(
                f"Embedding batch size {len(texts)} is below minimum {min_batch_size}. "
                "This will cause 100x performance degradation.",
                UserWarning,
            )
        return len(texts) >= min_batch_size

    return validate


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service with batch validation."""
    import numpy as np

    async def embed(texts: list[str]) -> list[list[float]]:
        # Simulate embedding generation
        return [np.random.rand(1024).tolist() for _ in texts]

    service = MagicMock()
    service.embed = AsyncMock(side_effect=embed)
    service.batch_size = 100
    return service


# ============================================================================
# Pipeline-Specific Fixtures
# ============================================================================


@pytest.fixture
def oideachais_test_data():
    """Sample curriculum data for oideachais tests."""
    return [
        {
            "id": "ie_jc_maths_1",
            "nation": "ireland",
            "subject": "mathematics",
            "level": "junior_cycle",
            "content": "Students should be able to solve quadratic equations",
            "strand": "algebra",
        },
        {
            "id": "ie_jc_irish_1",
            "nation": "ireland",
            "subject": "gaeilge",
            "level": "junior_cycle",
            "content": "Foghlaimíonn daltaí faoi litríocht na Gaeilge",
            "strand": "literature",
        },
    ]


@pytest.fixture
def crypteolas_test_data():
    """Sample crypto data for crypteolas tests."""
    return [
        {
            "protocol": "uniswap",
            "tvl": 5_000_000_000,
            "chain": "ethereum",
            "category": "dex",
        },
        {
            "protocol": "aave",
            "tvl": 10_000_000_000,
            "chain": "ethereum",
            "category": "lending",
        },
    ]


@pytest.fixture
def tuath_test_data():
    """Sample mythology data for tuath tests."""
    return [
        {
            "character": "Cú Chulainn",
            "tradition": "irish_mythology",
            "cycle": "ulster_cycle",
            "description": "The Hound of Culann",
        },
        {
            "character": "Fionn mac Cumhaill",
            "tradition": "irish_mythology",
            "cycle": "fenian_cycle",
            "description": "Leader of the Fianna",
        },
    ]


# ============================================================================
# Markers
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "mcp: marks tests requiring MCP servers")
    config.addinivalue_line("markers", "slow: marks slow tests")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "dagster: marks tests requiring Dagster")
