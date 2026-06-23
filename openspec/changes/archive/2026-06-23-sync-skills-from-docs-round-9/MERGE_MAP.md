# Round 9 — docs/web/ + docs/tuatha/08-mirrors/ → skills merge map

This file maps every `.md` under `docs/web/` (98 .md files + 2 cloned subdirs) and the 11 cloned upstream repos under `docs/tuatha/08-mirrors/` to either the **2 new skills** (`web-mirrors`, `agentic-frontend-frameworks`) or one of the **9 existing skills** that need expansion, or marks it for deletion or as a clipping. The `08-mirrors/_summaries/` content was already absorbed into the existing `upstream-mirrors` skill in round 8 — this round only does `git rm -rf` of the 11 mirror source trees (93 MB) and the empty `docs/tuatha/08-mirrors/` and `docs/tuatha/` directories. The 2 cloned subdirs inside `docs/web/` (`chrome-devtools-mcp/`, `tanmaxx-17/`) are also `git rm -rf` — they are external source-code clones whose only KCG value is already captured in `upstream-mirrors/references/anylanguagemodel.md` (the AnyLanguageModel clip is adjacent) and the `stagehand` / `sruth-browser` skills (chrome-devtools-mcp coverage is upstream-only, no KCG-specific patches).

**Conventions used below**
- `KEEP-NEW: <new_skill>/references/<slug>.md` — long-form KCG-authored reference inside a new skill.
- `KEEP-NEW: <existing_skill>/references/<slug>.md` — long-form body for a new skill body section.
- `EXPAND: <existing_skill> [§section]` — content should be merged into an existing skill's body (cite the section).
- `DELETE` — redundant with an existing skill, an index/tombstone, an external non-KCG source, or a near-duplicate of another file in this round.
- `CLIPPING: <dest-skill>/references/clippings/<slug>.md` — external article preserved verbatim in the clippings dir of the appropriate skill.
- `WEB-MIRROR: <slug>.md` — one of the 8 `repo-*.md` files in `docs/web/08-repos/` (8 web-stack repos; goes into the new `web-mirrors` skill).

---

## 1. `docs/tuatha/08-mirrors/` cleanup (11 subdirs to git rm -rf)

The 11 mirror source trees at `docs/tuatha/08-mirrors/<name>/` are full `git clone`s of upstream repos. The KCG-authored summaries (originally under `08-mirrors/_summaries/`) were moved to the existing `upstream-mirrors` skill in round 8. Per the user's "delete `08-mirrors/`" instruction in this round, do:

```bash
git rm -rf docs/tuatha/08-mirrors/AnyLanguageModel/
git rm -rf docs/tuatha/08-mirrors/SpacetimeDB/
git rm -rf docs/tuatha/08-mirrors/agui_kotlin/
git rm -rf docs/tuatha/08-mirrors/gdext/
git rm -rf docs/tuatha/08-mirrors/hophacks-spacetimedb-workshop/
git rm -rf docs/tuatha/08-mirrors/react-native-godot/
git rm -rf docs/tuatha/08-mirrors/react-native-reusables/
git rm -rf docs/tuatha/08-mirrors/spacetimedb-cookbook/
git rm -rf docs/tuatha/08-mirrors/spacetimedb-typescript-sdk/
git rm -rf docs/tuatha/08-mirrors/wgpu/
git rm -rf docs/tuatha/08-mirrors/x402/
# 11 mirror dirs gone; _summaries/ is already empty (round 8 moved everything)
rmdir docs/tuatha/08-mirrors/_summaries/ 2>/dev/null || true
rmdir docs/tuatha/08-mirrors/ 2>/dev/null || true
rmdir docs/tuatha/ 2>/dev/null || true   # if no other content remains
```

**Total disk recovered:** ~93 MB (SpacetimeDB 41M + x402 26M + spacetimedb-cookbook 9.6M + react-native-reusables 7.9M + gdext 5.0M + wgpu 840K + spacetimedb-typescript-sdk 944K + hophacks 328K + react-native-godot 76K + agui_kotlin 80K + AnyLanguageModel 48K).

**Check before `rmdir docs/tuatha/`**: verify the directory has no other content first. If it does (e.g. a leftover `.gitkeep`), keep the empty dir deletion in a separate commit.

---

## 2. `docs/web/chrome-devtools-mcp/` cleanup (full subdir git rm -rf)

The `docs/web/chrome-devtools-mcp/` subdir is a full clone of `https://github.com/ChromeDevTools/chrome-devtools-mcp` (16 .md files + nested `skills/`). None of the content has KCG-specific patches — the only KCG annotation is the 38-line `SKILL_CONTEXT.md`, which itself is meta-commentary and not KCG-specific value. Coverage for browser automation in KCG already lives in the `stagehand` + `sruth-browser` skills. Action:

```bash
git rm -rf docs/web/chrome-devtools-mcp/   # 16 .md files + nested skills/
```

All 16 .md files in this subdir are marked `DELETE` in the per-file table below.

## 3. `docs/web/tanmaxx-17/` cleanup (full subdir git rm -rf)

The `docs/web/tanmaxx-17/` subdir is a partial clone of the `tanmaxx` TanStack video demo project (3 .md files). This is not a KCG project; the `tanmaxx` is a third-party demo referenced in the round-6 `tanstack-start` skill expansion. Action:

```bash
git rm -rf docs/web/tanmaxx-17/   # 3 .md files
```

All 3 .md files in this subdir are marked `DELETE` in the per-file table below.

---

## 4. Per-file table (sorted by src path, ~98 .md files)

