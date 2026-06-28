# meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources

## Why

The meaisínfhoghlaim quadrant has 4 stale duplicate DLT source
files in `sruth/meaisinfhoghlaim/language/gaeilge/` that are
byte-for-byte duplicates of canonical implementations in
`sruth/oideachais/dlt_sources/ie/{culture,education}/`. These
duplicates:

1. **Are NOT imported by any active Dagster asset or Python
   code** in the entire repo (verified by grep on `sruth/`
   excluding `.venv/` + `__pycache__/` + 3rd-party)
2. **Reference deleted paths** in their lazy `try/except`-wrapped
   import blocks:
   - `from sruth.oideachais.dlt_sources.celtic.duchas import duchas_source`
     — `dlt_sources/celtic/` was DELETED in Phase 3B
     (`oideachais-audit-phase-3b-drop-domains-wrapper`)
   - `from sruth.oideachais.dlt_sources.tearma import tearma_source`
     — `dlt_sources/tearma.py` flat file was DELETED in Phase 4
     (`oideachais-audit-phase-4-consolidate-legacy-dirs`)
   - `from sruth.shared.http import duchas_client` /
     `tearma_client` / `ainm_client, logainm_client`
     — `sruth/shared/` was DELETED in commit `8484a6353` (the
     predecessor `bonneagar` project package removal)
3. **Are TRUE duplicates** of canonical implementations (verified
   by comparing `@dlt.source` decorator lines + helper function
   signatures):

| Meaisínfhoghlaim file | Lines | Canonical home | Evidence |
|---|--:|---|---|
| `sruth/meaisinfhoghlaim/language/gaeilge/duchas.py` | 374 | `sruth/oideachais/dlt_sources/ie/culture/duchas.py` | Both have `_get_duchas_factory` at L41, `@dlt.source(name="duchas_folklore")` at L46, `_extract_volume_items` at L176, `_fetch_school_xml` at L271; both 374 lines |
| `sruth/meaisinfhoghlaim/language/gaeilge/tearma.py` | 485 | `sruth/oideachais/dlt_sources/ie/culture/tearma.py` (bulk export) + `tearma_search.py` (search) + `_tearma_helpers.py` (shared helpers + `TerminologyLinker` class) | Meaisínfhoghlaim version was the pre-Phase 4 source; Phase 4 extracted the helpers into `_tearma_helpers.py` + split the 2 sources into separate files |
| `sruth/meaisinfhoghlaim/language/gaeilge/gaois.py` | 551 | `sruth/oideachais/dlt_sources/ie/culture/logainm.py` + `ainm.py` + `gaois_combined.py` | Meaisínfhoghlaim version defined all 4 `@dlt.source` functions together; canonical was split per Phase 3D (one source per file) |
| `sruth/meaisinfhoghlaim/language/gaeilge/universal_dependencies.py` | 377 | `sruth/oideachais/dlt_sources/ie/education/universal_dependencies.py` | Both have `@dlt.source(name="universal_dependencies")` at L48 with identical `ud_path: str = "repos/universal_dependencies"` parameter; both 377 lines (a third stale copy also exists at `sruth/oideachais/celtic/universal_dependencies.py`, the pre-Phase 3B legacy location) |

**Total: 1787 lines of dead duplicate DLT source code.**

**Risk of leaving them in place**:
- Contributors will assume `from meaisinfhoghlaim.language.gaeilge.X`
  is a valid import path and write new code against it, then hit
  `ImportError` when the broken lazy import fails
- The dagster import smoke-test (`sruth/meaisinfhoghlaim/dagster_defs/assets/healthchecks.py`)
  checks 4 sub-packages but NOT `language.gaeilge.*`, so the
  broken imports are not caught at materialisation time
- Round 11 audit report readers see "language/gaeilge has
  Dúchas, Canúint, Téarma, Gaois, UD support" in the README
  status and assume those are live implementations — but
  only the canonical homes are wired into oideachais Dagster
  assets

## What changes

1. **Delete 4 stale duplicate DLT source files** in
   `sruth/meaisinfhoghlaim/language/gaeilge/`:
   - `git rm sruth/meaisinfhoghlaim/language/gaeilge/duchas.py`
   - `git rm sruth/meaisinfhoghlaim/language/gaeilge/tearma.py`
   - `git rm sruth/meaisinfhoghlaim/language/gaeilge/gaois.py`
   - `git rm sruth/meaisinfhoghlaim/language/gaeilge/universal_dependencies.py`

2. **Add a `meaisinfhoghlaim-platform` spec Requirement** documenting
   the no-duplicate-DLT-source invariant: DLT source implementations
   MUST live at the canonical `sruth/oideachais/dlt_sources/{nation}/{domain}/`
   path; the meaisínfhoghlaim `language/` sub-package MUST NOT
   contain re-implementations of the same DLT sources.

3. **Update `sruth/meaisinfhoghlaim/README.md`** Known issues table
   with 1 RESOLVED row (the duplicate-source removal).

## Out of scope

- **`canuint.py` (1041 lines) + `duchas_images.py` (787 lines)**
  in `sruth/meaisinfhoghlaim/language/gaeilge/`. The canonical
  equivalents are SIGNIFICANTLY SMALLER (302 + 310 lines
  respectively — 3.4× and 2.5× size ratio). They are NOT
  duplicates; they are richer/different implementations that
  likely contain additional features not present in the
  canonical versions. A separate investigation is needed
  to determine which is canonical (or whether the meaisínfhoghlaim
  versions should be merged into the canonical ones). Out of
  scope for this phase; will be tracked in a future change.
- **`sruth/oideachais/celtic/universal_dependencies.py`** — a
  third stale copy of the UD source at the pre-Phase 3B legacy
  path. This is in the oideachais quadrant, not meaisinfhoghlaim,
  and is part of the broader oideachais legacy cleanup (covered
  by the `wire-unwired-dlt-sources` change). Out of scope here.
- **The 13 active cross-quadrant imports** of `from sruth.oideachais.X`
  in meaisinfhoghlaim modules (e.g., `from sruth.oideachais.observability.logging import get_logger`).
  These are INTENTIONAL cross-quadrant dependencies per
  `sruth/meaisinfhoghlaim/AGENTS.md` and the README row 6 RESOLVED
  status. The imports target REAL modules (verified) and are
  the production dependency surface.
- **The 6 Celtic-language subdirs themselves** (`brezhoneg/`,
  `cymraeg/`, `gaelg/`, `gaidhlig/`, `kernowek/` + the reduced
  `gaeilge/`). The remaining files in `gaeilge/` (canuint.py,
  duchas_images.py, __init__.py, irish_samples.yaml) remain.

## Verification

- `grep -rn "meaisinfhoghlaim.language.gaeilge.duchas\|meaisinfhoghlaim.language.gaeilge.tearma\|meaisinfhoghlaim.language.gaeilge.gaois\|meaisinfhoghlaim.language.gaeilge.universal_dependencies" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__`
  → 0 hits (no importers anywhere in the actual codebase, both
  pre-fix AND post-fix)
- `ls sruth/meaisinfhoghlaim/language/gaeilge/` post-fix → `__init__.py`,
  `canuint.py`, `duchas_images.py`, `irish_samples.yaml`
  (4 files remain, down from 8)
- The canonical homes at `sruth/oideachais/dlt_sources/ie/culture/{duchas,tearma,tearma_search,_tearma_helpers,logainm,ainm,gaois_combined}.py`
  are unchanged (verified via git diff — only the 4 deletes
  in the commit)
- `openspec validate meaisinfhoghlaim-audit-phase-2-delete-stale-duplicate-dlt-sources --strict` → PASS
