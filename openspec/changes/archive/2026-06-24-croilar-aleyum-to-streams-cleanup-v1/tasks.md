# Tasks for croilar-aleyum-to-streams-cleanup-v1

## 1. 5 aleyum→croilar alias collapses

- [x] 1.1 `sruth/croilar/pipelines/shared/destinations.py`: 8 aleyum renames
  (database_path, r2_bucket, catalog_uri, 4 pipeline names,
  env var ALEYUM_ENV → CROILAR_ENV)
- [x] 1.2 `sruth/croilar/pipelines/shared/ducklake.py`: 3 aleyum renames
  (default catalog_path, default r2_bucket, initialize_catalog defaults)
- [x] 1.3 `sruth/croilar/pipelines/shared/r2_client.py`: 1 aleyum constant
  removal (ALEYUM_R2_BUCKET = "aleyum-assets" removed)

## 2. Deprecated AleyumSettings alias removal

- [x] 2.1 `sruth/croilar/_shared/config/settings.py`: remove the
  `AleyumSettings = StreamSettings` deprecated alias

## 3. One new skill

- [x] 3.1 Create `.agents/skills/croilar-stream-registry/SKILL.md`
  (the 5 collapses + the StreamSettings Pydantic BaseSettings +
  the 12 stream-driven Dagster assets + the Stream model + the
  sources.yaml registry file + the add-a-new-stream workflow)

## 4. Spec delta

- [x] 4.1 ADDED Requirement "Aleyum-to-croilar cleanup mandate"
  (the 5 aliases collapsed + the deprecation mandate)
- [x] 4.2 ADDED Requirement "Stream-registry canonical config
  surface" (the StreamSettings Pydantic BaseSettings + the
  sources.yaml + the 12 default streams)

## 5. Documentation

- [x] 5.1 Update `sruth/croilar/AGENTS.md` (priority skills 8 of 108 →
  9 of 120 + 1 new skill row in the related skills section)

## 6. Validation + commit + push + archive

- [ ] 6.1 Run `openspec validate croilar-aleyum-to-streams-cleanup-v1 --strict`
- [ ] 6.2 Run `mise run lint:skills` to verify the 1 new skill
- [ ] 6.3 Commit + push
- [ ] 6.4 Run `openspec archive croilar-aleyum-to-streams-cleanup-v1 --yes`
