# Tasks: meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs

## Phase 1: Fix 3 docstring typos (sruth.oideachas → sruth.oideachais)

- [ ] In `sruth/meaisinfhoghlaim/ocr/vision_comparison.py:16`, change
      `from sruth.oideachas.ocr.vision_comparison import compare_vision_models`
      to
      `from sruth.oideachais.ocr.vision_comparison import compare_vision_models`
- [ ] In `sruth/meaisinfhoghlaim/ocr/irish_processing.py:17`, change
      `from sruth.oideachas.ocr.irish_processing import IrishOCRProcessor`
      to
      `from sruth.oideachais.ocr.irish_processing import IrishOCRProcessor`
- [ ] In `sruth/meaisinfhoghlaim/ocr/adapters.py:11`, change
      `from sruth.oideachas.ocr.adapters import get_adapter, compare_ocr_models`
      to
      `from sruth.oideachais.ocr.adapters import get_adapter, compare_ocr_models`
- [ ] Verify: `grep -rn "sruth\.oideachas" sruth/meaisinfhoghlaim/` returns 0 hits

## Phase 2: Fix stale AGENTS.md reference (scéimre → baml_src)

- [ ] In `sruth/meaisinfhoghlaim/AGENTS.md:77`, change
      `sruth/oideachais/scéimre/` to `sruth/oideachais/baml_src/`
      and update the surrounding parenthetical to:
      `(currently the `baml_src → scéimre` rename is deferred per
      the `lateralise-british-isles-domains` decision; `baml_src/`
      remains canonical)`
- [ ] Verify: `grep -rn "sruth/oideachais/scéimre" sruth/meaisinfhoghlaim/`
      returns 0 hits
- [ ] Verify: `grep -rn "sruth/oideachais/scéimre" sruth/meaisinfhoghlaim/`
      AND `grep -rn "sruth/oideachais/scéimre" openspec/specs/meaisinfhoghlaim-platform/spec.md`
      together confirm no live path-reference; the spec.md:266
      deferral note is the only surviving mention of "scéimre"
      in the meaisínfhoghlaim subtree

## Phase 3: Delete 3 dead services/ stubs

- [ ] `git rm sruth/meaisinfhoghlaim/services/celery_worker.py`
- [ ] `git rm sruth/meaisinfhoghlaim/services/pipeline_fastapi.py`
- [ ] `git rm sruth/meaisinfhoghlaim/services/agent_fastapi.py`
- [ ] Verify: `ls sruth/meaisinfhoghlaim/services/` returns only
      `__init__.py` (the 3 stubs are deleted)
- [ ] Verify: `grep -rn "meaisinfhoghlaim.services\|services.celery_worker\|services.pipeline_fastapi\|services.agent_fastapi" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__`
      returns 0 hits (no importers anywhere in the actual codebase)

## Phase 4: Update README.md Known issues table

- [ ] In `sruth/meaisinfhoghlaim/README.md`, append 3 new rows to
      the "Known issues" table (after the existing row #6
      RESOLVED row):
      - `| 7 | 3 docstring typos in ocr/{vision_comparison,irish_processing,adapters}.py referenced the non-existent path sruth.oideachas/ (typo for sruth.oideachais/). Docstring-only; no active imports were broken. | the 3 ocr/*.py files | RESOLVED (round 11 audit) |`
      - `| 8 | sruth/meaisinfhoghlaim/AGENTS.md:77 forward-referenced sruth/oideachais/scéimre/ (a deferred-rename target). Updated to sruth/oideachais/baml_src/ + a one-line note pointing at the lateralise-british-isles-domains deferral. | AGENTS.md:77 | RESOLVED (round 11 audit) |`
      - `| 9 | 3 dead stub files in services/ (celery_worker.py + pipeline_fastapi.py + agent_fastapi.py, 42 lines total). Phase-8-aspirational prototypes never imported anywhere. Deleted; services/ retains __init__.py. | services/ | RESOLVED (round 11 audit) |`

## Phase 5: Validate + archive

- [ ] `openspec validate meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs --strict` → PASS
- [ ] Commit + push the 7 file changes
- [ ] `openspec archive meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs --yes` → auto-applies spec delta
- [ ] Commit + push the auto-applied spec delta
