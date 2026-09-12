# Tasks: pipeline-computer_science-v1 (BIEP v3 Ireland LC Computer Science Pipeline)

## Stage 0 — Pre-flight
- [x] T0.1 — Confirm `pipeline-mathematics-v1` is shipped (the shared scaffolding + pytest harness pattern is reusable)

## Stage 1 — Computer Science CocoIndex v1 App
- [x] T1.1 — Create `cocoindex_flows/british_isles/ireland/education/lc/computer_science.py` (R1-R4 + BAML fallback)
- [x] T1.2 — Verify `from cocoindex_flows.british_isles.ireland.education.lc.computer_science import app, ComputerScienceChunk, run_computer_science_subject` imports cleanly
- [x] T1.3 — Verify `run_computer_science_subject(sourcedir=/nonexistent)` returns 3 rows from the in-tree fixture

## Stage 2 — Computer Science per-subject pytest
- [x] T2.1 — Create `tests/biep_parity_lc/test_computer_science.py` (4 tests)
- [x] T2.2 — Run `uv run pytest tests/biep_parity_lc/test_computer_science.py -v` and verify 4/4 pass

## Stage 3 — BAML fallback verification
- [x] T3.1 — Confirm `_BAML_AVAILABLE` is `False` (baml_client can't be generated)
- [x] T3.2 — Confirm `python_baml_fallback_extract("computer_science", ...)` returns non-empty `fields["topic"]` + `fields["level"]` + `fields["year"]`
- [x] T3.3 — Confirm the per-subject regex patterns match the canonical Computer Science vocabulary

## Stage 4 — Validation + handoff
- [x] T4.1 — Run `uv run pytest tests/biep_parity_lc/ -v` (full suite, all 29 tests pass)
- [x] T4.2 — Run `openspec validate pipeline-computer_science-v1 --strict`
- [x] T4.3 — Commit + push the change with a descriptive message

## Acceptance gate

This change is complete when:
- 4 Computer Science pytests pass (`tests/biep_parity_lc/test_computer_science.py`)
- All 29 pytests in `tests/biep_parity_lc/` pass (Mathematics + 5 sibling subjects)
- `openspec validate pipeline-computer_science-v1 --strict` passes
- The change is committed + pushed
