"""oideachais.dlt_sources.domains.education — domain-first education DLT source registry.

Phase 5 of the openspec change. Replaces the legacy
`oideachais.dlt_sources.{ireland,uk,crown_dependencies}/*` flat layout
with a `domain/{nation}/*` package tree. The legacy addresses remain
valid as re-export shims.
"""
from __future__ import annotations

from oideachais.dlt_sources.domains import education

__all__ = ["education"]
