"""
Download and process Scottish Data Zones.

Source: Scottish Spatial Data Infrastructure
Total areas: 6,976
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import httpx

SPATIAL_DATA_SCOT = "https://maps.gov.scot/server/rest/services/ScotGov/StatisticalUnits/MapServer"


def download_data_zones(
    output_path: str | Path | None = None,
    format: str = "geoparquet",
    include_simd: bool = True,
    max_records: int | None = None,
) -> gpd.GeoDataFrame:
    """
    Download Scottish Data Zones from SpatialData.gov.scot.

    Args:
        output_path: Optional path to save output
        format: Output format (geoparquet, geojson, gpkg)
        include_simd: Whether to include SIMD rankings
        max_records: Maximum records to download

    Returns:
        GeoDataFrame with Data Zone boundaries
    """
    # Data Zones 2011 layer
    layer = 1  # Data Zones layer index

    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }

    if max_records:
        params["resultRecordCount"] = max_records

    url = f"{SPATIAL_DATA_SCOT}/{layer}/query"

    all_features = []
    offset = 0
    batch_size = 1000

    with httpx.Client(timeout=120.0) as client:
        while True:
            params["resultOffset"] = offset
            params["resultRecordCount"] = batch_size

            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            features = data.get("features", [])
            if not features:
                break

            all_features.extend(features)

            if max_records and len(all_features) >= max_records:
                all_features = all_features[:max_records]
                break

            if len(features) < batch_size:
                break

            offset += batch_size

    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(all_features, crs="EPSG:4326")

    # Standardize column names
    column_mapping = {
        "DataZone": "area_code",
        "Name": "area_name",
        "TotPop2011": "population",
        "ResPop2011": "residential_population",
        "HHCnt2011": "household_count",
    }

    for old_col, new_col in column_mapping.items():
        if old_col in gdf.columns:
            gdf = gdf.rename(columns={old_col: new_col})

    gdf["nation"] = "scotland"
    gdf["area_type"] = "data_zone"

    # Add SIMD if available and requested
    if include_simd and "SIMD2020v2_Rank" in gdf.columns:
        gdf = gdf.rename(columns={
            "SIMD2020v2_Rank": "simd_rank",
            "SIMD2020v2_Decile": "simd_decile",
            "SIMD2020v2_Quintile": "simd_quintile",
        })

    # Save if output path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "geoparquet":
            gdf.to_parquet(output_path)
        elif format == "geojson":
            gdf.to_file(output_path, driver="GeoJSON")
        elif format == "gpkg":
            gdf.to_file(output_path, driver="GPKG")

    return gdf


def get_data_zones_metadata() -> dict[str, Any]:
    """Get metadata about Data Zones."""
    return {
        "source": "Scottish Spatial Data Infrastructure",
        "url": SPATIAL_DATA_SCOT,
        "area_count": 6976,
        "nation": "scotland",
        "year": 2011,
        "deprivation_index": "SIMD 2020v2",
        "fields": {
            "area_code": "DataZone - Data Zone code",
            "area_name": "Name - Data Zone name",
            "population": "TotPop2011 - Total population 2011",
            "simd_rank": "SIMD2020v2_Rank - SIMD rank (1=most deprived)",
            "simd_decile": "SIMD2020v2_Decile - SIMD decile (1=most deprived)",
        },
    }
