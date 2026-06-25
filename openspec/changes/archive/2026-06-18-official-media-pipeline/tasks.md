# Tasks — `official-media-pipeline`

Total: **6 phases, 41 tasks**.

## Phase 0 — OpenSpec scaffold (this commit)

- [x] 1. Create `openspec/changes/official-media-pipeline/{proposal.md, tasks.md, specs/{official-media-pipeline,official-media-fediverse,official-media-marimo}/spec.md}`
- [x] 2. Add 3 new capabilities to `openspec/project.md` (under Oideachais Quadrant)
- [x] 3. Add 3 new rows to `openspec/AGENTS.md` Capability Specs table
- [ ] 4. Validate: `openspec validate official-media-pipeline --strict`

## Phase 1 — DLT Instagram export parser (PR 1 commit A)

- [ ] 5. Create `sruth/oideachais/dlt_sources/official_media/__init__.py`
- [ ] 6. Create `sruth/oideachais/dlt_sources/official_media/instagram_export.py`
  - `@dlt.resource(name="profiles", write_disposition="merge", primary_key=["ig_export_id","ig_username","list_kind"])`
  - parses `connections/followers_and_following/{followers_1,following,close_friends,blocked_profiles,pending_follow_requests,removed_suggestions,restricted_profiles}.json`
  - yields one row per profile
- [ ] 7. Create `sruth/oideachais/dlt_sources/official_media/fixtures/allowlist_intelligence.yaml` (4 entries: mi5, mi6, gchq, hmgcc)
- [ ] 8. Create `sruth/oideachais/dlt_sources/official_media/fixtures/allowlist_universities.yaml` (~15 entries: UoG, QUB, UCL, TCD, MU, UL, UCD, NUIG, Aberystwyth, Cardiff Met, Edinburgh, Glasgow, Dundee, Stirling, Imperial, KCL)
- [ ] 9. Create `sruth/oideachais/dlt_sources/official_media/fixtures/allowlist_parties.yaml` (~12 entries: FF, FG, Labour, LD, Plaid, SNP, SF, DUP, UUP, SDLP, Alliance, Green IE)
- [ ] 10. Create `sruth/oideachais/dlt_sources/official_media/fixtures/allowlist_jurisdictions.yaml` (~42 entries: IE ~12, NI ~10, EN ~20)
- [ ] 11. Create `sruth/oideachais/dlt_sources/official_media/fixtures/official_media_overrides.yaml` (4 entries with hard-coded authoritative URLs for mi5.gov.uk, mi6.gov.uk, gchq.gov.uk, hmgcc.gov.uk + co-creation subpaths)
- [ ] 12. Create `sruth/oideachais/dlt_sources/official_media/allowlist.py` (YAML loader, normalised matcher, O(1) dict lookup)
- [ ] 13. Create `sruth/oideachais/dlt_sources/official_media/tests/__init__.py`
- [ ] 14. Create `sruth/oideachais/dlt_sources/official_media/tests/test_instagram_export.py` (parses synthetic fixture, asserts 1 row per profile)
- [ ] 15. Create `sruth/oideachais/dlt_sources/official_media/tests/test_allowlist.py` (asserts 4 known handles resolve, 4 friends do not)
- [ ] 16. `uv run pytest -q sruth/oideachais/dlt_sources/official_media/tests/` — must pass
- [ ] 17. `mise turbo lint && mise turbo typecheck`

## Phase 2 — BAML fallback (PR 1 commit B)

- [ ] 18. Create `baml_src/official_media.baml` with `ClassifyOfficialMedia` function calling `client "extract"`
- [ ] 19. Run `mise turbo baml:generate` (or `cd oideachais && uv run baml-cli generate`) to regen `baml_client/`
- [ ] 20. Create `sruth/oideachais/dlt_sources/official_media/classifier.py` (cheap regex heuristic gates BAML invocation; BAML fallback for lookalikes)
- [ ] 21. Create `sruth/oideachais/dlt_sources/official_media/tests/test_classifier.py` (5 fixtures, asserts fallback is invoked only for un-matched lookalikes)

