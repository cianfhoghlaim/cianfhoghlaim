# docs/ Agent Skill Consumability Audit

> **Date:** 2026-06-06 | **Auditor:** Agent Skill Consolidation Project

## 1. Reference Skill Analysis

### 1.1 `agent-docs` Skill (from dagster/erk)

- **Path:** `.agents/skills/dagster/erk-skills/agent-docs/SKILL.md`
- **Target scope:** `.erk/docs/agent/` (erk-internal documentation)
- **Frontmatter standard:**
  - Required: `title` (string), `read_when` (list of gerund phrases — "creating a plan", "fixing merge conflicts")
  - Optional: `tripwires` (list of `{action, warning}` pairs)
  - No other YAML keys permitted
- **Index generation:** Auto-generated from frontmatter via `erk docs sync` — index files (including per-category `index.md`) must NOT be edited manually
- **Category placement rules:** Match by topic → match by related docs → fall back to root → create new category when 3+ related docs exist at root
- **Routing:** Quick Navigation tables in index files with "When you need to... | Read this" pattern
- **Code in docs:** Strict rule against embedding Python functions that process erk data or encode business logic

### 1.2 `skill-creator` Skill

- **Frontmatter standard:** `name` + `description` only. The `description` IS the trigger mechanism.
- **Description convention:** "Comprehensive [what it does]. Use when [specific triggers and contexts]."
- **Progressive disclosure:** Metadata (always in context) → body (<5k words, loaded on trigger) → bundled resources (loaded on demand)
- **Key design principle:** Information lives in either SKILL.md or references files, never both
- **Reference files:** Documentation loaded only when Claude determines it's needed; files >10k words should have grep patterns in SKILL.md

### 1.3 `irish-edtech` Skill (Domain-Specific)

- **Trigger phrases:**
  - "Build a Leaving Cert study platform"
  - "Process Irish curriculum documents"
  - "Create bilingual educational content"
  - "Extract exam questions with BAML"
  - "Build knowledge graphs for education"
- **References:** No docs/ references in the skill body. Uses external URLs (curriculumonline.ie, examinations.ie, etc.) and inlined schemas/patterns.
- **Docs it SHOULD reference but doesn't:**
  - `docs/teanga/INDEX.md` — Celtic language AI resources
  - `docs/meaisínfhoghlaim/` — ML/fine-tuning patterns
  - `docs/bonneagar/` — infrastructure patterns for deployment
  - `docs/context/05-celtic-language/` — structured context

## 2. Frontmatter Audit — Sampled docs/ Files

**Method:** Sampled 10 files across the 7 primary subtrees plus root-level docs.

| # | File | Subtree | Has Frontmatter? | Content |
|---|------|---------|-------------------|---------|
| 1 | `docs/bonneagar/lakehouse-architecture.md` | bonneagar | **No** | `# Real-Time Open Data Lakehouse Architecture` |
| 2 | `docs/bonneagar/TECH_STACK.md` | bonneagar | **No** | `[dev] mise ...` (TOML-style) |
| 3 | `docs/bonneagar/knowledge-graph-schema.md` | bonneagar | **No** | `# Cryptocurrency Knowledge Graph Schema` |
| 4 | `docs/bonneagar/frontend-stack.md` | bonneagar | **No** | `# Frontend Stack for Irish Education Platform` |
| 5 | `docs/bonneagar/INDEX.md` | bonneagar | **No** | `# Bonneagar — Infrastructure Research Index` |
| 6 | `docs/ARCHITECTURE_RATIONALE.md` | root | **No** | `# Sovereign Educational Infrastructure: Architecture Rationale` |
| 7 | `docs/ARCHITECTURE_DEPLOYMENT.md` | root | **No** | `# Architecture & End-to-End Deployment Guide` |
| 8 | `docs/BROWSERBASE_MCP_VERTEX_PATCH_NOTES.md` | root | **No** | `# Browserbase MCP + Google Vertex AI Patch Notes` |
| 9 | `docs/media/lower_socioeconomic_piracy.md` | media | **No** | `# Lower Socioeconomic Piracy: A Budget Media Stack` |
| 10 | `docs/codebase_indexing/chunkhound-comprehensive-research.md` | codebase_indexing | **No** | `# ChunkHound: Comprehensive Research and Integration Guide` |
| 11 | `docs/tuatha/celtic_mmo.md` | tuatha | **No** | `# Building an "Anam" Celtic educational MMO...` |
| 12 | `docs/tuatha/ADDING_AGENTS.md` | tuatha | **No** | `# Adding New Agents` |
| 13 | `docs/team-workflow-stack/2026-06-06-migration.md` | team-workflow-stack | **No** | `# Team Workflow Stack — Migration Report` |
| 14 | `docs/opencode-design-patterns-ontology.md` | openspec | **No** | N/A (not shown but: no frontmatter from grep) |

