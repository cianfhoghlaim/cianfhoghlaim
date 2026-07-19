"""India (ind) Commonwealth pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.ind import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
