"""Newfoundland and Labrador (nl) national pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.can.nl import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
