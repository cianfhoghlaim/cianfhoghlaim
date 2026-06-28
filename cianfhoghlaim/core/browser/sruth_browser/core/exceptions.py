"""Custom exceptions for browser agent stack.

DEPRECATED: This module re-exports from sruth_browser.exceptions.
Update imports: from sruth_browser import BackendError, FallbackExhaustedError, etc.
"""

import warnings

warnings.warn(
    "sruth_browser.core.exceptions is deprecated. "
    "Import from sruth_browser instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from parent package
from sruth_browser.exceptions import (
    BackendError,
    BackendTimeoutError,
    BrowserAgentError,
    CircuitOpenError,
    ExtractionError,
    FallbackExhaustedError,
    NavigationError,
    SchemaValidationError,
    SessionError,
)

__all__ = [
    "BrowserAgentError",
    "BackendError",
    "BackendTimeoutError",
    "CircuitOpenError",
    "NavigationError",
    "ExtractionError",
    "SessionError",
    "SchemaValidationError",
    "FallbackExhaustedError",
]
