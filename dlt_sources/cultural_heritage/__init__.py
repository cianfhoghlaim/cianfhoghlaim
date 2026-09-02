"""dlt_sources.cultural_heritage — Irish-language + Celtic cultural-heritage sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1). This package replaces the previous
`dlt_sources/language/` grab-bag. Each module is a single DLT source
that produces rows for one of the canonical Celtic / Irish cultural
heritage databases:

| Module | Source name | Database |
|:--|:--|:--|
| `celtic_mythology.py` | `celtic_mythology_source` | Celtic mythology corpus (Mythological Cycle, Ulster Cycle, etc.) |
| `duchas_corpus.py` | `duchas_images_source` | Dúchas manuscript images + transcriptions (IIIF + TEI-XML) |
| `heritage.py` | `heritage_source` | Heritage Council of Ireland — sites & monuments |
| `hidden_heritages.py` | `hidden_heritages_source` | Hidden Heritages folklore archive |
| `local_documents_by_subject.py` | `local_documents_by_subject_source` | Local archive (subject-bucketed) |
| `local_education_documents.py` | `local_education_documents_source` | Local archive (education-bucketed) |

The 2 helpers (`_duchas_corpus_helpers.py`, `_local_documents_helpers.py`)
are co-located with their primary sources per the master plan §1.3
convention.

> **Note on the Duchas split** (per master plan §1.4): the original
> `language/duchas.py` (the lexicon — Schools' Collection terminology)
> moved to `dlt_sources.lexicographic/duchas.py` with source name
> `duchas_folklore`. The `language/duchas_images.py` (the folklore
> corpus — manuscript images + transcriptions) moved to
> `dlt_sources.cultural_heritage/duchas_corpus.py` with source name
> `duchas_images_source`. Both keep their original source names so
> existing registry lookups work.

Reference:
- Master plan §3.2 ("Themed sub-trees")
- Master plan §7.1 ("dlt_sources/ migrations — cultural_heritage")
- `dlt_sources.AGENTS.md` §"Themed sub-trees"
"""
from __future__ import annotations

# Re-export the canonical source modules for convenience.
__all__ = [
    "celtic_mythology",
    "duchas_corpus",
    "heritage",
    "hidden_heritages",
    "local_documents_by_subject",
    "local_education_documents",
]
