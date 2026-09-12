# Tasks: pipeline-british-isles-synthesis-v1 (BIEP v3 Ireland LC Pipeline Synthesis)

## Stage 0 — Inert-layer verification
- [x] T0.1 — Verify cocoindex resolves to PyPI (defect #1 FIXED)
- [x] T0.2 — Verify orchestration/defs/__init__.py exists (defect #2 FIXED)
- [x] T0.3 — Verify baml_client can't be generated (defect #3 EVOLVED — duplicate class defs)
- [x] T0.4 — Verify import dlt_sources is a no-op (defect #4 MOSTLY FIXED)
- [x] T0.5 — Verify OCR ensemble sends real images (defect #5 PARTIALLY FIXED)

## Stage 1 — Per-subject pipeline build
- [x] T1.1 — Ship `pipeline-mathematics-v1` (CocoIndex App + 9 pytests)
- [x] T1.2 — Ship `pipeline-chemistry-v1` (CocoIndex App + 4 pytests)
- [x] T1.3 — Ship `pipeline-geography-v1` (CocoIndex App + 4 pytests)
- [x] T1.4 — Ship `pipeline-english-v1` (CocoIndex App + 4 pytests)
- [x] T1.5 — Ship `pipeline-gaeilge-v1` (CocoIndex App + 4 pytests)
- [x] T1.6 — Ship `pipeline-computer-science-v1` (CocoIndex App + 4 pytests)

## Stage 2 — Synthesis
- [x] T2.1 — Write the per-subject status table to `proposal.md`
- [x] T2.2 — Write the "what works / what's blocked" Requirement + Scenario to the spec delta
- [x] T2.3 — Run `uv run pytest tests/biep_parity_lc/ -v` and confirm 29/29 pass
- [x] T2.4 — Run `openspec validate pipeline-british-isles-synthesis-v1 --strict`
- [x] T2.5 — Commit + push the synthesis change

## Acceptance gate

This change is complete when:
- All 6 per-subject openspec changes (`pipeline-mathematics-v1`
  through `pipeline-computer-science-v1`) are valid
- All 29 pytests in `tests/biep_parity_lc/` pass
- `openspec validate pipeline-british-isles-synthesis-v1 --strict` passes
- The synthesis change is committed + pushed
