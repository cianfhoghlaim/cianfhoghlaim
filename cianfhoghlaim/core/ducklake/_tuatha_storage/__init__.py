"""Tuath Storage Layer — re-export shim to canonical oideachais storage.

The original `sruth/tuatha/storage/serial_executor.py` shim imported from
the now-deleted `sruth.shared.storage` (deleted in commit `8484a6353`).
This `__init__.py` now re-exports the 3 names (`SerialDatabaseExecutor`,
`get_executor`, `run_serial`) directly from the canonical oideachais home
at `sruth.oideachais.core.storage.serial_executor`.
"""

from sruth.oideachais.core.storage.serial_executor import (
    SerialDatabaseExecutor,
    get_executor,
    run_serial,
)

__all__ = [
    "SerialDatabaseExecutor",
    "get_executor",
    "run_serial",
]
