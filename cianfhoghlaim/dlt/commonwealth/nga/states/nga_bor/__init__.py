"""Borno (nga_bor) state pipeline — re-exports the per-domain sub-trees."""
from cianfhoghlaim.dlt.commonwealth.nga.states.nga_bor import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
