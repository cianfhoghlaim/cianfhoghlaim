# Phase 5 tasks

## 1. Specs

- [ ] 1.1 Update `openspec/specs/oideachais-pipeline/spec.md` with the
      "pyproject.toml + Canonical Docstrings Use oideachais.* Namespace"
      Requirement (3 Scenarios: pyproject 4 refs fixed, docstring 3
      refs fixed, crown_dependencies removed from shim list)

## 2. `pyproject.toml` (4 references)

- [ ] 2.1 Line 166: REMOVE `"data_platform.dagster_defs"` from
      `[tool.hatch.build.targets.wheel] packages` list
      (the package does not exist on disk; was dead weight in the
      wheel build)
- [ ] 2.2 Line 222: `module_name = "data_platform.dagster_defs.definitions"`
      → `module_name = "oideachais.dagster_defs.definitions"`
- [ ] 2.3 Line 229: `root_module = "data_platform.dagster_defs"`
      → `root_module = "oideachais.dagster_defs"`
- [ ] 2.4 Line 230: `code_location_target_module = "data_platform.dagster_defs.definitions"`
      → `code_location_target_module = "oideachais.dagster_defs.definitions"`
- [ ] 2.5 Verify with `python -c "import tomllib; tomllib.load(open('sruth/oideachais/pyproject.toml', 'rb'))"`

## 3. Docstring fixes (3 references)

- [ ] 3.1 `sruth/oideachais/dlt_utils/destinations.py:9`
      `from oideachais.data_platform.dlt_utils import get_dlt_destination, create_pipeline`
      → `from dlt_utils import get_dlt_destination, create_pipeline`
      (in docstring only)
- [ ] 3.2 `sruth/oideachais/dlt_sources/dg.toml:4`
      `# from sruth/oideachais/data_platform/dagster_defs/.`
      → `# from sruth/oideachais/dagster_defs/.`
- [ ] 3.3 `sruth/oideachais/dlt_sources/__init__.py:9`
      Remove `crown_dependencies,` from the legacy shim docstring
      list (Phase 3E deleted the `dlt_sources/crown_dependencies/`
      umbrella on 2026-06-26)

## 4. Validation

- [ ] 4.1 `openspec validate oideachais-audit-phase-5-align-pyproject --strict` MUST pass
- [ ] 4.2 `grep -rn "data_platform" sruth/oideachais/pyproject.toml sruth/oideachais/dg.toml sruth/oideachais/dlt_sources/__init__.py sruth/oideachais/dlt_utils/destinations.py` → ZERO matches
- [ ] 4.3 `python -c "import tomllib; tomllib.load(open('sruth/oideachais/pyproject.toml', 'rb'))"` parses cleanly
- [ ] 4.4 31/31 prior canonical imports still succeed (Phase 3D + 3E + 4 regression)
- [ ] 4.5 8/8 Phase 3D+E+4 tests pass (the 3 skipped domains stay skipped — pre-existing)

## 5. REFACTORING.md + commit + push + archive

- [ ] 5.1 Add Phase 5 entry to `sruth/oideachais/REFACTORING.md`
- [ ] 5.2 Stage ONLY the Phase 5 files (carefully avoid in-flight
      modifications: `.agents/skills/*.md`, `.infisical.env`,
      `infrastructure/AGENTS.md`, `pyproject.toml` at root — note
      the ROOT pyproject.toml is in-flight from another change,
      DO NOT touch; only `sruth/oideachais/pyproject.toml` is
      Phase 5 scope)
- [ ] 5.3 Single atomic commit + push
- [ ] 5.4 `openspec archive oideachais-audit-phase-5-align-pyproject --yes`
- [ ] 5.5 Commit + push the spec delta auto-applied by the archive step
