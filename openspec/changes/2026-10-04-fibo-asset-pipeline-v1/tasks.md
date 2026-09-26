# Tasks: 2026-10-04-fibo-asset-pipeline-v1

## 1. Group A — Source recovery

- [x] **A1** `tuatha/asset_generation/fibo/__init__.py` — the public package surface (FiboResource + ValidationResource + 6 dataclasses + 3 Dagster assets + 3 helpers)
- [x] **A2** `tuatha/asset_generation/fibo/schemas.py` — the 6 dataclasses
- [x] **A3** `tuatha/asset_generation/fibo/education_fibo.py` — the 8 bilingual prompt templates
- [x] **A4** `tuatha/asset_generation/fibo/resources.py` — FiboResource (litellm image gen) + ValidationResource (VLM scorer)
- [x] **A5** `tuatha/asset_generation/fibo/assets.py` — the 3 Dagster assets

## 2. Group B — BAML integration

- [ ] **B1** Add `ExtractSyllabusDiagram` function to `baml_src/media/extract_design_pattern.baml` (deferred — only when baml-cli generate runs)
- [ ] **B2** `uv run baml-cli generate` succeeds (generates the typed Python client)

## 3. Group C — Visible demo

- [x] **C1** `scripts/fibo_render.py` — CLI: `list-subjects` + `show-prompt` + render-one + `render-all`
- [x] **C2** `notebooks/dashboards/fibo_diagram_demo.py` — marimo dashboard with subject picker + render button + validation score

## 4. Group D — Spec materialisation

- [x] **D1** `openspec/specs/fibo-asset-pipeline/spec.md` — 4 Requirements

## 5. Group E — Verification + commit + push

- [x] **E1** `uv run python scripts/fibo_render.py --list-subjects` → 8 subjects
- [x] **E2** `uv run python scripts/fibo_render.py --subject chemistry --show-prompt` → full BAML prompt
- [x] **E3** `bunx openspec validate 2026-10-04-fibo-asset-pipeline-v1 --strict` passes
- [ ] **E4** `bunx openspec archive 2026-10-04-fibo-asset-pipeline-v1 --yes`
- [ ] **E5** `git add -A && git commit && git push`
- [ ] **E6** Create PR via `gh pr create`
