"""South Africa (zaf) Commonwealth pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.zaf import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
