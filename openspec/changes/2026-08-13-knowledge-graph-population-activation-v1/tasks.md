# Tasks: Knowledge-graph population activation

## Phase A — Bring up Cognee stack (1 task, ~30 minutes)

- [ ] A1 `cd bonneagar/stacks/cognee/ && docker compose up -d` —
  bring up the 3-container Cognee stack (cognee-postgres + cognee
  redis + cognee api).
- [ ] A2 Verify `curl http://cognee:8000/health` returns 200.
- [ ] A3 Verify the `md:cianfhoghlaim.cognee_metadata` table exists
  in MotherDuck (auto-created by Cognee on first cognify).

## Phase B — Register 5 per-stage cognify `defs.yaml` files (1 task, ~30 minutes)

- [ ] B1 Copy the `cross_stage_cognify/defs.yaml` template to
  `orchestration/defs/3_model_lifecycle/cognify/{aistear,primary,junior_cycle,senior_cycle,university}/defs.yaml`,
  adjusting the dataset name + partition key per stage.
- [ ] B2 `dagster asset list | grep cognify` returns 5 new
  `lc5_<stage>_cognified` assets (one per stage).

## Phase C — Real BAML prompts for the 2 Gaeilge functions (1 task, ~30 minutes)

- [ ] C1 Replace the `"Auto-generated extraction prompt."` placeholders
  in `baml_src/british_isles/ireland/education/lc_extraction/gaeilge_extraction.baml`
  with real prompts for `ExtractBilingualLearningOutcome` and
  `ExtractCrossLinguisticGA`.
- [ ] C2 Wire both functions to `client gaeilge_lc_client`
  (`uccix-mistral-24b` via LiteLLM — per the
  `2026-08-10-baml-extraction-completion-v1` change's Phase 4).
- [ ] C3 `.venv/bin/baml-cli generate --from baml_src` regenerates
  the 14 BAML client files.

## Phase D — Activate the 8 BRIDGE cross-stage edges + 38 equivalences (2 tasks, ~1 hour)

- [ ] D1 Add the 8 BRIDGE cross-stage edges to the Cognee graph via
  `cognee_client.add_edges()` in
  `orchestration/defs/3_model_lifecycle/cognify/cross_stage_cognify/assets.py`.
- [ ] D2 Add the 38 cross-jurisdiction equivalences via
  `cognee_client.add_edges()` referencing the existing
  `british_isles_cross_jurisdiction_equivalences.csv` (the canonical
  equivalence table maintained by the Education Ministry).

## Phase E — Activate the 7 ingest sensors (1 task, ~30 minutes)

- [ ] E1 Create
  `orchestration/sensors/{aistear,primary,junior_cycle,senior_cycle,university,england_keystage,scotland_curriculum}_cognify_sensor.py`
  (7 new sensors, one per cognify stage + 2 cross-jurisdiction).
- [ ] E2 Each sensor uses the same pattern as the
  `garage_pdf_arrival_sensor.py` (poll every 300s, emit RunRequest
  on change).
- [ ] E3 Re-export from `orchestration/sensors/__init__.py`.

## Phase F — Validate (3 tasks, ~30 minutes)

- [ ] F1 `dagster asset materialize --select cognify_*` runs 5
  successful materializations (one per stage).
- [ ] F2 `SELECT COUNT(*) FROM cognee_graph.nodes WHERE stage IN
  ('aistear', 'primary', 'jc', 'sc', 'university')` returns ≥ 1,000
  real nodes (the live-verified hydration baseline).
- [ ] F3 `openspec validate
  2026-08-13-knowledge-graph-population-activation-v1 --strict`
  returns 0 errors.

## Out of scope (flagged for follow-up)

- The cognify tables for the 7 Celtic languages (Welsh, Scottish
  Gaelic, Cornish, Breton, Manx, + 1 placeholder) — separate change
  per the `celtic-language-pipeline` spec.
- The FalkorDB temporal KG layer (handled by
  `2026-08-15-retroactive-pre-v7-cleanup-v1`'s deferred items).
