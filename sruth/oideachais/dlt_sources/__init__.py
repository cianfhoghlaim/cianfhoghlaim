"""
oideachais.dlt_sources — DLT source registry.

Canonical layout (country-first): `dlt_sources/{nation}/{domain}/{entity}.py`.
Cross-cutting surfaces: `dlt_sources/{cross,law,site_analysis,leabharlann}/`.
Legacy flat trees `dlt_sources/{ireland,uk,celtic,bunchloch,geospatial,official_media}/`
remain as compatibility shims during migration. (Note: the
`dlt_sources/crown_dependencies/` umbrella was deleted in Phase 3E
on 2026-06-26.)
"""
from __future__ import annotations

__all__: list[str] = []
