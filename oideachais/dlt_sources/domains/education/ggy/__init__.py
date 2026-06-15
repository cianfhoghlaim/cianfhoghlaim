"""Re-export shim: domains.education.ggy ↔ crown_dependencies.channel_islands (Guernsey).

The crown_dependencies/channel_islands module covers both Jersey and Guernsey
endpoints; the per-island package is the new canonical split.
"""
from __future__ import annotations

from dlt_sources.crown_dependencies import channel_islands

__all__ = ["channel_islands"]
