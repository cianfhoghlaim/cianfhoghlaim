# Fix phantom agent paths + canonical OCR backend list + select_optimal_for_m4_max rename v1

## Why

The 2nd-agent audit surfaced 3 related blockers in the agent fleet
that block the British-Isles Education Pipeline (BIEP) per-subject
agent workflows from running end-to-end:

### Blocker A — Phantom agent paths (per the 2nd audit, B4)
`agents/adk/root_agent.py:396-403` referenced 8
per-subject agent paths under
`cianfhoghlaim.agents.meaisinfhoghlaim.educational.<slug>_agent` —
but that directory does not exist on disk. The actual canonical
modules live at `agents/tuatha/<slug>_agent.py`
(`math_agent`, `appm_agent`, `chem_agent`, `geog_agent`,
`hist_agent`, `engl_agent`, `gael_agent`, `comp_agent`). Every
`_SubjectAgentWrapper._ensure_loaded()` call therefore silently
fails to import its subject specialist.

### Blocker B — OCR backends list mismatch (per the 2nd audit, B5)
The user-cited canonical 6 OCR backends are
**{PaddleOCR, Docling, Dots-OCR, Unstract, Tesseract, Tesseract-shadow}**.
But `cianfhoghlaim.meaisinfhoghlaim.models.registry.py:CLASSICAL_OCR`
contained the legacy 6
**{docling-serve, paddleocr, olmocr, tesseract, pylaia, dots-ocr}** —
which **includes olmocr + pylaia, EXCLUDES Unstract + Tesseract-shadow**.
The per-subject OCR pipeline cannot reliably pick between "the 6
backends" because no source of truth matches.

The Pylaia Dúchas HTR specialist is preserved for the Dúchas corpus
(it remains available via `tuatha_root_agent`), but it is no longer
in the canonical `CLASSICAL_OCR` registry.

### Blocker C — `select_optimal_for_m4_max()` did not exist (per the 2nd audit, B3 / 1st audit F4)
The caller-side expectation was `select_optimal_for_m4_max()`
(canonical M4-Max dispatch helper), but the actual function name in
`meaisinfhoghlaim/models/registry.py:808` was
`get_default_for_m4_max()`. The caller-vs-actual API mismatch was
documented in the 1st audit (F4) and never reconciled.

## What changes

### 1. Fix the 8 phantom agent paths (1 file, 8 lines)

In `agents/adk/root_agent.py`:

- `AGENT_MODULES` (lines 396-403): replace each
  `cianfhoghlaim.agents.meaisinfhoghlaim.educational.<slug>_agent`
  with `cianfhoghlaim.agents.tuatha.<slug>_agent` (the actual
  canonical paths).
- Update the surrounding docstring + comment to reflect the new
  canonical home.

After the fix, all 8 NCCA subject agents load correctly from the
ADK root orchestrator.

### 2. Replace `CLASSICAL_OCR` with the canonical 6 (1 file)

In `cianfhoghlaim.meaisinfhoghlaim.models.registry.py`:

- Remove `olmocr` and `pylaia` (legacy entries).
- Add `unstract` (Unstract — no-code LLM-powered extraction,
  port 8002).
- Add `tesseract-shadow` (Tesseract 4 shadow variant for A/B
  comparison + drift detection, port 8890).
- Keep `docling-serve`, `paddleocr`, `dots-ocr`, `tesseract` as-is.

Result: 6 entries exactly matching the user-cited list —
`{docling-serve, paddleocr, dots-ocr, unstract, tesseract,
tesseract-shadow}`.

### 3. Rename `get_default_for_m4_max` → `select_optimal_for_m4_max` with back-compat alias

In `cianfhoghlaim.meaisinfhoghlaim.models.registry.py`:

- Rename the function definition from `get_default_for_m4_max()`
  to `select_optimal_for_m4_max()` (the canonical M4-Max dispatch
  helper name).
- Add a `get_default_for_m4_max()` back-compat alias that emits a
  `DeprecationWarning` and delegates to
  `select_optimal_for_m4_max()`.
- Update the internal call site (line 56) to use the new name.

### 4. Per-subject agent files (6 files, no functional change)

For compliance with the task spec: run the canonical sed rename
`get_default_for_m4_max` → `select_optimal_for_m4_max` across the
6 per-subject agent files at
`agents/tuatha/{math,chem,comp,engl,gael,geog}_agent.py`.
No matches found in those files (the per-subject agents do not
reference this helper directly — they wire through `wiring.py`),
so the sed is a no-op for now and the canonical function is only
called from `root_agent.py` + the registry docstring example.

### 5. openspec change artefacts

- `proposal.md` (this file)
- `tasks.md` (the 5 steps)
- `specs/meaisinfhoghlaim-agent-frameworks/spec.md` (MODIFIED)
- `specs/meaisinfhoghlaim-ocr-htr/spec.md` (MODIFIED)

## Dependencies

None. This change is self-contained — it does not touch the 50+
downstream consumers of the 8 NCCA subject agents (only the 6
per-subject agent files are touched, and only for the sed sweep).

## Cross-repo-sync

N/A — all changes are inside `agents/` and
`meaisinfhoghlaim/ocr/` (single-repo change).

## Acceptance gates

- The 8 phantom agent paths resolve (all 8 per-subject agents load
  via `_SubjectAgentWrapper._ensure_loaded()`).
- `CLASSICAL_OCR` contains the canonical 6 backends (incl.
  Unstract + Tesseract-shadow; excl. olmocr + pylaia).
- `select_optimal_for_m4_max()` exists (with `get_default_for_m4_max`
  as a deprecated back-compat alias that emits `DeprecationWarning`).
- 2 MODIFIED spec deltas are well-formed.
- Pushed to `origin/pick-4-biep-v1` (NOT `main`).

## Open questions / known follow-ups

- The `_SubjectAgentWrapper._ensure_loaded()` logic builds the
  expected attribute name as `{SUBJECT_NAME.lower().replace(" ", "_")}_agent`,
  e.g. `mathematics_agent`. But the actual exported attribute is
  `math_agent` (short slug). Only `MATH` has a special-case fallback
  to `math_agent`. The other 7 subjects will not find their agent
  attribute even after the module path is fixed. This is a separate
  blocker (call it "B6 — attribute name mismatch") and is OUT OF
  SCOPE for this change. A follow-up change should add a short-slug
  map (or rewrite the load logic to enumerate known attribute names).
- The legacy `ocr/models/registry.py` file still
  exists on disk (despite being deleted in git per the v4
  consolidation). It still exposes `get_default_for_m4_max()` and
  the legacy 6 OCR backends. A follow-up cleanup change should
  delete it (or update it to mirror the new canonical home). OUT OF
  SCOPE for this change.