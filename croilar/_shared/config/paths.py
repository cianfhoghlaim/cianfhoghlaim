"""
Path resolution for the croilar subproject.

The cianfhoghlaim monorepo has this layout:

    <repo_root>/
    ├── croilar/                    ← this package
    │   ├── dagster_assets/
    │   ├── pipelines/
    │   ├── _shared/                ← this file lives at _shared/config/paths.py
    │   └── ...
    ├── author_cian_deacy_lyons.../  ← CV / teaching / identity PDFs
    ├── oideachais/
    ├── tuatha/
    ├── meaisínfhoghlaim/
    ├── docs/
    ├── infrastructure/
    └── ...

Many assets and pipelines need to read the author directory which lives at
the repo root (NOT inside croilar/). Naive `Path(__file__).parent.parent...`
traversal is fragile — it breaks if the package is moved or installed
editable. This module provides a single, env-overridable way to resolve
the repo root.

Priority:
    1. ``CIANFHOGHLAIM_REPO_ROOT`` env var (set in mise.toml, compose, CI)
    2. ``CROILAR_REPO_ROOT`` legacy alias
    3. Compute from this file's location (4 levels up: _shared/config/paths.py
       → _shared → croilar → repo root)
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

# Path(__file__).parent.parent.parent.parent = repo root
_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# The author directory at the repo root
_AUTHOR_DIR_NAME = "author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin"


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    """Return the cianfhoghlaim monorepo root.

    Cached so repeated calls are O(1).
    """
    env = os.environ.get("CIANFHOGHLAIM_REPO_ROOT") or os.environ.get("CROILAR_REPO_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return _DEFAULT_REPO_ROOT


@lru_cache(maxsize=1)
def get_author_dir() -> Path:
    """Return the author PDFs directory at the repo root."""
    return get_repo_root() / _AUTHOR_DIR_NAME


def resolve_path(path: str | os.PathLike[str]) -> Path:
    """Resolve a path string against the repo root if it's relative.

    Absolute paths are returned as-is. Relative paths are interpreted
    as relative to the repo root (not the current working directory),
    which matches how the dagster assets and pipelines are configured.
    """
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    return get_repo_root() / p
