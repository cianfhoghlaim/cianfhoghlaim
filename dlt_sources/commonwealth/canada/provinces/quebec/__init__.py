"""Quebec (qc) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.can.qc import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
