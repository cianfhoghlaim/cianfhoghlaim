## Why

`.agents/skills/` had two code-search skills competing for the
same job:

- `ccc` — the KCG-canonical semantic code search (CocoIndex v1 +
  BGE-M3 + LanceDB HNSW + Dagster asset). Per `AGENTS.md`:
  *"Treat it as a first-class tool — always use it before
  grep/find."*
- `chunkhound` — an open-source local-first alternative (cAST
  chunking + multi-hop exploration + DuckDB/LanceDB + 29+
  language support). 764 lines of detailed documentation.

The two skills overlapped on the 80% case (semantic search,
rebuild index, configure for a project). `chunkhound` had a
handful of unique capabilities the KCG team liked
(multi-hop BFS exploration, adaptive token budgets, dual-store
DuckDB + LanceDB, 29+ language support) but no KCG project
actually uses ChunkHound in production; the
`openspec/specs/chunkhound-code-search` spec exists but
`AGENTS.md` says `ccc` is canonical.

The right move is to keep `ccc` as the only skill, and move
the unique ChunkHound content (the two-layer architecture, the
multi-hop exploration pattern, the 29-language matrix, the
adaptive token budgets, the "when to use ChunkHound vs ccc"
decision) into a new **Appendix A: Alternative engines**
section in `ccc/SKILL.md`.

After this change, code search has 1 skill (was 2).

## What changes

- `.agents/skills/chunkhound/` deleted
- `.agents/skills/ccc/SKILL.md` — new "Appendix A: Alternative
  engines" section appended (the ChunkHound vs ccc comparison
  + the "how to install ChunkHound if needed" snippet)

## Out of scope

- The `openspec/specs/chunkhound-code-search` spec is
  left in place. It is a capability spec; the canonical
  implementation is `ccc` (this skill documents that). The
  spec is the source of truth for the capability; this
  change only consolidates the skill.
- Migrating any code from ChunkHound → ccc (no KCG project
  uses ChunkHound in production).
