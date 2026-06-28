"""
Download and process LSOA 2021 boundaries for England and Wales.

Source: ONS Open Geography Portal
Total areas: 33,755
"""

from pathlib import Path
from typing import Any

import geopandas as gpd
import httpx

ONS_ARCGIS = "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services"
LSOA_SERVICE = "Lower_layer_Super_Output_Areas_2021_EW_BGC_V3"


def download_lsoa_boundaries(
    output_path: str | Path | None = None,
    format: str = "geoparquet",
    max_records: int | None = None,
) -> gpd.GeoDataFrame:
    """
    Download LSOA 2021 boundaries from ONS.

    Args:
        output_path: Optional path to save output
        format: Output format (geoparquet, geojson, gpkg)
        max_records: Maximum records to download

    Returns:
        GeoDataFrame with LSOA boundaries
    """
    # Query parameters
    params = {
        "where": "1=1",
        "outFields": "LSOA21CD,LSOA21NM,LSOA21NMW,LAD22CD,LAD22NM",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }

    if max_records:
        params["resultRecordCount"] = max_records

    # Fetch data
    url = f"{ONS_ARCGIS}/{LSOA_SERVICE}/FeatureServer/0/query"

    all_features = []
    offset = 0
    batch_size = 2000

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
    gdf = gdf.rename(columns={
        "LSOA21CD": "area_code",
        "LSOA21NM": "area_name",
        "LSOA21NMW": "area_name_welsh",
        "LAD22CD": "la_code",
        "LAD22NM": "la_name",
    })

    gdf["nation"] = gdf["area_code"].apply(
        lambda x: "england" if x.startswith("E") else "wales"
    )
    gdf["area_type"] = "lsoa"

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


def get_lsoa_metadata() -> dict[str, Any]:
    """Get metadata about LSOA boundaries."""
    return {
        "source": "ONS Open Geography Portal",
        "service": LSOA_SERVICE,
        "url": f"{ONS_ARCGIS}/{LSOA_SERVICE}",
        "area_count": 33755,
        "nations": ["england", "wales"],
        "year": 2021,
        "fields": {
            "area_code": "LSOA21CD - LSOA code",
            "area_name": "LSOA21NM - LSOA name (English)",
            "area_name_welsh": "LSOA21NMW - LSOA name (Welsh)",
            "la_code": "LAD22CD - Local Authority code",
            "la_name": "LAD22NM - Local Authority name",
        },
    }
