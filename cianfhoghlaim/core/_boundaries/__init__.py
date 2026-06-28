"""
Boundary download and processing for each nation.

Handles:
- LSOA 2021 (England/Wales) - 33,755 areas
- Data Zones 2011 (Scotland) - 6,976 areas
- Small Areas 2011 (Northern Ireland) - 4,537 areas
- Small Areas 2022 (Ireland) - 18,641 areas
"""

from .data_zones_scotland import download_data_zones, get_data_zones_metadata
from .lsoa_england_wales import download_lsoa_boundaries, get_lsoa_metadata
from .small_areas_ireland import download_small_areas, get_small_areas_metadata
from .soa_northern_ireland import download_soa_boundaries, get_soa_metadata

__all__ = [
    "download_data_zones",
    "download_lsoa_boundaries",
    "download_small_areas",
    "download_soa_boundaries",
    "get_data_zones_metadata",
    "get_lsoa_metadata",
    "get_small_areas_metadata",
    "get_soa_metadata",
]
