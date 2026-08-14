# 2026-08-13-skill-consolidation-and-extension-v1

## Why

After the 2026-08-15 `centralized-model-registry` trilogy and the
v7 flattening, three gaps remain in the agent/skill surface:

1. **OCR/VLM pipeline has no canonical skill entrypoint.** The
   22-entry `VISION_MODELS` (subset view of the 70-entry
   `MODEL_REGISTRY` `ocr_vision` family) + the 6
   `CLASSICAL_OCR` backends + the BIEP v2 4-path ensemble
   (`EnsembledExtractor`: baml + unstract + qwen3_vl + gemma4) +
   the 7 PDF converters in `meaisinfhoghlaim/document_factory/` +
   the 4 alignment methods in `meaisinfhoghlaim/alignment/` +
   the Irish HTR dataset + the M4-Max dispatch helper + the
   BAML `clients_ocr_ensemble.baml` patterns all live under
   `meaisinfhoghlaim/` — but the only always-on skill that touches
   them is `centralized-registry` at the family level. Agents
   working on OCR/VLM extraction have to discover the surface via
   `ccc search`.

2. **No single router for the data platform surface.** The 5
   canonical per-area docs (`dlt_sources/AGENTS.md`,
   `baml_src/AGENTS.md`, `cocoindex/AGENTS.md`,
   `orchestration/AGENTS.md`, `meaisinfhoghlaim/README.md`)
   each document one slice. There is no "data engineering at
   Cianfhoghlaim" entrypoint — new agents have to discover
   the surface via search. The historical
   `data-engineering-pipeline-documentation` skill (which
   referenced `sruth/cianfhoghlaim/STATUS.md`) was archived to
   `.agents/skills_backup/` during the 2026-07-06 cleanup and
   never replaced.

3. **The `ccc` CLI vs `codebase_indexing` v1 App split is
   unclear.** The `ccc` skill carries a "DEPRECATION NOTICE"
   banner; the v1 App at `cocoindex/codebase_indexing.py` has
   no skill of its own; `INDEXING_AND_COGNITION.md` §3 mentions
   both but does not resolve which to use when.

This change ships the minimal set of extensions + 1 new
co-located router doc that closes all 3 gaps without inflating
the skill count.

## What Changes

### A. Extend `centralized-registry` skill with §11 OCR/VLM Pipeline

**MODIFIED** `.agents/skills/centralized-registry/SKILL.md` —
add `## 11. OCR/VLM Pipeline` section after the existing
`## 10. The 6 follow-up issues`. Covers:

- The 22-entry `VISION_MODELS` (`ocr_vision` family subset view
  of `MODEL_REGISTRY`)
- The 6 `CLASSICAL_OCR` backends in
  `meaisinfhoghlaim/models/registry.py:CLASSICAL_OCR`
