# Tasks: pipeline-baml-extraction

> Cross-batch BAML completion + CopilotKit action wiring contract.
> Absorbs `2026-08-10-baml-extraction-completion-v1` (6/22) +
> `2026-08-10-copilotkit-action-wiring-v1` (0/16).

## 1. Real BAML extraction prompts for the 6 LC subjects (from baml-extraction-completion-v1)

- [ ] **B1.1** Un-stub `lc5_chemistry_diagrams_extracted` (the one real implementation of the LC5 factory pattern at `orchestration/defs/2_materials/lc_extraction/lc5_assets.py:218-313`)
- [x] **B1.2** Already complete: `ExtractSyllabusDiagram` gained the `image: image[]?` parameter (backwards-compatible)
- [x] **B1.3** Already complete: `pdf_to_image_bridge.py` (pymupdf-based page render → `baml_py.Image`)
- [x] **B1.4** Already complete: `BAML_AVAILABLE` import fallback fixed
- [x] **B1.5** Already complete: 139 real corpus rows + 11 real syllabus cross-check rows
- [x] **B1.6** Already complete: `lc5_computer_science_papers_extracted` un-stubbed (the simplest non-chemistry LC5 asset)
- [ ] **B1.7** Add the corresponding BAML function-side prompt to `baml_src/british_isles/ireland/education/lc_extraction/computer_science_papers.baml`
- [ ] **B1.8** Implement the LC pilot factory: `lc_subject_pilot_factory(subject) → Dagster asset group`
- [ ] **B1.9** Wire 6 subjects × 3 assets = 18 assets into Dagster under `orchestration/defs/2_materials/lc_extraction/`
- [ ] **B1.10** Add Irish-language path using `uccix-mistral-24b` for the 6 LC subjects
- [ ] **B1.11** Replace stubs for `lc5_physics_diagrams_extracted`, `lc5_biology_diagrams_extracted`, `lc5_agricultural_science_extracted`, `lc5_construction_studies_extracted`, `lc5_engineering_extracted`
- [ ] **B1.12** Update `openspec/specs/british-isles-education-pipeline-v3/spec.md` +6 ADDED Requirements (real prompts + factory + Irish path)

## 2. CopilotKit action wiring (from copilotkit-action-wiring-v1)

- [ ] **B2.1** Wire all 13 remaining stubs in `actions.ts` to real handlers (BAML / DuckLake / Convex / FalkorDB)
- [ ] **B2.2** Replace `/en/agents/$agent.tsx` metadata display with inline `<CopilotKit>` chat
- [ ] **B2.3** Add the 6th "Knowledge Graph Health" tab to `notebooks/00_control_panel.py`
- [ ] **B2.4** Update `openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` +3 ADDED Requirements (13 actions wired + agent chat route + KG health tab)

## 3. Verification

- [ ] Run `openspec validate pipeline-baml-extraction --strict` — pass
- [ ] Run `openspec validate --all --strict` — pass

## Verification

```bash
cd ~/dev/cianchosaint-laim 2>/dev/null || cd ~/dev/cianfhoghlaim
openspec validate pipeline-baml-extraction --strict
```
