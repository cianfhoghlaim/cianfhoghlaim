# Tasks: Leabharlann cognify + cross-archive edges

## Phase 1 — Cognify adapter

- [ ] Add `oideachais/cognee_integration/leabharlann_cognify.py` with the
      `LeabharlannCognify` class that takes a `LeabharlannDataset` enum
      (`books` | `zotero` | `takeout`) and runs `cognee.add()` + `cognify()`
      on the DuckLake rows.
- [ ] Hook `cognify_leabharlann_books` / `zotero` / `takeout` Dagster
      assets to call this adapter.
- [ ] Add a `oideachais/tests/test_leabharlann_cognify.py` test (graceful
      if `cognee` is missing).

## Phase 2 — Cross-archive edges

- [ ] Add `oideachais/cognify_rules/leabharlann_cross_archive.py` with 3
      rule classes: `ArxivIdMatch`, `ModuleTitleMatch`, `UrlMatch`.
- [ ] Add `oideachais/api/cross_archive_graph.py` FastAPI route
      `GET /cross-archive-graph/{query}` that runs a FalkorDB query.
- [ ] Wire `cross_archive_edges` Dagster asset to call the rules and
      populate FalkorDB via the `oideachais/graph/falkordb_client.py`.
- [ ] Add a `oideachais/tests/test_leabharlann_cross_archive.py` test
      (graceful if `falkordb` is missing).

## Phase 3 — Cron sensor

- [ ] Add `oideachais/dagster_defs/sensors/cognee_cron_sensor.py` with a
      daily cron that fires the 4 cognify + cross-archive assets.
- [ ] Register the sensor in `oideachais/dagster_defs/sensors/__init__.py`.

## Phase 4 — Validation

- [ ] Run `openspec validate leabharlann-cognify-and-cross-archive-edges --strict`.
- [ ] Run the leabharlann pytest suite; confirm 0 failures.
- [ ] Run `git push` and confirm "up to date with origin".
- [ ] Archive the change: `openspec archive leabharlann-cognify-and-cross-archive-edges --yes`.
