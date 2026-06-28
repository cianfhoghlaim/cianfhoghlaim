# Consolidated Examples — KCG Summary

## What It Is
This directory contains the project's own unified example applications — not third-party clones but purpose-built demonstrations of the Cianfhoghlaim stack patterns. The `api-unified` example shows how to combine MCP, oRPC, OpenAPI, and AI streaming in a single Hono server. The `web-unified` example demonstrates the full-stack TanStack Start pattern. The `cloudflare-unified` example shows Cloudflare Workers deployment patterns. The `data-unified` example covers data pipeline architecture. The `tanstack-unified` example consolidates TanStack-specific patterns.

## Why This Matters for Kings' College Galway
These are the project's own reference implementations — not third-party examples. `api-unified` is the canonical API architecture for the Cianfhoghlaim stack, combining all four protocol surfaces (MCP, oRPC, OpenAPI, AI streaming) in one coherent Hono application. The `architecture.md` documents are the definitive guides for building new sruth/ services. The `web-unified` example defines the project's frontend conventions with agent instructions (.roo, .ruler, AGENTS.md) that govern AI-assisted development.

## Key Patterns Preserved
- **docs/web/docs_examples_consolidated/api-unified/README.md** — Comprehensive API unified example: MCP + oRPC + OpenAPI + AI streaming in Hono
- **docs/web/docs_examples_consolidated/api-unified/ARCHITECTURE.md** — Deep technical architecture of the unified API server
- **docs/web/docs_examples_consolidated/api-unified/FILE_STRUCTURE.md** — Complete file structure reference
- **docs/web/docs_examples_consolidated/api-unified/INDEX.md** — Api-unified index
- **docs/web/docs_examples_consolidated/api-unified/PROJECT_SUMMARY.md** — High-level overview and key concepts
- **docs/web/docs_examples_consolidated/api-unified/QUICKSTART.md** — 5-minute quickstart guide
- **docs/web/docs_examples_consolidated/cloudflare-unified/ARCHITECTURE.md** — Cloudflare deployment architecture
- **docs/web/docs_examples_consolidated/cloudflare-unified/EXAMPLES.md** — Cloudflare integration examples
- **docs/web/docs_examples_consolidated/cloudflare-unified/FILE_STRUCTURE.md** — File structure for Cloudflare apps
- **docs/web/docs_examples_consolidated/cloudflare-unified/INDEX.md** — Cloudflare-unified index
- **docs/web/docs_examples_consolidated/cloudflare-unified/QUICKSTART.md** — Cloudflare quickstart
- **docs/web/docs_examples_consolidated/cloudflare-unified/README.md** — Cloudflare unified overview
- **docs/web/docs_examples_consolidated/data-unified/ARCHITECTURE.md** — Data pipeline architecture
- **docs/web/docs_examples_consolidated/data-unified/EXAMPLES.md** — Data pipeline examples
- **docs/web/docs_examples_consolidated/data-unified/FILES.md** — Data pipeline file layout
- **docs/web/docs_examples_consolidated/data-unified/INDEX.md** — Data-unified index
- **docs/web/docs_examples_consolidated/data-unified/PROJECT_SUMMARY.md** — Data platform summary
- **docs/web/docs_examples_consolidated/data-unified/QUICKSTART.md** — Data pipeline quickstart
- **docs/web/docs_examples_consolidated/data-unified/README.md** — Data unified overview
- **docs/web/docs_examples_consolidated/tanstack-unified/README.md** — TanStack unified patterns
- **docs/web/docs_examples_consolidated/tanstack-unified/PROJECT_SUMMARY.md** — TanStack project summary
- **docs/web/docs_examples_consolidated/tanstack-unified/QUICKSTART.md** — TanStack quickstart
- **docs/web/docs_examples_consolidated/web-unified/README.md** — Web unified full-stack example
- **docs/web/docs_examples_consolidated/web-unified/AGENTS.md** — Agent instructions for web-unified
- **docs/web/docs_examples_consolidated/web-unified/CLAUDE.md** — Claude agent instructions
- **docs/web/docs_examples_consolidated/web-unified/GEMINI.md** — Gemini agent instructions
- **docs/web/docs_examples_consolidated/web-unified/.github/copilot-instructions.md** — Copilot instructions
- **docs/web/docs_examples_consolidated/web-unified/.roo/rules/ultracite.md** — Roo agent rules
- **docs/web/docs_examples_consolidated/web-unified/.ruler/bts.md** — Ruler configuration

## Source Files
These are the project's own examples (not third-party clones). Full source removed (2026-06-06) but architecture documents and agent instructions retained. Source available in the main repository under `sruth/oideachais/web/`.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, tsconfig.json, hone.config.ts, wrangler.jsonc, etc.)
- All CSS/Styles (.css)
- All build artifacts and lock files (node_modules/, dist/)
- All Docker files
- All image/assets
- .git directories
- All non-.md files
