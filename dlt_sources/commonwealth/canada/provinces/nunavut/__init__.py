"""Nunavut (nu) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.can.nu import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
