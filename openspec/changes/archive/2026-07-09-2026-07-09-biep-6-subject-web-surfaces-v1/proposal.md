# Change: 2026-07-09-biep-6-subject-web-surfaces-v1

## Why

T2 (`9e97ba0ca`) shipped the British-Isles Education Pipeline (BIEP) v1
end-to-end pipelines (NCCA + SEC + gov.ie + BAML + 6 marimo notebooks +
42 Dagster assets + 4 MotherDuck Dives) for the 6 priority subjects
(Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science).
The 6 per-subject marimo notebooks live at
`cianfhoghlaim/notebooks/03_leaving_cert/18..23_*_biep_v1.py`.

But the **public web surface** of `cianfhoghlaim-leaving-cert` (the
5th surface per `agentic-frontend-frameworks/spec.md` R5) still only
renders the dynamic `/en/subjects/$subject` route for all 8 NCCA
subjects and a single per-subject landing. The 6 BIEP subjects each need
a concrete, BIEP-aware landing page that surfaces:

- The NCCA subject card (from
  `cianfhoghlaim/baml/education/lc_extraction/curriculum_syllabus.baml`)
- The live marimo embed of the corresponding per-subject BIEP notebook
- The 5 BIEP visualisations per subject (topic frequency, exam paper
  difficulty, marking scheme complexity, cross-linguistic mapping,
  asset generator)
- The 5×8 mastery matrix (per-subject row + cross-subject column view)
- The bilingual EN + GA toggle (with the Irish-language mirror at
  `/ga/subjects/{mata,ceimic,tireolaiocht,gaeilge,bearla,riomheolaiocht}`)

Plus, the user's Brown Ajah / WoT theming cleanup landed in `52b61a9b5`
(removing R6 / R7 / R10 references in 3 active specs), but the
**component code** of the same web app — the surface area of openspec —
still carries 55+ Brown Ajah / Aes Sedai / Amyrlin / Tuatha'an / WoT
references in:
- 7 component files (`Header.tsx`, `Sidebar.tsx`, `CianfhoghlaimOS.tsx`,
  `search.tsx`, `key-competencies.tsx`, `key-competencies.$slug.tsx`,
  `map.tsx`)
- 5 lore widgets (`packages/ui/src/lore/*` — `CiBrownAjahBadge`,
  `CiAmyrlinSeat`, `CiDragonBanner`, `CiTuathanWagon`, `CiCianHeader`)
- 2 i18n packages (`packages/i18n/src/index.ts`,
  `packages/i18n/src/mastery.ts`)
- 3 design tokens files
  (`docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css`,
  `apps/api/src/copilotkit/stage_router.ts`,
  `packages/api/src/routers/i18n.ts`)
- 1 historical doc (`docs/DEPLOY_STATUS.md`)
- 1 test (`tests/test_heritage_convex.py`)

The user said:
> "i dont want the brown ajah theming anymore ... remove that from openspec"

Per their preference, the mythology / historical-sources layer is
**deferred** to BIEP-v2; the public surface must be professional +
minimal. The accurate British Isles map (R7 of the agentic-frontend-frameworks
spec, kept) remains.

This change produces both:

1. **6 concrete BIEP per-subject web surfaces** (EN + GA mirrors = 12
   TanStack Start routes) under
   `apps/web/src/routes/en/subjects/{mathematics,chemistry,geography,gaeilge,english,computer_science}.tsx`
   + `apps/web/src/routes/ga/subjects/{mata,ceimic,tireolaiocht,gaeilge,bearla,riomheolaiocht}.tsx`.
   Each surfaces the per-subject BIEP notebook embed + 5 visualisations +
   the bilingual EN↔GA language toggle.

2. **The Brown Ajah / WoT theming cleanup** of all 12+ in-scope
   component, i18n, and design-token files. The 5 lore/ files are
   deleted and their exports removed from `packages/ui/src/index.ts`.
   The Header becomes a clean "C" letter-mark + the tagline
   "Cianfhoghlaim — Coláiste na Déisigh". The Sidebar shows
   `Theming=professional` (not `Theming=Brown Ajah`).

