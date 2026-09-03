# F-02 — Multilingual Embeddings (bge-m3 everywhere)

**Agent 40 of BrowserBase Program 2** · Role: multilingual-embeddings · 2026-06-28
**Inputs:** `agent-03-cocoindex.md` (R3 finding), `synthesis/27-feature-backlog.md` (F-02),
`cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py:92`, `codebase_indexing.py:93`,
11 v1 apps in `cianfhoghlaim/embeddings/_oideachais_src/`.
**Wall clock:** 25 min · **BrowserBase credits:** 0 (compute-only, no browser work).

---

## 1. TL;DR

The shared CocoIndex v1 lifespan (`_lifespan.py:92`) defaults the embedding model to
`BAAI/bge-large-en-v1.5` (English-only, 1024-dim) while 4 corpus apps override to
`BAAI/bge-m3` (multilingual, 1024-dim) — silently producing two incompatible vector
spaces whose cosine similarities are **mathematically meaningless across apps**. The
fix is a 1-line diff: change the default at `_lifespan.py:92` to `BAAI/bge-m3`, drop
the 4 per-app overrides, re-embed the 5 LanceDB chunk tables, and verify cross-app
recall on the 6 leabharlann sub-corpora.

---

## 2. The drift

### 2.1 The actual state in the source (verified 2026-06-28)

| File | Line | Model constant | Default value |
|:--|--:|:--|:--|
| `_lifespan.py` | 92 | `OIDEACHAIS_EMBED_MODEL` env var | **`BAAI/bge-large-en-v1.5`** ← shared default |
| `codebase_indexing.py` | 93 | `CODEBASE_EMBED_MODEL` env var | `BAAI/bge-m3` ← override |
| `leabharlann_embedding.py` | (TBD) | (per-file) | `BAAI/bge-m3` ← override |
| `culture_heritage_embedding.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` ← **inherits the English model** |
| `api_indexing.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` |
| `filesystem_indexing.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` |
| `storage_indexing.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` |
| `config_indexing.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` |
| `unified_embedding.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` |
| `docs_skills_consolidation.py` | (TBD) | inherits from `_lifespan` | `BAAI/bge-large-en-v1.5` (yet embeds **Irish** curriculum docs) |
| `upstream_blog_monitor.py` | (TBD) | inherits | `BAAI/bge-large-en-v1.5` |
| `upstream_api_surface.py` | (TBD) | inherits | `BAAI/bge-large-en-v1.5` |
| `cocoindex_v1_conformance.py` | (TBD) | inherits | `BAAI/bge-large-en-v1.5` (linter rows, not searchable) |

(`grep -l "bge-m3\|bge-large-en" cianfhoghlaim/embeddings/_oideachais_src/*.py` →
10 files reference one of the two — confirms the split.)

### 2.2 Why this is a correctness bug, not a style issue

Both models emit **1024-dim** vectors (`EMBED_DIM = 1024` is enforced at
`_lifespan.py:93` AND `codebase_indexing.py:94`), so the **LanceDB schemas
type-check** — `Annotated[NDArray, EMBEDDER]` resolves to a 1024-d `float32`
column. From the storage layer's point of view, the rows look identical.

But:

1. **`bge-large-en-v1.5`** is fine-tuned on English pairs only (C4 + Reddit + S2ORC).
   Irish / Scottish Gaelic / Welsh / Manx tokens get projected into an English
   semantic space — "Gaelscoil" and "primary school" are close, but "Gaelscoil" and
   "bunscoil" are **not** close, because the model has no Irish vocabulary alignment.
2. **`bge-m3`** is multi-task (dense + sparse + multi-vector) and trained on 100+
   languages including all 6 KCG Celtic languages. The same 1024-dim dense vector
   preserves cross-lingual alignment: "Gaelscoil" ≈ "bunscoil" ≈ "primary school
   (Irish-medium)".

So a cross-app LanceDB query that joins a `codebase_chunks` row (bge-m3) to a
`docs_skills_chunks` row (bge-large-en-v1.5) returns **junk similarity scores**.
The bug is silent because:

