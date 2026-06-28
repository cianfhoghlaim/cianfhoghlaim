# Proposal: Round 11 Phase 5 — Delete pre-split `canuint.py` + `duchas_images.py` duplicates from meaisínfhoghlaim

## Why

Round 11 Phases 2 + 4 already deleted 4 byte-for-byte duplicate DLT source
files from `sruth/meaisinfhoghlaim/language/gaeilge/`
(`duchas.py` + `tearma.py` + `gaois.py` + `universal_dependencies.py` =
1,787 lines). Phase 5 finishes the same audit for the **two pre-split
multi-source** files that survived Phase 2: `canuint.py` (1,041 lines,
all 5 canuint sources bundled in one file) and `duchas_images.py` (787
lines, both `duchas_images_source` + `hidden_heritages_source` bundled).

Both files are **pre-split duplicates** of the canonical split versions
in `sruth/oideachais/dlt_sources/ie/culture/`. The canonical split was
landed in Phase 3D (canuint into 5 files, 1,095 lines total) and Phase 3D
(duchas_images into 2 files, 445 lines total). The meaisínfhoghlaim files
predate the split and were not migrated when Phase 2 deleted the 4
single-source duplicates.

The Phase 5 audit confirms **byte-level near-identity** (≤0.6% byte diff
across all 7 source functions):

| Source function | Bytes (meaisínfhoghlaim) | Bytes (canonical) | Diff | IDENTICAL? |
|:--|--:|--:|--:|:--|
| `canuint_source` | 9,904 | 9,862 | 42 | FALSE (decorator only) |
| `canuint_search_source` | 2,481 | 2,446 | 35 | FALSE (decorator only) |
| `canuint_audio_source` | 9,275 | 9,232 | 43 | FALSE (decorator only) |
| `canuint_dialect_summary_source` | 1,899 | 1,855 | 44 | FALSE (decorator only) |
| `canuint_word_alignment_source` | 11,363 | 11,320 | 43 | FALSE (decorator only) |
| `duchas_images_source` | 7,751 | 7,717 | 34 | FALSE (decorator only) |
| `hidden_heritages_source` | 2,601 | 2,564 | 37 | FALSE (decorator only) |
| **TOTAL** | **45,274** | **44,996** | **278** | (0.6% diff, decorator-only) |

The only byte difference between the meaisínfhoghlaim pre-split version
and the canonical split version is the
`@dlt.source(name="canuint_pronunciation")` decorator on the top-level
`canuint_source` function (the meaisínfhoghlaim version keeps the
`@dlt.source` decorator from the predecessor `bonneagar` migration;
the canonical split dropped it during the Phase 3D re-write). All 7
function bodies are otherwise byte-identical.

## What changes

### 1. DELETE `sruth/meaisinfhoghlaim/language/gaeilge/canuint.py`

- 1,041 lines, contains all 5 canuint sources
- 0 active importers (verified via repo-wide `grep`)
- Canonical split: 5 files, 1,095 lines
  (`canuint.py` 302 + `canuint_audio.py` 271 + `canuint_dialect_summary.py` 79
  + `canuint_search.py` 105 + `canuint_word_alignment.py` 338)

### 2. DELETE `sruth/meaisinfhoghlaim/language/gaeilge/duchas_images.py`

- 787 lines, contains both `duchas_images_source` + `hidden_heritages_source`
- 0 active importers (verified via repo-wide `grep`)
- Canonical split: 2 files, 445 lines
  (`duchas_images.py` 310 + `hidden_heritages.py` 135)

### Net deletion: 1,828 lines

## What does NOT change

- `sruth/meaisinfhoghlaim/language/gaeilge/__init__.py` — already empty (0 bytes)
- `sruth/meaisinfhoghlaim/language/gaeilge/irish_samples.yaml` — retained
  (different file: actual Irish-language reference data, not DLT code)
- `sruth/meaisinfhoghlaim/quality/canuint_validator.py` — only imports
  `get_logger` from `sruth.oideachais.observability.logging`, NOT from
  `language/gaeilge/canuint.py`. Verified via
  `grep -n "^from\|^import" sruth/meaisinfhoghlaim/quality/canuint_validator.py`

## Out of scope (deferred to other changes)

- `sruth/meaisinfhoghlaim/language/{brezhoneg,cymraeg,gaelg,gaidhlig,kernowek}/`
  Celtic-language YAML files — referenced by `agents/enhanced_orchestrator.py`,
  `agents/root_agent.py`, and `catalog/sources.yaml`. Real registry content,
  not duplicates. Audit-trail candidate only.
- `sruth/meaisinfhoghlaim/catalog/{models,sources}.yaml` — real ML data source
  registry, 279 lines total. Not duplicates.

## Impact

- **Net deletion**: 1,828 lines (the 2 pre-split duplicates).
- **Files touched**: 2 deletions + 1 README.md update.
- **No spec deletion**: spec mandates `language/gaeilge/` retain non-duplicate
  content only (Phase 2 already added this requirement). Phase 5 reinforces it
  by deleting the last 2 duplicate files.
- **Build risk**: very low. Both files have 0 importers. The canonical split
  files all import cleanly via `PYTHONPATH=./sruth python3`.
