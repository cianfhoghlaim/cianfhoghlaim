"""Germany (deu) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.european_nations.deu import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