## Phase 3 — Source resolver (PR 1 commit C)

- [ ] 22. Create `sruth/oideachais/dlt_sources/official_media/source_resolver.py` (orchestrates 4 parallel lookups: Wikipedia REST, Companies House API, CRO Ireland, fediverse)
- [ ] 23. Create `sruth/oideachais/dlt_sources/official_media/fediverse.py` (Mastodon webfinger + Bluesky xrpc, pure library)
- [ ] 24. Create `sruth/oideachais/dlt_sources/official_media/official_media_source.py` (`@dlt.source` tying parser + allowlist + classifier + resolver together)
- [ ] 25. Create `sruth/oideachais/dlt_sources/official_media/tests/test_resolver.py` (4 unit tests, 1 integration test with `USE_LIVE_LOOKUPS=false` using fixtures)
- [ ] 26. Create `sruth/oideachais/dlt_sources/official_media/tests/test_fediverse.py` (mocked webfinger + xrpc responses)

## Phase 4 — Dagster assets (PR 1 commit D)

- [ ] 27. Create `sruth/oideachais/dagster_defs/assets/official_media/__init__.py`
- [ ] 28. Create `sruth/oideachais/dagster_defs/assets/official_media/extract.py` (`@asset key=["official_media","extract"] group_name="official_media"`)
- [ ] 29. Create `sruth/oideachais/dagster_defs/assets/official_media/resolve_sources.py` (`@asset key=["official_media","resolve_sources"]`)
- [ ] 30. Create `sruth/oideachais/dagster_defs/assets/official_media/embed.py` (`@asset` writes BGE-M3 embeddings to `oideachais.official_media.descriptions` LanceDB table)
- [ ] 31. Create `sruth/oideachais/dagster_defs/assets/official_media/cognify.py` (registers Cognee dataset `oideachais_official_media` with 4 edge types)
- [ ] 32. Append 4 YAML entries to `sruth/oideachais/sources.yaml` under new `official_media` domain (mi5, mi6, gchq, hmgcc)
- [ ] 33. Add `@schedule(cron_schedule="0 5 1 * *", target=AssetSelection.groups("official_media"))` to `sruth/oideachais/dagster_defs/schedules.py`
- [ ] 34. Register the 5 assets in `sruth/oideachais/dagster_defs/definitions.py`
- [ ] 35. `uv run dagster dev` — confirm assets appear under group `official_media`
- [ ] 36. `mise turbo lint && mise turbo typecheck && uv run pytest -q`

## Phase 5 — Three dashboards (PR 1 commit E)

- [ ] 37. Create `sruth/oideachais/notebooks/dashboards/official_media.py` (marimo mission control with strong-stance footer)
- [ ] 38. Create `sruth/oideachais/web/src/routes/official-media/index.tsx` (TanStack Start page with strong-stance footer)
- [ ] 39. Create `sruth/oideachais/api/routes/official_media.py` (3 FastAPI endpoints: `POST /official-media/upload`, `GET /official-media/candidates`, `GET /official-media/{candidate_id}`)
- [ ] 40. Create `sruth/oideachais/cognee_integration/official_media.py` (registers `oideachais_official_media` dataset + 4 edge types)
- [ ] 41. Extend `sruth/oideachais/agents/adk/callbacks/citation_callbacks.py:287-332` with the `official_media` URL bucket

## Phase 6 — File issues, commit, push, archive (final)

- [ ] 42. File 5 follow-up GitHub issues (PR 2 jurisdictions, side-loadable app, HMGCC co-creation sub-asset, Companies House re-identification, deplatforming-thesis paper)
- [ ] 43. `git pull --rebase && git add -A && git commit -m "feat(official-media): Instagram-export → British-Isles government source enrichment pipeline" && git push`
- [ ] 44. `openspec archive official-media-pipeline --yes`
- [ ] 45. `bun run scripts/sync_agent_docs.sh`

## Total: 45 tasks across 7 phases, ~3,500 lines of new code + 4 YAMLs + 1 openspec scaffold
