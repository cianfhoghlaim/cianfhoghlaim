"""Portugal (Portugal) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.european_nations.prt import (
    education,
    government,
    law,
    medicine,
    statistics,
)

__all__ = ["education", "government", "law", "medicine", "statistics"]
