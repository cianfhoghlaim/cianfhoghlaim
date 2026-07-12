"""EUR-Lex institutional sub-tree.

Re-exports the canonical EUR-Lex DLT sources (regulations, directives,
decisions, treaties, CJEU case law) so call sites can do:

    from cianfhoghlaim.dlt.europeanunion.eur_lex import regulations
    pipeline.run(regulations.eur_lex_regulations_source())
"""
from __future__ import annotations

from cianfhoghlaim.dlt.europeanunion.eur_lex import (
    cjeu_case_law,
    decisions,
    directives,
    regulations,
    treaties,
)

__all__ = [
    "cjeu_case_law",
    "decisions",
    "directives",
    "regulations",
    "treaties",
]
