"""
DLT sources for Tuath Celtic MMO.

Sources:
- mythology: Celtic gods, heroes, and legends
- geospatial: Gaeltacht boundaries, Celtic communities
"""

from .geospatial.gaelic_communities import gaelic_communities_source
from .geospatial.gaeltacht_boundaries import gaeltacht_boundaries_source
from .geospatial.welsh_language_areas import welsh_language_areas_source
from .mythology import celtic_mythology_source

__all__ = [
    "celtic_mythology_source",
    "gaelic_communities_source",
    "gaeltacht_boundaries_source",
    "welsh_language_areas_source",
]
