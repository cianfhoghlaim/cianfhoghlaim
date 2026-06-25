"""
Configuration management for Croílár.

Provides Pydantic-based settings with environment variable support
and path-resolution helpers used by dagster assets and pipelines.
"""

from .paths import get_author_dir, get_repo_root, resolve_path
from .settings import AleyumSettings, StreamSettings, get_settings

__all__ = [
    "AleyumSettings",
    "StreamSettings",
    "get_settings",
    "get_repo_root",
    "get_author_dir",
    "resolve_path",
]
