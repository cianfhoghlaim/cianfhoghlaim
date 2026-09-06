"""PR0.1 — CLARIN-UK cross-domain Celtic linguistic bridges.

Phase 0 of ciancheiltis. CLARIN-UK is the UK national centre of the
Common Language Resources and Technology Infrastructure; the Celtic
resource family is hosted at
`https://www.clarin.ac.uk/resource-families/celtic-languages/` and
ships curated bilingual and monolingual corpora for the Irish,
Welsh, Scottish Gaelic, Manx, Breton, and Cornish languages.

This module is the cross-domain grounding layer that the six phase
sub-pipelines ingest against. The `corpus_browser` source runs
weekly; the `cadhan_aonair` and `focloir_gd_ga` sources run on demand.
"""
from __future__ import annotations


CLARIN_UK_CELTIC_FAMILY_URL = (
    "https://www.clarin.ac.uk/resource-families/celtic-languages/"
)
CADHAN_AONAIR_URL = "https://cadhan.com/index-en.html"
FOCLOIR_GD_GA_URL = "https://kevinscannell.com/files/gd2ga.pdf"


__all__ = [
    "CLARIN_UK_CELTIC_FAMILY_URL",
    "CADHAN_AONAIR_URL",
    "FOCLOIR_GD_GA_URL",
]
