# Tasks — fix-phantom-agents-and-ocr-backend-list-v1

## Step 1: Fix the 8 phantom agent paths in `root_agent.py:396-403` (1h)

- [x] Show the current state of `AgentDomain.<X>:` references in `root_agent.py`
- [x] Confirm the 8 actual per-subject agent files exist on disk under
      `cianfhoghlaim/agents/tuatha/`
      (`math_agent.py`, `appm_agent.py`, `chem_agent.py`, `geog_agent.py`,
      `hist_agent.py`, `engl_agent.py`, `gael_agent.py`, `comp_agent.py`)
- [x] Update `AGENT_MODULES` to use `cianfhoghlaim.agents.tuatha.<slug>_agent`
      (8 lines, lines 396-403)
- [x] Update the surrounding docstring + comment to reflect the new
      canonical home (1 docstring + 1 inline comment updated)
- [x] Verify no phantom paths remain in the file
      (`grep -n "meaisinfhoghlaim.educational" root_agent.py` → empty)
- [x] Verify all 8 modules resolve
      (`import_module("cianfhoghlaim.agents.tuatha.<slug>_agent")` × 8 → OK)

## Step 2: Add `unstract` + `tesseract-shadow` to `CLASSICAL_OCR`; remove `olmocr` + `pylaia` (45 min)

- [x] Read the current `CLASSICAL_OCR` (lines 687-724)
- [x] Remove `olmocr` and `pylaia` entries (legacy)
- [x] Add `unstract` entry (Unstract no-code LLM extraction, port 8002)
- [x] Add `tesseract-shadow` entry (Tesseract 4 shadow variant, port 8890)
- [x] Verify `len(CLASSICAL_OCR) == 6` and the 6 keys are exactly
      `{docling-serve, paddleocr, dots-ocr, unstract, tesseract, tesseract-shadow}`

## Step 3: Rename `get_default_for_m4_max` → `select_optimal_for_m4_max` (45 min)

- [x] Locate `get_default_for_m4_max` definition (was line 808, now line 813
      after Step 2 edit)
- [x] Rename function definition to `select_optimal_for_m4_max`
- [x] Update the internal call site (line 56 docstring example) to use
      the new name
- [x] Add a `get_default_for_m4_max()` back-compat alias that emits a
      `DeprecationWarning` and delegates to the canonical function
- [x] Run the sed rename sweep across the 6 per-subject agent files
      (`math_agent.py`, `chem_agent.py`, `comp_agent.py`, `engl_agent.py`,
      `gael_agent.py`, `geog_agent.py`) — no-op (they don't reference
      this helper directly; routing is via `wiring.py`)
- [x] Verify both function names exist in the registry

## Step 4: Verify the 3 fixes (30 min)

- [x] All 8 phantom agent paths resolve
      (`import_module("cianfhoghlaim.agents.tuatha.<slug>_agent")` × 8 → OK)
- [x] `CLASSICAL_OCR` has 6 entries including unstract
      (`len(CLASSICAL_OCR) == 6`, `'unstract' in CLASSICAL_OCR`)
- [x] `select_optimal_for_m4_max()` returns `"gemma-4-26B-A4B"`
- [x] `get_default_for_m4_max()` (alias) returns the same value
      AND emits `DeprecationWarning`
- [x] No phantom `meaisinfhoghlaim.educational` paths remain in
      `root_agent.py`

## Step 5: Write the openspec change (1h)

- [x] `proposal.md` — explains the 3 fixes + dependencies + acceptance gates
- [x] `tasks.md` — this file
- [x] `specs/meaisinfhoghlaim-agent-frameworks/spec.md` — MODIFIED:
      ADDED Requirement "8 per-subject ADK specialist agents resolve
      to `agents/tuatha/<slug>_agent.py` (NOT the phantom
      `agents/meaisinfhoghlaim/` path); all 8 dispatch through
      `select_optimal_for_m4_max` (canonical M4-Max helper, alias for
      `get_default_for_m4_max`)"
- [x] `specs/meaisinfhoghlaim-ocr-htr/spec.md` — MODIFIED:
      ADDED Requirement "The canonical 6 OCR backends (PaddleOCR +
      Docling + Dots-OCR + Unstract + Tesseract + Tesseract-shadow)
      are registered in `CLASSICAL_OCR`; the user-cited 6 backends are
      the source of truth"

## Step 6: Commit + push (5 min)

- [x] `git add -A` (the 3 source files + the openspec change)
- [x] Commit with the canonical 3-blocker message
- [x] `git push --set-upstream origin pick-4-biep-v1` (NOT `main`)

## Acceptance gates

- [x] The 8 phantom agent paths resolve (all 8 per-subject agents load)
- [x] `CLASSICAL_OCR` contains the canonical 6 backends (incl. Unstract + Tesseract-shadow)
- [x] `select_optimal_for_m4_max()` exists (with `get_default_for_m4_max`
      as back-compat alias that emits `DeprecationWarning`)
- [x] 2 MODIFIED spec deltas are well-formed
- [ ] Pushed to `origin/pick-4-biep-v1` (NOT `main`) — final step