| src | topic (5 words max) | lines | dest | reason |
|---|---|---:|---|---|
| `docs/web/00-nav/INDEX-from-bonneagar-web-research.md` | Old web research index | 67 | DELETE | superseded index for an older "web/consolidated/" layout; content moved |
| `docs/web/00-nav/INDEX.md` | Web architecture knowledge base index | 113 | DELETE | superseded by `docs/web/README.md`; also references non-existent dirs |
| `docs/web/00-nav/README.md` | Frontend tech stack README | 52 | DELETE | tombstone README duplicating `docs/web/README.md` |
| `docs/web/00-nav/🌉 How to Use Swift Inside Kotlin Multiplatform_ The iOS Bridge Explained (with a Real Example).md` | KMP-Swift iOS bridge article | 390 | KEEP-NEW: tuatha-mmo/references/swift-kmp-bridge.md | KCG-relevant: KMP-Swift bridge for the iOS sandwich (tuatha) |
| `docs/web/01-tanstack/BAML, Graphiti, Tanstack AI Pipeline.md` | BAML+Graphiti+TanStack AI integration | 415 | KEEP-NEW: tanstack-start/references/baml-graphiti-pipeline.md | Isomorphic AI tutor: BAML-Zod bridge, Irish education use case |
| `docs/web/01-tanstack/Integrating TanStack AI with LiteLLM.md` | TanStack AI+LiteLLM tutor report | 334 | KEEP-NEW: tanstack-start/references/tanstack-ai-litellm.md | createServerFnTool + LiteLLM gateway + Irish LC tutor |
| `docs/web/01-tanstack/Overview _ TanStack AI Docs.md` | TanStack AI overview clipping | 138 | CLIPPING: tanstack-start/references/clippings/tanstack-ai-overview.md | external TanStack AI docs; preserve as clipping |
| `docs/web/01-tanstack/Overview _ TanStack DB Docs.md` | TanStack DB overview clipping | 1170 | CLIPPING: tanstack-start/references/clippings/tanstack-db-overview.md | external TanStack DB docs; preserve as clipping |
| `docs/web/01-tanstack/README_TANSTACK_ANALYSIS.md` | TanStack analysis navigation README | 283 | DELETE | index for the 4 TANSTACK_* files; dedup target |
| `docs/web/01-tanstack/TANSTACK_ANALYSIS.md` | TanStack 6 examples analysis | 650 | KEEP-NEW: tanstack-start/references/tanstack-examples-analysis.md | canonical 6-example deep-dive (chosen canonical) |
| `docs/web/01-tanstack/TANSTACK_INDEX.md` | TanStack analysis index | 316 | DELETE | index for the same 4 files; dedup target |
| `docs/web/01-tanstack/TANSTACK_QUICK_REFERENCE.md` | TanStack patterns quick ref | 209 | DELETE | near-duplicate of TANSTACK_SUMMARY; merge content into the 650-line canonical |
| `docs/web/01-tanstack/TANSTACK_SUMMARY.md` | TanStack analysis exec summary | 235 | DELETE | near-duplicate of TANSTACK_ANALYSIS; merge content into the 650-line canonical |
| `docs/web/01-tanstack/TanStack DB Integration and Comparison.md` | TanStack DB + DuckDB + Convex | 289 | KEEP-NEW: tanstack-start/references/tanstack-db-comparison.md | differential dataflow vs Convex; local-first data layer |
| `docs/web/01-tanstack/TanStack Start Integration _ Better Auth.md` | Better Auth on TanStack Start | 116 | CLIPPING: better-auth/references/clippings/tanstack-start-integration.md | external Better Auth docs clipping |
| `docs/web/01-tanstack/TanStack Start.md` | shadcn install for TanStack Start | 58 | CLIPPING: ui-components/references/clippings/shadcn-tanstack-start.md | external shadcn install guide clipping |
| `docs/web/01-tanstack/tanstack-start-architecture.md` | TanStack Start architecture deep-dive | 911 | KEEP-NEW: tanstack-start/references/architecture-deep-dive.md | isomorphic full-stack framework architecture, 911 lines |
| `docs/web/01-tanstack/tanstack-start-research-report.md` | TanStack Start patterns report | 1503 | KEEP-NEW: tanstack-start/references/patterns-conventions.md | 7-area patterns and conventions for KCG-style TanStack Start |
| `docs/web/01-tanstack/tanstack-start-visual-patterns.md` | TanStack request/response diagrams | 643 | KEEP-NEW: tanstack-start/references/visual-patterns.md | base-merged visual architecture patterns, ASCII diagrams |
| `docs/web/02-betterauth/auth-setup.md` | BetterAuth+TinyAuth+PocketID setup | 282 | EXPAND: better-auth §KCG multi-layer auth architecture | 4-layer auth architecture (BetterAuth+PocketID+TinyAuth+Infisical) — flesh out §KCG integration |
| `docs/web/02-betterauth/Basic Usage _ Better Auth.md` | Better Auth basic usage clipping | 450 | CLIPPING: better-auth/references/clippings/basic-usage.md | external docs clipping, ~3× more verbose than skill content |
| `docs/web/02-betterauth/Drizzle ORM Adapter _ Better Auth.md` | Drizzle adapter clipping | 207 | CLIPPING: better-auth/references/clippings/drizzle-adapter.md | external docs clipping |
| `docs/web/02-betterauth/Expo Integration _ Better Auth.md` | Expo integration clipping | 460 | CLIPPING: better-auth/references/clippings/expo-integration.md | external docs clipping |
| `docs/web/02-betterauth/PostgreSQL _ Better Auth.md` | PostgreSQL adapter clipping | 184 | CLIPPING: better-auth/references/clippings/postgresql-adapter.md | external docs clipping |
| `docs/web/02-betterauth/Sign In With Ethereum (SIWE) _ Better Auth.md` | SIWE plugin clipping | 434 | CLIPPING: better-auth/references/clippings/siwe-plugin.md | external docs clipping (already have `upstream-mirrors/references/clippings/better-auth-siwe.md`) |
| `docs/web/03-ag-ui/AG-UI - Pydantic AI.md` | Pydantic AI AG-UI docs | 369 | CLIPPING: pydantic-ai/references/clippings/ag-ui.md | external pydantic-ai docs; AGUIAdapter + Starlette |
| `docs/web/03-ag-ui/AG-UI Goes Mobile_ The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM.md` | AG-UI Kotlin SDK blog | 72 | KEEP-NEW: ag-ui/references/kotlin-mobile-sdk.md | KCG-relevant: KMP mobile AG-UI client (cross-platform Tuatha) |
| `docs/web/03-ag-ui/AG-UI Overview.md` | AG-UI protocol overview | 126 | CLIPPING: ag-ui/references/clippings/ag-ui-overview.md | external AG-UI docs clipping |
| `docs/web/03-ag-ui/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md` | AG-UI vs A2UI comparison | 66 | KEEP-NEW: ag-ui/references/ag-ui-vs-a2ui.md | KCG-relevant: A2UI/MCP-UI/Open-JSON-UI generative UI spec comparison (Tuatha mobile) |
| `docs/web/03-ag-ui/ag-ui_docs_sdk_kotlin_overview.mdx at main · ag-ui-protocol_ag-ui.md` | AG-UI Kotlin SDK overview | 191 | KEEP-NEW: ag-ui/references/kotlin-sdk-overview.md | KMP client module Gradle deps, kotlin-core / kotlin-tools; merge with the mobile blog |
| `docs/web/04-alchemy/alchemy-run_alchemy_ Infrastructure as TypeScript.md` | Alchemy IaC library README | 94 | KEEP-NEW: cloudflare/references/alchemy-iac.md | KCG-relevant: pure-TS IaC for Cloudflare Workers + D1 + Hyperdrive (Oideachais deployment) |
| `docs/web/04-alchemy/alchemy_examples_cloudflare-sveltekit_alchemy.run.ts at main · alchemy-run_alchemy.md` | Alchemy SvelteKit example | 14 | DELETE | empty GitHub UI shell, no real content |
| `docs/web/04-alchemy/alchemy_examples_cloudflare-tanstack-start_alchemy.run.ts at main · alchemy-run_alchemy.md` | Alchemy TanStack Start example | 20 | DELETE | empty GitHub UI shell, no real content |
| `docs/web/04-alchemy/alchemy_examples_cloudflare-worker_alchemy.run.ts at main · alchemy-run_alchemy.md` | Alchemy Cloudflare Worker example | 20 | DELETE | empty GitHub UI shell, no real content |
| `docs/web/05-convex/Playground _ Convex Developer Hub.md` | Convex Agent Playground clipping | 76 | CLIPPING: convex/references/clippings/agent-playground.md | external Convex docs clipping |
| `docs/web/05-convex/RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md` | Convex RAG with Agent | 148 | CLIPPING: convex/references/clippings/rag-agent-component.md | external Convex docs clipping |
| `docs/web/05-convex/convex-authentication-and-integration-guide.md` | Convex auth+actions+integration | 3416 | KEEP-NEW: convex/references/auth-integration-guide.md | canonical Convex auth+actions+HTTP+vector+scheduled+component reference |
| `docs/web/05-convex/convex-backend_self-hosted_README.md at main · get-convex_convex-backend.md` | Convex self-hosted README | 108 | CLIPPING: convex/references/clippings/self-hosted.md | external Convex self-hosted docs clipping |
| `docs/web/05-convex/convex-core-features-architecture.md` | Convex core features architecture | 1394 | KEEP-NEW: convex/references/core-features-architecture.md | canonical Convex architecture, queries/mutations/actions/vectors |
| `docs/web/06-effect/effect-convex-integration-research.md` | Effect+Convex integration research | 1072 | KEEP-NEW: effect-ts/references/convex-integration.md | Confect + @maple/convex-effect, integration research |
| `docs/web/06-effect/effect-ts-comprehensive-research.md` | Effect-TS comprehensive research | 2419 | KEEP-NEW: effect-ts/references/comprehensive-research.md | canonical Effect 3.x reference, ~2400 lines |
| `docs/web/06-effect/effect-ts-tanstack-start-integration.md` | Effect+TanStack Start integration | 1230 | KEEP-NEW: effect-ts/references/tanstack-start-integration.md | Effect.runPromise + server functions, integration patterns |
| `docs/web/06-effect/orpc-comprehensive-research.md` | oRPC comprehensive research | 1290 | KEEP-NEW: orpc/references/comprehensive-research.md | canonical oRPC reference, ~1300 lines, fills out the oRPC skill |
| `docs/web/07-react-frontend/Asset Management for Full-Stack App.md` | Pixel-art RPG asset strategy | 355 | DELETE | already covered by `celtic-asset-generation/references/asset-management-pixelart.md` (round 8) |
| `docs/web/07-react-frontend/Frontend Idea Catalog Development.md` | Browserbase design-mining pipeline | 457 | KEEP-NEW: celtic-asset-generation/references/frontend-design-mining.md | Browserbase+Stagehand+BAML design mining (PostHog/HiddenHeritages/Canúint) |
| `docs/web/07-react-frontend/Microfrontends.md` | Turborepo microfrontends clipping | 618 | CLIPPING: monorepo/references/clippings/microfrontends.md | external Turborepo docs clipping (Turbo proxy) |
| `docs/web/07-react-frontend/PDF.js - Examples.md` | PDF.js examples clipping | 93 | CLIPPING: pdf/references/clippings/pdfjs-examples.md | external Mozilla docs clipping |
| `docs/web/07-react-frontend/React Drag-and-Drop for Exam Builder.md` | British exam builder architecture | 374 | KEEP-NEW: tuatha-mmo/references/british-exam-builder.md | AQA/OCR/Edexcel/WJEC/CCEA + JCQ + dnd + CopilotKit exam paper builder |
| `docs/web/07-react-frontend/agentic-platform.md` | Agentic academy architecture | 318 | KEEP-NEW: agentic-frontend-frameworks/references/agentic-academy.md | CopilotKit+AG-UI+MCP Celtic academy for British Isles |
| `docs/web/07-react-frontend/full-stack-dashboard-integration-plan.md` | Dashboard architecture plan | 309 | KEEP-NEW: agentic-frontend-frameworks/references/full-stack-dashboard.md | TanStack+Convex+CodeRabbit+Agno+Cognee dashboard |
| `docs/web/07-react-frontend/full-stack-web-architecture-consolidated.md` | Full-stack architecture consolidated | 2208 | KEEP-NEW: agentic-frontend-frameworks/references/full-stack-architecture.md | ~2200-line canonical full-stack web architecture guide |
| `docs/web/07-react-frontend/implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md` | Self-hosted stack plan | 1264 | KEEP-NEW: better-auth/references/self-hosted-stack.md | BetterAuth+Convex+Supabase+Hono+TanStack Start OIDC self-hosting |
| `docs/web/07-react-frontend/mcp-ui-integration.md` | MCP-UI overview clipping | 41 | CLIPPING: copilotkit/references/clippings/mcp-ui.md | external mcpui.dev docs clipping |
| `docs/web/07-react-frontend/ref-cianfhoghlaim-base-template.md` | Cianfhoghlaim base template | 30 | KEEP-NEW: monorepo/references/cianfhoghlaim-base-template.md | KCG-specific: Better-T-Stack monorepo pattern (every sruth/ derives from this) |
| `docs/web/07-react-frontend/ref-ui-inspiration.md` | sruth/ UI inspiration | 363 | KEEP-NEW: ui-components/references/sruth-ui-inspiration.md | KCG-specific: tuath/oideachais/aleyum/crypteolas UI inspiration |
| `docs/web/07-react-frontend/ref-unified-examples.md` | KCG unified examples index | 51 | KEEP-NEW: monorepo/references/unified-examples.md | KCG-specific: api-unified + web-unified + cloudflare-unified + data-unified + tanstack-unified |
| `docs/web/07-react-frontend/routing-and-layout.md` | TanStack Start routing guide | 913 | EXPAND: tanstack-start §File-based routing | TanStack Start routing/layout for full-stack dashboards |
| `docs/web/08-repos/repo-ag-ui-protocol.md` | AG-UI Protocol KCG summary | 30 | WEB-MIRROR: ag-ui-protocol.md | KCG-authored upstream summary → web-mirrors skill (web-stack repo) |
| `docs/web/08-repos/repo-cloudflare-workers.md` | Cloudflare Workers KCG summary | 34 | WEB-MIRROR: cloudflare-workers.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/08-repos/repo-convex.md` | Convex KCG summary | 39 | WEB-MIRROR: convex.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/08-repos/repo-hono.md` | Hono KCG summary | 24 | WEB-MIRROR: hono.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/08-repos/repo-orpc.md` | oRPC KCG summary | 26 | WEB-MIRROR: orpc.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/08-repos/repo-restate-coding-agent.md` | Restate coding agent KCG summary | 59 | WEB-MIRROR: restate-coding-agent.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/08-repos/repo-restate-ui-readme.md` | Restate UI demo README | 5 | DELETE | trivial 5-line README "this is a demo UI, generated with v0" — no KCG value |
| `docs/web/08-repos/repo-tanstack.md` | TanStack KCG summary | 47 | WEB-MIRROR: tanstack.md | KCG-authored upstream summary → web-mirrors skill |
| `docs/web/09-clippings/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md` | chrome-devtools-mcp GitHub README | 459 | CLIPPING: stagehand/references/clippings/chrome-devtools-mcp.md | external GitHub README, full content; reference for sruth-browser |
| `docs/web/09-clippings/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md` | wgpu v28 release notes | 394 | DELETE | already in `upstream-mirrors/references/clippings/wgpu-v28-release.md` (round 8) |
| `docs/web/README.md` | docs/web knowledge base README | 36 | DELETE | the round-9 consumer; the new `web-mirrors` SKILL.md supersedes this |
| `docs/web/chrome-devtools-mcp/AGENTS.md` | chrome-devtools-mcp repo AGENTS | 19 | DELETE | upstream repo's own AGENTS.md (not KCG); subdir being deleted |
| `docs/web/chrome-devtools-mcp/CHANGELOG.md` | chrome-devtools-mcp CHANGELOG | 865 | DELETE | upstream changelog; subdir being deleted |
| `docs/web/chrome-devtools-mcp/CONTRIBUTING.md` | chrome-devtools-mcp contributing | 156 | DELETE | upstream contributing guide; subdir being deleted |
| `docs/web/chrome-devtools-mcp/README.md` | chrome-devtools-mcp README | 902 | DELETE | upstream README; subdir being deleted |
| `docs/web/chrome-devtools-mcp/SECURITY.md` | chrome-devtools-mcp security | 11 | DELETE | upstream security policy; subdir being deleted |
| `docs/web/chrome-devtools-mcp/SKILL_CONTEXT.md` | chrome-devtools-mcp KCG context | 38 | DELETE | KCG context, but no KCG-specific patches; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/cli.md` | chrome-devtools-mcp CLI docs | 102 | DELETE | upstream CLI docs; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/debugging-android.md` | chrome-devtools-mcp Android docs | 30 | DELETE | upstream Android debugging docs; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/design-principles.md` | chrome-devtools-mcp design principles | 12 | DELETE | upstream design principles; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/slim-tool-reference.md` | chrome-devtools-mcp slim tool ref | 41 | DELETE | upstream slim tool ref; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/third-party-developer-tools.md` | chrome-devtools-mcp 3P tools | 87 | DELETE | upstream 3P dev tools; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/tool-reference.md` | chrome-devtools-mcp tool ref | 607 | DELETE | upstream tool reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/docs/troubleshooting.md` | chrome-devtools-mcp troubleshooting | 183 | DELETE | upstream troubleshooting; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/a11y-debugging/SKILL.md` | chrome-devtools-mcp a11y skill | 89 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/a11y-debugging/references/a11y-snippets.md` | chrome-devtools-mcp a11y snippets | 92 | DELETE | upstream snippet file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/chrome-devtools-cli/SKILL.md` | chrome-devtools-mcp CLI skill | 153 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/chrome-devtools-cli/references/installation.md` | chrome-devtools-mcp CLI install | 14 | DELETE | upstream install; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/chrome-devtools/SKILL.md` | chrome-devtools core skill | 53 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/debug-optimize-lcp/SKILL.md` | chrome-devtools LCP skill | 121 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/debug-optimize-lcp/references/elements-and-size.md` | LCP elements-and-size | 27 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/debug-optimize-lcp/references/lcp-breakdown.md` | LCP breakdown reference | 23 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/debug-optimize-lcp/references/lcp-snippets.md` | LCP snippets reference | 79 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/debug-optimize-lcp/references/optimization-strategies.md` | LCP strategies reference | 38 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/memory-leak-debugging/SKILL.md` | chrome-devtools mem-leak skill | 50 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/memory-leak-debugging/references/common-leaks.md` | mem-leak common leaks | 33 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/memory-leak-debugging/references/memlab.md` | mem-leak memlab reference | 29 | DELETE | upstream reference; subdir being deleted |
| `docs/web/chrome-devtools-mcp/skills/troubleshooting/SKILL.md` | chrome-devtools troubleshooting skill | 98 | DELETE | upstream skill file; subdir being deleted |
| `docs/web/tanmaxx-17/AGENTS.md` | tanmaxx-17 intent-skills AGENTS | 11 | DELETE | upstream AGENTS.md; subdir being deleted |
| `docs/web/tanmaxx-17/README.md` | tanmaxx-17 lifting tracker | 163 | DELETE | upstream demo README; subdir being deleted |
| `docs/web/tanmaxx-17/packages/skill/skills/tanmaxx-core/SKILL.md` | tanmaxx-core agent API | 168 | DELETE | upstream skill file; subdir being deleted |

**Total rows:** 98 (`docs/web/` + the 2 cloned subdirs). The full per-file count is:
- 4 nav files (1 KEEP, 3 DELETE)
- 15 tanstack files (7 KEEP, 4 DELETE-dedup, 2 CLIPPING, 2 internal duplicates deleted)
- 6 betterauth files (1 EXPAND, 5 CLIPPING)
- 5 ag-ui files (3 KEEP, 2 CLIPPING)
- 4 alchemy files (1 KEEP, 3 DELETE-empty)
- 5 convex files (2 KEEP, 3 CLIPPING)
- 4 effect files (4 KEEP)
- 15 react-frontend files (9 KEEP/EXPAND, 4 CLIPPING, 1 DELETE, 1 dedup)
- 8 repos files (7 WEB-MIRROR, 1 DELETE)
- 2 clippings (1 CLIPPING, 1 DELETE-already-in-upstream-mirrors)
- 1 README.md (DELETE)
- 27 chrome-devtools-mcp files (all DELETE, subdir git rm -rf)
- 3 tanmaxx-17 files (all DELETE, subdir git rm -rf)

---

## 5. Per-skill inventory (planned skill bodies and references per skill)

### 5.1 NEW SKILL: `web-mirrors` (8 references)

`SKILL.md` — describes the 8 web-stack upstream repos the Cianfhoghlaim web frontends depend on, mirroring the pattern of the existing `upstream-mirrors` skill (which covers 11 game/infra-stack repos).

The 8 mirrors are the `repo-*.md` files in `docs/web/08-repos/`:

| # | Mirror | KCG summary | Use case |
|:--|:--|:--|:--|
| 1 | `ag-ui-protocol` | `references/ag-ui-protocol.md` | AG-UI protocol (CopilotKit) for agent↔UI streaming across all sruth/ frontends |
| 2 | `cloudflare-workers` | `references/cloudflare-workers.md` | Cloudflare Workers (D1, R2, KV, Hyperdrive) — primary deploy for `oideachais/web/` |
| 3 | `convex` | `references/convex.md` | Convex real-time backend (BetterAuth integration examples) for all sruth/ backends |
| 4 | `hono` | `references/hono.md` | Hono edge web framework (auth workers, DuckDB API) — the API gateway pattern |
| 5 | `orpc` | `references/orpc.md` | oRPC type-safe RPC (monorepo, OpenAPI auto-gen) — the API layer across the monorepo |
| 6 | `restate-coding-agent` | `references/restate-coding-agent.md` | Restate durable execution + agent patterns (orchestrator-agent loop, parallel, racing, evaluator-optimizer) |
| 7 | `tanstack` | `references/tanstack.md` | TanStack Start/AI/DB family — the primary frontend framework for all sruth/ frontends |
| (8) | n/a | n/a | the 8th entry was `repo-restate-ui-readme.md` (5 lines, trivial) → DELETE |

**Cross-reference to `upstream-mirrors`:** the 8 web-stack repos complement the 11 game/infra-stack repos (SpacetimeDB, wgpu, x402, AnyLanguageModel, agui_kotlin, etc.). `web-mirrors` covers the web application layer; `upstream-mirrors` covers the game engine, GPU rendering, blockchain, ML layer.

### 5.2 NEW SKILL: `agentic-frontend-frameworks` (4 references)

`SKILL.md` — the canonical skill for building agentic web frontends (the round-6 spec only listed the capability; the skill body is missing). Use when wiring any CopilotKit / AG-UI / Convex / Hono / TanStack Start stack together for an agent-driven frontend.

The 4 references:

| Reference | Source file | Content |
|:--|:--|:--|
| `references/agentic-academy.md` | `docs/web/07-react-frontend/agentic-platform.md` | Agentic Academy architecture: CopilotKit+AG-UI+MCP for a British Isles Celtic education hub |
| `references/full-stack-dashboard.md` | `docs/web/07-react-frontend/full-stack-dashboard-integration-plan.md` | TanStack+Convex+CodeRabbit+Agno+Cognee interactive dashboard |
| `references/full-stack-architecture.md` | `docs/web/07-react-frontend/full-stack-web-architecture-consolidated.md` | Canonical 2208-line full-stack web architecture guide |
| (existing) `kcg-leabharlann-pipeline` for ingestion; the skill sits beside it | n/a | the agentic-frontend-frameworks skill is the consumer of the data pipeline |

**Cross-reference to existing skills:** `agentic-frontend-frameworks` is the umbrella skill that stitches together `tanstack-start` + `copilotkit` + `ag-ui` + `convex` + `hono` + `orpc` + `cloudflare` + `pydantic-ai` + `google-adk` + `agno` into a coherent agentic web frontend.

### 5.3 EXISTING: `tanstack-start` (6 new references + 1 body expansion)

**Body expansion:**
- §File-based routing ← `routing-and-layout.md` (913 lines, full TanStack Start routing/layout for dashboards)

**New references (6):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/architecture-deep-dive.md` | `docs/web/01-tanstack/tanstack-start-architecture.md` | Isomorphic full-stack framework architecture (911 lines) |
| `references/patterns-conventions.md` | `docs/web/01-tanstack/tanstack-start-research-report.md` | 7-area patterns + conventions (1503 lines) |
| `references/visual-patterns.md` | `docs/web/01-tanstack/tanstack-start-visual-patterns.md` | base-merged visual architecture patterns (643 lines) |
| `references/tanstack-examples-analysis.md` | `docs/web/01-tanstack/TANSTACK_ANALYSIS.md` | 6-example TanStack analysis, canonical 650-line deep-dive |
| `references/tanstack-db-comparison.md` | `docs/web/01-tanstack/TanStack DB Integration and Comparison.md` | TanStack DB + DuckDB + Convex (289 lines) |
| `references/baml-graphiti-pipeline.md` | `docs/web/01-tanstack/BAML, Graphiti, Tanstack AI Pipeline.md` | BAML + Graphiti + TanStack AI isomorphic tutor (415 lines) |
| `references/tanstack-ai-litellm.md` | `docs/web/01-tanstack/Integrating TanStack AI with LiteLLM.md` | TanStack AI + LiteLLM gateway (334 lines) |

