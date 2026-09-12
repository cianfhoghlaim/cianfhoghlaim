# Change: pipeline-british-isles-synthesis-v1 (BIEP v3 Ireland LC Pipeline Synthesis)

## Why

Six per-subject openspec changes
(`pipeline-mathematics-v1` through `pipeline-computer-science-v1`)
have shipped the canonical per-subject CocoIndex v1 Apps + BAML
fallback + per-subject pytest harness for the 6 Ireland Leaving
Certificate (LC) subjects. This synthesis change is the canonical
landing page that documents:

1. **What works end-to-end** (verified by passing pytests)
2. **What is blocked by which inert layer** (with the verified defect
   number from the kcg-runtime-inert-layers memory)
3. **What the next session should attack to unblock the rest** (the
   defect remediation order)

## What changes

- **Synthesis report** (this change): documents the per-subject
  status table below.
- **openspec delta to `british-isles-education-pipeline-v3/spec.md`**:
  the new "BIEP v3 Ireland LC M1 per-subject pipeline synthesis"
  Requirement + the "What works / What's blocked" Scenario.

## Inert-layer verification (per the kcg-runtime-inert-layers memory)

The 5 defects documented in the kcg-runtime-inert-layers memory
were verified on 2026-09-12 (the date of this change):

| # | Defect | Status on 2026-09-12 | Evidence |
|---|---|---|---|
| 1 | Local `cocoindex/` package shadow | **FIXED** | `python3 -c "import cocoindex; print(cocoindex.__file__)"` resolves to `/Users/.../cianfhoghlaim/.venv/lib/python3.13/site-packages/cocoindex/__init__.py` (PyPI cocoindex 1.0.20). No local `cocoindex/` dir at repo root. |
| 2 | `orchestration/defs/__init__.py` missing | **FIXED** | `orchestration/defs/__init__.py` exists (774 bytes, with documentation explaining the namespace-package issue). `from orchestration.defs import ...` works. |
| 3 | `baml_client/__init__.py` missing | **EVOLVED** | `baml_client/` directory does NOT exist; `baml-cli generate --from baml_src` FAILS on duplicate class definitions in `baml_src/_shared/templates/` (e.g. `GeminiDeepResearchReport`, `DomainExtractor`). This blocks any code that does `from baml_client.baml_client import b`. The 6 per-subject modules use the Python BAML fallback (regex-based) instead. |
| 4 | `import dlt_sources` replaced `import dlt` in 9 files | **MOSTLY FIXED** | Files have BOTH `import dlt` AND `import dlt_sources`. The `dlt.X` API calls work everywhere; the `import dlt_sources` lines are dead. There's a SEPARATE pre-existing bug in `dlt_sources/api_sources/` (`from _shared.config import` fails because `api_sources/_shared/` doesn't exist) — out of scope for this work. |
| 5 | OCR ensemble hardcoded confidence_score | **PARTIALLY FIXED** | `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:639` still has `confidence_score=0.9 if result else 0.0`, but the VLM calls (line 795-870) now use real `image_url` blocks from `pdf_to_image_bridge`. Hardcoded 0.9 remains. |

## What works / What's blocked (per-subject status table)

| Subject | CocoIndex App | BAML fallback | Pytest | Pipeline end-to-end | Blocked by |
|---|---|---|---|---|---|
| Mathematics | ✅ `cocoindex_flows/british_isles/ireland/education/lc/mathematics.py` | ✅ regex fallback | ✅ 9/9 pass | ✅ load → embed → store → query | none |
| Chemistry | ✅ `.../chemistry.py` | ✅ regex fallback | ✅ 4/4 pass | ✅ load → embed → store → query | none |
| Geography | ✅ `.../geography.py` | ✅ regex fallback | ✅ 4/4 pass | ✅ load → embed → store → query | none |
| English | ✅ `.../english.py` | ✅ regex fallback | ✅ 4/4 pass | ✅ load → embed → store → query | none |
| Gaeilge | ✅ `.../gaeilge.py` | ✅ regex fallback (Irish-language keywords) | ✅ 4/4 pass | ✅ load → embed → store → query | none |
| Computer Science | ✅ `.../computer_science.py` | ✅ regex fallback | ✅ 4/4 pass | ✅ load → embed → store → query | none |

**Total: 29/29 pytests pass.** All 6 per-subject pipelines work
end-to-end against a 3-row fixture (HL/OL/FL snippets) using
in-memory substitutes for LanceDB + BGE-M3 + BAML.

## What is NOT exercised by these pytests (and why)

- **Real LanceDB writes** — the pytests use `InMemoryLanceTable`
  (a list-based substitute). Once a LanceDB instance is reachable
  from the test environment, swap `InMemoryLanceTable` for
  `lancedb.connect_async(...)` and the same test surface continues
  to work.
- **Real BGE-M3 embeddings** — the pytests use `pure_python_embed`
  (a deterministic numpy substitute). Swap for
  `coco.use_context(EMBEDDER).embed(text)` and the real BGE-M3
  model loads.
- **Real BAML extraction** — blocked by defect #3. Swap
  `_python_baml_fallback_extract` for `b.ExtractLCSyllabus<Subject>(text)`
  when `baml_client/` regenerates.
- **Dagster asset materialisation** — out of scope (the per-subject
  Apps are designed to be wired into a Dagster asset by a separate
  British Isles Dagster integration change).
- **Live network tests against MotherDuck / LanceDB namespace /
  Gemma-4 / Qwen3-VL** — these are CI-only and require a real
  GCP/Cloudflare environment.

## Pytest count before/after

| Surface | Before this work | After this work |
|---|---|---|
| `tests/biep_parity_lc/` (the 6 per-subject pytests) | 0 tests | **29 tests, all passing** |
| Total pytests in the cianfhoghlaim repo (excludes `_disabled`) | unchanged | unchanged (this work is additive) |

## Next session: defect remediation order

To unblock the next phase of work (BIEP v3 England A-Level +
England GCSE + the rest), the next session should attack the
defects in this order:

1. **Defect #3 (BAML client generation)** — the root cause is
   duplicate class definitions across
   `baml_src/_shared/templates/` (e.g. `GeminiDeepResearchReport`,
   `DomainExtractor`). The fix is to consolidate the templates
   into the single canonical home (the 18 domain templates per
   the 2026-12-XX-mega-3d-baml-quality-v1 change) and remove the
   duplicate definitions from the per-namespace `.baml` files.
   This unblocks the entire BAML → CocoIndex → LanceDB flow,
   and switches the 6 per-subject pipelines from the regex
   fallback to the real BAML extraction.
2. **Defect #5 (OCR ensemble hardcoded confidence)** — the fix is
   a small change at `ensembled_extractor.py:639` to compute the
   confidence from the actual RAGAS `biiep_extraction_consensus`
   vote instead of the hardcoded `0.9`. Lower priority (doesn't
   block any BIEP v3 cohort).
3. **Defect #4 (`dlt_sources/api_sources/_shared/`)** — separate
   bug; out of scope for this British Isles pipeline work.

## Acceptance gate

This change is complete when:
- All 6 per-subject openspec changes (`pipeline-mathematics-v1`
  through `pipeline-computer-science-v1`) are valid (--strict)
- All 29 pytests in `tests/biep_parity_lc/` pass
- This synthesis change is valid (--strict)
- This synthesis change is committed + pushed
