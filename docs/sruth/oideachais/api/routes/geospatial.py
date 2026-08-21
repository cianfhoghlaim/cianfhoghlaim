"""
Geospatial API Routes.

Map data and spatial query endpoints:
- Boundary polygons (Gaeltacht, dialect regions, LSOAs)
- Point locations (schools, recordings, folklore)
- Spatial queries (nearby, within, contains)

Endpoints:
    GET /geo/boundaries/{type} - Get boundary polygons
    GET /geo/locations/{type} - Get point locations
    GET /geo/nearby - Find locations near a point
    GET /geo/within/{boundary_id} - Find locations within a boundary
    GET /geo/stats/{boundary_type} - Aggregated statistics by boundary
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/geo", tags=["geospatial"])


# ============================================================================
# Models
# ============================================================================

class BoundaryType(str, Enum):
    """Available boundary types."""

    GAELTACHT = "gaeltacht"
    DIALECT_REGIONS = "dialect_regions"
    WELSH_SPEAKING = "welsh_speaking"
    GAIDHEALTACHD = "gaidhealtachd"
    IRISH_SMALL_AREAS = "irish_small_areas"


class LocationType(str, Enum):
    """Available location types."""

    DUCHAS = "duchas"
    CANUINT = "canuint"
    SCHOOLS = "schools"


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature."""

    type: str = "Feature"
    id: str | None = None
    geometry: dict[str, Any]
    properties: dict[str, Any] = Field(default_factory=dict)


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection."""

    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]
    metadata: dict[str, Any] = Field(default_factory=dict)


class NearbyRequest(BaseModel):
    """Nearby search request."""

    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lon: float = Field(..., ge=-180, le=180, description="Longitude")
    radius_km: float = Field(default=10, ge=0.1, le=100, description="Search radius in km")
    location_type: LocationType | None = Field(default=None, description="Filter by location type")
    limit: int = Field(default=50, ge=1, le=500)


class BoundaryStats(BaseModel):
    """Statistics for a boundary."""

    boundary_id: str
    boundary_name: str
    geometry: dict[str, Any] | None = None
    stats: dict[str, Any]


# ============================================================================
# Geospatial Implementation
# ============================================================================

class GeospatialService:
    """
    Geospatial service using DuckDB Spatial.
    """

    def __init__(self, duckdb_path: str = "./storage/data/celtic_education.duckdb"):
        self.duckdb_path = duckdb_path
        self._conn = None

    def _get_conn(self):
        """Lazy-load DuckDB connection with spatial extension."""
        if self._conn is None:
            import duckdb
            self._conn = duckdb.connect(self.duckdb_path, read_only=True)
            self._conn.execute("INSTALL spatial; LOAD spatial;")
        return self._conn

    def get_boundaries(
        self,
        boundary_type: BoundaryType,
        simplify: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Get boundary polygons as GeoJSON features.
        """
        conn = self._get_conn()

        table_mapping = {
            BoundaryType.GAELTACHT: "geospatial.gaeltacht_boundaries",
            BoundaryType.DIALECT_REGIONS: "geospatial.dialect_regions",
            BoundaryType.WELSH_SPEAKING: "geospatial.welsh_speaking_boundaries",
            BoundaryType.GAIDHEALTACHD: "geospatial.gaidhealtachd_boundaries",
            BoundaryType.IRISH_SMALL_AREAS: "geospatial.irish_small_areas",
        }

        table = table_mapping.get(boundary_type)
        if not table:
            return []

        # Simplify geometry for smaller responses
        geom_expr = "ST_AsGeoJSON(ST_Simplify(geometry, 0.001))" if simplify else "ST_AsGeoJSON(geometry)"

        try:
            query = f"""
                SELECT
                    *,
                    {geom_expr} as geojson
                FROM {table}
                LIMIT 1000
            """
            results = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description]

            features = []
            for row in results:
                row_dict = dict(zip(columns, row))
                geojson = row_dict.pop("geojson", None)
                geometry = row_dict.pop("geometry", None)

                import json
                geom = json.loads(geojson) if geojson else None

                features.append({
                    "id": row_dict.get("gaeltacht_id") or row_dict.get("province") or str(hash(str(row_dict))),
                    "geometry": geom,
                    "properties": {k: v for k, v in row_dict.items() if v is not None},
                })

            return features

        except Exception as e:
            return []

    def get_locations(
        self,
        location_type: LocationType,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        """
        Get point locations as GeoJSON features.
        """
        conn = self._get_conn()

        table_mapping = {
            LocationType.DUCHAS: "geospatial.duchas_locations",
            LocationType.CANUINT: "geospatial.canuint_locations",
            LocationType.SCHOOLS: "geospatial.celtic_medium_schools",
        }

        table = table_mapping.get(location_type)
        if not table:
            return []

        try:
            query = f"""
                SELECT
                    *,
                    ST_X(geometry) as lon,
                    ST_Y(geometry) as lat
                FROM {table}
                WHERE geometry IS NOT NULL
                LIMIT {limit}
            """
            results = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description]

            features = []
            for row in results:
                row_dict = dict(zip(columns, row))
                lat = row_dict.pop("lat", None)
                lon = row_dict.pop("lon", None)
                row_dict.pop("geometry", None)

                if lat is None or lon is None:
                    continue

                features.append({
                    "id": row_dict.get("volume_id") or row_dict.get("area_id") or row_dict.get("school_id"),
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat],
                    },
                    "properties": {k: v for k, v in row_dict.items() if v is not None},
                })

            return features

        except Exception:
            return []

    def find_nearby(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        location_type: LocationType | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Find locations within radius of a point.
        """
        conn = self._get_conn()

        # Determine which tables to search
        if location_type:
            tables = {location_type.value: {
                LocationType.DUCHAS: "geospatial.duchas_locations",
                LocationType.CANUINT: "geospatial.canuint_locations",
                LocationType.SCHOOLS: "geospatial.celtic_medium_schools",
            }.get(location_type)}
        else:
            tables = {
                "duchas": "geospatial.duchas_locations",
                "canuint": "geospatial.canuint_locations",
                "schools": "geospatial.celtic_medium_schools",
            }

        all_results = []

        for type_name, table in tables.items():
            if not table:
                continue

            try:
                # Use ST_DWithin for spatial query (radius in degrees, ~111km per degree)
                radius_deg = radius_km / 111.0

                query = f"""
                    SELECT
                        '{type_name}' as location_type,
                        *,
                        ST_X(geometry) as result_lon,
                        ST_Y(geometry) as result_lat,
                        ST_Distance(geometry, ST_Point({lon}, {lat})) * 111 as distance_km
                    FROM {table}
                    WHERE ST_DWithin(geometry, ST_Point({lon}, {lat}), {radius_deg})
                    ORDER BY distance_km
                    LIMIT {limit}
                """
                results = conn.execute(query).fetchall()
                columns = [desc[0] for desc in conn.description]

                for row in results:
                    row_dict = dict(zip(columns, row))
                    result_lat = row_dict.pop("result_lat", None)
                    result_lon = row_dict.pop("result_lon", None)
                    row_dict.pop("geometry", None)

                    if result_lat and result_lon:
                        all_results.append({
                            "location_type": type_name,
                            "distance_km": row_dict.pop("distance_km", 0),
                            "geometry": {
                                "type": "Point",
                                "coordinates": [result_lon, result_lat],
                            },
                            "properties": row_dict,
                        })

            except Exception:
                continue

        # Sort by distance and limit
        all_results.sort(key=lambda x: x.get("distance_km", float("inf")))
        return all_results[:limit]

    def find_within_boundary(
        self,
        boundary_type: BoundaryType,
        boundary_id: str,
        location_type: LocationType | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find locations within a specific boundary.
        """
        conn = self._get_conn()

        boundary_table = {
            BoundaryType.GAELTACHT: "geospatial.gaeltacht_boundaries",
            BoundaryType.DIALECT_REGIONS: "geospatial.dialect_regions",
        }.get(boundary_type)

        if not boundary_table:
            return []

        location_tables = {
            "duchas": "geospatial.duchas_locations",
            "canuint": "geospatial.canuint_locations",
            "schools": "geospatial.celtic_medium_schools",
        }

        if location_type:
            location_tables = {location_type.value: location_tables.get(location_type.value)}

        all_results = []

        for type_name, loc_table in location_tables.items():
            if not loc_table:
                continue

            try:
                query = f"""
                    SELECT
                        '{type_name}' as location_type,
                        l.*,
                        ST_X(l.geometry) as lon,
                        ST_Y(l.geometry) as lat
                    FROM {loc_table} l
                    JOIN {boundary_table} b ON ST_Contains(b.geometry, l.geometry)
                    WHERE b.gaeltacht_id = '{boundary_id}'
                       OR b.province = '{boundary_id}'
                    LIMIT 200
                """
                results = conn.execute(query).fetchall()
                columns = [desc[0] for desc in conn.description]

                for row in results:
                    row_dict = dict(zip(columns, row))
                    lat = row_dict.pop("lat", None)
                    lon = row_dict.pop("lon", None)
                    row_dict.pop("geometry", None)

                    if lat and lon:
                        all_results.append({
                            "location_type": type_name,
                            "geometry": {
                                "type": "Point",
                                "coordinates": [lon, lat],
                            },
                            "properties": row_dict,
                        })

            except Exception:
                continue

        return all_results

    def get_boundary_stats(
        self,
        boundary_type: BoundaryType,
    ) -> list[dict[str, Any]]:
        """
        Get aggregated statistics by boundary.
        """
        conn = self._get_conn()

        if boundary_type == BoundaryType.GAELTACHT:
            try:
                query = """
                    SELECT
                        gb.gaeltacht_id,
                        gb.gaeltacht_name,
                        gb.county,
                        gb.population,
                        gb.irish_speakers_daily,
                        COALESCE(d.folklore_count, 0) as folklore_items,
                        COALESCE(c.recording_count, 0) as pronunciation_recordings,
                        COALESCE(s.school_count, 0) as celtic_medium_schools
                    FROM geospatial.gaeltacht_boundaries gb
                    LEFT JOIN (
                        SELECT gaeltacht_id, COUNT(*) as folklore_count
                        FROM geospatial.duchas_by_gaeltacht
                        GROUP BY gaeltacht_id
                    ) d ON gb.gaeltacht_id = d.gaeltacht_id
                    LEFT JOIN (
                        SELECT province, SUM(recording_count) as recording_count
                        FROM geospatial.canuint_locations
                        GROUP BY province
                    ) c ON gb.county = c.province
                    LEFT JOIN (
                        SELECT COUNT(*) as school_count
                        FROM geospatial.celtic_medium_schools
                        WHERE nation = 'ireland'
                    ) s ON 1=1
                """
                results = conn.execute(query).fetchall()
                columns = [desc[0] for desc in conn.description]

                return [
                    {
                        "boundary_id": row[0],
                        "boundary_name": row[1],
                        "stats": dict(zip(columns[2:], row[2:])),
                    }
                    for row in results
                ]

            except Exception:
                return []

        return []


# Global service instance
_service: GeospatialService | None = None


def get_service() -> GeospatialService:
    """Get or create geospatial service instance."""
    global _service
    if _service is None:
        _service = GeospatialService()
    return _service


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/boundaries/{boundary_type}", response_model=GeoJSONFeatureCollection)
async def get_boundaries(
    boundary_type: BoundaryType,
    simplify: bool = Query(default=True, description="Simplify geometries for smaller response"),
) -> GeoJSONFeatureCollection:
    """
    Get boundary polygons as GeoJSON.

    Available types:
    - gaeltacht: Official Gaeltacht area boundaries
    - dialect_regions: Irish dialect regions (Munster/Connacht/Ulster)
    - welsh_speaking: Welsh-speaking areas from Census
    - gaidhealtachd: Scottish Gaelic areas
    - irish_small_areas: CSO Small Areas
    """
    service = get_service()
    features = service.get_boundaries(boundary_type, simplify=simplify)

    return GeoJSONFeatureCollection(
        features=[GeoJSONFeature(**f) for f in features],
        metadata={"boundary_type": boundary_type.value, "count": len(features)},
    )


@router.get("/locations/{location_type}", response_model=GeoJSONFeatureCollection)
async def get_locations(
    location_type: LocationType,
    limit: int = Query(default=500, ge=1, le=5000),
) -> GeoJSONFeatureCollection:
    """
    Get point locations as GeoJSON.

    Available types:
    - duchas: Folklore collection locations
    - canuint: Pronunciation recording locations
    - schools: Celtic-medium school locations
    """
    service = get_service()
    features = service.get_locations(location_type, limit=limit)

    return GeoJSONFeatureCollection(
        features=[GeoJSONFeature(**f) for f in features],
        metadata={"location_type": location_type.value, "count": len(features)},
    )


@router.post("/nearby", response_model=GeoJSONFeatureCollection)
async def find_nearby(request: NearbyRequest) -> GeoJSONFeatureCollection:
    """
    Find locations within a radius of a point.
    """
    service = get_service()

    results = service.find_nearby(
        lat=request.lat,
        lon=request.lon,
        radius_km=request.radius_km,
        location_type=request.location_type,
        limit=request.limit,
    )

    features = [
        GeoJSONFeature(
            id=str(i),
            geometry=r["geometry"],
            properties={
                "location_type": r["location_type"],
                "distance_km": r["distance_km"],
                **r["properties"],
            },
        )
        for i, r in enumerate(results)
    ]

    return GeoJSONFeatureCollection(
        features=features,
        metadata={
            "center": {"lat": request.lat, "lon": request.lon},
            "radius_km": request.radius_km,
            "count": len(features),
        },
    )


@router.get("/within/{boundary_type}/{boundary_id}", response_model=GeoJSONFeatureCollection)
async def find_within_boundary(
    boundary_type: BoundaryType,
    boundary_id: str,
    location_type: LocationType | None = Query(default=None),
) -> GeoJSONFeatureCollection:
    """
    Find locations within a specific boundary.
    """
    service = get_service()

    results = service.find_within_boundary(
        boundary_type=boundary_type,
        boundary_id=boundary_id,
        location_type=location_type,
    )

    features = [
        GeoJSONFeature(
            id=str(i),
            geometry=r["geometry"],
            properties={
                "location_type": r["location_type"],
                **r["properties"],
            },
        )
        for i, r in enumerate(results)
    ]

    return GeoJSONFeatureCollection(
        features=features,
        metadata={
            "boundary_type": boundary_type.value,
            "boundary_id": boundary_id,
            "count": len(features),
        },
    )


@router.get("/stats/{boundary_type}", response_model=list[BoundaryStats])
async def get_boundary_stats(boundary_type: BoundaryType) -> list[BoundaryStats]:
    """
    Get aggregated statistics by boundary.

    Returns counts of folklore items, recordings, schools, etc. per boundary.
    """
    service = get_service()
    stats = service.get_boundary_stats(boundary_type)

    return [BoundaryStats(**s) for s in stats]
