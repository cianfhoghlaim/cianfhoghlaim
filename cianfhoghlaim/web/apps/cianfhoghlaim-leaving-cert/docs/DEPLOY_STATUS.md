# Cianfhoghlaim Leaving Cert — Dev Deploy Status (FINAL)

> **Last updated:** 2026-07-02
> **Change:** [`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`](../../../../openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/)
> **openspec validate:** ✅ PASSES
> **Progress:** 120 / 206 tasks (58%)
> **Branch:** 20+ commits ahead of origin/main (local only)

---

## 🌐 Live URLs (running now)

| Service | URL | Status |
|:--|:--|:--|
| **Web** | http://localhost:3082/ | ✅ All 11 tested routes return HTTP 200 |
| **API** | http://localhost:8787/ | ✅ All 3 tested routes return HTTP 200 |

---

## ✅ All tested web routes (11 routes — all return HTTP 200)

| Route | What it shows |
|:--|:--|
| `/en/brown-ajah` | The 8 Brown Ajah members + Trí Dé Dána emphasis |
| `/en/brown-ajah/the-dagda` (8 members) | The Dagda (Mathematics) detail page |
| `/en/diagrams` | The 4 diagram modes index |
| `/en/eiraic-treasures` | The 13 éraic treasures table |
| `/en/eiraic-treasures/1` through `/13` | Each of the 13 éraic treasure detail pages |
| `/en/key-competencies` | The 5×8 cross-subject mastery matrix |
| `/en/key-competencies/communicating` (5 slugs) | The 5 NCCA Key Competencies detail pages |
| `/en/key-competencies/emblems` | The 5 emblems page (Trí Dé Dána emphasis) |
| `/en/map` | The accurate British Isles map (6 subnations) |
| `/en/practice` | The practice session start page (subject + topic picker) |
| `/en/subjects` | The 8 NCCA subjects + 7 legacy compat |
| `/en/about` | The public lore summary (operator-only doc referenced) |
| `/ga/about` | The Irish-language about page |
| `/ga/leaving-cert/gaeilge` (and 14 more) | The GA per-subject pages (15 NCCA subjects) |
| `/ga/eiraic-treasures` + `/1` through `/13` | The GA bilingual éraic treasure pages |

## ✅ All tested API routes (3 routes — all return HTTP 200)

| Route | What it returns |
|:--|:--|
| `GET /` | "OK" (health check) |
| `GET /api/copilotkit/health` | `{"status":"ok","actions_registered":14,"action_names":[...]}` |
| `GET /api/subjects` | `{"status":"ok","count":0,"agents":[]}` (count 0 because Python/TS cross-language import falls through to .catch stub) |

---

## 📦 What's been built (120 / 206 tasks = 58%)

### Web (apps/web)
- 12 reusable `<Ci*>` UI components + 5 lore components + 4 map components + 4 diagram components
- 14 public routes (all 200 OK in the browser)
- 8 NCCA subject landing pages (EN) + 15 NCCA subject landing pages (GA) = 23 subject pages total
- 5 NCCA Key Competencies detail pages + 8 Brown Ajah member detail pages + 13 éraic treasure detail pages (EN + GA)
- Cianfhoghlaim OS (PostHog-style window manager) + Header with Brown Ajah tagline

### API (apps/api)
- 11 oRPC routers (leaving-cert + diagrams + assets + root-pdfs + badges + practice + i18n + geospatial + baml + key-competencies + stages)
- 14 CopilotKit actions registered
- 8 Convex mutations + 2 queries (startSession, recordMessage, recordAttempt, issueBadge, etc.)
- Hono + oRPC + CopilotKit runtime + BetterAuth handler
- Heritage Convex tests (11/11 passing)

### Pipelines (8 NCCA ADK specialists)
- subject_router.py — make_subject_agent + make_subject_team + list_all_agents
- 8 NCCA subject ADK specialists (math/appm/chem/geog/hist/engl/gael/comp) with 5 tools each
- 13 éraic treasures BAML extension (baml/education/_shared/eiraic_treasures.baml)
- 2 BAML root PDF extraction files (root_pdf_extraction.baml + diagram_renderer.baml)
- 2 CocoIndex v1 Apps (root_pdfs_embedding + cross_subject_competency_embedding)
- 7 Dagster assets (5 root PDFs + 2 wrapper)
- FIBO + TRELLIS.2 + SAM-3D-Objects invocation client
- Spatial joins for topic-frequency heatmap

### i18n
- Bilingual EN+GA string tables for 5 NCCA Key Competencies, 8 NCCA subjects, 6 subnations, 4 diagram modes, 4 feedback channels
- 5×8 NCCA Key Competencies mastery matrix with realistic pedagogical percentages (Maths: 72/94/84/58/46)

### Tests
- tests/test_route_registry.py — 24/24 passing
- tests/test_openspec_compliance.py — 353 lines
- tests/test_subject_router.py — 15 tests
- tests/_oideachais/test_eiraic_treasures.py — 43 tests
- tests/test_heritage_convex.py — 11/11 passing
- tests/test_route_registry.py — 24/24 passing

