"""Repo-root + author-dir path resolution — the canonical dlt_sources home.

Per the `2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` Phase 3 cleanup
(the `cianchosaint-fail-subtree-fixes-2026-08-25` sub-batch), the original
`_shared.config.paths` module from `stedding/web/_croilar_shared/` (the
Croilar subproject) was being imported as `from _shared.config import ...`
from inside `dlt_sources/cv/`, `dlt_sources/portfolio/`,
`dlt_sources/api_sources/researchgate.py`, and
`dlt_sources/api_sources/linkedin.py` — none of those are on the
`sys.path` for the dlt_sources tree, so every smoke-test load failed
with `ImportError: _shared`.

This module re-implements the same 3 helpers (same signatures, same
`lru_cache(maxsize=1)` semantics) so the broken absolute imports can
point at a canonical dlt_sources home without dragging the Croilar
subproject into the import graph.

Priority for `get_repo_root()`:
1. ``CIANFHOGHLAIM_REPO_ROOT`` env var (set in mise.toml, compose, CI)
2. ``CROILAR_REPO_ROOT`` legacy alias (kept for back-compat with the
   Croilar subproject's own deployment manifests)
3. Compute from this file's location (4 levels up: paths.py →
   common → dlt_sources → repo root)

Reference: `stedding/web/_croilar_shared/config/paths.py` (the
upstream Croilar-side implementation; this file is the dlt_sources-
side twin with the same contract).
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

# Path(__file__).parent.parent.parent = repo root
# (paths.py → common → dlt_sources → repo_root)
_DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# The author directory at the repo root — matches the Croilar-side name
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


__all__ = ["get_repo_root", "get_author_dir", "resolve_path"]
