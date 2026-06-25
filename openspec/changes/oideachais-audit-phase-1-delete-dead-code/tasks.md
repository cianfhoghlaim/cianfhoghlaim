# Tasks: Oideachais Audit Phase 1 — Delete Dead Code

## 1. Pre-flight verification

- [ ] 1.1 Confirm zero importers of `sruth.oideachais.oideachais.core` + `sruth.oideachais.oideachais.data_platform`:
  ```bash
  grep -rEn "from oideachais\.oideachais|from sruth\.oideachais\.oideachais" sruth/ infrastructure/ scripts/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.2 Confirm zero importers of `sruth.oideachais.services.embedding_service`:
  ```bash
  grep -rEn "embedding_service" sruth/ infrastructure/ scripts/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.3 Confirm zero importers of `sruth.oideachais.marimo.ocr_comparison_enhanced`:
  ```bash
  grep -rEn "ocr_comparison_enhanced" sruth/ infrastructure/ scripts/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.4 Confirm zero importers of `sruth.oideachais.exam_scraper.{retry_failed,scrape_exam_stats}`:
  ```bash
  grep -rEn "from oideachais\.exam_scraper|from sruth\.oideachais\.exam_scraper|retry_failed|scrape_exam_stats" sruth/ infrastructure/ scripts/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.5 Confirm zero importers of `PIPELINE_OPERATIONS.md`:
  ```bash
  grep -rln "PIPELINE_OPERATIONS" sruth/ infrastructure/ docs/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.6 Confirm zero importers of the 5 orphaned test scripts:
  ```bash
  grep -rln "test_api\.py\|test_crawl\.py\|test_crawl2\.py\|test_full_crawl\.py\|test_all_sources\.py" sruth/ infrastructure/ 2>/dev/null | grep -v __pycache__
  ```
  Expected output: 0 matches.
- [ ] 1.7 Confirm `downloads/curriculum_pdfs/` is empty:
  ```bash
  ls -A sruth/oideachais/downloads/curriculum_pdfs/ 2>&1
  ```
  Expected output: empty / No such file.

## 2. Execute deletions

- [ ] 2.1 Delete nested legacy shim:
  ```bash
  git rm -r sruth/oideachais/oideachais/
  ```
- [ ] 2.2 Delete dead FastAPI embedding service:
  ```bash
  git rm -r sruth/oideachais/services/embedding_service/
  ```
- [ ] 2.3 Delete dead marimo stub:
  ```bash
  git rm -r sruth/oideachais/marimo/
  ```
- [ ] 2.4 Delete dead exam scraper:
  ```bash
  git rm -r sruth/oideachais/exam_scraper/
  ```
- [ ] 2.5 Delete empty downloads mount:
  ```bash
  rmdir sruth/oideachais/downloads/curriculum_pdfs/ && rmdir sruth/oideachais/downloads/
  ```
- [ ] 2.6 Delete orphaned PDF:
  ```bash
  git rm sruth/oideachais/leaving_cert_timetable.pdf
  ```
- [ ] 2.7 Delete orphaned doc:
  ```bash
  git rm sruth/oideachais/PIPELINE_OPERATIONS.md
  ```
- [ ] 2.8 Delete 5 orphaned root-level test scripts:
  ```bash
  git rm sruth/oideachais/test_api.py \
         sruth/oideachais/test_crawl.py \
         sruth/oideachais/test_crawl2.py \
         sruth/oideachais/test_full_crawl.py \
         sruth/oideachais/test_all_sources.py
  ```

## 3. Documentation updates

- [ ] 3.1 Update `sruth/oideachais/STATUS.md`:
  - Remove the "BAML × DLT × Dagster × CocoIndex matrix" reference to `oideachais/cocoindex_flows/curriculum_embedding.py` if any references to the deleted `marimo/ocr_comparison_enhanced.py` exist.
  - Update the "Top-level directory count" mention if present (61 → 56).
- [ ] 3.2 Update `sruth/oideachais/REFACTORING.md`:
  - Add a "Round 11, Phase 1 — done" entry to the changelog at the top of the file.
  - Strike through any backlog items now resolved by this change (e.g., "delete the oideachais nested legacy dir", "delete dead marimo stub").
- [ ] 3.3 Update `sruth/oideachais/AGENTS.md`:
  - Update the "12 oideachais-specific skills" mention in the cross-references section if it references any deleted dir.
  - Update the "Quick routing" table if it mentions `services/embedding_service/`.

## 4. Validation

- [ ] 4.1 Verify the openspec change validates:
  ```bash
  openspec validate oideachais-audit-phase-1-delete-dead-code --strict
  ```
  Must exit 0.
- [ ] 4.2 Verify Python import still works (the `__init__.py` and `pyproject.toml` are unchanged):
  ```bash
  python -c "import sruth.oideachais; print('OK')"
  ```
  Must print `OK`.
- [ ] 4.3 Verify the venv still resolves (deletion does not affect imports):
  ```bash
  uv sync
  ```
  Must succeed.
- [ ] 4.4 Run the canonical Dagster asset list:
  ```bash
  dg list defs
  ```
  Must show the same number of assets before and after.
- [ ] 4.5 Run the test suite (must still pass):
  ```bash
  uv run pytest sruth/oideachais/tests/ -x
  ```
  Expected: existing tests pass; no new failures introduced by the deletion.
- [ ] 4.6 Run the lint check (must still pass):
  ```bash
  mise run lint:skills
  ```
  Must report 108/108.
- [ ] 4.7 Verify the git status shows exactly the deletions (no surprises):
  ```bash
  git status --short
  ```
  Expected: 12 deletions, 0 modifications, 0 additions (other than the doc updates in step 3).

## 5. Archive + commit + push

- [ ] 5.1 Archive the change:
  ```bash
  openspec archive oideachais-audit-phase-1-delete-dead-code --yes
  ```
- [ ] 5.2 Stage all changes:
  ```bash
  git add -A
  ```
- [ ] 5.3 Commit with the conventional message format:
  ```bash
  git commit -m "oideachais(audit): round 11 phase 1 — delete 12 confirmed-dead items

  - DELETE sruth/oideachais/oideachais/ (nested legacy shim, 0 importers)
  - DELETE sruth/oideachais/services/embedding_service/ (dead FastAPI, 0 importers)
  - DELETE sruth/oideachais/marimo/ (dead 1-file stub, 0 importers)
  - DELETE sruth/oideachais/exam_scraper/ (dead 2-script, 0 importers)
  - DELETE sruth/oideachais/downloads/ (empty mount, 0 importers)
  - DELETE sruth/oideachais/leaving_cert_timetable.pdf (270 KB orphan)
  - DELETE sruth/oideachais/PIPELINE_OPERATIONS.md (orphaned doc)
  - DELETE 5 orphaned root-level test scripts (test_api, test_crawl*, test_all_sources)

  -310 KB total. 61 → 56 dirs. 0 LOC moved. Zero risk per pre-flight grep.

  Openspec: openspec/changes/archive/oideachais-audit-phase-1-delete-dead-code/"
  ```
- [ ] 5.4 Push to origin:
  ```bash
  git pull --rebase
  git push
  git status
  ```
  Expected final state: `up to date with origin`.

## Notes

- **Do NOT touch** `sruth/oideachais/__init__.py:30-44` (the legacy `data_platform` PEP 562 shim registration). That belongs to phase 5 (align pyproject.toml). The nested `oideachais/oideachais/` dir deletion is safe regardless because the shim registers an empty module that has no source files anyway.
- **Do NOT touch** `sruth/oideachais/settings.py`. It is imported by `infrastructure/observability/logging.py:21` and has its own deferred-to-phase-5 migration plan.
- **Do NOT touch** `sruth/oideachais/dashboard/`. It is a 1 MB Vite + Convex app that needs separate user decision.
