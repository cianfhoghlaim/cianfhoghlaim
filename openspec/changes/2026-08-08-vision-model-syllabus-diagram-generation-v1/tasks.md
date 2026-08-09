# Tasks — Vision-model syllabus diagram generation

## Phase 1 — Wire real SyllabusDiagram extraction into FIBO — DONE

- [x] 1.1 Added `fibo_configs_from_syllabus_diagrams` to
  `tuatha/asset_generation/fibo/assets.py`: self-contained
  `_find_english_syllabus_pdf()` (mirrors the syllabus-file slice of
  `quest_pack_assets.py`'s classifier without cross-layer importing),
  `SyllabusDiagramGenerationConfig` (subject/max_diagrams/style), and
  the asset function itself — extracts real PDF text, calls
  `ExtractSyllabusDiagram`, maps each returned `SyllabusDiagram` into a
  FIBO config via `FiboResource.create_educational_prompt()`.
- [x] 1.2 Live-verified `_find_english_syllabus_pdf()` against the
  real corpus: resolves the correct syllabus PDF for 7/8 subjects
  (mathematics, chemistry, geography, history, applied_mathematics,
  english, computer_science) and correctly returns `None` for gaeilge
  (Irish-medium, no English-medium syllabus in the corpus — same
  primary-language finding as `quest_pack_assets.py`'s classifier).
- [x] 1.3 Documented, not fixed: `ExtractSyllabusDiagram` takes no
  `image` parameter despite `client BIEPV3Vision` — text-only
  detection, not true vision pointing. Flagged in both the asset's own
  docstring and `proposal.md`.
- [x] 1.4 Updated `tuatha/asset_generation/fibo/__init__.py`'s export
  list.

## Phase 2 — Extend to more subjects / Junior Cycle

- [ ] 2.1 **Not attempted, blocked on the same real gap Proposal 1
  flagged**: Junior Cycle has no local PDF corpus under
  `leaving_certificate/` for these subjects; wiring Junior Cycle
  diagram generation needs the separate JC DLT ingestion tree wired
  first (out of scope here, same as Proposal 1 Phase 2).
- [x] 2.2 The new asset is already generic across all 8 LC subjects
  (`SyllabusDiagramGenerationConfig.subject`, not hardcoded per
  subject) — no additional per-subject code needed beyond Phase 1;
  "extend to geography + other diagram-bearing subjects" from the
  original plan is satisfied by this genericity rather than needing
  8 separate asset functions.

## Phase 3 — Correct the `celtic-asset-generation` spec — DONE (scoped)

- [x] 3.1 Added `Requirement: FIBO 2D educational diagram generation
  (as-built)` describing the real pipeline
  (`fibo_json_configs`/`generated_images`/
  `fibo_configs_from_syllabus_diagrams`).
- [x] 3.2 **Scoped down from a full spec rewrite**: added a correction
  note to the Purpose section rather than deleting or rewriting the
  existing "4 Successive Independent Asset Gen Pipelines" / VLM-
  backbone / 6-Celtic-language content — that content already
  cross-references a dedicated provisional-schema requirement
  pointing at a cleanup change; wholesale rewriting it here would risk
  losing roadmap context this change's author doesn't have full
  visibility into. Flagged as real, necessary future cleanup rather
  than silently left inconsistent.

## Phase 4 — Verification

- [x] 4.1 Live-verified `_find_english_syllabus_pdf()` against the
  real `leaving_certificate/` corpus for all 8 subjects (see 1.2).
- [ ] 4.2 A diagram traced end-to-end from source PDF page to a
  rendered image asset — **blocked**: `generated_images` (the
  render/validate/refine step) calls a LiteLLM image-generation
  endpoint (`/v1/images/generations`) that isn't configured/reachable
  in this environment; `fibo_configs_from_syllabus_diagrams` (the
  extraction → config step this change adds) was verified up to
  producing real FIBO configs, not through actual image rendering.
- [x] 4.3 `openspec validate 2026-08-08-vision-model-syllabus-diagram-
  generation-v1 --strict`.
