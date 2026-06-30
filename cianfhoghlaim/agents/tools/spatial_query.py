"""
Spatial Query Tools for ADK Agents.

Provides DuckDB Spatial queries for LSOA/Data Zone level analysis.
Supports multi-nation education statistics across UK and Ireland.
"""

from pathlib import Path
from typing import Literal

import duckdb
from google.adk.tools import ToolContext
from pydantic import BaseModel, Field

# Storage paths
DATA_DIR = Path(__file__).parent.parent.parent / "storage" / "data"
DUCKDB_PATH = str(DATA_DIR / "duckdb" / "education.duckdb")
GEOPARQUET_DIR = DATA_DIR / "geoparquet"


class AreaStatistics(BaseModel):
    """Statistics for a geographic area."""

    area_code: str
    area_name: str
    nation: str
    school_count: int
    metrics: dict[str, float]
    deprivation_rank: int | None = None


class NearbySchool(BaseModel):
    """School near a location."""

    urn: str
    school_name: str
    school_type: str
    distance_km: float
    nation: str
    postcode: str | None = None


class SpatialAggregation(BaseModel):
    """Aggregated statistics by area."""

    aggregation_level: str
    areas: list[AreaStatistics]
    total_areas: int
    total_schools: int


def get_connection() -> duckdb.DuckDBPyConnection:
    """Get DuckDB connection with spatial extension."""
    conn = duckdb.connect(DUCKDB_PATH, read_only=True)
    conn.execute("INSTALL spatial; LOAD spatial;")
    return conn


async def query_by_area(
    area_code: str = Field(description="Area code (LSOA, Data Zone, etc.)"),
    metrics: list[str] | None = Field(
        default=None,
        description="Metrics to retrieve (default: all available)",
    ),
    tool_context: ToolContext = None,
) -> AreaStatistics:
    """
    Get education statistics for a specific geographic area.

    Supports LSOA (England/Wales), Data Zone (Scotland),
    SOA (Northern Ireland), and Small Area (Ireland) codes.

    Examples:
    - query_by_area("E01000001")  # LSOA in England
    - query_by_area("S01006506")  # Data Zone in Scotland
    """
    conn = get_connection()

    try:
        # Query area information
        area_query = """
            SELECT
                area_code,
                area_name,
                nation
            FROM education.boundaries
            WHERE area_code = ?
            LIMIT 1
        """
        area_result = conn.execute(area_query, [area_code]).fetchone()

        if not area_result:
            return AreaStatistics(
                area_code=area_code,
                area_name="Unknown",
                nation="unknown",
                school_count=0,
                metrics={},
            )

        # Query schools in area
        school_query = """
            SELECT COUNT(*) as school_count
            FROM education.establishments e
            JOIN education.boundaries b ON ST_Contains(b.geometry, e.geometry)
            WHERE b.area_code = ?
        """
        school_count = conn.execute(school_query, [area_code]).fetchone()[0]

        # Query metrics
        metrics_query = """
            SELECT
                metric_name,
                metric_value
            FROM education.area_statistics
            WHERE area_code = ?
        """
        if metrics:
            metrics_query += " AND metric_name = ANY(?)"
            metrics_result = conn.execute(metrics_query, [area_code, metrics]).fetchall()
        else:
            metrics_result = conn.execute(metrics_query, [area_code]).fetchall()

        metrics_dict = {row[0]: row[1] for row in metrics_result}

        # Query deprivation rank if available
        dep_query = """
            SELECT deprivation_rank
            FROM education.deprivation_indices
            WHERE area_code = ?
            LIMIT 1
        """
        dep_result = conn.execute(dep_query, [area_code]).fetchone()
        dep_rank = dep_result[0] if dep_result else None

        return AreaStatistics(
            area_code=area_code,
            area_name=area_result[1],
            nation=area_result[2],
            school_count=school_count,
            metrics=metrics_dict,
            deprivation_rank=dep_rank,
        )

    finally:
        conn.close()


