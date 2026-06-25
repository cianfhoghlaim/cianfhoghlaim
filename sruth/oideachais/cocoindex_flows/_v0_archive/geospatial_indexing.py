"""
Geospatial Indexing Flow.

Indexes geospatial data for map-based search and visualization:
- Location point indexing with H3 cells
- Boundary polygon indexing
- Spatial text embeddings for location-aware search

Data Sources:
- Dúchas folklore locations
- Canuint pronunciation recording locations
- Celtic-medium school locations
- Gaeltacht/dialect region boundaries

Output:
- GeoParquet files for efficient spatial queries
- LanceDB embeddings with location metadata
- H3 cell indexes for hierarchical spatial search
"""
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex imports
try:
    import cocoindex
    from cocoindex import DuckDBSource, ParquetSink, Transform
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class GeospatialIndexConfig:
    """Configuration for geospatial indexing flow."""

    # H3 resolution levels
    h3_resolution_coarse: int = 4   # ~1,700 km² cells (country level)
    h3_resolution_medium: int = 6   # ~36 km² cells (county level)
    h3_resolution_fine: int = 8     # ~0.7 km² cells (townland level)

    # Output paths
    geoparquet_path: str = "./storage/data/geoparquet"
    lancedb_path: str = "./storage/data/lancedb"

    # Location sources
    duchas_table: str = "geospatial.duchas_locations"
    canuint_table: str = "geospatial.canuint_locations"
    schools_table: str = "geospatial.celtic_medium_schools"
    gaeltacht_table: str = "geospatial.gaeltacht_boundaries"


# ============================================================================
# H3 Spatial Indexing
# ============================================================================

class H3SpatialIndexer:
    """
    Spatial indexer using H3 hexagonal grid.

    H3 provides hierarchical spatial indexing with consistent cell sizes,
    enabling efficient spatial queries at multiple resolutions.
    """

    def __init__(self, config: GeospatialIndexConfig | None = None):
        self.config = config or GeospatialIndexConfig()
        self._h3 = None

    def _get_h3(self):
        """Lazy-load H3 library."""
        if self._h3 is None:
            try:
                import h3
                self._h3 = h3
            except ImportError:
                raise ImportError("h3 not installed - install with: pip install h3")
        return self._h3

    def point_to_h3_cells(
        self,
        lat: float,
        lon: float,
    ) -> dict[str, str]:
        """
        Convert point to H3 cells at multiple resolutions.

        Returns dict with h3_coarse, h3_medium, h3_fine cell IDs.
        """
        h3 = self._get_h3()

        return {
            "h3_coarse": h3.geo_to_h3(lat, lon, self.config.h3_resolution_coarse),
            "h3_medium": h3.geo_to_h3(lat, lon, self.config.h3_resolution_medium),
            "h3_fine": h3.geo_to_h3(lat, lon, self.config.h3_resolution_fine),
        }

    def polygon_to_h3_cells(
        self,
        geometry: Any,
        resolution: int = 6,
    ) -> list[str]:
        """
        Convert polygon to covering H3 cells.

        Returns list of H3 cell IDs that cover the polygon.
        """
        h3 = self._get_h3()

        # Extract polygon coordinates
        if hasattr(geometry, "__geo_interface__"):
            geojson = geometry.__geo_interface__
        else:
            geojson = geometry

        if geojson.get("type") == "Polygon":
            coords = geojson["coordinates"][0]
        elif geojson.get("type") == "MultiPolygon":
            coords = geojson["coordinates"][0][0]
        else:
            return []

        # Convert to H3 polyfill
        try:
            cells = h3.polyfill_geojson(geojson, resolution)
            return list(cells)
        except (ValueError, TypeError, KeyError) as e:
            # Fallback: use centroid for invalid polygons
            logger.warning("h3_polyfill_fallback", error=str(e), resolution=resolution)
            centroid_lat = sum(c[1] for c in coords) / len(coords)
            centroid_lon = sum(c[0] for c in coords) / len(coords)
            return [h3.geo_to_h3(centroid_lat, centroid_lon, resolution)]


