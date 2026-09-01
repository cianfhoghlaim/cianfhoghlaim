# Tasks — bonneagar Sister Umbrella Mirror v1

- [ ] **1** Adopt the
  [`2026-08-31-sister-repo-gemini-lesson-transfer-v1/`](../2026-08-31-sister-repo-gemini-lesson-transfer-v1/)
  as the primary dependency (Phase 8 of the v6-era plan
  executes the 6 GCP mirror stack promotions).
- [ ] **2** Mirror the 3 bonneagar-side changes
  (`bonneagar-init-v1` + `bonneagar-gcp-mirror-iac-promotion-v1` +
  `bonneagar-stackdriver-ai-agent-adk-instrumentation-v1`).
  **Verification:** `git ls-files openspec/changes/2026-09-01-bonneagar-*-mirror-v1/`
  reports 3 mirror directories.
- [ ] **3** Wire the per-PR reciprocal mirror CI gate (the
  `bonneagar:smoke` smoke test).
- [ ] **4** Wire the per-quadrant DuckLake `metadata_schema` to
  `bonneagar`.
- [ ] **5** Wire the per-sister Langfuse project
  (`bonneagar-dev` + `bonneagar-prod`).

**Total tasks:** 5.