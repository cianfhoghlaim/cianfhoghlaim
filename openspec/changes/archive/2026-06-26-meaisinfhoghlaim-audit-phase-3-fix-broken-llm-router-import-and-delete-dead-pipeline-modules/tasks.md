# Tasks: meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules

## Phase 1: Fix broken `llm_router.py` import

- [ ] Read `sruth/meaisinfhoghlaim/pipelines/llm_router.py:20-30` to confirm the broken import context
- [ ] Verify the canonical home: `ls sruth/oideachais/core/utils/circuit_breaker.py` returns the file (it does; the class is defined at line 54)
- [ ] In `sruth/meaisinfhoghlaim/pipelines/llm_router.py:23`, change
      `from ..core.utils import CircuitBreaker`
      to
      `from sruth.oideachais.core.utils import CircuitBreaker`
      (with a one-line comment: `# Canonical home: sruth/oideachais/core/utils/circuit_breaker.py:54`)
- [ ] Verify: `PYTHONPATH=./sruth python3 -c "from meaisinfhoghlaim.pipelines.llm_router import ModelRouter, LLMCapability; print('OK')"` succeeds (no `ModuleNotFoundError`)
- [ ] Verify: `PYTHONPATH=./sruth python3 -c "from meaisinfhoghlaim.pipelines.llm_router import CircuitBreaker; print(CircuitBreaker.__module__)"` prints `oideachais.core.utils.circuit_breaker`

## Phase 2: Delete 2 dead pipeline modules

- [ ] `git rm sruth/meaisinfhoghlaim/pipelines/vlm_bridge.py` (119 lines, 0 callers)
- [ ] `git rm sruth/meaisinfhoghlaim/pipelines/resources.py` (21 lines, 0 callers)
- [ ] Verify: `ls sruth/meaisinfhoghlaim/pipelines/` shows 7 files (was 9):
      `__init__.py`, `canuint_audio_slicer.py`, `dialect_classifier.py`,
      `ensemble_gradio.py`, `irish_document_scanner.py`,
      `llm_router.py`, `transcript_aligner.py`
- [ ] Verify: `grep -rn "vlm_bridge\|LlamaSwapResource\|transcribe_curriculums\|BrowserbaseResource\|browserbase_resource" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__`
      returns 0 hits within `sruth/meaisinfhoghlaim/`
      (the unrelated `BrowserbaseResource` references in
      `sruth/croilar/` and `sruth/crypteolas/` are unaffected)

## Phase 3: Update README.md Known issues table

- [ ] In `sruth/meaisinfhoghlaim/README.md`, append 2 new rows to the "Known issues" table (after row 10 from Phase 2):
      - `| 11 | sruth/meaisinfhoghlaim/pipelines/llm_router.py:23 imported `from ..core.utils import CircuitBreaker` (no such module — meaisinfhoghlaim/core/ does not exist). The module was unimportable. Fixed: rewired to the canonical home at sruth/oideachais/core/utils/circuit_breaker.py. | pipelines/llm_router.py:23 | RESOLVED (round 11 audit) |`
      - `| 12 | 2 dead pipeline modules (vlm_bridge.py 119 lines + resources.py 21 lines, 140 lines total). Zero callers in sruth/meaisinfhoghlaim/; both were pre-LiteLLM prototypes and a BrowserbaseResource singleton that was never consumed. Deleted. | pipelines/ | RESOLVED (round 11 audit) |`

## Phase 4: Validate + archive

- [ ] `openspec validate meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules --strict` → PASS
- [ ] Commit + push the 3 file changes (1 modification + 2 deletions) + README update
- [ ] `openspec archive meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules --yes` → auto-applies spec delta
- [ ] Commit + push the auto-applied spec delta
