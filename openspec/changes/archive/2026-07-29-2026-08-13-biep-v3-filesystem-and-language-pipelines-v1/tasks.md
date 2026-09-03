# Tasks: 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1

## Code tasks

- [x] 1.1 Create `orchestration/defs/2_materials/filesystem_pipelines/generic_filesystem_assets.py` — 3 generic assets + 3 asset checks + 11 per-source backfill jobs
- [x] 1.2 Create `orchestration/defs/2_materials/language_pipelines/generic_language_assets.py` — 3 generic assets + 3 asset checks + 19 per-source backfill jobs
- [x] 2.1 Create `motherduck/flights/filesystem_monthly_sync_flight.py` — monthly MotherDuck Flight for filesystem
- [x] 2.2 Create `motherduck/flights/language_monthly_sync_flight.py` — monthly MotherDuck Flight for language

## Validation

- [ ] 3.1 `openspec validate 2026-08-13-biep-v3-filesystem-and-language-pipelines-v1 --strict` passes
- [ ] 3.2 `dg list assets | grep filesystem_` lists 3 assets + 3 checks
- [ ] 3.3 `dg list assets | grep language_` lists 3 assets + 3 checks
- [ ] 3.4 `mise run filesystem:monthly:sync` (the new monthly flight) runs cleanly
- [ ] 3.5 `mise run language:monthly:sync` (the new monthly flight) runs cleanly
- [ ] 3.6 `mise run lint:skills` still passes (53/53)
- [ ] 3.7 Push target: `origin/main`
