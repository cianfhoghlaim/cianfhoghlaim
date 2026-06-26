# Tasks: Round 11 Phase 10 (tuatha Phase 2) — Split `dlt_source` from `leaving_cert/__init__.py`

## Pre-flight

- [x] Confirmed `sruth/tuatha/dlt_sources/leaving_cert/__init__.py` (97 lines) contains 5 function definitions (1 `@dlt.source` + 3 `@dlt.resource` + 1 helper `download_and_upload_to_s3`)
- [x] Confirmed `leaving_cert_source` function definition + `exam_papers` + `marking_schemes` + `syllabus_documents` resource definitions are inside `__init__.py` (not a sibling file)
- [x] Confirmed `from dlt.sources.helpers import requests` is a DEAD import (never used in the module — verified via `grep -n "requests\." sruth/tuatha/dlt_sources/leaving_cert/__init__.py`)
- [x] Confirmed `sruth/tuatha/dlt_sources/mythology/` follows the correct convention: `__init__.py` is a 7-line re-export shim, `celtic_mythology.py` (408 lines) contains the actual source code
- [x] Confirmed `sruth/tuatha/dlt_sources/geospatial/` follows the correct convention: 3 sibling `.py` files (gaeltacht_boundaries, gaelic_communities, welsh_language_areas), `__init__.py` is the package marker
- [x] Confirmed `sruth/tuatha/dagster_assets/exam_analysis.py:22: from dlt_sources.leaving_cert import leaving_cert_source` is the active importer
- [x] Confirmed `sruth/tuatha/dagster_assets/definitions.py:14,32` loads exam_analysis.py module (so the import IS exercised)
- [x] Confirmed `sruth/tuatha/dlt_sources/__init__.py` does NOT import from `leaving_cert/` (the package isn't in the top-level `__all__`)

## Implementation

- [ ] Create openspec change directory `openspec/changes/tuatha-audit-phase-2-split-leaving-cert-source-in-init/`
- [ ] Write `proposal.md` (done)
- [ ] Write `tasks.md` (this file)
- [ ] Write `specs/tuatha-platform/spec.md` delta with 1 ADDED Requirement (no-dlt-source-in-package-init)
- [ ] Run `openspec validate tuatha-audit-phase-2-split-leaving-cert-source-in-init --strict` (must pass before commit)
- [ ] Create `sruth/tuatha/dlt_sources/leaving_cert/leaving_cert.py` — move 97 lines verbatim from `__init__.py`, then remove the dead `from dlt.sources.helpers import requests` import (no callers)
- [ ] Rewrite `sruth/tuatha/dlt_sources/leaving_cert/__init__.py` to a 7-line re-export shim (matching `mythology/__init__.py` convention)
- [ ] Update `sruth/tuatha/README.md` "Known issues" table — add 1 RESOLVED row: leaving_cert/__init__.py anti-pattern split
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from dlt_sources.leaving_cert import leaving_cert_source"` returns OK (importer still works)
- [ ] Verify post-state: `PYTHONPATH=./sruth ./.venv/bin/python -c "from dlt_sources.leaving_cert.leaving_cert import leaving_cert_source"` returns OK (sibling file directly importable)
- [ ] Verify post-state: `ls sruth/tuatha/dlt_sources/leaving_cert/` returns `__init__.py` + `leaving_cert.py` + `__pycache__/`
- [ ] Verify post-state: `wc -l sruth/tuatha/dlt_sources/leaving_cert/__init__.py sruth/tuatha/dlt_sources/leaving_cert/leaving_cert.py` returns ~7 lines + ~96 lines (1 fewer due to removed dead `requests` import)
- [ ] Run `mise run lint:skills` (123/123 pass)

## Commit + push

- [ ] Stage only files for this phase: 2 file moves (git mv + new sibling) + 1 __init__.py rewrite + 1 README.md update + 3 openspec files
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `infrastructure/stacks/monitoring/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`
- [ ] Commit 1: `refactor(tuatha): round 11 phase 10 (tuatha phase 2) — split leaving_cert dlt_source from __init__.py`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive tuatha-audit-phase-2-split-leaving-cert-source-in-init --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 10 spec delta to tuatha-platform`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/changes/tuatha-audit-phase-2-split-leaving-cert-source-in-init/` is now in `archive/` subdirectory
- [ ] Confirm spec delta is now part of `openspec/specs/tuatha-platform/spec.md`
- [ ] Confirm 17 changes archived in Round 11 (10 oideachais + 5 meaisinfhoghlaim + 2 tuatha)
