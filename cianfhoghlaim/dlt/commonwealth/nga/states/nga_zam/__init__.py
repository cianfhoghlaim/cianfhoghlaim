"""Zamfara (nga_zam) state pipeline — re-exports the per-domain sub-trees."""
from cianfhoghlaim.dlt.commonwealth.nga.states.nga_zam import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
