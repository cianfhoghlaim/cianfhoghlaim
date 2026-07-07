# Tasks: croilar-personas-to-streams

## Phase 0 — OpenSpec setup

- [x] 0.1 Create change directory `openspec/changes/croilar-personas-to-streams/`
- [x] 0.2 Write `proposal.md`
- [x] 0.3 Write `tasks.md`
- [x] 0.4 Write `specs/croilar-data-engineering/spec.md` (MODIFIED)
- [x] 0.5 Write `specs/croilar-portfolio/spec.md` (MODIFIED)
- [x] 0.6 Write `specs/croilar-stream-registry/spec.md` (ADDED)
- [ ] 0.7 Run `openspec validate croilar-personas-to-streams --strict` until green

## Phase 1 — Stream registry (the core refactor)

- [ ] 1.1 Create `sruth/croilar/_shared/streams.py` with `StreamSourceType`, `StreamSource`, `Stream`, `load_streams_from_yaml`, `get_stream`, `list_streams`
- [ ] 1.2 Replace `sruth/croilar/_shared/config/settings.py` `AleyumSettings` with `StreamSettings`; env prefix `ALEYUM_` → `STREAMS_`; add `streams: dict[str, Stream]`
- [ ] 1.3 Update `sruth/croilar/_shared/config/paths.py` references if any to `aleyum`
- [ ] 1.4 Replace `sruth/croilar/config/sources.yaml` with the new `streams:` shape
- [ ] 1.5 Modify `sruth/croilar/pipelines/linkedin/source.py`: `flow_id` → `stream_id`, drop `carlcashman` default, default profile URL = Cian's LinkedIn
- [ ] 1.6 Modify `sruth/croilar/pipelines/github/source.py`: default `username="cianfhoghlaim"`
- [ ] 1.7 Modify `sruth/croilar/baml/linkedin_profile_extraction.baml`: `flowId` → `streamId`, allowed values `music|teaching|cv|research`, add `ownerDisplayName`
- [ ] 1.8 Create `sruth/croilar/baml/researchgate_extraction.baml` (mirrors LinkedIn schema)
- [ ] 1.9 Modify `sruth/croilar/dagster_assets/dlt_assets.py`: replace hard-coded `aleyummusic`/`aleyum` with generic asset factory
- [ ] 1.10 Modify `sruth/croilar/agent_os/main.py`: `init_config(service_name=aleyum)` → per-stream; per-stream ports 7774-7777
- [ ] 1.11 Modify `sruth/croilar/pipelines/shared/destinations.py`, `r2_client.py`, `ducklake.py`: generic R2 bucket, per-stream prefix, local-only gate
- [ ] 1.12 Modify `sruth/croilar/packages/i18n/src/index.ts`: rekey by stream id; migrate `resources/aleyum/`, `resources/cianfhoghlaim/` to `resources/streams/{music,teaching}/{en,ga}/`
- [ ] 1.13 Move `sruth/croilar/notebooks/aleyum/music_analytics.py` → `sruth/croilar/notebooks/streams/music/music_analytics.py`
- [ ] 1.14 Move `sruth/croilar/notebooks/cianfhoghlaim/teaching_analytics.py` → `sruth/croilar/notebooks/streams/teaching/teaching_analytics.py`
- [ ] 1.15 Modify `sruth/croilar/apps/web/package.json`: rekey `notebook:wasm:aleyum` → `notebook:wasm:music`
- [ ] 1.16 Modify `sruth/croilar/apps/portal/src/routes/_layout/analytics/index.tsx`: rekey dive URLs
- [ ] 1.17 Modify `sruth/croilar/apps/portal/src/lib/tenant/tenant-context.tsx`: body class `tenant-<owner>`
- [ ] 1.18 Modify `sruth/croilar/tests/test_database.py`, `test_smoke.py`: use stream ids, add new tests

## Phase 2 — New sources (ResearchGate, filesystem)

- [ ] 2.1 Create `sruth/croilar/pipelines/researchgate/__init__.py`, `source.py`, `scraper.py` (DLT REST + sruth-browser)
- [ ] 2.2 Create `sruth/croilar/pipelines/fs_author/__init__.py`, `source.py` (DLT filesystem, local-only)
- [ ] 2.3 Wire `researchgate` and `fs_author` into the new `sources.yaml` streams
- [ ] 2.4 Wire `researchgate` and `fs_author` into the dlt_assets.py factory
- [ ] 2.5 Add tests: `test_fs_author_local_only`, `test_researchgate_source_exports`

## Phase 3 — Migration script

- [ ] 3.1 Create `sruth/croilar/scripts/migrate-personas-to-streams.ts` (rename dirs, rewrite imports, emit CSV diff)
- [ ] 3.2 Run `bun run migrate:personas-to-streams` against the repo
- [ ] 3.3 Manual review of CSV diff; commit any stragglers

## Phase 4 — Quality gates

- [ ] 4.1 `openspec validate croilar-personas-to-streams --strict` — must pass
- [ ] 4.2 `bun run turbo typecheck` — must pass
- [ ] 4.3 `bun run turbo lint` — must pass
- [ ] 4.4 `bun run turbo test` — must pass
- [ ] 4.5 `bun run ccc:index` and `bun run ccc:search "Stream registry"` — confirm new abstraction is searchable
- [ ] 4.6 `mise turbo build dagster` — confirm code-location loads

## Phase 5 — Commit, push, follow-up

- [ ] 5.1 `git add -A`
- [ ] 5.2 `git commit -m "refactor(croilar): replace personas with Stream registry"`
- [ ] 5.3 `git push`
- [ ] 5.4 File follow-up issues:
  - [ ] Zotero SQLite ingest (deferred)
  - [ ] Kneecap pipeline in a separate repo outside leabharlann policy scope (deferred per user decision)
- [ ] 5.5 Update `sruth/croilar/README.md` and `stack.md` so the new Stream model is discoverable
- [ ] 5.6 `openspec archive croilar-personas-to-streams --yes` after deployment
