# docs/web/ — Web Architecture Knowledge Base

Tuath/Cianfhoghlaim web technology reference library. Consolidated from 194 files (98 .md + 2 nested subdirs + various config) into 10 topical subdirs.

Last consolidated: 2026-06-14

---

## Subdirectory map

| Subdir | Topic | Files |
|---|---|---|
| [00-nav/](00-nav/) | Index, README, KMP-Swift bridge | 4 |
| [01-tanstack/](01-tanstack/) | TanStack Start, AI, DB, Router, Query | 15 |
| [02-betterauth/](02-betterauth/) | BetterAuth + adapter docs (Drizzle, Expo, Postgres, SIWE) | 6 |
| [03-ag-ui/](03-ag-ui/) | AG-UI protocol (Pydantic, CopilotKit, Kotlin SDK) | 5 |
| [04-alchemy/](04-alchemy/) | Alchemy IaC + Cloudflare examples | 4 |
| [05-convex/](05-convex/) | Convex backend (auth, self-hosted, RAG) | 5 |
| [06-effect/](06-effect/) | Effect-TS (incl. orpc integration research) | 4 |
| [07-react-frontend/](07-react-frontend/) | React/Next.js/Microfrontends/MCP-UI patterns | 15 |
| [08-repos/](08-repos/) | `repo-*.md` upstream summaries (ag-ui, convex, hono, orpc, restate, tanstack, cloudflare) | 8 |
| [09-clippings/](09-clippings/) | External articles (chrome-devtools-mcp, wgpu release) | 2 |
| [chrome-devtools-mcp/](chrome-devtools-mcp/) | Chrome DevTools MCP server docs (skeletonized upstream) | 14 |
| [tanmaxx-17/](tanmaxx-17/) | tanmaxx-17 platform skeleton (apps, packages) | 8 |

Total: 9 .md topical subdirs + 2 nested source-code subdirs = 11 dirs, ~90 .md.

---

## How to navigate

- **Starting from scratch** → read [00-nav/README.md](00-nav/README.md), [01-tanstack/Overview _ TanStack Start.md](01-tanstack/Overview%20_%20TanStack%20DB%20Docs.md), [05-convex/Playground _ Convex Developer Hub.md](05-convex/Playground%20_%20Convex%20Developer%20Hub.md)
- **Setting up auth** → [02-betterauth/](02-betterauth/) (6 files covering SIWE, Drizzle, Expo, Postgres, basic usage)
- **Building an agent UI** → [03-ag-ui/](03-ag-ui/) (5 files) + [01-tanstack/Integrating TanStack AI with LiteLLM.md](01-tanstack/Integrating%20TanStack%20AI%20with%20LiteLLM.md)
- **Comparing backends** → [05-convex/](05-convex/) + [01-tanstack/TanStack DB Integration and Comparison.md](01-tanstack/TanStack%20DB%20Integration%20and%20Comparison.md)
- **Looking for upstream summary** → [08-repos/](08-repos/) (8 `repo-*.md` files)
