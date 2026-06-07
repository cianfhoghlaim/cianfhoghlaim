---
name: agent-docs
description: This skill should be used when working with the consolidated
  `docs/` tree at the Cianfhoghlaim monorepo root. Use when creating, updating,
  or reorganising canonical documentation; when the user asks "where do I find
  the docs for X?"; when routing a documentation query to the right canonical
  file; or when writing frontmatter for a new doc. The docs tree is organised
  into 7 numbered domain directories with a single master routing table at
  `docs/00_index.md`.
---

# Cianfhoghlaim Documentation Guide

The `docs/` tree at the repo root is the canonical documentation surface for
the entire monorepo. It is **not** organised by subproject (`oideachais/`,
`tuatha/`, `croilar/`, `meaisínfhoghlaim/`) — it is organised by **domain**.

## Quick Routing

**Always start at the master index:**

`docs/00_index.md`

It contains:

- A 31-row "I want to do X, where do I go?" routing table
- A "Documents by Domain" section listing all 36 canonical files
- A 25-row "Skill-to-Doc Mapping" table
- A "Consolidation Methodology" summary explaining the 1,038 → 36 file
  reduction

**When a user asks "where do I find docs for X?"** — consult the routing
table, then link to the canonical file.

## Frontmatter Schema (Mandatory)

Every canonical document at the root of a domain directory MUST start
with this YAML frontmatter block:

```yaml
---
title: "Human-readable title"
domain: architecture | data_platform | agents | ai_ml | web | product | standards
status: stable | draft | superseded | archived
description: "One-sentence summary"
supersedes:
  - docs/<original-subtree>/<file>.md
entities:
  - EntityName1
  - EntityName2
related_skills:
  - .agents/skills/<skill-name>/SKILL.md
ccc_query_hints:
  - "natural-language query that should return this doc"
last_reviewed: 2026-06-06
---
```

See `openspec/specs/documentation/spec.md` for the formal Requirements
and Scenarios. Key rules:

- **`domain:`** — one of 7 enum values, no free text
- **`status:`** — `stable` for production docs, `draft` for WIP,
  `superseded` if a newer doc replaces this, `archived` for historical
  reference only
- **`supersedes:`** — REQUIRED when the doc is the result of a merge.
  List every source file that was folded into this canonical
- **`entities:`** — named concepts (tools, protocols, services) the
  document discusses. Used by Cognee for entity extraction
- **`related_skills:`** — bidirectional link to agent skills that
  should load this doc
- **`ccc_query_hints:`** — the exact natural-language queries a user
  would type that should return this document. Highest-ROI field for
  ccc (CocoIndex Code) semantic search
- **`last_reviewed:`** — ISO date. Agents should prefer docs reviewed
  within 12 months

## Directory Layout (7 Numbered Domains)

| Domain | Path | What it covers |
|:--|:--|:--|
| **architecture** | `docs/01-platform-architecture/` | Platform overview, 89 Docker Compose stacks, Komodo GitOps, K8s, monorepo strategy, Pangolin networking, secrets management |
| **data_platform** | `docs/02-data-platform/` | Lakehouse architecture (DuckLake, Iceberg, Garage, R2, MotherDuck), Dagster orchestration, DLT pipelines |
| **agents** | `docs/03-agents/` | Agent frameworks (Agno, Google ADK, CopilotKit), BAML extraction, browser automation, MCP servers |
| **ai_ml** | `docs/04-ai-ml/` | Fine-tuning, OCR/HTR, RAG evaluation, knowledge graphs, vector embeddings, Celtic language AI, ML pipelines |
| **web** | `docs/05-web/` | TanStack Start frontend, Convex+Hono+BetterAuth, UI components |
| **product** | `docs/06-product/` | Celtic MMO, Crypteolas (x402/SIWE), game development, educational platform |
| **standards** | `docs/07-standards/` | Project conventions, observability patterns |

## Adding a New Canonical Document

