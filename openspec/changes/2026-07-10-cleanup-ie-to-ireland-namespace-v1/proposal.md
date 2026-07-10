# Cleanup `ie/` → `ireland/` namespace migration

## What changes

This change scopes the legacy `british_isles/ie/` and `baml/ie/`
subtrees into their canonical post-v4 homes and fixes one broken
import chain in `_oide_helpers.py`:

1. **Removes** `cianfhoghlaim/dlt/british_isles/ie/` (7 files: 5 law
   `.py` + `__init__.py` + the empty `ie/__init__.py` shim).
2. **Removes** `cianfhoghlaim/baml/ie/` (8 files: 6 law `.baml` +
   `__init__.py` + the empty `ie/__init__.py` shim).
3. **Adds** `cianfhoghlaim/dlt/british_isles/ireland/education/law/`
   (the 5 migrated law `.py` files).
4. **Adds** `cianfhoghlaim/baml/education/law/` (the 6 migrated law
   `.baml` files + `__init__.py`).
5. **Rewrites** 17 Python + BAML imports + 31 active openspec `*.md`
   refs to the canonical namespaces.
6. **Fixes** the broken `from common.firecrawl_source import …`
   chain in `dlt/british_isles/ireland/education/_oide_helpers.py:11`
   by routing through the canonical `cianfhoghlaim.dlt.common`
   shim.

2 spec deltas:

- `specs/oideachais-pipeline/spec.md` — MODIFIED: canonical
  Ireland/law namespaces (dlt + baml) + zero remaining `ie/` refs
- `specs/oideachais-marimo-dashboards/spec.md` — MODIFIED: marimo
  notebooks reference canonical namespaces only

## Why

The post-v4 consolidation (2026-06-28) moved `oideachais.dlt.british_isles.ie.*`
and `oideachais.baml.ie.*` into the canonical
`oideachais.dlt.british_isles.ireland.education.*` + `oideachais.baml.education.*`
namespaces, but the `dlt/british_isles/ie/` and `baml/ie/` subtrees (containing
the Ireland/law extraction sources — 6 DLT files + 6 BAML files + 2 `__init__.py`
shims) were left behind.

This is a small, scoped, **2-hour** cleanup that lands the Ireland/law quadrant
in its canonical home so the v4 consolidation is fully consistent. It also
fixes a stray `from common.firecrawl_source import …` line in
`dlt/british_isles/ireland/education/_oide_helpers.py:11` that bypasses the
canonical `dlt.common` shim.

## What changed

### 1. Subtree moves (2 × 2 subtrees)

| Source (removed) | Destination (canonical) |
|:--|:--|
| `cianfhoghlaim/dlt/british_isles/ie/law/` | `cianfhoghlaim/dlt/british_isles/ireland/education/law/` |
| `cianfhoghlaim/dlt/british_isles/ie/__init__.py` | (removed — empty shim) |
| `cianfhoghlaim/baml/ie/law/` | `cianfhoghlaim/baml/education/law/` |
| `cianfhoghlaim/baml/ie/__init__.py` | (removed — empty shim) |

Files migrated:
- **DLT** (`dlt/british_isles/ireland/education/law/`): `piab.py`, `courts.py`,
  `judgements.py`, `court_rules.py`, `legal_aid.py` (5 files; 1 was a 0-byte
  `__init__.py`)
- **BAML** (`baml/education/law/`): `piab.baml`, `courts.baml`, `judgements.baml`,
  `court_rules.baml`, `legal_aid.baml`, `shared_legal_enums.baml` + `__init__.py`

### 2. Import rewrites (sed-pass)

17 Python + BAML imports + 31 openspec `specs/*.md` references rewrote:

| Pattern | Replacement |
|:--|:--|
| `from oideachais.dlt.british_isles.ie.law …` | `from oideachais.dlt.british_isles.ireland.education.law …` |
| `from oideachais.baml.ie.law …` | `from oideachais.baml.education.law …` |
| `from oideachais.dlt.british_isles.ie.<X>` | `from oideachais.dlt.british_isles.ireland.<X>` |
| `from oideachais.baml.ie.<X>` | `from oideachais.baml.education.<X>` |
| `dlt/british_isles/ie/` (string path) | `dlt/british_isles/ireland/` |
| `baml/ie/` (string path) | `baml/education/` |
| `oideachais.baml.ie.law`, `oideachais.baml.ie.<X>` (docstring refs) | canonical |
| `oideachais.dlt.british_isles.ie.<X>` (docstring refs) | canonical |
| `cianfhoghlaim.baml.ie.<X>`, `cianfhoghlaim.dlt.british_isles.ie.<X>` | canonical |

### 3. `_oide_helpers.py` import-chain fix

`cianfhoghlaim/dlt/british_isles/ireland/education/_oide_helpers.py:11` had:

```python
from common.firecrawl_source import crawl_website, scrape_page
```

The bare `common` alias is installed by `cianfhoghlaim/dlt/common/__init__.py`
via `sys.modules` at import time, but Dagster user-code import ordering can
race against the shim install and fail with `ModuleNotFoundError: No module
named 'common'`. Replaced with the canonical `dlt.common` path:

```python
from cianfhoghlaim.dlt.common import firecrawl_source
from cianfhoghlaim.dlt.common.incremental import compute_content_hash

crawl_website, scrape_page = firecrawl_source.crawl_website, firecrawl_source.scrape_page
```

The `dlt.common` shim itself is unchanged (it still installs the bare-`common`
alias for any other legacy callers).

### 4. Openspec spec rewrites (31 refs)

All 31 active `british_isles.ie.|dlt/british_isles/ie/|baml.ie` references
in `openspec/specs/**/*.md` migrated to the canonical `british_isles.ireland.|dlt/british_isles/ireland/` form. The 24 residual refs in
`openspec/changes/archive/**` are historical records and intentionally
preserved as-is.

## Verified

```bash
# Baseline (pre-change): 16 python + 1 baml + 31 openspec = 48 refs
# Post-change: 0 python + 0 baml + 0 active openspec = 0 refs
grep -rn "british_isles.ie\|dlt/british_isles/ie\|baml.ie" \
  --include='*.{py,baml,md}' cianfhoghlaim/ openspec/specs/
# → 0 matches
ls cianfhoghlaim/dlt/british_isles/ | grep -c '^ie$'   # → 0
ls cianfhoghlaim/baml/              | grep -c '^ie$'   # → 0
ls cianfhoghlaim/dlt/british_isles/ireland/education/law/   # 5 .py files
ls cianfhoghlaim/baml/education/law/                        # 6 .baml + __init__.py
```

## Out of scope (separate changes)

- `sruth.<quadrant>.*` namespace drift (100+ refs) — owned by
  `2026-07-09-v6-drift-remediation-and-repo-boundary-lockdown-v1`
- `oideachais.<X>` (bare-namespace) drift (100+ refs) — same change
- `sruth/` references in `.agents/skills/` (54 refs) — separate change

## Dependencies

`Blocked by: none`
`Affected repos: cianfhoghlaim`