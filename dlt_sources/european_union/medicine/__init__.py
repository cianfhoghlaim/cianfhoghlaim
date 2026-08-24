"""dlt_sources/european_union/medicine — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

from . import ecdc_surveillance  # noqa: F401
from . import ema_medicines_register  # noqa: F401
from . import european_health_data_space  # noqa: F401

__all__ = ['ecdc_surveillance', 'ema_medicines_register', 'european_health_data_space']