3. **The 6 Hono API endpoints** under
   `apps/api/src/routers/bi-ep-subjects.ts` for SPA hydration:
   `GET /api/bi-ep-subjects/` + `GET /api/bi-ep-subjects/manifest` +
   `GET /api/bi-ep-subjects/:slug` + `GET .../:slug/syllabus|papers|marking-schemes|topics`.

4. **The clean `/en/about` + `/ga/about` mirror pages** with the
   professional-theming tagline "Cianfhoghlaim — Coláiste na Déisigh"
   and the 6 priority BIEP subjects surfaced (no mythology overlay).

5. **The openspec spec delta** wiring all the above into the existing
   `agentic-frontend-frameworks`, `cianfhoghlaim-leaving-cert-portal`,
   + `british-isles-education-pipeline` spec files.

This is the `T6` tangent of the
`openspec/changes/2026-07-09-five-tangent-modernization/` plan
(previously the
`openspec/changes/2026-07-09-five-tangent-modernization/` engagement
shipped T1 + T2 + T3 + T4 + T5 in commits `52b90f054`, `9e97ba0ca`,
`678b1e4d9`, `0bf713c45`, `8c0e06682`).

## What changes

### A — 6 per-subject BIEP web surfaces (T6 Step 2)

For each of the 6 priority subjects
(`mathematics | chemistry | geography | gaeilge | english | computer_science`):

- A concrete TanStack Start route at
  `/en/subjects/{slug}.tsx` (and Irish mirror at
  `/ga/subjects/{ga_slug}.tsx`).
- A shared renderer at `apps/web/src/components/BIEPSubjectPage.tsx`
  that consumes `apps/web/src/lib/bi-ep.ts` (the typed BIEP client).
- Each route renders:
  - The NCCA subject card (code, level, éraic tier, primary agent)
  - The 5×8 mastery matrix row + the cross-subject 5-column context
  - The 5 BIEP visualisations (5 CiTextbookPanels, each tagged with
    the BAML function + the marimo cell id)
  - The live marimo embed (iframe at `/_notebooks/{slug}.html`)
  - The bilingual EN↔GA language toggle + cross-link to the mirror
- The 6 concrete routes take precedence over the existing dynamic
  `/en/subjects/$subject` for the 6 BIEP slugs;
  `applied_mathematics` + `history` continue to fall through to the
  dynamic fallback.

### B — 6 Hono API endpoints (T6 Step 3)

`apps/api/src/routers/bi-ep-subjects.ts` is a new Hono router mounted at
`/api/bi-ep-subjects` in `apps/api/src/index.ts`. It serves:
- `GET /api/bi-ep-subjects/` — the full 6-subject manifest
- `GET /api/bi-ep-subjects/manifest` — the lite manifest (slug + name_ga +
  en_route + ga_route + notebook + primary_agent + table)
- `GET /api/bi-ep-subjects/:slug` — single subject by slug
- `GET /api/bi-ep-subjects/:slug/syllabus` — the syllabus rows for the
  `(md:oideachais.leaving_cert.<slug>_syllabus)` table
- `GET /api/bi-ep-subjects/:slug/papers` — past exam questions for the
  `(md:oideachais.leaving_cert.<slug>_papers)` table
- `GET /api/bi-ep-subjects/:slug/marking-schemes` — marking scheme
  patterns for `(md:oideachais.leaving_cert.<slug>_marking_schemes)`
- `GET /api/bi-ep-subjects/:slug/topics` — extracted topic vectors for
  `(md:oideachais.leaving_cert.<slug>_topics)`

(The 4 `*_rows` arrays ship empty until the BIEP v1 Dagster assets
materialise; run `mise run dagster:oideachais` then materialize
`lc5_<subject>_extract` + `lc6_<subject>_marking_schemes` to populate.)

### C — Brown Ajah / WoT theming cleanup (T6 Step 1)

The public surface of `cianfhoghlaim-leaving-cert` is now professional +
minimal. The mythology / historical-sources layer is deferred to
BIEP-v2 per the user's preference.

