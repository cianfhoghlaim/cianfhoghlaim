# Tasks: pipeline-mathematics-v1 (BIEP v3 Ireland LC Mathematics Pipeline)

## Stage 0 — Pre-flight
- [x] T0.1 — Verify `cocoindex` 1.0.20 resolves to the PyPI site-packages (not a local shadow)
- [x] T0.2 — Verify `orchestration/defs/__init__.py` exists (defect #2 fixed)
- [x] T0.3 — Verify `baml_client/` is unavailable (defect #3 still active — BAML fallback path is in use)

## Stage 1 — Per-subject shared scaffolding
- [x] T1.1 — Create `cocoindex_flows/british_isles/ireland/education/lc/__init__.py`
- [x] T1.2 — Create `cocoindex_flows/british_isles/ireland/education/lc/_shared.py` (LCSubjectSpec table + helpers)
- [x] T1.3 — Create `cocoindex_flows/british_isles/ireland/education/__init__.py` (so the relative imports resolve correctly)
- [x] T1.4 — Verify `from cocoindex_flows.british_isles.ireland.education.lc import LC_SUBJECTS, build_subject_fixture` imports cleanly

## Stage 2 — Mathematics CocoIndex v1 App
- [x] T2.1 — Create `cocoindex_flows/british_isles/ireland/education/lc/mathematics.py` (R1-R4 + BAML fallback)
- [x] T2.2 — Verify `from cocoindex_flows.british_isles.ireland.education.lc.mathematics import app, MathematicsChunk, run_mathematics_subject` imports cleanly
- [x] T2.3 — Verify `run_mathematics_subject(sourcedir=/nonexistent)` returns 3 rows from the in-tree fixture

## Stage 3 — Per-subject pytest suite
- [x] T3.1 — Create `tests/biep_parity_lc/__init__.py`
- [x] T3.2 — Create `tests/biep_parity_lc/conftest.py` (InMemoryLanceTable + cosine similarity + fixture helpers)
- [x] T3.3 — Create `tests/biep_parity_lc/test_mathematics.py` (9 tests)
- [x] T3.4 — Run `uv run pytest tests/biep_parity_lc/test_mathematics.py -v` and verify 9/9 pass

## Stage 4 — BAML fallback verification
- [x] T4.1 — Confirm `_BAML_AVAILABLE` is `False` (baml_client can't be generated)
- [x] T4.2 — Confirm `python_baml_fallback_extract("mathematics", ...)` returns non-empty `fields["topic"]` + `fields["level"]` + `fields["year"]`
- [x] T4.3 — Confirm the per-subject regex patterns match the canonical Mathematics vocabulary

## Stage 5 — Validation + handoff
- [x] T5.1 — Run `uv run pytest tests/biep_parity_lc/ -v` (full suite, all 29 tests pass)
- [x] T5.2 — Run `openspec validate pipeline-mathematics-v1 --strict`
- [x] T5.3 — Commit + push the change with a descriptive message

## Acceptance gate

This change is complete when:
- 9 Mathematics pytests pass (`tests/biep_parity_lc/test_mathematics.py`)
- All 29 pytests in `tests/biep_parity_lc/` pass (Mathematics + 5 sibling subjects)
- `openspec validate pipeline-mathematics-v1 --strict` passes
- The change is committed + pushed