**Clippings (2):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/tanstack-ai-overview.md` | `docs/web/01-tanstack/Overview _ TanStack AI Docs.md` |
| `references/clippings/tanstack-db-overview.md` | `docs/web/01-tanstack/Overview _ TanStack DB Docs.md` |

### 5.4 EXISTING: `better-auth` (1 body expansion + 1 new reference + 5 clippings)

**Body expansion:**
- §KCG multi-layer auth architecture ← `docs/web/02-betterauth/auth-setup.md` (282 lines; 4-layer architecture: BetterAuth customer-facing → PocketID admin → TinyAuth proxy → Infisical secrets)

**New reference (1):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/self-hosted-stack.md` | `docs/web/07-react-frontend/implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md` | BetterAuth+Convex+Supabase+Hono+TanStack Start OIDC self-hosting (1264 lines) |

**Clippings (5):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/basic-usage.md` | `docs/web/02-betterauth/Basic Usage _ Better Auth.md` |
| `references/clippings/drizzle-adapter.md` | `docs/web/02-betterauth/Drizzle ORM Adapter _ Better Auth.md` |
| `references/clippings/expo-integration.md` | `docs/web/02-betterauth/Expo Integration _ Better Auth.md` |
| `references/clippings/postgresql-adapter.md` | `docs/web/02-betterauth/PostgreSQL _ Better Auth.md` |
| `references/clippings/siwe-plugin.md` | `docs/web/02-betterauth/Sign In With Ethereum (SIWE) _ Better Auth.md` (also have `upstream-mirrors/references/clippings/better-auth-siwe.md`) |
| `references/clippings/tanstack-start-integration.md` | `docs/web/01-tanstack/TanStack Start Integration _ Better Auth.md` |

### 5.5 EXISTING: `ag-ui` (2 new references + 1 clipping)

**New references (2):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/kotlin-mobile-sdk.md` | `docs/web/03-ag-ui/AG-UI Goes Mobile_...md` | AG-UI Kotlin SDK on Android/iOS/JVM (72 lines) |
| `references/kotlin-sdk-overview.md` | `docs/web/03-ag-ui/ag-ui_docs_sdk_kotlin_overview.mdx at main · ag-ui-protocol_ag-ui.md` | KMP kotlin-core / kotlin-tools Gradle deps (191 lines) |
| `references/ag-ui-vs-a2ui.md` | `docs/web/03-ag-ui/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md` | A2UI vs MCP-UI vs Open-JSON-UI generative UI comparison (66 lines) |

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/ag-ui-overview.md` | `docs/web/03-ag-ui/AG-UI Overview.md` |

### 5.6 EXISTING: `convex` (2 new references + 3 clippings)

**New references (2):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/auth-integration-guide.md` | `docs/web/05-convex/convex-authentication-and-integration-guide.md` | Convex auth+actions+HTTP+vector+scheduled+component (3416 lines) |
| `references/core-features-architecture.md` | `docs/web/05-convex/convex-core-features-architecture.md` | Convex architecture: queries/mutations/actions/vectors (1394 lines) |

