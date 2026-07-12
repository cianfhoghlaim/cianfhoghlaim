"""
DuckDB Spatial joins for Celtic education data.

Joins school locations to statistical area boundaries
across all six nations and aggregates statistics by area.

Supports:
- Ireland: CSO Small Areas, Gaeltacht boundaries
- England/Wales: LSOA
- Scotland: Data Zones
- Northern Ireland: SOA
- Welsh/Gaelic language areas
"""


import duckdb
import geopandas as gpd
import pandas as pd


def get_duckdb_spatial_connection(db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    """
    Get DuckDB connection with spatial extension loaded.

    Args:
        db_path: Path to database file (None for in-memory)

    Returns:
        DuckDB connection with spatial extension
    """
    conn = duckdb.connect(db_path or ":memory:")
    conn.install_extension("spatial")
    conn.load_extension("spatial")
    return conn


def join_schools_to_areas(
    schools_gdf: gpd.GeoDataFrame,
    boundaries_gdf: gpd.GeoDataFrame,
    area_code_column: str = "area_code",
    nation_column: str | None = "nation",
    method: str = "duckdb",
) -> gpd.GeoDataFrame:
    """
    Spatially join schools to statistical area boundaries.

    Args:
        schools_gdf: GeoDataFrame with school point locations
        boundaries_gdf: GeoDataFrame with area polygons
        area_code_column: Name of area code column in boundaries
        nation_column: Optional nation column to include
        method: Join method ("duckdb" or "geopandas")

    Returns:
        Schools GeoDataFrame with added area code column
    """
    if method == "duckdb":
        return _join_with_duckdb(schools_gdf, boundaries_gdf, area_code_column, nation_column)
    else:
        return _join_with_geopandas(schools_gdf, boundaries_gdf, area_code_column, nation_column)


def _join_with_duckdb(
    schools_gdf: gpd.GeoDataFrame,
    boundaries_gdf: gpd.GeoDataFrame,
    area_code_column: str,
    nation_column: str | None,
) -> gpd.GeoDataFrame:
    """Use DuckDB Spatial for the join."""
    conn = get_duckdb_spatial_connection()

    # Register GeoDataFrames as views
    # Convert to WKB for DuckDB
    schools_df = schools_gdf.copy()
    schools_df["geometry_wkb"] = schools_gdf.geometry.to_wkb()

    boundaries_df = boundaries_gdf.copy()
    boundaries_df["geometry_wkb"] = boundaries_gdf.geometry.to_wkb()

    conn.register("schools", schools_df)
    conn.register("boundaries", boundaries_df)

    # Build nation column select if present
    nation_select = f", b.{nation_column} as matched_nation" if nation_column and nation_column in boundaries_df.columns else ""

    # Perform spatial join
    result = conn.execute(f"""
        SELECT
            s.*,
            b.{area_code_column} as matched_area_code
            {nation_select}
        FROM schools s
        LEFT JOIN boundaries b
        ON ST_Contains(
            ST_GeomFromWKB(b.geometry_wkb),
            ST_GeomFromWKB(s.geometry_wkb)
        )
    """).fetchdf()

    conn.close()

    # Convert back to GeoDataFrame
    result_gdf = gpd.GeoDataFrame(
        result.drop(columns=["geometry_wkb"]),
        geometry=schools_gdf.geometry,
        crs=schools_gdf.crs,
    )

    return result_gdf


def _join_with_geopandas(
    schools_gdf: gpd.GeoDataFrame,
    boundaries_gdf: gpd.GeoDataFrame,
    area_code_column: str,
    nation_column: str | None,
) -> gpd.GeoDataFrame:
    """Use GeoPandas for the join."""
    # Ensure same CRS
    if schools_gdf.crs != boundaries_gdf.crs:
        boundaries_gdf = boundaries_gdf.to_crs(schools_gdf.crs)

    # Select columns to join
    join_cols = [area_code_column, "geometry"]
    if nation_column and nation_column in boundaries_gdf.columns:
        join_cols.insert(1, nation_column)

    # Perform spatial join
    joined = gpd.sjoin(
        schools_gdf,
        boundaries_gdf[join_cols],
        how="left",
        predicate="within",
    )

    # Rename and clean up
    joined = joined.rename(columns={area_code_column: "matched_area_code"})
    if nation_column:
        joined = joined.rename(columns={nation_column: "matched_nation"})
    joined = joined.drop(columns=["index_right"], errors="ignore")

    return joined


def join_to_gaeltacht(
    gdf: gpd.GeoDataFrame,
    gaeltacht_boundaries: gpd.GeoDataFrame,
    gaeltacht_name_column: str = "gaeltacht_name",
) -> gpd.GeoDataFrame:
    """
    Join locations to Gaeltacht boundaries.

    Args:
        gdf: GeoDataFrame with point or polygon geometries
        gaeltacht_boundaries: GeoDataFrame with Gaeltacht polygons
        gaeltacht_name_column: Column containing Gaeltacht region name

    Returns:
        GeoDataFrame with is_gaeltacht and gaeltacht_name columns
    """
    # Ensure same CRS
    if gdf.crs != gaeltacht_boundaries.crs:
        gaeltacht_boundaries = gaeltacht_boundaries.to_crs(gdf.crs)

    # Perform spatial join
    joined = gpd.sjoin(
        gdf,
        gaeltacht_boundaries[[gaeltacht_name_column, "geometry"]],
        how="left",
        predicate="within" if gdf.geometry.type.iloc[0] == "Point" else "intersects",
    )

    # Add is_gaeltacht flag
    joined["is_gaeltacht"] = joined[gaeltacht_name_column].notna()

    # Clean up
    joined = joined.drop(columns=["index_right"], errors="ignore")

    return joined


def join_to_language_areas(
    gdf: gpd.GeoDataFrame,
    language_areas: gpd.GeoDataFrame,
    language: str = "irish",
    threshold_column: str = "speakers_pct",
    threshold: float = 0.0,
) -> gpd.GeoDataFrame:
    """
    Join locations to Celtic language speaking areas.

    Args:
        gdf: GeoDataFrame with geometries
        language_areas: GeoDataFrame with language area polygons
        language: Language code (irish, welsh, gaelic)
        threshold_column: Column with speaker percentage
        threshold: Minimum speaker percentage to include

    Returns:
        GeoDataFrame with language area columns
    """
    # Filter by threshold
    filtered_areas = language_areas[language_areas[threshold_column] >= threshold].copy()

    if filtered_areas.empty:
        gdf[f"{language}_speaking_area"] = False
        gdf[f"{language}_speakers_pct"] = None
        return gdf

    # Ensure same CRS
    if gdf.crs != filtered_areas.crs:
        filtered_areas = filtered_areas.to_crs(gdf.crs)

    # Perform spatial join
    joined = gpd.sjoin(
        gdf,
        filtered_areas[[threshold_column, "geometry"]],
        how="left",
        predicate="within" if gdf.geometry.type.iloc[0] == "Point" else "intersects",
    )

    # Add flags
    joined[f"{language}_speaking_area"] = joined[threshold_column].notna()
    joined[f"{language}_speakers_pct"] = joined[threshold_column]

    # Clean up
    joined = joined.drop(columns=["index_right", threshold_column], errors="ignore")

    return joined


def aggregate_by_area(
    schools_gdf: gpd.GeoDataFrame,
    area_code_column: str = "matched_area_code",
    nation_column: str | None = "matched_nation",
    aggregations: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Aggregate school statistics by statistical area.

    Args:
        schools_gdf: GeoDataFrame with schools joined to areas
        area_code_column: Name of area code column
        nation_column: Optional nation column for grouping
        aggregations: Dictionary of column -> aggregation function

    Returns:
        DataFrame with aggregated statistics per area
    """
    default_aggs = {
        "urn": "count",  # Number of schools (or school_id)
    }

    aggs = {**(aggregations or {}), **default_aggs}

    # Build group columns
    group_cols = [area_code_column]
    if nation_column and nation_column in schools_gdf.columns:
        group_cols.insert(0, nation_column)

    # Group by area and aggregate
    result = schools_gdf.groupby(group_cols).agg(aggs).reset_index()

    # Rename columns
    result = result.rename(columns={"urn": "school_count"})

    return result


def aggregate_by_area_sql(
    db_path: str,
    schools_table: str,
    boundaries_table: str,
    output_table: str,
    metrics: list[str] | None = None,
    include_nation: bool = True,
) -> None:
    """
    Aggregate education statistics by area using DuckDB SQL.

    Args:
        db_path: Path to DuckDB database
        schools_table: Name of schools table
        boundaries_table: Name of boundaries table
        output_table: Name for output table
        metrics: List of metrics to aggregate
        include_nation: Whether to include nation in grouping
    """
    conn = get_duckdb_spatial_connection(db_path)

    metrics = metrics or ["attainment_score", "absence_rate"]

    # Build aggregation expressions
    agg_expressions = []
    for metric in metrics:
        agg_expressions.append(f"AVG({metric}) as avg_{metric}")
        agg_expressions.append(f"MIN({metric}) as min_{metric}")
        agg_expressions.append(f"MAX({metric}) as max_{metric}")

    agg_sql = ",\n            ".join(agg_expressions)

    nation_col = "b.nation," if include_nation else ""
    nation_group = ", b.nation" if include_nation else ""

    conn.execute(f"""
        CREATE OR REPLACE TABLE {output_table} AS
        SELECT
            b.area_code,
            b.area_name,
            {nation_col}
            COUNT(s.*) as school_count,
            {agg_sql}
        FROM {boundaries_table} b
        LEFT JOIN {schools_table} s
        ON ST_Contains(b.geometry, s.geometry)
        GROUP BY b.area_code, b.area_name{nation_group}
    """)

    conn.close()


def query_area_statistics(
    db_path: str,
    area_codes: list[str],
    metrics: list[str] | None = None,
    table_name: str = "education_by_area",
) -> pd.DataFrame:
    """
    Query education statistics for specific areas.

    Args:
        db_path: Path to DuckDB database
        area_codes: List of area codes (LSOA, Small Area, etc.)
        metrics: Specific metrics to return
        table_name: Name of the statistics table

    Returns:
        DataFrame with area statistics
    """
    conn = get_duckdb_spatial_connection(db_path)

    # Build query
    area_list = ", ".join(f"'{code}'" for code in area_codes)

    if metrics:
        columns = ["area_code", "area_name", "nation", "school_count"] + [f"avg_{m}" for m in metrics]
        column_sql = ", ".join(columns)
    else:
        column_sql = "*"

    result = conn.execute(f"""
        SELECT {column_sql}
        FROM {table_name}
        WHERE area_code IN ({area_list})
    """).fetchdf()

    conn.close()

    return result


def query_nearby_areas(
    db_path: str,
    center_lat: float,
    center_lon: float,
    radius_km: float = 10.0,
    limit: int = 20,
) -> pd.DataFrame:
    """
    Query education statistics for areas near a point.

    Args:
        db_path: Path to DuckDB database
        center_lat: Center latitude
        center_lon: Center longitude
        radius_km: Search radius in kilometers
        limit: Maximum number of results

    Returns:
        DataFrame with nearby area statistics
    """
    conn = get_duckdb_spatial_connection(db_path)

    # Create point geometry
    # Use ST_Distance_Spheroid for accurate distance calculation
    result = conn.execute(f"""
        SELECT
            area_code,
            area_name,
            nation,
            school_count,
            ST_Distance_Spheroid(
                centroid,
                ST_Point({center_lon}, {center_lat})
            ) / 1000 as distance_km
        FROM education_by_area
        WHERE ST_Distance_Spheroid(
            centroid,
            ST_Point({center_lon}, {center_lat})
        ) < {radius_km * 1000}
        ORDER BY distance_km
        LIMIT {limit}
    """).fetchdf()

    conn.close()

    return result
