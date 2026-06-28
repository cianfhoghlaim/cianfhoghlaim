# Round 11 Phase 3E — Split Crown Dependencies Umbrella + Break Circular Import

## Why

Phase 3D completed the per-source split of the 16 multi-source legacy files, but the Crown Dependencies umbrella at `dlt_sources/crown_dependencies/` was left untouched. That umbrella contains:

- `channel_islands.py` — defines BOTH `jersey_source` AND `guernsey_source` (2 `@dlt.source` functions)
- `isle_of_man.py` — defines `isle_of_man_source` (1 `@dlt.source` function)

The umbrella's `__init__.py` re-exports these sources, but the per-nation `iom/jey/ggy/education/__init__.py` shims ALSO re-export from the umbrella. This creates a **circular import**:

```
iom/education/__init__.py → crown_dependencies/__init__.py → crown_dependencies/isle_of_man.py
   ↑                                                                          ↓
   └──────────────── crown_dependencies/__init__.py ────────────────────────┘
   ↑                                                                          ↓
   jey/education/__init__.py → crown_dependencies/channel_islands.py ←────────┘
```

The umbrella itself flags this in its docstring: *"DEPRECATED LOCATION (2026-06-24)... The canonical home for Crown Dependencies education sources is `oideachais/dlt_sources/domains/education/{iom,jey,ggy}/`... New code MUST import from the canonical location."*

Phase 3E finishes the country-first cleanup by:

1. Splitting `channel_islands.py` (2 sources) into per-nation files
2. Moving `isle_of_man.py` (1 source) to its canonical home
3. Replacing the circular re-export chain with direct imports from canonical paths
4. Deleting the umbrella

## What changes

### 1. Split `crown_dependencies/channel_islands.py` → per-nation canonical files

| Legacy file | Sources | Splits into |
|:--|:--|:--|
| `crown_dependencies/channel_islands.py` | `jersey_source`, `guernsey_source` (2) | `jey/education/channel_islands.py` (jersey_source) + `ggy/education/channel_islands.py` (guernsey_source) + shared `_channel_islands_helpers.py` |

The shared private helper `_crawl_jersey_education` + `_crawl_guernsey_education` go into a sibling `_channel_islands_helpers.py` file (symmetric to the `_helpers.py` files in 3D).

### 2. Move `crown_dependencies/isle_of_man.py` → canonical home

| Legacy file | Source | Moves to |
|:--|:--|:--|
| `crown_dependencies/isle_of_man.py` | `isle_of_man_source` | `iom/education/isle_of_man.py` |

`_crawl_iom_education` stays private inside the file (single-source, no extraction needed).

### 3. Break the circular import

| File | Before | After |
|:--|:--|:--|
| `iom/education/__init__.py` | `from dlt_sources.crown_dependencies import isle_of_man` | `from dlt_sources.iom.education.isle_of_man import isle_of_man_source` |
| `jey/education/__init__.py` | `from dlt_sources.crown_dependencies import channel_islands` | `from dlt_sources.jey.education.channel_islands import jersey_source` |
| `ggy/education/__init__.py` | `from dlt_sources.crown_dependencies import channel_islands` | `from dlt_sources.ggy.education.channel_islands import guernsey_source` |

### 4. Delete the `crown_dependencies/` umbrella

After the canonical files exist + the shims import from them, the umbrella (`crown_dependencies/__init__.py`, `crown_dependencies/channel_islands.py`, `crown_dependencies/isle_of_man.py`, plus cached `__pycache__/`) is no longer needed and can be removed.

The one consumer in production code, `dagster_defs/assets/uk_education_assets.py`, needs its imports rewritten to the canonical paths.

## Impact

- 2 legacy multi-source files → 3 canonical files (2 per-nation + 1 helper) + 1 single-source file
- 4 `__init__.py` shims updated (3 per-nation + the umbrella itself removed)
- 1 importer rewritten (`dagster_defs/assets/uk_education_assets.py`)
- 1 broken circular import eliminated
- ~200 LOC net reduction (umbrella docstring + re-export boilerplate gone)

## Risk

- **MEDIUM**: The circular import has been there for ~2 weeks; consumers that import `from dlt_sources.crown_dependencies import X` will break. Need to find all consumers and migrate them. Mitigation: update the umbrella shim BEFORE deleting it (run the new canonical files in parallel + update consumers, then delete).
- Some sources have nested `@dlt.resource` functions that need to move with their parent source.
- The umbrella's docstring mentions `oideachais/dlt_sources/domains/education/{iom,jey,ggy}/` (an outdated `domains/`-wrapped path); after 3E the actual canonical path is `oideachais/dlt_sources/{iom,jey,ggy}/education/` (per Phase 3B's drop of the `domains/` wrapper).

## Out of scope (deferred to Phase 4 or later)

- `dlt_sources/law/_legislation_helper.py` — top-level helper with broken `from ...ireland.curriculum_source import _crawl_source` (pre-existing fragility). Not a multi-source file, not a Crown Dependency issue.
- `dlt_sources/site_analysis/site_analysis.py` — single-source file at the canonical path; not a multi-source split issue.
- `dlt_sources/official_media/` subtree — complex (15+ files); deferred per Phase 3D.
- `dlt_sources/{ireland,uk,celtic,geospatial,bunchloch}/` legacy trees — already deleted in Phase 3D.