# consolidate-embedding-batcher — Delete redundant `sruth/oideachais/embeddings/` package

## Why

The oideachais quadrant has **3 competing implementations** of an
`EmbeddingBatcher` class plus a 4th `EmbeddingService` class. The
canonical implementation (`sruth/oideachais/dlt_utils/batching.py:EmbeddingBatcher`,
re-exported via `sruth/oideachais/dlt_utils/__init__.py:16`) is the only
one that should be used. The other 3 are redundant:

| Location | Classes | Status | Reason |
|---|---|---|---|
| `sruth/oideachais/dlt_utils/batching.py` | `EmbeddingBatcher`, `batch_embeddings`, `batch_items`, `should_drop_hnsw`, `calculate_optimal_batch_size` | **CANONICAL** | Re-exported via `dlt_utils/__init__.py:16`; provides 7 utility functions; the only one intended for production use |
| `sruth/oideachais/embeddings/batcher.py` | `EmbeddingBatcher`, `batch_embed` | Dead code | 0 callers; same class name, simpler API, never imported |
| `sruth/oideachais/embeddings/service.py` | `EmbeddingService`, `OpenAIEmbeddings`, `CohereEmbeddings`, `SentenceTransformersEmbeddings`, `OllamaEmbeddings` | Dead code | 0 callers; multi-provider wrapper that was superseded by `dagster_defs/resources.py:LanceDBResource` and `sruth/meaisinfhoghlaim/` agent-layer code |
| `sruth/oideachais/modal_finetune/embed_batch.py` | `EmbeddingService` (Modal `@app.cls` worker) | **KEEP** | Not a duplicate — this is a Modal GPU worker (serverless), not a local Python utility. Different layer. |
| `sruth/croilar/_shared/embeddings/batcher.py` | `EmbeddingBatcher` | **KEEP** | Separate quadrant (croilar). The `_shared` namespace is croilar-local per `sruth/croilar/AGENTS.md:8-10`. |

**Zero callers anywhere in the repo** (verified by `grep`):

```
grep -r "from oideachais.embeddings" --include="*.py" /Users/cianmacandeisigh/dev/kings_college_galway/
→ 0 hits
```

The `sruth/oideachais/embeddings/` package was the early prototype for
what is now in `dlt_utils/batching.py`. The `EmbeddingService` class
in `embeddings/service.py` was a multi-provider wrapper that was
superseded by:

- `dagster_defs/resources.py:LanceDBResource` (the canonical
  embedding resource for the Dagster code-location)
- `sruth/meaisinfhoghlaim/` agent-layer code (the model-layer
  embedding integration)

**Risk of keeping it:** new contributors will be confused — the
`sruth/oideachais/embeddings/` package is shadowed by `dlt_utils/batching.py`
but has a more discoverable name. The `EmbeddingBatcher` class
name collision is a footgun.

## What

1. **Delete the entire `sruth/oideachais/embeddings/` directory tree:**
   - `__init__.py` (1 KB, 11 re-exports)
   - `batcher.py` (4.7 KB, `EmbeddingBatcher` + `batch_embed`)
   - `service.py` (11.6 KB, 4 backends + `EMBEDDING_MODELS` registry + `EmbeddingService` + 2 convenience functions)
   - `README.md` (439 B, generic stub)
   - `__pycache__/` (auto-regenerated)

2. **Keep these intact (they are NOT duplicates):**
   - `sruth/oideachais/dlt_utils/batching.py:EmbeddingBatcher` — the canonical local-Python batcher
   - `sruth/oideachais/modal_finetune/embed_batch.py:EmbeddingService` — the Modal GPU worker (different layer)
   - `sruth/croilar/_shared/embeddings/batcher.py:EmbeddingBatcher` — croilar quadrant-local

3. **Add a deprecation pointer** in `sruth/oideachais/embeddings/README.md`'s
   replacement location (`sruth/oideachais/dlt_utils/README.md`) confirming
   that `EmbeddingBatcher` is the canonical entry point.

## Impact

### Affected files
- **Deleted:** `sruth/oideachais/embeddings/` (entire tree, ~16 KB, 3 files + 1 README + `__pycache__/`)
- **Modified:** `sruth/oideachais/dlt_utils/README.md` (add a 1-paragraph note that `EmbeddingBatcher` is the canonical entry point and `sruth/oideachais/embeddings/` is gone)

### Affected specs
- MODIFIED `oideachais-pipeline` — the rule that the canonical
  `EmbeddingBatcher` lives in `oideachais.dlt_utils.batching`, not
  in `oideachais.embeddings`. The new rule explicitly forbids a
  top-level `sruth/oideachais/embeddings/` package.

### Backward compatibility
- Zero code references to `oideachais.embeddings` exist (verified
  by `grep`).
- The canonical `oideachais.dlt_utils.batching.EmbeddingBatcher` is
  already re-exported via `oideachais.dlt_utils.__init__.py:16`, so
  anyone who was using the old name was actually using nothing
  (zero callers).
- No runtime path or import is affected.

## Non-Goals

- No new batching code is added. The canonical `dlt_utils/batching.py`
  already covers all use cases.
- No merge of `sruth/croilar/_shared/embeddings/batcher.py` — that is a
  separate quadrant with its own conventions.
- No changes to `sruth/oideachais/modal_finetune/embed_batch.py` — that
  is a Modal GPU worker, not a duplicate.

## Risk Assessment

- **Risk: someone misses a hidden reference.** Mitigation:
  `grep -r "oideachais.embeddings" --include="*.py"` returns 0 hits
  before deletion.
- **Risk: someone wanted to use the multi-provider `EmbeddingService`.**
  Mitigation: the canonical multi-provider integration is
  `dagster_defs/resources.py:LanceDBResource` (re-exported via
  `dlt_utils/__init__.py:24-28` and wired to `oideachais.dlt_utils.batching.EmbeddingBatcher`).

## Validation

1. `grep -r "oideachais\.embeddings" --include="*.py"` returns 0 hits
2. `ls sruth/oideachais/embeddings/` returns "No such file or directory"
3. `uv run --package oideachais python -c "from oideachais.dlt_utils import EmbeddingBatcher; print(EmbeddingBatcher)"` works
4. `uv run --package oideachais python -c "import dagster_defs.definitions"` still loads
5. `openspec validate consolidate-embedding-batcher --strict` passes
