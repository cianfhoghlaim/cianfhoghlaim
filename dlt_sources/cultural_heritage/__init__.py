"""dlt_sources.cultural_heritage — backward-compat re-export shim.

Per the 2026-09-25-ciancheiltis-init-v1 openspec change + the parent change
`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` §21.3 (the Phase 4 carve-out
hand-off), the `language/`, `cultural_heritage/`, and `lexicographic/`
subtrees have moved from Cianfhoghlaim to the new Ciancheiltis sister repo.

This module is the backward-compatibility shim that lives at the OLD path in
Cianfhoghlaim. New code SHOULD import directly from the Ciancheiltis sister
repo: `from ciancheiltis.dlt_sources.cultural_heritage import <symbol>`.

Emits a `DeprecationWarning` on import. Per the v2 plan §F + the openspec
bidirectional cascade contract #1, the Ciancheiltis sister repo mirrors
changes back into Cianfhoghlaim via the per-PR reciprocal PR + the
nightly mirror-merge sensor.
"""
from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "dlt_sources.cultural_heritage has moved to the ciancheiltis sister repo. "
    "Update your imports to `from ciancheiltis.dlt_sources.cultural_heritage "
    "import <symbol>`. See openspec/changes/2026-09-25-ciancheiltis-init-v1/"
    "proposal.md for the carve-out plan + the bilingual educational carve rule.",
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name: str):
    """Lazy re-export — Ciancheiltis must be installed for the carved
    `cultural_heritage` symbols. Phase 3+ will wire the [tool.uv.sources]
    workspace declaration so the re-export resolves transparently."""
    try:
        from ciancheiltis.dlt_sources import cultural_heritage as _ch
    except ImportError as exc:
        raise ImportError(
            "dlt_sources.cultural_heritage.* requires ciancheiltis to be "
            "installed (the carve-out target per the 2026-09-25-ciancheiltis-"
            "init-v1 openspec change). Install via `uv pip install -e "
            "../ciancheiltis` or wire the [tool.uv.sources] workspace "
            "declaration in Phase 3+."
        ) from exc
    return getattr(_ch, name)


__all__ = [
    "celtic_mythology",
    "duchas",
    "duchas_images",
    "gaois",
    "gaois_combined",
    "heritage",
    "hidden_heritages",
]
