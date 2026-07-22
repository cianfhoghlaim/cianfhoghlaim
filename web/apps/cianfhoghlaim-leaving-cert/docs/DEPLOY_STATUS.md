# Cianfhoghlaim Leaving Cert — Dev Deploy Status (FINAL — historical snapshot)

> **Last updated:** 2026-07-02
> **Change:** [`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`](../../../../openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/)
> **openspec validate:** ✅ PASSES
> **Progress:** 130 / 206 tasks (63%)
> **Branch:** 27+ commits ahead of origin/main (local only)

> **Note (2026-07-09):** The WoT-flavored theming + the
> `"/en/brown-ajah"` and `"/en/eiraic-treasures"` routes
> were removed in the subsequent
> `2026-07-09-remove-brown-ajah-theming-v1` change. This status file
> documents the state as of 2026-07-02; the live route inventory has
> since been trimmed to the 6 spec-required routes + 4 extras. The
> commit log below is preserved verbatim as a historical record of
> what was shipped up to that date.

---

## 🌐 Live URLs (running at 2026-07-02)

| Service | URL | Status |
|:--|:--|:--|
| **Web** | http://localhost:3082/ | ✅ 51 tested routes returned HTTP 200 |
| **API** | http://localhost:8787/ | ✅ 3 tested routes returned HTTP 200 |

---

## ✅ Tested web routes as of 2026-07-02 (51 routes — historical snapshot)

### Public landing + nav (13 routes)

| Route | Status (2026-07-02) |
|:--|:--|
| `/en/brown-ajah` | Removed 2026-07-09 (WoT theming cleanup) |
| `/en/diagrams` | The 4 diagram modes index |
| `/en/eiraic-treasures` | Removed 2026-07-09 (WoT theming cleanup) |
| `/en/key-competencies` | The 5×8 cross-subject mastery matrix |
| `/en/key-competencies/emblems` | Removed 2026-07-09 |
| `/en/lore-archive` | Removed 2026-07-09 (operator-only lore) |
| `/en/map` | The accurate British Isles map (6 subnations) |
| `/en/practice` | The practice session start page (subject + topic picker) |
| `/en/search` | The client-side search index |
| `/en/subjects` | The 8 NCCA subjects + 7 legacy compat |
| `/en/about` | The public about page |
| `/ga/about` | The Irish-language about page |
| `/ga/lore-archive` | Removed 2026-07-09 |

### Per-subject 6-section shell (18 routes — 3 subjects × 6 sections)

For each of `mathematics`, `gaeilge`, `chemistry`:
- `/en/leaving-cert/{subject}/syllabus` (concept-map + mastery matrix)
- `/en/leaving-cert/{subject}/past-exams` (heatmap + Sankey)
- `/en/leaving-cert/{subject}/marking-schemes` (PCLM flow)
- `/en/leaving-cert/{subject}/prioritisation` (ranked mastery)
- `/en/leaving-cert/{subject}/exam-tips` (time per question)
- `/en/leaving-cert/{subject}/pdf-library` (5 PDF resources)

### Detail pages (20 routes — historical snapshot)

- 5 NCCA Key Competencies: `/en/key-competencies/{slug}` (5 pages)
- 13 éraic treasures: `/en/eiraic-treasures/{tier}` (13 pages, removed 2026-07-09)
- 8 lore members: `/en/brown-ajah/{member}` (8 pages, removed 2026-07-09)
- 15 NCCA subjects: `/en/leaving-cert/{subject}` + `/ga/leaving-cert/{subject}` (15 EN + 15 GA = 30 pages)
- 1 practice detail: `/en/leaving-cert/{subject}/practice/{topic}` (3 subjects tested)

### API (3 routes — historical snapshot)

| Route | What it returns |
|:--|:--|
| `GET /` | "OK" (health check) |
| `GET /api/copilotkit/health` | `{"status":"ok","actions_registered":14,"action_names":[...]}` |
| `GET /api/subjects` | `{"status":"ok","count":0,"agents":[]}` (count 0 because the cross-language Python import falls through to the .catch() stub) |

---

## 📊 27+ commits in the change (historical snapshot)

```
386753b7c add /en/search (client-side search index)
8d50a6724 add /ga/lore-archive (the Irish mirror) — REMOVED 2026-07-09
b5c95a5f1 add /en/lore-archive (the 7 lineage clippings summary) — REMOVED 2026-07-09
788d0fa40 ship the 3D+2D asset gallery page
ec7d64e2d ship the practice detail page
4e4663a63 implement the full 6-section shell per subject
a2fc08185 add /en/practice index page (subject + topic picker)
341b944b9 add /en/diagrams index page (4 diagram modes)
c87478874 add /en/subjects index page (8 NCCA + 7 legacy compat)
cd857149d add /en/brown-ajah/{member} detail pages (8 members) — REMOVED 2026-07-09
8b4b7b604 add /ga/eiraic-treasures/{tier} detail pages (13 tiers GA) — REMOVED 2026-07-09
41ee6408a add /en/eiraic-treasures/{tier} detail pages (13 tiers) — REMOVED 2026-07-09
10e37708a add /en/key-competencies/{slug} detail pages (5 NCCA Key Competencies)
326822dc6 add /en/brown-ajah (the 8 lore members + Trí Dé Dána) — REMOVED 2026-07-09
bf3d38054 add /en/key-competencies/emblems + /ga/leaving-cert/{subject} + .gitignore — emblems REMOVED
87462a971 add /en/eiraic-treasures + /ga/eiraic-treasures + register 2 more routes — REMOVED 2026-07-09
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
7bd9c7175 ship Phase 9 (root PDFs) + Phase 12 (WoT theming) + 10 Ci components + 5 lore/map components + 3 routes — WoT theming REMOVED 2026-07-09
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
curl http://localhost:3082/en/about
curl http://localhost:8787/api/copilotkit/health
```

## 🚧 What did NOT work yet as of 2026-07-02

These are the 76 remaining tasks across 12 phases of the 206-subtask plan (historical snapshot):

### Blocked by external provisioning
- ⏳ **Convex `conic-leaving-cert` deployment** (Phase 1 T1.6/T1.7)
- ⏳ **Cloudflare Pages project** (Phase 1 T1.7)
- ⏳ **Pocket ID OIDC instance** (Phase 2 T2.3)

### Blocked by TanStack Start migration
- ⏳ **The per-section TanStack Start route** (the file-based router for the per-subject routes)
- ⏳ **The 3D asset gallery TanStack Start route**

### Blocked by Convex
- ⏳ **Real Convex queries** — `practice_attempts` + `badge_ledger` need the actual deployment
- ⏳ **Real /api/subjects response** — currently 0 because of the cross-language Python import

### Blocked by asset generation
- ⏳ **3D meshes** (Phase 7) — TRELLIS.2 + SAM-3D-Objects + R2 upload
- ⏳ **2D sprite atlases** (Phase 7) — FIBO

### Blocked by validation
- ⏳ **Full cross-workspace Convex tests** (Phase 8)
- ⏳ **Post-launch Wayback snapshot** (Phase 8 T8.8)

### Blocked by user environment
- ⏳ **`uv sync` blocked by `outlines-core==0.1.26` Rust build failure** (pre-existing, unrelated to this change)