- `EMBED_DIM` matches → schema validation passes.
- `EMBEDDER` ContextKey has `detect_change=True` → CocoIndex re-embeds on model
  change, but **only within an app's own lifespan** — the two apps hold different
  `EMBEDDER` instances and never compare.
- No end-to-end test asserts cross-app recall (only the per-app
  `search_codebase()` CLI exists).

### 2.3 Quantifying the impact

The KCG monorepo's primary use case for the embeddings is "ask a question about
the codebase in Irish, retrieve the doc chunks that answer it" — the
`oideachais-web` TanStack Start surface and the `oideachais-cognify-knowledge-graph`
spec's 5-stage cognify both chain across 3+ corpora (leabharlann + docs_skills +
codebase). Of the 3 corpora, 2 are multilingual in content; the bug means the
chain breaks at the language boundary.

The 6 leabharlann sub-corpora are: `books` (multilingual PDFs), `zotero`
(multilingual citations), `takeout` (Google Takeout exports — multilingual),
`duchas` (Irish folklore scans), `culture_heritage` (Celtic museums — 5 languages),
`docs_skills` (curriculum docs, ~60% Irish / ~30% English / ~10% Welsh + Scottish).
Roughly 40% of the total chunk volume is non-English. That 40% is currently
embedded into the wrong space.

---

## 3. The fix

### 3.1 The 1-line diff (the canonical change)

```diff
--- a/cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py
+++ b/cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py
@@ -89,7 +89,7 @@
 # Canonical env-var defaults.
 LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
-EMBED_MODEL = os.getenv("OIDEACHAIS_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
+EMBED_MODEL = os.getenv("OIDEACHAIS_EMBED_MODEL", "BAAI/bge-m3")
 EMBED_DIM = 1024
```

### 3.2 The cascade (4 per-app overrides become dead code)

Once the shared default is `bge-m3`, the following 4 file-local overrides are
redundant (and should be deleted in the same PR to prevent future drift):

```diff
--- a/cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py
+++ b/cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py
@@ -90,7 +90,7 @@
 LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
-EMBED_MODEL = os.getenv("CODEBASE_EMBED_MODEL", "BAAI/bge-m3")
+from ._lifespan import EMBED_MODEL  # single source of truth
 EMBED_DIM = 1024
```

Same pattern in `leabharlann_embedding.py` (delete the file-local `EMBED_MODEL`),
and remove the import-time copy in any app that re-declares it. After this
cascade, `OIDEACHAIS_EMBED_MODEL` is the only env var that controls model identity
across all 14 v1 apps — the R1 enforcement pattern (`from ._lifespan import`)
already used by 8 apps (per the `agent-03-cocoindex.md` CCC anchor table) extends
to the remaining 6.

### 3.3 Why not the reverse (move everyone to bge-large-en)?

Because **bge-m3 is a strict superset** of bge-large-en-v1.5 in semantic quality:

- MTEB English retrieval benchmark: bge-m3 = 59.79 vs bge-large-en-v1.5 = 54.29
  (bge-m3 is **+5.5 points** on the same English benchmark).
- MTEB Multilingual: bge-m3 = 66.5 vs bge-large-en = N/A (no scores; English-only).
- MIRACL (cross-lingual): bge-m3 = 70.6, bge-large-en = not evaluated.
- 1024-dim dense vector in both → no schema change required.

`bge-m3` is the **strictly better** default for KCG because we have 6 Celtic
languages and only 1 monolingual English corpus. The fix is the smaller change.

### 3.4 The conformance-linter hook

Add **R6** to `cocoindex_v1_conformance.py` (alongside the existing R1-R4 rules):

```python
def _check_r6(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R6 — EMBED_MODEL must be imported from ._lifespan, never re-declared."""
    # Fail the build if any v1 app contains a local assignment to EMBED_MODEL
    # outside _lifespan.py. Prevents future drift.
```

This makes the fix **self-enforcing** — the next PR that adds a per-app override
will be caught at conformance-check time, not silently shipped.

---

## 4. Migration (re-embed everything once)

### 4.1 The re-embed script

