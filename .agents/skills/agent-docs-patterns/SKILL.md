---
name: agent-docs-patterns
description: The canonical frontmatter schema for Cianfhoghlaim agent-consumable documentation — `title`, `domain` (7 enum values), `status` (4 lifecycle states), `read_when` (gerund-phrase routing directives), `related_skills` (bidirectional back-links), `ccc_query_hints` (natural-language search seeds), and `entities` (named tools/protocols/services). The companion `agent-docs` skill router pattern: frontmatter → auto-generated index → per-skill routing. Use when authoring a new doc, adding frontmatter to an existing doc, building an auto-generated routing index, integrating with the `agent-docs` skill loader, or asking "what frontmatter does a Cianfhoghlaim doc need?" / "which `domain` enum should this doc use?" / "how do I link a doc to the agent skills that consume it?".
---

# Agent Docs Patterns

## When to use this skill

Use when you need to:

- "Author a new Cianfhoghlaim doc with the canonical
  frontmatter"
- "Pick the right `domain` enum value for a doc"
- "Add `read_when` routing directives so agents can find
  the doc at the right time"
- "Add `related_skills` back-links to a doc"
- "Add `ccc_query_hints` natural-language seeds for the
  semantic index"
- "Generate the master routing index (`docs/00_index.md`)
  from frontmatter"
- "Understand the 4-state lifecycle (`draft` / `stable` /
  `superseded` / `archived`)"
- "Distinguish the Cianfhoghlaim frontmatter from the
  dagster/erk `agent-docs` skill (different scope)"

## Overview

The **agent-docs-patterns** skill encodes the canonical
Cianfhoghlaim frontmatter schema for
**agent-consumable documentation**. The schema was defined
in the round-1 `docs/02-audit/agent_skill_consumability.md`
audit and is the result of a 10-file sample that found
**0 of 10 docs carried any agent-routing frontmatter** —
the discovery that triggered the 2026-06-06 docs
consolidation.

The schema has 12 fields, of which 3 are **required** and
9 are **optional**. The required fields (`title`, `domain`,
`status`) make a doc discoverable in the routing index; the
optional fields (`read_when`, `related_skills`,
`ccc_query_hints`, `entities`, `supersedes`, `superseded_by`,
`last_reviewed`, `description`, `tags`, `sources`) wire the
doc into the agent ecosystem (semantic search, skill
back-links, lifecycle tracking).

The companion pattern is the **auto-generated routing
index** — instead of a hand-maintained `docs/INDEX.md`
(which rots), a `docs:sync` script reads every file's
frontmatter, validates the required fields, and emits
`docs/00_index.md` with a routing table, a per-domain
document list, and a skill-to-doc map. This is the same
pattern the dagster/erk `agent-docs` skill uses (different
scope, different fields), hence the skill name.

## The 12-field frontmatter schema

| Field | Type | Required | Purpose |
|:--|:--|:--|:--|
| `title` | string | **Yes** | Human-readable title. Used in index generation. |
| `domain` | enum | **Yes** | Primary domain. Controls which skill router picks up the doc. |
| `status` | enum | **Yes** | `draft` / `stable` / `superseded` / `archived`. Agents prefer `stable`; skip `archived`. |
| `read_when` | list[string] | No | Gerund phrases describing when an agent should load this doc. **Primary routing mechanism.** |
| `description` | string | No | 1-sentence summary for index listings. |
| `supersedes` | list[path] | No | List of doc paths this doc replaces. Enables dedup. |
| `superseded_by` | path | No | If this doc is outdated, what replaced it. |
| `last_reviewed` | date | No | ISO date. Agents can skip docs unreviewed >12 months. |
| `entities` | list[string] | No | Named entities (tools, protocols, services) discussed. Enables entity-based search. |
| `related_skills` | list[string] | No | Agent skill names that should load this doc. **Bidirectional link.** |
| `ccc_query_hints` | list[string] | No | Natural-language queries that should return this doc. Feeds the ccc semantic index. |
| `sources` / `tags` | list[object / string] | No | Freeform metadata (URLs, cross-cutting concerns). |

## The 7 `domain` enum values

| Value | Scope | Example docs/ subtree |
|:--|:--|:--|
| `data_platform` | Data pipelines, lakehouse, orchestration, DLT, DuckDB | `data_engineering/` |
| `ai_ml` | Fine-tuning, embeddings, OCR, RAG, model serving | `meaisínfhoghlaim/`, `teanga/` |
| `agents` | Agent frameworks, MCP, browser automation, AG-UI | `agents/`, `codebase_indexing/` |
| `web` | Frontend frameworks, SSR, edge compute, auth | `web/` |
| `product` | Educational platform, MMO game, media stack | `tuatha/`, `media/` |
| `architecture` | System architecture, deployment, CI/CD | `bonneagar/`, root-level arch docs |
| `standards` | Conventions, AGENTS.md, coding standards, project identity | `context/00-core/` |

The 7 values correspond to the **7 numbered domains** in
the post-2026-06-06 docs tree (`00-core/`,
`01-platform-architecture/`, `02-data-platform/`, `03-agents/`,
`04-ai-ml/`, `05-web/`, `06-product/`, `07-standards/`).
A doc's `domain` field should match the subtree it lives
in.

## The 4 `status` enum values + agent behaviour

| Value | Meaning | Agent behaviour |
|:--|:--|:--|
| `draft` | Work in progress | Skip unless explicitly requested |
| `stable` | Reviewed, accurate, current | **Preferred source** |
| `superseded` | Replaced by another doc | Show warning, redirect to `superseded_by` |
| `archived` | Historical reference only | Skip unless explicitly requested |

The 4 values form a one-way lifecycle:
`draft → stable → superseded → archived`. The
`superseded_by` field is the link from `superseded` →
its replacement; agents follow it before reading the body.