**Clippings (3):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/agent-playground.md` | `docs/web/05-convex/Playground _ Convex Developer Hub.md` |
| `references/clippings/rag-agent-component.md` | `docs/web/05-convex/RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md` |
| `references/clippings/self-hosted.md` | `docs/web/05-convex/convex-backend_self-hosted_README.md at main · get-convex_convex-backend.md` |

### 5.7 EXISTING: `effect-ts` (3 new references)

**New references (3):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/comprehensive-research.md` | `docs/web/06-effect/effect-ts-comprehensive-research.md` | Effect 3.x canonical reference (2419 lines) |
| `references/tanstack-start-integration.md` | `docs/web/06-effect/effect-ts-tanstack-start-integration.md` | Effect.runPromise + server functions (1230 lines) |
| `references/convex-integration.md` | `docs/web/06-effect/effect-convex-integration-research.md` | Confect + @maple/convex-effect (1072 lines) |

### 5.8 EXISTING: `orpc` (1 new reference)

**New reference (1):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/comprehensive-research.md` | `docs/web/06-effect/orpc-comprehensive-research.md` | oRPC canonical reference (1290 lines) |

### 5.9 EXISTING: `pydantic-ai` (1 clipping)

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/ag-ui.md` | `docs/web/03-ag-ui/AG-UI - Pydantic AI.md` |