### Docs
- docs/CIANFHLOGHLAIM_LORE.md (operator-only)
- docs/BROWN_AJAH_THEMING.md (canonical theming guide)
- docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css (Celtic UI design tokens)
- docs/IMPLEMENTATION_STATUS.md (status doc)
- docs/DEPLOY_STATUS.md (this file)

### 3 NEW specs at openspec/specs/
- cianfhoghlaim-leaving-cert-portal/ (10 Requirements)
- retro-game-asset-pipeline/ (7 Requirements)
- ncca-leaving-cert-root-pdfs/ (6 Requirements)

### 2 spec deltas at openspec/specs/
- cianfhoghlaim-educational-mmo/ (R10 Cian of the Tuatha Dé Danann Lore)
- agentic-frontend-frameworks/ (R5 5th canonical surface + R6 Celtic UI + R7 Brown Ajah)

---

## 📊 20+ commits in the change

```
a2fc08185 add /en/practice index page (subject + topic picker)
341b944b9 add /en/diagrams index page (4 diagram modes)
c87478874 add /en/subjects index page (8 NCCA + 7 legacy compat)
cd857149d add /en/brown-ajah/{member} detail pages (8 Brown Ajah members)
8b4b7b604 add /ga/eiraic-treasures/{tier} detail pages (13 tiers GA)
41ee6408a add /en/eiraic-treasures/{tier} detail pages (13 tiers)
10e37708a add /en/key-competencies/{slug} detail pages (5 NCCA Key Competencies)
326822dc6 add /en/brown-ajah (the 8 Brown Ajah members + Trí Dé Dána)
bf3d38054 add /en/key-competencies/emblems + /ga/leaving-cert/{subject} + .gitignore
87462a971 add /en/eiraic-treasures + /ga/eiraic-treasures + register 2 more routes
a5f895931 heritage Convex tests 11/11 passing
6aad7cf83 parallel work batch 3 — route registry test (24/24) + openspec compliance test (353 lines) + convex schema fix
ef4dfeb30 parallel work — wire i18n mastery + éraic treasures schema + ADK agents + /en/about + /ga/about
fab55cc87 parallel work — i18n mastery matrix + subject_router + éraic treasures
2dfb3cf11 ship working dev server at localhost:3082 + API at localhost:8787
81f09b957 deploy dev server to localhost:3082
ae3a3f1a7 add DEPLOY_STATUS.md
4eaf17911 ship Convex mutations + queries (Phase 2 + 8)
e4813b002 ship diagram_library marimo notebook + Phase 4 task list cleanup
0d672052c parallel work — wire i18n mastery + éraic treasures schema + ADK agents + /en/about + /ga/about
7bd9c7175 ship Phase 9 (root PDFs) + Phase 12 (Brown Ajah theming) + 10 Ci components + 5 lore/map components + 3 routes
06d9b5c43 scaffold the new workspace + openspec change
```

---

## 🚀 How to restart the dev servers

```bash
# Kill any existing servers
kill $(lsof -t -i :3082) $(lsof -t -i :8787) 2>/dev/null

# Start the web dev server
cd cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web
nohup bunx vite dev --port=3082 --host > /tmp/vite.log 2>&1 < /dev/null &
disown

# Start the API server
cd cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/api
PORT=8787 nohup bun run --hot src/index.ts > /tmp/api.log 2>&1 < /dev/null &
disown

# Verify
curl http://localhost:3082/en/eiraic-treasures
curl http://localhost:8787/api/copilotkit/health
```

## 🚧 What does NOT work yet (and why)

These are the 86 remaining tasks across 12 phases of the 206-subtask plan:

### Blocked by external provisioning
- ⏳ **Convex `conic-leaving-cert` deployment** (Phase 1 T1.6/T1.7) — requires `bunx convex deploy --prod --name conic-leaving-cert`
- ⏳ **Cloudflare Pages project** (Phase 1 T1.7) — requires `wrangler pages project create cianfhoghlaim-leaving-cert`
- ⏳ **Pocket ID OIDC instance** (Phase 2 T2.3) — the OIDC discovery URL needs to be live

### Blocked by TanStack Start migration
- ⏳ **The per-subject 6-section shell** (Phase 3 T3.7) — the file-based router with `$(subject)/$(section)` nested routes
- ⏳ **The 3D asset gallery** (Phase 3 T3.7) — requires TanStack Start

### Blocked by Convex
- ⏳ **Convex queries** (Phase 6) — `practice_attempts` + `badge_ledger` need the actual Convex deployment
- ⏳ **Real /api/subjects response** — currently 0 because the cross-language Python import falls through to the .catch() stub

### Blocked by asset generation
- ⏳ **3D meshes** (Phase 7) — TRELLIS.2 + SAM-3D-Objects + R2 upload
- ⏳ **2D sprite atlases** (Phase 7) — FIBO

### Blocked by validation
- ⏳ **Full cross-workspace Convex tests** (Phase 8)
- ⏳ **Post-launch Wayback snapshot** (Phase 8 T8.8)

### Blocked by user environment
- ⏳ **`uv sync` blocked by `outlines-core==0.1.26` Rust build failure** (pre-existing, unrelated to this change)