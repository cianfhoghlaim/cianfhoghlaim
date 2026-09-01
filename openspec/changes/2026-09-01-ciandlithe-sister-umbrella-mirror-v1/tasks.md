# Tasks — ciandlíthe Sister Umbrella Mirror v1

- [ ] **1** Adopt the 5 cianfhoghlaim-side umbrellas as
  dependencies (per the proposal's "Sister-side awareness" section).
  **Verification:** the 5 umbrellas' proposals include
  ciandlíthe-side awareness entries.
- [ ] **2** Mirror the 8 ciandlíthe-side changes to the
  cianfhoghlaim-side mirror directories.
  **Verification:** `git ls-files openspec/changes/2026-MM-DD-ciandlithe-*-mirror-v1/`
  reports 8 mirror directories.
- [ ] **3** Wire the per-PR reciprocal mirror CI gate.
  **Verification:** the CI gate runs on every PR to ciandlíthe/.
- [ ] **4** Wire the per-quadrant DuckLake `metadata_schema` to
  `oideachais`.
  **Verification:** every ciandlíthe destination writes to the
  `oideachais` quadrant.
- [ ] **5** Wire the per-sister Langfuse project (`ciandlithe-dev` +
  `ciandlithe-prod`).
  **Verification:** the projects exist in `observability/langfuse_config.py`.

**Total tasks:** 5.