**Result: 0 of 10+ sampled files have agent-consumable YAML frontmatter.**

**Exception:** Files under `docs/tuatha/tuatha/` (cloned upstream repo content) DO have frontmatter using an Obsidian/Notes clipping format:
```yaml
---
title: "SpacetimeDB"
source: "https://spacetimedb.com/install"
author:
published:
created: 2025-12-15
description: "Multiplayer at the speed of light."
tags:
  - "clippings"
---
```
This is NOT the `agent-docs` format and does not contain `read_when` routing directives.

### 2.1 Index File Analysis

9 INDEX.md files found (all manual, none auto-generated):

| Index | Manually maintained? | Has routing table? | Frontmatter? |
|-------|---------------------|-------------------|--------------|
| `docs/INDEX.md` | Yes | Yes ("Search Quick Reference") | No |
| `docs/bonneagar/INDEX.md` | Yes | No (list of merged guides) | No |
| `docs/data_engineering/INDEX.md` | Yes | No | No |
| `docs/agents/INDEX.md` | Yes | No | No |
| `docs/context/INDEX.md` | Yes | No | No |
| `docs/tuatha/INDEX.md` | Yes | No | No |
| `docs/web/INDEX.md` | Yes | No | No |
| `docs/teanga/INDEX.md` | Yes | No | No |
| `docs/meaisínfhoghlaim/INDEX.md` | Yes | No | No |
| `docs/old/INDEX.md` | Yes | No | No |

None of the INDEX files have frontmatter or auto-generation capability. They will rot.

## 3. Skill-to-docs Mapping

Which agent skills could/should reference docs/ content:

### Skills WITH existing docs references

| Skill | Docs referenced now | Gap |
|-------|-------------------|-----|
| `irish-edtech` | None explicitly (uses inlined schemas + external URLs) | Should reference `docs/teanga/`, `docs/context/05-celtic-language/`, `docs/bonneagar/frontend-stack.md` |
| `oideachas-pipeline` | None explicitly | Should reference `docs/data_engineering/ARCHITECTURE.md`, `docs/data_engineering/DLT_COMPLETE_GUIDE.md` |
| `dagster` | None explicitly (has own bundled references) | Should reference `docs/data_engineering/dagster/` |
| `dlt` | Routes to sub-skills (`create-filesystem-pipeline`, `create-rest-api-pipeline`) | Should reference `docs/data_engineering/dlt/` |

### Skills that SHOULD gain docs/ sections

| Skill | Domain | New docs/ section needed | Priority |
|-------|--------|------------------------|----------|
| `irish-edtech` | Education platform | `docs/celtic-education/` or formalize `docs/teanga/` + `docs/context/05-celtic-language/` | High |
| `dagster` + `dlt` + `add-incremental-loading` | Data pipelines | `docs/data_engineering/` already exists but needs frontmatter | High |
| `motherduck-*` (all 14 sub-skills) | Analytics/storage | `docs/data_engineering/ducklake/`, `docs/data_engineering/data-engineering/` need frontmatter | Medium |
| `cocoindex` + `ccc` | Code indexing | `docs/codebase_indexing/` already exists but needs frontmatter | Medium |
| `lancedb` | Vector DB | `docs/data_engineering/lance/` needs frontmatter | Medium |
| `cognee` | Knowledge graphs | `docs/cognee/` needs frontmatter | Medium |
| `graphiti` + `graphiti-core` | Temporal KG | `docs/meaisínfhoghlaim/`, `docs/bonneagar/knowledge-graph-schema.md` need frontmatter | Medium |
| `falkordb` | Hybrid vector/graph | `docs/bonneagar/knowledge-graph-infrastructure.md` needs frontmatter | Low |
| `pangolin` + `komodo` | Infrastructure | `docs/bonneagar/PANGOLIN_COMPLETE_GUIDE.md`, `docs/bonneagar/KOMODO_COMPLETE_GUIDE.md` need frontmatter | Medium |
| `duckdb` + `ducklake` | Analytics DB | `docs/data_engineering/ARCHITECTURE.md` needs frontmatter | Medium |
| `stack-ops` | Docker Compose stacks | `docs/bonneagar/DOCKER_COMPOSE_ARCHITECTURE.md` needs frontmatter | Medium |
| `browser` + `browserbase-cli` + `safe-browser` | Browser automation | `docs/chrome-devtools-mcp/` has SKILL_CONTEXT.md but no frontmatter | Medium |
| `firecrawl-*` (all 9 sub-skills) | Web scraping | `docs/bonneagar/agentic-scraping-architecture.md`, `docs/bonneagar/web-scraping-automation.md` need frontmatter | Low |
| `build-notebook` + `explore-data` | Analytics notebooks | `docs/notebooks/README.md` needs frontmatter | Low |
| `frontend-design` + `web-artifacts-builder` | UI | `docs/web/INDEX.md` needs frontmatter | Low |
| `google-adk` + `agno` | Agent frameworks | `docs/agents/INDEX.md` needs frontmatter | Medium |
| `document-intelligence` + `docx` + `pdf` + `xlsx` | Document processing | No dedicated docs/ section yet | Low |
| `tuatha` (MMO) | Game dev | `docs/tuatha/INDEX.md` needs frontmatter | Medium |
| `celtic-language-ai` | Language AI | `docs/meaisínfhoghlaim/celtic/` needs frontmatter | High |

