"""Kogi (nga_kog) state pipeline — re-exports the per-domain sub-trees."""
from cianfhoghlaim.dlt.commonwealth.nga.states.nga_kog import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
