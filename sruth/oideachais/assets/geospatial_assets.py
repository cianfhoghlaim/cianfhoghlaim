"""
Geospatial Assets for Linguistic Boundaries.

Pipeline for geospatial data focused on:
- Language-speaking area boundaries (Gaeltacht, Welsh-speaking, Gàidhealtachd)
- Dialect region polygons (Munster, Connacht, Ulster)
- Canuint/Dúchas/Hidden Heritage recording locations
- School locations for Celtic-medium education

Asset Hierarchy:
    geospatial.boundaries.gaeltacht (Official Gaeltacht areas)
    geospatial.boundaries.dialect_regions (Munster/Connacht/Ulster)
    geospatial.boundaries.welsh_speaking (Welsh language areas)
    geospatial.boundaries.gaidhealtachd (Scottish Gaelic areas)
    geospatial.locations.canuint (Recording locations)
    geospatial.locations.duchas (Folklore collection locations)
    geospatial.locations.schools (Celtic-medium schools)
    geospatial.aggregated.duchas_by_gaeltacht (Folklore by area)
    geospatial.aggregated.canuint_by_dialect (Recordings by dialect)

Uses DuckDB Spatial extension for geometry operations.
"""
# Note: Removed future annotations for Dagster compatibility


from dagster import (
    AssetKey,
    MaterializeResult,
    asset,
)
from dagster_dlt import DagsterDltResource

from ..resources import DuckDBResource, GeoParquetResource

# ============================================================================
# Gaeltacht Boundaries
# ============================================================================

