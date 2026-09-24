"""
DLT sources for Crown Dependencies education data.

Sources:
- Isle of Man (DESC)
- Jersey
- Guernsey
"""

from .channel_islands import guernsey_source, jersey_source
from .isle_of_man import isle_of_man_source

__all__ = [
    "isle_of_man_source",
    "jersey_source",
    "guernsey_source",
]
