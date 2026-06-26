# Spec Delta: Round 11 Phase 11 (tuatha Phase 3) — No missing package `__init__.py` in tuatha

## ADDED Requirements

### Requirement: No missing package `__init__.py` in tuatha

The system SHALL provide a valid `__init__.py` file in every
sub-package of `sruth/tuatha/` that is declared in
`pyproject.toml` under
`[tool.hatch.build.targets.wheel].packages`. The umbrella
package itself SHALL also have an `__init__.py` so `tuatha`
is a real Python package (importable as `from tuatha.X import Y`).

A package directory without an `__init__.py` falls back to a
PEP 420 namespace package, which:

1. Has unpredictable import resolution across Python versions.
2. **Cannot contain sub-packages** — PEP 420 namespace packages
   can only contain modules, not nested package directories.
3. Breaks `hatch` builds that validate the manifest against
   filesystem reality.
4. Breaks the `pytest` conftest at
   `sruth/tuatha/tests/conftest.py:8` which (after the Phase 11
   import-name fix) does `from tuatha.api.main import app` —
   fails with `ModuleNotFoundError: No module named 'tuatha'`.

The fix mirrors the croilar packaging fix from commit
`e9e0fc7d2` ("fix(croilar): close issue #17 — packaging fix
for the dagster code-location"): create the umbrella
`__init__.py` + change `[tool.hatch.build.targets.wheel]`
to `packages = ["."]` so hatch auto-detects sub-packages
that have an `__init__.py` + create a post-install
`fix-pth.sh` script that rewrites the broken uv-generated
`.pth` file so `import tuatha` resolves to
`sruth/tuatha/__init__.py`.

#### Scenario: `import tuatha` succeeds

- **GIVEN** the new `sruth/tuatha/__init__.py` (canonical
  package marker) is created
- **AND** the new `sruth/tuatha/api/__init__.py` is created
- **AND** `sruth/tuatha/scripts/fix-pth.sh` has been run
  (rewriting the `.pth` file)
- **WHEN** a developer runs `uv run python -c "import tuatha"`
- **THEN** the import succeeds
- **AND** `tuatha.__file__` points to
  `sruth/tuatha/__init__.py`
- **AND** `from tuatha.api.main import app` succeeds (the
  conftest's actual usage, after the Phase 11 import-name fix)

#### Scenario: A sub-package inside `tuatha.cocoindex_flows/` is importable

- **GIVEN** the new `sruth/tuatha/cocoindex_flows/__init__.py`
- **AND** the new `sruth/tuatha/cocoindex_flows/transforms/__init__.py`
- **AND** `sruth/tuatha/scripts/fix-pth.sh` has been run
- **WHEN** a developer runs
  `uv run python -c "from tuatha.cocoindex_flows.transforms.celtic_multilingual import detect_celtic_language"`
- **THEN** the import succeeds
- **AND** `detect_celtic_language` is callable

#### Scenario: Repo-wide grep finds no missing `__init__.py` in tuatha subdirs

- **GIVEN** the 5 new `__init__.py` files created by Phase 3
- **WHEN** the developer runs a check that every subdir under
  `sruth/tuatha/` listed in `pyproject.toml`'s packages array
  has an `__init__.py`
- **THEN** the check passes for all 12 listed subdirs
  (`dlt_sources`, `dagster_assets`, `cocoindex_flows`,
  `knowledge_graph`, `agents`, `api`, `storage`,
  `asset_generation`, `dlt_utils`, `fibo_generation`,
  `demo`, `tests`)
- **AND** the umbrella `sruth/tuatha/` itself has
  `__init__.py`