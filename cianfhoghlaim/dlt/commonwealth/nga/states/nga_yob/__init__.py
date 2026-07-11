"""Yobe (nga_yob) state pipeline — re-exports the per-domain sub-trees."""
from cianfhoghlaim.dlt.commonwealth.nga.states.nga_yob import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
