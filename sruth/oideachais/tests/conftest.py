"""
Pytest fixtures for oideachais tests.

Provides fixtures for:
- DLT pipeline testing
- Dagster asset testing
- Database connections (DuckDB, LanceDB)
- Mock external APIs
- Sample data
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Ensure test environment
os.environ.setdefault("DAGSTER_HOME", tempfile.mkdtemp())
os.environ.setdefault("OIDEACHAIS_ENV", "test")


# ===========================================================================
# Database Fixtures
# ===========================================================================


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def duckdb_connection(temp_dir: Path) -> Generator[Any, None, None]:
    """Provide a test DuckDB connection."""
    try:
        import duckdb
    except ImportError:
        pytest.skip("duckdb not installed")

    db_path = temp_dir / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    yield conn
    conn.close()


@pytest.fixture
def lancedb_connection(temp_dir: Path) -> Generator[Any, None, None]:
    """Provide a test LanceDB connection."""
    try:
        import lancedb
    except ImportError:
        pytest.skip("lancedb not installed")

    db = lancedb.connect(str(temp_dir / "lancedb"))
    yield db


# ===========================================================================
# DLT Fixtures
# ===========================================================================


@pytest.fixture
def dlt_pipeline(temp_dir: Path) -> Generator[Any, None, None]:
    """Provide a test DLT pipeline with DuckDB destination."""
    try:
        import dlt
    except ImportError:
        pytest.skip("dlt not installed")

    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline",
        destination="duckdb",
        dataset_name="test_dataset",
        pipelines_dir=str(temp_dir / "pipelines"),
    )
    yield pipeline


@pytest.fixture
def mock_http_client() -> Generator[MagicMock, None, None]:
    """Mock httpx client for testing API sources."""
    with patch("httpx.AsyncClient") as mock:
        client_instance = MagicMock()
        mock.return_value.__aenter__.return_value = client_instance
        yield client_instance


# ===========================================================================
# Dagster Fixtures
# ===========================================================================


@pytest.fixture
def dagster_instance(temp_dir: Path) -> Generator[Any, None, None]:
    """Provide a test Dagster instance."""
    try:
        from dagster import DagsterInstance
    except ImportError:
        pytest.skip("dagster not installed")

    with DagsterInstance.ephemeral() as instance:
        yield instance


@pytest.fixture
def dagster_context(dagster_instance: Any) -> Generator[Any, None, None]:
    """Provide a mock Dagster asset context."""
    try:
        from dagster import build_asset_context
    except ImportError:
        pytest.skip("dagster not installed")

    context = build_asset_context()
    yield context


# ===========================================================================
# Sample Data Fixtures
# ===========================================================================


@pytest.fixture
def sample_curriculum_data() -> list[dict[str, Any]]:
    """Sample curriculum data for testing."""
    return [
        {
            "id": "ncca_math_jc",
            "title": "Junior Cycle Mathematics",
            "title_ga": "Matamaitic na Sraithe Sóisearaí",
            "level": "junior_cycle",
            "subject": "mathematics",
            "language": "en",
            "content": "Learning outcomes for algebra and geometry...",
            "source_url": "https://curriculumonline.ie/Junior-Cycle/Mathematics",
        },
        {
            "id": "ncca_irish_lc",
            "title": "Leaving Certificate Irish",
            "title_ga": "Gaeilge na hArdteistiméireachta",
            "level": "leaving_cert",
            "subject": "irish",
            "language": "ga",
            "content": "Torthaí foghlama don Ghaeilge...",
            "source_url": "https://curriculumonline.ie/Senior-Cycle/Irish",
        },
    ]


@pytest.fixture
def sample_exam_data() -> list[dict[str, Any]]:
    """Sample SEC exam data for testing."""
    return [
        {
            "id": "sec_math_hl_2024",
            "subject": "mathematics",
            "level": "higher",
            "year": 2024,
            "paper_number": 1,
            "language": "en",
            "pdf_url": "https://examinations.ie/archive/2024/LC001ALP100EV.pdf",
        },
        {
            "id": "sec_irish_ol_2024",
            "subject": "irish",
            "level": "ordinary",
            "year": 2024,
            "paper_number": 1,
            "language": "ga",
            "pdf_url": "https://examinations.ie/archive/2024/LC012ALP100GV.pdf",
        },
    ]


@pytest.fixture
def sample_embedding_data() -> list[dict[str, Any]]:
    """Sample embedding data for testing."""
    import numpy as np

    return [
        {
            "id": "doc_1",
            "text": "Mathematics learning outcomes for algebra",
            "embedding": np.random.rand(384).tolist(),
            "metadata": {"subject": "math", "level": "junior_cycle"},
        },
        {
            "id": "doc_2",
            "text": "Torthaí foghlama don Ghaeilge",
            "embedding": np.random.rand(384).tolist(),
            "metadata": {"subject": "irish", "level": "leaving_cert"},
        },
    ]


# ===========================================================================
# Mock Service Fixtures
# ===========================================================================


@pytest.fixture
def mock_lancedb_cloud() -> Generator[MagicMock, None, None]:
    """Mock LanceDB Cloud connection."""
    with patch("lancedb.connect") as mock:
        db = MagicMock()
        mock.return_value = db
        yield db


@pytest.fixture
def mock_kafka_producer() -> Generator[MagicMock, None, None]:
    """Mock Kafka producer."""
    with patch("confluent_kafka.Producer") as mock:
        producer = MagicMock()
        mock.return_value = producer
        yield producer


@pytest.fixture
def mock_modal_function() -> Generator[MagicMock, None, None]:
    """Mock Modal function for GPU workloads."""
    with patch("modal.Function") as mock:
        fn = MagicMock()
        mock.return_value = fn
        yield fn


# ===========================================================================
# Serial Executor Fixture
# ===========================================================================


@pytest.fixture
def serial_executor() -> Generator[Any, None, None]:
    """Provide a serial executor for database operations."""
    from sruth.oideachais.storage.serial_executor import SerialDatabaseExecutor

    executor = SerialDatabaseExecutor()
    yield executor


# ===========================================================================
# Circuit Breaker Fixture
# ===========================================================================


@pytest.fixture
def circuit_breaker() -> Generator[Any, None, None]:
    """Provide a circuit breaker for testing."""
    from sruth.oideachais.storage.lancedb_cloud import CircuitBreaker

    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_time=1,
        half_open_max_calls=1,
    )
    yield breaker


# ===========================================================================
# Rate Limiter Fixture (TODO: Implement rate limiter utility)
# ===========================================================================


# @pytest.fixture
# def rate_limiter() -> Generator[Any, None, None]:
#     """Provide a rate limiter for testing."""
#     # Rate limiter not yet implemented
#     pass


# ===========================================================================
# Pytest Configuration
# ===========================================================================


def pytest_configure(config: Any) -> None:
    """Configure pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks integration tests")
    config.addinivalue_line("markers", "gpu: marks tests requiring GPU")
    config.addinivalue_line("markers", "modal: marks tests requiring Modal")
