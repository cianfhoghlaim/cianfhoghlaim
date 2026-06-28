# CocoIndex v0 → v1 Retirement Notice

**Status:** Active deprecation period.
**Hard-removal date:** **2026-07-15** (~3 weeks notice as of 2026-06-27).
**Owner:** Build agent.
**Change:** `centralize-agent-context-and-automate` (archived 2026-06-27).

---

## What is being retired?

The legacy **CocoIndex Code CLI** (`ccc search`, `ccc index`,
`ccc init`, `ccc status`, `ccc describe`, `ccc reset`, `ccc doctor`,
`ccc daemon`) — i.e. everything that ships in the standalone
`cocoindex-code` PyPI package, which is *separate from* the
CocoIndex library that powers the v1 apps.

It is being replaced by **CocoIndex v1 Apps** in
`sruth/oideachais/cocoindex_flows/`, which are the canonical
code-search surface for the Cianfhoghlaim monorepo.

The v0 Python apps in this `_v0_archive/` directory (e.g.
`author_archive_embedding.py`, `curriculum_embedding.py`,
`pdf_embedding.py`) were already retired in the round-8 v1
migration and remain here only as historical references. They
are not affected by the 2026-07-15 hard-removal date.

---

## Timeline

| Date | Event |
|:--|:--|
| 2026-06-16 | `ccc:v1:search` and `ccc:v1:index` aliases added (`package.json` + `mise.toml`) |
| 2026-06-16 | `docs-skills-consolidation-pipeline` change archived — v1 migration complete |
| 2026-06-27 | `centralize-agent-context-and-automate` change archived: deprecation warning banner added to `ccc:search` |
| 2026-06-27 | `scripts/validate-ccc-freshness.ts` added as CI gate; `ccc:index` continues to work |
| 2026-07-15 | **Hard removal**: `ccc search`, `ccc index`, `ccc init` aliases will be deleted from `package.json` + `mise.toml`; the deprecation banner script will be removed; documentation in `.agents/skills/INDEXING_AND_COGNITION.md` and `.agents/skills/ccc/SKILL.md` will be rewritten to reference v1 only |

---

## What you need to do

### Today (during the deprecation period)

1. **Use v1 search instead of v0:**
   ```bash
   # OLD (deprecated; emits a yellow deprecation warning to stderr)
   bun run ccc:search "BAML extraction function"

   # NEW (canonical v1 path)
   bun run ccc:v1:search "BAML extraction function"
   ```

2. **Use v1 index instead of v0:**
   ```bash
   # OLD (deprecated; kept working until 2026-07-15)
   bun run ccc:index

   # NEW (canonical v1 path — same as OLD today, but renamed for clarity)
   bun run ccc:v1:index
   ```

3. **Pre-commit hook** (`scripts/templates/pre-commit`,
   installed by `bash scripts/install-hooks.sh`) will print a
   *non-blocking* warning if your CCC index is stale:
   ```
   [pre-commit] CCC index may be stale:
     validate-ccc-freshness: STALE — last index update was 8.2d ago (threshold: 7d on main)
   [pre-commit] Refresh with: bun run ccc:index
   [pre-commit] (Bypass with: git commit --no-verify)
   ```
   The hook is **best-effort** — it NEVER blocks a commit. Bypass
   with `git commit --no-verify` if you need to.

4. **CI gate** (`mise run validate-ccc-freshness` or
   `bun run validate-ccc-freshness`) exits 1 if the index is
   >7d old on main or >24h on feature branches. Run this
   locally before pushing to avoid CI failures.

### After 2026-07-15 (post-hard-removal)

- `bun run ccc:search` will no longer exist. Use `bun run ccc:v1:search`.
- `bun run ccc:index` will no longer exist. Use `bun run ccc:v1:index`.
- `bun run ccc:init` will no longer exist. Index initialisation happens
  automatically when the first v1 app runs (or via `bun run ccc:v1:index`).
- The `cocoindex-code` MCP server (`ccc mcp` in `opencode.json`) will
  be removed; agents that need code search will use the
  `croilar-devtools` MCP or a future v1-native MCP wrapper.
- Documentation in `.agents/skills/ccc/SKILL.md` and
  `.agents/skills/INDEXING_AND_COGNITION.md` will be updated to
  reference v1 exclusively.

---

## Why are we doing this?

1. **Single source of truth.** Today the v0 CLI and the v1 apps index
   the same files into two different SQLite databases
   (`.cocoindex_code/target_sqlite.db` for v0, LanceDB
   `codebase_chunks` table for v1). Running both doubles the
   indexing cost (~2× storage, ~2× CPU, ~2× wall time).

2. **One embedding model.** Both surfaces use `BAAI/bge-m3`, so
   search results are equivalent in quality. There is no
   reason to keep two parallel indexes.

3. **CocoIndex v1 is the canonical KCG pattern.** The
   `oideachais-cocoindex-v1` skill (`.agents/skills/.../SKILL.md`)
   documents `coco.App(...)` + `@coco.fn(memo=True)` +
   `@coco.lifespan` + `lancedb.mount_table_target` as the
   only blessed pattern. The v0 CLI predates this convention.

4. **MCP consolidation.** The `croilar-devtools` MCP server
   (10th server, added in `consolidate-observability-and-graph`)
   exposes Stagehand + Firecrawl + codex-cli + E2B. A future
   v1-native code-search MCP wrapper will replace the v0
   `cocoindex-code` MCP entirely.

---

## Where to look for the canonical v1 surface

| Resource | Path |
|:--|:--|
| Canonical v1 code-search App | `sruth/oideachais/cocoindex_flows/codebase_indexing.py` |
| Canonical v1 shared lifespan | `sruth/oideachais/cocoindex_flows/_lifespan.py` |
| v1 conformance linter (11-rule) | `sruth/oideachais/cocoindex_flows/cocoindex_v1_conformance.py` |
| v1 App list (16 Apps) | `.agents/skills/oideachais-cocoindex-v1/SKILL.md` |
| v1 migration guide | `openspec/changes/archive/2026-06-16-docs-skills-consolidation-pipeline/` |
| OpenSpec spec (canonical) | `openspec/specs/indexing-and-cognition/spec.md` |

---

**Questions?** Open a GitHub issue or ask in `#kcg-build` Slack.
The build agent owns this retirement and will resolve any blockers
in the remaining 3 weeks.
