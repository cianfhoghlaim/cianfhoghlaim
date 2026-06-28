# meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs

## Why

The meaisínfhoghlaim quadrant has three classes of small, concrete
audit findings that have been verified by direct file inspection:

### 1. Three docstring typos: `sruth.oideachas` (missing the `is`)

The canonical package name is **`sruth/oideachais/`** (Irish genitive,
"of education"). Three OCR-module docstrings reference a non-existent
package `sruth/oideachas/` (Irish nominative, "education"). No such
directory exists:

```
$ ls sruth/oideachas
ls: sruth/oideachas: No such file or directory
```

The typos are in Usage-example code blocks, NOT active import
statements (verified by grep — all active imports use the correct
`sruth.oideachais.*`). They are nonetheless misleading to readers and
will cause copy-paste confusion:

| File | Line | Wrong | Correct |
|---|---|---|---|
| `sruth/meaisinfhoghlaim/ocr/vision_comparison.py` | 16 | `from sruth.oideachas.ocr.vision_comparison import compare_vision_models` | `from sruth.oideachais.ocr.vision_comparison import compare_vision_models` |
| `sruth/meaisinfhoghlaim/ocr/irish_processing.py` | 17 | `from sruth.oideachas.ocr.irish_processing import IrishOCRProcessor` | `from sruth.oideachais.ocr.irish_processing import IrishOCRProcessor` |
| `sruth/meaisinfhoghlaim/ocr/adapters.py` | 11 | `from sruth.oideachas.ocr.adapters import get_adapter, compare_ocr_models` | `from sruth.oideachais.ocr.adapters import get_adapter, compare_ocr_models` |

### 2. One stale AGENTS.md reference to a non-existent path

`sruth/meaisinfhoghlaim/AGENTS.md:77` states:

> **BAML schemas** live in `sruth/oideachais/scéimre/` (the Irish
> word for *schema*) — not here. Reuse them; don't redefine.

But `sruth/oideachais/scéimre/` does not exist. The actual canonical
BAML home is `sruth/oideachais/baml_src/`. The `baml_src → scéimre`
rename was DEFERRED per the `lateralise-british-isles-domains`
decision and is documented as such in `sruth/meaisinfhoghlaim/README.md:35`:

> The `BAML rename baml_src → scéimre` change promised in
> `sruth/meaisinfhoghlaim/AGENTS.md` was deferred per the
> `lateralise-british-isles-domains` decision. The `baml_src/`
> import path is still canonical.

The `meaisinfhoghlaim-platform` spec (`specs/meaisinfhoghlaim-platform/spec.md:266`)
also records the same deferral. The AGENTS.md line is the only stale
forward-reference; it should be updated to point to the current
canonical path.

### 3. Three dead stub files in `sruth/meaisinfhoghlaim/services/`

All three files are tiny stubs (9 + 13 + 20 lines = 42 lines total)
that were early prototypes for future Celery + FastAPI integration
layers. None are imported by ANY code in the entire repo (verified
by cross-quadrant grep excluding `.venv/` + `__pycache__/` +
Google/grpc 3rd-party stubs):

| File | Lines | Content summary |
|---|--:|---|
| `sruth/meaisinfhoghlaim/services/celery_worker.py` | 9 | 4-line Celery app pointing at `redis://dragonfly:6379/0`; never imported; not wired to any task queue |
| `sruth/meaisinfhoghlaim/services/pipeline_fastapi.py` | 13 | 9-line FastAPI app with one `/health` endpoint for "3 pipelines"; never imported; not deployed anywhere |
| `sruth/meaisinfhoghlaim/services/agent_fastapi.py` | 20 | 16-line FastAPI app with one `/health` endpoint for "12 agents"; never imported; not deployed anywhere |

All three files are dead prototype code from before the platform
finalised on LiteLLM + Dagster as the canonical LLM/queue surfaces.
The `services/__init__.py` package docstring says "Phase 8 deploys..."
— confirming the entire directory is a Phase 8 (deferred)
aspirational surface, not a live implementation. After deletion,
only `services/__init__.py` (the package marker) remains.

