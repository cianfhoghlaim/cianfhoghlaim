"""dlt_sources.language_models — NLP / Universal Dependencies corpus.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change (master plan §3.2, §7.1). This package replaces the previous
`dlt_sources/language/` grab-bag's Universal Dependencies source.

The `universal_dependencies.py` source produces rows for the Universal
Dependencies (UD) treebanks — CoNLL-U formatted training corpora for
syntactic parsing, lemmatisation, and morphological tagging. UD is
fundamentally an NLP / language-model training corpus concern, NOT a
lexicographic or cultural-heritage concern, so it lives in its own
themed sub-tree.

| Module | Source name | Database |
|:--|:--|:--|
| `universal_dependencies.py` | `universal_dependencies_source` | Universal Dependencies (CoNLL-U treebanks) |

> **Sister-repo ownership** (per master plan §1.1, INVARIANT 1):
> UD corpora are owned by the `ciancheiltis` sister repo. The pinned
> cross-repo reference uses `ciar://ciancheiltis/datasets/ud_<lang>@v<N>`.
> This source is the `cianfhoghlaim` mirror that re-publishes the
> corpora into the consolidated `ducklake_cianfhoghlaim` DuckLake
> namespace.

Reference:
- Master plan §3.2 ("Themed sub-trees")
- Master plan §7.1 ("dlt_sources/ migrations — language_models")
- `openspec/specs/cianfhoghlaim-dlt-sources-multi-repo/spec.md` (INVARIANT 1 — bilingual carve)
"""
from __future__ import annotations

# Re-export the canonical source module for convenience.
__all__ = ["universal_dependencies"]
