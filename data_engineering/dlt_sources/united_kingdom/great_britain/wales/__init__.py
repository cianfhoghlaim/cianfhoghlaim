"""
DLT sources for Wales education data.

Sources:
- StatsWales OData API
- Estyn inspection reports
"""

from .estyn import estyn_source
from .statswales import statswales_source

__all__ = [
    "statswales_source",
    "estyn_source",
]