12 files cleaned:
1. `apps/web/src/components/Header.tsx` — drop `<CiBrownAjahBadge>`
   import + drop `<CiTuathanWagon>` import + replace "Aes Sedai —
   servants of all" tagline with "Cianfhoghlaim — Coláiste na Déisigh"
2. `apps/web/src/components/Sidebar.tsx` — replace "Aes Sedai —
   servants of all" tagline with "Cianfhoghlaim — Coláiste na
   Déisigh"; replace `Theming=Brown Ajah` with `Theming=professional`
3. `apps/web/src/components/CianfhoghlaimOS.tsx` — drop "Brown Ajah
   member" reference from the comment
4. `apps/web/src/routes/__root.tsx` — replace `Cianfhoghlaim — Aes
   Sedai — servants of all` title + drop "Brown Ajah theming" from
   the meta description
5. `apps/web/src/routes/en/search.tsx` — drop "Brown Ajah" from the
   search placeholder
6. `apps/web/src/routes/en/key-competencies.tsx` — drop "Brown Ajah
   member ↔ Tuatha Dé deity" line
7. `apps/web/src/routes/en/key-competencies.$slug.tsx` — drop "★
   Brown Ajah member (per docs/BROWN_AJAH_THEMING.md)" + drop "via the
   Brown Ajah theming" sentence
8. `apps/web/src/routes/en/map.tsx` — replace `<CiDragonBanner>` with
   `<CiSubnationFlag subnation="wales">` (the Welsh flag stays, the
   WoT terminology goes)
9. `apps/api/src/copilotkit/stage_router.ts` — drop the 3 Brown Ajah
   / Amyrlin Seat comment lines
10. `packages/api/src/routers/i18n.ts` — replace "Aes Sedai — servants
    of all" / "Aes Sedai — freastalaithe ar gach duine" with the
    professional tagline
11. `packages/i18n/src/index.ts` — drop the "Brown Ajah welcome
    banner" comment; replace the bilingual EN+GA `tagline` keys with
    "Cianfhoghlaim — Coláiste na Déisigh"
12. `packages/i18n/src/mastery.ts` — drop the "Brown Ajah
    `KeyCompetencies` page renders" sentence
13. `docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css` — drop the `--ci-brown-ajah`
    tokens; rename the `--ci-competency-personal-effective` comment
14. `docs/DEPLOY_STATUS.md` — rephrased as a 2026-07-02 historical
    snapshot with the 2026-07-09 removal noted on each removed route
15. `tests/test_heritage_convex.py` — `test_brown_ajah_theming_loaded`
    renamed to `test_professional_theming_loaded` with a rephrased
    body
16. `packages/ui/src/{progress-ring,skill-tree,boons-choice}.tsx` —
    drop the "per the Brown Ajah theming" comments
17. `packages/ui/src/index.ts` — drop the 5 `<Ci*>` lore component
    exports (the corresponding `lore/*.tsx` files are deleted)
18. `packages/ui/src/lore/{brown-ajah-badge,amyrlin-seat,dragon-banner,
    tuathan-wagon,cian-header}.tsx` — DELETED (5 files)
19. `packages/ui/src/lore/` directory — DELETED (now empty)

### D — `/en/about` + `/ga/about` mirror pages (T6 Step 4)

`apps/web/src/routes/en/about.tsx` is rewritten to a clean professional
page (per the user's directive — the operator-only lore reference is
preserved in the matrix doc but the public surface mentions only the
6 BIEP priority subjects + the 5 NCCA Foundations + the 6 subnations +
the open-source architecture).

`apps/web/src/routes/ga/about.tsx` is created as the Irish mirror
(dátheangach EN/GA).

### E — openspec spec deltas

3 spec deltas:

#### E.1 — `agentic-frontend-frameworks/spec.md` — 1 ADDED Requirement

A new requirement (R-AGENTIC-BIEP-WS-1) is added to the
`agentic-frontend-frameworks` spec covering the 6 per-subject BIEP web
surfaces + the 6 Hono API endpoints + the professional-theming
palette. The R7 "Brown Ajah theming" reference was already removed by
`52b61a9b5`; the new requirement does NOT reintroduce it. The 4
canonical surfaces table is updated to add a 6th row for the BIEP web
surfaces (the 5th surface is the Cianfhoghlaim Leaving Cert surface
itself, and the new BIEP surfaces are subroutes of that surface).

