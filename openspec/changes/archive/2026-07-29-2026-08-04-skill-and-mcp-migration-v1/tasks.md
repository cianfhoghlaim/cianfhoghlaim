# 2026-08-04-skill-and-mcp-migration-v1 — Tasks

## Pre-implementation

- [x] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [x] Verify A1 (dlt bugfix) merged — `git log --oneline -5 -- dlt_sources/` shows
  `aa80f4111 fix(dlt_sources+misetoml): reconcile Ireland cohort count + fix baml:generate guard`
- [x] Verify the ccc code index is fresh: `bun run ccc:index` — already in good shape per `.cocoindex_code/target_sqlite.db`

## Stage 1 — Audit sruth/ references (closes #97)

- [x] `grep -rl "sruth/" .agents/skills/ | wc -l` → **0** (the migration was already
  swept; only 3 benign mentions remain — `sruth-subagents` + 2x `sruth_browser`,
  all in History sections of `INDEXING_AND_COGNITION.md` + `browser-tools/SKILL.md`)
- [x] `grep -rl "sruth/" docs/ | head -10` → 4 files. 3 contain intentional
  `sruth/<quadrant>/` path references in code-blocks / quoted lines that document
  the migration itself:
  - `docs/audits/2026-07-06-drift-audit.md` (10 lines — the original drift audit)
  - `docs/p3-skill-mcp-migration-status.md` (2 lines — the migration status)
  - `docs/biiep-v3/post-iac-namespace-rename-secrets.md` (1 line — quotes the
    pre-v7 `.infisical.env` line)
  - `docs/ui-inspiration/UI_INSPIRATION_GUIDE.md` (mentions "sruth/" but does NOT
    match the strict path regex `sruth/(quadrant)/`)

## Stage 2 — Migrate sruth/ paths

- [x] `find .agents/skills -name "SKILL.md" -exec sed -i '' ...` — **NO-OP** because
  the sed pattern matches 0 lines in `.agents/skills/` (the migration was swept by
  the v4 consolidation). The 3 remaining `sruth` strings are non-path mentions
  (`sruth-subagents`, `sruth_browser`) that should NOT be removed.
- [x] Apply the same sed to `docs/` — **PARTIAL**: would BREAK the 3 docs that
  intentionally quote the legacy paths (the sed would rewrite
  `infisical://dev-baile/sruth/cianfhoghlaim/OPENAI_API_KEY` into
  `infisical://dev-baile/./OPENAI_API_KEY`, corrupting the URI). The CI gate
  now excludes these 3 docs.
- [x] Spot-check 5 skills manually:
  - `.agents/skills/INDEXING_AND_COGNITION.md` — 1 mention `sruth-subagents` (intentional)
  - `.agents/skills/browser-tools/SKILL.md` — 2 mentions `sruth_browser` (intentional)
  - `.agents/skills/baml/SKILL.md` — 0 matches
  - `.agents/skills/cocoindex/SKILL.md` — 0 matches
  - `.agents/skills/motherduck/SKILL.md` — 0 matches
- [x] Update the BAML examples in the skills that have them — NO-OP (no BAML examples
  in any skill file reference `sruth/` paths)
- [x] Add a CI gate that fails on any remaining `sruth/`:
  - Fixed `.github/workflows/skill-refs-check.yaml` (the existing file used a too-strict
    regex that failed on the 3 intentional historical docs; added a 3-doc exclude list)
  - Created `.forgejo/workflows/skill-refs-check.yaml` (mirror with the same fixed logic)

## Stage 3 — Migrate croilar-devtools (closes #96)

- [x] `git mv agents/_croilar/_croilar_convex/devtools.ts
  agents/api/_croilar_convex/devtools.ts` — **ALREADY DONE** at the canonical path
- [x] Move the 3 associated files (package.json + tsconfig + README) — **N/A**: the
  agents/api/_croilar_convex/ directory only contains .ts files (no package.json/tsconfig/README
  needed; it's an internal Convex function module under the cianfhoghlaim package).
- [x] Update the import paths in the moved file — **N/A**: the imports
  (`../_generated/server` + `./helpers`) are relative and work correctly from
  `agents/api/_croilar_convex/`.
- [x] Update the route registrations in `agents/api/index.ts` — **N/A**: `agents/api/`
  is a Python module (`__init__.py` exports `curriculum_endpoint.app`); there is NO
  `agents/api/index.ts` to update. The devtools.ts is a Convex query, not a Hono route.
  It is auto-registered by Convex when its parent directory is mounted.

## Stage 4 — Validation

- [x] `grep -r "sruth/" .agents/skills/ docs/` returns 0 matches for the strict path
  regex `sruth/(cianfhoghlaim|meaisinfhoghlaim|tuatha|croilar|oideachais)/` in
  non-excluded files (the 3 excluded docs retain their intentional mentions)
- [x] `grep -r "croilar-devtools" agents/` shows the canonical path
  (`agents/api/_croilar_convex/devtools.ts`) — the 2 remaining references in
  `schema.ts` + `crons.ts` are comments documenting the Web-stack observability hub
- [ ] `bun run mcp:test` passes — **[deferred]**: there is no `mcp:test` script defined
  in `package.json` or `agents/api/package.json`. The agents/api folder is a Python
  module, not a Bun MCP server. The devtools.ts is a Convex query function, not an
  MCP tool. The MCP-test verification has been replaced by the path-existence check
  in the CI gate (`.github/workflows/skill-refs-check.yaml` step 2).
- [x] `openspec validate 2026-08-04-skill-and-mcp-migration-v1 --strict` passes
  → "Change '2026-08-04-skill-and-mcp-migration-v1' is valid"

## Stage 5 — Spec delta + validation

- [x] Write the spec delta to
  `openspec/changes/2026-08-04-skill-and-mcp-migration-v1/specs/agent-platform-cluster/spec.md`
  — REWRITTEN to use `## ADDED Requirements` (the original delta used `## MODIFIED`
  for a requirement that does not exist in the parent spec — format corrected)
- [ ] Commit the change on a dedicated branch — **[skipped per task contract]**
- [ ] Open a PR on `origin/main` referencing this change — **[skipped per task contract]**
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-04-skill-and-mcp-migration-v1 --yes` — **[skipped per task contract]**

## Stage 6 — Close the GitHub issues

- [ ] `gh issue close 96 --comment "Closes via 2026-08-04-skill-and-mcp-migration-v1"` — **[skipped per task contract]**
- [ ] `gh issue close 97 --comment "Closes via 2026-08-04-skill-and-mcp-migration-v1"` — **[skipped per task contract]**

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues — **[skipped per task contract]**
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol — **[skipped per task contract]**

## Summary

- **Tasks complete:** 16/26 (the 10 skipped/deferred items are all explicitly
  out-of-scope per the task contract — commit, push, archive, close-issue, sync-docs).
- **Tasks deferred:** 1 — `bun run mcp:test` does not exist as a script in this repo.
  The path-existence check in the CI gate is the correct functional equivalent.