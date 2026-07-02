# Cianfhoghlaim Leaving Cert — Dev Deploy Status

> **Last updated:** 2026-07-02
> **Change:** [`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`](../../../../openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/)
> **openspec validate:** ✅ PASSES

---

## 🌐 Live URLs (running now)

| Service | URL | Status |
|:--|:--|:--|
| **Web** (Vite SPA) | http://localhost:3082/ | ✅ Running |
| **API** (Hono) | http://localhost:8787/ | ✅ Running |
| **API Health** | http://localhost:8787/api/copilotkit/health | ✅ 14 actions registered |
| **RPC** | http://localhost:8787/rpc | ✅ 11 oRPC routers |
| **OpenAPI** | http://localhost:8787/api-reference | ✅ Schema docs |

Both servers are running in parallel via `nohup + disown` in detached background processes.

---

## 📋 What works in the browser

### Web (http://localhost:3082/)
- ✅ `/` — Landing page (6 subnations, Brown Ajah tagline)
- ✅ `/en/map` — Accurate British Isles map with 6 subnations + 5 NCCA Key Competencies land-marks
- ✅ `/en/key-competencies` — 5×8 cross-subject mastery matrix

The Brown Ajah russet-brown badge is rendered in the header. The "Aes Sedai — servants of all" tagline is visible. The bilingual left nav links to Curriculum / Map / Key Competencies.

### API (http://localhost:8787/)
- ✅ `GET /` — returns "OK" (health check)
- ✅ `GET /api/copilotkit/health` — returns:
  ```json
  {
    "status": "ok",
    "actions_registered": 14,
    "action_names": [
      "getSyllabusTopics",
      "listExamMaterials",
      "getMarkingSchemeSummary",
      "getTopicPrioritisation",
      "getExamLayoutTips",
      "openPdf",
      "generateConceptMap",
      "generateTopicHeatmap",
      "generatePCLMFlow",
      "generateQuestionSankey",
      "generate3DAsset",
      "listAssets",
      "lookupKeyCompetency",
      "lookupSCRCommentary"
    ]
  }
  ```
- ✅ `POST /api/copilotkit?stage=senior_cycle&subject=mathematics&language=en` — AG-UI SSE stream (stub returns welcome text)
- ✅ `POST /rpc/*` — oRPC RPC handler (11 routers mounted: leaving-cert + diagrams + assets + root-pdfs + badges + practice + i18n + geospatial + baml + key-competencies + stages)
- ✅ `POST /api/auth/*` — BetterAuth catch-all (with 32-char secret warning; needs `BETTER_AUTH_SECRET` env var for production)
- ✅ `GET /api-reference/*` — oRPC OpenAPI / Swagger docs

---

## 📸 Screenshots (captured)

- `docs/deploy-screenshot-1-index.png` — Landing page
- `docs/deploy-screenshot-2-map.png` — British Isles map page (the one that worked after SPA fallback fix)
- `docs/deploy-screenshot-3-map-404.png` — 404 screenshot (before SPA fallback fix)
- `docs/deploy-screenshot-final-map.png` — Final map page after fix
- `docs/screenshot-1-index.png` — Earlier landing page screenshot

---

## 🚧 What does NOT work yet (and why)

These are the 136 remaining tasks across 12 phases of the 206-subtask plan:

### Blocked by external provisioning
- ⏳ **Convex `conic-leaving-cert` deployment** (Phase 2 T1.6/T1.7) — requires `bunx convex deploy --prod --name conic-leaving-cert` against the Convex cloud
- ⏳ **Cloudflare Pages project** (Phase 1 T1.7) — requires `wrangler pages project create cianfhoghlaim-leaving-cert`
- ⏳ **Pocket ID OIDC instance** (Phase 2 T2.3) — the OIDC discovery URL needs to be live

### Blocked by TanStack Start migration
- ⏳ **The per-subject 6-section shell** (Phase 3 T3.7) — requires TanStack Start for the file-based router with `$(subject)/$(section)` nested routes
- ⏳ **The practice page** (Phase 3 T3.7) — requires TanStack Start
- ⏳ **The 3D asset gallery** (Phase 3 T3.7) — requires TanStack Start
- ⏳ **The CopilotKit chat** (Phase 5 T5.6) — the SSE stream works but the LLM backend (LiteLLM gateway) needs to be running

### Blocked by Convex
- ⏳ **Convex queries** (Phase 6) — `practice_attempts` + `badge_ledger` need the actual Convex deployment

### Blocked by asset generation
- ⏳ **3D meshes** (Phase 7) — TRELLIS.2 + SAM-3D-Objects + R2 upload
- ⏳ **2D sprite atlases** (Phase 7) — FIBO
- ⏳ **16 realm-celebration posters** (Phase 7) — FIBO

---

## 🎯 What was tested in the browser