- The BIEP v2 4-path ensemble (`EnsembledExtractor` —
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`)
- The 5 PDF converters in
  `meaisinfhoghlaim/document_factory/converters/`
  (`docling`, `marker`, `unstructured`, `deepseekocr`,
  `pymupdf4llm`) + the `curriculum_document` + the `pdf_factory`
  orchestrator
- The 4 alignment methods in
  `meaisinfhoghlaim/alignment/aligner.py` (`VecAlign`,
  `HunAlign`, `GaoisAlign`, `Hybrid`) + the `ColPaliAligner`
  (manuscript bbox extraction)
- The Irish HTR dataset
  (`meaisinfhoghlaim/datasets/irish_htr_dataset.py`, 25KB)
- The M4-Max dispatch helper
  (`select_optimal_for_m4_max()`)
- The llama-swap GGUF inference path
  (`meaisinfhoghlaim/models/llama_swap_config.yaml`)
- The BAML `baml_src/clients_ocr_ensemble.baml` patterns
- The RAGAS-voted chunk emission pattern
- The `meaisinfhoghlaim/ocr/` back-compat shim (deprecated
  location; canonical is `meaisinfhoghlaim.models`)

### B. Extend `INDEXING_AND_COGNITION.md` with §10 Code-search canonical entrypoint

**MODIFIED** `.agents/skills/INDEXING_AND_COGNITION.md` —
add `## 10. Code-search canonical entrypoint` after the
existing `## 9. The cianfhoghlaim v4 consolidation`. Resolves
the dual CLI vs v1 App split:

- CLI: `bun run ccc:search "<query>"` (kept for developer
  shortcuts)
- Python v1 App: `from cocoindex.codebase_indexing import
  code_search`
- Graph companion:
  `search_code_graph(file_path=..., node_type=...)`
- 4 infrastructure companions: `search_api_endpoints(...)`,
  `search_filesystem(...)`, `search_storage(...)`,
  `search_config(...)`
- A 3×5 decision matrix: "use CLI for ad-hoc, use v1 App for
  pipelines, use graph companion for code-structure queries"

### C. Create new `dlt_sources/DATA_PLATFORM_ROUTER.md`

**NEW** `dlt_sources/DATA_PLATFORM_ROUTER.md` — the single
router for the 5 per-area AGENTS.md files. Co-located with
the per-area `AGENTS.md` surface (not in `.agents/skills/`).
Covers:

- The 5-area routing table (`dlt_sources/`, `baml_src/`,
  `cocoindex/`, `orchestration/`, `meaisinfhoghlaim/`)
- The 6 critical conventions:
  1. Always use relative imports
  2. Respect the ingestion cache (`USE_LOCAL_SCRAPES=true`)
  3. Zero absolute namespaces in data pipelines
  4. R1-R4 CocoIndex conformance
  5. MODEL_REGISTRY-only (no hardcoded model strings)
  6. Factory pattern for N nearly-identical Apps
- The "I want to add X, where do I go?" routing table
- Cross-references back to each per-area `AGENTS.md`

### D. Cross-link from per-area AGENTS.md files

**MODIFIED** (5 files, +1 line each):
- `dlt_sources/AGENTS.md`
- `baml_src/AGENTS.md`
- `cocoindex/AGENTS.md`
- `orchestration/AGENTS.md`
- `meaisinfhoghlaim/README.md`

Each gets a 1-line `## Data platform router` cross-reference
to `dlt_sources/DATA_PLATFORM_ROUTER.md`.

### E. Spec delta to `centralized-model-registry`

**ADDED Requirement** in the
`openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/specs/centralized-model-registry/spec.md`
delta. See sibling `specs/centralized-model-registry/spec.md`
in this change.

## Dependencies

`Blocked by: none` (Change 1 is the first in the sequence)

`Blocks`:
- `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1`
  (Change 2) — needs the new `DATA_PLATFORM_ROUTER.md` path
  for the `docs/02-data-platform/*` guides.yml rewrite.
- `2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1`
  (Change 3) — needs Change 1's extensions to settle the
  skill count claim (66 → 67 skills).

`Affected repos: cianfhoghlaim` (single-repo change)

## Out of scope (intentionally)

- `.agents/skills_backup/` cleanup (55 deprecated skills) —
  left alone per the user's instruction (the backup is kept
  as a historical reference, not promoted to active).
- `sruth/` directory leftovers (`aleyum`, `anti-phish`,
  `browser`, `códeolas`, `crypteolas`, `data-engineering`,
  `oideachais`, `shared`, `shared-ui`, `spaces`, `tuath`) —
  preserved as historical pattern references per the user's
  instruction; not part of the active code surface; not
  documented in this change.
- New openspec spec for the data platform router — the router
  is an AGENTS.md-style doc (not a skill), so it lives under
  the existing `centralized-model-registry` spec delta
  (this change) and is referenced from
  `openspec/specs/data-engineering-pipeline-documentation/spec.md`
  in a follow-up.
- `ccc` skill deletion — still needed for the CLI shortcuts;
  the §10 entrypoint just makes the CLI vs v1 App split
  unambiguous.

## Verification

```bash
# 1. Skill metadata lint (66 → 67 after the new content)
mise run lint:skills
# Expected: 67/67 pass

# 2. Drift lint (no new drift introduced)
mise run lint:drift-docs --dry-run
# Expected: no new failures

# 3. OpenSpec validation
openspec validate 2026-08-13-skill-consolidation-and-extension-v1 --strict
# Expected: "Change is valid"

# 4. CCC search verification
bun run ccc:index
bun run ccc:search "OCR VLM pipeline"
bun run ccc:search "data platform router"
# Expected: centralized-registry §11 and DATA_PLATFORM_ROUTER.md as top results

# 5. Cross-link spot-check
grep -l "DATA_PLATFORM_ROUTER" dlt_sources/AGENTS.md baml_src/AGENTS.md cocoindex/AGENTS.md orchestration/AGENTS.md meaisinfhoghlaim/README.md
# Expected: all 5 files match

# 6. Skill frontmatter verification
head -3 .agents/skills/centralized-registry/SKILL.md
# Expected: frontmatter `description:` line mentions "OCR/VLM"
```