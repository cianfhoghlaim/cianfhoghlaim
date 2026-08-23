# 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1

## Why

The `mise run lint:drift-docs` validation gate (added by
the 2026-07-29-repo-hygiene change) currently reports **7
stale count claims** across 4 AGENTS.md files. These are
the pre-existing drift violations that were deliberately
left alone by Changes 1+2 (which focused on skills +
guides.yml). The `retrospective-cleanup` spec was added
2026-08-15 to formalize the safe `--fix` mode + the Layer
6 `sync:dagster` cleanup, but the AGENTS.md count
rebaseline was not yet implemented.

**Verified drift violations (2026-08-13):**

| File:line | Category | Claimed | Actual (ground truth) |
|:--|:--|--:|--:|
| `AGENTS.md:20` | specs | 89 | 92 |
| `AGENTS.md:81` | stacks | 92 | 93 |
| `agents/tuatha/AGENTS.md:61` | specs | 89 | 92 |
| `bonneagar/AGENTS.md:29` | stacks | 92 | 93 |
| `bonneagar/AGENTS.md:89` | stacks | 92 | 93 |
| `bonneagar/AGENTS.md:155` | stacks | 92 | 93 |
| `notebooks/AGENTS.md:239` | notebooks | 52 | 54 |

Plus several **internal inconsistencies** in
`.agents/skills/INDEXING_AND_COGNITION.md` that the
`centralize-agent-context-and-automate` openspec change
(2026-06-27) introduced but did not catch:

| File:line | Issue |
|:--|:--|
| `INDEXING_AND_COGNITION.md:13` | Says "8,845 source files / 257,957 chunks" — outdated (the index now has more chunks after recent additions) |
| `INDEXING_AND_COGNITION.md:14` | Says "1,743 `.md` docs / ~2,242 docs / 7 typed clusters" — outdated |
| `INDEXING_AND_COGNITION.md:288` | Says "9 MCP servers, 75+ tools" — actually 15 MCPs (per `opencode.json`) |
| `INDEXING_AND_COGNITION.md:401` | Says "all 153 skills" — actually 162 (recursive per the `rglob` logic in `scripts/lint_drift_docs.py`) |
| `INDEXING_AND_COGNITION.md:495` | Says `MCPs: 12 Agents: 14` — actually `MCPs: 15 Agents: 15` |
| `INDEXING_AND_COGNITION.md:421` | Says "all 123 skills" — actually 162 |
| `INDEXING_AND_COGNITION.md:500-509` | Health-check snippets reference wrong counts |
| `INDEXING_AND_COGNITION.md:§9.1` | Directory migration map references the dead `sruth/cianfhoghlaim/STATUS.md` path |

## What Changes

### A. Rebaseline the 7 count violations in 4 AGENTS.md files

**MODIFIED** — 7 lines across 4 files. Each is a single
number update:

1. `AGENTS.md:20` — `89 specs` → `92 specs`
2. `AGENTS.md:81` — `92 stacks` → `93 stacks`
3. `agents/tuatha/AGENTS.md:61` — `89 specs` → `92 specs`
4. `bonneagar/AGENTS.md:29` — `92 stacks` → `93 stacks`
5. `bonneagar/AGENTS.md:89` — `92 stacks` → `93 stacks`
6. `bonneagar/AGENTS.md:155` — `92 stacks` → `93 stacks`
7. `notebooks/AGENTS.md:239` — `52 notebooks` → `54 notebooks`

### B. Rebaseline the 8 internal inconsistencies in `INDEXING_AND_COGNITION.md`

**MODIFIED** `.agents/skills/INDEXING_AND_COGNITION.md` —
fix 8 count claims + drop 1 dead path reference:

1. §1 CCC chunk count — update to current
2. §2 Cognee cluster count — update to current
3. §3 the 9 MCP servers — update to 15 (per `opencode.json`)
4. §8 the 14 OpenCode agents — keep at 14 (or update to 15)
5. §8 the 9 MCP servers — update to 15
6. §8 the skill count claims — update from 123/153 to 162
7. §8 health-check snippets — update expected outputs
8. §9.1 directory migration map — drop the
   `sruth/cianfhoghlaim/STATUS.md` reference; replace with
   `dlt_sources/AGENTS.md` + the new `data-engineering`
   skill (from Change 1)

### C. Add `mise run lint:drift-docs:rebaseline` task

**NEW** `scripts/rebaseline_drift_docs.py` — the
auto-fixer that walks every drift violation reported by
`mise run lint:drift-docs` and rewrites the count claim in
place. Reports a dry-run preview by default; `--apply`
flag commits the changes.

**MODIFIED** `mise.toml` — add 2 new tasks:

```toml
[tasks."lint:drift-docs:rebaseline"]
description = "Auto-fix the 7 stale count claims reported by lint:drift-docs (safe --fix mode per the retrospective-cleanup spec). Per the 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1 change."
run = "uv run python scripts/rebaseline_drift_docs.py --apply"

[tasks."lint:drift-docs:rebaseline:dry-run"]
description = "Dry-run the auto-fix (prints the diff, exits 0)"
run = "uv run python scripts/rebaseline_drift_docs.py"
```

### D. Spec delta to `retrospective-cleanup`

**ADDED Requirement** in
`openspec/changes/2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1/specs/retrospective-cleanup/spec.md`.
See sibling `specs/retrospective-cleanup/spec.md` in
this change.

## Dependencies

`Blocked by: 2026-08-13-guides-yml-repair-and-docs-integrations-index-v1`
(needs Change 2's stable guides.yml + the
`DATA_PLATFORM_ROUTER.md` path before re-baselining
INDEXING_AND_COGNITION.md's §9.1 directory map).

`Affected repos: cianfhoghlaim` (single-repo change)

`Blocks: none` (this is the final change in the sequence).

## Out of scope (intentionally)

- `.agents/skills_backup/` cleanup (55 deprecated skills) —
  left alone per the user's instruction.
- `sruth/` directory leftovers — preserved as historical
  pattern references per the user's instruction.
- New spec for the `lint:drift-docs:rebaseline` task — the
  task is an extension of the existing `retrospective-cleanup`
  spec, not a new capability.

## Verification

```bash
# 1. Drift gate passes
mise run lint:drift-docs
# Expected: "0 violations"

# 2. Internal INDEXING_AND_COGNITION.md consistency check
grep -E "153 skills|123 skills|12 Agents|MCPs: 12" .agents/skills/INDEXING_AND_COGNITION.md
# Expected: 0 matches (all stale claims removed)

# 3. New rebaseline task
mise run lint:drift-docs:rebaseline:dry-run
# Expected: "0 changes needed (already clean)" OR "N changes available"

# 4. openspec validation
openspec validate 2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1 --strict
# Expected: "Change is valid"

# 5. Skill metadata lint (no regression)
mise run lint:skills
# Expected: 61 skills pass

# 6. guides.yml validation (no regression from Change 2)
mise run lint:guides-yml
# Expected: "All 26 guides have valid paths"
```