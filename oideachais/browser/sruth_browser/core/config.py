"""Configuration for browser agent stack.

DEPRECATED: Import from browser.config instead.

This module re-exports from browser.config for backwards compatibility.
"""

import warnings

warnings.warn(
    "browser.core.config is deprecated. Import from browser.config instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export everything from root config module
from ..config import BrowserConfig, get_config

__all__ = ["BrowserConfig", "get_config"]
