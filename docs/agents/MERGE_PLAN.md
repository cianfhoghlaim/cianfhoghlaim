# Merge Plan: agents

**Date:** 2026-06-06
**Current state:** 131 .md files across 9 subdirs + 16 root-level standalone files
**Target:** 0 subdirectories, all content in ~4 root-level .md files (collapsing 10 existing + adding 4 merge-target docs)

---

## Existing Consolidated Docs (Keep at Root)

These 10 root-level mega-merges already exist. Their source subdirectories contain only stubs and must be deleted:

| Consolidated Doc | Lines | Source Subdirs | Stubs Remaining |
|---|---|---|---|
| `AGNO_COMPREHENSIVE_REFERENCE.md` | ~500 | `agno/` (8 files) | 8 stubs |
| `GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md` | ~400 | `google-adk/` (20 files) | 20 stubs |
| `STAGEHAND_COMPREHENSIVE_REFERENCE.md` | ~300 | `stagehand/` (24 files) | 24 stubs |
| `DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md` | ~600 | `durable/` (30 files) | 30 stubs |
| `BAML_COMPREHENSIVE_GUIDE.md` | ~400 | Root BAML files (5) | 5 root files |
| `MCP_COMPREHENSIVE_RESEARCH.md` | ~500 | `z_ai/` (4) + root MCP files | 11 stubs + root files |
| `BROWSER_AUTOMATION_PLATFORM.md` | ~400 | `browserbase/` (2) + `smolagents/` (3) | 5 stubs |
| `CONVEX_AGENT_PLATFORM.md` | ~200 | `convex/` (2 files) | 2 stubs |
| `PYDIANTIC_AI_REFERENCE.md` | ~300 | `pydantic_ai/` (4 files) | 4 stubs |
| `IRISH_EDUCATION_PLATFORM_BLUEPRINT.md` | ~400 | Root education files (3) | 3 root files |

---

## Planned Merges: Root-Level Standalone Files

The remaining 16 root-level files need to be absorbed or reorganized into 4 thematic merge targets:

### Merge A: `mcp-ecosystem-reference.md`
**Expand:** `MCP_COMPREHENSIVE_RESEARCH.md` → rename to `mcp-ecosystem-reference.md`
**Root files to absorb:**
- `MCP_RESEARCH.md` — duplicate research
- `mcp-research-report.md` — duplicate report
- `mcp-ui-gradio-evidence-integration-analysis.md` — UI analysis
- `MCP Server.md` — standalone server docs
- `MCP Server with x402.md` — x402 integration
- `MCP Toolbox.md` — MCP tools catalog
- `MCP-UI.md` — MCP UI solutions
- `MCP _ Better Auth.md` — Better Auth integration
- `Sign In With Ethereum (SIWE) _ Better Auth.md` — SIWE auth
- `x402_examples_typescript_servers_hono at main · coinbase_x402.md` — x402 examples
**Subdirs to absorb:** `z_ai/` (4 files: Vision MCP, Web Reader, Web Search, Zread)
**Firecrawl supplement:** MCP specification latest, x402 protocol docs, Better Auth docs
**Result:** Single `mcp-ecosystem-reference.md` covering MCP protocol, all server implementations, auth patterns (Better Auth, SIWE, x402), MCP-UI ecosystem, and Zread/Vision/Web Search tools.

### Merge B: `agent-frameworks-comparison.md`
**Expand:** `AGENT_IMPLEMENTATIONS_SUMMARY.md` → rename to `agent-frameworks-comparison.md`
**Root files to absorb:**
- `Agent UI Ecosystem - A2UI.md` — A2UI ecosystem survey
- `Agentic Translation Workflow Technologies.md` — Translation agents
- `Agentic Web Scraping Pipeline.md` — Web scraping patterns
- `Agentic Education Platform Development.md` — Education platform (overlap with IRISH_EDUCATION_PLATFORM_BLUEPRINT.md)
- `AI Agents for Irish Language Resources.md` — Irish language agents
- `BAML for Syllabus-Driven Data Extraction.md` — BAML syllabus extraction (overlap with BAML_COMPREHENSIVE_GUIDE.md)
- `BAML Schemas for Irish Education.md` — Irish BAML schemas (overlap)
- `BAML_DUCKDB_DRAGONFLY_ANALYSIS.md` — BAML/DB analysis (overlap)
- `baml-patterns-and-best-practices.md` — BAML patterns (overlap)
- `Agent _ Firecrawl.md` — Firecrawl agent docs
**Firecrawl supplement:** CopilotKit docs, A2UI protocol spec, Vercel AI SDK
**Result:** Single `agent-frameworks-comparison.md` covering CopilotKit vs AgentOS architecture, A2UI ecosystem, translation workflows, and web scraping agent patterns.

