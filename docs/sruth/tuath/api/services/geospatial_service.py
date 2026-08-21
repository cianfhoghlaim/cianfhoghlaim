"""
Geospatial Service for Tuath.

Provides Celtic language area boundaries and spatial queries.
"""

from pathlib import Path
from typing import Any

import duckdb


class GeospatialService:
    """Service for Celtic geospatial queries."""

    def __init__(self, db_path: str):
        """Initialize DuckDB connection with spatial extension."""
        self.db_path = db_path
        self._conn = None

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        """Get or create connection with spatial extension."""
        if self._conn is None:
            self._conn = duckdb.connect(self.db_path)
            self._conn.execute("INSTALL spatial; LOAD spatial;")
        return self._conn

    def close(self):
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    async def get_gaeltacht_boundaries(
        self,
        county: str | None = None,
    ) -> list[dict]:
        """Get Irish Gaeltacht boundaries."""
        try:
            if county:
                results = self.conn.execute(
                    """
                    SELECT name, county, population, area_km2,
                           ST_AsGeoJSON(geometry) as geojson
                    FROM geospatial.gaeltacht_boundaries
                    WHERE county = ?
                    """,
                    [county],
                ).fetchall()
            else:
                results = self.conn.execute(
                    """
                    SELECT name, county, population, area_km2,
                           ST_AsGeoJSON(geometry) as geojson
                    FROM geospatial.gaeltacht_boundaries
                    """,
                ).fetchall()

            return [
                {
                    "name": r[0],
                    "county": r[1],
                    "population": r[2],
                    "area_km2": r[3],
                    "geojson": r[4],
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_welsh_language_areas(
        self,
        min_percentage: float = 0.0,
    ) -> list[dict]:
        """Get Welsh language areas."""
        try:
            results = self.conn.execute(
                """
                SELECT name, welsh_speakers_pct, population,
                       ST_AsGeoJSON(geometry) as geojson
                FROM geospatial.welsh_language_areas
                WHERE welsh_speakers_pct >= ?
                ORDER BY welsh_speakers_pct DESC
                """,
                [min_percentage],
            ).fetchall()

            return [
                {
                    "name": r[0],
                    "welsh_speakers_pct": r[1],
                    "population": r[2],
                    "geojson": r[3],
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_gaelic_communities(
        self,
        region: str | None = None,
    ) -> list[dict]:
        """Get Scottish Gaelic community areas."""
        try:
            if region:
                results = self.conn.execute(
                    """
                    SELECT name, region, gaelic_speakers_pct, population,
                           ST_AsGeoJSON(geometry) as geojson
                    FROM geospatial.gaelic_communities
                    WHERE region = ?
                    """,
                    [region],
                ).fetchall()
            else:
                results = self.conn.execute(
                    """
                    SELECT name, region, gaelic_speakers_pct, population,
                           ST_AsGeoJSON(geometry) as geojson
                    FROM geospatial.gaelic_communities
                    ORDER BY gaelic_speakers_pct DESC
                    """,
                ).fetchall()

            return [
                {
                    "name": r[0],
                    "region": r[1],
                    "gaelic_speakers_pct": r[2],
                    "population": r[3],
                    "geojson": r[4],
                }
                for r in results
            ]
        except Exception:
            return []

    async def point_in_celtic_area(
        self,
        latitude: float,
        longitude: float,
    ) -> dict | None:
        """Check if a point is within a Celtic language area."""
        try:
            result = self.conn.execute(
                """
                SELECT 'gaeltacht' as area_type, name, county as region
                FROM geospatial.gaeltacht_boundaries
                WHERE ST_Contains(geometry, ST_Point(?, ?))
                UNION ALL
                SELECT 'welsh' as area_type, name, NULL as region
                FROM geospatial.welsh_language_areas
                WHERE ST_Contains(geometry, ST_Point(?, ?))
                UNION ALL
                SELECT 'gaelic' as area_type, name, region
                FROM geospatial.gaelic_communities
                WHERE ST_Contains(geometry, ST_Point(?, ?))
                LIMIT 1
                """,
                [longitude, latitude, longitude, latitude, longitude, latitude],
            ).fetchone()

            if result:
                return {
                    "in_celtic_area": True,
                    "area_type": result[0],
                    "name": result[1],
                    "region": result[2],
                    "latitude": latitude,
                    "longitude": longitude,
                }
            return {
                "in_celtic_area": False,
                "latitude": latitude,
                "longitude": longitude,
            }
        except Exception:
            return None

    async def nearby_celtic_areas(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
        limit: int = 10,
    ) -> list[dict]:
        """Find Celtic language areas near a point."""
        try:
            results = self.conn.execute(
                """
                WITH point AS (SELECT ST_Point(?, ?) as geom)
                SELECT 'gaeltacht' as area_type, name, county as region,
                       ST_Distance(ST_Centroid(geometry), point.geom) * 111 as distance_km
                FROM geospatial.gaeltacht_boundaries, point
                WHERE ST_Distance(ST_Centroid(geometry), point.geom) * 111 <= ?
                UNION ALL
                SELECT 'welsh' as area_type, name, NULL as region,
                       ST_Distance(ST_Centroid(geometry), point.geom) * 111 as distance_km
                FROM geospatial.welsh_language_areas, point
                WHERE ST_Distance(ST_Centroid(geometry), point.geom) * 111 <= ?
                UNION ALL
                SELECT 'gaelic' as area_type, name, region,
                       ST_Distance(ST_Centroid(geometry), point.geom) * 111 as distance_km
                FROM geospatial.gaelic_communities, point
                WHERE ST_Distance(ST_Centroid(geometry), point.geom) * 111 <= ?
                ORDER BY distance_km
                LIMIT ?
                """,
                [longitude, latitude, radius_km, radius_km, radius_km, limit],
            ).fetchall()

            return [
                {
                    "area_type": r[0],
                    "name": r[1],
                    "region": r[2],
                    "distance_km": round(r[3], 2),
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_game_world_zones(self) -> list[dict]:
        """Get game world zones for Celtic MMO."""
        try:
            zones = []

            gaeltacht = await self.get_gaeltacht_boundaries()
            for area in gaeltacht:
                zones.append(
                    {
                        "zone_id": f"gaeltacht_{area['name'].lower().replace(' ', '_')}",
                        "zone_name": area["name"],
                        "zone_type": "gaeltacht",
                        "language": "irish",
                        "real_world_location": area["county"],
                        "geojson": area["geojson"],
                    }
                )

            welsh = await self.get_welsh_language_areas(min_percentage=50)
            for area in welsh:
                zones.append(
                    {
                        "zone_id": f"welsh_{area['name'].lower().replace(' ', '_')}",
                        "zone_name": area["name"],
                        "zone_type": "welsh_heartland",
                        "language": "welsh",
                        "welsh_speakers_pct": area["welsh_speakers_pct"],
                        "geojson": area["geojson"],
                    }
                )

            gaelic = await self.get_gaelic_communities()
            for area in gaelic:
                zones.append(
                    {
                        "zone_id": f"alba_{area['name'].lower().replace(' ', '_')}",
                        "zone_name": area["name"],
                        "zone_type": "gaidhealtachd",
                        "language": "scottish_gaelic",
                        "real_world_location": area["region"],
                        "geojson": area["geojson"],
                    }
                )

            return zones
        except Exception:
            return []

    def list_counties(self) -> list[str]:
        """List Irish counties with Gaeltacht areas."""
        try:
            result = self.conn.execute(
                "SELECT DISTINCT county FROM geospatial.gaeltacht_boundaries ORDER BY county"
            ).fetchall()
            return [r[0] for r in result]
        except Exception:
            return []

    def list_regions(self) -> list[str]:
        """List Scottish regions with Gaelic communities."""
        try:
            result = self.conn.execute(
                "SELECT DISTINCT region FROM geospatial.gaelic_communities ORDER BY region"
            ).fetchall()
            return [r[0] for r in result]
        except Exception:
            return []

    def get_stats(self) -> dict:
        """Get geospatial data statistics."""
        try:
            gaeltacht = self.conn.execute(
                "SELECT COUNT(*), SUM(population), SUM(area_km2) FROM geospatial.gaeltacht_boundaries"
            ).fetchone()
            welsh = self.conn.execute(
                "SELECT COUNT(*), SUM(population) FROM geospatial.welsh_language_areas"
            ).fetchone()
            gaelic = self.conn.execute(
                "SELECT COUNT(*), SUM(population) FROM geospatial.gaelic_communities"
            ).fetchone()

            return {
                "gaeltacht": {
                    "areas": gaeltacht[0] or 0,
                    "population": gaeltacht[1] or 0,
                    "area_km2": gaeltacht[2] or 0,
                },
                "welsh": {
                    "areas": welsh[0] or 0,
                    "population": welsh[1] or 0,
                },
                "gaelic": {
                    "areas": gaelic[0] or 0,
                    "population": gaelic[1] or 0,
                },
            }
        except Exception:
            return {
                "gaeltacht": {"areas": 0, "population": 0, "area_km2": 0},
                "welsh": {"areas": 0, "population": 0},
                "gaelic": {"areas": 0, "population": 0},
            }
