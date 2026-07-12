"""EU institutional pipeline — canonical path + cross-region contract.

Implements the EU institutional half of the
`european-union-official-language-pipeline` capability
(``openspec/specs/european-union-official-language-pipeline/spec.md``).

The umbrella spec for the global expansion is
``openspec/specs/cross-region-pipeline/spec.md`` — every file in this
directory obeys the canonical contract:

    dlt/european_union/<institution>/<source>.py
    source_id = european_union.<institution>.<source_slug>
    language  ∈ {bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu,
                 ga, it, lv, lt, mt, pl, pt, ro, sk, sl, es, sv}

Re-exports the per-institution submodules so call sites can do:

    from cianfhoghlaim.dlt.european_union import eur_lex, eurydice, ema
    pipeline.run(eur_lex.regulations_source())

or import the specific source function:

    from cianfhoghlaim.dlt.european_union.eur_lex.regulations import (
        eur_lex_regulations_source,
    )
"""
from __future__ import annotations

from cianfhoghlaim.dlt.european_union import (
    education,
    government,
    medicine,
    publications_office,
    statistics,
)
from cianfhoghlaim.dlt.european_union.eur_lex import (
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
    "education",
    "government",
    "medicine",
    "publications_office",
    "regulations",
    "statistics",
    "treaties",
]
