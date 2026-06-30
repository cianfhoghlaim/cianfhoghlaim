"""
GeoParquet file operations for Celtic education data.

Writes and reads GeoParquet files with proper metadata
and optional partitioning by nation or H3 cells.
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import pyarrow.parquet as pq

from .hilbert_indexing import add_hilbert_index


def write_geoparquet(
    gdf: gpd.GeoDataFrame,
    output_path: str | Path,
    partition_by: str | list[str] | None = None,
    add_spatial_index: bool = True,
    compression: str = "zstd",
    row_group_size: int = 100_000,
) -> dict[str, Any]:
    """
    Write GeoDataFrame to GeoParquet format.

    Args:
        gdf: GeoDataFrame to write
        output_path: Output file or directory path
        partition_by: Column(s) to partition by (e.g., "nation" or ["nation", "language"])
        add_spatial_index: Whether to add Hilbert spatial index
        compression: Parquet compression (zstd, snappy, gzip)
        row_group_size: Rows per row group

    Returns:
        Metadata about written file(s)
    """
    output_path = Path(output_path)

    # Add spatial index if requested
    if add_spatial_index:
        gdf = add_hilbert_index(gdf)

    # Ensure geometry is valid
    gdf["geometry"] = gdf.geometry.make_valid()

    # Write with partitioning if specified
    if partition_by:
        return _write_partitioned(
            gdf, output_path, partition_by, compression, row_group_size
        )
    else:
        return _write_single_file(gdf, output_path, compression, row_group_size)


def _write_single_file(
    gdf: gpd.GeoDataFrame,
    output_path: Path,
    compression: str,
    row_group_size: int,
) -> dict[str, Any]:
    """Write single GeoParquet file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write using geopandas
    gdf.to_parquet(
        output_path,
        compression=compression,
        row_group_size=row_group_size,
    )

    return {
        "path": str(output_path),
        "rows": len(gdf),
        "columns": list(gdf.columns),
        "crs": str(gdf.crs) if gdf.crs else None,
        "bounds": list(gdf.total_bounds),
        "compression": compression,
    }


def _write_partitioned(
    gdf: gpd.GeoDataFrame,
    output_dir: Path,
    partition_by: str | list[str],
    compression: str,
    row_group_size: int,
) -> dict[str, Any]:
    """Write partitioned GeoParquet files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(partition_by, str):
        partition_by = [partition_by]

    metadata = {
        "base_path": str(output_dir),
        "partition_columns": partition_by,
        "partitions": [],
        "total_rows": len(gdf),
        "crs": str(gdf.crs) if gdf.crs else None,
        "compression": compression,
    }

    # Group by partition columns
    for keys, group in gdf.groupby(partition_by):
        if not isinstance(keys, tuple):
            keys = (keys,)

        # Build partition path
        partition_parts = []
        for col, val in zip(partition_by, keys, strict=False):
            partition_parts.append(f"{col}={val}")

        partition_path = output_dir / "/".join(partition_parts) / "data.parquet"
        partition_path.parent.mkdir(parents=True, exist_ok=True)

        # Write partition
        group.to_parquet(
            partition_path,
            compression=compression,
            row_group_size=row_group_size,
        )

        metadata["partitions"].append({
            "path": str(partition_path),
            "keys": dict(zip(partition_by, keys, strict=False)),
            "rows": len(group),
        })

    return metadata


def write_nation_partitioned(
    gdf: gpd.GeoDataFrame,
    output_dir: str | Path,
    nation_column: str = "nation",
    compression: str = "zstd",
) -> dict[str, Any]:
    """
    Write GeoParquet partitioned by nation.

    Creates structure:
    output_dir/
        nation=ireland/data.parquet
        nation=england/data.parquet
        nation=scotland/data.parquet
        ...

    Args:
        gdf: GeoDataFrame with nation column
        output_dir: Output directory
        nation_column: Column containing nation code
        compression: Parquet compression

    Returns:
        Metadata about written files
    """
    return write_geoparquet(
        gdf,
        output_dir,
        partition_by=nation_column,
        add_spatial_index=True,
        compression=compression,
    )


def read_geoparquet(
    path: str | Path,
    columns: list[str] | None = None,
    filters: list[tuple] | None = None,
    bbox: tuple[float, float, float, float] | None = None,
    nation: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Read GeoParquet file(s).

    Args:
        path: File path or directory with partitions
        columns: Specific columns to read
        filters: Parquet filters [(column, op, value), ...]
        bbox: Bounding box filter (minx, miny, maxx, maxy)
        nation: Filter by nation (for partitioned data)

    Returns:
        GeoDataFrame
    """
    path = Path(path)

    # Add nation filter if specified
    if nation and filters is None:
        filters = [("nation", "=", nation)]
    elif nation:
        filters = [*filters, ("nation", "=", nation)]

    # Check if directory (partitioned) or file
    if path.is_dir():
        return _read_partitioned(path, columns, filters)
    else:
        return _read_single_file(path, columns, bbox)


