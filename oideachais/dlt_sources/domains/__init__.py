"""oideachais.dlt_sources.domains — domain-first DLT source registry.

Phase 5 of the openspec change. Replaces the legacy flat layout
`oideachais.dlt_sources/{ireland,uk,crown_dependencies}/*` with a
`domain/{nation}/*` package tree.
"""
from __future__ import annotations

from dlt_sources.domains import education

__all__ = ["education"]