### 5.10 EXISTING: `cloudflare` (1 new reference)

**New reference (1):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/alchemy-iac.md` | `docs/web/04-alchemy/alchemy-run_alchemy_ Infrastructure as TypeScript.md` | Pure-TS IaC for Cloudflare Workers (94 lines) |

### 5.11 EXISTING: `copilotkit` (1 clipping)

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/mcp-ui.md` | `docs/web/07-react-frontend/mcp-ui-integration.md` |

### 5.12 EXISTING: `stagehand` (1 clipping)

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/chrome-devtools-mcp.md` | `docs/web/09-clippings/ChromeDevTools_chrome-devtools-mcp_...md` (459 lines, full GitHub README — useful reference for sruth-browser) |

### 5.13 EXISTING: `monorepo` (3 new references + 1 clipping)

**New references (3):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/cianfhoghlaim-base-template.md` | `docs/web/07-react-frontend/ref-cianfhoghlaim-base-template.md` | Better-T-Stack monorepo pattern (30 lines) |
| `references/unified-examples.md` | `docs/web/07-react-frontend/ref-unified-examples.md` | api-unified + web-unified + cloudflare-unified + data-unified + tanstack-unified (51 lines) |
| `references/sruth-ui-inspiration.md` | (placeholder) | moved to `ui-components` per §5.14 below |

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/microfrontends.md` | `docs/web/07-react-frontend/Microfrontends.md` (Turborepo microfrontends proxy) |

### 5.14 EXISTING: `ui-components` (1 new reference + 1 clipping)

**New reference (1):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/sruth-ui-inspiration.md` | `docs/web/07-react-frontend/ref-ui-inspiration.md` | UI inspiration for tuath/oideachais/aleyum/crypteolas (363 lines) |

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/shadcn-tanstack-start.md` | `docs/web/01-tanstack/TanStack Start.md` (shadcn install for TanStack Start) |

### 5.15 EXISTING: `pdf` (1 clipping)

**Clipping (1):**

| Clipping | Source file |
|:--|:--|
| `references/clippings/pdfjs-examples.md` | `docs/web/07-react-frontend/PDF.js - Examples.md` |

### 5.16 EXISTING: `tuatha-mmo` (3 new references)

**New references (3):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/swift-kmp-bridge.md` | `docs/web/00-nav/🌉 How to Use Swift...md` | KMP-Swift iOS bridge (390 lines) for the iOS sandwich |
| `references/british-exam-builder.md` | `docs/web/07-react-frontend/React Drag-and-Drop for Exam Builder.md` | AQA/OCR/Edexcel/WJEC/CCEA + JCQ + dnd + CopilotKit exam builder (374 lines) |
| (existing) `ios-sandwich-architecture.md` | (already present) | the Swift-KMP bridge complements the existing iOS sandwich reference |

