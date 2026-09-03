"""Re-export the Canada statistics DLT source module."""
from dlt_sources.commonwealth.can.statistics import statcan  # noqa: F401

__all__ = ["statcan"]
