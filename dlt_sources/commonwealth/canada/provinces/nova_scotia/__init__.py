"""Nova Scotia (ns) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.can.ns import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