@asset(
    key=["geospatial", "boundaries", "gaeltacht"],
    group_name="geospatial",
    description="Official Gaeltacht area boundaries from GeoHive.ie",
    compute_kind="dlt",
)
def gaeltacht_boundaries(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Ingest official Gaeltacht boundaries.

    7 Gaeltacht regions:
    - Donegal (Dún na nGall)
    - Mayo (Maigh Eo)
    - Galway (Gaillimh)
    - Kerry (Ciarraí)
    - Cork (Corcaigh)
    - Waterford (Port Láirge)
    - Meath (An Mhí)

    Fields:
    - gaeltacht_id: Unique identifier
    - gaeltacht_name: Irish name
    - county: Parent county
    - geometry: Polygon boundary (WGS84)
    - population: Gaeltacht population
    - irish_speakers_daily: Daily Irish speakers
    """
    context.log.info("Ingesting Gaeltacht boundaries")

    from dlt_sources.geospatial.geohive import geohive_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="gaeltacht_boundaries",
        destination="duckdb",
        dataset_name="geospatial",
    )

    source = geohive_source(layer="gaeltacht")
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    # Also write to GeoParquet for efficient spatial queries
    try:
        import geopandas as gpd
        conn = duckdb.get_connection()

        gdf = gpd.GeoDataFrame.from_postgis(
            "SELECT * FROM geospatial.gaeltacht_boundaries",
            conn,
            geom_col="geometry",
        )

        output_path = geoparquet.write("gaeltacht_boundaries", gdf)
        context.log.info(f"Wrote GeoParquet to {output_path}")
    except Exception as e:
        context.log.warning(f"GeoParquet export failed: {e}")

    return MaterializeResult(
        metadata={
            "gaeltacht_regions": 7,
            "rows_loaded": sum(row_counts.values()),
            "fields": ["gaeltacht_id", "gaeltacht_name", "county", "geometry", "population"],
        }
    )


# ============================================================================
# Dialect Region Boundaries
# ============================================================================

@asset(
    key=["geospatial", "boundaries", "dialect_regions"],
    group_name="geospatial",
    description="Irish dialect region boundaries (Munster/Connacht/Ulster)",
    deps=[AssetKey(["geospatial", "boundaries", "gaeltacht"])],
    compute_kind="spatial",
)
def dialect_region_boundaries(
    context,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Create dialect region boundaries from Gaeltacht aggregation.

    Dialect provinces:
    - Munster (Cúige Mumhan): Kerry, Cork, Waterford Gaeltachts
    - Connacht (Cúige Connacht): Galway, Mayo Gaeltachts
    - Ulster (Cúige Uladh): Donegal Gaeltacht

    Sub-dialects mapped from Canuint areas.
    """
    context.log.info("Creating dialect region boundaries")

    conn = duckdb.get_connection()

    # Map Gaeltachts to dialect provinces
    dialect_mapping = {
        "Ciarraí": "munster",
        "Corcaigh": "munster",
        "Port Láirge": "munster",
        "Gaillimh": "connacht",
        "Maigh Eo": "connacht",
        "Dún na nGall": "ulster",
        "An Mhí": "connacht",  # Ráth Cairn - Connacht dialect
    }

    try:
        # Create aggregated dialect regions
        conn.execute("""
            CREATE OR REPLACE TABLE geospatial.dialect_regions AS
            SELECT
                CASE
                    WHEN county IN ('Ciarraí', 'Corcaigh', 'Port Láirge') THEN 'munster'
                    WHEN county IN ('Gaillimh', 'Maigh Eo', 'An Mhí') THEN 'connacht'
                    WHEN county = 'Dún na nGall' THEN 'ulster'
                END as province,
                CASE
                    WHEN county IN ('Ciarraí', 'Corcaigh', 'Port Láirge') THEN 'Cúige Mumhan'
                    WHEN county IN ('Gaillimh', 'Maigh Eo', 'An Mhí') THEN 'Cúige Connacht'
                    WHEN county = 'Dún na nGall' THEN 'Cúige Uladh'
                END as province_irish,
                ST_Union_Agg(geometry) as geometry,
                SUM(population) as population,
                SUM(irish_speakers_daily) as irish_speakers_daily
            FROM geospatial.gaeltacht_boundaries
            GROUP BY province, province_irish
        """)

        regions_created = 3

        # Write to GeoParquet
        import geopandas as gpd
        gdf = gpd.GeoDataFrame.from_postgis(
            "SELECT * FROM geospatial.dialect_regions",
            conn,
            geom_col="geometry",
        )
        geoparquet.write("dialect_regions", gdf)

    except Exception as e:
        context.log.warning(f"Dialect region creation failed: {e}")
        regions_created = 0

    return MaterializeResult(
        metadata={
            "dialect_regions": regions_created,
            "provinces": ["munster", "connacht", "ulster"],
        }
    )


# ============================================================================
# Welsh-Speaking Areas
# ============================================================================

@asset(
    key=["geospatial", "boundaries", "welsh_speaking"],
    group_name="geospatial",
    description="Welsh-speaking area boundaries from Census data",
    compute_kind="dlt",
)
def welsh_speaking_boundaries(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Ingest Welsh-speaking area boundaries.

    Based on Census 2021 Welsh language data by LSOA.

    Fields:
    - lsoa_code: LSOA identifier
    - lsoa_name: LSOA name
    - geometry: Polygon boundary
    - welsh_speakers_pct: Percentage Welsh speakers
    - welsh_speakers_count: Number of Welsh speakers
    """
    context.log.info("Ingesting Welsh-speaking boundaries")

    from dlt_sources.geospatial.ons_lsoa import ons_lsoa_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="welsh_speaking",
        destination="duckdb",
        dataset_name="geospatial",
    )

    source = ons_lsoa_source(nation="wales", include_language_data=True)
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "lsoas_loaded": sum(row_counts.values()),
            "nation": "wales",
        }
    )


# ============================================================================
# Scottish Gaelic Areas (Gàidhealtachd)
# ============================================================================

@asset(
    key=["geospatial", "boundaries", "gaidhealtachd"],
    group_name="geospatial",
    description="Scottish Gaelic speaking area boundaries",
    compute_kind="dlt",
)
def gaidhealtachd_boundaries(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Ingest Gàidhealtachd (Scottish Gaelic-speaking area) boundaries.

    Based on Census 2022 Gaelic language data.

    Fields:
    - datazone_code: Scottish Data Zone
    - council_area: Local authority
    - geometry: Polygon boundary
    - gd_speakers_pct: Percentage Gaelic speakers
    - gd_speakers_count: Number of Gaelic speakers
    """
    context.log.info("Ingesting Gàidhealtachd boundaries")

    from dlt_sources.geospatial.scotland_gov import scotland_datazones_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="gaidhealtachd",
        destination="duckdb",
        dataset_name="geospatial",
    )

    source = scotland_datazones_source(include_gaelic_data=True)
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "datazones_loaded": sum(row_counts.values()),
            "nation": "scotland",
        }
    )


