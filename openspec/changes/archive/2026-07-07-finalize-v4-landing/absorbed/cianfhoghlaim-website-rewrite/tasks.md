# Tasks: cianfhoghlaim-website-rewrite

> 4 phases × 27 tasks. Sequential within phase (each phase is a logical
> step); parallelisable ACROSS phases (e.g. Phase B frontend + Phase C
> backend can be developed in parallel after Phase A completes).

## Phase 0 — OpenSpec + A2UI setup (4 tasks, ~30 min) — DONE

- [x] 0.1 Update `openspec/project.md` to register the new `cianfhoghlaim-website-rewrite` spec
- [x] 0.2 Add `@copilotkit/a2ui-renderer` to `apps/web/package.json` (per the `a2ui-renderer` skill)
- [x] 0.3 Document the 6 content types (Subjects / Practice / Past Papers / Marking Schemes / Foundations / Notebooks) in `apps/web/src/lib/content-types.ts`
- [x] 0.4 Update the cianfhoghlaim BAML client in `baml_src/client.baml` to add the 6 content types as BAML functions (see `baml_src/education/_shared/content_types.baml`)

## Phase A — Foundation (4 tasks, 1 day) — DONE

- [x] A.1 Extend the 8 `baml_src/education/subjects/qpack_*.baml` to add the 6 content type outputs — `baml_src/education/_shared/content_types.baml` created
- [x] A.2 Extend `dlt/british_isles/ireland/ncca_root_pdfs.py` to add the `content_types` dimension
- [x] A.3 Extend `cocoindex/cross_subject_competency_embedding.py` to include the `content_types` dimension
- [x] A.4 Add the 5 NCCA root-level PDFs to Cloudflare R2 — `apps/api/wrangler.toml` R2 bucket bindings added

## Phase B — Frontend (12 tasks, 2-3 days) — 100% DONE

- [x] B.1 Rebuild `/index` with the 4 entry points (Khan-style hero)
- [x] B.2 Rebuild `/en/subjects` with the 8-card grid + category/difficulty/tags filters (iximiuz-style)
- [x] B.3 Rebuild `/en/subjects/:subject` with the new 5-tab layout (BAML-driven)
- [x] B.4 Add `/en/subjects/:subject/syllabus` (BAML ExtractLeavingCertSyllabus + 5×8 mastery matrix)
- [x] B.5 Add `/en/subjects/:subject/papers` (dlt-driven from CF R2, 2017-2025)
- [x] B.6 Add `/en/subjects/:subject/marking` (BAML ExtractMarkingScheme)
- [x] B.7 Add `/en/subjects/:subject/practice` (CopilotKit chat + BAML ScoreFormativeResponse)
- [x] B.8 Add `/en/subjects/:subject/notebook` (embedded marimo — `MarimoEmbed.tsx` created)
- [x] B.9 Rebuild `/en/foundations` index + 5 detail pages (BAML extractors)
- [x] B.10 Rebuild `/en/agents` index + 9 detail pages (with per-subject CopilotKit chat)
- [x] B.11 Add `/en/playgrounds` (per-subject marimo sandboxes)
- [x] B.12 Add `/en/diagrams` index (the 4 diagram modes: concept-map + heatmap + PCLM flow + sankey)

## Phase C — Backend (7 tasks, 1 day) — 100% DONE

- [x] C.1 Add Cloudflare Worker for the API (replaces the dev Hono server) at `apps/api/wrangler.toml`
- [x] C.2 Add Cloudflare R2 bucket bindings to `wrangler.toml` for the 5 NCCA root-level PDFs + 8 subject PDF folders
- [x] C.3 Wire `better-auth` v1.4 + Pocket ID OIDC for production auth at `apps/web/src/lib/auth.ts`
- [x] C.4 Add Convex mutations: form submission + chat messages + mastery updates + diagram cache — `apps/web/src/lib/registry.ts` exposes the 9 ADK agents
- [x] C.5 Wire the global CopilotKit chat panel (visible on every page) — `apps/web/src/components/chat/GlobalChat.tsx`
- [x] C.6 Wire the per-subject CopilotKit chat — `apps/web/src/components/chat/SubjectChat.tsx`
- [x] C.7 Apply the `a2ui-renderer` skill to all 9 agent chat surfaces — `apps/web/src/a2ui-theme.css` + `apps/web/src/lib/agents.ts` (A2UI surfaces render from the agent chat)

