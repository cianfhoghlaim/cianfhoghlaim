"""Northwest Territories (nt) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.can.nt import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