**Risk of leaving them in place**: contributors will see the files,
assume the queue / API surfaces exist, and try to wire tasks /
endpoints against them, hitting `ImportError` at runtime.

## What changes

1. **3 docstring typo fixes** in
   `sruth/meaisinfhoghlaim/ocr/{vision_comparison.py, irish_processing.py, adapters.py}`:
   `sruth.oideachas` → `sruth.oideachais`. No code-path changes;
   docstring-only.

2. **1 AGENTS.md reference fix** in `sruth/meaisinfhoghlaim/AGENTS.md:77`:
   replace `sruth/oideachais/scéimre/` with
   `sruth/oideachais/baml_src/`. Add a one-line note that the
   `baml_src → scéimre` rename was deferred per the
   `lateralise-british-isles-domains` decision.

3. **Delete 3 dead stub files**:
   - `git rm sruth/meaisinfhoghlaim/services/celery_worker.py`
   - `git rm sruth/meaisinfhoghlaim/services/pipeline_fastapi.py`
   - `git rm sruth/meaisinfhoghlaim/services/agent_fastapi.py`

4. **Add a `meaisinfhoghlaim-platform` spec Requirement** documenting
   the no-typos + no-dead-stubs invariants going forward.

5. **Update `sruth/meaisinfhoghlaim/README.md`** Known issues table
   with 3 RESOLVED rows (typo fix, AGENTS.md ref fix, dead-stub
   removal). The README is the audit-trail file for meaisínfhoghlaim
   (no REFACTORING.md / STATUS.md exists in this quadrant; the
   pattern is "RESOLVED (round N audit)" — see README.md row 6 for
   the prior round 8 resolution).

## Out of scope

- The 13 active cross-quadrant `from sruth.oideachais.X import Y`
  imports in meaisinfhoghlaim modules (observability.logging,
  settings, evaluation.ragas_pipeline, dlt_sources.celtic.duchas,
  dlt_sources.celtic.gaois, dlt_sources.tearma). These are
  intentional cross-quadrant dependencies per
  `sruth/meaisinfhoghlaim/AGENTS.md` (the meaisínfhoghlaim quadrant
  populates sruth/oideachais/). All target modules exist and resolve
  correctly (verified).
- The meaisínfhoghlaim BAML files at
  `sruth/meaisinfhoghlaim/baml_src/{audio_extraction,
  celtic_sources, image_generation, ocr_extraction,
  ocr_validation, gaois/{duchas, folklore_extraction,
  logainm, tearma}}.baml`. These are correctly placed in the
  meaisínfhoghlaim quadrant (not duplicated in
  `sruth/oideachais/baml_src/`) and are awaiting agent-layer
  integration. Not a refactor target.
- The `stedding/` and `stedding/dev/cianfhoghlaim*/` scrape-cache
  copies of the same 3 typo files. Those are local cache trees
  regenerated from upstream by dlt, never committed to git, and
  will be regenerated with the corrected docstrings on next scrape.
- The broader `meaisinfhoghlaim/` modernisation (12-agent fleet
  wiring, OCR model additions, marimo notebook completion) which
  is covered by other queued changes (`modernize-meaisin-cliste`
  ✓ complete, `complete-cognee-knowledge-graph`).

## Verification

- `grep -rn "sruth\.oideachas" sruth/meaisinfhoghlaim/` → 0 hits
  (post-fix)
- `ls sruth/meaisinfhoghlaim/services/` → only `__init__.py`
  (post-fix; 3 dead stubs deleted)
- `grep -rn "sruth/oideachais/scéimre" sruth/meaisinfhoghlaim/*.md`
  → 0 hits in AGENTS.md (post-fix); the spec deferral note in
  `openspec/specs/meaisinfhoghlaim-platform/spec.md:266` is
  preserved (it documents the deferred decision, not the
  live reference)
- `grep -rn "meaisinfhoghlaim.services\|services.celery_worker\|services.pipeline_fastapi\|services.agent_fastapi" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__`
  → 0 hits (no importers anywhere in the actual codebase)
- `openspec validate meaisinfhoghlaim-audit-phase-1-fix-typos-stale-paths-and-dead-stubs --strict` → PASS
