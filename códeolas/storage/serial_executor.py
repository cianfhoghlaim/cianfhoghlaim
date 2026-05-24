"""
Serial Database Executor - Re-export from shared.

DEPRECATED: Import directly from sruth.shared.storage instead.

This file is kept for backwards compatibility and will be removed
in a future version.
"""

import warnings

warnings.warn(
    "Importing from sruth.códeolas.storage.serial_executor is deprecated. "
    "Use sruth.shared.storage instead.",
    DeprecationWarning,
    stacklevel=2,
)

from sruth.shared.storage import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
