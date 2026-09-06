"""PR0.1 — Cadhan Aonair Universal Dependencies Celtic treebanks.

`cadhan.com` is the home of the Universal Dependencies (UD) Celtic
treebanks. Per the `celtic-language-pipeline` spec, the relevant
treebanks are:

- UD_Irish-IDT (modern Irish)
- UD_Irish-Cadhan (Irish historical)
- UD_Irish-TwittIrish (Irish Twitter-derived)
- UD_Scottish_Gaelic-ARCOSG (Scottish Gaelic)
- UD_Welsh-CCG (Welsh)
- UD_Breton-KEB (Breton)
- UD_Manx-Cadhan (Manx)

These are CoNLL-U text files ingested from
`repos/universal_dependencies/` on disk; the `language_detector`
helper is unnecessary because the treebank filenames carry the
language identity.

This is a deferred stub — live ingestion awaits the next Firecrawl
reset (keyless tier is exhausted today).
"""
from __future__ import annotations

from dlt_sources.ciancheiltis.clarin_uk import CADHAN_AONAIR_URL


SOURCE_ID = "ciancheiltis.clarin_uk.cadhan_aonair"


TREEBOOKS = [
    "UD_Irish-IDT",
    "UD_Irish-Cadhan",
    "UD_Irish-TwittIrish",
    "UD_Scottish_Gaelic-ARCOSG",
    "UD_Welsh-CCG",
    "UD_Breton-KEB",
    "UD_Manx-Cadhan",
]


__all__ = ["TREEBOOKS", "SOURCE_ID", "CADHAN_AONAIR_URL"]