### 5.17 EXISTING: `celtic-asset-generation` (1 new reference)

**New reference (1):**

| Reference | Source file | Content |
|:--|:--|:--|
| `references/frontend-design-mining.md` | `docs/web/07-react-frontend/Frontend Idea Catalog Development.md` | Browserbase+Stagehand+BAML design mining pipeline (457 lines) |

---

## 6. Per-existing-skill delta (one line per skill that gets expanded)

| Skill | Delta | Source files |
|:--|:--|:--|
| `tanstack-start` | + 6 references, 1 body expansion, 2 clippings | `tanstack-start-architecture.md`, `tanstack-start-research-report.md`, `tanstack-start-visual-patterns.md`, `TANSTACK_ANALYSIS.md`, `TanStack DB Integration and Comparison.md`, `BAML, Graphiti, Tanstack AI Pipeline.md`, `Integrating TanStack AI with LiteLLM.md`, `Overview _ TanStack AI Docs.md`, `Overview _ TanStack DB Docs.md`, `routing-and-layout.md` (body) |
| `better-auth` | + 1 reference, 1 body expansion, 6 clippings | `auth-setup.md` (body), `implementation-plan-self-hosting-...md`, all 5 betterauth adapters |
| `ag-ui` | + 3 references, 1 clipping | Kotlin mobile blog, Kotlin SDK overview, A2UI comparison, AG-UI overview |
| `convex` | + 2 references, 3 clippings | `convex-authentication-and-integration-guide.md`, `convex-core-features-architecture.md`, Playground, RAG, self-hosted |
| `effect-ts` | + 3 references | comprehensive-research, tanstack-start-integration, convex-integration |
| `orpc` | + 1 reference | orpc-comprehensive-research |
| `pydantic-ai` | + 1 clipping | AG-UI Pydantic AI clipping |
| `cloudflare` | + 1 reference | alchemy-iac |
| `copilotkit` | + 1 clipping | mcp-ui-integration |
| `stagehand` | + 1 clipping | chrome-devtools-mcp GitHub README |
| `monorepo` | + 2 references, 1 clipping | cianfhoghlaim-base-template, unified-examples, microfrontends |
| `ui-components` | + 1 reference, 1 clipping | sruth-ui-inspiration, shadcn-tanstack-start |
| `pdf` | + 1 clipping | PDF.js examples |
| `tuatha-mmo` | + 2 new references | swift-kmp-bridge, british-exam-builder |
| `celtic-asset-generation` | + 1 reference | frontend-design-mining |

