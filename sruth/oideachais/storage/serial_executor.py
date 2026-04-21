"""
Serial Database Executor for DuckDB/LanceDB Safety.

DEPRECATED: This module is deprecated. Import from oideachais.core.storage instead.

This file re-exports from core.storage for backward compatibility.
"""

import warnings

warnings.warn(
    "sruth.oideachais.storage.serial_executor is deprecated. "
    "Import from oideachais.core.storage instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from core.storage (authoritative location)
from ..core.storage import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