### Merge C: `agno-agentos-architecture.md`
**Subdirs to absorb:** `agno/` → merge stubs into `AGNO_COMPREHENSIVE_REFERENCE.md`, rename to `agno-agentos-architecture.md`
**Root files to absorb:**
- `agno_architecure_z_ai.md` — architecture comparison
- `agno-architecture-guide.md` — architecture guide
- `agno-openapi-specification-research.md` — OpenAPI research
**Firecrawl supplement:** Agno docs (AgentOS v2, multi-agent teams, AgentOS runtime)
**Result:** Single `agno-agentos-architecture.md` — the definitive Agno + AgentOS reference with architecture, OpenAPI patterns, and multi-agent patterns.

### Merge D: `web-automation-reference.md`
**Expand:** `BROWSER_AUTOMATION_PLATFORM.md` → rename to `web-automation-reference.md`
**Subdirs to absorb:** `browserbase/` (2), `smolagents/` (3), `stagehand/` (24 — merged into STAGEHAND_COMPREHENSIVE_REFERENCE.md)
**Root files to absorb:**
- `Agentic Web Scraping Pipeline.md` — overlaps with browser automation
**Firecrawl supplement:** Stagehand V3 docs, Browserbase platform, Firecrawl MCP integration
**Result:** Single `web-automation-reference.md` covering Stagehand V3, Browserbase, Smolagents deep research, and Firecrawl integration.

---

## Post-Merge Root File Map

After all merges, the `docs/agents/` directory will contain:

| File | Size | Content |
|---|---|---|
| `INDEX.md` | 50 lines | Updated index pointing to all consolidated docs |
| `agno-agentos-architecture.md` | ~800 lines | Agno SDK + AgentOS runtime (Merge C) |
| `google-adk-reference.md` | ~500 lines | Google ADK (existing, renamed) |
| `web-automation-reference.md` | ~700 lines | Stagehand, Browserbase, Smolagents, Firecrawl (Merge D) |
| `durable-execution-reference.md` | ~600 lines | Restate + DBOS (existing, renamed) |
| `baml-structured-outputs.md` | ~500 lines | BAML patterns (existing, renamed) |
| `mcp-ecosystem-reference.md` | ~800 lines | MCP protocol + servers + auth (Merge A) |
| `convex-agent-platform.md` | ~200 lines | Convex AI (existing) |
| `pydantic-ai-reference.md` | ~300 lines | Pydantic AI stack (existing, renamed) |
| `irish-education-blueprint.md` | ~400 lines | Irish EdTech platform (existing) |
| `agent-frameworks-comparison.md` | ~800 lines | CopilotKit vs AgentOS, A2UI, patterns (Merge B) |

**Total: 11 files, 0 subdirectories**

---

## Deletion Plan

| Subdir | Status | Delete After |
|---|---|---|
| `agno/` | Merged → `AGNO_COMPREHENSIVE_REFERENCE.md` → `agno-agentos-architecture.md` | After Merge C |
| `browserbase/` | Merged → `BROWSER_AUTOMATION_PLATFORM.md` | ✅ Safe to delete |
| `convex/` | Merged → `CONVEX_AGENT_PLATFORM.md` | ✅ Safe to delete |
| `durable/` | Merged → `DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md` | ✅ Safe to delete |
| `google-adk/` | Merged → `GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md` | ✅ Safe to delete |
| `pydantic_ai/` | Merged → `PYDIANTIC_AI_REFERENCE.md` | ✅ Safe to delete |
| `smolagents/` | Merged → `BROWSER_AUTOMATION_PLATFORM.md` | ✅ Safe to delete |
| `stagehand/` | Merged → `STAGEHAND_COMPREHENSIVE_REFERENCE.md` | ✅ Safe to delete |
| `z_ai/` | → `mcp-ecosystem-reference.md` | After Merge A |

---

## Root File Disposition

