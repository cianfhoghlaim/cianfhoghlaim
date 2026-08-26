"""dlt_sources.language — backward-compat re-export shim.

Per the 2026-09-25-ciancheiltis-init-v1 openspec change + the parent change
`2026-08-24-dlt-sources-to-multi-repo-scaffold-v1` §21.3 (the Phase 4 carve-out
hand-off), the `language/`, `cultural_heritage/`, and `lexicographic/`
subtrees have moved from Cianfhoghlaim to the new Ciancheiltis sister repo.

This module is the backward-compatibility shim that lives at the OLD path in
Cianfhoghlaim. New code SHOULD import directly from the Ciancheiltis sister
repo: `from ciancheiltis.dlt_sources.lexicographic import *` (or the
`cultural_heritage` sub-package).

The 3 themed sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change were:

- `dlt_sources.lexicographic/` — carved to Ciancheiltis
- `dlt_sources.cultural_heritage/` — carved to Ciancheiltis
- `dlt_sources.local_archive/` — STAYS in Cianfhoghlaim per the bilingual
   educational carve rule (local_archive contains education-curriculum-
   referenced local-language sources)

Emits a `DeprecationWarning` on import. Per the v2 plan §F + the
openspec bidirectional cascade contract #1, the Ciancheiltis sister repo
mirrors changes back into Cianfhoghlaim via the per-PR reciprocal PR +
the nightly mirror-merge sensor.
"""
from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "dlt_sources.language has moved to the ciancheiltis sister repo. "
    "Update your imports to `from ciancheiltis.dlt_sources.lexicographic "
    "import *` (or `from ciancheiltis.dlt_sources.cultural_heritage import *`). "
    "See openspec/changes/2026-09-25-ciancheiltis-init-v1/proposal.md for the "
    "carve-out plan + the bilingual educational carve rule.",
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name: str):
    """Lazy re-export — Ciancheiltis must be installed for the carved
    sub-packages (`lexicographic`, `cultural_heritage`); local_archive
    stays in Cianfhoghlaim."""
    if name == "local_archive":
        from dlt_sources import local_archive as _la
        return _la

    try:
        from ciancheiltis.dlt_sources import lexicographic as _lex
        from ciancheiltis.dlt_sources import cultural_heritage as _ch
    except ImportError as exc:
        raise ImportError(
            "dlt_sources.language.* requires ciancheiltis to be installed "
            "(the carve-out target per the 2026-09-25-ciancheiltis-init-v1 "
            "openspec change). Install via `uv pip install -e ../ciancheiltis` "
            "or wire the [tool.uv.sources] workspace declaration in Phase 3+."
        ) from exc

    if name == "lexicographic":
        return _lex
    if name == "cultural_heritage":
        return _ch

    raise AttributeError(f"module 'dlt_sources.language' has no attribute {name!r}")


__all__ = ["lexicographic", "cultural_heritage", "local_archive"]
