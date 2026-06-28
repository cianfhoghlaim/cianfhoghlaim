# Phase 5 — Align `pyproject.toml` + docstrings to canonical `oideachais.*` namespace

## Why

Post-cleanup (commit `8484a6353`) the legacy `oideachais/data_platform/`
namespace was deleted. The current code lives at `sruth/oideachais/`
and the canonical Python package name is `oideachais`. However 4 stale
`data_platform.*` references remain in `pyproject.toml` plus 2 stale
references in docstrings + 1 in the `dlt_sources/__init__.py` shim
docstring.

The `data_platform.dagster_defs` package does not exist on disk; these
references would break `dg dev`, the wheel build, and confuse any
agent that reads the config. The `dg.toml` at `sruth/oideachais/dg.toml`
already uses the correct `oideachais.dagster_defs.definitions` form,
but the `[tool.dagster]` + `[tool.dg.project]` + `[tool.hatch.build]`
sections in `pyproject.toml` still point at the legacy path.

## What changes

### `pyproject.toml` — 4 references fixed

| Line | Section | Before | After |
|:--|:--|:--|:--|
| 166 | `[tool.hatch.build.targets.wheel] packages` | `"data_platform.dagster_defs"` | REMOVED (package does not exist on disk) |
| 222 | `[tool.dagster] module_name` | `"data_platform.dagster_defs.definitions"` | `"oideachais.dagster_defs.definitions"` |
| 229 | `[tool.dg.project] root_module` | `"data_platform.dagster_defs"` | `"oideachais.dagster_defs"` |
| 230 | `[tool.dg.project] code_location_target_module` | `"data_platform.dagster_defs.definitions"` | `"oideachais.dagster_defs.definitions"` |

### Docstring fixes — 3 references

| File | Line | Fix |
|:--|:--|:--|
| `dlt_utils/destinations.py:9` | docstring usage example | `from oideachais.data_platform.dlt_utils import …` → `from dlt_utils import …` |
| `dlt_sources/dg.toml:4` | comment | `# from sruth/oideachais/data_platform/dagster_defs/.` → `# from sruth/oideachais/dagster_defs/.` |
| `dlt_sources/__init__.py:9` | shim docstring | `Legacy flat trees dlt_sources/{ireland,uk,crown_dependencies,celtic,bunchloch,geospatial,official_media}/` → remove `crown_dependencies,` (deleted in Phase 3E) |

## Out of scope (deferred)

- The `data_platform.*` STRING values in
  `dagster_defs/factories.py:47,285,292,299,315,…` — these are
  `DLTAssetConfig.source_module` strings used to dynamically import
  modules at runtime. The canonical paths post-Phase 3C/3D are
  `oideachais.dlt_sources.ie.education.ncca` etc. Fixing them is a
  separate concern (data plumbing, not config alignment) and would
  also touch assets that were intentionally left unwired (per the
  pre-existing queued `wire-unwired-dlt-sources` change).
- `CHANGELOG.md` historical references — leave alone.
- `tests/dagster_defs/test_definitions_loads.py` and
  `tests/sources/test_cross_namespace.py` — both already enforce
  no-`data_platform`-imports; leave them as the regression guards
  they are.
- `dg.toml` at `sruth/oideachais/dg.toml` already uses the correct
  form — only the comment is stale.
- Pre-existing top-level `oideachais/` dir (`.venv/` + `dagster.yaml`
  only) — out of scope; would break local tooling if touched.

## Validation

- `openspec validate oideachais-audit-phase-5-align-pyproject --strict` MUST pass
- `grep -rn "data_platform" sruth/oideachais/{pyproject.toml,dg.toml,dlt_sources,dlt_utils,dagster_defs}/…` — should return ZERO matches in pyproject.toml + canonical docstrings
- `python -c "import tomllib; tomllib.load(open('sruth/oideachais/pyproject.toml', 'rb'))"` parses cleanly
- 9/9 prior canonical imports still succeed (Phase 3D + 3E + 4 regression check)
- `mise run lint:skills` → 138/138 still pass
- No new tests added (this is a config-alignment change; the
  pre-existing `test_no_legacy_data_platform_imports` at
  `tests/dagster_defs/test_definitions_loads.py:93` already enforces
  no-`oideachais.data_platform` references)
