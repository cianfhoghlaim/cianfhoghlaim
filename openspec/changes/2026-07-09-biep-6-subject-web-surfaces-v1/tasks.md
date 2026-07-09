# Tasks: 2026-07-09-biep-6-subject-web-surfaces-v1

## Phase 1 — Brown Ajah / WoT theming cleanup (T6 Step 1, 4 hours)

### 1.1 — Component code (Header + Sidebar + OsProvider + 5 routes)

- [x] 1.1.1 Strip `CiBrownAjahBadge` + `CiTuathanWagon` imports from `apps/web/src/components/Header.tsx`; replace with a "C" letter-mark `<CiBrandBadge>`; update tagline to "Cianfhoghlaim — Coláiste na Déisigh"
- [x] 1.1.2 Drop "Aes Sedai — servants of all" tagline from `apps/web/src/components/Sidebar.tsx`; replace `Theming=Brown Ajah` with `Theming=professional`
- [x] 1.1.3 Drop "Brown Ajah member" from `apps/web/src/components/CianfhoghlaimOS.tsx`
- [x] 1.1.4 Drop "Brown Ajah theming" from `apps/web/src/routes/__root.tsx` (title + meta description)
- [x] 1.1.5 Drop "Brown Ajah" from `apps/web/src/routes/en/search.tsx` placeholder
- [x] 1.1.6 Drop "Brown Ajah member ↔ Tuatha Dé deity" from `apps/web/src/routes/en/key-competencies.tsx`
- [x] 1.1.7 Drop "Brown Ajah member" + "Brown Ajah theming" references from `apps/web/src/routes/en/key-competencies.$slug.tsx`
- [x] 1.1.8 Replace `<CiDragonBanner>` with `<CiSubnationFlag subnation="wales">` in `apps/web/src/routes/en/map.tsx`

### 1.2 — API + i18n

- [x] 1.2.1 Drop the 3 Brown Ajah / Amyrlin Seat comment lines from `apps/api/src/copilotkit/stage_router.ts`
- [x] 1.2.2 Replace "Aes Sedai — servants of all" / "Aes Sedai — freastalaithe ar gach duine" with "Cianfhoghlaim — Coláiste na Déisigh" in `packages/api/src/routers/i18n.ts`
- [x] 1.2.3 Drop the "Brown Ajah welcome banner" comment from `packages/i18n/src/index.ts`; replace the bilingual `tagline` keys with the professional tagline
- [x] 1.2.4 Drop the "Brown Ajah `KeyCompetencies` page renders" sentence from `packages/i18n/src/mastery.ts`

### 1.3 — Design tokens + ui components

- [x] 1.3.1 Drop the `--ci-brown-ajah` tokens from `docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css`; rename the 5 NCCA Key Competency comment
- [x] 1.3.2 Drop the "per the Brown Ajah theming" comments from `packages/ui/src/{progress-ring,skill-tree,boons-choice}.tsx`
- [x] 1.3.3 Drop the 5 `<Ci*>` lore component exports from `packages/ui/src/index.ts`
- [x] 1.3.4 DELETED `packages/ui/src/lore/{brown-ajah-badge,amyrlin-seat,dragon-banner,tuathan-wagon,cian-header}.tsx` (5 files)
- [x] 1.3.5 DELETED the now-empty `packages/ui/src/lore/` directory

### 1.4 — Tests + historical doc

- [x] 1.4.1 Rename `test_brown_ajah_theming_loaded` to `test_professional_theming_loaded` in `tests/test_heritage_convex.py`
- [x] 1.4.2 Update `docs/DEPLOY_STATUS.md` prose to rephrase as a 2026-07-02 historical snapshot with the 2026-07-09 removal noted

## Phase 2 — 6 per-subject BIEP web surfaces (T6 Step 2, 8 hours)

### 2.1 — Shared BIEP client lib

- [x] 2.1.1 Create `apps/web/src/lib/bi-ep.ts` with `BIEP_SUBJECTS[]`, `BIEP_SUBJECT_BY_SLUG`, `BIEP_SUBJECT_SLUGS`, `isBIEPSubject()`, `getBIEPSubject()`, `getGASlug()`, `getEnglishSlugFromGA()`
- [x] 2.1.2 Document the BAML / DLT / notebook / mo_sql engine / PEP 723 / ibis-first patterns per KCG

### 2.2 — Shared `<BIEPSubjectPage>` component

- [x] 2.2.1 Create `apps/web/src/components/BIEPSubjectPage.tsx` with the bilingual EN+GA renderer (subject header + 5×8 mastery matrix + pipeline integration cards + 5 BIEP visualisations + marimo notebook embed + 5 NCCA Key Competencies context)

### 2.3 — 6 EN concrete TanStack Start routes

