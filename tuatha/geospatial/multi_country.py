"""
Multi-country boundary configuration for Celtic education data.

Supports unified handling of statistical boundaries across:
- Ireland: CSO Small Areas (18,641 areas), Gaeltacht boundaries
- England/Wales: LSOA (34,753 areas)
- Scotland: Data Zones (6,976 areas)
- Northern Ireland: SOA (890 areas)
- Crown Dependencies: Isle of Man, Jersey, Guernsey

Also includes Celtic language area boundaries:
- Gaeltacht (Ireland)
- Gàidhealtachd (Scotland)
- Welsh-speaking areas (Wales)
"""

from dataclasses import dataclass
from typing import Any

import geopandas as gpd
import pandas as pd


@dataclass
class NationBoundaryConfig:
    """Configuration for a nation's statistical boundaries."""

    nation_code: str
    nation_name: str
    area_type: str
    area_code_column: str
    area_name_column: str
    area_count: int
    crs: str
    source_url: str | None = None
    language_area_type: str | None = None
    language_code: str | None = None


# Configuration for each nation's statistical areas
NATION_CONFIGS = {
    "ireland": NationBoundaryConfig(
        nation_code="ie",
        nation_name="Ireland",
        area_type="small_area",
        area_code_column="sa_2016",
        area_name_column="ed_name",
        area_count=18641,
        crs="EPSG:2157",  # Irish Transverse Mercator
        source_url="https://data.cso.ie/",
        language_area_type="gaeltacht",
        language_code="ga",
    ),
    "england": NationBoundaryConfig(
        nation_code="en",
        nation_name="England",
        area_type="lsoa",
        area_code_column="lsoa21cd",
        area_name_column="lsoa21nm",
        area_count=33755,
        crs="EPSG:27700",  # British National Grid
        source_url="https://geoportal.statistics.gov.uk/",
    ),
    "wales": NationBoundaryConfig(
        nation_code="cy",
        nation_name="Wales",
        area_type="lsoa",
        area_code_column="lsoa21cd",
        area_name_column="lsoa21nm",
        area_count=1909,
        crs="EPSG:27700",
        source_url="https://geoportal.statistics.gov.uk/",
        language_area_type="welsh_speaking",
        language_code="cy",
    ),
    "scotland": NationBoundaryConfig(
        nation_code="sc",
        nation_name="Scotland",
        area_type="data_zone",
        area_code_column="datazone",
        area_name_column="name",
        area_count=6976,
        crs="EPSG:27700",
        source_url="https://www.gov.scot/",
        language_area_type="gaidhealtachd",
        language_code="gd",
    ),
    "northern_ireland": NationBoundaryConfig(
        nation_code="ni",
        nation_name="Northern Ireland",
        area_type="soa",
        area_code_column="soa2021",
        area_name_column="soa2021nm",
        area_count=890,
        crs="EPSG:29903",  # Irish Grid
        source_url="https://www.nisra.gov.uk/",
        language_area_type="irish_medium",
        language_code="ga",
    ),
    "isle_of_man": NationBoundaryConfig(
        nation_code="im",
        nation_name="Isle of Man",
        area_type="parish",
        area_code_column="parish_code",
        area_name_column="parish_name",
        area_count=17,
        crs="EPSG:27700",
        language_area_type="manx_speaking",
        language_code="gv",
    ),
    "jersey": NationBoundaryConfig(
        nation_code="je",
        nation_name="Jersey",
        area_type="parish",
        area_code_column="parish_code",
        area_name_column="parish_name",
        area_count=12,
        crs="EPSG:32630",  # UTM zone 30N
    ),
    "guernsey": NationBoundaryConfig(
        nation_code="gg",
        nation_name="Guernsey",
        area_type="parish",
        area_code_column="parish_code",
        area_name_column="parish_name",
        area_count=10,
        crs="EPSG:32630",
    ),
}


# Area code prefix patterns for each nation
AREA_CODE_PATTERNS = {
    "ireland": ["SA_"],  # Small Area codes start with SA_
    "england": ["E0"],  # English LSOA codes start with E0
    "wales": ["W0"],  # Welsh LSOA codes start with W0
    "scotland": ["S0"],  # Scottish Data Zone codes start with S0
    "northern_ireland": ["95"],  # NI SOA codes start with 95
    "isle_of_man": ["IM"],
    "jersey": ["JE"],
    "guernsey": ["GG"],
}


def get_nation_boundary_config(nation: str) -> NationBoundaryConfig:
    """
    Get boundary configuration for a nation.

    Args:
        nation: Nation code (ireland, england, scotland, wales, northern_ireland, etc.)

    Returns:
        NationBoundaryConfig for the nation

    Raises:
        ValueError: If nation is not supported
    """
    if nation.lower() not in NATION_CONFIGS:
        supported = ", ".join(NATION_CONFIGS.keys())
        raise ValueError(f"Unknown nation: {nation}. Supported: {supported}")

    return NATION_CONFIGS[nation.lower()]