**Key finding:** ~40 agent skills exist. ~25 could benefit from frontmatter-enabled docs/ sections. Zero currently have structured frontmatter that an agent skill router can consume.

## 4. Proposed Frontmatter Schema

Adapted from the `agent-docs` standard and extended for the broader docs/ corpus:

```yaml
---
# REQUIRED
title: "Lakehouse Architecture"
domain: data_platform
status: stable

# OPTIONAL — Discoverability
read_when:
  - "designing a data lakehouse"
  - "comparing OLake vs Fivetran"
  - "setting up RisingWave CDC pipelines"
description: "Reference architecture for OLake + Lakekeeper + RisingWave lakehouse."

# OPTIONAL — Lifecycle
supersedes:
  - docs/data_engineering/old/old-lakehouse.md
superseded_by:
last_reviewed: 2026-06-01

# OPTIONAL — Entity linking
entities:
  - olake
  - lakekeeper
  - risingwave

# OPTIONAL — Skill routing
related_skills:
  - dagster
  - dlt
  - motherduck-ducklake
ccc_query_hints:
  - "lakehouse architecture"
  - "CDC pipeline OLake"
  - "RisingWave streaming"

# OPTIONAL — Provenance
sources:
  - url: https://example.com/olake-docs
    description: "OLake upstream documentation"

# OPTIONAL — Categorization
tags:
  - streaming
  - lakehouse
  - CDC
---
```

### Field Definitions

| Field | Type | Required | Purpose |
|-------|------|----------|---------|
| `title` | string | **Yes** | Human-readable title. Used in index generation. |
| `domain` | enum | **Yes** | Primary domain. Controls which skill router picks up the doc. |
| `status` | enum | **Yes** | `draft`, `stable`, `superseded`, `archived`. Agents should prefer `stable`, ignore `archived`. |
| `read_when` | list[string] | No | Gerund phrases describing when an agent should load this doc. PRIMARY routing mechanism. |
| `description` | string | No | 1-sentence summary for index listings. |
| `supersedes` | list[path] | No | List of doc paths this doc replaces. Enables dedup. |
| `superseded_by` | path | No | If this doc is outdated, what replaced it. |
| `last_reviewed` | date | No | ISO date. Agents can skip docs unreviewed >12 months. |
| `entities` | list[string] | No | Named entities (tools, protocols, services) discussed. Enables entity-based search. |
| `related_skills` | list[string] | No | Agent skill names that should load this doc. Bidirectional link. |
| `ccc_query_hints` | list[string] | No | Natural-language queries that should return this doc. Feeds into ccc indexing. |
| `sources` | list[object] | No | URLs + descriptions of upstream sources. |
| `tags` | list[string] | No | Freeform tags for cross-cutting concerns. |

### `domain` Enum Values