| Root File | Absorbed Into | Action |
|---|---|---|
| `Agent _ Firecrawl.md` | `web-automation-reference.md` | After Merge D |
| `Agent UI Ecosystem - A2UI.md` | `agent-frameworks-comparison.md` | After Merge B |
| `AGENT_IMPLEMENTATIONS_SUMMARY.md` | `agent-frameworks-comparison.md` (becomes base) | After Merge B |
| `Agentic Education Platform Development.md` | `irish-education-blueprint.md` | ✅ Already referenced |
| `Agentic Translation Workflow Technologies.md` | `agent-frameworks-comparison.md` | After Merge B |
| `Agentic Web Scraping Pipeline.md` | `web-automation-reference.md` | After Merge D |
| `agno_architecure_z_ai.md` | `agno-agentos-architecture.md` | After Merge C |
| `agno-architecture-guide.md` | `agno-agentos-architecture.md` | After Merge C |
| `agno-openapi-specification-research.md` | `agno-agentos-architecture.md` | After Merge C |
| `AI Agents for Irish Language Resources.md` | `agent-frameworks-comparison.md` | After Merge B |
| `BAML for Syllabus-Driven Data Extraction.md` | `baml-structured-outputs.md` | ✅ Already referenced |
| `BAML Schemas for Irish Education.md` | `baml-structured-outputs.md` | ✅ Already referenced |
| `BAML_DUCKDB_DRAGONFLY_ANALYSIS.md` | `baml-structured-outputs.md` | ✅ Already referenced |
| `baml-patterns-and-best-practices.md` | `baml-structured-outputs.md` | ✅ Already referenced |
| `MCP_RESEARCH.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `mcp-research-report.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `mcp-ui-gradio-evidence-integration-analysis.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `MCP Server.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `MCP Server with x402.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `MCP Toolbox.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `MCP-UI.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `MCP _ Better Auth.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `Sign In With Ethereum (SIWE) _ Better Auth.md` | `mcp-ecosystem-reference.md` | After Merge A |
| `x402_examples_typescript_servers_hono...md` | `mcp-ecosystem-reference.md` | After Merge A |

---

## Firecrawl Research Summary

| Tool/Framework | Firecrawl Result | Key Findings |
|---|---|---|
| **Agno** (docs.agno.com) | ✅ Complete | Rebranded from PhiData: AgentOS v2 runtime, multi-user sessions, RBAC, audit logs, scheduling, SDK for Python/TS |
| **Stagehand** (github.com/browserbase/stagehand) | ✅ Complete | V3: act/extract/observe API, Playwright-based, AI-native DOM interaction, Browserbase integration |
| **Google ADK** (adk.dev) | ✅ Complete | ADK 2.0: Graph workflows, 5 languages (Py/TS/Go/Java/Kotlin), Agents CLI, enterprise deployment to GCP |
| **ColPali** (github.com/illuin-tech/colpali) | ✅ Complete | v0.3.16, ColQwen3.5 (90.9 ViDoRe), ColSmol-256M (80.1), ColNetraEmbed, Plaid indexing, token pooling |
| **Restate** (not scraped) | ⏭️ Deferred | Covered by `DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md` with 30 stub files |
| **DBOS** (not scraped) | ⏭️ Deferred | Covered by durable docs |
| **BAML** (boundaryml.com) | ⚠️ Blog 404 | Primary docs at docs.boundaryml.com should be scraped in Phase 2 |
| **Pydantic AI** (not scraped) | ⏭️ Deferred | Covered by `PYDIANTIC_AI_REFERENCE.md` |
| **Convex** (not scraped) | ⏭️ Deferred | Covered by `CONVEX_AGENT_PLATFORM.md` |

---

## Execution Order

1. **Phase 1:** Delete already-merged subdirectory stubs (browserbase, convex, durable, google-adk, pydantic_ai, smolagents, stagehand) — 7 subdirs, ~85 stub files
2. **Phase 2:** Merge A (`mcp-ecosystem-reference.md`) — largest consolidation, 13 files + z_ai subdir
3. **Phase 3:** Merge B (`agent-frameworks-comparison.md`) — 10 root files
4. **Phase 4:** Merge C (`agno-agentos-architecture.md`) — 3 root files + agno subdir
5. **Phase 5:** Merge D (`web-automation-reference.md`) — 2 root files
6. **Phase 6:** Rename existing consolidated docs to standardized names
7. **Phase 7:** Update `INDEX.md` with new structure
8. **Phase 8:** Delete leftover root stub files (the 24 files absorbed into merges)

---

## Stats Summary

| Metric | Count |
|---|---|
| Total .md files currently | 131 |
| Subdirectories to flatten | 9 |
| Existing consolidated docs | 10 |
| Planned merged files (new/expanded) | 4 |
| Final file count | 11 |
| Subdirs safe to delete immediately | 7 (already merged) |
| Subdirs needing merge first | 2 (agno, z_ai) |
| Root files to absorb | 24 |
| Firecrawl scrapes completed | 6 |