def get_nation_from_area_code(area_code: str) -> str | None:
    """
    Determine nation from area code prefix.

    Args:
        area_code: Statistical area code

    Returns:
        Nation code or None if not recognized
    """
    for nation, prefixes in AREA_CODE_PATTERNS.items():
        for prefix in prefixes:
            if area_code.startswith(prefix):
                return nation
    return None


def normalize_area_codes(
    gdf: gpd.GeoDataFrame,
    nation: str,
    area_code_column: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Normalize area codes to unified format.

    Creates standardized 'area_code' column with format:
    {nation_code}_{original_code}

    Args:
        gdf: GeoDataFrame with area boundaries
        nation: Nation code
        area_code_column: Source column for area codes (uses config default if None)

    Returns:
        GeoDataFrame with normalized area_code column
    """
    config = get_nation_boundary_config(nation)

    if area_code_column is None:
        area_code_column = config.area_code_column

    if area_code_column not in gdf.columns:
        raise ValueError(f"Column '{area_code_column}' not found in GeoDataFrame")

    # Create normalized code
    gdf = gdf.copy()
    gdf["area_code"] = config.nation_code + "_" + gdf[area_code_column].astype(str)
    gdf["nation"] = nation
    gdf["area_type"] = config.area_type

    return gdf


def load_unified_boundaries(
    boundary_sources: dict[str, gpd.GeoDataFrame | str],
    target_crs: str = "EPSG:4326",
) -> gpd.GeoDataFrame:
    """
    Load and unify boundaries from multiple nations.

    Args:
        boundary_sources: Dict mapping nation -> GeoDataFrame or file path
        target_crs: Target CRS for unified data (default WGS84)

    Returns:
        Unified GeoDataFrame with all boundaries
    """
    unified_gdfs = []

    for nation, source in boundary_sources.items():
        config = get_nation_boundary_config(nation)

        # Load if path
        gdf = gpd.read_parquet(source) if isinstance(source, str) else source.copy()

        # Normalize area codes
        gdf = normalize_area_codes(gdf, nation)

        # Ensure area_name column exists
        if config.area_name_column in gdf.columns:
            gdf["area_name"] = gdf[config.area_name_column]
        else:
            gdf["area_name"] = gdf["area_code"]

        # Transform CRS
        if gdf.crs and str(gdf.crs) != target_crs:
            gdf = gdf.to_crs(target_crs)

        # Select standard columns
        standard_cols = ["area_code", "area_name", "nation", "area_type", "geometry"]
        available_cols = [c for c in standard_cols if c in gdf.columns]
        gdf = gdf[available_cols]

        unified_gdfs.append(gdf)

    return gpd.GeoDataFrame(pd.concat(unified_gdfs, ignore_index=True), crs=target_crs)


def get_celtic_language_areas() -> dict[str, dict[str, Any]]:
    """
    Get configuration for Celtic language speaking areas.

    Returns:
        Dict mapping language code to configuration
    """
    return {
        "ga": {
            "name": "Irish",
            "native_name": "Gaeilge",
            "area_type": "gaeltacht",
            "nations": ["ireland", "northern_ireland"],
            "source": "Department of Tourism, Culture, Arts, Gaeltacht, Sport and Media",
        },
        "gd": {
            "name": "Scottish Gaelic",
            "native_name": "Gàidhlig",
            "area_type": "gaidhealtachd",
            "nations": ["scotland"],
            "source": "Bòrd na Gàidhlig",
        },
        "cy": {
            "name": "Welsh",
            "native_name": "Cymraeg",
            "area_type": "welsh_speaking",
            "nations": ["wales"],
            "source": "Welsh Government Census",
        },
        "gv": {
            "name": "Manx",
            "native_name": "Gaelg",
            "area_type": "manx_speaking",
            "nations": ["isle_of_man"],
            "source": "Culture Vannin",
        },
        "kw": {
            "name": "Cornish",
            "native_name": "Kernewek",
            "area_type": "cornish_speaking",
            "nations": ["england"],  # Cornwall
            "source": "Cornish Language Partnership",
        },
        "br": {
            "name": "Breton",
            "native_name": "Brezhoneg",
            "area_type": "breton_speaking",
            "nations": [],  # Not in UK/Ireland
            "source": "Office public de la langue bretonne",
        },
    }


def get_summary_by_nation(gdf: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Get summary statistics by nation.

    Args:
        gdf: Unified GeoDataFrame with 'nation' column

    Returns:
        DataFrame with counts and extent per nation
    """
    summary = []

    for nation in gdf["nation"].unique():
        nation_gdf = gdf[gdf["nation"] == nation]
        bounds = nation_gdf.total_bounds

        summary.append({
            "nation": nation,
            "area_count": len(nation_gdf),
            "area_type": nation_gdf["area_type"].iloc[0] if "area_type" in nation_gdf.columns else None,
            "minx": bounds[0],
            "miny": bounds[1],
            "maxx": bounds[2],
            "maxy": bounds[3],
        })

    return pd.DataFrame(summary)