# ============================================================================
# Location Indexing Transform
# ============================================================================

class LocationIndexTransform:
    """
    Transform that adds H3 spatial indexes to location data.
    """

    def __init__(self, config: GeospatialIndexConfig | None = None):
        self.config = config or GeospatialIndexConfig()
        self.indexer = H3SpatialIndexer(config)

    def process_points(
        self,
        rows: list[dict[str, Any]],
    ) -> Iterator[dict[str, Any]]:
        """
        Add H3 indexes to point location data.
        """
        for row in rows:
            lat = row.get("lat") or row.get("latitude")
            lon = row.get("lon") or row.get("longitude")

            if lat is None or lon is None:
                continue

            try:
                h3_cells = self.indexer.point_to_h3_cells(float(lat), float(lon))
                yield {
                    **row,
                    **h3_cells,
                    "indexed_at": "now()",
                }
            except (ValueError, TypeError) as e:
                logger.debug("h3_point_indexing_failed", lat=lat, lon=lon, error=str(e))
                yield row

    def process_polygons(
        self,
        rows: list[dict[str, Any]],
        resolution: int = 6,
    ) -> Iterator[dict[str, Any]]:
        """
        Add H3 indexes to polygon boundary data.
        """
        for row in rows:
            geometry = row.get("geometry")
            if geometry is None:
                continue

            try:
                h3_cells = self.indexer.polygon_to_h3_cells(geometry, resolution)
                yield {
                    **row,
                    "h3_cells": h3_cells,
                    "h3_cell_count": len(h3_cells),
                    "indexed_at": "now()",
                }
            except (ValueError, TypeError, KeyError) as e:
                logger.debug("h3_polygon_indexing_failed", error=str(e))
                yield row


# ============================================================================
# GeoParquet Writer
# ============================================================================

class GeoParquetWriter:
    """
    Write GeoDataFrames to GeoParquet format.
    """

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)

    def write(
        self,
        table_name: str,
        data: list[dict[str, Any]],
        geometry_column: str = "geometry",
    ) -> Path:
        """
        Write data to GeoParquet.
        """
        import geopandas as gpd
        import pandas as pd
        from shapely import wkt
        from shapely.geometry import Point

        df = pd.DataFrame(data)

        # Convert geometry column
        if geometry_column in df.columns:
            # Handle different geometry formats
            def parse_geom(g):
                if g is None:
                    return None
                if isinstance(g, str):
                    return wkt.loads(g)
                if hasattr(g, "__geo_interface__"):
                    return g
                return None

            df[geometry_column] = df[geometry_column].apply(parse_geom)
        elif "lat" in df.columns and "lon" in df.columns:
            # Create point geometry from lat/lon
            df[geometry_column] = df.apply(
                lambda r: Point(r["lon"], r["lat"]) if r["lat"] and r["lon"] else None,
                axis=1,
            )

        gdf = gpd.GeoDataFrame(df, geometry=geometry_column, crs="EPSG:4326")

        output_file = self.output_path / f"{table_name}.parquet"
        gdf.to_parquet(output_file)

        return output_file


# ============================================================================
# CocoIndex Flow Definition
# ============================================================================

