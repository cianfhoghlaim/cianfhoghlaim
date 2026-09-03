# stale-pipelines-cleanup — Delete dead `sruth/oideachais/pipelines/` package

## Why

The `sruth/oideachais/pipelines/` package (6 files, 94 KB) is dead code that
predates the dagster/dlt migration. Its `__init__.py` (line 1-17)
claims *"Each pipeline integrates DLT, Dagster, Modal, LanceDB Cloud,
Kafka, MLflow"* but no `@dlt.source`, `@asset`, or `@op` decorator
exists anywhere in the package — it is plain Python classes with
mock-quality integration points that were never wired.

**Zero callers anywhere in the repo** (verified by `grep`):

```
grep -r --include="*.py" "oideachais\.pipelines" /Users/cianmacandeisigh/dev/kings_college_galway/
→ 0 hits
```

The class names are also never referenced:

```
grep -r --include="*.py" "IrishDocumentScanner\|AcousticDialectClassifier\|Wav2Vec2DialectClassifier\|LinguisticDialectClassifier\|TranscriptAligner\|WhisperXAligner\|CTCAligner\|DTWAligner" /Users/cianmacandeisigh/dev/kings_college_galway/
→ 0 hits
```

The 4 surviving classes are:
- `pipelines/dialect_classifier.py` (24 KB) — `AcousticDialectClassifier`,
  `Wav2Vec2DialectClassifier`, `LinguisticDialectClassifier` — early
  prototype for what is now in
  `dagster_defs/assets/canuint_alignment_assets.py` (10 assets, working)
- `pipelines/irish_document_scanner.py` (23 KB) — `IrishDocumentScanner`,
  `ScannerConfig`, `ScanResult` — early prototype for what is now in
  `dagster_defs/assets/htr_training_assets.py` (6 assets, working)
- `pipelines/transcript_aligner.py` (21 KB) — `TranscriptAligner`,
  `WhisperXAligner`, `CTCAligner`, `DTWAligner` — prototype that
  duplicates `sruth/meaisinfhoghlaim/audio/` + `dagster_defs/assets/unified_audio_dataset_assets.py`
  (5 assets, working)
- `pipelines/canuint_audio_slicer.py` (14 KB) — audio-slicing logic that
  is simpler than what `canuint_alignment_assets.py` produces
- `pipelines/llm_router.py` (9 KB) — `LLMRouter` that **duplicates**
  `sruth/meaisinfhoghlaim/pipelines/llm_router.py` (which is the canonical
  location per the quadrant layout in `sruth/oideachais/AGENTS.md:28-36`)

**Risk of keeping it:** new contributors will be confused — the
`sruth/oideachais/pipelines/` package appears to be a primary entry point
but has no actual integration. The class names conflict with the
real assets in `dagster_defs/assets/`.

## What

Delete the entire `sruth/oideachais/pipelines/` directory tree:
- `__init__.py` (1.9 KB, 30+ re-exports)
- `dialect_classifier.py` (24 KB)
- `irish_document_scanner.py` (23 KB)
- `transcript_aligner.py` (21 KB)
- `canuint_audio_slicer.py` (14 KB)
- `llm_router.py` (9 KB)
- `README.md` (439 B, generic stub)
- `__pycache__/` (auto-regenerated)

**Salvageable logic that is being lost:**

The 4 surviving files have **no logic worth porting**:
- All 4 are early prototypes whose functionality is already in
  `dagster_defs/assets/canuint_alignment_assets.py`,
  `dagster_defs/assets/htr_training_assets.py`, and
  `dagster_defs/assets/unified_audio_dataset_assets.py` (which are
  working and being called).
- The `llm_router.py` has 0 imports anywhere in the repo;
  `sruth/meaisinfhoghlaim/pipelines/llm_router.py` is the canonical
  location per the quadrant layout.

**If any logic is needed later**, the canonical patterns are:
- Dialect classification → `dagster_defs/assets/canuint_alignment_assets.py:canuint_dialect_summary`
- Irish HTR / document scanning → `dagster_defs/assets/htr_training_assets.py:htr_*
- Audio alignment / transcript alignment → `dagster_defs/assets/canuint_alignment_assets.py:canuint_phoneme_alignments`
- LLM routing → `sruth/meaisinfhoghlaim/pipelines/llm_router.py`

## Impact

### Affected files
- **Deleted:** `sruth/oideachais/pipelines/` (entire tree, ~94 KB, 6 files + 1 README + `__pycache__/`)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that pipeline-level
  Python classes live in `dagster_defs/assets/` (the canonical
  Dagster entry point) or in `sruth/meaisinfhoghlaim/` (the model-layer
  quadrant), not in a top-level `sruth/oideachais/pipelines/` package.

### Backward compatibility
- Zero code references to `oideachais.pipelines` exist (verified
  by `grep`).
- No runtime path or import is affected.
- Anyone who was relying on the misleading `pipelines/` package
  was actually using nothing (zero callers).

## Non-Goals

- No new pipeline code is added. The canonical patterns in
  `dagster_defs/assets/` already cover all use cases.
- No class re-implementation. The 4 surviving classes were early
  prototypes superseded by the dagster_defs/assets/ working code.
- No git history rewrite. The deleted files remain in git history.

## Risk Assessment

- **Risk: someone misses a hidden reference.** Mitigation:
  `grep -r "oideachais.pipelines" --include="*.py"` returns 0 hits
  before deletion. The 4 surviving class names also return 0 hits.
- **Risk: someone wanted to salvage the prototype logic.**
  Mitigation: the canonical implementations are documented above
  and are working. The prototypes were never finished (no `@asset`
  decorators, no Dagster wiring).

## Validation

1. `grep -r "oideachais.pipelines" --include="*.py"` returns 0 hits
2. `grep -r "IrishDocumentScanner\|AcousticDialectClassifier\|..." --include="*.py"` returns 0 hits
3. `ls sruth/oideachais/pipelines/` returns "No such file or directory"
4. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
5. `openspec validate stale-pipelines-cleanup --strict` passes
