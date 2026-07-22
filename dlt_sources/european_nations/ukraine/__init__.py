"""Ukraine (ukr) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.european_nations.ukr import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