# ============================================================================
# Canuint Recording Locations
# ============================================================================

@asset(
    key=["geospatial", "locations", "canuint"],
    group_name="geospatial",
    description="Canuint pronunciation recording locations",
    deps=[
        AssetKey(["celtic", "pronunciation", "areas"]),
        AssetKey(["geospatial", "boundaries", "gaeltacht"]),
    ],
    compute_kind="spatial",
)
def canuint_locations(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Extract Canuint recording locations.

    Creates point geometries from Canuint areas and links to Gaeltacht boundaries.

    Fields:
    - area_id: Canuint area identifier
    - area_name: Irish name (e.g., "Múscraí", "Cois Fharraige")
    - province: Dialect province (Munster/Connacht/Ulster)
    - geometry: Point location (centroid of associated Gaeltacht)
    - recording_count: Number of recordings from this location
    """
    context.log.info("Creating Canuint location points")

    conn = duckdb.get_connection()

    # Map Canuint areas to Gaeltacht locations
    area_gaeltacht_mapping = {
        "Múscraí": "Corcaigh",
        "Corca Dhuibhne": "Ciarraí",
        "Iarthar Dhún na nGall": "Dún na nGall",
        "Cois Fharraige": "Gaillimh",
        "Conamara Theas": "Gaillimh",
        "Árainn": "Gaillimh",
    }

    try:
        conn.execute("""
            CREATE OR REPLACE TABLE geospatial.canuint_locations AS
            SELECT
                ca.area_id,
                ca.area_name,
                ca.province,
                ST_Centroid(gb.geometry) as geometry,
                COUNT(cr.recording_id) as recording_count
            FROM celtic.canuint_areas ca
            LEFT JOIN geospatial.gaeltacht_boundaries gb
                ON ca.area_name LIKE '%' || gb.gaeltacht_name || '%'
            LEFT JOIN celtic.canuint_recordings cr
                ON cr.area_id = ca.area_id
            GROUP BY ca.area_id, ca.area_name, ca.province, gb.geometry
        """)

        row_count = conn.execute("SELECT COUNT(*) FROM geospatial.canuint_locations").fetchone()[0]

    except Exception as e:
        context.log.warning(f"Canuint location creation failed: {e}")
        row_count = 0

    return MaterializeResult(
        metadata={
            "locations_created": row_count,
            "fields": ["area_id", "area_name", "province", "geometry", "recording_count"],
        }
    )


# ============================================================================
# Dúchas Collection Locations
# ============================================================================

@asset(
    key=["geospatial", "locations", "duchas"],
    group_name="geospatial",
    description="Dúchas folklore collection locations with coordinates",
    deps=[
        AssetKey(["celtic", "folklore", "volumes"]),
        AssetKey(["celtic", "gaois", "placenames"]),
    ],
    compute_kind="spatial",
)
def duchas_locations(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Extract Dúchas collection locations.

    Links folklore collection points to Logainm placenames for coordinates.

    Fields:
    - volume_id: Dúchas volume identifier
    - county: Collection county
    - townland: Townland name
    - logainm_id: Link to placename database
    - geometry: Point location (from Logainm or county centroid)
    - item_count: Number of folklore items
    """
    context.log.info("Creating Dúchas location points")

    conn = duckdb.get_connection()

    try:
        conn.execute("""
            CREATE OR REPLACE TABLE geospatial.duchas_locations AS
            SELECT
                dv.volume_id,
                dv.county,
                dv.townland,
                dv.logainm_id,
                COALESCE(
                    ST_Point(lp.lon, lp.lat),
                    ST_Point(dv.lon, dv.lat)
                ) as geometry,
                COUNT(*) as item_count
            FROM celtic.duchas_volumes dv
            LEFT JOIN celtic.logainm_placenames lp
                ON dv.logainm_id = lp.logainm_id
            WHERE dv.lat IS NOT NULL OR lp.lat IS NOT NULL
            GROUP BY dv.volume_id, dv.county, dv.townland, dv.logainm_id,
                     dv.lat, dv.lon, lp.lat, lp.lon
        """)

        row_count = conn.execute("SELECT COUNT(*) FROM geospatial.duchas_locations").fetchone()[0]

    except Exception as e:
        context.log.warning(f"Dúchas location creation failed: {e}")
        row_count = 0

    return MaterializeResult(
        metadata={
            "locations_created": row_count,
            "fields": ["volume_id", "county", "townland", "logainm_id", "geometry", "item_count"],
        }
    )


# ============================================================================
# Celtic-Medium Schools Locations
# ============================================================================

@asset(
    key=["geospatial", "locations", "schools"],
    group_name="geospatial",
    description="Celtic-medium school locations across all nations",
    compute_kind="dlt",
)
def celtic_medium_schools(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Ingest Celtic-medium school locations.

    Sources:
    - Ireland: Gaelscoileanna, Gaeltacht schools
    - Northern Ireland: Irish-medium schools
    - Scotland: Gaelic-medium units
    - Wales: Welsh-medium schools
    - Isle of Man: Bunscoill Ghaelgagh

    Fields:
    - school_id: Unique identifier
    - school_name: School name
    - nation: Country
    - language: Celtic language (ga/gd/cy/gv)
    - medium_type: fully_immersion, partial, subject_only
    - geometry: Point location
    - pupil_count: Number of pupils
    """
    context.log.info("Ingesting Celtic-medium school locations")

    from dlt_sources.geospatial.schools import celtic_schools_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="celtic_medium_schools",
        destination="duckdb",
        dataset_name="geospatial",
    )

    source = celtic_schools_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "schools_loaded": sum(row_counts.values()),
            "nations": ["ireland", "northern_ireland", "scotland", "wales", "isle_of_man"],
            "languages": ["ga", "gd", "cy", "gv"],
        }
    )


# ============================================================================
# Aggregated: Dúchas by Gaeltacht
# ============================================================================

@asset(
    key=["geospatial", "aggregated", "duchas_by_gaeltacht"],
    group_name="geospatial",
    description="Folklore items aggregated by Gaeltacht region",
    deps=[
        AssetKey(["geospatial", "locations", "duchas"]),
        AssetKey(["geospatial", "boundaries", "gaeltacht"]),
    ],
    compute_kind="spatial",
)
def duchas_by_gaeltacht(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Aggregate Dúchas folklore by Gaeltacht region.

    Spatial join to count folklore items per Gaeltacht.
    """
    context.log.info("Aggregating Dúchas by Gaeltacht")

    conn = duckdb.get_connection()

    try:
        conn.execute("""
            CREATE OR REPLACE TABLE geospatial.duchas_by_gaeltacht AS
            SELECT
                gb.gaeltacht_id,
                gb.gaeltacht_name,
                gb.county,
                gb.geometry,
                COUNT(dl.volume_id) as folklore_volumes,
                SUM(dl.item_count) as folklore_items
            FROM geospatial.gaeltacht_boundaries gb
            LEFT JOIN geospatial.duchas_locations dl
                ON ST_Contains(gb.geometry, dl.geometry)
            GROUP BY gb.gaeltacht_id, gb.gaeltacht_name, gb.county, gb.geometry
        """)

        row_count = conn.execute("SELECT COUNT(*) FROM geospatial.duchas_by_gaeltacht").fetchone()[0]

    except Exception as e:
        context.log.warning(f"Dúchas aggregation failed: {e}")
        row_count = 0

    return MaterializeResult(
        metadata={
            "gaeltacht_regions": row_count,
        }
    )


# ============================================================================
# Aggregated: Canuint by Dialect
# ============================================================================

@asset(
    key=["geospatial", "aggregated", "canuint_by_dialect"],
    group_name="geospatial",
    description="Pronunciation recordings aggregated by dialect region",
    deps=[
        AssetKey(["geospatial", "locations", "canuint"]),
        AssetKey(["geospatial", "boundaries", "dialect_regions"]),
    ],
    compute_kind="spatial",
)
def canuint_by_dialect(
    context,
    duckdb: DuckDBResource,
) -> MaterializeResult:
    """
    Aggregate Canuint recordings by dialect region.

    Counts recordings and unique words per dialect province.
    """
    context.log.info("Aggregating Canuint by dialect")

    conn = duckdb.get_connection()

    try:
        conn.execute("""
            CREATE OR REPLACE TABLE geospatial.canuint_by_dialect AS
            SELECT
                dr.province,
                dr.province_irish,
                dr.geometry,
                COUNT(DISTINCT cl.area_id) as recording_areas,
                SUM(cl.recording_count) as total_recordings
            FROM geospatial.dialect_regions dr
            LEFT JOIN geospatial.canuint_locations cl
                ON ST_Contains(dr.geometry, cl.geometry)
            GROUP BY dr.province, dr.province_irish, dr.geometry
        """)

        row_count = conn.execute("SELECT COUNT(*) FROM geospatial.canuint_by_dialect").fetchone()[0]

    except Exception as e:
        context.log.warning(f"Canuint aggregation failed: {e}")
        row_count = 0

    return MaterializeResult(
        metadata={
            "dialect_regions": row_count,
        }
    )


# ============================================================================
# Irish Small Areas (CSO)
# ============================================================================

@asset(
    key=["geospatial", "boundaries", "irish_small_areas"],
    group_name="geospatial",
    description="CSO Small Areas (18,641 areas) with deprivation data",
    compute_kind="dlt",
)
def irish_small_areas(
    context,
    dlt: DagsterDltResource,
    duckdb: DuckDBResource,
    geoparquet: GeoParquetResource,
) -> MaterializeResult:
    """
    Ingest CSO Small Areas from GeoHive.ie.

    18,641 statistical areas with HP Deprivation Index.

    Fields:
    - sa_2016: Small Area code
    - county: County name
    - ed_name: Electoral Division
    - geometry: Polygon boundary
    - population: 2022 population
    - hp_deprivation: HP Deprivation Index score
    """
    context.log.info("Ingesting Irish Small Areas")

    from dlt_sources.geospatial.cso_small_areas import cso_small_areas_source

    pipeline = dlt.build_dlt_pipeline(
        pipeline_name="irish_small_areas",
        destination="duckdb",
        dataset_name="geospatial",
    )

    source = cso_small_areas_source()
    load_info = pipeline.run(source)

    row_counts = pipeline.last_trace.last_normalize_info.row_counts if pipeline.last_trace else {}

    return MaterializeResult(
        metadata={
            "small_areas_loaded": sum(row_counts.values()),
            "expected_count": 18641,
        }
    )


# ============================================================================
# Export All Assets
# ============================================================================

geospatial_assets = [
    gaeltacht_boundaries,
    dialect_region_boundaries,
    welsh_speaking_boundaries,
    gaidhealtachd_boundaries,
    canuint_locations,
    duchas_locations,
    celtic_medium_schools,
    duchas_by_gaeltacht,
    canuint_by_dialect,
    irish_small_areas,
]
