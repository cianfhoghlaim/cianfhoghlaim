# Change: Knowledge-graph population activation (bring up Cognee + populate 5-stage Irish education KG)

## Why

The Irish 5-stage education knowledge graph (Aistear → Primary → JC →
SC → University) is architecturally complete in code but **not
populated**:

1. The `cognee` Docker stack at `bonneagar/stacks/cognee/` is not
   running (`docker compose up cognee` from that directory has never
   been executed in the current deployment).
2. The 5 stage cognify `defs.yaml` files at
   `orchestration/defs/3_model_lifecycle/cognify/{aistear,primary,junior_cycle,senior_cycle,university}/`
   exist as directories but only `cross_stage_cognify/defs.yaml` has
   been registered; the 5 per-stage `defs.yaml` files are missing.
3. The 8 BRIDGE cross-stage edges + 38 cross-jurisdiction equivalences
   + 7 ingest sensors are specified in the existing
   `2026-08-10-knowledge-graph-population-v1` change (currently 0/16
   tasks) but never executed.
4. The 2 BAML Gaeilge functions (`ExtractBilingualLearningOutcome`,
   `ExtractCrossLinguisticGA`) are stub-prompted; without Cognee
   running, the cognify assets that would call them have no effect.

The blocking chain: Plan V-A closes the OCR/VLM end-to-end
round-trip → Plan V-B un-stubs the 4-path ensemble → this change
populates the KG that downstream agents (the 12-agent fleet's
`education_research`, `curriculum_comparison`, etc.) consume.

## What Changes

- **Bring up the Cognee stack** — `docker compose up -d` from
  `bonneagar/stacks/cognee/` (one command, currently down per the
  `2026-08-10-knowledge-graph-population-v1` change's Why section).
- **Register the 5 missing per-stage cognify `defs.yaml` files** at
  `orchestration/defs/3_model_lifecycle/cognify/{aistear,primary,junior_cycle,senior_cycle,university}/defs.yaml`.
- **Activate the 8 BRIDGE cross-stage edges** — between Aistear ↔
  Primary, Primary ↔ JC, JC ↔ SC, SC ↔ University, plus the 4 lateral
  equivalences (JC SC ↔ England KS4, SC ↔ Scotland Higher, etc.).
- **Activate the 38 cross-jurisdiction equivalences** — the
  equivalence edges that connect the Irish 5-stage KG to the
  England / Scotland / Wales / NI 5-stage KGs (per the
  `british-isles-education-pipeline-v3` spec).
- **Activate the 7 ingest sensors** (one per KG stage) — each polls
  the upstream registry for new cohorts and triggers cognify.
- **Add real BAML prompts** for the 2 Gaeilge functions
  (`ExtractBilingualLearningOutcome`, `ExtractCrossLinguisticGA`)
  with the `gaeilge_lc_client` (routed through
  `uccix-mistral-24b` — the platform's only dedicated Irish-language
  model).
- Add 2 new Requirements to `british-isles-education-pipeline-v3`
  formalising the "5-stage cognify graph must be populated" and
  "Bilingual EN+GA extraction must use the Gaeilge client"
  invariants.

## Dependencies

`Blocked by: none`. `Blocked by (soft):
2026-08-10-ocr-vision-activation-completion-v1` (the OCR table this
change writes to downstream of cognify). `Affected repos: cianfhoghlaim
(single repo)`.

## Impact

- Capabilities: MODIFIED `british-isles-education-pipeline-v3` (2
  ADDED Requirements).
- Code: 5 new `defs.yaml` files at
  `orchestration/defs/3_model_lifecycle/cognify/<stage>/defs.yaml` +
  7 new sensor files at
  `orchestration/sensors/<stage>_cognify_sensor.py` + BAML prompt
  additions for the 2 Gaeilge functions + Cognee stack deployment.
- Risk: medium — bringing up a new service is operationally invasive
  (cognee-postgres + cognee redis + cognee api containers all come up
  together); mitigated by the `bonneagar/stacks/GOLD_STANDARD.md`
  6-file pattern that this stack follows.