| Value | Scope | Example docs/ subtree |
|-------|-------|---------------------|
| `data_platform` | Data pipelines, lakehouse, orchestration, DLT, DuckDB | `data_engineering/` |
| `ai_ml` | Fine-tuning, embeddings, OCR, RAG, model serving | `meaisínfhoghlaim/`, `teanga/` |
| `agents` | Agent frameworks, MCP, browser automation, AG-UI | `agents/`, `codebase_indexing/` |
| `web` | Frontend frameworks, SSR, edge compute, auth | `web/` |
| `product` | Educational platform, MMO game, media stack | `tuatha/`, `media/` |
| `architecture` | System architecture, deployment, CI/CD | `bonneagar/`, root-level arch docs |
| `standards` | Conventions, AGENTS.md, coding standards, project identity | `context/00-core/` |

### `status` Enum Values

| Value | Meaning | Agent behavior |
|-------|---------|---------------|
| `draft` | Work in progress | Skip unless explicitly requested |
| `stable` | Reviewed, accurate, current | Preferred source |
| `superseded` | Replaced by another doc | Show warning, redirect to `superseded_by` |
| `archived` | Historical reference only | Skip unless explicitly requested |

## 5. Proposed `docs/00_index.md` Structure

A single master index at `docs/00_index.md` that agent skills can route against. Generated from frontmatter (not manually maintained).

```markdown
---
title: "Cianfhoghlaim Documentation Index"
domain: standards
status: stable
read_when:
  - "starting any task in this codebase"
  - "looking for documentation on a specific topic"
  - "unsure which doc to read"
---

# Cianfhoghlaim Documentation Index

> Auto-generated from frontmatter. Do not edit.
> Last generated: 2026-06-06T12:00:00Z

## Routing Table

| When you need to... | Read this | Domain | Status |
|---------------------|-----------|--------|--------|
| design a data lakehouse | `data_engineering/ARCHITECTURE.md` | data_platform | stable |
| set up DLT pipelines | `data_engineering/DLT_COMPLETE_GUIDE.md` | data_platform | stable |
| understand Dagster assets | `data_engineering/dagster/...` | data_platform | stable |
| fine-tune an Irish LLM | `meaisínfhoghlaim/fine-tuning-reference.md` | ai_ml | stable |
| process Irish curriculum docs | `teanga/INDEX.md` | ai_ml | stable |
| integrate Pangolin reverse proxy | `bonneagar/PANGOLIN_COMPLETE_GUIDE.md` | architecture | stable |
| deploy with Komodo | `bonneagar/KOMODO_COMPLETE_GUIDE.md` | architecture | stable |
| add an MCP server | `agents/MCP_COMPREHENSIVE_RESEARCH.md` | agents | stable |
| build a TanStack Start app | `web/INDEX.md` | web | stable |
| design a Celtic MMO | `tuatha/celtic_mmo.md` | product | stable |
| understand project architecture | `ARCHITECTURE_RATIONALE.md` | architecture | stable |
| deploy to production | `ARCHITECTURE_DEPLOYMENT.md` | architecture | stable |

## Documents by Domain

### data_platform (N docs)
- `data_engineering/ARCHITECTURE.md` — 6-layer architecture...
- `data_engineering/DLT_COMPLETE_GUIDE.md` — DLT pipeline patterns...
- ...

### ai_ml (N docs)
- ...

## Skill-to-Doc Mapping

| Skill | Primary Doc(s) |
|-------|---------------|
| `dagster` | `data_engineering/ARCHITECTURE.md`, `data_engineering/dagster/` |
| `dlt` | `data_engineering/DLT_COMPLETE_GUIDE.md` |
| `irish-edtech` | `teanga/INDEX.md`, `context/05-celtic-language/` |
| `celtic-language-ai` | `meaisínfhoghlaim/celtic/CELTIC_LANGUAGES_AI_RESOURCES.md` |
| `pangolin` | `bonneagar/PANGOLIN_COMPLETE_GUIDE.md` |
| `komodo` | `bonneagar/KOMODO_COMPLETE_GUIDE.md` |
| ... | ... |
```

## 6. Gap Analysis

### Current State (June 2026)