The dev server is running at `http://localhost:3082`. The 3 routes that work without backend dependencies are:

1. **`/`** — Landing page (the 6 subnations of the British Isles — Éire highlighted as v1 active, the other 5 greyed out with "Coming soon" badges)
2. **`/en/map`** — The accurate British Isles map (SVG-rendered with the 6 subnations as coloured regions, the 5 NCCA Key Competencies as land-marks, the Connacht province detail panel, the Wales Dragon Banner)
3. **`/en/key-competencies`** — The 5×8 cross-subject mastery matrix (5 NCCA Key Competencies × 8 NCCA subjects, with the Trí Dé Dána emphasis + the Cian → Lugh + Tuatha Dé deity mappings)

The components rendered in the browser:
- The Brown Ajah russet-brown badge in the header
- The "Aes Sedai — servants of all" tagline (the Brown Ajah motto)
- The bilingual left nav (Curriculum / Map / Key Competencies)
- The CiTextbookPanel component (the material library frame)
- The CiSubnationFlag component (6 subnation flags)
- The CiLandmark component (5 NCCA Key Competencies land-marks)
- The CiProgressRing component (the Khan Academy 4-tier mastery)
- The ConnachtProvince component (the home base + Cian lineage highlights)
- The CiDragonBanner component (the Wales subnation flag)

---

## 🔜 Next deploy-blocking tasks

To go from "Vite SPA + Hono API in dev mode" to "production deploy on Cloudflare Pages":

1. **Phase 1 T1.6 — Convex provisioning:**
   ```bash
   bunx convex deploy --prod --name conic-leaving-cert
   ```

2. **Phase 1 T1.7 — Cloudflare Pages project:**
   ```bash
   wrangler pages project create cianfhoghlaim-leaving-cert
   ```

3. **Phase 1 T1.7 — TanStack Start migration** (the file-based router with virtual modules — to enable the per-subject routes)

4. **Phase 2 T2.3 — Pocket ID OIDC instance** for production auth

5. **Phase 2 T2.9 — `bun run typecheck` clean** for type validation

6. **Phase 8 T8.2 — `mise run lint:skills`** for the 123-skill lint check

7. **Phase 8 T8.6 — Retire oideachais-web** (per the user's explicit decision: "skip it will be retired it was a prototype")

8. **Phase 8 T8.8 — Public launch + Wayback snapshot**

---

## 📊 Commit history (this change)

12 commits on the `rewrite-cianfhoghlaim-leaving-cert-v2` change, 70 / 206 tasks done (34%):

```
2dfb3cf11 rewrite-cianfhoghlaim-leaving-cert-v2: ship working dev server at localhost:3082 + API at localhost:8787
81f09b957 rewrite-cianfhoghlaim-leaving-cert-v2: deploy dev server to localhost:3082
4eaf17911 rewrite-cianfhoghlaim-leaving-cert-v2: ship Convex mutations + queries (Phase 2 + 8)
e4813b002 rewrite-cianfhoghlaim-leaving-cert-v2: ship diagram_library marimo notebook + Phase 4 task list cleanup
0d672052c rewrite-cianfhoghlaim-leaving-cert-v2: ship subject_router fix + 2 oRPC routers (key_competencies + stages) + orpc client + auth client + FIBO/3D invoke + heritage assets + auth.config.ts + spatial_joins + heritage tests + cocoindex subject registry
ecd753b99 rewrite-cianfhoghlaim-leaving-cert-v2: ship 2 more oRPC routers (baml + geospatial) + IMPLEMENTATION_STATUS.md
666b36bd9 rewrite-cianfhoghlaim-leaving-cert-v2: ship subject_router + math_syllabus_lookup tool + project.md update + tasks.md cleanup
0724b6302 rewrite-cianfhoghlaim-leaving-cert-v2: ship 14 CopilotKit actions (Phase 5) + 6 marimo notebooks + Connacht province (Phase 12 T12.8 + T12.14)
55fa307b5 rewrite-cianfhoghlaim-leaving-cert-v2: ship oRPC routers (Phase 4 partial) + 3 packages + GA mirror + 2 dagster assets + 2 marimo notebooks
7bd9c7175 rewrite-cianfhoghlaim-leaving-cert-v2: ship Phase 9 (root PDFs) + Phase 12 (Brown Ajah theming) + 10 Ci components + 5 lore/map components + 3 routes
06d9b5c43 rewrite-cianfhoghlaim-leaving-cert-v2: scaffold the new workspace + openspec change
```

The branch is **12 commits ahead of origin/main** (local only).

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
curl -sS --max-time 5 -w "\nHTTP_STATUS:%{http_code}\n" http://localhost:3082/
curl -sS --max-time 5 -w "\nHTTP_STATUS:%{http_code}\n" http://localhost:8787/
curl -sS --max-time 5 http://localhost:8787/api/copilotkit/health
```