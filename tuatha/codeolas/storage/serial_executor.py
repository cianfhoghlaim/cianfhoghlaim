"""
Serial Database Executor - Re-export from oideachais core storage.

DEPRECATED: Import directly from oideachais.core.storage.serial_executor instead.

This file is kept for backwards compatibility and will be removed
in a future version.
"""

import warnings

warnings.warn(
    "Importing from codeolas.storage.serial_executor is deprecated. "
    "Use oideachais.core.storage.serial_executor instead.",
    DeprecationWarning,
    stacklevel=2,
)

from oideachais.core.storage.serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