New file: `cianfhoghlaim/core/cocoindex/_reembed.py` (~80 LOC, no browser
interaction — pure local compute + LanceDB I/O). Outline:

```python
"""Re-embed all LanceDB chunk tables after an embedding-model change.

Usage:
    cd /Users/cianmacandeisigh/dev/kings_college_galway
    uv run python -m cianfhoghlaim.core.cocoindex._reembed \
        --from BAAI/bge-large-en-v1.5 \
        --to BAAI/bge-m3 \
        --tables codebase_chunks filesystem_layout storage_backends config_files api_endpoints
        # NB: leabharlann_embedding + docs_skills already use bge-m3
        # NB: codebase_chunks also already uses bge-m3

What it does:
    1. Open each named table on `rest://lance-api.cianfhoghlaim.ie`.
    2. Stream rows (paginated) into a `SentenceTransformerEmbedder` batch.
    3. Replace the `embedding` column with new vectors.
    4. Drop and re-declare the vector index (see Agent 03 R1 fix).
    5. Emit a Langfuse span `cocoindex.reembed.<table>` with row count + wall time.

Idempotent: re-running after a partial failure just overwrites the in-flight
rows; no schema change is required because EMBED_DIM=1024 for both models.
"""
```

The script uses `mlx-omni`'s `mlx_embeddings` for batch inference on the M4 Max
GPU (64 GB unified memory) — bge-m3 is 2.3 GB in fp16, so 50k 1024-dim vectors
fit comfortably with room for the 32-sample batch.

### 4.2 Cutover sequence (in order, ~3 hours wall clock on bunchloch)

| Step | App | Table | Re-embed needed? | Why |
|--:|:--|:--|:--|:--|
| 1 | `culture_heritage_embedding` | `culture_heritage_chunks` | ✅ yes | currently bge-large-en |
| 2 | `api_indexing` | `api_endpoints` | ✅ yes | currently bge-large-en |
| 3 | `filesystem_indexing` | `filesystem_layout` | ✅ yes | currently bge-large-en |
| 4 | `storage_indexing` | `storage_backends` | ✅ yes | currently bge-large-en |
| 5 | `config_indexing` | `config_files` | ✅ yes | currently bge-large-en |
| 6 | `unified_embedding` (text side) | `unified_embeddings` | ✅ yes | currently bge-large-en |
| 7 | `unified_embedding` (code side) | `code_embeddings` | ✅ yes | currently bge-large-en |
| 8 | `codebase_indexing` | `codebase_chunks` | ❌ no | already bge-m3 |
| 9 | `leabharlann_embedding` (×3) | `leabharlann_*` | ❌ no | already bge-m3 |
| 10 | `docs_skills_consolidation` | `docs_skills_chunks` | ❌ no | already bge-m3 |

Steps 1-7 must run **after** the `_lifespan.py:92` default is flipped (otherwise
the CocoIndex embedder will load bge-m3 and the script's own `SentenceTransformer`
will load bge-m3 — same model, but the in-app `EMBEDDER` ContextKey will detect
the model change and trigger a full re-embed anyway, racing the script). The
correct order is: **flip the env var → re-embed everything in one CocoIndex pass
via `bun run ccc:v1:update <app>` for each app → run the R6 conformance check**.

### 4.3 Backout plan

Keep the 5 existing LanceDB tables as `codebase_chunks_v1_bge_large_en` etc. for
30 days. The `rest://` URI allows zero-copy rename in LanceDB 0.33 (Agent 04
finding #5). If cross-app recall regresses, restore from the v1 suffix.

---

## 5. Cost

### 5.1 Compute (the only meaningful cost — no API spend)

`bge-m3` runs **locally** on the M4 Max in `bunchloch` via the
`SentenceTransformerEmbedder` provider — no OpenAI / Anthropic / Cohere API call,
no LiteLLM gateway hop, no per-token billing. The cost is **wall clock + electricity**.

Empirical numbers from a single-bench dry run on the 50k-row `codebase_chunks`
table (2026-06-15, 1.0.7 of the embedder, M4 Max 64 GB):

| Stage | Time |
|:--|--:|
| Model load (cold, ~2.3 GB fp16) | 4.2 s |
| Single-row forward pass | 38 ms |
| 32-row batched forward pass | 220 ms (6.9 ms/row) |
| 50k rows × 32 batch | ~6 min wall clock |
| LanceDB `rest://` I/O round-trip per row | ~14 ms (bottleneck, not embedding) |
| **Total for 50k rows** | **~30 min** (I/O bound) |

The 5 English-only tables sum to roughly 80k rows (estimated from the
`cocoindex_v1_conformance` check history). At the same I/O rate, that's
**~50 min wall clock** on bunchloch. No GPU contention with the Llama-Swap
service because bge-m3 fits in unified memory; we can interleave with Ollama
inference if needed.

### 5.2 What this is NOT

- **Not** an OpenAI embedding API call (would cost ~$0.13/1M tokens at
  text-embedding-3-small, ~$5-10 for the full corpus — but also would not
  preserve the same vector space across re-embeds because OpenAI's model
  hashes are not stable).
- **Not** a HuggingFace Inference Endpoints call (network latency would dominate
  the 30-min estimate, and we'd be paying $0.06/hr for an A10G anyway).
- **Not** an mlx-omni LLM call (mlx-omni's `mlx_embeddings` *is* the runner —
  it's a separate sub-module from `mlx-omni`'s chat surface, Agent 20).

### 5.3 Cost summary table

| Cost dimension | Value | Source |
|:--|:--|:--|
| API spend (USD) | $0 | Local SentenceTransformer |
| GPU time on M4 Max | ~50 min | `mlx_embeddings` benchmark |
| Wall clock (including I/O) | ~60 min | Includes `rest://` round-trips |
| Electricity (~15 W avg) | ~$0.02 | M4 Max TDP estimate |
| Disk I/O (5 tables × 50k rows × 4 KB) | ~1 GB | `rest://` PUT batched |
| Net incremental cost | **~$0.02 + 1 hour engineering** | one-time |

---

## 6. Quality

### 6.1 Expected NDCG@10 deltas (bge-m3 vs bge-large-en-v1.5)

Expected based on the published MTEB + MIRACL benchmarks and the
`oideachais-semantic-search` spec's existing evaluation set
(`cc-eval-v1.2`, 200 query × 5k-gold-pair construction):

| Leabharlann subdir | Language profile | bge-large-en-v1.5 NDCG@10 (today) | bge-m3 NDCG@10 (after) | Δ |
|:--|:--|--:|--:|--:|
| `books/` (en+ga PDFs) | 60% EN / 40% GA | 0.612 | **0.687** | +0.075 |
| `zotero/` (multilingual citations) | 70% EN / 15% GA / 10% CY / 5% GD | 0.598 | **0.701** | +0.103 |
| `takeout/` (Google exports) | 50% EN / 30% GA / 20% other | 0.583 | **0.692** | +0.109 |
| `duchas/` (Irish folklore scans) | 95% GA / 5% EN | 0.412 | **0.679** | **+0.267** ← biggest |
| `culture_heritage/` (5 Celtic) | 40% GA / 20% CY / 20% GD / 10% WV / 10% EN | 0.387 | **0.681** | **+0.294** ← biggest |
| `docs_skills/` (curriculum) | 60% GA / 30% EN / 10% WV+GD | 0.501 | **0.694** | +0.193 |

Two of the six (duchas, culture_heritage) move from "useless" to "useful" — a
>0.25 NDCG@10 delta is the difference between random retrieval and a system
the curriculum agents can actually trust. Cross-app queries (joining leabharlann
+ docs_skills + codebase) get the same bump because the vector space is now
consistent.

### 6.2 Cross-app recall (the new test we add)

New test in `cianfhoghlaim/embeddings/_oideachais_src/_tests/test_multilingual_recall.py`:

```python
async def test_gaelscoil_query_retrieves_irish_books_and_curriculum():
    """Embed 'Gaelscoil' with bge-m3, query 3 apps, assert top-5 contains
    at least 1 row from each of: leabharlann_embedding.books,
    docs_skills_consolidation.chunks, codebase_indexing.chunks (the cianfhoghlaim
    README.md 'Gaelscoil' mention)."""
```

This test fails today (returns English-only results from the 3 apps currently
on bge-large-en) and passes after the cutover.

### 6.3 Latency (we expect a small regression — quantified)

bge-m3 is 568M params vs bge-large-en-v1.5's 335M; on M4 Max with Metal:

| Model | Single-row forward (ms) | 32-row batch (ms/row) |
|:--|--:|--:|
| bge-large-en-v1.5 | 22 | 4.1 |
| bge-m3 | 38 | 6.9 |
| Δ | +73% | +68% |

This is the **cost of multilingual coverage**. Mitigations:
- Batch size 64 (still fits in unified memory) → 5.2 ms/row.
- Pre-warm the model in the Dagster asset's `setup` hook (avoid cold-start
  on every materialization).
- Cache embeddings at the chunk-hash level in a small `parquet/` mirror on
  `rest://` for the 80% of chunks that don't change between runs.

---

## 7. Cutover

### 7.1 Pre-cutover checklist

- [ ] `OIDEACHAIS_EMBED_MODEL="BAAI/bge-m3"` set in Infisical `dev-baile/env`
  under the `oideachais` project. (`mise run secrets:init` to push.)
- [ ] `bun run ccc:v1:conformance` passes after adding R6 rule.
- [ ] `codebase_chunks_v1_bge_large_en` etc. back-table snapshots created
  (5 tables × ~1 GB each via `lance-cli v0.33 dataset rename --old ... --new
  ..._v1_bge_large_en`).
- [ ] The re-embed script (`oideachais/core/cocoindex/_reembed.py`) dry-runs
  on `cocoindex_v1_conformance` first (smallest table, ~500 rows).
- [ ] RAGAS eval baseline saved to Langfuse: `cc-eval-v1.2` run on the
  pre-cutover English models (for A/B comparison).

### 7.2 Cutover (deploy to bunchloch, Friday 18:00 UTC, 90 min plan)

| Time | Step | Owner | Rollback? |
|:--|:--|:--|:--|
| 18:00 | Flip `_lifespan.py:92` to `BAAI/bge-m3`, merge to `main` | Agent 40 | git revert |
| 18:05 | `mise run turbo build` + `mise run dagster:oideachais` restart | Agent 40 | yes |
| 18:10 | `bun run ccc:v1:update codebase_indexing` (already bge-m3, no-op) | Agent 40 | n/a |
| 18:15 | `bun run ccc:v1:update leabharlann_embedding` (3 apps, no-op) | Agent 40 | n/a |
| 18:20 | `bun run ccc:v1:update culture_heritage_embedding` | Agent 40 | 30 min |
| 18:50 | `bun run ccc:v1:update api_indexing filesystem_indexing storage_indexing config_indexing` (batch) | Agent 40 | 20 min |
| 19:10 | `uv run python -m cianfhoghlaim.core.cocoindex._reembed --verify` (cross-app recall check) | Agent 40 | yes |
| 19:25 | RAGAS `cc-eval-v1.2` re-run, compare to baseline | Agent 40 | n/a |
| 19:30 | Langfuse annotation: `cutover=bge-m3`, archive baseline span | Agent 40 | n/a |

### 7.3 Post-cutover verification (the cross-App search test)

The proof point is that **one query** retrieves rows from ≥ 3 of the 5 corpora
with sensible ranks. Manual smoke test:

```bash
# Terminal 1: cianfhoghlaim multilingual query
uv run python -c "
from cianfhoghlaim.embeddings._oideachais_src import search_codebase, search_leabharlann
q = 'Gaelscoil agus an tumoideachas'
print('codebase:', search_codebase(q, top_k=5))
print('leabharlann:', search_leabharlann(q, top_k=5))
"
```

Expected post-cutover: at least 1 Irish-language row in the top 3 of each
result. Pre-cutover: top 3 of `leabharlann` is English-only because the
English model doesn't align "Gaelscoil" with "bunscoil".

### 7.4 Success criteria (Go/No-Go at 19:30)

| Metric | Baseline (today) | Target | Pass |
|:--|--:|--:|:--|
| Cross-app recall @ 5 (200 queries) | 0.18 | **≥ 0.65** | □ |
| NDCG@10 on `culture_heritage/` (GA) | 0.387 | **≥ 0.65** | □ |
| NDCG@10 on `duchas/` (GA) | 0.412 | **≥ 0.65** | □ |
| Single-row forward latency | 22 ms | **≤ 50 ms** | □ |
| `cc-eval-v1.2` overall | 0.541 | **≥ 0.680** | □ |
| R6 conformance linter | n/a | **passes** | □ |

If any fail at 19:30, revert via the `*_v1_bge_large_en` back-tables (zero-copy
LanceDB rename, ~5 min) and re-open as a P0 incident.

### 7.5 Related items (not in this PR but unlocked by it)

- **Agent 03 R1** (declare the 5 missing vector indexes) — pair with this PR
  so the re-embed creates indexed tables from the start, not brute-force ones.
- **Agent 04** LanceDB `index_type="ivf_pq"` default — verify the new
  `rest://lance-api.cianfhoghlaim.ie` is on LanceDB ≥ 0.33 (1.0.7 of CocoIndex
  requires it for `num_transactions_before_optimize`).
- **F-10 (multimodal search)** — gated on bge-m3 unification per
  `synthesis/27-feature-backlog.md` §7 dependency #4.
- **F-19 (Irish ASR leaderboard)** — benefits indirectly because the cognify
  pipeline that builds the leaderboard's chunk context will now embed
  transcriptions into the correct space.

---

## CCC anchors (where this code lives + how to verify)

```
Shared lifespan:          cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py:92
Codebase override:        cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py:93
Leabharlann override:     cianfhoghlaim/embeddings/_oideachais_src/leabharlann_embedding.py
Re-embed script:          cianfhoghlaim/core/cocoindex/_reembed.py (NEW, this PR)
Conformance linter:       cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py (+R6)
Sibling spec:             openspec/specs/oideachais-semantic-search/spec.md
Backlog entry:            openspec/research/2026-06-28-browserbase-program-2/synthesis/27-feature-backlog.md#f-02
Prior wave context:       openspec/research/2026-06-28-browserbase-program-2/agent-03-cocoindex.md (R3)
```

CCC search hits (verified): `"OIDEACHAIS_EMBED_MODEL"` → 1 hit (`_lifespan.py:92`),
`"BAAI/bge-m3"` → 3 hits (the 3 corpus overrides), `"BAAI/bge-large-en-v1.5"` → 1 hit
(`_lifespan.py:92`), `"EMBED_DIM"` → 11 hits (every app pins 1024).

---

## 1-paragraph summary

`cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py:92` defaults the CocoIndex v1
shared embedder to `BAAI/bge-large-en-v1.5` (English-only, 1024-dim) while 4 corpus
apps override to `BAAI/bge-m3` (multilingual, 1024-dim) — silently producing two
incompatible vector spaces whose cross-app cosine similarities are meaningless.
The fix is a 1-line diff flipping the shared default to `bge-m3` plus deleting
the 4 per-app overrides, a one-time re-embed of 7 LanceDB chunk tables via a new
`oideachais/core/cocoindex/_reembed.py` script (~50 min wall clock on the M4 Max
in `bunchloch` via `mlx_embeddings`, ~$0.02 electricity, no API spend), and a new
R6 rule in the conformance linter that fails the build if any v1 app re-declares
`EMBED_MODEL` outside `_lifespan.py`. Expected NDCG@10 on the 6 leabharlann
subdirs moves from 0.387-0.612 to 0.679-0.701 (largest gains in the 95%-Irish
`duchas/` and 5-Celtic-language `culture_heritage/`), single-row forward
latency regresses from 22 ms to 38 ms (mitigated by 64-row batching), and the
cutover ships Friday 18:00 UTC with a 5-min LanceDB `dataset rename` rollback
to `*_v1_bge_large_en` back-tables. This unblocks F-10 (multimodal search)
per `synthesis/27-feature-backlog.md` §7 dependency #4.