## The `read_when` routing directive (gerund phrases)

`read_when` is the **primary mechanism** that lets an agent
discover a doc at the right time. Each entry is a gerund
phrase (verb + object) describing the situation:

```yaml
read_when:
  - planning cross-border credential work
  - reviewing DLT sources for NCCA / SEC / CCEA / Ofqual / DfE
  - building a micro-credential issuer
  - debugging DID resolution
```

The `read_when` text is matched against the **agent's
current task description** (LLM fuzzy match, top-K). The
top-scoring doc is loaded; the others are skipped. Good
`read_when` phrases are **specific, task-shaped, and
verb-led** — "planning X" / "debugging Y" / "reviewing Z"
/ "adding a new W".

## The `related_skills` bidirectional link

`related_skills` is a **bidirectional** link: the doc says
"these agent skills should load me", and the agent skill
says "this doc is a reference" in its own `## References`
section. The Cianfhoghlaim convention is **paths**, not
just names — so the index can render a clickable link:

```yaml
related_skills:
  - .agents/skills/dlt/SKILL.md
  - .agents/skills/baml/SKILL.md
  - .agents/skills/cognee/SKILL.md
```

A doc with `related_skills` populated appears in the
skill's `## References` section automatically when the
auto-index is generated.

## The `ccc_query_hints` (semantic search seeds)

`ccc_query_hints` is the bridge from frontmatter to the
`ccc` (CocoIndex Code) semantic search index. Each entry
is a natural-language query that should return the doc:

```yaml
ccc_query_hints:
  - cianfhoghlaim documentation index
  - which doc to read
  - ccc cocoindex-code search
  - dagster asset partition definition
```

When the doc is ingested, the hints are stored alongside
the chunk embeddings; a search query that matches a hint
boosts the doc's relevance score. The hint text is the
**same natural language** an agent would use in a
`ccc search "<query>"` call.

## The `agent-docs` skill router pattern

The Cianfhoghlaim pattern is **synthesised** from the
dagster/erk `agent-docs` skill (which targets
`.erk/docs/agent/`, a different scope). The KCG version:

1. **Frontmatter on every doc** — `title`, `domain`,
   `status` are required; the rest are optional
2. **Auto-generated index** — `docs:sync` script (akin to
   `erk docs sync`) reads every doc's frontmatter,
   validates the schema, and emits `docs/00_index.md`
3. **Per-category index summaries** — the index is split
   by `domain` value; each domain has its own routing
   table
4. **Bidirectional skill↔doc links** — `related_skills`
   in the doc frontmatter, `## References` in the
   skill body
5. **ccc integration** — `ccc_query_hints` feed the
   semantic search index
6. **Lifecycle tracking** — `status` + `supersedes` /
   `superseded_by` + `last_reviewed` make the
   corpus self-cleaning

The reference at `references/frontmatter-schema.md` is the
full 372-line round-1 audit report that motivated this
schema — it carries the original 10-file audit, the gap
analysis, and the 4-phase rollout plan (Phase 1: frontmatter
on INDEX.md files → Phase 2: skill back-linking → Phase 3:
`docs:sync` automation → Phase 4: full coverage of the
300+ file corpus).

## Worked example (a complete doc header)

```yaml
---
title: 'Deploy Plan 01 — Micro-Credentials & Cross-Border Equivalence Ledger'
domain: deploy-plan
status: draft
description: 'W3C Verifiable Credentials + DIDs for ROI↔UK NFQ↔RQF micro-credentials.'
read_when:
  - planning cross-border credential work
  - reviewing DLT sources for NCCA / SEC / CCEA / Ofqual / DfE
  - building a micro-credential issuer
supersedes: []
superseded_by: []
related_skills:
  - .agents/skills/baml/SKILL.md
  - .agents/skills/dlt/SKILL.md
  - .agents/skills/lancedb/SKILL.md
  - .agents/skills/cognee/SKILL.md
entities:
  - W3C VerifiableCredentials
  - DID (did:key, did:web)
  - PocketID
  - BAML EquivalenceAssertion
ccc_query_hints:
  - micro-credentials cross-border
  - NFQ RQF equivalence
  - verifiable credentials DID
  - W3C VC JSON-LD
last_reviewed: '2026-06-13'
---
```

## What to avoid

| Anti-pattern | Why it fails |
|:--|:--|
| Frontmatter with only `title` | The doc is invisible to the routing index (missing `domain` + `status`) |
| `read_when` entries that are nouns, not gerunds | Agents match on the verb (the *action* being performed) |
| `related_skills` listing only skill names (no path) | Index can't render a clickable link |
| `supersedes` populated but `superseded_by` empty on the reverse | Dedup graph is one-way; the reverse-doc never gets pointed back |
| `status: stable` on an un-reviewed doc | Agents trust the doc; the doc lies |
| `ccc_query_hints` that are the doc's title verbatim | No semantic value; only the natural-language queries the doc *should match* |

## Cross-references

- `.agents/skills/dagster/erk-skills/agent-docs/SKILL.md` —
  the dagster/erk `agent-docs` skill (the source of the
  pattern; different scope)
- `references/frontmatter-schema.md` — the full 372-line
  round-1 audit report (the 10-file frontmatter sample,
  the gap analysis, the 4-phase rollout plan)
- `docs/00_index.md` — the master routing index (auto-generated
  from frontmatter)
- `oideachais/sources.yaml` — the source registry using
  a Cognee-clean frontmatter variant
- `openspec/AGENTS.md` — the OpenSpec workflow (its
  capability spec frontmatter is a different schema)
- `kcg-docs-consolidation/SKILL.md` — the round-1
  retrospective that produced the 1,038 → 36 file
  consolidation and the frontmatter requirement
