"""Re-export the Canada medicine DLT source module."""
from dlt_sources.commonwealth.can.medicine import health_canada  # noqa: F401

__all__ = ["health_canada"]
