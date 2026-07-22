"""California (California) Americas pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.americas.us.us_ca import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