1. **Pick the right domain** from the table above
2. **Create the file** at `docs/0N-<domain>/<kebab-case-topic>.md`
3. **Apply the frontmatter** (see schema above)
4. **Add a routing entry** in `docs/00_index.md` under the appropriate
   "I want to..." table row, and a "Documents by Domain" entry
5. **List it in the skill-to-doc mapping** if a new agent skill references it
6. **If the doc replaces older content**, move the originals to
   `docs/archive/YYYY-MM-DD-<subtree>/` and list them in `supersedes:`

## Cognee Ingestion

Canonical docs are ingested into the Cognee knowledge graph for semantic
search across the documentation. The ingestion is a two-phase flow:

- **Phase 1 (add)**: stores raw text in a Cognee dataset (no LLM)
- **Phase 2 (cognify)**: builds the knowledge graph (requires LLM)

Use the `docs:cognee` mise task or the script directly:

```bash
# Print the ingestion plan without executing
mise run docs:cognee:summary

# Ingest a single domain
mise run docs:cognee:domain standards

# Ingest all 7 domains
mise run docs:cognee
# or:
uv run python infrastructure/scripts/cognee-ingest-docs.py --all
```

Each domain becomes a Cognee dataset named `docs-<domain>` (e.g.
`docs-standards`, `docs-data-platform`, `docs-ai-ml`). The script
respects the `LLM_API_KEY` env var — if not set, it prints a warning
and skips Phase 2 (you can also pass `--no-cognify` to skip explicitly).

## Cognee MCP Server Configuration

The Cognee MCP server (`uvx cognee-mcp`) is configured in
`opencode.json`. The `LLM_API_KEY` is set to `${DEEPSEEK_API_KEY}` so
it picks up the mise-hydrated key from `.env` at subprocess launch.
On the FIRST session start, the LLM key must be set in `.env`:

```bash
# In .env (mise-hydrated, NEVER edit by hand)
DEEPSEEK_API_KEY=sk-...   # used by Cognee as LLM_API_KEY
```

## Reading the Audit Reports

Four discovery audits from the 2026-06-06 consolidation are preserved
in `docs/audit/`:

- `docs/audit/discovery_inventory.md` — full file inventory of the
  pre-consolidation tree (1,038 files, 49.7 MiB, 12-cluster
  proposal)
- `docs/audit/cognee_readiness_audit.md` — what makes a doc
  cognify-clean, per-domain graph_model_file patterns
- `docs/audit/cocoindex_readiness_audit.md` — ccc indexing coverage,
  frontmatter convention, query hint strategy
- `docs/audit/agent_skill_consumability.md` — what makes docs
  consumable by agent skills (frontmatter fields, routing tables)
- `docs/audit/consolidation_plan.md` — full retrospective plan with
  the migration map

## Archive Policy

All merged-into-canonical originals are preserved in
`docs/archive/YYYY-MM-DD-<subtree>/` with their content unchanged. The
canonical file's `supersedes:` field lists the original paths so the
provenance is traceable. **No content is lost in a merge.**

## When NOT to Use This Skill

- If the user is asking about **code** (not docs), use `.agents/skills/ccc/`
  for semantic code search
- If the user is asking about a **specific subproject** (oideachais,
  tuatha, croilar, meaisínfhoghlaim), use the subproject's README in
  addition to the docs/ tree — READMEs describe the code; docs/
  describe the patterns
- If the user is asking about **infrastructure** (Docker, Komodo,
  Pangolin), prefer `infrastructure/README.md` and
  `infrastructure/AGENTS.md` over `docs/01-platform-architecture/`,
  since the latter is the canonical narrative while the former are
  operational entry points

## Quick Reference

- **Master index**: `docs/00_index.md`
- **Cognee ingestion script**: `infrastructure/scripts/cognee-ingest-docs.py`
- **Cognee MCP server**: `.agents/skills/cognee/SKILL.md`
- **ccc search**: `bun run ccc:search "<query>"`
- **Mise task**: `mise run docs:cognee`
- **OpenSpec capability spec**: `openspec/specs/documentation/spec.md`
- **OpenSpec change**: `openspec/changes/docs-restructuring/`
- **Audit reports**: `docs/audit/*.md`
