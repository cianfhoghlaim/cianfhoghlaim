# meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules

## Why

The meaisínfhoghlaim quadrant has 3 concrete pipeline/audit
findings in `sruth/meaisinfhoghlaim/pipelines/`:

### 1. `llm_router.py:23` — broken import blocks the entire module

The file `sruth/meaisinfhoghlaim/pipelines/llm_router.py:23`
imports:

```python
from ..core.utils import CircuitBreaker
```

But `sruth/meaisinfhoghlaim/core/` does NOT exist (verified by
`ls sruth/meaisinfhoghlaim/core/`). The module is therefore
**unimportable** — direct execution confirms:

```
$ PYTHONPATH=./sruth python3 -c "from meaisinfhoghlaim.pipelines import llm_router; print('OK')"
ModuleNotFoundError: No module named 'meaisinfhoghlaim.core'
```

This is an ACTIVE (non-lazy) import, so the module raises on
load. The 325-line LLM router — which implements the
`LLMCapability` enum + `ModelRouter` class used to select models
by capability tier — is completely unusable until fixed.

The canonical `CircuitBreaker` lives at
`sruth/oideachais/core/utils/circuit_breaker.py:54` (verified
importable: `from oideachais.core.utils import CircuitBreaker` →
returns `<class 'oideachais.core.utils.circuit_breaker.CircuitBreaker'>`).
The `CircuitBreaker` class is used at `llm_router.py:99` (parameter
type hint) and `llm_router.py:102` (constructor default), so the
fix is straightforward.

### 2. `vlm_bridge.py` (119 lines) — dead code, no callers

`sruth/meaisinfhoghlaim/pipelines/vlm_bridge.py` defines
`LlamaSwapResource` (a `ConfigurableResource`) + a
`transcribe_curriculums` function. Zero callers anywhere in the
repo (verified by `grep -rn "vlm_bridge\|LlamaSwapResource\|transcribe_curriculums" sruth/` —
only the definitions appear, no importers). The file is a
prototype from before the VLM call path was routed through
LiteLLM (per `sruth/oideachais/foinse/litellm_config.yaml`).

### 3. `resources.py` (21 lines) — dead code, no callers

`sruth/meaisinfhoghlaim/pipelines/resources.py` defines
`BrowserbaseResource` + a `browserbase_resource` singleton. Zero
callers within `sruth/meaisinfhoghlaim/` (verified). The
`BrowserbaseResource` singleton is referenced by other
`pipelines/resources.py` files in `sruth/croilar/` and
`sruth/crypteolas/` — but those are DIFFERENT files (separate
`resources.py` in separate subtrees), not the meaisínfhoghlaim
one. The meaisínfhoghlaim singleton is orphaned.

**Risk of leaving them in place**:
- The broken `llm_router.py` import means ANY future consumer
  of the LLM router hits `ModuleNotFoundError` immediately
- The 2 dead modules contribute to the "Most sub-packages are
  stubs" known issue (#1 in the README) by inflating the
  pipelines/ subtree size and creating false signals that
  pipeline resources exist

## What changes

1. **Fix the broken import** in
   `sruth/meaisinfhoghlaim/pipelines/llm_router.py:23`:
   change `from ..core.utils import CircuitBreaker` to
   `from sruth.oideachais.core.utils import CircuitBreaker`.
   Add a one-line comment that the canonical home is
   `sruth/oideachais/core/utils/circuit_breaker.py`.

2. **Delete 2 dead pipeline modules**:
   - `git rm sruth/meaisinfhoghlaim/pipelines/vlm_bridge.py`
   - `git rm sruth/meaisinfhoghlaim/pipelines/resources.py`

3. **Add a `meaisinfhoghlaim-platform` spec Requirement** documenting
   the no-broken-imports + no-dead-modules invariants for the
   pipelines subtree.

4. **Update `sruth/meaisinfhoghlaim/README.md`** Known issues table
   with 2 RESOLVED rows (broken import + dead modules).

## Out of scope

- The `pipelines/__init__.py` re-exports (3 main pipelines:
  `dialect_classifier` + `irish_document_scanner` +
  `transcript_aligner`). These are the 3 pipelines referenced
  by the heartbeat assets in `dagster_defs/assets/healthchecks.py`
  (the spec promises "4 heartbeat assets" covering these 3 +
  the `curriculum_agent` heartbeat). KEEP.
- `pipelines/canuint_audio_slicer.py` (463 lines). Imported by
  `sruth/oideachais/dagster_defs/assets/canuint_alignment_assets.py:429`
  via a lazy `from pipelines.canuint_audio_slicer import CanuintAudioSlicer`.
  KEEP — it's the production audio-slicing pipeline.
- `pipelines/ensemble_gradio.py` (128 lines). Used by
  `sruth/meaisinfhoghlaim/tests/test_ensemble_gradio.py:12,29,52,67`
  (4 test call sites). KEEP — has active test consumers.
- The README row #1 known issue ("Most sub-packages are stubs")
  remains open; the 2 dead-module deletions are a step toward
  reducing the stub count but the broader stub-removal work
  (modernising the 4 heartbeats into real Dagster+DLT wrappers)
  is tracked in the `modernize-meaisin-cliste` change (✓ Complete
  per `openspec list`).
- Wiring `llm_router.py` into the heartbeat assets or
  `oideachais/dagster_defs/`. The fix here is just the
  import; future `wire-baml-with-known-consumers` /
  `refactor-dlt-dagster-2026-stack-align` changes will
  integrate it.

## Verification

- `PYTHONPATH=./sruth python3 -c "from meaisinfhoghlaim.pipelines.llm_router import ModelRouter, LLMCapability; print('OK')"`
  succeeds (post-fix)
- `PYTHONPATH=./sruth python3 -c "from meaisinfhoghlaim.pipelines.llm_router import CircuitBreaker; print(CircuitBreaker)"`
  prints the canonical oideachais `CircuitBreaker` class
- `ls sruth/meaisinfhoghlaim/pipelines/` post-fix → 6 files
  (`__init__.py`, `canuint_audio_slicer.py`, `dialect_classifier.py`,
  `ensemble_gradio.py`, `irish_document_scanner.py`,
  `llm_router.py`, `transcript_aligner.py` — wait, that's 7;
  the deletion of vlm_bridge.py + resources.py brings it to 7
  from 9)
- `grep -rn "vlm_bridge\|LlamaSwapResource\|transcribe_curriculums\|BrowserbaseResource\|browserbase_resource" sruth/ --include="*.py" --exclude-dir=.venv --exclude-dir=__pycache__`
  → 0 hits (no callers; the canonical `BrowserbaseResource`
  in `sruth/crypteolas/pipelines/dagster/resources/` is
  unrelated and unaffected)
- `openspec validate meaisinfhoghlaim-audit-phase-3-fix-broken-llm-router-import-and-delete-dead-pipeline-modules --strict` → PASS
