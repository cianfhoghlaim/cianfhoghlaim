"""
DLT sources for Wales education data.

Sources:
- StatsWales OData API
- Estyn inspection reports
"""

from .statswales import statswales_source
from .estyn import estyn_source

__all__ = [
    "statswales_source",
    "estyn_source",
]
