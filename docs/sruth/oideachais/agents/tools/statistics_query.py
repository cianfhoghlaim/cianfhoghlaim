"""
Statistics Query Tools for ADK Agents.

Provides DuckDB-based statistics queries across British Isles education data.
"""

from pathlib import Path
from typing import Literal

import duckdb
from pydantic import BaseModel, Field
from google.adk.tools import ToolContext

# Storage paths
DATA_DIR = Path(__file__).parent.parent.parent / "storage" / "data"
DUCKDB_PATH = str(DATA_DIR / "duckdb" / "education.duckdb")


class StatisticsResult(BaseModel):
    """Result from a statistics query."""

    metric: str
    value: float | None
    unit: str
    nation: str
    year: str
    breakdown: dict | None = None


class NationComparison(BaseModel):
    """Comparison of a metric across nations."""

    metric: str
    year: str
    values: dict[str, float]  # nation -> value
    highest: str
    lowest: str
    uk_average: float | None = None


class TrendData(BaseModel):
    """Historical trend data for a metric."""

    metric: str
    nation: str
    data_points: list[dict]  # [{"year": "2023-24", "value": 45.2}, ...]
    trend_direction: Literal["increasing", "decreasing", "stable"]
    average_change: float


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get DuckDB connection."""
    return duckdb.connect(DUCKDB_PATH, read_only=True)


async def query_statistics(
    metric: str = Field(description="Metric name (e.g., 'attainment_8', 'absence_rate')"),
    nation: str = Field(description="Nation code (england, scotland, wales, etc.)"),
    year: str = Field(description="Academic year (e.g., '2023-24')"),
    aggregation_level: str = Field(
        default="national",
        description="Aggregation level: national, local_authority, school",
    ),
    breakdown_by: str | None = Field(
        default=None,
        description="Optional breakdown dimension (gender, fsm, ethnicity)",
    ),
    tool_context: ToolContext = None,
) -> StatisticsResult:
    """
    Query education statistics from DuckDB.

    Retrieves a specific metric for a nation and year, with optional breakdowns.

    Examples:
    - query_statistics("attainment_8", "england", "2023-24")
    - query_statistics("absence_rate", "wales", "2023-24", breakdown_by="fsm")
    """
    conn = get_connection()

    try:
        # Build query based on aggregation level
        if aggregation_level == "national":
            query = f"""
                SELECT
                    metric_name,
                    metric_value,
                    unit,
                    nation,
                    academic_year
                FROM education.statistics
                WHERE metric_name = ?
                AND nation = ?
                AND academic_year = ?
                AND aggregation_level = 'national'
                LIMIT 1
            """
            result = conn.execute(query, [metric, nation, year]).fetchone()

            if result:
                return StatisticsResult(
                    metric=result[0],
                    value=result[1],
                    unit=result[2],
                    nation=result[3],
                    year=result[4],
                )

        # Handle breakdowns
        if breakdown_by:
            query = f"""
                SELECT
                    breakdown_category,
                    metric_value
                FROM education.statistics_breakdowns
                WHERE metric_name = ?
                AND nation = ?
                AND academic_year = ?
                AND breakdown_dimension = ?
            """
            results = conn.execute(
                query, [metric, nation, year, breakdown_by]
            ).fetchall()

            breakdown = {row[0]: row[1] for row in results}

            return StatisticsResult(
                metric=metric,
                value=None,
                unit="",
                nation=nation,
                year=year,
                breakdown=breakdown,
            )

        return StatisticsResult(
            metric=metric,
            value=None,
            unit="",
            nation=nation,
            year=year,
        )

    finally:
        conn.close()


async def compare_nations(
    metric: str = Field(description="Metric to compare"),
    year: str = Field(description="Academic year"),
    nations: list[str] | None = Field(
        default=None,
        description="Nations to compare (default: all main nations)",
    ),
    tool_context: ToolContext = None,
) -> NationComparison:
    """
    Compare a metric across multiple British Isles nations.

    Retrieves the same metric for all specified nations and identifies
    highest/lowest performers.

    Examples:
    - compare_nations("attainment_8", "2023-24")
    - compare_nations("teacher_vacancy_rate", "2023-24", ["england", "scotland"])
    """
    if nations is None:
        nations = ["england", "scotland", "wales", "northern_ireland", "ireland"]

    conn = get_connection()

    try:
        query = """
            SELECT
                nation,
                metric_value
            FROM education.statistics
            WHERE metric_name = ?
            AND academic_year = ?
            AND nation = ANY(?)
            AND aggregation_level = 'national'
        """
        results = conn.execute(query, [metric, year, nations]).fetchall()

        values = {row[0]: row[1] for row in results if row[1] is not None}

        if not values:
            return NationComparison(
                metric=metric,
                year=year,
                values={},
                highest="",
                lowest="",
            )

        highest = max(values, key=values.get)
        lowest = min(values, key=values.get)

        # Calculate UK average (excluding Ireland)
        uk_nations = ["england", "scotland", "wales", "northern_ireland"]
        uk_values = [v for n, v in values.items() if n in uk_nations]
        uk_average = sum(uk_values) / len(uk_values) if uk_values else None

        return NationComparison(
            metric=metric,
            year=year,
            values=values,
            highest=highest,
            lowest=lowest,
            uk_average=uk_average,
        )

    finally:
        conn.close()


async def get_trend(
    metric: str = Field(description="Metric to analyze"),
    nation: str = Field(description="Nation code"),
    start_year: str = Field(default="2019-20", description="Start year"),
    end_year: str = Field(default="2023-24", description="End year"),
    tool_context: ToolContext = None,
) -> TrendData:
    """
    Get historical trend data for a metric.

    Retrieves year-over-year data and calculates trend direction.

    Examples:
    - get_trend("absence_rate", "england", "2019-20", "2023-24")
    """
    conn = get_connection()

    try:
        query = """
            SELECT
                academic_year,
                metric_value
            FROM education.statistics
            WHERE metric_name = ?
            AND nation = ?
            AND academic_year >= ?
            AND academic_year <= ?
            AND aggregation_level = 'national'
            ORDER BY academic_year
        """
        results = conn.execute(query, [metric, nation, start_year, end_year]).fetchall()

        data_points = [{"year": row[0], "value": row[1]} for row in results]

        if len(data_points) < 2:
            return TrendData(
                metric=metric,
                nation=nation,
                data_points=data_points,
                trend_direction="stable",
                average_change=0.0,
            )

        # Calculate trend
        values = [dp["value"] for dp in data_points if dp["value"] is not None]
        if len(values) >= 2:
            changes = [values[i + 1] - values[i] for i in range(len(values) - 1)]
            avg_change = sum(changes) / len(changes)

            if avg_change > 0.5:
                direction = "increasing"
            elif avg_change < -0.5:
                direction = "decreasing"
            else:
                direction = "stable"
        else:
            avg_change = 0.0
            direction = "stable"

        return TrendData(
            metric=metric,
            nation=nation,
            data_points=data_points,
            trend_direction=direction,
            average_change=avg_change,
        )

    finally:
        conn.close()


async def list_available_metrics(
    nation: str | None = Field(default=None, description="Filter by nation"),
    category: str | None = Field(default=None, description="Filter by category"),
    tool_context: ToolContext = None,
) -> list[dict]:
    """
    List available metrics in the database.

    Useful for discovering what statistics are available to query.
    """
    conn = get_connection()

    try:
        conditions = ["1=1"]
        params = []

        if nation:
            conditions.append("nation = ?")
            params.append(nation)
        if category:
            conditions.append("metric_category = ?")
            params.append(category)

        query = f"""
            SELECT DISTINCT
                metric_name,
                metric_category,
                unit,
                nation
            FROM education.statistics
            WHERE {' AND '.join(conditions)}
            ORDER BY metric_category, metric_name
        """
        results = conn.execute(query, params).fetchall()

        return [
            {
                "metric": row[0],
                "category": row[1],
                "unit": row[2],
                "nation": row[3],
            }
            for row in results
        ]

    finally:
        conn.close()
