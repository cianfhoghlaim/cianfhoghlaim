"""
Configuration management for Aleyum.

Provides Pydantic-based settings with environment variable support.
"""

from .settings import AleyumSettings, get_settings

__all__ = [
    "AleyumSettings",
    "get_settings",
]
