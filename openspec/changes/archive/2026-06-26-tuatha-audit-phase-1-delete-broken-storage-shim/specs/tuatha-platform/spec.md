# Spec Delta: Round 11 Phase 9 (tuatha Phase 1) — No broken cross-quadrant imports in tuatha storage

## ADDED Requirements

### Requirement: No broken cross-quadrant imports in tuatha storage

The system SHALL NOT contain a Python module under
`sruth/tuatha/` that imports from `sruth.shared.*`. The
`sruth.shared` package was deleted in commit `8484a6353` as
part of the canonical-home migration, so any remaining
`from sruth.shared.X import ...` in `sruth/tuatha/` is
guaranteed to fail at module-load time with
`ModuleNotFoundError: No module named 'sruth.shared'`.

Any tuatha submodule that historically re-exported a name
from `sruth.shared.*` MUST be either deleted (if the
functionality is available at the canonical home and there
are 0 active importers in the repo) or rewritten as a
thin re-export shim that delegates to the canonical home
(the same pattern used by
`sruth/tuatha/agents/tools/__init__.py` and the 4 spec-mandated
`sruth/tuatha/agents/adk/{celtic_tutor,mythology_narrator,quest_guide,research_assistant}.py`
thin re-export shims).

#### Scenario: `sruth.tuatha.storage` is importable

- **GIVEN** the rewrite of `sruth/tuatha/storage/__init__.py`
  to re-export from the canonical
  `sruth.oideachais.core.storage.serial_executor` module
- **AND** the deletion of the broken
  `sruth/tuatha/storage/serial_executor.py` shim
  (which previously imported from the deleted
  `sruth.shared.storage`)
- **WHEN** a developer runs
  `PYTHONPATH=./sruth uv run python -c "from sruth.tuatha.storage import SerialDatabaseExecutor"`
- **THEN** the import succeeds without `ModuleNotFoundError`
- **AND** `SerialDatabaseExecutor` is the same class object as
  `sruth.oideachais.core.storage.serial_executor.SerialDatabaseExecutor`

#### Scenario: Repo-wide grep for `from sruth.shared` in `sruth/tuatha/`

- **GIVEN** the rewrite of `sruth/tuatha/storage/__init__.py`
  and the deletion of the broken shim
- **WHEN** the developer runs
  `grep -rn "from sruth\.shared\|import sruth\.shared" sruth/tuatha/ --include="*.py"`
- **THEN** the output is empty (zero matches)
- **AND** no other tuatha submodule re-imports the
  deleted `sruth.shared` package
