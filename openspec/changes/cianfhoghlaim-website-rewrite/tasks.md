# Tasks: cianfhoghlaim-website-rewrite

> 4 phases × 27 tasks. Sequential within phase (each phase is a logical
> step); parallelisable ACROSS phases (e.g. Phase B frontend + Phase C
> backend can be developed in parallel after Phase A completes).

## Phase 0 — OpenSpec + A2UI setup (4 tasks, ~30 min)

- [ ] 0.1 Update `openspec/project.md` to register the new `cianfhoghlaim-website-rewrite` spec
- [ ] 0.2 Add `@copilotkit/a2ui-renderer` to `apps/web/package.json` (per the `a2ui-renderer` skill)
- [ ] 0.3 Document the 6 content types (Subjects / Practice / Past Papers / Marking Schemes / Foundations / Notebooks) in `apps/web/src/lib/content-types.ts`
- [ ] 0.4 Update the cianfhoghlaim BAML client in `baml_src/client.baml` to add the 6 content types as BAML functions

## Phase A — Foundation (4 tasks, 1 day)

- [ ] A.1 Extend the 8 `baml_src/education/subjects/qpack_*.baml` to add the 6 content type outputs (Subject, PastPaper, MarkingScheme, PracticeItem, Foundation, Notebook) — BAML contracts
- [ ] A.2 Extend `dlt/british_isles/ireland/ncca_root_pdfs.py` to add the `content_types` dimension + sync to MotherDuck
- [ ] A.3 Extend `cocoindex/cross_subject_competency_embedding.py` to include the `content_types` dimension in the LanceDB table `oideachais.lc.cross_subject.competencies`
- [ ] A.4 Add the 5 NCCA root-level PDFs to Cloudflare R2 via `scripts/upload-pdfs-to-r2.ts` (one-shot)

## Phase B — Frontend (12 tasks, 2-3 days)

- [ ] B.1 Rebuild `/index` with the 4 entry points (Student / Teacher / Family / School) — Khan-style hero
- [ ] B.2 Rebuild `/en/subjects` with the 8-card grid + category/difficulty/tags filters (iximiuz-style)
- [ ] B.3 Rebuild `/en/subjects/:subject` with the new 5-tab layout (BAML-driven: Syllabus / Papers / Marking / Practice / Notebook)
- [ ] B.4 Add `/en/subjects/:subject/syllabus` (BAML ExtractLeavingCertSyllabus + 5×8 mastery matrix)
- [ ] B.5 Add `/en/subjects/:subject/papers` (dlt-driven from CF R2, 2017-2025)
- [ ] B.6 Add `/en/subjects/:subject/marking` (BAML ExtractMarkingScheme)
- [ ] B.7 Add `/en/subjects/:subject/practice` (CopilotKit chat + BAML ScoreFormativeResponse)
- [ ] B.8 Add `/en/subjects/:subject/notebook` (embedded marimo from `notebooks/leaving_cert/{subject}.py`)
- [ ] B.9 Rebuild `/en/foundations` index + 5 detail pages (BAML ExtractKeyCompetencies + ExtractSCProgramme + ExtractSCRAdvisory + ExtractOnlineLearning + ExtractOnlineCertification)
- [ ] B.10 Rebuild `/en/agents` index + 9 detail pages (with per-subject CopilotKit chat)
- [ ] B.11 Add `/en/playgrounds` (per-subject sandboxes — match iximiuz Labs)
- [ ] B.12 Add `/en/diagrams` index (the 4 diagram modes: concept-map + heatmap + PCLM flow + sankey)

## Phase C — Backend (7 tasks, 1 day)

- [ ] C.1 Add Cloudflare Worker for the API (replaces the dev Hono server) at `apps/api/wrangler.toml`
- [ ] C.2 Add Cloudflare R2 bucket bindings to `wrangler.toml` for the 5 NCCA root-level PDFs + 8 subject PDF folders
- [ ] C.3 Wire `better-auth` v1.4 + Pocket ID OIDC for production auth at `apps/web/src/lib/auth.ts`
- [ ] C.4 Add Convex mutations: form submission + chat messages + mastery updates + diagram cache (at `apps/web/convex/`)
- [ ] C.5 Wire the global CopilotKit chat panel (visible on every page) — the cianfhoghlaim operator agent at `apps/web/src/components/chat/GlobalChat.tsx`
- [ ] C.6 Wire the per-subject CopilotKit chat — the 8 NCCA subject agents at `apps/web/src/components/chat/SubjectChat.tsx`
- [ ] C.7 Apply the `a2ui-renderer` skill to all 9 agent chat surfaces (render A2UI components from agent responses)

## Phase D — Polish (4 tasks, 0.5 day)

- [ ] D.1 Add `/en/playgrounds/:slug` for each subject's marimo notebook embed (match iximiuz Labs "Provisioned in seconds")
- [ ] D.2 Add `/en/about` rewrite (operator-only + public-facing summary + the 4 entry points)
- [ ] D.3 Update `README.md` + `apps/cianfhoghlaim-leaving-cert/docs/SELF-HOST.md` (the 3-step install works in 5 minutes)
- [ ] D.4 Update openspec change artefacts: cianfhoghlaim-website-rewrite/proposal.md + tasks.md + the new spec

## Archive

- [ ] After deploy + Wayback snapshot: `openspec archive cianfhoghlaim-website-rewrite --yes`