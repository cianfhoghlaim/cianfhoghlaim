"""
Download and process Northern Ireland Small Areas.

Source: NISRA Geography
Total areas: 4,537
"""

from pathlib import Path
from typing import Any

import geopandas as gpd

NISRA_GEOGRAPHY = "https://ons-inspire.esriuk.com/arcgis/rest/services/Census_Boundaries"


def download_soa_boundaries(
    output_path: str | Path | None = None,
    format: str = "geoparquet",
    max_records: int | None = None,
) -> gpd.GeoDataFrame:
    """
    Download Northern Ireland Small Areas.

    Note: This is a placeholder implementation. The actual
    NISRA geography service may require different endpoints.

    Args:
        output_path: Optional path to save output
        format: Output format (geoparquet, geojson, gpkg)
        max_records: Maximum records to download

    Returns:
        GeoDataFrame with Small Area boundaries
    """
    # NI Small Areas 2011
    # This is a simplified implementation - actual service may differ

    # Create placeholder with expected structure
    gdf = gpd.GeoDataFrame({
        "area_code": [],
        "area_name": [],
        "soa_code": [],
        "lgd_code": [],
        "lgd_name": [],
        "nation": [],
        "area_type": [],
    }, geometry=[], crs="EPSG:4326")

    gdf["nation"] = "northern_ireland"
    gdf["area_type"] = "small_area"

    # TODO: Implement actual NISRA API integration
    # The NISRA Open Data portal may provide different access methods

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == "geoparquet":
            gdf.to_parquet(output_path)
        elif format == "geojson":
            gdf.to_file(output_path, driver="GeoJSON")

    return gdf


def get_soa_metadata() -> dict[str, Any]:
    """Get metadata about NI Small Areas."""
    return {
        "source": "NISRA Geography",
        "url": "https://www.nisra.gov.uk/support/geography",
        "area_count": 4537,
        "nation": "northern_ireland",
        "year": 2011,
        "deprivation_index": "NI Multiple Deprivation Measure 2017",
        "note": "Implementation requires NISRA API access",
        "fields": {
            "area_code": "SA2011 - Small Area code",
            "area_name": "SA2011_NAME - Small Area name",
            "soa_code": "SOA2011 - Super Output Area code",
            "lgd_code": "LGD2014 - Local Government District code",
        },
    }