- [x] 2.3.1 Create `apps/web/src/routes/en/subjects/mathematics.tsx`
- [x] 2.3.2 Create `apps/web/src/routes/en/subjects/chemistry.tsx`
- [x] 2.3.3 Create `apps/web/src/routes/en/subjects/geography.tsx`
- [x] 2.3.4 Create `apps/web/src/routes/en/subjects/gaeilge.tsx`
- [x] 2.3.5 Create `apps/web/src/routes/en/subjects/english.tsx`
- [x] 2.3.6 Create `apps/web/src/routes/en/subjects/computer_science.tsx`

### 2.4 — 6 GA Irish mirror routes

- [x] 2.4.1 Create `apps/web/src/routes/ga/subjects/mata.tsx`
- [x] 2.4.2 Create `apps/web/src/routes/ga/subjects/ceimic.tsx`
- [x] 2.4.3 Create `apps/web/src/routes/ga/subjects/tireolaiocht.tsx`
- [x] 2.4.4 Create `apps/web/src/routes/ga/subjects/gaeilge.tsx`
- [x] 2.4.5 Create `apps/web/src/routes/ga/subjects/bearla.tsx`
- [x] 2.4.6 Create `apps/web/src/routes/ga/subjects/riomheolaiocht.tsx`

### 2.5 — Test route registry coverage

- [x] 2.5.1 Update `tests/test_route_registry.py` with `EXPECTED_BIEP_EN_ROUTES` + `EXPECTED_BIEP_GA_ROUTES` + the updated `EXPECTED_ROUTE_COUNT`

### 2.6 — Regenerated routeTree.gen.ts

- [x] 2.6.1 Run `bunx @tanstack/router-cli generate` to regenerate the auto-generated `routeTree.gen.ts` with the 12 new concrete routes
- [x] 2.6.2 Verify all 6 BIEP EN routes + 6 GA mirrors + the dynamic `/en/subjects/$subject` are registered

## Phase 3 — Hono API endpoints (T6 Step 3, 2 hours)

- [x] 3.1 Create `apps/api/src/routers/bi-ep-subjects.ts` (Hono router) with 7 routes:
  - `GET /api/bi-ep-subjects/` (manifest)
  - `GET /api/bi-ep-subjects/manifest` (lite manifest)
  - `GET /api/bi-ep-subjects/:slug` (single subject)
  - `GET /api/bi-ep-subjects/:slug/syllabus`
  - `GET /api/bi-ep-subjects/:slug/papers`
  - `GET /api/bi-ep-subjects/:slug/marking-schemes`
  - `GET /api/bi-ep-subjects/:slug/topics`
- [x] 3.2 Mount the router at `/api/bi-ep-subjects` in `apps/api/src/index.ts`

## Phase 4 — /en/about + /ga/about mirror pages (T6 Step 4, 1 hour)

- [x] 4.1 Rewrite `apps/web/src/routes/en/about.tsx` to a clean professional page (6 BIEP priority subjects + 5 NCCA Foundations + 6 subnations + open-source architecture stack)
- [x] 4.2 Create `apps/web/src/routes/ga/about.tsx` as the Irish mirror (dátheangach EN/GA)

## Phase 5 — openspec change (T6 Step 6)

- [x] 5.1 Create `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/` directory
- [x] 5.2 Write `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/proposal.md` (this file)
- [x] 5.3 Write `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/tasks.md` (this file)
- [x] 5.4 Write 3 spec delta files under `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/`
- [x] 5.5 `openspec validate 2026-07-09-biep-6-subject-web-surfaces-v1 --strict` passes

## Phase 6 — Commit + push (T6 Step 7)

- [ ] 6.1 Stage all 49 files (29 created + 15 edited + 5 deleted)
- [ ] 6.2 `git commit -m "feat(biep): T6 6-subject BIEP web surfaces + Brown Ajah cleanup"`
- [ ] 6.3 `git push origin pick-4-biep-v1`

## Acceptance

- `openspec validate 2026-07-09-biep-6-subject-web-surfaces-v1 --strict` passes
- `curl http://localhost:3082/en/subjects/mathematics` returns 200 with the BIEP subject card HTML
- `curl http://localhost:3082/ga/subjects/mata` returns 200 with the Irish mirror HTML
- `curl http://localhost:8787/api/bi-ep-subjects/manifest` returns JSON with the 6 BIEP subjects
- `ccc search "Brown Ajah"` in `cianfhoghlaim/web/` returns 0 matches
- `ccc search "Aes Sedai"` in `cianfhoghlaim/web/` returns 0 matches
- The Header does NOT show "Aes Sedai — servants of all" anywhere
- The Sidebar does NOT show "Theming=Brown Ajah"
