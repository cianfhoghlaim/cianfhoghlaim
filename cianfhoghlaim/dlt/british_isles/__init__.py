"""
oideachais.cianfhoghlaim.dlt.law — shared UK statutory-law helpers.

Crown Dependencies + UK nations (EN, NI, SCT, WLS) legislation sources all
share `_crawl_legislation()`. Canonical per-nation sources live in
`dlt_sources/{nation}/law/legislation.py`.
"""
from __future__ import annotations

__all__ = ["_crawl_legislation"]
