"""Browser client library for other sruth projects.

This module provides a simple HTTP client interface to the browser agent service.
Other flows (crypteolas, oideachais, aleyum, tuath) should import from here.

Usage:
    from sruth_browser.client import BrowserClient

    client = BrowserClient()
    result = await client.scrape("https://example.com")
"""

from .http_client import BrowserClient
from .types import (
    BackendType,
    BrowserOperation,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ResearchResult,
    ScreenshotResult,
    SessionState,
    VisionAnalysisResult,
    VisualGroundingResult,
)

__all__ = [
    "BrowserClient",
    "BackendType",
    "BrowserOperation",
    "ExtractionFormat",
    "ExtractionResult",
    "InteractionResult",
    "NavigationResult",
    "ResearchResult",
    "ScreenshotResult",
    "SessionState",
    "VisionAnalysisResult",
    "VisualGroundingResult",
]
