# Tasks: 2026-10-03-cocoindex-retro-gameplay-v1

## 1. Group A — BAML contracts

- [ ] **A1** `baml_src/media/extract_design_pattern.baml` — define the new `RetroGameplayPattern` class + the `ExtractGameplayPattern` function
- [ ] **A2** Re-export the 4 existing classes from `gameplay_descriptor.baml` (`GameplayGenre` + `GameplayPowerEvent` + `GameplayVisualGrammar` + `GameplayPalette`) + add the new `RetroPatternSource` provenance class
- [ ] **A3** `uv run baml-cli generate` succeeds

## 2. Group B — CocoIndex flow

- [ ] **B1** `cocoindex_flows/media/retro_design_embedding.py` — the missing App
- [ ] **B2** Mount the `lance://media.retro_design_patterns` table (per the existing image_generation_flow.py pattern)
- [ ] **B3** Wire the BAML `ExtractGameplayPattern` function call inside the flow
- [ ] **B4** Add the SAM3 segmentation glue (against `sam3-server` stack — stubbed if stack not up)
- [ ] **B5** Add a `pattern_catalog_watcher` Dagster sensor (per the retro-game-design-catalogue spec)

## 3. Group C — ADK agent + tools

- [ ] **C1** `agents/adk/tools/retro_capture.py` — the libretro + ludusavi screenshot wrapper
- [ ] **C2** `agents/adk/tools/retro_pattern_extractor.py` — the BAML → typed pattern tool
- [ ] **C3** `agents/adk/retro_pattern_agent.py` — the ADK agent (the 25th in the 24-agent fleet, brings us to 25)

## 4. Group D — Visible demo (C6 quality-of-life)

- [ ] **D1** `scripts/retro_capture.py` — CLI: `python scripts/retro_capture.py "number_munchers.nes"` → 1 title screen captured + pattern extracted + stored in LanceDB
- [ ] **D2** `notebooks/dashboards/retro_patterns.py` — marimo notebook that displays the pattern catalog
- [ ] **D3** `mise run retro:capture` (wraps the CLI)
- [ ] **D4** `bun run retro:demo` (wraps the marimo notebook)

## 5. Group E — Skills + docs (C5 tie-off)

- [ ] **E1** `.agents/skills/retro-gameplay/SKILL.md` — new skill (the canonical reference for the pattern catalog)
- [ ] **E2** Update `.agents/skills/INDEXING_AND_COGNITION.md` with the new skill
- [ ] **E3** Update `AGENTS.md` to reference Plan 3 status
- [ ] **E4** Update `CHEATSHEET.md` with the `mise run retro:capture` quick path

## 6. Group F — Verification + commit + push

- [ ] **F1** `uv run python scripts/retro_capture.py --list-roms` (lists the available ROMs in the dev cache)
- [ ] **F2** `uv run python scripts/retro_capture.py <rom>` produces a screenshot + pattern (real or stub)
- [ ] **F3** `bunx openspec validate 2026-10-03-cocoindex-retro-gameplay-v1 --strict` passes
- [ ] **F4** `bunx openspec archive 2026-10-03-cocoindex-retro-gameplay-v1 --yes`
- [ ] **F5** `git add -A && git commit && git push`
- [ ] **F6** Create PR via `gh pr create`
