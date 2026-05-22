"""
DLT sources for England education data.

Sources:
- DfE Explore Education Statistics API
- Ofsted inspection reports
- GIAS (Get Information About Schools)
"""

from .dfe_explore_statistics import dfe_statistics_source
from .ofsted import ofsted_source
from .school_info import gias_source

__all__ = [
    "dfe_statistics_source",
    "ofsted_source",
    "gias_source",
]
