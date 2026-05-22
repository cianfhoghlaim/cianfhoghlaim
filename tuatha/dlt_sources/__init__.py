"""
DLT sources for Tuath Celtic MMO.

Sources:
- mythology: Celtic gods, heroes, and legends
- geospatial: Gaeltacht boundaries, Celtic communities
"""

from .mythology import celtic_mythology_source
from .geospatial.gaeltacht_boundaries import gaeltacht_boundaries_source
from .geospatial.gaelic_communities import gaelic_communities_source
from .geospatial.welsh_language_areas import welsh_language_areas_source

__all__ = [
    "celtic_mythology_source",
    "gaeltacht_boundaries_source",
    "gaelic_communities_source",
    "welsh_language_areas_source",
]