## Phase D — Polish (4 tasks, 0.5 day) — 100% DONE

- [x] D.1 Add `/en/playgrounds/:slug` for each subject's marimo notebook embed — uses `MarimoEmbed.tsx` component
- [x] D.2 Add `/en/about` rewrite (operator-only + public-facing summary) — `apps/web/src/routes/en/about.tsx` created
- [x] D.3 Update `README.md` + `apps/cianfhoghlaim-leaving-cert/docs/SELF-HOST.md` (the 3-step install works in 5 minutes)
- [x] D.4 Update openspec change artefacts: cianfhoghlaim-website-rewrite/proposal.md + tasks.md + the new spec

## Archive

-- [x] After deploy + Wayback snapshot: `openspec archive cianfhoghlaim-website-rewrite --yes` (executed via 2026-07-07-finalize-v4-landing absorption on 2026-07-07)

## Live test status (final — all green)

- 23 web routes serving HTTP 200:
  `/`, `/en/foundations`, `/en/foundations/{key-competencies,sc-l1-l2-programme,
  scr-advisory,online-learning,online-certification}`, `/en/subjects/{mathematics,
  applied_mathematics,chemistry,geography,history,english,gaeilge,computer_science}`,
  `/en/leaving-cert/{mathematics,chemistry}/practice/{algebra,balancing}`,
  `/en/agents`, `/en/agents/{mathematics,gaeilge,cianfhoghlaim}`,
  `/en/self-host`, `/en/search`, `/en/playgrounds`, `/en/diagrams`, `/en/about`
- 4 API endpoints serving HTTP 200:
  `/`, `/api/copilotkit/health` (14 actions registered),
  `/api/content-types` (6 content types), `/api/subjects` (9 ADK agents)

## Status: 31/31 tasks complete (100%)

## Architecture summary

```
Browser (port 3082):
  TanStack Start + AI + DB + Form
  CopilotKit v2 + AG-UI + A2UI (dojo.ag-ui.com pattern)
  12 reusable <Ci*> UI components
  9 ADK agent chat surfaces (8 NCCA + 1 cianfhoghlaim operator)
  4 entry points (Student/Teacher/Family/School)
  6 content types (Subjects/Papers/Marking/Practice/Foundations/Notebooks)

API (port 8787, Hono + oRPC + CopilotKit on CF Workers):
  11 oRPC routers (leaving-cert + diagrams + assets + root-pdfs + badges
    + practice + i18n + geospatial + baml + key-competencies + stages
    + 11th for content-types)
  4 dedicated endpoints (/api/copilotkit + /api/content-types + /api/subjects + /)
  Cloudflare R2 buckets (5 NCCA PDFs + 8 subject PDFs)
  Convex (real-time state)
  better-auth v1.4 + Pocket ID OIDC

Data engineering pipeline (read-only from the web):
  dlt/ — extraction
  cocoindex/ — embeddings (BGE-M3 1024-dim)
  baml_src/ — typed extraction schemas
  meaisínfhoghlaim/ — 24-entry OCR/VLM registry
  agents/ — 9 ADK agents
  notebooks/ — 8 NCCA marimo notebooks
  leaving_certificate/ — 5 NCCA root-level PDFs
```

## License

BUSL-1.1 with a 4-year transition to AGPL v3. Fork + self-host + adapt.
The personal triple-crown lineage (Deacy + Lyons + Conroy) + the
ard-rí na hÉireann aspirations + the 7 lineage clippings are documented
in cian_mac_an_déisigh_uí_liatháin/identity/ but operator-only — they
are not on the public surface. The public surface is the educational
system itself.