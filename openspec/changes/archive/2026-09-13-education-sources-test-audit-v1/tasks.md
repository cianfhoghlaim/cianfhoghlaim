# Tasks: Education Sources Test Audit v1

> 2 sections, 4 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-education-sources-test-audit-v1 --yes`.

## Phase A — Education source tests (10 min)

- [x] **A.1** Author `tests/education_sources/__init__.py` + `tests/education_sources/test_education_sources.py`
- [x] **A.2** Add 9 health tests (NCCA, OFQUAL, SQA, WJEC, CCEA, Crown deps, BIEP change, NCCA unified, LC subjects)

## Phase B — Validation (5 min)

- [x] **B.1** `uv run pytest tests/education_sources/ -v` all 9 pass
- [x] **B.2** `uv run openspec validate 2026-09-13-education-sources-test-audit-v1 --strict` exits 0
- [x] **B.3** `uv run openspec archive 2026-09-13-education-sources-test-audit-v1 --yes`