| Capability | Status | Detail |
|-----------|--------|--------|
| Frontmatter on docs/ files | **None** | 0 of ~10 sampled files across 7 subtrees have YAML frontmatter |
| `read_when` routing directives | **None** | No file has agent-consumable trigger conditions |
| Auto-generated indexes | **None** | 9 manual INDEX.md files exist; none can regenerate from frontmatter |
| Status/lifecycle tracking | **None** | No way to distinguish stable docs from superseded ones |
| Skill-to-doc mapping | **None** | Agent skills reference no docs/ paths; docs mention no skill names |
| Entity-based search | **None** | No `entities` field to link docs to specific tools/protocols |
| CCC query hints | **Partial** | `docs/INDEX.md` has a manual "Search Quick Reference" table, not tied to frontmatter |
| Routing table (AGENTS.md-style) | **None** | Only `docs/INDEX.md` has "Search Quick Reference"; no skill-consumable routing table exists |

### What Must Change

To make every docs/ file discoverable by an agent skill, the following changes are needed:

#### Phase 1: Foundation (must happen first)

1. **Add frontmatter to all INDEX.md files** (9 files). Minimum required: `title`, `domain`, `status`. This enables category-level routing immediately.
2. **Create `docs/00_index.md`** as the master routing index generated from frontmatter.
3. **Add frontmatter to top-priority docs** — start with:
   - `docs/ARCHITECTURE_RATIONALE.md` (`domain: architecture`)
   - `docs/ARCHITECTURE_DEPLOYMENT.md` (`domain: architecture`)
   - `docs/data_engineering/ARCHITECTURE.md` (`domain: data_platform`)
   - `docs/data_engineering/DLT_COMPLETE_GUIDE.md` (`domain: data_platform`)
   - `docs/meaisínfhoghlaim/fine-tuning-reference.md` (`domain: ai_ml`)
   - `docs/meaisínfhoghlaim/celtic/CELTIC_LANGUAGES_AI_RESOURCES.md` (`domain: ai_ml`)
   - `docs/bonneagar/PANGOLIN_COMPLETE_GUIDE.md` (`domain: architecture`)
   - `docs/bonneagar/KOMODO_COMPLETE_GUIDE.md` (`domain: architecture`)
   - `docs/agents/MCP_COMPREHENSIVE_RESEARCH.md` (`domain: agents`)

#### Phase 2: Skill Backlinking

4. **Update agent SKILL.md files** to reference docs/ paths in a `## References` section at the bottom. Follow the `skill-creator` progressive disclosure pattern:
   ```markdown
   ## References
   - Data pipeline architecture: See `docs/data_engineering/ARCHITECTURE.md`
   - DLT pipeline patterns: See `docs/data_engineering/DLT_COMPLETE_GUIDE.md`
   ```
5. **Add `related_skills` field** to docs/ frontmatter, creating bidirectional links.

#### Phase 3: Automation

6. **Write a `docs:sync` script** (equivalent to `erk docs sync`) that:
   - Scans all docs/ for YAML frontmatter
   - Validates required fields
   - Generates `docs/00_index.md` with routing table
   - Generates per-category index summaries
   - Reports files missing frontmatter
7. **Add to `turbo.json`** as `docs:sync` task.
8. **Add pre-commit hook** that warns on undocumented files.

#### Phase 4: Full Coverage

9. **Audit all remaining docs/ files** (est. 300+) for frontmatter addition.
10. **Identify and archive superseded docs** using `status: superseded` + `superseded_by`.
11. **Integrate with ccc indexing** — use `ccc_query_hints` frontmatter to improve code search relevance.

### Estimated Effort

| Phase | Files affected | Effort |
|-------|---------------|--------|
| Phase 1: Foundation | ~15 files | 1 session |
| Phase 2: Skill Backlinking | ~40 SKILL.md files + ~15 docs | 2 sessions |
| Phase 3: Automation | 1 new script + turbo config | 1 session |
| Phase 4: Full Coverage | ~300 docs/ files | 3-4 sessions |

**Total:** ~8 sessions for complete agent-consumable documentation.

### Critical Risks

- **Manual index rot:** Current INDEX.md files are already stale in places (e.g., `docs/data_engineering/INDEX.md` references merged guides that may not exist anymore). Without auto-generation, this will only get worse.
- **Skill-to-docs disconnect:** Agent skills (100+) and docs/ files (300+) are two disconnected graphs. Agents cannot discover relevant docs without explicit references.
- **No freshness signal:** Without `last_reviewed` or `status` fields, agents have no way to know if a doc is current. An agent reading a 2024 doc about a 2026 stack will produce wrong results.
- **Duplication risk:** Without `supersedes`/`superseded_by`, multiple docs on the same topic coexist, and agents may read the wrong one.
