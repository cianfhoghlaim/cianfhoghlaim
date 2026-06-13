"""oideachais.dlt_sources.domains.law.ie — Ireland statutory-law DLT sources.

Phase 6 of the openspec change. Only **statutory** law sources per
the user decision (case law is reserved for a future
`case-law-and-precedent` change).
"""
from __future__ import annotations

from oideachais.dlt_sources.domains.law.ie import (
    doj,
    irish_statute_book,
    lawreform,
)

__all__ = ["doj", "irish_statute_book", "lawreform"]
