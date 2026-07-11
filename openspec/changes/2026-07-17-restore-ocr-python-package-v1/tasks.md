# Tasks — Restore the canonical `cianfhoghlaim/ocr/` Python package

## 1. Verify the broken state

- [x] `git checkout pick-4-biep-v1`
- [x] Confirm `git status` shows the 3 deletions
  (`D cianfhoghlaim/ocr/__init__.py`,
  `D cianfhoghlaim/ocr/models/__init__.py`,
  `D cianfhoghlaim/ocr/models/registry.py`)
- [x] Reproduce the `ModuleNotFoundError`:
  `uv run python -c "from cianfhoghlaim.ocr.models.registry import VISION_MODELS, CLASSICAL_OCR"`
- [x] Confirm the back-compat shims also fail with
  `ModuleNotFoundError: No module named 'cianfhoghlaim.ocr'`
- [x] Count the 19 downstream consumers with
  `grep -rln "cianfhoghlaim\.ocr" cianfhoghlaim/ --include='*.py'`
- [x] Verify the audit's referenced `pyproject.toml` line numbers
  (272, 308-315, 316-323) **do not exist** — the file is 163 lines

## 2. Restore the canonical package from HEAD

- [x] `git checkout HEAD -- cianfhoghlaim/ocr/`
- [x] Verify line counts match HEAD:
  `wc -l cianfhoghlaim/ocr/__init__.py cianfhoghlaim/ocr/models/__init__.py cianfhoghlaim/ocr/models/registry.py`
  → 81 / 71 / 929 = 1081 total
- [x] Verify `git status --porcelain cianfhoghlaim/ocr/` is now
  empty (files match HEAD byte-for-byte)

## 3. Verify the canonical import works

- [x] `uv run python -c "from cianfhoghlaim.ocr.models.registry
  import VISION_MODELS, CLASSICAL_OCR; print(f'OK: {len(VISION_MODELS)}
  vision models, {len(CLASSICAL_OCR)} OCR backends')"`
  → `OK: 22 vision models, 6 OCR backends`
- [x] Verify all 19 OCR-using files AST-parse cleanly:
  `for f in $(grep -rln "cianfhoghlaim\.ocr" cianfhoghlaim/ --include='*.py'); do python -c "import ast; ast.parse(open('$f').read())"; done`
- [x] Verify the back-compat shims now resolve (with their
  expected `DeprecationWarning`s):
  `uv run python -W default -c "from cianfhoghlaim.meaisinfhoghlaim.models import VISION_MODELS"`

## 4. Write the openspec change

- [x] Create
  `openspec/changes/2026-07-17-restore-ocr-python-package-v1/`
- [x] `proposal.md` — explains the symptom, root cause, impact
  (19 files), scope (3 restored files only), and the **stale
  audit claims** about `pyproject.toml` line numbers
- [x] `tasks.md` — this file
- [x] `specs/oideachais-marimo-dashboards/spec.md` — MODIFIED:
  ADDED 1 requirement

## 5. Validate the openspec change

- [ ] `openspec validate 2026-07-17-restore-ocr-python-package-v1
  --strict`

## 6. Commit and push

- [ ] Stage only the restored files + the new openspec change:
  `git add cianfhoghlaim/ocr/ openspec/changes/2026-07-17-restore-ocr-python-package-v1/`
- [ ] Commit (using the build-agent identity, per the prompt):
  `git -c user.email="build-agent@cianfhoghlaim" -c user.name="Build Agent" commit -m "fix(infrastructure): restore the canonical cianfhoghlaim/ocr/ Python package"`
- [ ] Push to `origin/pick-4-biep-v1` (NOT `main`):
  `git push --set-upstream origin pick-4-biep-v1`