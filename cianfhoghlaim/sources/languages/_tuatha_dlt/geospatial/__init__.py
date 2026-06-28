"""
Geospatial DLT sources for Tuath Celtic MMO.

Sources for Celtic language region boundaries and communities.
"""

from .gaelic_communities import gaelic_communities_source
from .gaeltacht_boundaries import gaeltacht_boundaries_source
from .welsh_language_areas import welsh_language_areas_source

__all__ = [
    "gaelic_communities_source",
    "gaeltacht_boundaries_source",
    "welsh_language_areas_source",
]
