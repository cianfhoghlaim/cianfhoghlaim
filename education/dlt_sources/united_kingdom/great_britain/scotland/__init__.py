"""
DLT sources for Scotland education data.

Sources:
- gov.scot education statistics
- Insight benchmarking data
- SIMD (Scottish Index of Multiple Deprivation)
"""

from .gov_scot_statistics import gov_scot_source
from .insight_benchmarking import insight_source
from .simd import simd_source

__all__ = [
    "gov_scot_source",
    "insight_source",
    "simd_source",
]
