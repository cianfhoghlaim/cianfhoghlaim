"""
Geospatial DLT sources for Tuath Celtic MMO.

Sources for Celtic language region boundaries and communities.
"""

from .gaeltacht_boundaries import gaeltacht_boundaries_source
from .gaelic_communities import gaelic_communities_source
from .welsh_language_areas import welsh_language_areas_source

__all__ = [
    "gaeltacht_boundaries_source",
    "gaelic_communities_source",
    "welsh_language_areas_source",
]
