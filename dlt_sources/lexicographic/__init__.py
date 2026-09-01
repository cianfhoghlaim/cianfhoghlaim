"""dlt_sources.lexicographic — Irish-language + Celtic lexicographic sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1). This package replaces the previous
`dlt_sources/language/` grab-bag. Each module is a single DLT source
that produces rows for one of the canonical Celtic / Irish-language
lexicographic databases:

| Module | Source name | Database |
|:--|:--|:--|
| `ainm.py` | `ainm_source` | Ainm — Irish place-names |
| `canuint.py` | `canuint_source` | Canúint — Irish dialect corpus |
| `canuint_audio.py` | `canuint_audio_source` | Canúint audio recordings |
| `canuint_dialect_summary.py` | `canuint_dialect_summary_source` | Canúint dialect summaries |
| `canuint_search.py` | `canuint_search_source` | Canúint search index |
| `canuint_word_alignment.py` | `canuint_word_alignment_source` | Canúint word alignment |
| `duchas.py` | `duchas_folklore` | Dúchas lexicon — *Schools' Collection* terminology |
| `gaois.py` | `gaois_source` | Gaois — National Terminology Database (English) |
| `gaois_combined.py` | `gaois_combined_source` | Gaois combined (multi-language) |
| `logainm.py` | `logainm_source` | Logainm — Placenames Database of Ireland |
| `tearma.py` | `tearma_source` | Téarma — Irish National Terminology Database |
| `tearma_search.py` | `tearma_search_source` | Téarma search index |

The 5 helpers (`_canuint_helpers.py`, `_gaois_helpers.py`,
`_tearma_helpers.py` + the `duchas_*.py` and `logainm.py` inline
helpers) are co-located with their primary sources per the master
plan §1.3 convention.

Reference:
- Master plan §3.2 ("Themed sub-trees")
- Master plan §7.1 ("dlt_sources/ migrations — lexicographic")
- `dlt_sources.AGENTS.md` §"Themed sub-trees"
"""
from __future__ import annotations

# Re-export the canonical source functions for convenience so that
# `from dlt_sources.lexicographic import ainm, canuint, ...` works.
# Each module exposes its own source function; importing the module
# is sufficient.
__all__ = [
    "ainm",
    "canuint",
    "canuint_audio",
    "canuint_dialect_summary",
    "canuint_search",
    "canuint_word_alignment",
    "duchas",
    "gaois",
    "gaois_combined",
    "logainm",
    "tearma",
    "tearma_search",
]
