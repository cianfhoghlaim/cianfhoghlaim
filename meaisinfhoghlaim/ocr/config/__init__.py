"""
Configuration utilities for oideachais pipeline.

Provides base settings classes and configuration management.
"""

from .base import FlowSettings, get_flow_settings

__all__ = [
    "FlowSettings",
    "get_flow_settings",
]
