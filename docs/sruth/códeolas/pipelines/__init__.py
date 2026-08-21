"""Dagster pipelines for códeolas.

Provides:
- Dagster assets for code indexing
- Schedules for periodic updates
"""

from .code_assets import (
    architecture_docs,
    code_chunks,
    code_graph,
    codeolas_assets,
)
from .schedules import (
    codeolas_schedules,
    daily_architecture_docs_schedule,
    hourly_code_indexing_schedule,
    weekly_full_rebuild_schedule,
)

__all__ = [
    # Assets
    "code_chunks",
    "code_graph",
    "architecture_docs",
    "codeolas_assets",
    # Schedules
    "hourly_code_indexing_schedule",
    "daily_architecture_docs_schedule",
    "weekly_full_rebuild_schedule",
    "codeolas_schedules",
]
