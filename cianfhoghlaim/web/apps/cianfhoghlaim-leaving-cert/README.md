# cianfhoghlaim Web App

> **cianfhoghlaim** — a self-hostable consolidation of Leaving
> Certificate education system resources. Anyone can `git clone` and run
> their own instance. Reduce barriers to education.

A progressive rewrite of the cianfhoghlaim website per
`openspec/changes/cianfhoghlaim-website-rewrite/`. The site is the
agentic tutorial for the cianfhoghlaim data engineering pipeline that
backs it — the 9 ADK agents (8 NCCA subject specialists + 1 cianfhoghlaim
operator) are wired to the dlt/ + cocoindex/ + baml_src/ + meaisínfhoghlaim/
pipeline.

## Stack

- **Frontend**: TanStack Start + Router + AI + DB + Form (per the latest tanstack packages)
- **Backend**: Hono + oRPC on Cloudflare Workers
- **Real-time**: Convex
- **Storage**: Cloudflare R2 (the 5 NCCA root-level PDFs + 8 subject PDF folders)
- **Auth**: better-auth v1.4 + Pocket ID OIDC
- **Agents**: CopilotKit v2 + AG-UI + A2UI (the dojo.ag-ui.com pattern)
- **Content types**: 6 (Subjects / Past Papers / Marking Schemes / Practice / Foundations / Notebooks)
- **Data engineering**: dlt + CocoIndex + baml_src + meaisínfhoghlaim + LanceDB + DuckLake/MotherDuck

## Local dev

```bash
cd cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert
bun install
bun run dev

# Web: http://localhost:3082
# API: http://localhost:8787
```

## Routes

### Public

- `/` — Khan-style 4 entry points (Student / Teacher / Family / School)
- `/en/foundations` — 5 NCCA root-level PDFs index
- `/en/foundations/:slug` — Each PDF detail page
- `/en/subjects/:subject` — Per-subject landing (5×8 mastery matrix + 5-tab layout)
- `/en/subjects/:subject/:section` — Per-section page (syllabus / papers / marking / practice / notebook)
- `/en/subjects/:subject/practice/:topic` — Per-subject practice (with SubjectChat + 3-way boon choice)
- `/en/agents` — 9 ADK agents index
- `/en/agents/:agent` — Per-agent detail (with pipeline integration)
- `/en/playgrounds` — Per-subject marimo sandboxes
- `/en/diagrams` — 4 diagram modes index
- `/en/self-host` — 3-step install guide
- `/en/search` — Client-side search index

### API

- `GET /` — Health check
- `GET /api/copilotkit/health` — CopilotKit runtime + actions
- `POST /api/copilotkit` — AG-UI SSE stream
- `GET /api/content-types` — 6 content types
- `GET /api/content-types/:type` — Single content type
- `GET /api/subjects` — 9 ADK agents metadata
- `GET /api/subjects/:subject` — Single ADK agent
- `POST /rpc/*` — oRPC RPC handler
- `GET /api-reference/*` — oRPC OpenAPI / Swagger
- `ANY /api/auth/*` — better-auth handler

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Browser (port 3082)                                          │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ TanStack Start (SSR + streaming + server functions)        ││
│  │ + TanStack AI + DB (reactive client store)                ││
│  │ + CopilotKit v2 + AG-UI + A2UI                            ││
│  │ + 12 reusable <Ci*> UI components                         ││
│  │ + 9 ADK agent chat surfaces (8 NCCA + 1 operator)        ││
│  │ + 4 entry points (Student/Teacher/Family/School)          ││
│  │ + 6 content types (Subjects/Papers/Marking/Practice/...) ││
│  └──────────────────────────────────────────────────────────┘│
│              ↑                ↑                                │
│              oRPC over /rpc    AG-UI over /api/copilotkit      │
└──────────────────────────────────────────────────────────────┘
              ↓                ↓
┌──────────────────────────────────────────────────────────────┐
│  API (port 8787, Hono + oRPC + CopilotKit on CF Workers)    │
│  + Cloudflare R2 (5 NCCA PDFs + 8 subject PDF folders)       │
│  + Convex (real-time state)                                    │
│  + better-auth v1.4 + Pocket ID OIDC                          │
└──────────────────────────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────────────────────────┐
│  Data engineering pipeline                                     │
│  + dlt/ (extraction)                                          │
│  + cocoindex/ (embeddings — BGE-M3 1024-dim)                  │
│  + baml_src/ (typed extraction schemas — 8 subjects + 6 types) │
│  + meaisínfhoghlaim/ (24-entry OCR/VLM registry)             │
│  + agents/tuatha/ (9 ADK agents — 8 NCCA + 1 operator)        │
│  + notebooks/leaving_cert/ (8 NCCA marimo notebooks)          │
│  + leaving_certificate/ (5 NCCA root-level PDFs)              │
└──────────────────────────────────────────────────────────────┘
```

## License

BUSL-1.1 with a 4-year transition to AGPL v3. Fork + self-host + adapt.