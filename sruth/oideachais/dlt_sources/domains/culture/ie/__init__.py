"""oideachais.dlt_sources.domains.culture.ie — Ireland cultural-heritage sub-package.

Phase 1 of the `ingest-culture-heritage` openspec change. Sources the 6
personal-heritage Gemini Deep Research PDFs at
`leabharlann/gemini_deep_research/culture/` and the 3 Wikipedia fixtures
at `oideachais/dlt_sources/official_media/fixtures/identity_*.json`.
"""
from __future__ import annotations

from dlt_sources.domains.culture.ie import heritage_source

__all__ = ["heritage_source"]