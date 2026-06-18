"""Tests for the `oideachais.dagster_defs.weekly_downloads` asset check.

The `celtic-data-engineering-pipeline` scenario "Dev target builds 3 models"
implies a follow-up check: after the dbt model materializes, the row count
should be > 100. This file tests the `check_weekly_downloads_row_count`
function (registered in `oideachais/dagster_defs/asset_checks.py`).
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from oideachais.dagster_defs.asset_checks import check_weekly_downloads_row_count


def test_check_passes_when_row_count_above_threshold() -> None:
    """101 rows → passed=True."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.return_value.fetchone.return_value = (101,)
    result = check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    assert result.passed is True
    # Dagster wraps metadata values in IntMetadataValue (has a .value attr)
    assert result.metadata["row_count"].value == 101
    assert result.metadata["threshold"].value == 100


def test_check_passes_at_large_row_count() -> None:
    """1000 rows → passed=True (smoke gate is > 100, not a small cap)."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.return_value.fetchone.return_value = (1000,)
    result = check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    assert result.passed is True
    assert result.metadata["row_count"].value == 1000


def test_check_fails_at_zero_rows() -> None:
    """0 rows → passed=False (the model hasn't been built yet)."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.return_value.fetchone.return_value = (0,)
    result = check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    assert result.passed is False
    assert result.metadata["row_count"].value == 0


def test_check_fails_at_threshold_boundary() -> None:
    """100 rows → passed=False (strictly greater than 100, not >=)."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.return_value.fetchone.return_value = (100,)
    result = check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    assert result.passed is False


def test_check_handles_missing_table() -> None:
    """If the `main.weekly_downloads` table doesn't exist, the check returns passed=False with a note."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.side_effect = RuntimeError("Catalog Error: Table 'main.weekly_downloads' does not exist")
    result = check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    assert result.passed is False
    assert "weekly_downloads not yet materialized" in result.metadata.get("note", "")


def test_check_uses_main_schema_table() -> None:
    """Regression: the SQL must read from `main.weekly_downloads` (the dbt default schema)."""
    fake_resource = MagicMock()
    fake_conn = fake_resource.get_connection.return_value
    fake_conn.execute.return_value.fetchone.return_value = (0,)
    check_weekly_downloads_row_count(context=None, duckdb=fake_resource)
    sql = fake_conn.execute.call_args[0][0]
    assert "main.weekly_downloads" in sql
    assert "count(*)" in sql.lower()
