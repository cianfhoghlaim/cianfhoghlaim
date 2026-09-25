# Tasks: 2026-10-02-adk-asset-generation-pillar3-v1

## 1. Group A — Stub-to-real sweep (C1 cross-cutting, Plan 1's first deliverable)

- [ ] **A1** `agents/adk/tools/image_generation.py` — replace `_stub_generate_image` with real `litellm.completion(model=model_for('image_gen', role), messages=[...])` calls (3 sites, lines 547/553/565)
- [ ] **A2** `agents/adk/image_generation_agent.py` — replace `GENERATE_2D_ASSET_TOOL = None` with `FunctionTool(generate_2d_asset)` (line 39)
- [ ] **A3** Same file — replace `GENERATE_TEXTURE_TOOL = None` with `FunctionTool(generate_texture)` (line 40)
- [ ] **A4** Same file — replace `STYLE_MATCH_TOOL = None` with `FunctionTool(style_match)` (line 41)
- [ ] **A5** Same file — replace `COCOINDEX_REGISTER_TOOL = None` with `FunctionTool(cocoindex_register)` (line 42)
- [ ] **A6** Same file — replace `LIST_IMAGE_MODELS_TOOL = None` with `FunctionTool(list_image_models)` (line 43)
- [ ] **A7** Verify all 6 tool replacements are wired into the agent's `tools=[...]` list

## 2. Group B — Pillar 3 → image-gen wiring (5 pipelines)

- [ ] **B1** `agents/workflows/aistear_deep_research.py` — add `render_assets_node` after `synthesize`; takes the briefing, generates 8 subject illustrations + 4 theme diagrams via image-gen tools
- [ ] **B2** `agents/workflows/primary_deep_research.py` — same pattern, 12 curriculum area illustrations
- [ ] **B3** `agents/workflows/jc_deep_research.py` — same pattern, 18 subject illustrations + CBA diagrams
- [ ] **B4** `agents/workflows/sc_deep_research.py` — same pattern, 50+ subject illustrations + past-paper diagrams
- [ ] **B5** `agents/workflows/tertiary_deep_research.py` — same pattern, 14 institution illustrations + module diagrams
- [ ] **B6** Add a shared `agents/workflows/_render_assets_node.py` helper to reduce duplication across the 5 pipelines
- [ ] **B7** Wire the `render_assets_node` output to `cocoindex_flows/media/image_generation_flow.py` LanceDB upsert (per the existing flow)

## 3. Group C — Visible demo surface (C6 quality-of-life)

- [ ] **C1** `scripts/asset_bench.py` — CLI: `python scripts/asset_bench.py "An Irish round tower at sunset"` → generates 5 variants (one per image_gen model) + LanceDB upsert + timing report
- [ ] **C2** `notebooks/dashboards/asset_gen_demo.py` — marimo notebook that demonstrates the full chain (Pillar 3 → image-gen → LanceDB → DuckLake)
- [ ] **C3** `mise run asset:bench` — wraps the CLI in mise.toml
- [ ] **C4** `bun run asset:demo` — wraps the marimo notebook in package.json

## 4. Group D — Skills + docs (C5 tie-off)

- [ ] **D1** `.agents/skills/tuatha-asset-generation/SKILL.md` — new skill (replaces deprecated `celtic-asset-generation`)
- [ ] **D2** Update `.agents/skills/INDEXING_AND_COGNITION.md` with the new skill
- [ ] **D3** Update `AGENTS.md` to reference the saga + Plan 1 status
- [ ] **D4** Update `CHEATSHEET.md` with the `mise run asset:bench` quick path

## 5. Group E — Spec materialisation

- [ ] **E1** `openspec/specs/adk-asset-gen-pillar3/spec.md` — 4 Requirements (R1: real image-gen calls, R2: Pillar 3 wiring, R3: 24 agents wired, R4: per-language support)
- [ ] **E2** `bunx openspec validate 2026-10-02-adk-asset-generation-pillar3-v1 --strict` passes

## 6. Group F — Verification + commit + push

- [ ] **F1** `uv run python scripts/asset_bench.py "An Irish round tower at sunset"` produces 5 variants + LanceDB upsert + timing report
- [ ] **F2** `uv run python scripts/preflight_education.py` still passes (5/5)
- [ ] **F3** `uv run python scripts/walk_education.py` still passes (5/5)
- [ ] **F4** `bunx openspec archive 2026-10-02-adk-asset-generation-pillar3-v1 --yes` (after F1-F3 pass)
- [ ] **F5** `git add -A && git commit && git push`
- [ ] **F6** Create PR via `gh pr create`
