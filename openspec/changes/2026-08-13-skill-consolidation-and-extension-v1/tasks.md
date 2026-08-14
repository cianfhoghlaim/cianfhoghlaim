# Tasks — Skill Consolidation & Extension

## 1. Extend `centralized-registry` skill with §11 OCR/VLM Pipeline

- [ ] 1.1 Verify the append point in
      `.agents/skills/centralized-registry/SKILL.md` (after
      `## 10. The 6 follow-up issues` — confirmed at line 321-330)
- [ ] 1.2 Add `## 11. OCR/VLM Pipeline` header
- [ ] 1.3 Write §11.1 — The 22-entry `VISION_MODELS` subset view
      (table with key + role + upstream_id + backend)
- [ ] 1.4 Write §11.2 — The 6 `CLASSICAL_OCR` backends
      (Pylaia + TrOCR + PaddleOCR + Tesseract + dots.ocr + VLM)
- [ ] 1.5 Write §11.3 — The BIEP v2 4-path ensemble
      (`EnsembledExtractor` — `baml + unstract + qwen3_vl + gemma4`
      with `asyncio.gather` + RAGAS voting + OCR_WEBHOOK_URL emission)
- [ ] 1.6 Write §11.4 — The 7 PDF converters
      (`docling`, `marker`, `unstructured`, `deepseekocr`,
      `pymupdf4llm`, `curriculum_document`, `pdf_factory`)
- [ ] 1.7 Write §11.5 — The 4 alignment methods + `ColPaliAligner`
      (VecAlign + HunAlign + GaoisAlign + Hybrid)
- [ ] 1.8 Write §11.6 — The Irish HTR dataset
      (point at the 25KB `irish_htr_dataset.py`)
- [ ] 1.9 Write §11.7 — The M4-Max dispatch helper
      (`select_optimal_for_m4_max()`)
- [ ] 1.10 Write §11.8 — llama-swap GGUF inference
      (`meaisinfhoghlaim/models/llama_swap_config.yaml`)
- [ ] 1.11 Write §11.9 — BAML `clients_ocr_ensemble.baml` patterns
- [ ] 1.12 Write §11.10 — RAGAS-voted chunk emission
- [ ] 1.13 Write §11.11 — The `meaisinfhoghlaim/ocr/` back-compat
      shim warning section
- [ ] 1.14 Update the `Version` + `Last Updated` lines in the
      frontmatter

## 2. Extend `INDEXING_AND_COGNITION.md` with §10 Code-search canonical entrypoint

- [ ] 2.1 Verify the append point (after `## 9. The cianfhoghlaim
      v4 consolidation` at line 578+)
- [ ] 2.2 Add `## 10. Code-search canonical entrypoint` header
- [ ] 2.3 Write §10.1 — Decision matrix (3 columns × 5 rows: CLI vs
      v1 App vs graph companion)
- [ ] 2.4 Write §10.2 — Code samples for each of the 3 surfaces
- [ ] 2.5 Write §10.3 — The 4 infrastructure companions table
      (`search_api_endpoints`, `search_filesystem`, `search_storage`,
      `search_config`)
- [ ] 2.6 Update the `Last updated` line

## 3. Create `dlt_sources/DATA_PLATFORM_ROUTER.md`

- [ ] 3.1 Write the header (post-v7 flattening + canonical homes)
- [ ] 3.2 Write the 5-area routing table (`dlt_sources/` /
      `baml_src/` / `cocoindex/` / `orchestration/` /
      `meaisinfhoghlaim/`) with line-counts + key artifact counts
- [ ] 3.3 Write the 6 critical conventions section
      (relative imports / USE_LOCAL_SCRAPES / zero-absolute-namespace /
      R1-R4 conformance / MODEL_REGISTRY-only / factory pattern)
- [ ] 3.4 Write the "I want to add X, where do I go?" routing table
      (10+ rows: new DLT source / new BAML extraction / new CocoIndex
      App / new jurisdiction / new Dagster asset / new OCR model /
      new alignment method / new PDF converter / new dataset / etc.)
- [ ] 3.5 Write the cross-references section (per-area AGENTS.md +
      openspec specs + skills)

## 4. Add cross-links from 5 per-area AGENTS.md files

- [ ] 4.1 Add `## Data platform router` section to
      `dlt_sources/AGENTS.md` (1 line cross-link to
      `DATA_PLATFORM_ROUTER.md`)
- [ ] 4.2 Same for `baml_src/AGENTS.md`
- [ ] 4.3 Same for `cocoindex/AGENTS.md`
- [ ] 4.4 Same for `orchestration/AGENTS.md`
- [ ] 4.5 Same for `meaisinfhoghlaim/README.md`

## 5. Spec delta to `centralized-model-registry`

- [ ] 5.1 Verify the
      `openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/specs/centralized-model-registry/spec.md`
      delta file is in place
- [ ] 5.2 Verify the ADDED Requirement + 2 Scenarios follow the
      `#### Scenario:` (4 hashtags) format per
      `openspec/AGENTS.md` §"Spec Delta Format"

## 6. Validation

- [ ] 6.1 `mise run lint:skills` — 67/67 pass (was 66 before)
- [ ] 6.2 `mise run lint:drift-docs --dry-run` — no new drift
- [ ] 6.3 `openspec validate 2026-08-13-skill-consolidation-and-extension-v1 --strict`
- [ ] 6.4 `bun run ccc:index` — refresh the index
- [ ] 6.5 `bun run ccc:search "OCR VLM pipeline"` — verify
      `centralized-registry §11` is first
- [ ] 6.6 `bun run ccc:search "data platform router"` — verify
      `DATA_PLATFORM_ROUTER.md` is first
- [ ] 6.7 `grep -l "DATA_PLATFORM_ROUTER" <5 files>` — all 5
      cross-links in place

## 7. Commit + push (Landing the Plane)

- [ ] 7.1 `git pull --rebase`
- [ ] 7.2 `git status` — review the changes
- [ ] 7.3 `git add openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/ .agents/skills/centralized-registry/SKILL.md .agents/skills/INDEXING_AND_COGNITION.md dlt_sources/DATA_PLATFORM_ROUTER.md dlt_sources/AGENTS.md baml_src/AGENTS.md cocoindex/AGENTS.md orchestration/AGENTS.md meaisinfhoghlaim/README.md`
- [ ] 7.4 `git commit -m "Skill consolidation: add OCR/VLM §11 + code-search §10 + DATA_PLATFORM_ROUTER"`
- [ ] 7.5 `git push`
- [ ] 7.6 `git status` — must show "up to date with origin"