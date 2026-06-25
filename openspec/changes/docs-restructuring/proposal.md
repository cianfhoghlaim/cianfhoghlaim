# Change: docs-restructuring

## Why

The `docs/` tree grew organically across 8 subtrees (`agents/`, `bonneagar/`,
`context/`, `data_engineering/`, `meaisínfhoghlaim/`, `teanga/`, `web/`,
`sruth/tuatha/`) with 1,038 files totalling 49.7 MiB. This created three concrete
problems:

1. **Discoverability** — agents and humans could not route a question like
   "how do I add a Dagster asset?" to the right file because the same topic
   lived in 4-5 overlapping files spread across 3 subtrees.
2. **Indexing bloat** — the ccc (CocoIndex Code) search index was carrying
   near-duplicate vectors, with one test query ("ADK agent routing")
   returning 4 identical chunks from different files.
3. **No machine-readable structure** — 0 of 1,038 files had `domain:` or
   `status:` frontmatter, so Cognee and agent-skill routing had no metadata
   to work with.

## What Changes

- **Reorganize** `docs/` from 8 unstructured subtrees into 7 numbered
  domain directories (`01-platform-architecture/` through
  `07-standards/`) with one README.md index per domain.
- **Consolidate** 1,038 source files into **36 canonical documents** through
  heavy merge. Any file with >50% topic overlap is folded into a single
  canonical; the merged originals are preserved in `docs/archive/2026-06-06-*/`
  with their content intact.
- **Add frontmatter** to every canonical document with a fixed schema
  (title, domain, status, description, supersedes, entities, related_skills,
  ccc_query_hints, last_reviewed) that makes the docs simultaneously
  Cognee-cognify-ready, ccc-indexable, and agent-skill-consumable.
- **Add `docs/00_index.md`** — a single master routing table that maps
  "I want to do X, where do I go?" → canonical file, with a separate
  skill-to-doc mapping covering 25 agent skills.
- **Add `infrastructure/scripts/cognee-ingest-docs.py`** — a two-phase
  ingestion script that reads all canonical docs, stores them in Cognee
  via the REST API, and triggers per-dataset `cognify()` to build the
  knowledge graph.
- **Fix `opencode.json`** — replace the unresolved `infisical://` template
  string in the Cognee MCP server's `LLM_API_KEY` with `${DEEPSEEK_API_KEY}`
  so the mise-hydrated key is picked up at subprocess launch.
- **Remove** the 8 old subtree directories (`agents/`, `bonneagar/`,
  `context/`, `data_engineering/`, `meaisínfhoghlaim/`, `teanga/`, `web/`,
  `sruth/tuatha/`) and the 116-file nested `sruth/tuatha/sruth/tuatha/` mirror.

## Impact

- **Affected specs**: none directly; this is a docs/ restructure, not a
  capability change. The canonical docs themselves may eventually become
  inputs to spec changes (e.g. a future `docs-cognee-graph` change may
  propose typed graph models for each domain).
- **Affected code**: nothing runtime; only metadata + archive structure.
- **Affected agent skills**: all skills that previously referenced files
  under `docs/{agents,bonneagar,context,data_engineering,meaisínfhoghlaim,teanga,web,tuatha}/`
  will need their `references` lists updated. The `00_index.md` provides
  the new canonical paths for each topic.
- **Affected CI**: none; the ccc index is the only thing that needs a
  refresh after a canonical doc changes, and that happens automatically
  when the next agent runs `bun run ccc:index`.
- **Affected workflows**: per the audit, ccc already indexes
  `**/*.md` so the new structure is searchable as soon as
  `bun run ccc:index` is re-run.

## Non-Goals

- This change does **not** run `cognee.cognify()` for all 7 domains.
  The ingestion script is provided; running it requires `LLM_API_KEY`
  to be set in the environment, which depends on the mise hooks
  properly hydrating the .env file. This is wired up but the
  cognify step is deferred to a follow-up change.
- This change does **not** retire the `docs/bunchloch/` legacy mirror
  (the buneagar worktree from when the docs/ tree lived in a
  separate repo) — that's a separate concern tracked elsewhere.
- This change does **not** rewrite the canonical content; it only
  reorganises. Any factual corrections should be a follow-up change
  with its own proposal.
