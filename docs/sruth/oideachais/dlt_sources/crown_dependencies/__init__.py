"""
DLT sources for Crown Dependencies education data.

Sources:
- Isle of Man (DESC)
- Jersey
- Guernsey
"""

from .isle_of_man import isle_of_man_source
from .channel_islands import jersey_source, guernsey_source

__all__ = [
    "isle_of_man_source",
    "jersey_source",
    "guernsey_source",
]