#### E.2 — `cianfhoghlaim-leaving-cert-portal/spec.md` — 1 ADDED Requirement

A new requirement (R-LEAVING-CERT-BIEP-WS-1) is added to the
`cianfhoghlaim-leaving-cert-portal` spec covering the 6 concrete
per-subject routes (EN + GA mirrors) + the bilingual EN+GA toggle.

The R8 "Brown Ajah theming" reference was already removed by
`52b61a9b5`; the new requirement does NOT reintroduce it.

#### E.3 — `british-isles-education-pipeline/spec.md` — 1 MODIFIED Requirement

The existing R-LEAVING-CERT-BIEP-NOTEBOOK requirement is MODIFIED to
reference the new per-subject marimo embed surface
(`apps/web/src/routes/en/subjects/{slug}.tsx` → `/_notebooks/{slug}.html`).
The R-LEAVING-CERT-BIEP-NB-IBIS-FIRST still applies (marimo notebooks
default to the `bunchloch-infra` lakehouse via `ibis.duckdb.connect()` +
`ibis.lancedb.connect()`).

## What does NOT change

- 50+ archived openspec changes under `openspec/changes/archive/*`
- `docs/BROWN_AJAH_THEMING.md` + `docs/CIANFHLOGHLAIM_LORE.md` —
  referenced but never created on disk
- The BIEP v1 marimo notebooks at
  `cianfhoghlaim/notebooks/03_leaving_cert/18..23_*_biep_v1.py`
  (owned by T2 Phase 3+4)
- The 5 `<Ci*>` map components at `packages/ui/src/map/*`
  (British Isles accurate map — kept)
