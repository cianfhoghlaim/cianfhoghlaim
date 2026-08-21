"""
Geospatial module for Celtic education data.

Provides spatial indexing, boundary management, and DuckDB Spatial
joins for multi-nation education statistics across:
- Ireland: CSO Small Areas (18,641), Gaeltacht boundaries
- England/Wales: LSOA (36,664 combined)
- Scotland: Data Zones (6,976)
- Northern Ireland: SOA (890)
- Crown Dependencies: Isle of Man, Jersey, Guernsey

Celtic language area support:
- Gaeltacht (Irish)
- Gàidhealtachd (Scottish Gaelic)
- Welsh-speaking areas
- Manx-speaking areas
"""

from .hilbert_indexing import (
    add_centroid_columns,
    add_dialect_region_index,
    add_gaeltacht_h3_index,
    add_hilbert_index,
    compute_h3_neighbors,
    compute_spatial_extent,
    create_hilbert_partitions,
    create_nation_partitions,
    get_h3_cells_for_bbox,
    h3_to_boundary,
)
from .spatial_joins import (
    aggregate_by_area,
    aggregate_by_area_sql,
    get_duckdb_spatial_connection,
    join_schools_to_areas,
    join_to_gaeltacht,
    join_to_language_areas,
    query_area_statistics,
    query_nearby_areas,
)
from .geoparquet_writer import (
    get_geoparquet_metadata,
    list_partitions,
    read_geoparquet,
    write_geoparquet,
    write_nation_partitioned,
)
from .multi_country import (
    AREA_CODE_PATTERNS,
    NATION_CONFIGS,
    NationBoundaryConfig,
    get_celtic_language_areas,
    get_nation_boundary_config,
    get_nation_from_area_code,
    get_summary_by_nation,
    load_unified_boundaries,
    normalize_area_codes,
)

__all__ = [
    # Hilbert indexing
    "add_hilbert_index",
    "create_hilbert_partitions",
    "create_nation_partitions",
    "compute_spatial_extent",
    "add_centroid_columns",
    "compute_h3_neighbors",
    "h3_to_boundary",
    "get_h3_cells_for_bbox",
    "add_gaeltacht_h3_index",
    "add_dialect_region_index",
    # Spatial joins
    "get_duckdb_spatial_connection",
    "join_schools_to_areas",
    "join_to_gaeltacht",
    "join_to_language_areas",
    "aggregate_by_area",
    "aggregate_by_area_sql",
    "query_area_statistics",
    "query_nearby_areas",
    # GeoParquet
    "write_geoparquet",
    "write_nation_partitioned",
    "read_geoparquet",
    "get_geoparquet_metadata",
    "list_partitions",
    # Multi-country
    "NationBoundaryConfig",
    "NATION_CONFIGS",
    "AREA_CODE_PATTERNS",
    "get_nation_boundary_config",
    "get_nation_from_area_code",
    "normalize_area_codes",
    "load_unified_boundaries",
    "get_celtic_language_areas",
    "get_summary_by_nation",
]
