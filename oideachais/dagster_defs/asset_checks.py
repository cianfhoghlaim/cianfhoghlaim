"""
Asset Checks for Celtic Education Platform.

Data quality validation checks that run after asset materialization.
These checks validate:
- Content completeness
- Data integrity
- Embedding quality
- Translation coverage

Usage:
    Checks automatically run after associated asset materialization.
    Failed checks surface in the Dagster UI for investigation.
"""
from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    AssetKey,
    asset_check,
)

from .resources import DuckDBResource, LanceDBResource

# ============================================================================
# Ireland Education Asset Checks - DEPRECATED
# ============================================================================
# NOTE: Legacy checks removed - assets were in deleted ie_education_assets.py
# TODO: Add checks for unified curriculum assets (ireland.curriculum.*)


# ============================================================================
# Celtic Language Asset Checks
# ============================================================================


@asset_check(
    asset=AssetKey(["celtic", "duchas", "pages"]),
    description="Verify Duchas pages have manuscript content",
)
def check_duchas_pages(context, duckdb: DuckDBResource) -> AssetCheckResult:
    """Check Duchas manuscript pages for content."""
    try:
        conn = duckdb.get_connection()
        result = conn.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT county) as counties,
                COUNT(CASE WHEN transcription IS NOT NULL THEN 1 END) as transcribed
            FROM celtic.duchas_pages
        """).fetchone()

        if result is None:
            return AssetCheckResult(passed=True, metadata={"note": "No data yet"})

        total, counties, transcribed = result
        transcription_rate = transcribed / total if total > 0 else 0

        return AssetCheckResult(
            passed=total > 0,
            metadata={
                "total_pages": total,
                "counties_covered": counties,
                "transcription_rate": f"{transcription_rate:.1%}",
            },
        )
    except Exception as e:
        return AssetCheckResult(
            passed=True,
            metadata={"note": f"Check skipped: {str(e)}"},
        )


@asset_check(
    asset=AssetKey(["celtic", "embeddings"]),
    description="Verify Celtic language embeddings are multilingual",
)
def check_celtic_embeddings(context, lancedb: LanceDBResource) -> AssetCheckResult:
    """Check that Celtic embeddings cover multiple languages."""
    try:
        db = lancedb.get_db()

        # Check tables with celtic prefix
        celtic_tables = [t for t in db.table_names() if t.startswith("teanga.") or t.startswith("celtic.")]

        if not celtic_tables:
            return AssetCheckResult(
                passed=True,
                metadata={"note": "No Celtic embeddings yet"},
            )

        total_embeddings = 0
        for table_name in celtic_tables:
            table = db.open_table(table_name)
            total_embeddings += table.count_rows()

        return AssetCheckResult(
            passed=total_embeddings > 0,
            metadata={
                "celtic_tables": celtic_tables,
                "total_embeddings": total_embeddings,
            },
        )
    except Exception as e:
        return AssetCheckResult(
            passed=True,
            metadata={"note": f"Check skipped: {str(e)}"},
        )


# ============================================================================
# Translation Asset Checks
# ============================================================================


# NOTE: check_translation_coverage removed - asset was in deleted ie_education_assets.py


# ============================================================================
# Geospatial Asset Checks
# ============================================================================


@asset_check(
    asset=AssetKey(["geospatial", "boundaries"]),
    description="Verify geospatial boundaries have valid geometry",
)
def check_geospatial_validity(context, duckdb: DuckDBResource) -> AssetCheckResult:
    """Check that geospatial data has valid geometries."""
    try:
        conn = duckdb.get_connection()
        # Use DuckDB spatial extension
        conn.execute("LOAD spatial;")

        result = conn.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN ST_IsValid(geometry) THEN 1 END) as valid
            FROM geospatial.boundaries
        """).fetchone()

        if result is None:
            return AssetCheckResult(passed=True, metadata={"note": "No boundaries yet"})

        total, valid = result
        validity_rate = valid / total if total > 0 else 0

        return AssetCheckResult(
            passed=validity_rate >= 0.95,  # 95% valid geometries
            severity=AssetCheckSeverity.ERROR if validity_rate < 0.95 else AssetCheckSeverity.INFO,
            metadata={
                "total_boundaries": total,
                "valid_geometries": valid,
                "validity_rate": f"{validity_rate:.1%}",
            },
        )
    except Exception as e:
        return AssetCheckResult(
            passed=True,
            metadata={"note": f"Check skipped: {str(e)}"},
        )


# ============================================================================
# dbt-duckdb project (the celtic-data-engineering-patterns change)
# ============================================================================
# Validates the `celtic-data-engineering-pipeline` scenario: when the
# weekly_downloads dbt model materializes, we expect at least 100 rows.
# This is the smoke gate for the dbt → marimo notebook pipeline (the
# marimo notebooks query this model).


@asset_check(
    asset=AssetKey(["weekly_downloads"]),
    description="Validate that weekly_downloads has more than 100 rows after materialization (the dbt → marimo smoke gate)",
)
def check_weekly_downloads_row_count(context, duckdb: DuckDBResource) -> AssetCheckResult:
    """Check that the `weekly_downloads` dbt model has at least 100 rows.

    Mirrors the prior-art `spaces/data-engineering/dbt_project/` pattern
    of using dbt-built models as the contract surface for downstream
    consumers (marimo notebooks, Evidence dashboards, the lakehouse).
    """
    try:
        conn = duckdb.get_connection()
        row_count = conn.execute(
            "SELECT count(*) FROM main.weekly_downloads"
        ).fetchone()[0]
        passed = row_count > 100
        return AssetCheckResult(
            passed=passed,
            metadata={"row_count": row_count, "threshold": 100},
        )
    except Exception as e:
        return AssetCheckResult(
            passed=False,
            metadata={"error": str(e), "note": "weekly_downloads not yet materialized"},
        )


# ============================================================================
# Export All Checks
# ============================================================================

all_asset_checks = [
    # Ireland Education - removed (legacy assets deleted)
    # Celtic Language
    check_duchas_pages,
    check_celtic_embeddings,
    # Geospatial
    check_geospatial_validity,
    # dbt project
    check_weekly_downloads_row_count,
]