def _read_single_file(
    path: Path,
    columns: list[str] | None,
    bbox: tuple[float, float, float, float] | None,
) -> gpd.GeoDataFrame:
    """Read single GeoParquet file."""
    gdf = gpd.read_parquet(path, columns=columns)

    # Apply bbox filter if specified
    if bbox:
        from shapely.geometry import box
        bbox_geom = box(*bbox)
        gdf = gdf[gdf.geometry.intersects(bbox_geom)]

    return gdf


def _read_partitioned(
    base_path: Path,
    columns: list[str] | None,
    filters: list[tuple] | None,
) -> gpd.GeoDataFrame:
    """Read partitioned GeoParquet files."""
    # Find all parquet files
    parquet_files = list(base_path.rglob("*.parquet"))

    if not parquet_files:
        return gpd.GeoDataFrame()

    # Filter files based on partition path if filters specify partition columns
    if filters:
        partition_filters = {}
        for col, op, val in filters:
            if op == "=":
                partition_filters[col] = val

        if partition_filters:
            filtered_files = []
            for file_path in parquet_files:
                rel_path = file_path.relative_to(base_path)
                match = True
                for part in rel_path.parts[:-1]:
                    if "=" in part:
                        col, file_val = part.split("=", 1)
                        if col in partition_filters and partition_filters[col] != file_val:
                            match = False
                            break
                if match:
                    filtered_files.append(file_path)
            parquet_files = filtered_files

    # Read and concatenate
    gdfs = []
    for file_path in parquet_files:
        gdf = gpd.read_parquet(file_path, columns=columns)

        # Extract partition values from path
        rel_path = file_path.relative_to(base_path)
        for part in rel_path.parts[:-1]:
            if "=" in part:
                col, val = part.split("=", 1)
                gdf[col] = val

        gdfs.append(gdf)

    if not gdfs:
        return gpd.GeoDataFrame()

    combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))

    # Apply non-partition filters
    if filters:
        for col, op, val in filters:
            if col not in combined.columns:
                continue
            if op == "=":
                combined = combined[combined[col] == val]
            elif op == "in":
                combined = combined[combined[col].isin(val)]
            elif op == ">":
                combined = combined[combined[col] > val]
            elif op == "<":
                combined = combined[combined[col] < val]

    return combined


def get_geoparquet_metadata(path: str | Path) -> dict[str, Any]:
    """
    Get metadata from GeoParquet file.

    Args:
        path: Path to GeoParquet file

    Returns:
        Metadata dictionary
    """
    path = Path(path)

    # Read parquet metadata
    parquet_file = pq.ParquetFile(path)
    schema = parquet_file.schema_arrow

    # Read geo metadata
    geo_metadata = {}
    if schema.metadata and b"geo" in schema.metadata:
        import json

        geo_metadata = json.loads(schema.metadata[b"geo"])

    return {
        "num_rows": parquet_file.metadata.num_rows,
        "num_row_groups": parquet_file.metadata.num_row_groups,
        "columns": [field.name for field in schema],
        "geo_metadata": geo_metadata,
        "created_by": parquet_file.metadata.created_by,
    }


def list_partitions(path: str | Path) -> list[dict[str, str]]:
    """
    List partitions in a partitioned GeoParquet directory.

    Args:
        path: Path to partitioned directory

    Returns:
        List of partition key dictionaries
    """
    path = Path(path)

    if not path.is_dir():
        return []

    partitions = []
    for parquet_file in path.rglob("*.parquet"):
        rel_path = parquet_file.relative_to(path)
        partition_keys = {}
        for part in rel_path.parts[:-1]:
            if "=" in part:
                col, val = part.split("=", 1)
                partition_keys[col] = val
        if partition_keys:
            partitions.append(partition_keys)

    return partitions
