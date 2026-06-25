# Tasks: consolidate-embedding-batcher

## Phase 1: Pre-deletion audit

- [x] Confirm no Python code imports from `oideachais.embeddings`
  - `grep -r "from oideachais\.embeddings\|import oideachais\.embeddings" --include="*.py" /Users/cianmacandeisigh/dev/kings_college_galway/`
  - Result: 0 hits
- [x] Confirm `oideachais.dlt_utils.batching.EmbeddingBatcher` is the canonical entry point
  - Read `sruth/oideachais/dlt_utils/__init__.py:13-21` (re-exports `EmbeddingBatcher`)
  - Read `sruth/oideachais/dagster_defs/resources.py` (uses `oideachais.dlt_utils.batching` patterns)
- [x] Confirm `sruth/oideachais/modal_finetune/embed_batch.py` is a Modal worker, not a duplicate
  - Read first 100 lines: `@app.cls(gpu="T4", timeout=3600)` Modal app definition
  - Decision: KEEP — different layer (serverless GPU vs local Python)
- [x] Confirm `sruth/croilar/_shared/embeddings/batcher.py` is croilar quadrant-local
  - Read `sruth/croilar/AGENTS.md:8-10` (`_shared` namespace is croilar-local)
  - Decision: KEEP — separate quadrant

## Phase 2: Wholesale directory deletion

- [ ] Delete the entire `sruth/oideachais/embeddings/` directory tree
  - `rm -rf /Users/cianmacandeisigh/dev/kings_college_galway/sruth/oideachais/embeddings/`
  - Removes: __init__.py, batcher.py, service.py, README.md, __pycache__/
- [ ] Verify deletion: `ls sruth/oideachais/embeddings/` → "No such file or directory"
- [ ] Verify with git: `git status` shows the deletion

## Phase 3: Documentation pointer

- [ ] Update `sruth/oideachais/dlt_utils/README.md` to add a 1-paragraph note
  - "The canonical EmbeddingBatcher lives in `oideachais.dlt_utils.batching` and is re-exported via `oideachais.dlt_utils.__init__`. The legacy `sruth/oideachais/embeddings/` package has been removed; use `oideachais.dlt_utils` instead."

## Phase 4: Validation

- [ ] `grep -r "oideachais\.embeddings" --include="*.py"` returns 0 hits
- [ ] `uv run --package oideachais python -c "from oideachais.dlt_utils import EmbeddingBatcher; print(EmbeddingdingBatcher)"` works
- [ ] `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
- [ ] `openspec validate consolidate-embedding-batcher --strict` passes

## Phase 5: Land the plane

- [ ] Stage the deletion: `git add -A sruth/oideachais/embeddings/ openspec/changes/consolidate-embedding-batcher/`
- [ ] Commit: `git commit -m "consolidate-embedding-batcher: delete dead sruth/oideachais/embeddings/ package"`
- [ ] `git pull --rebase`
- [ ] `git push origin q3-2026-oideachais-consolidation`
- [ ] `git status` → "up to date with origin"
