"""New Brunswick (nb) national pipeline — re-exports the per-domain sub-trees."""
from cianfhoghlaim.dlt.commonwealth.can.nb import education, government, law, medicine, statistics

__all__ = ["education", "government", "law", "medicine", "statistics"]