async def get_area_statistics(
    nation: str = Field(description="Nation code"),
    aggregation_level: Literal["lsoa", "local_authority", "region"] = Field(
        default="local_authority",
        description="Geographic aggregation level",
    ),
    metric: str = Field(description="Metric to aggregate"),
    top_n: int = Field(default=10, description="Number of top/bottom areas"),
    order: Literal["asc", "desc"] = Field(default="desc", description="Sort order"),
    tool_context: ToolContext = None,
) -> SpatialAggregation:
    """
    Get aggregated education statistics by geographic area.

    Supports ranking areas by education metrics.

    Examples:
    - get_area_statistics("england", "local_authority", "attainment_8", top_n=10)
    - get_area_statistics("scotland", "lsoa", "absence_rate", order="asc")
    """
    conn = get_connection()

    try:
        # Map aggregation level to table/column
        level_mapping = {
            "lsoa": ("boundaries", "area_code", "area_name"),
            "local_authority": ("local_authorities", "la_code", "la_name"),
            "region": ("regions", "region_code", "region_name"),
        }

        table, code_col, name_col = level_mapping.get(
            aggregation_level, ("boundaries", "area_code", "area_name")
        )

        query = f"""
            SELECT
                a.{code_col} as area_code,
                a.{name_col} as area_name,
                AVG(s.metric_value) as avg_value,
                COUNT(DISTINCT e.urn) as school_count
            FROM education.{table} a
            JOIN education.establishments e ON ST_Contains(a.geometry, e.geometry)
            LEFT JOIN education.school_statistics s ON e.urn = s.urn AND s.metric_name = ?
            WHERE a.nation = ?
            GROUP BY a.{code_col}, a.{name_col}
            HAVING COUNT(DISTINCT e.urn) > 0
            ORDER BY avg_value {"DESC" if order == "desc" else "ASC"} NULLS LAST
            LIMIT ?
        """

        results = conn.execute(query, [metric, nation, top_n]).fetchall()

        areas = [
            AreaStatistics(
                area_code=row[0],
                area_name=row[1],
                nation=nation,
                school_count=row[3],
                metrics={metric: row[2]} if row[2] else {},
            )
            for row in results
        ]

        # Get totals
        totals_query = f"""
            SELECT
                COUNT(DISTINCT a.{code_col}) as total_areas,
                COUNT(DISTINCT e.urn) as total_schools
            FROM education.{table} a
            JOIN education.establishments e ON ST_Contains(a.geometry, e.geometry)
            WHERE a.nation = ?
        """
        totals = conn.execute(totals_query, [nation]).fetchone()

        return SpatialAggregation(
            aggregation_level=aggregation_level,
            areas=areas,
            total_areas=totals[0],
            total_schools=totals[1],
        )

    finally:
        conn.close()


async def find_nearby_schools(
    latitude: float = Field(description="Latitude of location"),
    longitude: float = Field(description="Longitude of location"),
    radius_km: float = Field(default=5.0, description="Search radius in kilometers"),
    school_type: str | None = Field(default=None, description="Filter by school type"),
    limit: int = Field(default=20, description="Maximum results"),
    tool_context: ToolContext = None,
) -> list[NearbySchool]:
    """
    Find schools near a geographic location.

    Uses DuckDB Spatial for distance calculations.

    Examples:
    - find_nearby_schools(51.5074, -0.1278, 2.0)  # Schools within 2km of central London
    - find_nearby_schools(53.3498, -6.2603, 5.0, school_type="secondary")  # Dublin
    """
    conn = get_connection()

    try:
        # Create point geometry for location
        query = """
            WITH location AS (
                SELECT ST_Point(?, ?) as point
            )
            SELECT
                e.urn,
                e.school_name,
                e.school_type,
                ST_Distance(e.geometry, l.point) / 1000 as distance_km,
                e.nation,
                e.postcode
            FROM education.establishments e, location l
            WHERE ST_DWithin(e.geometry, l.point, ? * 1000)
        """

        params = [longitude, latitude, radius_km]

        if school_type:
            query += " AND e.school_type = ?"
            params.append(school_type)

        query += " ORDER BY distance_km LIMIT ?"
        params.append(limit)

        results = conn.execute(query, params).fetchall()

        return [
            NearbySchool(
                urn=str(row[0]),
                school_name=row[1],
                school_type=row[2],
                distance_km=round(row[3], 2),
                nation=row[4],
                postcode=row[5],
            )
            for row in results
        ]

    finally:
        conn.close()


async def get_deprivation_correlation(
    nation: str = Field(description="Nation code"),
    metric: str = Field(description="Education metric to correlate"),
    tool_context: ToolContext = None,
) -> dict:
    """
    Calculate correlation between education metrics and deprivation.

    Uses deprivation indices (IMD, SIMD, etc.) to analyze
    socioeconomic factors in education outcomes.

    Examples:
    - get_deprivation_correlation("england", "attainment_8")
    - get_deprivation_correlation("scotland", "absence_rate")
    """
    conn = get_connection()

    try:
        query = """
            SELECT
                CORR(d.deprivation_score, s.metric_value) as correlation,
                COUNT(*) as sample_size
            FROM education.deprivation_indices d
            JOIN education.area_statistics s ON d.area_code = s.area_code
            WHERE d.nation = ?
            AND s.metric_name = ?
            AND d.deprivation_score IS NOT NULL
            AND s.metric_value IS NOT NULL
        """

        result = conn.execute(query, [nation, metric]).fetchone()

        correlation = result[0] if result else None
        sample_size = result[1] if result else 0

        # Interpret correlation
        if correlation is not None:
            if abs(correlation) < 0.3:
                strength = "weak"
            elif abs(correlation) < 0.7:
                strength = "moderate"
            else:
                strength = "strong"

            direction = "positive" if correlation > 0 else "negative"
        else:
            strength = "unknown"
            direction = "unknown"

        return {
            "correlation": correlation,
            "sample_size": sample_size,
            "strength": strength,
            "direction": direction,
            "interpretation": f"{strength.title()} {direction} correlation between {metric} and deprivation",
        }

    finally:
        conn.close()
