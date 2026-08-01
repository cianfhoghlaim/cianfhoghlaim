"""
DLT sources for UK education data.

Organized by nation:
- england: DfE statistics, Ofsted, school info
- scotland: Scottish Government statistics, SIMD, Insight benchmarking
- wales: StatsWales, Estyn inspections
- northern_ireland: Education NI, NISRA, ETI inspections
"""

from . import england
from . import scotland
from . import wales
from . import northern_ireland

__all__ = [
    "england",
    "scotland",
    "wales",
    "northern_ireland",
]