def create_geospatial_indexing_flow(
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
    geoparquet_path: str = "./storage/data/geoparquet",
) -> Any:
    """
    Create CocoIndex flow for geospatial indexing.
    """
    if not COCOINDEX_AVAILABLE:
        raise ImportError("cocoindex not available")

    config = GeospatialIndexConfig(geoparquet_path=geoparquet_path)
    transform = LocationIndexTransform(config)

    @cocoindex.flow(name="geospatial_indexing")
    def geospatial_indexing_flow():
        # Source: Dúchas locations
        duchas_source = DuckDBSource(
            database=duckdb_path,
            query=f"SELECT * FROM {config.duchas_table}",
        )

        # Transform: Add H3 indexes
        duchas_indexed = duchas_source.transform(
            Transform(
                name="index_duchas_locations",
                fn=transform.process_points,
                batch_size=100,
            )
        )

        # Sink: GeoParquet
        duchas_indexed.sink(
            ParquetSink(
                path=f"{geoparquet_path}/duchas_locations.parquet",
            )
        )

        # Source: Canuint locations
        canuint_source = DuckDBSource(
            database=duckdb_path,
            query=f"SELECT * FROM {config.canuint_table}",
        )

        canuint_indexed = canuint_source.transform(
            Transform(
                name="index_canuint_locations",
                fn=transform.process_points,
                batch_size=100,
            )
        )

        canuint_indexed.sink(
            ParquetSink(
                path=f"{geoparquet_path}/canuint_locations.parquet",
            )
        )

    return geospatial_indexing_flow


# ============================================================================
# Standalone Execution
# ============================================================================

def run_geospatial_indexing(
    duckdb_path: str = "./storage/data/celtic_education.duckdb",
    geoparquet_path: str = "./storage/data/geoparquet",
) -> dict[str, int]:
    """
    Run geospatial indexing standalone (without CocoIndex).
    """
    import duckdb

    conn = duckdb.connect(duckdb_path)
    config = GeospatialIndexConfig(geoparquet_path=geoparquet_path)
    transform = LocationIndexTransform(config)
    writer = GeoParquetWriter(geoparquet_path)

    results = {}

    # Process Dúchas locations
    try:
        import duckdb as duckdb_module
        query = f"SELECT * FROM {config.duchas_table}"
        rows = conn.execute(query).fetchall()
        columns = [desc[0] for desc in conn.description]
        data = [dict(zip(columns, row)) for row in rows]

        indexed_data = list(transform.process_points(data))
        output_path = writer.write("duchas_locations", indexed_data)

        results["duchas_locations"] = len(indexed_data)
        logger.info("geospatial_indexing_complete", table="duchas_locations", count=len(indexed_data))
    except (duckdb_module.Error, OSError, ValueError) as e:
        logger.error("geospatial_indexing_failed", table="duchas_locations", error=str(e))
        results["duchas_locations_error"] = str(e)

    # Process Canuint locations
    try:
        query = f"SELECT * FROM {config.canuint_table}"
        rows = conn.execute(query).fetchall()
        columns = [desc[0] for desc in conn.description]
        data = [dict(zip(columns, row)) for row in rows]

        indexed_data = list(transform.process_points(data))
        output_path = writer.write("canuint_locations", indexed_data)

        results["canuint_locations"] = len(indexed_data)
        logger.info("geospatial_indexing_complete", table="canuint_locations", count=len(indexed_data))
    except (duckdb_module.Error, OSError, ValueError) as e:
        logger.error("geospatial_indexing_failed", table="canuint_locations", error=str(e))
        results["canuint_locations_error"] = str(e)

    # Process school locations
    try:
        query = f"SELECT * FROM {config.schools_table}"
        rows = conn.execute(query).fetchall()
        columns = [desc[0] for desc in conn.description]
        data = [dict(zip(columns, row)) for row in rows]

        indexed_data = list(transform.process_points(data))
        output_path = writer.write("celtic_medium_schools", indexed_data)

        results["celtic_medium_schools"] = len(indexed_data)
        logger.info("geospatial_indexing_complete", table="celtic_medium_schools", count=len(indexed_data))
    except (duckdb_module.Error, OSError, ValueError) as e:
        logger.error("geospatial_indexing_failed", table="celtic_medium_schools", error=str(e))
        results["celtic_medium_schools_error"] = str(e)

    conn.close()

    return results


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run geospatial indexing")
    parser.add_argument("--database", default="./storage/data/celtic_education.duckdb")
    parser.add_argument("--output", default="./storage/data/geoparquet")
    args = parser.parse_args()

    results = run_geospatial_indexing(
        duckdb_path=args.database,
        geoparquet_path=args.output,
    )

    for table, count in results.items():
        print(f"{table}: {count}")
