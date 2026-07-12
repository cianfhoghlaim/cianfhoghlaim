"""Type definitions for browser agent stack.

DEPRECATED: Import from browser.types instead.

This module re-exports from browser.types for backwards compatibility.
"""

import warnings

warnings.warn(
    "browser.core.types is deprecated. Import from browser.types instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from root types module
from ..browser_types import (
    BackendType,
    BrowserOperation,
    ExtractionFormat,
    CircuitState,
    BackendHealth,
    SessionState,
    NavigationResult,
    ExtractionResult,
    InteractionResult,
    ScreenshotResult,
    ResearchResult,
    VisualGroundingResult,
    VisionAnalysisResult,
    BACKEND_PRIORITY,
    BACKEND_COST,
)

__all__ = [
    "BackendType",
    "BrowserOperation",
    "ExtractionFormat",
    "CircuitState",
    "BackendHealth",
    "SessionState",
    "NavigationResult",
    "ExtractionResult",
    "InteractionResult",
    "ScreenshotResult",
    "ResearchResult",
    "VisualGroundingResult",
    "VisionAnalysisResult",
    "BACKEND_PRIORITY",
    "BACKEND_COST",
]
