"""
Hilbert curve spatial indexing for GeoParquet.

Uses H3 hexagonal hierarchical indexing for fast spatial queries.
Supports all Celtic education regions including Gaeltacht and language areas.

Reference: Ibis + DuckDB + GeoParquet patterns
"""


import geopandas as gpd
import h3


def add_hilbert_index(
    gdf: gpd.GeoDataFrame,
    h3_resolution: int = 7,
    column_name: str = "hilbert_index",
) -> gpd.GeoDataFrame:
    """
    Add Hilbert curve index to GeoDataFrame for spatial partitioning.

    Uses H3 hexagonal indexing which approximates Hilbert curve properties
    for spatial locality preservation.

    Args:
        gdf: GeoDataFrame with geometry column
        h3_resolution: H3 resolution (0-15, 7 is ~5km cells)
        column_name: Name for the index column

    Returns:
        GeoDataFrame with added Hilbert index column

    Resolution reference:
        - 4: ~22km (nation-level partitioning)
        - 5: ~8km (county-level)
        - 6: ~3km (town-level)
        - 7: ~1.2km (neighborhood-level)
        - 8: ~460m (street-level)
    """
    # Ensure CRS is WGS84 for H3
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    # Get centroids for H3 indexing
    centroids = gdf.geometry.centroid

    # Calculate H3 indices
    h3_indices = []
    for point in centroids:
        if point is None or point.is_empty:
            h3_indices.append(None)
        else:
            try:
                h3_idx = h3.latlng_to_cell(point.y, point.x, h3_resolution)
                h3_indices.append(h3_idx)
            except Exception:
                h3_indices.append(None)

    return gdf.assign(**{column_name: h3_indices})


def create_hilbert_partitions(
    gdf: gpd.GeoDataFrame,
    partition_resolution: int = 4,
) -> dict[str, gpd.GeoDataFrame]:
    """
    Partition GeoDataFrame by Hilbert curve regions.

    Args:
        gdf: GeoDataFrame with geometry
        partition_resolution: H3 resolution for partitioning (lower = larger areas)
                            4 is good for nation-level partitioning

    Returns:
        Dictionary mapping partition keys to GeoDataFrames
    """
    # Add partition index
    gdf_indexed = add_hilbert_index(gdf, h3_resolution=partition_resolution, column_name="partition_key")

    # Group by partition key
    partitions = {}
    for key, group in gdf_indexed.groupby("partition_key"):
        if key is not None:
            partitions[str(key)] = group.copy()

    return partitions


def create_nation_partitions(
    gdf: gpd.GeoDataFrame,
    nation_column: str = "nation",
    sub_partition_resolution: int = 5,
) -> dict[str, dict[str, gpd.GeoDataFrame]]:
    """
    Create two-level partitions: nation -> H3 cells.

    Args:
        gdf: GeoDataFrame with geometry and nation column
        nation_column: Column containing nation code
        sub_partition_resolution: H3 resolution for within-nation partitions

    Returns:
        Nested dictionary: {nation: {h3_cell: GeoDataFrame}}
    """
    nation_partitions = {}

    for nation, nation_gdf in gdf.groupby(nation_column):
        # Create H3 partitions within each nation
        h3_partitions = create_hilbert_partitions(nation_gdf, sub_partition_resolution)
        nation_partitions[str(nation)] = h3_partitions

    return nation_partitions


def compute_spatial_extent(gdf: gpd.GeoDataFrame) -> dict[str, float]:
    """
    Compute spatial extent (bounding box) of GeoDataFrame.

    Args:
        gdf: GeoDataFrame with geometry

    Returns:
        Dictionary with minx, miny, maxx, maxy
    """
    bounds = gdf.total_bounds
    return {
        "minx": float(bounds[0]),
        "miny": float(bounds[1]),
        "maxx": float(bounds[2]),
        "maxy": float(bounds[3]),
    }


def add_centroid_columns(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Add centroid latitude/longitude columns.

    Args:
        gdf: GeoDataFrame with geometry

    Returns:
        GeoDataFrame with centroid_lat and centroid_lon columns
    """
    centroids = gdf.geometry.centroid

    return gdf.assign(
        centroid_lat=centroids.y,
        centroid_lon=centroids.x,
    )


def compute_h3_neighbors(h3_index: str, ring_size: int = 1) -> list[str]:
    """
    Compute neighboring H3 cells.

    Args:
        h3_index: H3 cell index
        ring_size: Number of rings of neighbors to include

    Returns:
        List of neighboring H3 indices
    """
    try:
        return list(h3.grid_disk(h3_index, ring_size))
    except Exception:
        return []


def h3_to_boundary(h3_index: str) -> list[tuple[float, float]]:
    """
    Convert H3 index to polygon boundary coordinates.

    Args:
        h3_index: H3 cell index

    Returns:
        List of (lat, lon) tuples forming the cell boundary
    """
    try:
        return h3.cell_to_boundary(h3_index)
    except Exception:
        return []


def get_h3_cells_for_bbox(
    bbox: tuple[float, float, float, float],
    resolution: int = 7,
) -> list[str]:
    """
    Get all H3 cells covering a bounding box.

    Args:
        bbox: (minx, miny, maxx, maxy) in WGS84
        resolution: H3 resolution

    Returns:
        List of H3 cell indices
    """
    minx, miny, maxx, maxy = bbox

    try:
        from shapely.geometry import box
        bbox_geom = box(minx, miny, maxx, maxy)

        # Convert to H3 polygon cells
        coords = list(bbox_geom.exterior.coords)
        # H3 expects [(lat, lon), ...] format
        h3_coords = [(lat, lon) for lon, lat in coords]

        return list(h3.polygon_to_cells(h3.LatLngPoly(h3_coords), resolution))
    except Exception:
        return []


def add_gaeltacht_h3_index(
    gdf: gpd.GeoDataFrame,
    resolution: int = 6,
) -> gpd.GeoDataFrame:
    """
    Add H3 index optimized for Gaeltacht/Irish-speaking areas.

    Uses resolution 6 (~3km) which aligns well with
    Gaeltacht community boundaries.

    Args:
        gdf: GeoDataFrame with geometry
        resolution: H3 resolution (default 6 for Gaeltacht scale)

    Returns:
        GeoDataFrame with gaeltacht_h3 column
    """
    return add_hilbert_index(gdf, h3_resolution=resolution, column_name="gaeltacht_h3")


def add_dialect_region_index(
    gdf: gpd.GeoDataFrame,
    dialect_boundaries: gpd.GeoDataFrame,
    dialect_column: str = "dialect",
) -> gpd.GeoDataFrame:
    """
    Add dialect region classification based on spatial join with dialect boundaries.

    Args:
        gdf: GeoDataFrame with point or polygon geometries
        dialect_boundaries: GeoDataFrame with dialect region polygons
        dialect_column: Column name in dialect_boundaries containing dialect name

    Returns:
        GeoDataFrame with dialect column added
    """
    # Ensure same CRS
    if gdf.crs != dialect_boundaries.crs:
        dialect_boundaries = dialect_boundaries.to_crs(gdf.crs)

    # Spatial join
    joined = gpd.sjoin(
        gdf,
        dialect_boundaries[[dialect_column, "geometry"]],
        how="left",
        predicate="within" if gdf.geometry.type.iloc[0] == "Point" else "intersects",
    )

    # Clean up
    joined = joined.drop(columns=["index_right"], errors="ignore")

    return joined
