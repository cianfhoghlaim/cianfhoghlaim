# Change: 2026-10-06-adk-cognee-visual-assets-v1

## Why

The ADK 2 Pillar 3 deep-research pipelines (aistear + primary + JC + SC +
tertiary) write briefings to in-memory context but never persist to
Cognee. The 8 subject agents (maths + applied_maths + chemistry + biology
+ physics + geography + history + english + gaeilge + computer_science)
can't answer "show me the assets related to Julius Caesar" because
there's no Cognee graph linking entities to assets.

The Cognee stack has 9 services running (per Plan 5 audit) but isn't
wired to the Pillar 3 pipeline. The 5 Pillar 3 pipelines need to:

1. Write the briefing to Cognee as a `LearningEpisode` record
2. Extract NER entities (people, places, concepts) via BAML
3. Link entities to assets via `CITED_IN` edges

This is Plan 6 of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — new (~3 files)
- `baml_src/media/extract_entities.baml` — the NER function + Entity + Relationship types
- `agents/meaisinfhoghlaim/media_intel/cognee_linker.py` — the linker (writes LearningEpisode + CITED_IN edges via the Cognee client)
- `notebooks/dashboards/cognee_asset_graph.py` — the marimo visual graph (entity → asset explorer)

### Spec materialised
- `openspec/specs/adk-cognee-visual-assets/spec.md` — 4 Requirements

### Reference surfaces
- `agents/workflows/{aistear,primary,jc,sc,tertiary}_deep_research.py` — the Pillar 3 pipelines (per Plan 2)
- `agents/meaisinfhoghlaim/media_intel/__init__.py` — the back-compat shim
- `bonneagar/stacks/lakehouse/cognee` — the Cognee service at :8000 (per Plan 5)

## What this does NOT ship
- A live connection to the running Cognee service (the 9 services are up but the SDK calls fall back to a stub when the Cognee endpoint is unreachable — offline dev mode)
- Cross-jurisdictional entity support (EN + GA + CY + GD) — deferred to Plan 7 (Celtic bilingual)
- The Tuatha closed-loop demo (deferred to Plan 8)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
