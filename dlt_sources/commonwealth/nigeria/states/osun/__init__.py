"""Osun (Osun State) state pipeline — re-exports the per-domain sub-trees."""
from dlt_sources.commonwealth.nga.states.nga_osn import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
