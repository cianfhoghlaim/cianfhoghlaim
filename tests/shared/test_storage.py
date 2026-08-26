"""
Tests for sruth.shared.storage module.

Tests:
- SerialDatabaseExecutor singleton behavior
- DuckDBClient operations
- LanceDBClient vector operations
"""

import tempfile
from pathlib import Path

import pytest


class TestSerialDatabaseExecutor:
    """Tests for SerialDatabaseExecutor."""

    def test_singleton_pattern(self):
        """Test that SerialDatabaseExecutor is a singleton."""
        from sruth.shared.storage import SerialDatabaseExecutor

        executor1 = SerialDatabaseExecutor()
        executor2 = SerialDatabaseExecutor()

        assert executor1 is executor2

    def test_run_executes_function(self):
        """Test that run() executes the provided function."""
        from sruth.shared.storage import get_executor

        executor = get_executor()
        result = executor.run(lambda: 42)

        assert result == 42

    def test_run_passes_arguments(self):
        """Test that run() passes arguments correctly."""
        from sruth.shared.storage import run_serial

        def add(a, b):
            return a + b

        result = run_serial(add, 10, 20)
        assert result == 30

    def test_run_propagates_exceptions(self):
        """Test that run() propagates exceptions."""
        from sruth.shared.storage import run_serial

        def failing_func():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            run_serial(failing_func)


class TestDuckDBClient:
    """Tests for DuckDBClient."""

    def test_in_memory_connection(self):
        """Test in-memory database connection."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            result = client.query("SELECT 1 as value")
            assert result == [{"value": 1}]

    def test_query_with_params(self):
        """Test query with parameters."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            client.execute("CREATE TABLE test (id INT, name VARCHAR)")
            client.execute("INSERT INTO test VALUES (?, ?)", [1, "Alice"])

            result = client.query("SELECT * FROM test WHERE id = ?", [1])
            assert len(result) == 1
            assert result[0]["name"] == "Alice"

    def test_insert_batch(self):
        """Test batch insert."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            client.execute("CREATE TABLE users (id INT, name VARCHAR)")

            rows = [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
                {"id": 3, "name": "Carol"},
            ]
            count = client.insert_batch("users", rows)

            assert count == 3
            result = client.query("SELECT COUNT(*) as cnt FROM users")
            assert result[0]["cnt"] == 3

    def test_table_exists(self):
        """Test table existence check."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            assert not client.table_exists("nonexistent")

            client.execute("CREATE TABLE test (id INT)")
            assert client.table_exists("test")

    def test_transaction_commit(self):
        """Test transaction commit."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            client.execute("CREATE TABLE test (id INT)")

            with client.transaction():
                client.execute("INSERT INTO test VALUES (1)")
                client.execute("INSERT INTO test VALUES (2)")

            result = client.query("SELECT COUNT(*) as cnt FROM test")
            assert result[0]["cnt"] == 2

    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        from sruth.shared.storage import DuckDBClient

        with DuckDBClient(path=":memory:") as client:
            client.execute("CREATE TABLE test (id INT)")
            client.execute("INSERT INTO test VALUES (1)")

            try:
                with client.transaction():
                    client.execute("INSERT INTO test VALUES (2)")
                    raise ValueError("Simulated error")
            except ValueError:
                pass

            result = client.query("SELECT COUNT(*) as cnt FROM test")
            # Should only have the initial row, transaction rolled back
            assert result[0]["cnt"] == 1

    def test_file_persistence(self):
        """Test file-based database persistence."""
        from sruth.shared.storage import DuckDBClient

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.duckdb"

            # Create and populate
            with DuckDBClient(path=db_path) as client:
                client.execute("CREATE TABLE test (value INT)")
                client.execute("INSERT INTO test VALUES (42)")

            # Reopen and verify
            with DuckDBClient(path=db_path) as client:
                result = client.query("SELECT * FROM test")
                assert result == [{"value": 42}]


class TestLanceDBClient:
    """Tests for LanceDBClient."""

    def test_create_table(self):
        """Test table creation."""
        from sruth.shared.storage import LanceDBClient

        with tempfile.TemporaryDirectory() as tmpdir:
            client = LanceDBClient(uri=tmpdir)

            data = [
                {"text": "hello", "vector": [0.1, 0.2, 0.3]},
                {"text": "world", "vector": [0.4, 0.5, 0.6]},
            ]
            client.create_table("test", data=data)

            assert client.table_exists("test")
            assert "test" in client.list_tables()

    def test_add_vectors(self):
        """Test adding vectors to table."""
        from sruth.shared.storage import LanceDBClient

        with tempfile.TemporaryDirectory() as tmpdir:
            client = LanceDBClient(uri=tmpdir)

            initial_data = [{"text": "hello", "vector": [0.1, 0.2, 0.3]}]
            client.create_table("test", data=initial_data)

            new_data = [{"text": "world", "vector": [0.4, 0.5, 0.6]}]
            count = client.add("test", new_data)

            assert count == 1
            assert client.count("test") == 2

    def test_search(self):
        """Test vector search."""
        from sruth.shared.storage import LanceDBClient

        with tempfile.TemporaryDirectory() as tmpdir:
            client = LanceDBClient(uri=tmpdir)

            data = [
                {"text": "hello", "vector": [1.0, 0.0, 0.0]},
                {"text": "world", "vector": [0.0, 1.0, 0.0]},
                {"text": "foo", "vector": [0.0, 0.0, 1.0]},
            ]
            client.create_table("test", data=data)

            # Search for vector closest to [1, 0, 0]
            results = client.search("test", query_vector=[1.0, 0.0, 0.0], limit=1)

            assert len(results) == 1
            assert results[0]["text"] == "hello"

    def test_delete(self):
        """Test deleting records."""
        from sruth.shared.storage import LanceDBClient

        with tempfile.TemporaryDirectory() as tmpdir:
            client = LanceDBClient(uri=tmpdir)

            data = [
                {"id": 1, "text": "hello", "vector": [0.1, 0.2, 0.3]},
                {"id": 2, "text": "world", "vector": [0.4, 0.5, 0.6]},
            ]
            client.create_table("test", data=data)

            client.delete("test", "id = 1")

            assert client.count("test") == 1

    def test_hnsw_threshold(self):
        """Test HNSW drop threshold constant."""
        from sruth.shared.storage import HNSW_DROP_THRESHOLD

        assert HNSW_DROP_THRESHOLD == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
