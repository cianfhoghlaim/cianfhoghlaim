# Tasks: 2026-10-06-adk-cognee-visual-assets-v1

## 1. Group A — BAML NER contract

- [x] **A1** `baml_src/media/extract_entities.baml` — the NER function + `Entity` + `Relationship` + `EntityKnowledgeGraph` types

## 2. Group B — Cognee linker

- [x] **B1** `agents/meaisinfhoghlaim/media_intel/cognee_linker.py` — the linker (writes `LearningEpisode` + `CITED_IN` edges via the Cognee client)
- [x] **B2** `link_briefing_to_cognee(briefing, subject, language)` — the canonical entry point (called from each Pillar 3 pipeline)
- [x] **B3** `extract_entities(briefing)` — calls the BAML NER + returns the `EntityKnowledgeGraph`
- [x] **B4** `link_entities_to_assets(entities, subject)` — creates the `CITED_IN` edges via Cognee

## 3. Group C — Visible demo

- [x] **C1** `notebooks/dashboards/cognee_asset_graph.py` — the marimo visual graph (entity → asset explorer)
- [x] **C2** `scripts/cognee_link.py` — CLI demo: `link --briefing "Julius Caesar was assassinated..." --subject history`

## 4. Group D — Spec materialisation

- [x] **D1** `openspec/specs/adk-cognee-visual-assets/spec.md` — 4 Requirements

## 5. Group E — Verification + commit + push

- [x] **E1** `bunx openspec validate 2026-10-06-adk-cognee-visual-assets-v1 --strict` passes
- [x] **E2** `uv run python -c "from agents.meaisinfhoghlaim.media_intel.cognee_linker import link_briefing_to_cognee"` works
- [x] **E3** `git add -A && git commit && git push`
- [x] **E4** Create PR via `gh pr create`