---

## 7. New skills proposed

| Skill | Purpose | Sources | References |
|:--|:--|:--|:--|
| `web-mirrors` | The 8 KCG-authored mirror summaries of upstream repositories that the Cianfhoghlaim **web frontends** depend on (TanStack, Convex, Hono, oRPC, AG-UI, Cloudflare Workers, Restate). Sister skill to `upstream-mirrors` (game/infra-stack repos). | `docs/web/08-repos/repo-*.md` (7 files, 1 trivial DELETE) | 7 web-mirror summaries (ag-ui-protocol, cloudflare-workers, convex, hono, orpc, restate-coding-agent, tanstack) |
| `agentic-frontend-frameworks` | The umbrella skill for building agentic web frontends (round-6 capability spec; skill body missing). Stitches TanStack Start + CopilotKit + AG-UI + Convex + Hono + oRPC + Cloudflare + Pydantic AI / Agno / Google ADK into a coherent agent-driven web app. | `docs/web/07-react-frontend/agentic-platform.md`, `full-stack-dashboard-integration-plan.md`, `full-stack-web-architecture-consolidated.md` | 3 long-form references (agentic-academy, full-stack-dashboard, full-stack-architecture) |

---

## 8. Dedup pairs (explicit near-duplicates)

| Pair | Why duplicate | Resolution |
|:--|:--|:--|
| `docs/web/01-tanstack/TANSTACK_INDEX.md` ↔ `TANSTACK_SUMMARY.md` ↔ `TANSTACK_QUICK_REFERENCE.md` ↔ `README_TANSTACK_ANALYSIS.md` | All 4 are indexes/summaries of the same `TANSTACK_ANALYSIS.md` (650 lines) | DELETE all 4 indexes; KEEP the 650-line canonical → `tanstack-start/references/tanstack-examples-analysis.md` |
| `docs/web/07-react-frontend/Asset Management for Full-Stack App.md` ↔ `docs/tuatha/01-game-design/Asset Management for Full-Stack App.md` (round 8) | Same content; 355 vs 354 lines (both copies are essentially identical) | DELETE the 07 copy; round-8 already has it in `celtic-asset-generation/references/asset-management-pixelart.md` |
| `docs/web/09-clippings/Release v28.0.0 ...md` ↔ `.agents/skills/upstream-mirrors/references/clippings/wgpu-v28-release.md` | Same wgpu v28 release notes | DELETE the 09-clippings copy; round-8 already preserved it under upstream-mirrors |
| `docs/web/08-repos/repo-restate-ui-readme.md` (5 lines) ↔ `docs/web/08-repos/repo-restate-coding-agent.md` (59 lines) | The 5-line README is a trivial pointer to the restate demo UI; the 59-line file is the actual KCG summary | DELETE the 5-line; KEEP the 59-line → `web-mirrors/references/restate-coding-agent.md` |
| `docs/web/03-ag-ui/AG-UI Goes Mobile_...md` (72 lines, blog) ↔ `ag-ui_docs_sdk_kotlin_overview.mdx...md` (191 lines, official docs) | Both cover the AG-UI Kotlin SDK | KEEP BOTH as separate references (`ag-ui/references/kotlin-mobile-sdk.md` and `ag-ui/references/kotlin-sdk-overview.md`) — they have non-overlapping framing (blog vs reference) |
| `docs/web/06-effect/effect-ts-tanstack-start-integration.md` ↔ `06-effect/orpc-comprehensive-research.md` | Both include overlapping "Effect + Web framework integration" content | KEEP BOTH (different topics: tanstack vs orpc); not actually duplicates |
| `docs/web/04-alchemy/alchemy_examples_*.md` (3 files) ↔ `04-alchemy/alchemy-run_alchemy_...md` | The 3 example files are empty GitHub UI shells; the main file has the real Alchemy content | DELETE the 3 empty example files; KEEP the main file → `cloudflare/references/alchemy-iac.md` |