- The 12 `<Ci*>` professional components at `packages/ui/src/*`
- The Dark Ajah / AoL / sidenote content (per `openspec/specs/`
- The 4 priority Dives (`lc_syllabus_topics`, `lc_exam_difficulty`,
  `lc_marking_complexity`, `gov_circulars_archive`) — owned by the
  BIEP v1 spec
- The Dagster lc5/lc6 assets + the 7 v1 CocoIndex flows — owned by
  the BIEP v1 spec
- `openspec/changes/2026-07-09-five-tangent-modernization/` (the
  master plan) — no changes needed

## Files (29 created + 15 edited + 5 deleted = 49 files)

### Created (29)

- `apps/web/src/lib/bi-ep.ts` (the BIEP client lib)
- `apps/web/src/components/BIEPSubjectPage.tsx` (shared renderer)
- `apps/web/src/routes/en/subjects/mathematics.tsx`
- `apps/web/src/routes/en/subjects/chemistry.tsx`
- `apps/web/src/routes/en/subjects/geography.tsx`
- `apps/web/src/routes/en/subjects/gaeilge.tsx`
- `apps/web/src/routes/en/subjects/english.tsx`
- `apps/web/src/routes/en/subjects/computer_science.tsx`
- `apps/web/src/routes/ga/subjects/mata.tsx`
- `apps/web/src/routes/ga/subjects/ceimic.tsx`
- `apps/web/src/routes/ga/subjects/tireolaiocht.tsx`
- `apps/web/src/routes/ga/subjects/gaeilge.tsx`
- `apps/web/src/routes/ga/subjects/bearla.tsx`
- `apps/web/src/routes/ga/subjects/riomheolaiocht.tsx`
- `apps/web/src/routes/ga/about.tsx`
- `apps/api/src/routers/bi-ep-subjects.ts`
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/proposal.md` (this file)
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/tasks.md`
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/agentic-frontend-frameworks/spec.md`
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/cianfhoghlaim-leaving-cert-portal/spec.md`
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/british-isles-education-pipeline/spec.md`

(The regenerated routeTree.gen.ts and the 5 dropped `lore/*.tsx` files
are NOT counted here; the routeTree.gen.ts is auto-regenerated by the
TanStack router-plugin on the next build.)

### Edited (15)

- `apps/web/src/components/Header.tsx`
- `apps/web/src/components/Sidebar.tsx`
- `apps/web/src/components/CianfhoghlaimOS.tsx`
- `apps/web/src/routes/__root.tsx`
- `apps/web/src/routes/en/search.tsx`
- `apps/web/src/routes/en/key-competencies.tsx`
- `apps/web/src/routes/en/key-competencies.$slug.tsx`
- `apps/web/src/routes/en/map.tsx`
- `apps/web/src/routes/en/about.tsx`
- `apps/api/src/copilotkit/stage_router.ts`
- `apps/api/src/index.ts` (mounts the new `/api/bi-ep-subjects` router)
- `apps/api/src/routers/bi-ep-subjects.ts` — see "Created"
- `packages/api/src/routers/i18n.ts`
- `packages/i18n/src/index.ts`
- `packages/i18n/src/mastery.ts`
- `packages/ui/src/index.ts`
- `packages/ui/src/progress-ring.tsx`
- `packages/ui/src/skill-tree.tsx`
- `packages/ui/src/boons-choice.tsx`
- `docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css`
- `docs/DEPLOY_STATUS.md`
- `tests/test_heritage_convex.py`
- `tests/test_route_registry.py` (expanded to cover the 6 BIEP EN + 6 GA + 1 dynamic)

### Deleted (5)

- `packages/ui/src/lore/brown-ajah-badge.tsx`
- `packages/ui/src/lore/amyrlin-seat.tsx`
- `packages/ui/src/lore/dragon-banner.tsx`
- `packages/ui/src/lore/tuathan-wagon.tsx`
- `packages/ui/src/lore/cian-header.tsx`
- (and the empty `packages/ui/src/lore/` directory)

## New openspec change files (4 created)

- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/proposal.md` (this file)
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/tasks.md`
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/agentic-frontend-frameworks/spec.md` (1 ADDED Requirement)
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (1 ADDED Requirement)
- `openspec/changes/2026-07-09-biep-6-subject-web-surfaces-v1/specs/british-isles-education-pipeline/spec.md` (1 MODIFIED Requirement)

## Acceptance gates

- `openspec validate 2026-07-09-biep-6-subject-web-surfaces-v1 --strict` passes
- `marimo edit cianfhoghlaim/notebooks/03_leaving_cert/23_mathematics_biep_v1.py` renders (the per-subject BIEP notebook)
- `curl http://localhost:3082/en/subjects/mathematics` returns 200 with the BIEP subject card HTML
- `curl http://localhost:3082/ga/subjects/mata` returns 200 with the Irish mirror HTML
- `curl http://localhost:8787/api/bi-ep-subjects/manifest` returns JSON with the 6 BIEP subjects
- `ccc search "Brown Ajah"` in `cianfhoghlaim/web/` returns 0 matches (except the workbench vendored copy at `dlthub-ai-workbench/`)
- `ccc search "Aes Sedai"` in `cianfhoghlaim/web/` returns 0 matches
- The Header does NOT show "Aes Sedai — servants of all" anywhere
- The Sidebar does NOT show "Theming=Brown Ajah"

## Cross-references

- T2 (Phase 3+4): `openspec/changes/2026-07-06-british-isles-education-pipeline-v1/`
  + commit `9e97ba0ca` — wires NCCA + SEC + gov.ie + PDF + the 6 marimo notebooks
- T5 (cross-nation audit): `openspec/changes/2026-07-09-cross-nation-content-audit-v1/`
  + commit `8c0e06682` — 5 scaffolded DLT sources + audit doc
- The Brown Ajah cleanup (R6/R7/R10 removed): `openspec/changes/2026-07-09-remove-brown-ajah-theming-v1/`
  + commit `52b61a9b5`
- The 5-tangent plan: `docs/agents/five-tangent-modernization.md`
- The 6 BIEP subjects + the 5 visualisations per subject are
  documented in the BIEP v1 spec
  (`openspec/specs/british-isles-education-pipeline/spec.md`)
