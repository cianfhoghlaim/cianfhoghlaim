"""cianfhoghlaim.dlt.british_isles.ireland.law — Ireland legal DLT sources (Pick-8 scope).

Pick-8 scoped reimplementation of the 5 highest-value operational-law
sources for the Ireland/law quadrant. Co-exists with the absorbed
`2026-07-06-ireland-legal-pipeline` change (which lives at
`cianfhoghlaim/dlt/british_isles/ireland/law/`) — these are
intentionally distinct paths so the data plane has 2 parallel ingress
routes for the same domain.

Sources:
- `piab`         — Personal Injuries Assessment Board (injuries.ie)
- `courts`       — Courts Service of Ireland — forms + fees (courts.ie)
- `judgements`   — Judgements.ie — published court decisions
- `court_rules`  — Court Rules library (court-rules.ie / courts.ie/rules)
- `legal_aid`    — Legal Aid Board (legalaidboard.ie)
"""
from __future__ import annotations

from cianfhoghlaim.dlt.british_isles.ireland.law import (
    court_rules,
    courts,
    judgements,
    legal_aid,
    piab,
)

__all__ = [
    "court_rules",
    "courts",
    "judgements",
    "legal_aid",
    "piab",
]