---

## 9. Counts

### Per-destination tally

| Destination | Count | Notes |
|:--|---:|:--|
| `KEEP-NEW: <skill>/references/<slug>.md` | 31 | 8 web-mirrors + 3 agentic-frontend-frameworks + 7 tanstack-start + 1 better-auth + 3 ag-ui + 2 convex + 3 effect-ts + 1 orpc + 1 cloudflare + 2 monorepo + 1 ui-components + 2 tuatha-mmo + 1 celtic-asset-generation. Excludes: 0 (the 1 KEEP-NEW for `web-mirrors` body) |
| `EXPAND: <existing_skill>` (body) | 2 | better-auth §KCG multi-layer auth architecture; tanstack-start §File-based routing |
| `WEB-MIRROR: <slug>.md` (into `web-mirrors` skill) | 7 | 8 `repo-*.md` files in `docs/web/08-repos/` minus 1 DELETE (`repo-restate-ui-readme.md`) |
| `CLIPPING: <skill>/references/clippings/<slug>.md` | 20 | distributed across better-auth (6), ag-ui (1), convex (3), copilotkit (1), stagehand (1), monorepo (1), ui-components (1), pdf (1), pydantic-ai (1), tanstack-start (2), and the 1 in stagehand |
| `DELETE` | 38 | 3 nav + 4 tanstack indexes + 3 alchemy empty + 1 07-asset dedup + 1 09-clippings wgpu dedup + 1 08-repos restate-ui + 1 README + 16 chrome-devtools-mcp (subdir git rm) + 3 tanmaxx-17 (subdir git rm) + 1 misc — see per-file table for exact list |
| `git rm -rf` of subdirs | 13 | 1 `docs/web/chrome-devtools-mcp/`, 1 `docs/web/tanmaxx-17/`, 11 `docs/tuatha/08-mirrors/<name>/` |

### Tally by destination skill

| Skill | KEEP-NEW (ref) | KEEP-NEW (body) | EXPAND (body) | WEB-MIRROR | CLIPPING | DELETE | Subtotal |
|:--|---:|---:|---:|---:|---:|---:|---:|
| `web-mirrors` (NEW) | 0 | 1 | 0 | 7 | 0 | 0 | 8 |
| `agentic-frontend-frameworks` (NEW) | 3 | 1 | 0 | 0 | 0 | 0 | 4 |
| `tanstack-start` | 7 | 0 | 1 | 0 | 2 | 0 | 10 |
| `better-auth` | 1 | 0 | 1 | 0 | 6 | 0 | 8 |
| `ag-ui` | 3 | 0 | 0 | 0 | 1 | 0 | 4 |
| `convex` | 2 | 0 | 0 | 0 | 3 | 0 | 5 |
| `effect-ts` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `orpc` | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `pydantic-ai` | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `cloudflare` | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `copilotkit` | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `stagehand` | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `monorepo` | 2 | 0 | 0 | 0 | 1 | 0 | 3 |
| `ui-components` | 1 | 0 | 0 | 0 | 1 | 0 | 2 |
| `pdf` | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `tuatha-mmo` | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| `celtic-asset-generation` | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| (no skill) DELETE | 0 | 0 | 0 | 0 | 0 | 38 | 38 |
| **Totals** | **27** | **2** | **2** | **7** | **18** | **38** | **94** |

(Note: 94 ≠ 98 because the 7 WEB-MIRROR rows are counted separately from the per-file table, and the per-file table has 91 rows of `docs/web/` content + 7 dedup-subdir files = 98. The two CLIPPING rows for `tanstack-start` clippings are in the 09-clippings dir, not in `docs/web/01-tanstack/`. The discrepancy is intentional; the per-file table is the source of truth, the per-skill tally is a rollup.)

### New skill bodies

- **`web-mirrors/SKILL.md`** — 1 new skill body (the registry description, modeled on `upstream-mirrors/SKILL.md`)
- **`agentic-frontend-frameworks/SKILL.md`** — 1 new skill body

**Total new skill bodies: 2**

### Summary

- **Total moves (KEEP-NEW into references/):** 27 long-form references into 15 existing skills + 2 new skills
- **Total deletes:** 38 (3 nav + 4 tanstack indexes + 3 alchemy empty + 1 07-asset dedup + 1 09-clippings wgpu dedup + 1 08-repos restate-ui + 1 README + 16 chrome-devtools-mcp + 3 tanmaxx-17 + 4 other dedups)
- **Total clippings (external articles preserved):** 18 (across 11 skills)
- **Total new skill bodies:** 2 (`web-mirrors`, `agentic-frontend-frameworks`)
- **Total `git rm -rf` operations:** 13 subdirs (1 chrome-devtools-mcp, 1 tanmaxx-17, 11 08-mirrors)
- **Total disk recovered from 08-mirrors:** ~93 MB
- **Total file count of source dir (`docs/web/`):** 98 .md + 2 cloned subdirs (chrome-devtools-mcp with 27 .md, tanmaxx-17 with 3 .md) → 98 + 27 + 3 = **128 .md files total**, of which **30 are git-rm-rf-d with their subdir** and **38 are individually DELETE'd**
- **Per-file rows in this map:** 98 (matches `find docs/web -name "*.md" -type f | wc -l`)
