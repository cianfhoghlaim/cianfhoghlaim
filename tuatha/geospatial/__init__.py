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

from .geoparquet_writer import (
    get_geoparquet_metadata,
    list_partitions,
    read_geoparquet,
    write_geoparquet,
    write_nation_partitioned,
)
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

__all__ = [
    "AREA_CODE_PATTERNS",
    "NATION_CONFIGS",
    # Multi-country
    "NationBoundaryConfig",
    "add_centroid_columns",
    "add_dialect_region_index",
    "add_gaeltacht_h3_index",
    # Hilbert indexing
    "add_hilbert_index",
    "aggregate_by_area",
    "aggregate_by_area_sql",
    "compute_h3_neighbors",
    "compute_spatial_extent",
    "create_hilbert_partitions",
    "create_nation_partitions",
    "get_celtic_language_areas",
    # Spatial joins
    "get_duckdb_spatial_connection",
    "get_geoparquet_metadata",
    "get_h3_cells_for_bbox",
    "get_nation_boundary_config",
    "get_nation_from_area_code",
    "get_summary_by_nation",
    "h3_to_boundary",
    "join_schools_to_areas",
    "join_to_gaeltacht",
    "join_to_language_areas",
    "list_partitions",
    "load_unified_boundaries",
    "normalize_area_codes",
    "query_area_statistics",
    "query_nearby_areas",
    "read_geoparquet",
    # GeoParquet
    "write_geoparquet",
    "write_nation_partitioned",
]
