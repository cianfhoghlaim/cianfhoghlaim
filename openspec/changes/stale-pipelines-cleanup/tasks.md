# Tasks: stale-pipelines-cleanup

## Phase 1: Pre-deletion audit

- [x] Confirm no Python code imports from `oideachais.pipelines`
  - `grep -r "oideachais\.pipelines" --include="*.py" /Users/cianmacandeisigh/dev/kings_college_galway/`
  - Result: 0 hits
- [x] Confirm no Python code references the 4 surviving class names
  - `grep -r "IrishDocumentScanner\|AcousticDialectClassifier\|Wav2Vec2DialectClassifier\|LinguisticDialectClassifier\|TranscriptAligner\|WhisperXAligner\|CTCAligner\|DTWAligner" --include="*.py" /Users/cianmacandeisigh/dev/kings_college_galway/`
  - Result: 0 hits
- [x] Confirm `dagster_defs/assets/canuint_alignment_assets.py` and `htr_training_assets.py` exist and are wired
  - `ls /Users/cianmacandeisigh/dev/kings_college_galway/oideachais/dagster_defs/assets/canuint_alignment_assets.py`
  - `ls /Users/cianmacandeisigh/dev/kings_college_galway/oideachais/dagster_defs/assets/htr_training_assets.py`
  - `ls /Users/cianmacandeisigh/dev/kings_college_galway/oideachais/dagster_defs/assets/unified_audio_dataset_assets.py`
  - `ls /Users/cianmacandeisigh/dev/kings_college_galway/meaisinfhoghlaim/pipelines/llm_router.py` (canonical LLM router)
- [x] Confirm `oideachais/pipelines/llm_router.py` is a duplicate of `meaisinfhoghlaim/pipelines/llm_router.py`
  - `find /Users/cianmacandeisigh/dev/kings_college_galway/oideachais -name "llm_router.py" -o -path "*/meaisinfhoghlaim/*llm_router.py"`

## Phase 2: Wholesale directory deletion

- [ ] Delete the entire `oideachais/pipelines/` directory tree
  - `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/oideachais/pipelines/`
  - Removes: __init__.py, dialect_classifier.py, irish_document_scanner.py, transcript_aligner.py, canuint_audio_slicer.py, llm_router.py, README.md, __pycache__/
- [ ] Verify deletion: `ls oideachais/pipelines/` → "No such file or directory"
- [ ] Verify with git: `git status` shows the deletion

## Phase 3: Validation

- [ ] `grep -r "oideachais\.pipelines" --include="*.py"` returns 0 hits
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] `openspec validate stale-pipelines-cleanup --strict` passes
- [ ] `mise turbo lint` passes (or the configured linter)

## Phase 4: Land the plane

- [ ] Stage the deletion: `git add -A oideachais/pipelines/ openspec/changes/stale-pipelines-cleanup/`
- [ ] Commit: `git commit -m "stale-pipelines-cleanup: delete 94 KB dead code package"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
- [ ] `git status` → "up to date with origin"
