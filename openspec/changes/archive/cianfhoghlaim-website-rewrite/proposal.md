# cianfhoghlaim-website-rewrite — Progressive rewrite to a professional educational resource

## Why

The current cianfhoghlaim site (36 web routes + 1 API) is a working
prototype but has the wrong positioning: it reads as a "theme site" (the
rebranded-from-Cianfhoghlaim-OS surface) rather than an official
educational resource. The reference points — Khan Academy
(Khanmigo + mastery-based learning), iximiuz Labs (6 content types +
real sandboxes + per-content authors), and dojo.ag-ui.com (AG-UI +
A2UI live embedded demos) — are the template for the rewrite.

The unique angle: the cianfhoghlaim site IS the agentic tutorial for
the data engineering pipeline that backs it. The 9 ADK agents (8 NCCA
subject specialists + 1 cianfhoghlaim operator) are wired to the
dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/ pipeline. Visitors
can see the live pipeline by reading any subject page and clicking
into the agent chat.

## What

Progressive rewrite of the cianfhoghlaim website. Builds on the
existing 36 web routes + 1 API + 9 GA routes. Removes the previous
positioning. Adds 6 content types (Subjects / Practice / Past Papers /
Marking Schemes / Foundations / Notebooks) + 9 ADK agents + global +
per-subject CopilotKit chat with A2UI surface rendering + Cloudflare
Workers + R2 + Convex + better-auth v1.4 + Pocket ID OIDC.

The existing dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/
pipeline is the foundation. The rewrite is the surface.

## Impact

### Specs
- `openspec/specs/cianfhoghlaim-website-rewrite/spec.md` (NEW — 6
  Requirements for the 6 content types + 4 entry points + 9 ADK agents
  + A2UI surfaces + Cloudflare + auth)

### Files
- `openspec/changes/cianfhoghlaim-website-rewrite/proposal.md` (the
  full Why / What / Impact / Risks / Acceptance)
- `openspec/changes/cianfhoghlaim-website-rewrite/tasks.md` (27
  tasks across 4 phases)
- `openspec/changes/cianfhoghlaim-website-rewrite/specs/*` (4 spec
  deltas + 1 new spec)

### Code
- `web/apps/cianfhoghlaim-leaving-cert/` — all 36 web routes rebuilt
  with the new design system
- `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/registry.ts`
  (NEW — the 9 ADK agent registry)
- `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/agents.ts`
  (NEW — the 9 ADK agent definitions)
- `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/components/chat/`
  (NEW — the global + per-subject CopilotKit chat + A2UI)
- `web/apps/cianfhoghlaim-leaving-cert/apps/api/` — Cloudflare Workers
  API for the 8 subject endpoints
- `baml_src/education/_shared/content_types.baml` (NEW — the 6
  content types as BAML functions)
- `baml_src/education/subjects/qpack_*.baml` — extended with content
  type integrations
- `apps/api/src/copilotkit/` — global + per-subject chat with A2UI

### Refactors
- `baml_src/education/subjects/qpack_mathematics.baml` (and the 7
  others) — extended with the new content type outputs
- `cocoindex/cross_subject_competency_embedding.py` — extended with
  content_types dimension
- `dlt/british_isles/ireland/ncca_root_pdfs.py` — extended with
  content_types column

## Non-Goals

- No new subject content (8 NCCA subjects stay as-is)
- No new ADK agents (9 stay as-is — 8 NCCA + 1 cianfhoghlaim operator)
- No 14th éraic treasure or 6th NCCA Key Competency
- No new marimo notebooks (the 8 + root_pdfs + diagram_library stay)
- No new dlt sources (the 8 NCCA root-level PDFs + 8 subject folders
  stay as the source of truth)
- No rewrite of openspec/ (the cianfhoghlaim-website-rewrite change
  is additive to the existing rewrite-cianfhoghlaim-leaving-cert-v2
  change)

## Risks

- **R1 — Scope creep**: The progressive rewrite touches 36 web routes +
  the API + 9 agents. Mitigation: the 27 tasks are prioritised (Phase
  A = foundation, Phase B = frontend, Phase C = backend, Phase D = polish).
- **R2 — A2UI integration**: The CopilotKit v2 + a2ui-renderer skill is
  new. Mitigation: the per-subject chat is a thin wrapper around the
  existing `agents/{subject}_agent.py` + a new chat surface that emits
  A2UI operations.
- **R3 — Cloudflare Workers**: The API moves from Hono dev to CF Workers.
  Mitigation: the existing Hono server stays as the dev environment;
  the CF Worker is a thin deployment wrapper.
- **R4 — R2 data migration**: The 5 NCCA root-level PDFs + 8 subject
  PDF folders need to be uploaded to R2. Mitigation: a one-shot
  `pnpm run upload-pdfs-to-r2` script uploads from
  `leaving_certificate/`.
- **R5 — better-auth v1.4**: The auth stack is new. Mitigation: the
  existing 8 NCCA subject routes stay public; only the chat +
  progress-tracking endpoints require auth.

## Acceptance

- **A1**: All 8 NCCA subject pages render with the 5-tab layout
  (Syllabus / Papers / Marking / Practice / Notebook) + the 5×8 mastery
  matrix
- **A2**: The 9 ADK agents are wired to the chat surface with the
  per-subject + global chat pattern
- **A3**: The 5 NCCA root-level PDFs are indexed in LanceDB via CocoIndex
- **A4**: The 6 content types are exposed as BAML functions
- **A5**: A2UI surfaces render from the agent chat (matching the
  dojo.ag-ui.com pattern)
- **A6**: Cloudflare Workers + R2 + Convex + better-auth v1.4 are
  the deployment target
- **A7**: The self-host 3-step install works in 5 minutes (matching
  the iximiuz Labs "Provisioned in seconds" pattern)